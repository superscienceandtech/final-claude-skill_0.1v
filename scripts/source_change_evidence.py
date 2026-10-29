"""Observe bounded repository-file changes for implementation handoffs.

The resulting report describes filesystem state between two snapshots. It is
not authenticated proof of authorship, authorization, or sandbox enforcement.
"""

from __future__ import annotations

import hashlib
import re
import stat
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath


_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_MAX_FILE_SIZE_BYTES = 16 * 1024 * 1024
_MAX_SNAPSHOT_SIZE_BYTES = 64 * 1024 * 1024
_MAX_SNAPSHOT_PATHS = 256
_MAX_PATH_LENGTH = 4096


class SourceSnapshotError(ValueError):
    """Raised when a requested source path cannot be safely observed."""


class SourceChangeKind(str, Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"


@dataclass(frozen=True, slots=True)
class FileSnapshot:
    """Bounded digest of one explicitly selected regular file or absent path."""

    path: str
    sha256: str | None
    size_bytes: int | None

    def __post_init__(self) -> None:
        _validate_relative_path(self.path)
        if self.sha256 is None:
            if self.size_bytes is not None:
                raise ValueError("absent files must not have a size.")
        elif (
            not isinstance(self.sha256, str)
            or not _SHA256_PATTERN.fullmatch(self.sha256)
            or not isinstance(self.size_bytes, int)
            or isinstance(self.size_bytes, bool)
            or self.size_bytes < 0
        ):
            raise ValueError("present files require a SHA-256 digest and byte size.")


@dataclass(frozen=True, slots=True)
class RepositorySnapshot:
    """Filesystem snapshot limited to a caller-selected set of repository paths."""

    root: Path
    files: tuple[FileSnapshot, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.root, Path) or not self.root.is_absolute():
            raise ValueError("snapshot root must be an absolute pathlib.Path.")
        if not isinstance(self.files, tuple) or not self.files:
            raise ValueError("snapshot files must be a non-empty tuple.")
        paths = tuple(file.path for file in self.files if isinstance(file, FileSnapshot))
        if len(paths) != len(self.files) or paths != tuple(sorted(set(paths))):
            raise ValueError("snapshot files must be unique and sorted by path.")

    @property
    def scope_paths(self) -> tuple[str, ...]:
        return tuple(file.path for file in self.files)


@dataclass(frozen=True, slots=True)
class SourceFileChange:
    """Observed digest transition for one selected repository file."""

    path: str
    kind: SourceChangeKind
    before_sha256: str | None
    after_sha256: str | None
    before_size_bytes: int | None
    after_size_bytes: int | None

    def __post_init__(self) -> None:
        _validate_relative_path(self.path)
        if not isinstance(self.kind, SourceChangeKind):
            raise ValueError("kind must be a SourceChangeKind value.")
        before = FileSnapshot(self.path, self.before_sha256, self.before_size_bytes)
        after = FileSnapshot(self.path, self.after_sha256, self.after_size_bytes)
        if before == after:
            raise ValueError("source changes must describe different file states.")
        expected_kind = (
            SourceChangeKind.CREATED
            if before.sha256 is None
            else SourceChangeKind.DELETED
            if after.sha256 is None
            else SourceChangeKind.MODIFIED
        )
        if self.kind is not expected_kind:
            raise ValueError("kind does not match the observed file states.")


@dataclass(frozen=True, slots=True)
class SourceChangeReport:
    """Observed source changes and the exact paths included in both snapshots."""

    scope_paths: tuple[str, ...]
    changes: tuple[SourceFileChange, ...]
    outcome: str = "observed"
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.scope_paths, tuple) or not self.scope_paths:
            raise ValueError("scope_paths must be a non-empty tuple.")
        for path in self.scope_paths:
            _validate_relative_path(path)
        if self.scope_paths != tuple(sorted(set(self.scope_paths))):
            raise ValueError("scope_paths must be unique and sorted by path.")
        if not isinstance(self.changes, tuple) or any(
            not isinstance(change, SourceFileChange) for change in self.changes
        ):
            raise ValueError("changes must contain SourceFileChange values.")
        if not isinstance(self.outcome, str) or self.outcome not in {
            "observed",
            "incomplete",
        }:
            raise ValueError("outcome must be observed or incomplete.")
        if not isinstance(self.limitations, tuple) or any(
            not isinstance(limitation, str) or not limitation.strip()
            for limitation in self.limitations
        ):
            raise ValueError("limitations must contain non-empty strings.")
        if (self.outcome == "incomplete") != bool(self.limitations):
            raise ValueError("incomplete observations require limitations.")
        changed_paths = tuple(change.path for change in self.changes)
        if changed_paths != tuple(sorted(set(changed_paths))):
            raise ValueError("changes must be unique and sorted by path.")
        if not set(changed_paths).issubset(self.scope_paths):
            raise ValueError("changed paths must be within scope_paths.")

    @property
    def changed_paths(self) -> tuple[str, ...]:
        return tuple(change.path for change in self.changes)

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence_type": "local_filesystem_observation",
            "authenticated": False,
            "outcome": self.outcome,
            "scope_paths": list(self.scope_paths),
            "limitations": list(self.limitations),
            "changes": [
                {
                    "path": change.path,
                    "kind": change.kind.value,
                    "before_sha256": change.before_sha256,
                    "after_sha256": change.after_sha256,
                    "before_size_bytes": change.before_size_bytes,
                    "after_size_bytes": change.after_size_bytes,
                }
                for change in self.changes
            ],
        }


def capture_repository_snapshot(
    repository_root: Path, paths: tuple[str, ...]
) -> RepositorySnapshot:
    """Hash only explicit in-repository regular files, rejecting symlink paths."""
    if not isinstance(repository_root, Path):
        raise SourceSnapshotError("repository_root must be a pathlib.Path.")
    if not isinstance(paths, tuple) or not paths:
        raise SourceSnapshotError("paths must be a non-empty tuple.")
    if len(paths) > _MAX_SNAPSHOT_PATHS:
        raise SourceSnapshotError("paths exceed the observation limit.")
    for path in paths:
        _validate_relative_path(path)
    normalized_paths = tuple(sorted(paths))
    if len(set(normalized_paths)) != len(normalized_paths):
        raise SourceSnapshotError("paths must not contain duplicates.")
    try:
        root = repository_root.resolve(strict=True)
    except OSError as error:
        raise SourceSnapshotError("repository_root must exist and be accessible.") from error
    if not root.is_dir():
        raise SourceSnapshotError("repository_root must be a directory.")
    snapshots: list[FileSnapshot] = []
    total_size = 0
    for path in normalized_paths:
        maximum_size = min(
            _MAX_FILE_SIZE_BYTES, _MAX_SNAPSHOT_SIZE_BYTES - total_size
        )
        snapshot = _capture_file(root, path, maximum_size)
        total_size += snapshot.size_bytes or 0
        snapshots.append(snapshot)
    return RepositorySnapshot(root, tuple(snapshots))


def compare_repository_snapshots(
    before: RepositorySnapshot, after: RepositorySnapshot
) -> SourceChangeReport:
    """Build a deterministic report for selected paths observed at two times."""
    if not isinstance(before, RepositorySnapshot) or not isinstance(
        after, RepositorySnapshot
    ):
        raise ValueError("before and after must be RepositorySnapshot values.")
    if before.root != after.root:
        raise ValueError("snapshots must use the same repository root.")
    if before.scope_paths != after.scope_paths:
        raise ValueError("snapshots must use the same path scope.")

    changes: list[SourceFileChange] = []
    for old, new in zip(before.files, after.files, strict=True):
        if old == new:
            continue
        kind = (
            SourceChangeKind.CREATED
            if old.sha256 is None
            else SourceChangeKind.DELETED
            if new.sha256 is None
            else SourceChangeKind.MODIFIED
        )
        changes.append(
            SourceFileChange(
                path=old.path,
                kind=kind,
                before_sha256=old.sha256,
                after_sha256=new.sha256,
                before_size_bytes=old.size_bytes,
                after_size_bytes=new.size_bytes,
            )
        )
    return SourceChangeReport(before.scope_paths, tuple(changes))


def incomplete_source_change_report(
    scope_paths: tuple[str, ...], limitation: str
) -> SourceChangeReport:
    """Represent a failed post-execution observation without claiming no edits."""
    if not isinstance(scope_paths, tuple):
        raise ValueError("scope_paths must be a tuple.")
    for path in scope_paths:
        _validate_relative_path(path)
    normalized_paths = tuple(sorted(scope_paths))
    if not normalized_paths or len(set(normalized_paths)) != len(normalized_paths):
        raise ValueError("scope_paths must be non-empty and unique.")
    if not isinstance(limitation, str) or not limitation.strip():
        raise ValueError("limitation must be a non-empty string.")
    return SourceChangeReport(
        scope_paths=normalized_paths,
        changes=(),
        outcome="incomplete",
        limitations=(limitation,),
    )


def _validate_relative_path(path: str) -> None:
    if (
        not isinstance(path, str)
        or not path
        or len(path) > _MAX_PATH_LENGTH
        or "\\" in path
        or ":" in path
        or "\x00" in path
    ):
        raise ValueError("source paths must be normalized repository-relative POSIX paths.")
    relative = PurePosixPath(path)
    if (
        relative.is_absolute()
        or not relative.parts
        or relative.as_posix() != path
        or any(part in ("", ".", "..") or part.casefold() == ".git" for part in relative.parts)
    ):
        raise ValueError("source paths must be normalized repository-relative POSIX paths.")


def _capture_file(
    root: Path, relative_path: str, maximum_size: int
) -> FileSnapshot:
    current = root
    parts = PurePosixPath(relative_path).parts
    for index, part in enumerate(parts):
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            return FileSnapshot(relative_path, None, None)
        except OSError as error:
            raise SourceSnapshotError(
                f"cannot inspect source path: {relative_path} ({type(error).__name__})"
            ) from error
        if stat.S_ISLNK(metadata.st_mode) or current.is_junction():
            raise SourceSnapshotError(f"source path cannot traverse a symlink: {relative_path}")
        if index < len(parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise SourceSnapshotError(f"source path parent is not a directory: {relative_path}")
        if index == len(parts) - 1:
            if not stat.S_ISREG(metadata.st_mode):
                raise SourceSnapshotError(f"source path is not a regular file: {relative_path}")
            if metadata.st_size > maximum_size:
                raise SourceSnapshotError(
                    f"snapshot exceeds the observation limit: {relative_path}"
                )
            digest = hashlib.sha256()
            size_bytes = 0
            try:
                with current.open("rb") as source_file:
                    while chunk := source_file.read(64 * 1024):
                        size_bytes += len(chunk)
                        if size_bytes > maximum_size:
                            raise SourceSnapshotError(
                                f"snapshot exceeds the observation limit: {relative_path}"
                            )
                        digest.update(chunk)
            except OSError as error:
                raise SourceSnapshotError(
                    f"cannot read source file: {relative_path} ({type(error).__name__})"
                ) from error
            return FileSnapshot(relative_path, digest.hexdigest(), size_bytes)
    raise SourceSnapshotError(f"source path could not be observed: {relative_path}")

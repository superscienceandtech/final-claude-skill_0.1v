from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.source_change_evidence import (
    SourceChangeKind,
    SourceSnapshotError,
    capture_repository_snapshot,
    compare_repository_snapshots,
)


class SourceChangeEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        source_directory = self.root / "src"
        source_directory.mkdir()
        (source_directory / "modified.py").write_bytes(b"before\n")
        (source_directory / "deleted.py").write_bytes(b"remove\n")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_hashes_actual_created_modified_and_deleted_file_changes(self) -> None:
        scope = ("src/created.py", "src/deleted.py", "src/modified.py")
        before = capture_repository_snapshot(self.root, scope)

        (self.root / "src" / "created.py").write_bytes(b"new\n")
        (self.root / "src" / "deleted.py").unlink()
        (self.root / "src" / "modified.py").write_bytes(b"after\n")
        after = capture_repository_snapshot(self.root, scope)

        report = compare_repository_snapshots(before, after)
        changes = {change.path: change for change in report.changes}
        self.assertEqual(report.outcome, "observed")
        self.assertEqual(
            {path: change.kind for path, change in changes.items()},
            {
                "src/created.py": SourceChangeKind.CREATED,
                "src/deleted.py": SourceChangeKind.DELETED,
                "src/modified.py": SourceChangeKind.MODIFIED,
            },
        )
        self.assertEqual(
            changes["src/modified.py"].before_sha256,
            hashlib.sha256(b"before\n").hexdigest(),
        )
        self.assertEqual(
            changes["src/modified.py"].after_sha256,
            hashlib.sha256(b"after\n").hexdigest(),
        )

    def test_unchanged_files_are_scoped_but_not_reported_as_changes(self) -> None:
        before = capture_repository_snapshot(self.root, ("src/modified.py",))
        after = capture_repository_snapshot(self.root, ("src/modified.py",))

        report = compare_repository_snapshots(before, after)

        self.assertEqual(report.scope_paths, ("src/modified.py",))
        self.assertEqual(report.changes, ())

    def test_rejects_traversal_git_metadata_duplicates_and_non_files(self) -> None:
        for invalid_path in ("../outside.py", ".", ".git/config", "src\\modified.py"):
            with self.subTest(path=invalid_path), self.assertRaises(ValueError):
                capture_repository_snapshot(self.root, (invalid_path,))
        with self.assertRaisesRegex(SourceSnapshotError, "duplicates"):
            capture_repository_snapshot(
                self.root, ("src/modified.py", "src/modified.py")
            )
        with self.assertRaisesRegex(SourceSnapshotError, "not a regular file"):
            capture_repository_snapshot(self.root, ("src",))

    def test_bounds_snapshot_path_count(self) -> None:
        paths = tuple(f"src/missing-{index}.py" for index in range(257))
        with self.assertRaisesRegex(SourceSnapshotError, "observation limit"):
            capture_repository_snapshot(self.root, paths)

    def test_reports_file_read_permission_failure_without_claiming_absence(self) -> None:
        with patch.object(Path, "open", side_effect=PermissionError):
            with self.assertRaisesRegex(
                SourceSnapshotError,
                "cannot read source file: src/modified.py \\(PermissionError\\)",
            ):
                capture_repository_snapshot(self.root, ("src/modified.py",))

    def test_rejects_symlink_source_paths_when_host_allows_symlink_creation(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside.py"
        outside.write_text("outside\n", encoding="utf-8")
        link = self.root / "src" / "linked.py"
        try:
            link.symlink_to(outside)
        except OSError as error:
            outside.unlink(missing_ok=True)
            self.skipTest(f"symlink creation is unavailable: {error}")
        try:
            with self.assertRaisesRegex(SourceSnapshotError, "cannot traverse a symlink"):
                capture_repository_snapshot(self.root, ("src/linked.py",))
        finally:
            link.unlink(missing_ok=True)
            outside.unlink(missing_ok=True)

    def test_snapshots_must_have_matching_repository_and_scope(self) -> None:
        before = capture_repository_snapshot(self.root, ("src/modified.py",))
        other_root = Path(tempfile.mkdtemp())
        try:
            other = capture_repository_snapshot(other_root, ("src/modified.py",))
            with self.assertRaisesRegex(ValueError, "same repository root"):
                compare_repository_snapshots(before, other)
        finally:
            other_root.rmdir()


if __name__ == "__main__":
    unittest.main()

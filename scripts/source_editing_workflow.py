"""Bounded local source editing through the configured Skill pipeline.

The path grant is an application-level permission check, not an OS sandbox.
Filesystem metadata checks cannot prevent a hostile concurrent path swap.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import re
import secrets
import stat
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Mapping

from scripts.skill_pipeline import (
    SkillPipeline,
    SkillExecutionAdapter,
    SkillExecutionContext,
    SkillExecutionFailure,
    SkillExecutionStatus,
)
from scripts.skill_registry import SkillContract
from scripts.source_change_evidence import (
    FileSnapshot,
    RepositorySnapshot,
    SourceChangeReport,
    SourceSnapshotError,
    capture_repository_snapshot,
    compare_repository_snapshots,
    incomplete_source_change_report,
)
from scripts.tool_workflow import WorkflowCancellationToken
from scripts.validation_adapter import (
    ValidationCommand,
    ValidationCommandAdapter,
    ValidationOperation,
    ValidationRunEvidence,
)


_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_MAX_OPERATIONS = 32
_MAX_FILE_BYTES = 2 * 1024 * 1024
_MAX_TOTAL_BYTES = 8 * 1024 * 1024


class SourceEditOutcome(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class SourceEditError(ValueError):
    """Expected, safely reportable source-edit rejection."""

    def __init__(self, error_code: str) -> None:
        self.error_code = error_code
        super().__init__(error_code)


class SourceEditCancelled(Exception):
    """Raised when cancellation is observed before an atomic replacement."""


@dataclass(frozen=True, slots=True)
class SourceWriteAuthorization:
    """Application-level exact-path read and write grants."""

    repository_root: Path
    authorized_paths: tuple[str, ...]
    readable_paths: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.repository_root, Path):
            raise ValueError("repository_root must be a pathlib.Path.")
        try:
            root = self.repository_root.resolve(strict=True)
        except OSError as error:
            raise ValueError("repository_root must exist and be accessible.") from error
        if not root.is_dir():
            raise ValueError("repository_root must be a directory.")
        if not isinstance(self.authorized_paths, tuple) or not self.authorized_paths:
            raise ValueError("authorized_paths must be a non-empty tuple.")
        for path in self.authorized_paths:
            _validate_relative_path(path)
        paths = tuple(sorted(set(self.authorized_paths)))
        if len(paths) != len(self.authorized_paths):
            raise ValueError("authorized_paths must not contain duplicates.")
        if len(paths) > 256:
            raise ValueError("authorized_paths exceed the observation limit.")
        readable_paths = self.readable_paths
        if not isinstance(readable_paths, tuple):
            raise ValueError("readable_paths must be a tuple.")
        original_readable_paths = readable_paths
        for path in readable_paths:
            _validate_relative_path(path)
        readable_paths = tuple(sorted(set(readable_paths)))
        if len(readable_paths) != len(original_readable_paths):
            raise ValueError("readable_paths must not contain duplicates.")
        if len(readable_paths) > 256:
            raise ValueError("readable_paths exceed the observation limit.")
        object.__setattr__(self, "repository_root", root)
        object.__setattr__(self, "authorized_paths", paths)
        object.__setattr__(self, "readable_paths", readable_paths)


@dataclass(frozen=True, slots=True)
class SourceEditOperation:
    """Replace or create one UTF-8 file, conditional on its observed prior hash."""

    path: str
    content: str
    expected_sha256: str | None

    def __post_init__(self) -> None:
        _validate_relative_path(self.path)
        if not isinstance(self.content, str):
            raise ValueError("content must be a string.")
        encoded = self.content.encode("utf-8")
        if len(encoded) > _MAX_FILE_BYTES:
            raise ValueError("content exceeds the per-file edit limit.")
        if self.expected_sha256 is not None and (
            not isinstance(self.expected_sha256, str)
            or not _SHA256_PATTERN.fullmatch(self.expected_sha256)
        ):
            raise ValueError("expected_sha256 must be a lowercase SHA-256 digest or None.")


@dataclass(frozen=True, slots=True)
class SourceEditingRequest:
    """A bounded set of proposed file contents and fixed validation operations."""

    objective: str
    operations: tuple[SourceEditOperation, ...]
    validation_commands: tuple[ValidationCommand, ...]
    request_id: str = ""
    cancellation_token: WorkflowCancellationToken | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be a non-empty string.")
        if (
            not isinstance(self.operations, tuple)
            or not self.operations
            or len(self.operations) > _MAX_OPERATIONS
            or any(not isinstance(operation, SourceEditOperation) for operation in self.operations)
        ):
            raise ValueError("operations must be a non-empty bounded tuple of edit operations.")
        paths = tuple(operation.path for operation in self.operations)
        if len(paths) != len(set(paths)):
            raise ValueError("edit operation paths must be unique.")
        if sum(len(operation.content.encode("utf-8")) for operation in self.operations) > _MAX_TOTAL_BYTES:
            raise ValueError("edit contents exceed the total request limit.")
        if not isinstance(self.validation_commands, tuple) or not self.validation_commands:
            raise ValueError("validation_commands must be a non-empty tuple.")
        if any(
            not isinstance(command, ValidationCommand)
            for command in self.validation_commands
        ):
            raise ValueError("validation_commands must contain ValidationCommand values.")
        if len({command.identifier for command in self.validation_commands}) != len(
            self.validation_commands
        ):
            raise ValueError("validation command identifiers must be unique.")
        if self.request_id:
            try:
                parsed_id = uuid.UUID(self.request_id)
            except ValueError as error:
                raise ValueError("request_id must be a valid UUID.") from error
            if str(parsed_id) != self.request_id.lower():
                raise ValueError("request_id must use canonical UUID formatting.")
        else:
            object.__setattr__(self, "request_id", str(uuid.uuid4()))
        if self.cancellation_token is not None and not isinstance(
            self.cancellation_token, WorkflowCancellationToken
        ):
            raise ValueError("cancellation_token must be a WorkflowCancellationToken.")


@dataclass(frozen=True, slots=True)
class SourceEditOperationResult:
    path: str
    outcome: str
    before_sha256: str | None
    after_sha256: str | None
    error_code: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "outcome": self.outcome,
            "before_sha256": self.before_sha256,
            "after_sha256": self.after_sha256,
            "error_code": self.error_code,
        }


@dataclass(frozen=True, slots=True)
class SourceEditingResult:
    request_id: str
    outcome: SourceEditOutcome
    operation_results: tuple[SourceEditOperationResult, ...]
    validation_runs: tuple[ValidationRunEvidence, ...]
    source_change_report: SourceChangeReport | None
    error_code: str | None = None

    @property
    def success(self) -> bool:
        return (
            self.outcome is SourceEditOutcome.SUCCEEDED
            and all(run.outcome == "succeeded" for run in self.validation_runs)
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "outcome": self.outcome.value,
            "operation_results": [
                result.to_dict() for result in self.operation_results
            ],
            "validation_runs": [
                {
                    "command_id": run.command_id,
                    "operation": run.operation,
                    "outcome": run.outcome,
                    "exit_code": run.exit_code,
                    "stdout": run.stdout,
                    "stderr": run.stderr,
                    "limitation": run.limitation,
                    "output_truncated": run.output_truncated,
                }
                for run in self.validation_runs
            ],
            "source_change_report": (
                None
                if self.source_change_report is None
                else self.source_change_report.to_dict()
            ),
            "error_code": self.error_code,
        }


class SourceEditingWorkflow:
    """Apply only explicitly granted file edits, then run fixed validations."""

    def __init__(
        self,
        repository_root: Path,
        authorization: SourceWriteAuthorization | None,
        *,
        validation_adapter: ValidationCommandAdapter | None = None,
    ) -> None:
        if not isinstance(repository_root, Path):
            raise ValueError("repository_root must be a pathlib.Path.")
        try:
            root = repository_root.resolve(strict=True)
        except OSError as error:
            raise ValueError("repository_root must exist and be accessible.") from error
        if not root.is_dir():
            raise ValueError("repository_root must be a directory.")
        if authorization is not None and (
            not isinstance(authorization, SourceWriteAuthorization)
            or authorization.repository_root != root
        ):
            raise ValueError("authorization must grant paths under repository_root.")
        if validation_adapter is None:
            validation_adapter = ValidationCommandAdapter(root)
        if (
            not isinstance(validation_adapter, ValidationCommandAdapter)
            or validation_adapter.repository_root != root
        ):
            raise ValueError("validation_adapter must use the same repository root.")
        self.repository_root = root
        self.authorization = authorization
        self.validation_adapter = validation_adapter

    def execute(
        self,
        request: SourceEditingRequest,
        *,
        cancellation_token: WorkflowCancellationToken | None = None,
    ) -> SourceEditingResult:
        if not isinstance(request, SourceEditingRequest):
            raise ValueError("request must be a SourceEditingRequest.")
        token = cancellation_token or request.cancellation_token
        if token is not None and not isinstance(token, WorkflowCancellationToken):
            raise ValueError("cancellation_token must be a WorkflowCancellationToken.")
        if self.authorization is None:
            return self._rejected(request, "source_edit_blocked")
        authorized = set(self.authorization.authorized_paths)
        readable = set(self.authorization.readable_paths or ())
        if any(
            operation.path not in authorized or operation.path not in readable
            for operation in request.operations
        ):
            return self._rejected(request, "source_edit_blocked")
        observed_paths = tuple(sorted(readable))
        try:
            self.validation_adapter.validate_commands(request.validation_commands)
            if any(
                command.operation is not ValidationOperation.GIT_DIFF_CHECK
                or not command.targets
                or not set(command.targets).issubset(readable)
                for command in request.validation_commands
            ):
                return self._rejected(
                    request,
                    "source_edit_validation_scope_denied",
                )
            for operation in request.operations:
                _resolve_edit_target(self.repository_root, operation.path)
            before = capture_repository_snapshot(
                self.repository_root,
                observed_paths,
            )
        except (OSError, SourceSnapshotError, SourceEditError, ValueError):
            return self._rejected(request, "source_edit_blocked")

        before_by_path = {item.path: item for item in before.files}
        for operation in request.operations:
            current = before_by_path[operation.path]
            if current.sha256 != operation.expected_sha256:
                return self._rejected(request, "source_edit_conflict", before)

        results: list[SourceEditOperationResult] = []
        operation_error: str | None = None
        cancelled = False
        for operation_index, operation in enumerate(request.operations):
            if token is not None and token.is_cancelled:
                cancelled = True
                results.extend(
                    SourceEditOperationResult(
                        pending.path,
                        "not_run",
                        before_by_path[pending.path].sha256,
                        None,
                        "source_edit_cancelled",
                    )
                    for pending in request.operations[len(results) :]
                )
                break
            initial = before_by_path[operation.path]
            try:
                after_digest = self._apply_operation(operation, initial, token)
            except SourceEditCancelled:
                cancelled = True
                results.append(
                    SourceEditOperationResult(
                        operation.path,
                        "not_run",
                        initial.sha256,
                        None,
                        "source_edit_cancelled",
                    )
                )
                results.extend(
                    SourceEditOperationResult(
                        pending.path,
                        "not_run",
                        before_by_path[pending.path].sha256,
                        None,
                        "source_edit_cancelled",
                    )
                    for pending in request.operations[operation_index + 1 :]
                )
                break
            except SourceEditError as error:
                operation_error = error.error_code
                results.append(
                    SourceEditOperationResult(
                        operation.path,
                        "failed",
                        initial.sha256,
                        None,
                        error.error_code,
                    )
                )
                results.extend(
                    SourceEditOperationResult(
                        pending.path,
                        "not_run",
                        before_by_path[pending.path].sha256,
                        None,
                        "source_edit_not_run",
                    )
                    for pending in request.operations[operation_index + 1 :]
                )
                break
            except OSError as error:
                operation_error = (
                    "source_edit_write_denied"
                    if isinstance(error, PermissionError)
                    else "source_edit_write_failed"
                )
                results.append(
                    SourceEditOperationResult(
                        operation.path,
                        "failed",
                        initial.sha256,
                        None,
                        operation_error,
                    )
                )
                results.extend(
                    SourceEditOperationResult(
                        pending.path,
                        "not_run",
                        before_by_path[pending.path].sha256,
                        None,
                        "source_edit_not_run",
                    )
                    for pending in request.operations[operation_index + 1 :]
                )
                break
            results.append(
                SourceEditOperationResult(
                    operation.path,
                    "succeeded",
                    initial.sha256,
                    after_digest,
                )
            )

        if token is not None and token.is_cancelled and len(results) < len(request.operations):
            cancelled = True
        try:
            after = capture_repository_snapshot(
                self.repository_root, before.scope_paths
            )
            change_report = compare_repository_snapshots(before, after)
        except (OSError, SourceSnapshotError, ValueError) as error:
            after = None
            change_report = incomplete_source_change_report(
                before.scope_paths,
                f"post_edit_snapshot_failed:{type(error).__name__}",
            )
        expected_hashes = {
            operation.path: hashlib.sha256(
                operation.content.encode("utf-8")
            ).hexdigest()
            for operation in request.operations
        }
        if after is not None:
            observed_hashes = {item.path: item.sha256 for item in after.files}
            results = [
                SourceEditOperationResult(
                    result.path,
                    result.outcome,
                    result.before_sha256,
                    observed_hashes.get(result.path),
                    result.error_code,
                )
                for result in results
            ]
        verified_results: list[SourceEditOperationResult] = []
        for result in results:
            content_mismatch = (
                result.outcome == "succeeded"
                and result.after_sha256 != expected_hashes[result.path]
            )
            if content_mismatch:
                operation_error = "source_edit_content_mismatch"
            verified_results.append(
                SourceEditOperationResult(
                    result.path,
                    "failed" if content_mismatch else result.outcome,
                    result.before_sha256,
                    result.after_sha256,
                    "source_edit_content_mismatch"
                    if content_mismatch
                    else result.error_code,
                )
            )
        results = verified_results
        committed = (
            any(result.outcome == "succeeded" for result in results)
            or bool(change_report.changes)
            or change_report.outcome == "incomplete"
        )
        requested_paths = {operation.path for operation in request.operations}
        unexpected_changes = (
            set(change_report.changed_paths).difference(requested_paths)
            if change_report.outcome == "observed"
            else set()
        )

        if cancelled:
            validation_runs = self.validation_adapter.skip(
                request.validation_commands,
                "validation_skipped_because_edit_workflow_was_cancelled",
            )
            outcome = SourceEditOutcome.PARTIAL if committed else SourceEditOutcome.CANCELLED
            error_code = "source_edit_cancelled"
        elif operation_error is not None:
            if committed:
                validation_runs = self.validation_adapter.execute(
                    request.validation_commands,
                    cancellation_token=token,
                )
                outcome = SourceEditOutcome.PARTIAL
                error_code = "source_edit_partial"
            elif operation_error in {
                "source_edit_blocked",
                "source_edit_path_unsafe",
                "source_edit_path_unavailable",
            }:
                validation_runs = self.validation_adapter.skip(
                    request.validation_commands,
                    "validation_skipped_because_edit_request_was_blocked",
                )
                outcome = SourceEditOutcome.BLOCKED
                error_code = operation_error
            else:
                validation_runs = self.validation_adapter.skip(
                    request.validation_commands,
                    "validation_skipped_because_no_edit_succeeded",
                )
                outcome = SourceEditOutcome.FAILED
                error_code = operation_error
        else:
            validation_runs = self.validation_adapter.execute(
                request.validation_commands,
                cancellation_token=token,
            )
            validation_cancelled = any(
                run.outcome == "cancelled" for run in validation_runs
            )
            validation_failed = any(
                run.outcome != "succeeded" for run in validation_runs
            )
            outcome = (
                SourceEditOutcome.PARTIAL
                if (
                    validation_failed
                    or change_report.outcome == "incomplete"
                    or unexpected_changes
                )
                else SourceEditOutcome.SUCCEEDED
            )
            error_code = (
                "source_edit_cancelled"
                if validation_cancelled
                else
                "source_edit_validation_failed"
                if validation_failed
                else "source_edit_observation_incomplete"
                if change_report.outcome == "incomplete"
                else "source_edit_unexpected_change"
                if unexpected_changes
                else None
            )
        return SourceEditingResult(
            request_id=request.request_id,
            outcome=outcome,
            operation_results=tuple(results),
            validation_runs=validation_runs,
            source_change_report=change_report,
            error_code=error_code,
        )

    def _apply_operation(
        self,
        operation: SourceEditOperation,
        initial: FileSnapshot,
        token: WorkflowCancellationToken | None = None,
    ) -> str | None:
        self._check_write_authorization(operation)
        target = _resolve_edit_target(self.repository_root, operation.path)
        if initial.sha256 != operation.expected_sha256:
            raise SourceEditError("source_edit_conflict")
        current = _snapshot_one(self.repository_root, operation.path)
        if current.sha256 != operation.expected_sha256:
            raise SourceEditError("source_edit_conflict")

        original_mode: int | None = None
        if current.sha256 is not None:
            metadata = target.lstat()
            if not stat.S_ISREG(metadata.st_mode):
                raise SourceEditError("source_edit_path_unsafe")
            original_mode = stat.S_IMODE(metadata.st_mode)
        encoded = operation.content.encode("utf-8")
        temporary_path: Path | None = None
        file_descriptor = -1
        try:
            temporary_path, file_descriptor = self._create_staging_file(target)
            with os.fdopen(file_descriptor, "wb") as stream:
                file_descriptor = -1
                if stream.write(encoded) != len(encoded):
                    raise OSError("source_edit_short_write")
                stream.flush()
                if original_mode is not None:
                    self._set_file_mode(stream.fileno(), temporary_path, original_mode)
                os.fsync(stream.fileno())

            if os.name == "nt" and operation.expected_sha256 is not None:
                _copy_windows_file_dacl(target, temporary_path)
            if token is not None and token.is_cancelled:
                raise SourceEditCancelled
            self._check_write_authorization(operation)
            current_target = _resolve_edit_target(
                self.repository_root, operation.path
            )
            if current_target != target:
                raise SourceEditError("source_edit_path_unsafe")
            current = _snapshot_one(self.repository_root, operation.path)
            if current.sha256 != operation.expected_sha256:
                raise SourceEditError("source_edit_conflict")
            _validate_staging_file(temporary_path)
            if token is not None and token.is_cancelled:
                raise SourceEditCancelled
            self._check_write_authorization(operation)
            os.replace(temporary_path, target)
            temporary_path = None
        finally:
            if file_descriptor >= 0:
                os.close(file_descriptor)
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass
        return _snapshot_one(self.repository_root, operation.path).sha256

    def _create_staging_file(self, target: Path) -> tuple[Path, int]:
        for _ in range(10):
            candidate = target.with_name(
                f".{target.name}.{secrets.token_hex(16)}.tmp"
            )
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            flags |= getattr(os, "O_BINARY", 0)
            try:
                descriptor = os.open(candidate, flags, 0o600)
            except FileExistsError:
                continue
            return candidate, descriptor
        raise OSError("source_edit_staging_name_unavailable")

    def _check_write_authorization(
        self, operation: SourceEditOperation
    ) -> None:
        authorization = self.authorization
        if (
            authorization is None
            or authorization.repository_root != self.repository_root
            or operation.path not in authorization.authorized_paths
        ):
            raise SourceEditError("source_edit_blocked")

    @staticmethod
    def _set_file_mode(
        file_descriptor: int, temporary_path: Path, mode: int
    ) -> None:
        if hasattr(os, "fchmod"):
            os.fchmod(file_descriptor, mode)
        else:
            os.chmod(temporary_path, mode)

    def _rejected(
        self,
        request: SourceEditingRequest,
        error_code: str,
        before: RepositorySnapshot | None = None,
    ) -> SourceEditingResult:
        results = tuple(
            SourceEditOperationResult(
                operation.path,
                "blocked",
                None if before is None else next(
                    (
                        item.sha256
                        for item in before.files
                        if item.path == operation.path
                    ),
                    None,
                ),
                None,
                error_code,
            )
            for operation in request.operations
        )
        return SourceEditingResult(
            request.request_id,
            SourceEditOutcome.BLOCKED,
            results,
            self.validation_adapter.skip(
                request.validation_commands,
                "validation_skipped_because_edit_request_was_blocked",
            ),
            None,
            error_code,
        )


def _read_windows_security_descriptor(
    path: Path,
) -> tuple[ctypes.Array[ctypes.c_char], int]:
    if os.name != "nt":
        raise OSError("Windows security descriptors are unavailable on this platform.")
    from ctypes import wintypes

    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    get_file_security = advapi32.GetFileSecurityW
    get_file_security.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    get_file_security.restype = wintypes.BOOL
    dacl_security_information = 0x00000004
    required = wintypes.DWORD()
    get_file_security(
        str(path),
        dacl_security_information,
        None,
        0,
        ctypes.byref(required),
    )
    if ctypes.get_last_error() != 122 or required.value == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    descriptor = ctypes.create_string_buffer(required.value)
    if not get_file_security(
        str(path),
        dacl_security_information,
        descriptor,
        required.value,
        ctypes.byref(required),
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return descriptor, dacl_security_information


def _read_windows_file_dacl(path: Path) -> tuple[bool, bool, bytes | None]:
    if os.name != "nt":
        raise OSError("Windows DACLs are unavailable on this platform.")
    from ctypes import wintypes

    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    descriptor, _security_information = _read_windows_security_descriptor(path)
    get_dacl = advapi32.GetSecurityDescriptorDacl
    get_dacl.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(wintypes.BOOL),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(wintypes.BOOL),
    ]
    get_dacl.restype = wintypes.BOOL
    present = wintypes.BOOL()
    defaulted = wintypes.BOOL()
    acl_pointer = ctypes.c_void_p()
    if not get_dacl(
        ctypes.byref(descriptor),
        ctypes.byref(present),
        ctypes.byref(acl_pointer),
        ctypes.byref(defaulted),
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    if not present.value or not acl_pointer.value:
        return bool(present.value), bool(defaulted.value), None
    acl_size = ctypes.cast(acl_pointer, ctypes.POINTER(wintypes.WORD))[1]
    return (
        bool(present.value),
        bool(defaulted.value),
        ctypes.string_at(acl_pointer, acl_size),
    )


def _copy_windows_file_dacl(source: Path, destination: Path) -> None:
    from ctypes import wintypes

    descriptor, security_information = _read_windows_security_descriptor(source)
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    get_control = advapi32.GetSecurityDescriptorControl
    get_control.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(wintypes.WORD),
        ctypes.POINTER(wintypes.DWORD),
    ]
    get_control.restype = wintypes.BOOL
    control = wintypes.WORD()
    revision = wintypes.DWORD()
    if not get_control(ctypes.byref(descriptor), ctypes.byref(control), ctypes.byref(revision)):
        raise ctypes.WinError(ctypes.get_last_error())
    if control.value & 0x1000:
        security_information |= 0x80000000
    else:
        security_information |= 0x20000000

    set_file_security = advapi32.SetFileSecurityW
    set_file_security.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.c_void_p,
    ]
    set_file_security.restype = wintypes.BOOL
    if not set_file_security(
        str(destination),
        security_information,
        ctypes.byref(descriptor),
    ):
        raise ctypes.WinError(ctypes.get_last_error())


class SourceEditingSkillExecutionAdapter(SkillExecutionAdapter):
    """Connect the bounded edit workflow to the native implementation Skill."""

    def __init__(self, workflow: SourceEditingWorkflow) -> None:
        if not isinstance(workflow, SourceEditingWorkflow):
            raise ValueError("workflow must be a SourceEditingWorkflow.")
        self.workflow = workflow

    def supports(self, skill: SkillContract) -> bool:
        return isinstance(skill, SkillContract) and skill.identifier == "implementation"

    def execute(self, context: SkillExecutionContext) -> Mapping[str, object]:
        if not isinstance(context, SkillExecutionContext) or not self.supports(
            context.skill
        ):
            raise SkillExecutionFailure("source_edit_blocked")
        request = context.inputs.get("source_edit_request")
        if not isinstance(request, SourceEditingRequest):
            raise SkillExecutionFailure("source_edit_blocked")
        result = self.workflow.execute(request)
        if result.success:
            return {"source_editing_result": result.to_dict()}
        if result.outcome is SourceEditOutcome.CANCELLED:
            raise SkillExecutionFailure(
                "source_edit_cancelled",
                status=SkillExecutionStatus.CANCELLED,
                details={"source_editing_result": result.to_dict()},
            )
        error_code = result.error_code
        if error_code == "source_edit_conflict":
            safe_code = "source_edit_conflict"
        elif error_code == "source_edit_blocked":
            safe_code = "source_edit_blocked"
        elif error_code == "source_edit_validation_failed":
            safe_code = "source_edit_validation_failed"
        elif error_code == "source_edit_partial":
            safe_code = "source_edit_partial"
        else:
            safe_code = "source_edit_failed"
        raise SkillExecutionFailure(
            safe_code,
            details={"source_editing_result": result.to_dict()},
        )


def create_source_editing_pipeline(
    repository_root: Path,
    authorization: SourceWriteAuthorization,
    *,
    validation_adapter: ValidationCommandAdapter | None = None,
) -> SkillPipeline:
    """Create and discover a pipeline with the bounded editor explicitly wired."""
    if not isinstance(authorization, SourceWriteAuthorization):
        raise ValueError("authorization must be a SourceWriteAuthorization.")
    workflow = SourceEditingWorkflow(
        repository_root,
        authorization,
        validation_adapter=validation_adapter,
    )
    pipeline = SkillPipeline(
        repository_root,
        execution_adapter=SourceEditingSkillExecutionAdapter(workflow),
    )
    discovery = pipeline.discover()
    if "implementation" not in discovery.registered_identifiers:
        raise ValueError("the implementation Skill must be discoverable.")
    return pipeline


def _validate_relative_path(path: str) -> None:
    if (
        not isinstance(path, str)
        or not path
        or len(path) > 4096
        or "\\" in path
        or ":" in path
        or "\x00" in path
    ):
        raise ValueError("path must be a normalized repository-relative POSIX path.")
    relative = PurePosixPath(path)
    if (
        relative.is_absolute()
        or relative.as_posix() != path
        or not relative.parts
        or any(
            part in ("", ".", "..") or part.casefold() == ".git"
            for part in relative.parts
        )
    ):
        raise ValueError("path must be a normalized repository-relative POSIX path.")


def _resolve_edit_target(root: Path, relative_path: str) -> Path:
    _validate_relative_path(relative_path)
    components = PurePosixPath(relative_path).parts
    current = root
    for part in components[:-1]:
        current = current / part
        try:
            metadata = current.lstat()
        except OSError as error:
            raise SourceEditError("source_edit_path_unavailable") from error
        if (
            stat.S_ISLNK(metadata.st_mode)
            or current.is_junction()
            or not stat.S_ISDIR(metadata.st_mode)
        ):
            raise SourceEditError("source_edit_path_unsafe")
    target = current / components[-1]
    try:
        metadata = target.lstat()
    except FileNotFoundError:
        return target
    except OSError as error:
        raise SourceEditError("source_edit_path_unavailable") from error
    if stat.S_ISLNK(metadata.st_mode) or target.is_junction():
        raise SourceEditError("source_edit_path_unsafe")
    if not stat.S_ISREG(metadata.st_mode):
        raise SourceEditError("source_edit_path_unsafe")
    if not target.resolve(strict=True).is_relative_to(root):
        raise SourceEditError("source_edit_path_unsafe")
    return target


def _snapshot_one(root: Path, relative_path: str):
    try:
        return capture_repository_snapshot(root, (relative_path,)).files[0]
    except (OSError, SourceSnapshotError) as error:
        raise SourceEditError("source_edit_path_unavailable") from error


def _validate_staging_file(path: Path) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise SourceEditError("source_edit_path_unsafe") from error
    if (
        stat.S_ISLNK(metadata.st_mode)
        or path.is_junction()
        or not stat.S_ISREG(metadata.st_mode)
    ):
        raise SourceEditError("source_edit_path_unsafe")

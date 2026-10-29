"""Constrained local validation-command execution for implementation handoffs.

This adapter is not a sandbox and does not edit source code. It invokes only
fixed repository validation operations without a shell, from an explicit
repository root, under a reduced environment.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
from threading import Thread
from time import monotonic
from typing import BinaryIO, Mapping

from scripts.tool_workflow import (
    ImplementationStatus,
    ImplementationVerificationHandoff,
    ReleaseStatus,
    ValidationRunEvidence,
    VerificationOutcome,
    WorkflowEngine,
    WorkflowExecutionEvidence,
    WorkflowResult,
    WorkflowCancellationToken,
)
from scripts.source_change_evidence import (
    SourceSnapshotError,
    capture_repository_snapshot,
    compare_repository_snapshots,
    incomplete_source_change_report,
)


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")
_UNITTEST_MODULE_PATTERN = re.compile(r"tests\.test_[A-Za-z0-9_]+\Z")
_MAX_TIMEOUT_SECONDS = 300.0
_MAX_OUTPUT_BYTES = 16 * 1024


class ValidationOperation(str, Enum):
    UNITTEST = "unittest"
    MARKDOWN_LINKS = "markdown_links"
    PROVIDER_MANIFEST = "provider_manifest"
    GIT_DIFF_CHECK = "git_diff_check"
    GIT_CACHED_DIFF_CHECK = "git_cached_diff_check"


@dataclass(frozen=True, slots=True)
class ValidationCommand:
    """One explicitly selected operation from the adapter's fixed allowlist."""

    identifier: str
    operation: ValidationOperation
    targets: tuple[str, ...] = ()
    timeout_seconds: float = 60.0
    skip_reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.identifier
        ):
            raise ValueError("identifier must be a lowercase command identifier.")
        if not isinstance(self.operation, ValidationOperation):
            raise ValueError("operation must be a ValidationOperation.")
        if not isinstance(self.targets, tuple) or any(
            not isinstance(target, str) or not target.strip()
            for target in self.targets
        ):
            raise ValueError("targets must be a tuple of non-empty strings.")
        if (
            not isinstance(self.timeout_seconds, (int, float))
            or isinstance(self.timeout_seconds, bool)
            or not 0 < self.timeout_seconds <= _MAX_TIMEOUT_SECONDS
        ):
            raise ValueError(
                f"timeout_seconds must be greater than 0 and at most {_MAX_TIMEOUT_SECONDS:g}."
            )
        if self.skip_reason is not None and (
            not isinstance(self.skip_reason, str) or not self.skip_reason.strip()
        ):
            raise ValueError("skip_reason must be a non-empty string or None.")
        if self.operation is ValidationOperation.UNITTEST:
            if not self.targets or any(
                not _UNITTEST_MODULE_PATTERN.fullmatch(target)
                for target in self.targets
            ):
                raise ValueError(
                    "unittest targets must be explicit tests.test_<module> names."
                )
        elif self.operation is ValidationOperation.GIT_DIFF_CHECK:
            if len(self.targets) != len(set(self.targets)):
                raise ValueError("git diff check targets must be unique.")
            if len(self.targets) > 256 or sum(map(len, self.targets)) > 8192:
                raise ValueError("git diff check targets exceed the argument limit.")
            for target in self.targets:
                _validate_repository_relative_target(target)
        elif self.targets:
            raise ValueError(f"{self.operation.value} does not accept targets.")


@dataclass(frozen=True, slots=True)
class HandoffExecutionResult:
    """Result of running one registered tool workflow and its validations."""

    workflow_result: WorkflowResult
    validation_runs: tuple[ValidationRunEvidence, ...]
    handoff: ImplementationVerificationHandoff

    def __post_init__(self) -> None:
        if not isinstance(self.workflow_result, WorkflowResult):
            raise ValueError("workflow_result must be a WorkflowResult.")
        if not isinstance(self.validation_runs, tuple) or any(
            not isinstance(run, ValidationRunEvidence)
            for run in self.validation_runs
        ):
            raise ValueError("validation_runs must contain ValidationRunEvidence values.")
        if not isinstance(self.handoff, ImplementationVerificationHandoff):
            raise ValueError(
                "handoff must be an ImplementationVerificationHandoff."
            )
        workflow_evidence = self.handoff.workflow_execution
        if workflow_evidence is None:
            raise ValueError("handoff must contain workflow execution evidence.")
        expected_workflow_evidence = WorkflowExecutionEvidence(
            workflow_identifier=self.workflow_result.workflow_identifier,
            run_id=self.workflow_result.run_id,
            status=self.workflow_result.status,
            execution_began=self.workflow_result.execution_began,
            execution_completed=self.workflow_result.execution_completed,
            successful_step_count=self.workflow_result.successful_step_count,
            failed_step_count=self.workflow_result.failed_step_count,
            skipped_step_count=self.workflow_result.skipped_step_count,
            cancelled_step_count=self.workflow_result.cancelled_step_count,
            error_code=self.workflow_result.error_code,
        )
        if workflow_evidence != expected_workflow_evidence:
            raise ValueError(
                "handoff workflow evidence must match workflow_result."
            )
        if self.handoff.validation_runs != self.validation_runs:
            raise ValueError(
                "handoff validation runs must match validation_runs."
            )

    def to_json(self) -> str:
        """Return the connected result using the canonical handoff serializer."""
        return self.handoff.to_json()


class ValidationCommandAdapter:
    """Run only fixed, repository-local validation operations.

    This is a command runner, not an isolation boundary. Unit tests execute
    repository code with the current user's filesystem permissions.
    """

    def __init__(self, repository_root: Path) -> None:
        if not isinstance(repository_root, Path):
            raise ValueError("repository_root must be a pathlib.Path.")
        try:
            root = repository_root.resolve(strict=True)
        except OSError as error:
            raise ValueError("repository_root must exist and be accessible.") from error
        if not root.is_dir():
            raise ValueError("repository_root must be a directory.")
        self._root = root

    @property
    def repository_root(self) -> Path:
        return self._root

    def validate_commands(
        self, commands: tuple[ValidationCommand, ...]
    ) -> None:
        if not isinstance(commands, tuple) or not commands:
            raise ValueError("commands must be a non-empty tuple.")
        if any(not isinstance(command, ValidationCommand) for command in commands):
            raise ValueError("commands must contain ValidationCommand values.")
        identifiers = [command.identifier for command in commands]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("validation command identifiers must be unique.")

    def execute(
        self,
        commands: tuple[ValidationCommand, ...],
        *,
        cancellation_token: WorkflowCancellationToken | None = None,
    ) -> tuple[ValidationRunEvidence, ...]:
        """Execute commands in order and return actual, bounded outcomes."""
        self.validate_commands(commands)
        if cancellation_token is not None and not isinstance(
            cancellation_token, WorkflowCancellationToken
        ):
            raise ValueError("cancellation_token must be a WorkflowCancellationToken.")
        return tuple(
            self._execute_one(command, cancellation_token)
            for command in commands
        )

    def skip(
        self, commands: tuple[ValidationCommand, ...], reason: str
    ) -> tuple[ValidationRunEvidence, ...]:
        """Record commands as skipped without invoking a process."""
        self.validate_commands(commands)
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("skip reason must be a non-empty string.")
        return tuple(
            self._record(
                command,
                outcome="skipped",
                command_text=self._display_command(command),
                limitation=reason,
            )
            for command in commands
        )

    def _execute_one(
        self,
        command: ValidationCommand,
        cancellation_token: WorkflowCancellationToken | None = None,
    ) -> ValidationRunEvidence:
        command_text = self._display_command(command)
        if cancellation_token is not None and cancellation_token.is_cancelled:
            return self._record(
                command,
                outcome="cancelled",
                command_text=command_text,
                limitation="cancelled_before_start",
            )
        if command.skip_reason is not None:
            return self._record(
                command,
                outcome="skipped",
                command_text=command_text,
                limitation=command.skip_reason,
            )
        try:
            argv = self._build_argv(command)
        except (OSError, ValueError) as error:
            return self._record(
                command,
                outcome="blocked",
                command_text=command_text,
                limitation=str(error),
            )

        stdout_buffer = bytearray()
        stderr_buffer = bytearray()
        truncated = [False, False]
        started = monotonic()
        try:
            process = subprocess.Popen(
                argv,
                cwd=self._root,
                env=self._environment(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )
        except OSError as error:
            return self._record(
                command,
                outcome="blocked",
                command_text=command_text,
                limitation=f"process_start_failed:{type(error).__name__}",
                duration_seconds=max(0.0, monotonic() - started),
            )

        if process.stdout is None or process.stderr is None:
            process.kill()
            process.wait()
            return self._record(
                command,
                outcome="failed",
                command_text=command_text,
                exit_code=process.returncode or 1,
                limitation="process_output_unavailable",
                duration_seconds=max(0.0, monotonic() - started),
            )

        readers = (
            Thread(
                target=self._capture_output,
                args=(process.stdout, stdout_buffer, truncated, 0),
                daemon=True,
            ),
            Thread(
                target=self._capture_output,
                args=(process.stderr, stderr_buffer, truncated, 1),
                daemon=True,
            ),
        )
        for reader in readers:
            reader.start()
        timed_out = False
        cancelled = False
        deadline = started + command.timeout_seconds
        try:
            while True:
                if cancellation_token is not None and cancellation_token.is_cancelled:
                    cancelled = True
                    process.kill()
                    exit_code = process.wait()
                    break
                remaining = deadline - monotonic()
                if remaining <= 0:
                    timed_out = True
                    process.kill()
                    exit_code = process.wait()
                    break
                try:
                    exit_code = process.wait(timeout=min(remaining, 0.05))
                    break
                except subprocess.TimeoutExpired:
                    continue
        finally:
            for reader in readers:
                reader.join()
            process.stdout.close()
            process.stderr.close()

        duration = max(0.0, monotonic() - started)
        captured_stdout = bytes(stdout_buffer).decode("utf-8", errors="replace")
        captured_stderr = bytes(stderr_buffer).decode("utf-8", errors="replace")
        output_truncated = any(truncated)
        if cancelled:
            outcome = "cancelled"
            limitation = "cancelled_by_request"
            exit_code = None
        elif timed_out:
            outcome = "timed_out"
            limitation = "command_timeout"
            exit_code = None
        elif exit_code == 0:
            outcome = "succeeded"
            limitation = ""
        else:
            outcome = "failed"
            limitation = ""
        return ValidationRunEvidence(
            command_id=command.identifier,
            operation=command.operation.value,
            command=command_text,
            outcome=outcome,
            exit_code=exit_code,
            stdout=captured_stdout,
            stderr=captured_stderr,
            duration_seconds=duration,
            limitation=limitation,
            output_truncated=output_truncated,
        )

    def _build_argv(self, command: ValidationCommand) -> tuple[str, ...]:
        if command.operation is ValidationOperation.UNITTEST:
            for module in command.targets:
                relative = Path(*module.split(".")).with_suffix(".py")
                self._resolve_repository_file(relative.as_posix())
            return (sys.executable, "-B", "-m", "unittest", *command.targets)
        if command.operation is ValidationOperation.MARKDOWN_LINKS:
            script = self._resolve_repository_file("scripts/check_markdown_links.py")
            return (sys.executable, "-B", str(script))
        if command.operation is ValidationOperation.PROVIDER_MANIFEST:
            self._resolve_repository_file("scripts/check_provider_manifest.py")
            return (
                sys.executable,
                "-B",
                "-m",
                "scripts.check_provider_manifest",
                "--repository-root",
                str(self._root),
            )
        git = shutil.which("git")
        if git is None:
            raise OSError("git_executable_unavailable")
        if command.operation is ValidationOperation.GIT_DIFF_CHECK:
            argv = [
                git,
                "--literal-pathspecs",
                "-c",
                "core.whitespace=cr-at-eol",
                "diff",
                "--check",
            ]
            if command.targets:
                argv.extend(("--", *command.targets))
            return tuple(argv)
        if command.operation is ValidationOperation.GIT_CACHED_DIFF_CHECK:
            return (
                git,
                "-c",
                "core.whitespace=cr-at-eol",
                "diff",
                "--cached",
                "--check",
            )
        raise ValueError("validation operation is not allowed.")

    def _resolve_repository_file(self, relative_path: str) -> Path:
        relative = PurePosixPath(relative_path)
        if relative.is_absolute() or any(
            part in ("", ".", "..") for part in relative.parts
        ):
            raise ValueError("validation target must be a normalized repository-relative path.")
        candidate = self._root.joinpath(*relative.parts)
        current = self._root
        for part in relative.parts:
            current = current / part
            if current.is_symlink() or current.is_junction():
                raise ValueError(
                    "validation target cannot traverse a symlink or junction."
                )
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError as error:
            raise ValueError(
                "validation target must be an existing file inside repository_root."
            ) from error
        if self._root not in resolved.parents or not resolved.is_file():
            raise ValueError("validation target must be a file inside repository_root.")
        return resolved

    def _environment(self) -> dict[str, str]:
        env: dict[str, str] = {}
        for name in ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP"):
            value = os.environ.get(name)
            if value:
                env[name] = value
        env.update(
            {
                "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONUTF8": "1",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_OPTIONAL_LOCKS": "0",
                "GIT_TERMINAL_PROMPT": "0",
            }
        )
        return env

    @staticmethod
    def _capture_output(
        stream: BinaryIO,
        buffer: bytearray,
        truncation_flags: list[bool],
        index: int,
    ) -> None:
        while chunk := stream.read(4096):
            remaining = _MAX_OUTPUT_BYTES - len(buffer)
            if remaining > 0:
                buffer.extend(chunk[:remaining])
            if len(chunk) > remaining:
                truncation_flags[index] = True

    def _display_command(self, command: ValidationCommand) -> str:
        if command.operation is ValidationOperation.UNITTEST:
            args = ("python", "-B", "-m", "unittest", *command.targets)
        elif command.operation is ValidationOperation.MARKDOWN_LINKS:
            args = ("python", "-B", "scripts/check_markdown_links.py")
        elif command.operation is ValidationOperation.PROVIDER_MANIFEST:
            args = (
                "python",
                "-B",
                "-m",
                "scripts.check_provider_manifest",
                "--repository-root",
                str(self._root),
            )
        elif command.operation is ValidationOperation.GIT_DIFF_CHECK:
            args = (
                "git",
                "--literal-pathspecs",
                "-c",
                "core.whitespace=cr-at-eol",
                "diff",
                "--check",
                *(("--", *command.targets) if command.targets else ()),
            )
        else:
            args = (
                "git",
                "-c",
                "core.whitespace=cr-at-eol",
                "diff",
                "--cached",
                "--check",
            )
        return subprocess.list2cmdline(args)

    @staticmethod
    def _record(
        command: ValidationCommand,
        *,
        outcome: str,
        command_text: str,
        exit_code: int | None = None,
        limitation: str = "",
        duration_seconds: float = 0.0,
    ) -> ValidationRunEvidence:
        return ValidationRunEvidence(
            command_id=command.identifier,
            operation=command.operation.value,
            command=command_text,
            outcome=outcome,
            exit_code=exit_code,
            stdout="",
            stderr="",
            duration_seconds=duration_seconds,
            limitation=limitation,
        )


def execute_handoff_workflow(
    engine: WorkflowEngine,
    workflow_identifier: str,
    workflow_inputs: Mapping[str, object],
    adapter: ValidationCommandAdapter,
    commands: tuple[ValidationCommand, ...],
    handoff: ImplementationVerificationHandoff,
    *,
    source_paths: tuple[str, ...] | None = None,
) -> HandoffExecutionResult:
    """Execute a configured tool workflow, then validations, and attach evidence.

    Validation commands are skipped when the tool workflow does not succeed.
    Neither stage changes the handoff's implementation, verification,
    authorization, or release status. If source_paths is supplied, changes to
    exactly those paths are observed before validation; this is not a write
    permission boundary or authenticated proof of authorship.
    """
    if not isinstance(engine, WorkflowEngine):
        raise ValueError("engine must be a WorkflowEngine.")
    if not isinstance(workflow_identifier, str) or not workflow_identifier.strip():
        raise ValueError("workflow_identifier must be a non-empty string.")
    if not isinstance(workflow_inputs, Mapping):
        raise ValueError("workflow_inputs must be a mapping.")
    if not isinstance(adapter, ValidationCommandAdapter):
        raise ValueError("adapter must be a ValidationCommandAdapter.")
    if not isinstance(handoff, ImplementationVerificationHandoff):
        raise ValueError("handoff must be an ImplementationVerificationHandoff.")
    adapter.validate_commands(commands)
    source_baseline = None
    if source_paths is not None:
        if handoff.source_change_report is not None or handoff.files_changed:
            raise ValueError(
                "source_paths requires a handoff without pre-existing changed-file evidence."
            )
        source_baseline = capture_repository_snapshot(
            adapter.repository_root, source_paths
        )

    workflow_result = engine.execute(workflow_identifier, workflow_inputs)
    attached = workflow_result.attach_to_handoff(handoff)
    if source_baseline is not None:
        try:
            source_after = capture_repository_snapshot(
                adapter.repository_root, source_baseline.scope_paths
            )
        except SourceSnapshotError as error:
            source_report = incomplete_source_change_report(
                source_baseline.scope_paths,
                f"post_workflow_snapshot_failed:{type(error).__name__}",
            )
        else:
            source_report = compare_repository_snapshots(
                source_baseline, source_after
            )
        attached = attached.attach_source_change_report(source_report)
    if workflow_result.success:
        validation_runs = adapter.execute(commands)
    else:
        validation_runs = adapter.skip(
            commands,
            "validation_skipped_because_tool_workflow_did_not_succeed",
        )
    attached = attached.attach_validation_runs(validation_runs)
    return HandoffExecutionResult(workflow_result, validation_runs, attached)


def execute_validation_handoff(
    adapter: ValidationCommandAdapter,
    commands: tuple[ValidationCommand, ...],
    handoff: ImplementationVerificationHandoff,
) -> ImplementationVerificationHandoff:
    """Run configured validations and attach their actual outcomes to a handoff.

    This validation-only entry point is useful when an implementation has
    already been performed by an external, explicitly authorized editor. It
    does not create workflow, implementation, verification, or release
    evidence.
    """
    if not isinstance(adapter, ValidationCommandAdapter):
        raise ValueError("adapter must be a ValidationCommandAdapter.")
    if not isinstance(handoff, ImplementationVerificationHandoff):
        raise ValueError("handoff must be an ImplementationVerificationHandoff.")
    if handoff.validation_runs:
        raise ValueError("handoff already contains validation run evidence.")
    validation_runs = adapter.execute(commands)
    return handoff.attach_validation_runs(validation_runs)


def _validate_repository_relative_target(target: str) -> None:
    if (
        not target
        or len(target) > 4096
        or "\\" in target
        or ":" in target
        or "\x00" in target
    ):
        raise ValueError(
            "git diff targets must be normalized repository-relative paths."
        )
    relative = PurePosixPath(target)
    if (
        relative.is_absolute()
        or relative.as_posix() != target
        or not relative.parts
        or any(
            part in ("", ".", "..") or part.casefold() == ".git"
            for part in relative.parts
        )
    ):
        raise ValueError(
            "git diff targets must be normalized repository-relative paths."
        )


def _validation_commands_from_args(
    args: argparse.Namespace,
) -> tuple[ValidationCommand, ...]:
    commands = [
        ValidationCommand(
            f"unittest-{index}",
            ValidationOperation.UNITTEST,
            (module,),
            timeout_seconds=args.timeout_seconds,
        )
        for index, module in enumerate(args.unittest, start=1)
    ]
    for selected, identifier, operation in (
        (
            args.markdown_links,
            "markdown-links",
            ValidationOperation.MARKDOWN_LINKS,
        ),
        (
            args.provider_manifest_check,
            "provider-manifest-check",
            ValidationOperation.PROVIDER_MANIFEST,
        ),
        (
            args.git_diff_check,
            "git-diff-check",
            ValidationOperation.GIT_DIFF_CHECK,
        ),
        (
            args.git_cached_diff_check,
            "git-cached-diff-check",
            ValidationOperation.GIT_CACHED_DIFF_CHECK,
        ),
    ):
        if selected:
            commands.append(
                ValidationCommand(
                    identifier,
                    operation,
                    timeout_seconds=args.timeout_seconds,
                )
            )
    return tuple(commands)


def main(argv: list[str] | None = None) -> int:
    """CLI for running only allowlisted validations and serializing a handoff."""
    parser = argparse.ArgumentParser(
        description=(
            "Run explicitly selected repository validation checks and emit "
            "their actual outcomes as a handoff JSON document."
        )
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--task-objective", required=True)
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=60.0,
        metavar="SECONDS",
        help=(
            "maximum duration for each selected operation "
            f"(greater than 0 and at most {_MAX_TIMEOUT_SECONDS:g}; default: 60)"
        ),
    )
    parser.add_argument(
        "--unittest",
        action="append",
        default=[],
        metavar="tests.test_MODULE",
        help="run one explicit tests.test_* module (repeatable)",
    )
    parser.add_argument(
        "--markdown-links",
        action="store_true",
        help="run scripts/check_markdown_links.py",
    )
    parser.add_argument(
        "--provider-manifest-check",
        action="store_true",
        help=(
            "check local Claude plugin manifest against canonical Skills; "
            "does not invoke the provider runtime"
        ),
    )
    parser.add_argument(
        "--git-diff-check",
        action="store_true",
        help="run git diff --check",
    )
    parser.add_argument(
        "--git-cached-diff-check",
        action="store_true",
        help="run git diff --cached --check",
    )
    args = parser.parse_args(argv)
    try:
        commands = _validation_commands_from_args(args)
    except ValueError as error:
        parser.error(str(error))
    if not commands:
        parser.error("select at least one validation operation.")

    try:
        adapter = ValidationCommandAdapter(args.repository_root)
        handoff = ImplementationVerificationHandoff(
            task_objective=args.task_objective,
            status=ImplementationStatus.NOT_RUN,
            verification_status=VerificationOutcome.NOT_RUN,
            release_status=ReleaseStatus.UNKNOWN,
            next_action=(
                "Review validation evidence separately; implementation, "
                "authorization, and release are not established by this command."
            ),
        )
        result = execute_validation_handoff(adapter, commands, handoff)
    except ValueError as error:
        parser.error(str(error))

    print(result.to_json())
    return int(any(run.outcome != "succeeded" for run in result.validation_runs))


if __name__ == "__main__":
    raise SystemExit(main())

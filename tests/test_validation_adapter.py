from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from io import StringIO
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from threading import Thread
from time import sleep
from typing import Mapping
from unittest.mock import patch

from scripts.tool_framework import (
    ExecutionAvailability,
    InputField,
    InputType,
    LocalToolAdapter,
    ToolContract,
    ToolExecutor,
    ToolRegistry,
    ToolRuntimeError,
)
from scripts.tool_workflow import (
    ImplementationStatus,
    ImplementationVerificationHandoff,
    ReleaseStatus,
    VerificationOutcome,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowInputRef,
    WorkflowRegistry,
    WorkflowStep,
    WorkflowCancellationToken,
    ValidationRunEvidence,
)
from scripts.validation_adapter import (
    HandoffExecutionResult,
    ValidationCommand,
    ValidationCommandAdapter,
    ValidationOperation,
    execute_handoff_workflow,
    main,
)


class ValidationCommandAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.tests_directory = self.root / "tests"
        self.tests_directory.mkdir()
        (self.tests_directory / "__init__.py").write_text("", encoding="utf-8")
        self.adapter = ValidationCommandAdapter(self.root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _write_test_module(self, name: str, source: str) -> None:
        (self.tests_directory / f"{name}.py").write_text(source, encoding="utf-8")

    def test_runs_real_allowlisted_unittest_and_captures_success(self):
        self._write_test_module(
            "test_adapter_success",
            "import unittest\n"
            "class ExampleTest(unittest.TestCase):\n"
            "    def test_passes(self):\n"
            "        self.assertEqual(2 + 2, 4)\n",
        )

        (self.root / "scripts").mkdir()
        (self.root / "scripts" / "check_markdown_links.py").write_text(
            "raise SystemExit('should not be called')\n", encoding="utf-8"
        )
        command = ValidationCommand(
            "unit-tests",
            ValidationOperation.UNITTEST,
            ("tests.test_adapter_success",),
        )

        (self.root / "README.md").write_text("# Temporary fixture\n", encoding="utf-8")
        with tempfile.TemporaryDirectory() as git_directory:
            git_root = Path(git_directory)
            subprocess.run(
                ["git", "init", "--quiet"],
                cwd=git_root,
                check=True,
                capture_output=True,
                text=True,
            )
            real_root_adapter = ValidationCommandAdapter(git_root)
            real_git_check = real_root_adapter.execute(
                (
                    ValidationCommand(
                        "git-diff",
                        ValidationOperation.GIT_DIFF_CHECK,
                    ),
                ),
            )[0]
        self.assertEqual(real_git_check.outcome, "succeeded", real_git_check.stderr)
        self.assertEqual(real_git_check.exit_code, 0)

        result = self.adapter.execute((command,))[0]

        self.assertEqual(result.outcome, "succeeded")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("unittest", result.command)

    def test_real_nonzero_unittest_exit_is_failed_not_success(self):
        self._write_test_module(
            "test_adapter_failure",
            "import unittest\n"
            "class ExampleTest(unittest.TestCase):\n"
            "    def test_fails(self):\n"
            "        self.fail('expected fixture failure')\n",
        )
        result = self.adapter.execute(
            (
                ValidationCommand(
                    "failing-tests",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_failure",),
                ),
            )
        )[0]

        self.assertEqual(result.outcome, "failed")
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("expected fixture failure", result.stderr)

    def test_cancellation_terminates_running_validation_process(self):
        token = WorkflowCancellationToken()
        command = ValidationCommand(
            "cancellable",
            ValidationOperation.GIT_DIFF_CHECK,
            timeout_seconds=10,
        )
        launched: list[subprocess.Popen[bytes]] = []
        original_popen = subprocess.Popen

        def tracked_popen(*args, **kwargs):
            process = original_popen(*args, **kwargs)
            launched.append(process)
            return process

        def request_cancel() -> None:
            sleep(0.15)
            token.request_cancel()

        cancel_thread = Thread(target=request_cancel, daemon=True)
        with (
            patch.object(
                self.adapter,
                "_build_argv",
                return_value=(sys.executable, "-c", "import time; time.sleep(30)"),
            ),
            patch(
                "scripts.validation_adapter.subprocess.Popen",
                side_effect=tracked_popen,
            ),
        ):
            cancel_thread.start()
            result = self.adapter.execute(
                (command,),
                cancellation_token=token,
            )[0]
            cancel_thread.join(timeout=2)

        self.assertEqual(result.outcome, "cancelled")
        self.assertEqual(result.limitation, "cancelled_by_request")
        self.assertEqual(len(launched), 1)
        self.assertIsNotNone(launched[0].poll())

    def test_pre_cancelled_validation_does_not_start_a_process(self):
        token = WorkflowCancellationToken()
        token.request_cancel()
        command = ValidationCommand(
            "already-cancelled",
            ValidationOperation.GIT_DIFF_CHECK,
        )

        with patch(
            "scripts.validation_adapter.subprocess.Popen",
            side_effect=AssertionError("cancelled command must not launch"),
        ):
            result = self.adapter.execute(
                (command,),
                cancellation_token=token,
            )[0]

        self.assertEqual(result.outcome, "cancelled")
        self.assertEqual(result.limitation, "cancelled_before_start")
        self.assertIsNone(result.exit_code)

    def test_git_diff_check_scopes_to_literal_repository_paths(self):
        command = ValidationCommand(
            "scoped-diff",
            ValidationOperation.GIT_DIFF_CHECK,
            ("tests/test_validation.py",),
        )

        argv = self.adapter._build_argv(command)

        self.assertIn("--literal-pathspecs", argv)
        self.assertEqual(
            argv[-3:],
            ("--check", "--", "tests/test_validation.py"),
        )

    def test_rejects_unsupported_commands_and_protected_test_modules(self):
        with self.assertRaisesRegex(ValueError, "ValidationOperation"):
            ValidationCommand("shell", "powershell")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "explicit tests.test_"):
            ValidationCommand(
                "protected",
                ValidationOperation.UNITTEST,
                ("tests.skills.repository_audit.test_validate_skill",),
            )
        with self.assertRaisesRegex(ValueError, "normalized repository-relative"):
            ValidationCommand(
                "git-with-args",
                ValidationOperation.GIT_DIFF_CHECK,
                ("../outside.txt",),
            )
        with self.assertRaisesRegex(ValueError, "must be unique"):
            ValidationCommand(
                "duplicate-diff-path",
                ValidationOperation.GIT_DIFF_CHECK,
                ("src/file.txt", "src/file.txt"),
            )
        with self.assertRaisesRegex(ValueError, "argument limit"):
            ValidationCommand(
                "oversized-diff-paths",
                ValidationOperation.GIT_DIFF_CHECK,
                ("a" * 4096, "b" * 4096, "c"),
            )

    def test_missing_target_is_blocked_without_process_execution(self):
        result = self.adapter.execute(
            (
                ValidationCommand(
                    "missing-tests",
                    ValidationOperation.UNITTEST,
                    ("tests.test_missing_adapter_target",),
                ),
            )
        )[0]

        self.assertEqual(result.outcome, "blocked")
        self.assertIsNone(result.exit_code)
        self.assertIn("existing file inside repository_root", result.limitation)

    def test_symlink_target_cannot_escape_repository_root(self):
        outside_directory = self.root.parent / f"{self.root.name}-outside"
        outside_directory.mkdir()
        outside_file = outside_directory / "test_adapter_escape.py"
        outside_file.write_text("raise SystemExit(0)\n", encoding="utf-8")
        link = self.tests_directory / "test_adapter_symlink.py"
        try:
            link.symlink_to(outside_file)
        except OSError as error:
            outside_file.unlink(missing_ok=True)
            outside_directory.rmdir()
            self.skipTest(f"symlink creation is unavailable: {error}")
        try:
            result = self.adapter.execute(
                (
                    ValidationCommand(
                        "symlink-tests",
                        ValidationOperation.UNITTEST,
                        ("tests.test_adapter_symlink",),
                    ),
                )
            )[0]
            self.assertEqual(result.outcome, "blocked")
            self.assertIsNone(result.exit_code)
            self.assertIn("cannot traverse a symlink", result.limitation)
        finally:
            outside_file.unlink(missing_ok=True)
            outside_directory.rmdir()

    def test_junction_target_is_rejected_before_execution(self):
        test_module = self.tests_directory / "test_junction_target.py"
        test_module.write_text("raise SystemExit(0)\n", encoding="utf-8")
        original_is_junction = Path.is_junction

        def is_junction(path: Path) -> bool:
            if path == self.tests_directory:
                return True
            return original_is_junction(path)

        with patch.object(Path, "is_junction", is_junction):
            result = self.adapter.execute(
                (
                    ValidationCommand(
                        "junction-tests",
                        ValidationOperation.UNITTEST,
                        ("tests.test_junction_target",),
                    ),
                )
            )[0]

        self.assertEqual(result.outcome, "blocked")
        self.assertIsNone(result.exit_code)
        self.assertIn("cannot traverse a symlink or junction", result.limitation)

    def test_skip_is_recorded_without_execution(self):
        result = self.adapter.execute(
            (
                ValidationCommand(
                    "deferred",
                    ValidationOperation.GIT_DIFF_CHECK,
                    skip_reason="No Git checkout is available for this fixture.",
                ),
            )
        )[0]

        self.assertEqual(result.outcome, "skipped")
        self.assertIsNone(result.exit_code)
        self.assertIn("No Git checkout", result.limitation)

    def test_execution_timeout_is_distinct_from_failure(self):
        self._write_test_module(
            "test_adapter_slow",
            "import time\n"
            "import unittest\n"
            "class SlowTest(unittest.TestCase):\n"
            "    def test_waits(self):\n"
            "        time.sleep(2)\n",
        )
        result = self.adapter.execute(
            (
                ValidationCommand(
                    "slow-tests",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_slow",),
                    timeout_seconds=0.1,
                ),
            )
        )[0]

        self.assertEqual(result.outcome, "timed_out")
        self.assertIsNone(result.exit_code)
        self.assertEqual(result.limitation, "command_timeout")

    def test_output_is_captured_with_a_bounded_size(self):
        self._write_test_module(
            "test_adapter_output",
            "import unittest\n"
            "print('x' * 20000)\n"
            "class OutputTest(unittest.TestCase):\n"
            "    def test_passes(self):\n"
            "        self.assertTrue(True)\n",
        )
        result = self.adapter.execute(
            (
                ValidationCommand(
                    "output-tests",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_output",),
                ),
            )
        )[0]

        self.assertEqual(result.outcome, "succeeded")
        self.assertTrue(result.output_truncated)
        self.assertLessEqual(len(result.stdout.encode("utf-8")), 16 * 1024)

    def test_provider_manifest_operation_executes_the_repository_checker(self):
        repository_root = Path(__file__).resolve().parents[1]
        adapter = ValidationCommandAdapter(repository_root)

        result = adapter.execute(
            (
                ValidationCommand(
                    "provider-manifest",
                    ValidationOperation.PROVIDER_MANIFEST,
                ),
            )
        )[0]

        self.assertEqual(result.outcome, "succeeded", result.stderr)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("scripts.check_provider_manifest", result.command)
        self.assertIn("canonical Skill discovery", result.stdout)

    def test_provider_manifest_subprocess_failure_is_preserved_in_evidence(self):
        repository_root = Path(__file__).resolve().parents[1]
        scripts_directory = self.root / "scripts"
        scripts_directory.mkdir()
        (scripts_directory / "__init__.py").write_text("", encoding="utf-8")
        for script_name in ("check_provider_manifest.py", "skill_registry.py"):
            shutil.copy2(
                repository_root / "scripts" / script_name,
                scripts_directory / script_name,
            )
        plugin_directory = self.root / ".claude-plugin"
        plugin_directory.mkdir()
        (plugin_directory / "plugin.json").write_text("{", encoding="utf-8")

        result = self.adapter.execute(
            (
                ValidationCommand(
                    "invalid-provider-manifest",
                    ValidationOperation.PROVIDER_MANIFEST,
                ),
            )
        )[0]

        self.assertEqual(result.outcome, "failed")
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("JSONDecodeError", result.stderr)
        self.assertFalse(result.output_truncated)

    def test_validation_evidence_rejects_inconsistent_or_invalid_outcomes(self):
        valid = {
            "command_id": "unit-tests",
            "operation": "unittest",
            "command": "python -B -m unittest tests.test_example",
            "outcome": "succeeded",
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "duration_seconds": 0.1,
        }
        with self.assertRaisesRegex(ValueError, "supported validation run status"):
            ValidationRunEvidence(**{**valid, "outcome": []})
        with self.assertRaisesRegex(ValueError, "non-negative number"):
            ValidationRunEvidence(**{**valid, "duration_seconds": float("nan")})
        with self.assertRaisesRegex(ValueError, "require exit_code 0"):
            ValidationRunEvidence(**{**valid, "exit_code": None})
        with self.assertRaisesRegex(ValueError, "require a non-zero exit code"):
            ValidationRunEvidence(**{**valid, "outcome": "failed", "exit_code": 0})


class HandoffExecutionIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        tests_directory = self.root / "tests"
        tests_directory.mkdir()
        (tests_directory / "__init__.py").write_text("", encoding="utf-8")
        (tests_directory / "test_adapter_integration.py").write_text(
            "import unittest\n"
            "class IntegrationCheck(unittest.TestCase):\n"
            "    def test_passes(self):\n"
            "        self.assertEqual('ok', 'ok')\n",
            encoding="utf-8",
        )
        (tests_directory / "test_adapter_integration_failure.py").write_text(
            "import unittest\n"
            "class IntegrationFailureCheck(unittest.TestCase):\n"
            "    def test_fails(self):\n"
            "        self.fail('expected validation failure')\n",
            encoding="utf-8",
        )
        scripts = self.root / "scripts"
        scripts.mkdir()
        (scripts / "check_markdown_links.py").write_text(
            "raise SystemExit('unused')\n", encoding="utf-8"
        )
        self.tools = ToolRegistry()
        self.tools.register(
            ToolContract(
                identifier="local.echo",
                name="Echo",
                description="Return a safe summary of the input.",
                input_schema=(InputField("text", InputType.STRING),),
                adapter_id="local.validation-test",
                execution_availability=ExecutionAvailability.AVAILABLE,
            )
        )

        def echo(inputs: Mapping[str, object]) -> Mapping[str, object]:
            return {"characters": len(str(inputs["text"]))}

        self.executor = ToolExecutor(self.tools)
        self.executor.register_adapter(
            LocalToolAdapter("local.validation-test", {"local.echo": echo})
        )
        self.workflows = WorkflowRegistry()
        self.workflows.register(
            WorkflowDefinition(
                "workflow.handoff",
                "Handoff integration",
                (
                    WorkflowStep(
                        "echo",
                        "local.echo",
                        {"text": WorkflowInputRef("request")},
                    ),
                ),
            )
        )
        self.engine = WorkflowEngine(self.workflows, self.tools, self.executor)
        self.adapter = ValidationCommandAdapter(self.root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _handoff(self) -> ImplementationVerificationHandoff:
        return ImplementationVerificationHandoff(
            task_objective="Exercise the supported workflow and validation path.",
            status=ImplementationStatus.PARTIAL,
            verification_status=VerificationOutcome.NOT_RUN,
            release_status=ReleaseStatus.NOT_APPROVED,
            next_action="A verifier must inspect validation evidence separately.",
        )

    def test_entry_point_runs_tool_workflow_validation_and_serializes_actual_results(self):
        result = execute_handoff_workflow(
            self.engine,
            "workflow.handoff",
            {"request": "secret-like input omitted from trace"},
            self.adapter,
            (
                ValidationCommand(
                    "integration-test",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_integration",),
                ),
            ),
            self._handoff(),
        )

        self.assertIsInstance(result, HandoffExecutionResult)
        self.assertEqual(result.workflow_result.status.value, "succeeded")
        self.assertEqual(result.validation_runs[0].outcome, "succeeded")
        serialized = json.loads(result.to_json())
        self.assertEqual(
            serialized["workflow_execution"]["status"], "succeeded"
        )
        self.assertEqual(
            serialized["validation_runs"][0]["exit_code"], 0
        )
        self.assertEqual(serialized["verification_status"], "not_run")
        self.assertEqual(serialized["release_status"], "not_approved")
        self.assertNotIn("secret-like input", result.to_json())

    def test_workflow_file_write_is_observed_in_serialized_handoff(self):
        source_file = self.root / "src" / "implementation.py"
        source_file.parent.mkdir()
        source_file.write_text("before = True\n", encoding="utf-8")
        self._register_source_writer(source_file)

        result = execute_handoff_workflow(
            self.engine,
            "workflow.source-write",
            {"content": "after = True\n"},
            self.adapter,
            (
                ValidationCommand(
                    "integration-test",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_integration",),
                ),
            ),
            self._handoff(),
            source_paths=("src/implementation.py",),
        )

        self.assertEqual(result.workflow_result.status.value, "succeeded")
        self.assertEqual(result.validation_runs[0].outcome, "succeeded")
        self.assertEqual(
            result.handoff.files_changed,
            ("src/implementation.py",),
        )
        serialized = json.loads(result.to_json())
        report = serialized["source_change_report"]
        self.assertFalse(report["authenticated"])
        self.assertEqual(report["outcome"], "observed")
        self.assertEqual(report["changes"][0]["kind"], "modified")
        self.assertEqual(serialized["verification_status"], "not_run")
        self.assertEqual(serialized["release_status"], "not_approved")

    def test_failed_workflow_preserves_partial_file_changes_and_skips_validation(self):
        source_file = self.root / "src" / "partial.py"
        source_file.parent.mkdir()
        source_file.write_text("before = True\n", encoding="utf-8")
        self._register_source_writer(source_file, fail_after_write=True)

        result = execute_handoff_workflow(
            self.engine,
            "workflow.source-write",
            {"content": "partial = True\n"},
            self.adapter,
            (
                ValidationCommand(
                    "integration-test",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_integration",),
                ),
            ),
            self._handoff(),
            source_paths=("src/partial.py",),
        )

        self.assertEqual(result.workflow_result.status.value, "failed")
        self.assertEqual(result.validation_runs[0].outcome, "skipped")
        self.assertEqual(result.handoff.files_changed, ("src/partial.py",))
        serialized = json.loads(result.to_json())
        self.assertEqual(
            serialized["source_change_report"]["changes"][0]["kind"],
            "modified",
        )
        self.assertEqual(serialized["verification_status"], "not_run")
        self.assertEqual(serialized["release_status"], "not_approved")

    def test_post_workflow_snapshot_failure_is_reported_as_incomplete(self):
        source_file = self.root / "src" / "replaced.py"
        source_file.parent.mkdir()
        source_file.write_text("before = True\n", encoding="utf-8")
        self._register_source_writer(source_file, replace_target_with_directory=True)

        result = execute_handoff_workflow(
            self.engine,
            "workflow.source-write",
            {"content": "not used\n"},
            self.adapter,
            (
                ValidationCommand(
                    "integration-test",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_integration",),
                ),
            ),
            self._handoff(),
            source_paths=("src/replaced.py",),
        )

        serialized = json.loads(result.to_json())
        report = serialized["source_change_report"]
        self.assertEqual(result.workflow_result.status.value, "succeeded")
        self.assertEqual(report["outcome"], "incomplete")
        self.assertEqual(
            report["limitations"],
            ["post_workflow_snapshot_failed:SourceSnapshotError"],
        )
        self.assertEqual(serialized["files_changed"], [])
        self.assertEqual(serialized["validation_runs"][0]["outcome"], "succeeded")

    def test_invalid_source_scope_blocks_workflow_before_execution(self):
        invoked = False

        def mark_invoked(inputs: Mapping[str, object]) -> Mapping[str, object]:
            nonlocal invoked
            invoked = True
            return {"characters": len(str(inputs["text"]))}

        tools = ToolRegistry()
        tools.register(
            ToolContract(
                identifier="local.mark",
                name="Mark invocation",
                description="Record whether the workflow was invoked.",
                input_schema=(InputField("text", InputType.STRING),),
                adapter_id="local.marker",
                execution_availability=ExecutionAvailability.AVAILABLE,
            )
        )
        executor = ToolExecutor(tools)
        executor.register_adapter(
            LocalToolAdapter("local.marker", {"local.mark": mark_invoked})
        )
        workflows = WorkflowRegistry()
        workflows.register(
            WorkflowDefinition(
                "workflow.mark",
                "Invocation marker workflow",
                (
                    WorkflowStep(
                        "mark",
                        "local.mark",
                        {"text": WorkflowInputRef("request")},
                    ),
                ),
            )
        )
        engine = WorkflowEngine(workflows, tools, executor)
        with self.assertRaisesRegex(ValueError, "normalized repository-relative"):
            execute_handoff_workflow(
                engine,
                "workflow.mark",
                {"request": "should not execute"},
                self.adapter,
                (
                    ValidationCommand(
                        "integration-test",
                        ValidationOperation.UNITTEST,
                        ("tests.test_adapter_integration",),
                    ),
                ),
                self._handoff(),
                source_paths=("../outside.py",),
            )
        self.assertFalse(invoked)

    def _register_source_writer(
        self,
        source_file: Path,
        *,
        fail_after_write: bool = False,
        replace_target_with_directory: bool = False,
    ) -> None:
        def write_source(inputs: Mapping[str, object]) -> Mapping[str, object]:
            if replace_target_with_directory:
                source_file.unlink()
                source_file.mkdir()
            else:
                source_file.write_text(str(inputs["content"]), encoding="utf-8")
            if fail_after_write:
                raise ToolRuntimeError("source write failed after partial output")
            return {"written": True}

        self.tools.register(
            ToolContract(
                identifier="local.source-write",
                name="Write source fixture",
                description="Write one test-selected fixture file.",
                input_schema=(InputField("content", InputType.STRING),),
                adapter_id="local.source-writer",
                execution_availability=ExecutionAvailability.AVAILABLE,
            )
        )
        self.executor.register_adapter(
            LocalToolAdapter("local.source-writer", {"local.source-write": write_source})
        )
        self.workflows.register(
            WorkflowDefinition(
                "workflow.source-write",
                "Source write test workflow",
                (
                    WorkflowStep(
                        "write",
                        "local.source-write",
                        {"content": WorkflowInputRef("content")},
                    ),
                ),
            )
        )

    def test_failed_tool_workflow_skips_validation_and_cannot_claim_verification(self):
        failing_tools = ToolRegistry()
        failing_tools.register(
            ToolContract(
                identifier="local.fail",
                name="Fail",
                description="Fail deterministically.",
                input_schema=(),
                adapter_id="local.validation-failure",
                execution_availability=ExecutionAvailability.AVAILABLE,
            )
        )

        def fail(inputs: Mapping[str, object]) -> Mapping[str, object]:
            raise RuntimeError(f"expected failure with {len(inputs)} inputs")

        failing_executor = ToolExecutor(failing_tools)
        failing_executor.register_adapter(
            LocalToolAdapter("local.validation-failure", {"local.fail": fail})
        )
        failing_workflows = WorkflowRegistry()
        failing_workflows.register(
            WorkflowDefinition(
                "workflow.failure",
                "Failing workflow",
                (WorkflowStep("fail", "local.fail", {}),),
            )
        )
        failing_engine = WorkflowEngine(
            failing_workflows, failing_tools, failing_executor
        )

        result = execute_handoff_workflow(
            failing_engine,
            "workflow.failure",
            {},
            self.adapter,
            (
                ValidationCommand(
                    "integration-test",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_integration",),
                ),
            ),
            self._handoff(),
        )

        self.assertEqual(result.workflow_result.status.value, "failed")
        self.assertEqual(result.validation_runs[0].outcome, "skipped")
        self.assertEqual(result.validation_runs[0].exit_code, None)
        self.assertEqual(result.handoff.verification_status, VerificationOutcome.NOT_RUN)
        self.assertEqual(result.handoff.release_status, ReleaseStatus.NOT_APPROVED)

    def test_failed_validation_cannot_promote_verification_or_release(self):
        result = execute_handoff_workflow(
            self.engine,
            "workflow.handoff",
            {"request": "run validation that fails"},
            self.adapter,
            (
                ValidationCommand(
                    "failing-integration-test",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_integration_failure",),
                ),
            ),
            self._handoff(),
        )

        self.assertEqual(result.workflow_result.status.value, "succeeded")
        self.assertEqual(result.validation_runs[0].outcome, "failed")
        self.assertNotEqual(result.validation_runs[0].exit_code, 0)
        self.assertEqual(result.handoff.verification_status, VerificationOutcome.NOT_RUN)
        self.assertEqual(result.handoff.release_status, ReleaseStatus.NOT_APPROVED)
        serialized = json.loads(result.to_json())
        self.assertEqual(serialized["validation_runs"][0]["outcome"], "failed")
        self.assertEqual(serialized["verification_status"], "not_run")
        self.assertEqual(serialized["release_status"], "not_approved")

    def test_handoff_result_rejects_mismatched_attached_evidence(self):
        result = execute_handoff_workflow(
            self.engine,
            "workflow.handoff",
            {"request": "consistent evidence"},
            self.adapter,
            (
                ValidationCommand(
                    "integration-test",
                    ValidationOperation.UNITTEST,
                    ("tests.test_adapter_integration",),
                ),
            ),
            self._handoff(),
        )
        altered_workflow = replace(
            result.handoff.workflow_execution,
            successful_step_count=0,
        )
        with self.assertRaisesRegex(ValueError, "must match workflow_result"):
            HandoffExecutionResult(
                result.workflow_result,
                result.validation_runs,
                replace(result.handoff, workflow_execution=altered_workflow),
            )
        altered_run = replace(
            result.validation_runs[0],
            outcome="failed",
            exit_code=1,
        )
        with self.assertRaisesRegex(ValueError, "must match validation_runs"):
            HandoffExecutionResult(
                result.workflow_result,
                (altered_run,),
                result.handoff,
            )

    def test_cli_executes_real_allowlisted_check_and_emits_unapproved_handoff(self):
        output = StringIO()
        errors = StringIO()
        with tempfile.TemporaryDirectory() as git_directory:
            repository_root = Path(git_directory)
            subprocess.run(
                ["git", "init", "--quiet"],
                cwd=repository_root,
                check=True,
                capture_output=True,
                text=True,
            )

            with redirect_stdout(output), redirect_stderr(errors):
                exit_code = main(
                    [
                        "--repository-root",
                        str(repository_root),
                        "--task-objective",
                        "Run an actual working diff check.",
                        "--git-diff-check",
                    ]
                )

        self.assertEqual(exit_code, 0, errors.getvalue())
        serialized = json.loads(output.getvalue())
        self.assertEqual(serialized["status"], "not_run")
        self.assertEqual(serialized["validation_runs"][0]["outcome"], "succeeded")
        self.assertEqual(serialized["validation_runs"][0]["exit_code"], 0)
        self.assertIsNone(serialized["workflow_execution"])
        self.assertEqual(serialized["verification_status"], "not_run")
        self.assertEqual(serialized["release_status"], "unknown")

    def test_cli_runs_provider_manifest_check_and_keeps_lifecycle_unapproved(self):
        output = StringIO()
        errors = StringIO()
        repository_root = Path(__file__).resolve().parents[1]

        with redirect_stdout(output), redirect_stderr(errors):
            exit_code = main(
                [
                    "--repository-root",
                    str(repository_root),
                    "--task-objective",
                    "Check canonical provider packaging.",
                    "--provider-manifest-check",
                ]
            )

        self.assertEqual(exit_code, 0, errors.getvalue())
        serialized = json.loads(output.getvalue())
        self.assertEqual(
            serialized["validation_runs"][0]["operation"],
            ValidationOperation.PROVIDER_MANIFEST.value,
        )
        self.assertEqual(serialized["validation_runs"][0]["outcome"], "succeeded")
        self.assertEqual(serialized["status"], "not_run")
        self.assertEqual(serialized["verification_status"], "not_run")
        self.assertEqual(serialized["release_status"], "unknown")

    def test_cli_emits_blocked_outcome_and_nonzero_exit_for_missing_test(self):
        output = StringIO()
        errors = StringIO()

        with redirect_stdout(output), redirect_stderr(errors):
            exit_code = main(
                [
                    "--repository-root",
                    str(self.root),
                    "--task-objective",
                    "Attempt a missing test module.",
                    "--unittest",
                    "tests.test_missing_cli_target",
                ]
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(errors.getvalue(), "")
        serialized = json.loads(output.getvalue())
        self.assertEqual(serialized["validation_runs"][0]["outcome"], "blocked")
        self.assertIsNone(serialized["validation_runs"][0]["exit_code"])
        self.assertEqual(serialized["status"], "not_run")
        self.assertEqual(serialized["verification_status"], "not_run")
        self.assertEqual(serialized["release_status"], "unknown")

    def test_cli_applies_requested_timeout_and_serializes_timeout_outcome(self):
        (self.root / "tests" / "test_cli_slow.py").write_text(
            "import time\n"
            "import unittest\n"
            "class SlowTest(unittest.TestCase):\n"
            "    def test_waits(self):\n"
            "        time.sleep(2)\n",
            encoding="utf-8",
        )
        output = StringIO()
        errors = StringIO()

        with redirect_stdout(output), redirect_stderr(errors):
            exit_code = main(
                [
                    "--repository-root",
                    str(self.root),
                    "--task-objective",
                    "Verify the CLI operation timeout.",
                    "--timeout-seconds",
                    "0.1",
                    "--unittest",
                    "tests.test_cli_slow",
                ]
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(errors.getvalue(), "")
        serialized = json.loads(output.getvalue())
        self.assertEqual(
            serialized["validation_runs"][0]["outcome"],
            "timed_out",
        )
        self.assertEqual(
            serialized["validation_runs"][0]["limitation"],
            "command_timeout",
        )
        self.assertEqual(serialized["verification_status"], "not_run")
        self.assertEqual(serialized["release_status"], "unknown")

    def test_cli_rejects_timeout_outside_supported_range(self):
        for timeout in ("0", "-1", "300.1", "nan", "inf"):
            with self.subTest(timeout=timeout):
                errors = StringIO()
                with redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
                    main(
                        [
                            "--repository-root",
                            str(self.root),
                            "--task-objective",
                            "Reject an invalid timeout.",
                            "--timeout-seconds",
                            timeout,
                            "--git-diff-check",
                        ]
                    )

                self.assertEqual(raised.exception.code, 2)
                self.assertIn("timeout_seconds must be greater than 0", errors.getvalue())

    def test_cli_requires_explicit_allowlisted_operation(self):
        errors = StringIO()

        with redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
            main(
                [
                    "--repository-root",
                    str(self.root),
                    "--task-objective",
                    "Do not run an implicit default check.",
                ]
            )

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("select at least one validation operation", errors.getvalue())


if __name__ == "__main__":
    unittest.main()

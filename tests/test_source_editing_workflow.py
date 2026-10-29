from __future__ import annotations

import ctypes
import hashlib
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import source_editing_workflow as source_editing_module
from scripts.source_editing_workflow import _read_windows_file_dacl
from scripts.skill_pipeline import (
    InvocationRequest,
    SkillExecutionStatus,
    SkillPipeline,
)
from scripts.skill_registry import SkillContract
from scripts.source_editing_workflow import (
    SourceEditOperation,
    SourceEditOutcome,
    SourceEditingRequest,
    SourceEditingSkillExecutionAdapter,
    SourceEditingWorkflow,
    SourceWriteAuthorization,
    create_source_editing_pipeline,
)
from scripts.tool_workflow import WorkflowCancellationToken
from scripts.validation_adapter import (
    ValidationCommand,
    ValidationOperation,
)


_PASSING_TEST = (
    "import unittest\n"
    "class ValidationCheck(unittest.TestCase):\n"
    "    def test_passes(self):\n"
    "        self.assertTrue(True)\n"
)

_FAILING_TEST = (
    "import unittest\n"
    "class ValidationCheck(unittest.TestCase):\n"
    "    def test_fails(self):\n"
    "        self.assertTrue(False)\n"
)


class SourceEditingWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "skills" / "implementation").mkdir(parents=True)
        (self.root / "skills" / "implementation" / "SKILL.md").write_text(
            "---\nname: implementation\ndescription: Implement changes.\n---\n",
            encoding="utf-8",
        )
        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (self.root / "tests" / "test_validation.py").write_text(
            _PASSING_TEST, encoding="utf-8"
        )
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "add", "--", "tests/test_validation.py"],
            cwd=self.root,
            check=True,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _authorization(self, *paths: str) -> SourceWriteAuthorization:
        return SourceWriteAuthorization(self.root, tuple(paths), tuple(paths))

    def _request(
        self,
        *operations: SourceEditOperation,
        cancellation_token: WorkflowCancellationToken | None = None,
    ) -> SourceEditingRequest:
        return SourceEditingRequest(
            objective="Apply bounded local edits and verify them.",
            operations=tuple(operations),
            validation_commands=(
                ValidationCommand(
                    "git-diff-check",
                    ValidationOperation.GIT_DIFF_CHECK,
                    tuple(operation.path for operation in operations),
                    timeout_seconds=10,
                ),
            ),
            cancellation_token=cancellation_token,
        )

    def test_creates_authorized_file_runs_fixed_validation_and_integrates_pipeline(self):
        authorization = self._authorization("src/new.py")
        workflow = SourceEditingWorkflow(self.root, authorization)
        operation = SourceEditOperation("src/new.py", "VALUE = 7\n", None)
        result = workflow.execute(self._request(operation))

        self.assertEqual(result.outcome, SourceEditOutcome.SUCCEEDED)
        self.assertTrue(result.success)
        self.assertEqual((self.root / "src" / "new.py").read_text(), "VALUE = 7\n")
        self.assertEqual(result.validation_runs[0].outcome, "succeeded")
        self.assertEqual(result.validation_runs[0].exit_code, 0)
        self.assertEqual(result.source_change_report.changed_paths, ("src/new.py",))

        pipeline = create_source_editing_pipeline(self.root, authorization)
        selected = pipeline.select("implement a repository change")
        self.assertEqual(selected.selected.identifier, "implementation")
        pipeline_result = pipeline.invoke(
            InvocationRequest(
                "implementation",
                "Create the authorized source file.",
                {
                    "source_edit_request": self._request(
                        SourceEditOperation(
                            "src/new.py",
                            "VALUE = 8\n",
                            hashlib.sha256(b"VALUE = 7\n").hexdigest(),
                        )
                    )
                },
            )
        )
        self.assertEqual(pipeline_result.status, SkillExecutionStatus.SUCCEEDED)
        self.assertEqual(
            (self.root / "src" / "new.py").read_text(encoding="utf-8"),
            "VALUE = 8\n",
        )
        self.assertIn("source_editing_result", pipeline_result.output)

    def test_missing_authorization_blocks_without_writing(self):
        workflow = SourceEditingWorkflow(self.root, None)
        request = self._request(
            SourceEditOperation("src/new.py", "VALUE = 1\n", None)
        )

        result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
        self.assertEqual(result.error_code, "source_edit_blocked")
        self.assertFalse((self.root / "src" / "new.py").exists())
        self.assertEqual(result.validation_runs[0].outcome, "skipped")

    def test_write_grant_does_not_implicitly_grant_read_access(self):
        authorization = SourceWriteAuthorization(
            self.root,
            ("src/new.py",),
        )
        workflow = SourceEditingWorkflow(self.root, authorization)

        result = workflow.execute(
            self._request(
                SourceEditOperation("src/new.py", "value\n", None)
            )
        )

        self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
        self.assertFalse((self.root / "src" / "new.py").exists())

    def test_snapshot_reads_only_explicitly_readable_grants(self):
        private_file = self.root / "src" / "write-only.txt"
        private_file.write_text("must not be read\n", encoding="utf-8")
        authorization = SourceWriteAuthorization(
            self.root,
            ("src/new.py", "src/write-only.txt"),
            ("src/new.py",),
        )
        workflow = SourceEditingWorkflow(self.root, authorization)
        capture_snapshot = source_editing_module.capture_repository_snapshot

        with patch.object(
            source_editing_module,
            "capture_repository_snapshot",
            wraps=capture_snapshot,
        ) as capture:
            result = workflow.execute(
                self._request(
                    SourceEditOperation("src/new.py", "value\n", None)
                )
            )

        self.assertEqual(result.outcome, SourceEditOutcome.SUCCEEDED)
        observed_scopes = [call.args[1] for call in capture.call_args_list]
        self.assertGreaterEqual(len(observed_scopes), 2)
        self.assertTrue(all(scope == ("src/new.py",) for scope in observed_scopes))
        self.assertEqual(private_file.read_text(encoding="utf-8"), "must not be read\n")

    def test_unscoped_git_diff_validation_is_blocked(self):
        workflow = SourceEditingWorkflow(
            self.root,
            self._authorization("src/new.py"),
        )
        request = SourceEditingRequest(
            objective="Reject a repository-wide diff check outside the read grant.",
            operations=(
                SourceEditOperation("src/new.py", "value\n", None),
            ),
            validation_commands=(
                ValidationCommand(
                    "repository-diff",
                    ValidationOperation.GIT_DIFF_CHECK,
                ),
            ),
        )

        result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
        self.assertEqual(
            result.error_code,
            "source_edit_validation_scope_denied",
        )
        self.assertFalse((self.root / "src" / "new.py").exists())

    def test_unscoped_cached_git_diff_validation_is_blocked(self):
        staged_path = self.root / "src" / "outside-grant.txt"
        staged_path.write_text("staged content \n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "--", "src/outside-grant.txt"],
            cwd=self.root,
            check=True,
        )
        workflow = SourceEditingWorkflow(
            self.root,
            self._authorization("src/new.py"),
        )
        request = SourceEditingRequest(
            objective="Reject a repository-wide cached diff check outside the read grant.",
            operations=(
                SourceEditOperation("src/new.py", "value\n", None),
            ),
            validation_commands=(
                ValidationCommand(
                    "cached-repository-diff",
                    ValidationOperation.GIT_CACHED_DIFF_CHECK,
                ),
            ),
        )

        result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
        self.assertEqual(
            result.error_code,
            "source_edit_validation_scope_denied",
        )
        self.assertFalse((self.root / "src" / "new.py").exists())
        self.assertEqual(result.validation_runs[0].outcome, "skipped")

    def test_caller_selected_python_validation_is_blocked_before_edit(self):
        marker_path = self.root / "executed.marker"
        operation = SourceEditOperation(
            "tests/test_untrusted.py",
            "from pathlib import Path\n"
            "Path('executed.marker').write_text('executed', encoding='utf-8')\n",
            None,
        )
        workflow = SourceEditingWorkflow(
            self.root,
            self._authorization("tests/test_untrusted.py"),
        )
        request = SourceEditingRequest(
            objective="Reject caller-selected Python code as source validation.",
            operations=(operation,),
            validation_commands=(
                ValidationCommand(
                    "caller-selected-test",
                    ValidationOperation.UNITTEST,
                    ("tests.test_untrusted",),
                ),
            ),
        )

        result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
        self.assertEqual(
            result.error_code,
            "source_edit_validation_scope_denied",
        )
        self.assertFalse((self.root / operation.path).exists())
        self.assertFalse(marker_path.exists())
        self.assertEqual(result.validation_runs[0].outcome, "skipped")

    def test_target_outside_exact_grant_is_blocked(self):
        outside = self.root / "src" / "other.py"
        outside.write_bytes(b"leave this file unchanged\n")
        workflow = SourceEditingWorkflow(self.root, self._authorization("src/allowed.py"))
        request = self._request(
            SourceEditOperation("src/other.py", "VALUE = 2\n", None)
        )

        result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
        self.assertEqual(outside.read_bytes(), b"leave this file unchanged\n")

    def test_rejects_traversal_and_absolute_targets_at_request_construction(self):
        for path in ("../outside.py", "src/../outside.py", "C:/outside.py", "/outside.py"):
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, "normalized repository-relative"):
                    SourceEditOperation(path, "value\n", None)

    def test_rejects_symlink_and_junction_parent_components(self):
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/new.py")
        )
        original_is_junction = Path.is_junction

        def is_junction(path: Path) -> bool:
            if path == self.root / "src":
                return True
            return original_is_junction(path)

        with patch.object(Path, "is_junction", is_junction):
            result = workflow.execute(
                self._request(SourceEditOperation("src/new.py", "value\n", None))
            )

        self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
        self.assertFalse((self.root / "src" / "new.py").exists())

    def test_rejects_symlink_escape_when_host_allows_creation(self):
        outside = Path(self.temporary_directory.name).parent / (
            f"{self.root.name}-outside.py"
        )
        outside.write_bytes(b"outside sentinel\n")
        link = self.root / "src" / "linked.py"
        try:
            link.symlink_to(outside)
        except OSError as error:
            outside.unlink()
            self.skipTest(f"symlink creation is unavailable: {error}")
        try:
            workflow = SourceEditingWorkflow(
                self.root, self._authorization("src/linked.py")
            )
            result = workflow.execute(
                self._request(
                    SourceEditOperation("src/linked.py", "replacement\n", None)
                )
            )
            self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
            self.assertEqual(outside.read_bytes(), b"outside sentinel\n")
        finally:
            outside.unlink(missing_ok=True)

    def test_preexisting_change_conflicts_with_expected_hash(self):
        target = self.root / "src" / "existing.py"
        target.write_text("before\n", encoding="utf-8")
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        target.write_text("concurrent change\n", encoding="utf-8")
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/existing.py")
        )

        result = workflow.execute(
            self._request(
                SourceEditOperation("src/existing.py", "replacement\n", expected)
            )
        )

        self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
        self.assertEqual(result.error_code, "source_edit_conflict")
        self.assertEqual(target.read_text(encoding="utf-8"), "concurrent change\n")

    def test_concurrent_change_after_preflight_is_not_overwritten(self):
        target = self.root / "src" / "existing.py"
        target.write_text("before\n", encoding="utf-8")
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/existing.py")
        )
        request = self._request(
            SourceEditOperation("src/existing.py", "replacement\n", expected)
        )
        original_apply = workflow._apply_operation

        def race(operation, initial, token=None):
            target.write_text("changed after preflight\n", encoding="utf-8")
            return original_apply(operation, initial, token)

        with patch.object(workflow, "_apply_operation", side_effect=race):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.PARTIAL)
        self.assertEqual(result.error_code, "source_edit_partial")
        self.assertEqual(target.read_text(encoding="utf-8"), "changed after preflight\n")

    def test_permission_failure_is_reported_without_success(self):
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/new.py")
        )
        request = self._request(
            SourceEditOperation("src/new.py", "value\n", None)
        )

        with patch.object(workflow, "_apply_operation", side_effect=PermissionError):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.FAILED)
        self.assertEqual(result.error_code, "source_edit_write_denied")
        self.assertEqual(result.validation_runs[0].outcome, "skipped")

    def test_staging_failure_preserves_original_and_reports_original_hash(self):
        target = self.root / "src" / "existing.py"
        target.write_bytes(b"before\n")
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/existing.py")
        )
        request = self._request(
            SourceEditOperation("src/existing.py", "replacement\n", expected)
        )

        with patch(
            "scripts.source_editing_workflow.os.fsync",
            side_effect=OSError("simulated staging interruption"),
        ):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.FAILED)
        self.assertEqual(result.error_code, "source_edit_write_failed")
        self.assertEqual(result.operation_results[0].outcome, "failed")
        self.assertEqual(
            result.operation_results[0].after_sha256,
            expected,
        )
        self.assertEqual(target.read_bytes(), b"before\n")
        self.assertEqual(result.source_change_report.changed_paths, ())
        self.assertEqual(tuple(target.parent.glob(f".{target.name}.*.tmp")), ())

    def test_atomic_replace_failure_preserves_original_and_cleans_staging_file(self):
        target = self.root / "src" / "existing.py"
        target.write_bytes(b"original\n")
        original_bytes = target.read_bytes()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/existing.py")
        )
        request = self._request(
            SourceEditOperation(
                "src/existing.py",
                "replacement\n",
                hashlib.sha256(original_bytes).hexdigest(),
            )
        )

        with patch(
            "scripts.source_editing_workflow.os.replace",
            side_effect=PermissionError("simulated replace denial"),
        ):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.FAILED)
        self.assertEqual(result.error_code, "source_edit_write_denied")
        self.assertEqual(target.read_bytes(), original_bytes)
        self.assertEqual(tuple(target.parent.glob(f".{target.name}.*.tmp")), ())
        self.assertEqual(
            result.operation_results[0].after_sha256,
            hashlib.sha256(original_bytes).hexdigest(),
        )

    def test_atomic_replace_preserves_existing_posix_mode(self):
        if os.name != "posix":
            self.skipTest("POSIX permission-bit semantics are not available")
        target = self.root / "src" / "mode.py"
        target.write_bytes(b"original\n")
        target.chmod(0o640)
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/mode.py")
        )

        result = workflow.execute(
            self._request(
                SourceEditOperation(
                    "src/mode.py",
                    "replacement\n",
                    hashlib.sha256(target.read_bytes()).hexdigest(),
                )
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)

    def test_atomic_replace_preserves_windows_target_dacl(self):
        if os.name != "nt":
            self.skipTest("Windows DACL semantics are only available on Windows")
        from ctypes import wintypes

        target = self.root / "src" / "acl.py"
        target.write_bytes(b"original\n")
        advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        convert = advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW
        convert.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(wintypes.DWORD),
        ]
        convert.restype = wintypes.BOOL
        set_security = advapi32.SetFileSecurityW
        set_security.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.c_void_p,
        ]
        set_security.restype = wintypes.BOOL
        local_free = kernel32.LocalFree
        local_free.argtypes = [ctypes.c_void_p]
        local_free.restype = ctypes.c_void_p
        descriptor = ctypes.c_void_p()
        descriptor_size = wintypes.DWORD()
        if not convert(
            "D:(A;;GR;;;WD)",
            1,
            ctypes.byref(descriptor),
            ctypes.byref(descriptor_size),
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            if not set_security(str(target), 0x00000004, descriptor):
                raise ctypes.WinError(ctypes.get_last_error())
        finally:
            local_free(descriptor)

        original_dacl = _read_windows_file_dacl(target)
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/acl.py")
        )
        result = workflow.execute(
            self._request(
                SourceEditOperation(
                    "src/acl.py",
                    "replacement\n",
                    hashlib.sha256(target.read_bytes()).hexdigest(),
                )
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(target.read_bytes(), b"replacement\n")
        self.assertTrue(original_dacl[0])
        self.assertIsNotNone(original_dacl[2])
        self.assertEqual(
            _read_windows_file_dacl(target),
            original_dacl,
        )

    def test_windows_dacl_copy_failure_does_not_replace_target(self):
        if os.name != "nt":
            self.skipTest("Windows DACL semantics are only available on Windows")
        target = self.root / "src" / "acl-failure.py"
        original_bytes = b"original\n"
        target.write_bytes(original_bytes)
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/acl-failure.py")
        )
        request = self._request(
            SourceEditOperation(
                "src/acl-failure.py",
                "replacement\n",
                hashlib.sha256(original_bytes).hexdigest(),
            )
        )

        with patch(
            "scripts.source_editing_workflow._copy_windows_file_dacl",
            side_effect=PermissionError("simulated DACL-copy denial"),
        ):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.FAILED)
        self.assertEqual(result.error_code, "source_edit_write_denied")
        self.assertEqual(target.read_bytes(), original_bytes)
        self.assertEqual(tuple(target.parent.glob(f".{target.name}.*.tmp")), ())
        self.assertEqual(result.validation_runs[0].outcome, "skipped")

    def test_characterizes_destination_swap_after_final_hash_check(self):
        target = self.root / "src" / "raced.py"
        target.write_bytes(b"before\n")
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/raced.py")
        )
        request = self._request(
            SourceEditOperation("src/raced.py", "editor bytes\n", expected)
        )
        original_replace = os.replace
        race_bytes = b"concurrent bytes after final hash check\n"
        replaced = False

        def replace_after_concurrent_write(source, destination):
            nonlocal replaced
            if Path(destination) == target:
                target.write_bytes(race_bytes)
                replaced = True
            return original_replace(source, destination)

        with patch(
            "scripts.source_editing_workflow.os.replace",
            side_effect=replace_after_concurrent_write,
        ):
            result = workflow.execute(request)

        self.assertTrue(replaced)
        self.assertEqual(result.outcome, SourceEditOutcome.SUCCEEDED)
        self.assertTrue(result.success)
        self.assertEqual(target.read_bytes(), b"editor bytes\n")

    def test_characterizes_staging_file_modification_before_replacement(self):
        target = self.root / "src" / "staging-raced.py"
        target.write_bytes(b"before\n")
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/staging-raced.py")
        )
        request = self._request(
            SourceEditOperation(
                "src/staging-raced.py",
                "editor bytes\n",
                expected,
            )
        )
        original_replace = os.replace
        replacement_bytes = b"concurrent staging-file modification\n"
        replaced = False

        def replace_after_staging_write(source, destination):
            nonlocal replaced
            if Path(destination) == target:
                Path(source).write_bytes(replacement_bytes)
                replaced = True
            return original_replace(source, destination)

        with patch(
            "scripts.source_editing_workflow.os.replace",
            side_effect=replace_after_staging_write,
        ):
            result = workflow.execute(request)

        self.assertTrue(replaced)
        self.assertEqual(result.outcome, SourceEditOutcome.PARTIAL)
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "source_edit_partial")
        self.assertEqual(
            result.operation_results[0].error_code,
            "source_edit_content_mismatch",
        )
        self.assertEqual(target.read_bytes(), replacement_bytes)

    def test_same_user_process_can_replace_destination_before_installation(self):
        target = self.root / "src" / "process-raced.py"
        target.write_bytes(b"before\n")
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/process-raced.py")
        )
        request = self._request(
            SourceEditOperation("src/process-raced.py", "editor bytes\n", expected)
        )
        original_replace = os.replace
        race_bytes = b"same-user process bytes\n"
        process_completed = False

        def replace_after_process_write(source, destination):
            nonlocal process_completed
            if Path(destination) == target:
                subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        "-c",
                        "from pathlib import Path; import sys; "
                        "Path(sys.argv[1]).write_bytes(sys.argv[2].encode())",
                        str(target),
                        race_bytes.decode(),
                    ],
                    check=True,
                    timeout=10,
                )
                process_completed = True
            return original_replace(source, destination)

        with patch(
            "scripts.source_editing_workflow.os.replace",
            side_effect=replace_after_process_write,
        ):
            result = workflow.execute(request)

        self.assertTrue(process_completed)
        self.assertEqual(result.outcome, SourceEditOutcome.SUCCEEDED)
        self.assertTrue(result.success)
        self.assertEqual(target.read_bytes(), b"editor bytes\n")

    def test_same_user_process_can_modify_staging_file_before_installation(self):
        target = self.root / "src" / "process-staging-raced.py"
        target.write_bytes(b"before\n")
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/process-staging-raced.py")
        )
        request = self._request(
            SourceEditOperation(
                "src/process-staging-raced.py",
                "editor bytes\n",
                expected,
            )
        )
        original_replace = os.replace
        replacement_bytes = b"same-user staging process bytes\n"
        process_completed = False

        def replace_after_process_write(source, destination):
            nonlocal process_completed
            if Path(destination) == target:
                subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        "-c",
                        "from pathlib import Path; import sys; "
                        "Path(sys.argv[1]).write_bytes(sys.argv[2].encode())",
                        str(source),
                        replacement_bytes.decode(),
                    ],
                    check=True,
                    timeout=10,
                )
                process_completed = True
            return original_replace(source, destination)

        with patch(
            "scripts.source_editing_workflow.os.replace",
            side_effect=replace_after_process_write,
        ):
            result = workflow.execute(request)

        self.assertTrue(process_completed)
        self.assertEqual(result.outcome, SourceEditOutcome.PARTIAL)
        self.assertFalse(result.success)
        self.assertEqual(
            result.operation_results[0].error_code,
            "source_edit_content_mismatch",
        )
        self.assertEqual(target.read_bytes(), replacement_bytes)

    def test_authorization_is_rechecked_before_atomic_replace(self):
        target = self.root / "src" / "new.py"
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/new.py")
        )
        request = self._request(SourceEditOperation("src/new.py", "value\n", None))
        original_check = workflow._check_write_authorization

        with patch.object(
            workflow, "_check_write_authorization", wraps=original_check
        ) as authorization_check:
            result = workflow.execute(request)

        self.assertTrue(result.success)
        self.assertGreaterEqual(authorization_check.call_count, 2)
        self.assertEqual(target.read_text(encoding="utf-8"), "value\n")

    def test_revoked_authorization_blocks_before_atomic_replace(self):
        target = self.root / "src" / "new.py"
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/new.py")
        )
        request = self._request(SourceEditOperation("src/new.py", "value\n", None))
        original_check = workflow._check_write_authorization
        checks = 0

        def revoke_before_commit(operation):
            nonlocal checks
            checks += 1
            if checks == 2:
                workflow.authorization = None
            return original_check(operation)

        with patch.object(
            workflow,
            "_check_write_authorization",
            side_effect=revoke_before_commit,
        ):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.BLOCKED)
        self.assertFalse(target.exists())
        self.assertEqual(tuple(target.parent.glob(f".{target.name}.*.tmp")), ())

    def test_cancellation_after_staging_prevents_atomic_replace(self):
        target = self.root / "src" / "new.py"
        token = WorkflowCancellationToken()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/new.py")
        )
        request = self._request(
            SourceEditOperation("src/new.py", "value\n", None),
            cancellation_token=token,
        )
        original_fsync = os.fsync

        def cancel_after_staging(descriptor):
            original_fsync(descriptor)
            token.request_cancel()

        with patch(
            "scripts.source_editing_workflow.os.fsync",
            side_effect=cancel_after_staging,
        ):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.CANCELLED)
        self.assertFalse(target.exists())
        self.assertEqual(tuple(target.parent.glob(f".{target.name}.*.tmp")), ())

    def test_concurrent_change_before_final_precondition_check_is_not_replaced(self):
        target = self.root / "src" / "existing.py"
        target.write_bytes(b"before\n")
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/existing.py")
        )
        request = self._request(
            SourceEditOperation("src/existing.py", "replacement\n", expected)
        )
        original_snapshot = source_editing_module._snapshot_one
        snapshots = 0

        def change_before_final_check(root, relative_path):
            nonlocal snapshots
            snapshots += 1
            if snapshots == 2:
                target.write_bytes(b"concurrent bytes\n")
            return original_snapshot(root, relative_path)

        with patch(
            "scripts.source_editing_workflow._snapshot_one",
            side_effect=change_before_final_check,
        ):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.PARTIAL)
        self.assertEqual(target.read_bytes(), b"concurrent bytes\n")
        self.assertEqual(
            result.operation_results[0].after_sha256,
            hashlib.sha256(b"concurrent bytes\n").hexdigest(),
        )
        self.assertEqual(tuple(target.parent.glob(f".{target.name}.*.tmp")), ())

    def test_validation_failure_keeps_actual_failure_and_partial_status(self):
        test_file = self.root / "tests" / "test_validation.py"
        expected = hashlib.sha256(test_file.read_bytes()).hexdigest()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("tests/test_validation.py")
        )
        content_with_whitespace_error = _FAILING_TEST + "trailing whitespace \n"

        result = workflow.execute(
            self._request(
                SourceEditOperation(
                    "tests/test_validation.py",
                    content_with_whitespace_error,
                    expected,
                )
            )
        )

        self.assertEqual(result.outcome, SourceEditOutcome.PARTIAL)
        self.assertEqual(result.error_code, "source_edit_validation_failed")
        self.assertEqual(result.validation_runs[0].outcome, "failed")
        self.assertNotEqual(result.validation_runs[0].exit_code, 0)
        self.assertFalse(result.success)

    def test_cancellation_before_edit_prevents_writes(self):
        token = WorkflowCancellationToken()
        token.request_cancel()
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/new.py")
        )

        result = workflow.execute(
            self._request(
                SourceEditOperation("src/new.py", "value\n", None),
                cancellation_token=token,
            )
        )

        self.assertEqual(result.outcome, SourceEditOutcome.CANCELLED)
        self.assertFalse((self.root / "src" / "new.py").exists())
        self.assertEqual(result.validation_runs[0].outcome, "skipped")

    def test_cancellation_between_edits_prevents_next_write(self):
        token = WorkflowCancellationToken()
        workflow = SourceEditingWorkflow(
            self.root,
            self._authorization("src/first.py", "src/second.py"),
        )
        request = self._request(
            SourceEditOperation("src/first.py", "first\n", None),
            SourceEditOperation("src/second.py", "second\n", None),
            cancellation_token=token,
        )
        original_apply = workflow._apply_operation
        applied = 0

        def cancel_after_first(operation, initial, cancellation=None):
            nonlocal applied
            result = original_apply(operation, initial, cancellation)
            applied += 1
            if applied == 1:
                token.request_cancel()
            return result

        with patch.object(workflow, "_apply_operation", side_effect=cancel_after_first):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.PARTIAL)
        self.assertTrue((self.root / "src" / "first.py").exists())
        self.assertFalse((self.root / "src" / "second.py").exists())
        self.assertEqual(result.operation_results[1].outcome, "not_run")
        self.assertEqual(result.validation_runs[0].outcome, "skipped")

    def test_cancellation_during_validation_reports_partial_and_cancelled_run(self):
        token = WorkflowCancellationToken()
        workflow = SourceEditingWorkflow(
            self.root,
            self._authorization("src/new.py"),
        )
        request = self._request(
            SourceEditOperation("src/new.py", "value\n", None),
            cancellation_token=token,
        )
        original_execute = workflow.validation_adapter.execute

        def cancel_before_validation(commands, *, cancellation_token=None):
            token.request_cancel()

            return original_execute(
                commands,
                cancellation_token=cancellation_token,
            )

        with patch.object(
            workflow.validation_adapter,
            "execute",
            side_effect=cancel_before_validation,
        ):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.PARTIAL)
        self.assertEqual(result.error_code, "source_edit_cancelled")
        self.assertTrue((self.root / "src" / "new.py").exists())
        self.assertEqual(result.validation_runs[0].outcome, "cancelled")
        self.assertIsNone(result.validation_runs[0].exit_code)

    def test_multi_file_failure_retains_first_commit_and_reports_partial(self):
        authorization = self._authorization(
            "src/first.py", "src/second.py", "src/third.py"
        )
        workflow = SourceEditingWorkflow(self.root, authorization)
        request = self._request(
            SourceEditOperation("src/first.py", "first\n", None),
            SourceEditOperation("src/second.py", "second\n", None),
            SourceEditOperation("src/third.py", "third\n", None),
        )
        original_apply = workflow._apply_operation
        applied_paths = []

        def fail_second(operation, initial, token=None):
            if operation.path == "src/second.py":
                raise PermissionError("simulated second-file failure")
            digest = original_apply(operation, initial, token)
            applied_paths.append(operation.path)
            return digest

        with patch.object(workflow, "_apply_operation", side_effect=fail_second):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.PARTIAL)
        self.assertEqual(result.error_code, "source_edit_partial")
        self.assertEqual(applied_paths, ["src/first.py"])
        self.assertEqual((self.root / "src" / "first.py").read_bytes(), b"first\n")
        self.assertFalse((self.root / "src" / "second.py").exists())
        self.assertFalse((self.root / "src" / "third.py").exists())
        self.assertEqual(result.source_change_report.changed_paths, ("src/first.py",))
        self.assertEqual(result.operation_results[0].outcome, "succeeded")
        self.assertEqual(result.operation_results[1].outcome, "failed")
        self.assertEqual(result.operation_results[2].outcome, "not_run")
        self.assertEqual(result.validation_runs[0].outcome, "succeeded")

    def test_final_snapshot_detects_unexpected_change_within_granted_scope(self):
        first = self.root / "src" / "first.py"
        second = self.root / "src" / "second.py"
        first.write_text("first old\n", encoding="utf-8")
        second.write_text("second old\n", encoding="utf-8")
        workflow = SourceEditingWorkflow(
            self.root,
            self._authorization("src/first.py", "src/second.py"),
        )
        request = self._request(
            SourceEditOperation(
                "src/first.py",
                "first new\n",
                hashlib.sha256(first.read_bytes()).hexdigest(),
            )
        )
        original_apply = workflow._apply_operation

        def change_extra(operation, initial, token=None):
            digest = original_apply(operation, initial, token)
            second.write_text("unexpected\n", encoding="utf-8")
            return digest

        with patch.object(workflow, "_apply_operation", side_effect=change_extra):
            result = workflow.execute(request)

        self.assertEqual(result.outcome, SourceEditOutcome.PARTIAL)
        self.assertEqual(result.error_code, "source_edit_unexpected_change")
        self.assertEqual(
            result.source_change_report.changed_paths,
            ("src/first.py", "src/second.py"),
        )

    def test_pipeline_reports_cancelled_and_unavailable_states_truthfully(self):
        authorization = self._authorization("src/new.py")
        pipeline = create_source_editing_pipeline(self.root, authorization)
        token = WorkflowCancellationToken()
        token.request_cancel()
        cancelled = pipeline.invoke(
            InvocationRequest(
                "implementation",
                "Create a file.",
                {
                    "source_edit_request": self._request(
                        SourceEditOperation("src/new.py", "value\n", None),
                        cancellation_token=token,
                    )
                },
            )
        )
        self.assertEqual(cancelled.status, SkillExecutionStatus.CANCELLED)
        self.assertEqual(cancelled.error_code, "source_edit_cancelled")
        self.assertFalse((self.root / "src" / "new.py").exists())

        unavailable_pipeline = SkillPipeline(self.root)
        unavailable_pipeline.discover()
        unavailable = unavailable_pipeline.invoke(
            InvocationRequest("implementation", "No editor configured.")
        )
        self.assertEqual(unavailable.status, SkillExecutionStatus.UNAVAILABLE)
        self.assertEqual(unavailable.error_code, "execution_unavailable")

    def test_pipeline_failure_preserves_structured_edit_and_validation_evidence(self):
        test_file = self.root / "tests" / "test_validation.py"
        authorization = self._authorization("tests/test_validation.py")
        pipeline = create_source_editing_pipeline(self.root, authorization)
        content_with_whitespace_error = _FAILING_TEST + "trailing whitespace \n"
        result = pipeline.invoke(
            InvocationRequest(
                "implementation",
                "Replace the test with a failing assertion.",
                {
                    "source_edit_request": self._request(
                        SourceEditOperation(
                            "tests/test_validation.py",
                            content_with_whitespace_error,
                            hashlib.sha256(test_file.read_bytes()).hexdigest(),
                        )
                    )
                },
            )
        )

        self.assertEqual(result.status, SkillExecutionStatus.FAILED)
        self.assertEqual(result.error_code, "source_edit_validation_failed")
        self.assertIsNone(result.output)
        details = result.failure_details["source_editing_result"]
        self.assertEqual(details["outcome"], "partial")
        self.assertEqual(details["validation_runs"][0]["outcome"], "failed")
        self.assertNotEqual(details["validation_runs"][0]["exit_code"], 0)

    def test_other_skills_are_not_supported_by_editing_adapter(self):
        workflow = SourceEditingWorkflow(
            self.root, self._authorization("src/new.py")
        )
        adapter = SourceEditingSkillExecutionAdapter(workflow)
        pipeline = SkillPipeline(self.root, execution_adapter=adapter)
        pipeline.discover()

        unsupported_skill = SkillContract(
            identifier="unsupported",
            name="Unsupported",
            description="A Skill without a source-editing implementation.",
            source_path=Path("skills/unsupported/SKILL.md"),
        )
        self.assertFalse(adapter.supports(unsupported_skill))


if __name__ == "__main__":
    unittest.main()

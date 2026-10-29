from __future__ import annotations

import hashlib
from io import StringIO
import json
import os
import signal
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.source_editing_cli import main
from scripts import source_editing_workflow


class SourceEditingCliTests(unittest.TestCase):
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
            "original\n",
            encoding="utf-8",
        )
        (self.root / "tests" / "test_unreadable.py").write_text(
            "baseline\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "add", "--", "tests/test_validation.py", "tests/test_unreadable.py"],
            cwd=self.root,
            check=True,
        )
        self.request_template = {
            "objective": "Apply the proposed file content and validate it.",
            "operations": [
                {
                    "path": "src/result.txt",
                    "content": "new content\n",
                    "expected_sha256": None,
                }
            ],
        }

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _invoke(
        self,
        payload: str,
        *allowed_paths: str,
        readable_paths: tuple[str, ...] | None = None,
    ) -> tuple[int, dict[str, object], str]:
        output = StringIO()
        error = StringIO()
        read_grants = allowed_paths if readable_paths is None else readable_paths
        status = main(
            [
                "--repository-root",
                str(self.root),
                *[
                    argument
                    for path in allowed_paths
                    for argument in ("--allow-write", path)
                ],
                *[
                    argument
                    for path in read_grants
                    for argument in ("--allow-read", path)
                ],
            ],
            stdin=StringIO(payload),
            stdout=output,
            stderr=error,
        )
        return status, json.loads(output.getvalue()), error.getvalue()

    def test_write_grant_without_read_grant_is_denied(self):
        status, result, _ = self._invoke(
            json.dumps(self.request_template),
            "src/result.txt",
            readable_paths=(),
        )

        self.assertEqual(status, 1)
        edit_result = result["failure_details"]["source_editing_result"]
        self.assertEqual(edit_result["outcome"], "blocked")
        self.assertFalse((self.root / "src" / "result.txt").exists())

    def test_executes_json_request_through_pipeline_and_reports_validation(self):
        status, result, error = self._invoke(
            json.dumps(self.request_template),
            "src/result.txt",
        )

        self.assertEqual(status, 0)
        self.assertEqual(error, "")
        self.assertEqual(result["status"], "succeeded")
        edit_result = result["output"]["source_editing_result"]
        self.assertEqual(edit_result["outcome"], "succeeded")
        self.assertEqual(edit_result["validation_runs"][0]["outcome"], "succeeded")
        self.assertEqual((self.root / "src" / "result.txt").read_text(), "new content\n")

    def test_validation_does_not_read_ungranted_tracked_paths(self):
        edited_path = self.root / "tests" / "test_validation.py"
        unreadable_path = self.root / "tests" / "test_unreadable.py"
        unreadable_path.write_text("ungranted trailing space \n", encoding="utf-8")
        payload = {
            "objective": "Edit one explicitly granted file.",
            "operations": [
                {
                    "path": "tests/test_validation.py",
                    "content": "updated\n",
                    "expected_sha256": hashlib.sha256(
                        edited_path.read_bytes()
                    ).hexdigest(),
                }
            ],
        }
        launched: list[tuple[str, ...]] = []
        original_popen = subprocess.Popen

        def capture_argv(args, *positional, **kwargs):
            launched.append(tuple(str(argument) for argument in args))
            return original_popen(args, *positional, **kwargs)

        with patch(
            "scripts.validation_adapter.subprocess.Popen",
            side_effect=capture_argv,
        ):
            status, result, error = self._invoke(
                json.dumps(payload),
                "tests/test_validation.py",
                readable_paths=("tests/test_validation.py",),
            )

        self.assertEqual(status, 0, error)
        validation = result["output"]["source_editing_result"]["validation_runs"][0]
        self.assertEqual(validation["outcome"], "succeeded")
        self.assertEqual(len(launched), 1)
        self.assertIn("--literal-pathspecs", launched[0])
        self.assertEqual(
            launched[0][-3:],
            ("--check", "--", "tests/test_validation.py"),
        )
        self.assertNotIn("tests/test_unreadable.py", launched[0])
        self.assertEqual(edited_path.read_text(encoding="utf-8"), "updated\n")
        self.assertEqual(
            unreadable_path.read_text(encoding="utf-8"),
            "ungranted trailing space \n",
        )

    def test_rejects_malformed_json_without_writing(self):
        status, result, error = self._invoke("{", "src/result.txt")

        self.assertEqual(status, 2)
        self.assertEqual(result["error_code"], "invalid_json")
        self.assertIn("invalid_json", error)
        self.assertFalse((self.root / "src" / "result.txt").exists())

    def test_rejects_duplicate_json_keys_without_writing(self):
        payload = (
            '{"objective":"first","objective":"second",'
            '"operations":[{"path":"src/result.txt","content":"new",'
            '"expected_sha256":null}]}'
        )

        status, result, _ = self._invoke(payload, "src/result.txt")

        self.assertEqual(status, 2)
        self.assertEqual(result["error_code"], "invalid_request")
        self.assertFalse((self.root / "src" / "result.txt").exists())

    def test_rejects_request_over_size_limit_without_writing(self):
        oversized = json.dumps(
            {
                "objective": "x" * (12 * 1024 * 1024),
                "operations": self.request_template["operations"],
            }
        )

        status, result, _ = self._invoke(oversized, "src/result.txt")

        self.assertEqual(status, 2)
        self.assertEqual(result["status"], "invalid_request")
        self.assertFalse((self.root / "src" / "result.txt").exists())

    def test_rejects_caller_selected_validation_commands(self):
        payload = dict(self.request_template)
        payload["validation_commands"] = [
            {
                "identifier": "untrusted-test",
                "operation": "unittest",
                "targets": ["tests.test_validation"],
            }
        ]

        status, result, _ = self._invoke(json.dumps(payload), "src/result.txt")

        self.assertEqual(status, 2)
        self.assertEqual(result["error_code"], "invalid_request")
        self.assertFalse((self.root / "src" / "result.txt").exists())

    def test_out_of_grant_operation_is_reported_without_writing(self):
        status, result, _ = self._invoke(
            json.dumps(self.request_template),
            "src/other.txt",
        )

        self.assertEqual(status, 1)
        self.assertEqual(result["status"], "failed")
        edit_result = result["failure_details"]["source_editing_result"]
        self.assertEqual(edit_result["outcome"], "blocked")
        self.assertFalse((self.root / "src" / "result.txt").exists())

    def test_invalid_path_grant_is_rejected_without_writing(self):
        status, result, _ = self._invoke(
            json.dumps(self.request_template),
            "../outside.txt",
        )

        self.assertEqual(status, 2)
        self.assertEqual(result["status"], "invalid_request")
        self.assertFalse((self.root / "src" / "result.txt").exists())

    def test_missing_implementation_skill_is_reported_as_unavailable(self):
        (self.root / "skills" / "implementation" / "SKILL.md").unlink()

        status, result, error = self._invoke(
            json.dumps(self.request_template),
            "src/result.txt",
        )

        self.assertEqual(status, 1)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_code"], "pipeline_unavailable")
        self.assertIn("pipeline_unavailable", error)
        self.assertFalse((self.root / "src" / "result.txt").exists())

    def test_failed_validation_returns_nonzero_with_failure_evidence(self):
        test_file = self.root / "tests" / "test_validation.py"
        test_file.write_text(
            "changed with trailing whitespace \n",
            encoding="utf-8",
        )
        payload = dict(self.request_template)
        payload["operations"] = [
            {
                "path": "tests/test_validation.py",
                "content": test_file.read_text(encoding="utf-8"),
                "expected_sha256": hashlib.sha256(test_file.read_bytes()).hexdigest(),
            }
        ]

        status, result, _ = self._invoke(
            json.dumps(payload),
            "tests/test_validation.py",
        )

        self.assertEqual(status, 1)
        self.assertEqual(result["status"], "failed")
        edit_result = result["failure_details"]["source_editing_result"]
        self.assertEqual(edit_result["outcome"], "partial")
        self.assertEqual(edit_result["validation_runs"][0]["outcome"], "failed")
        self.assertEqual(
            edit_result["validation_runs"][0]["command_id"],
            "git-diff-check",
        )

    def test_reports_staging_tampering_as_partial_instead_of_success(self):
        target = self.root / "src" / "result.txt"
        target.write_text("before\n", encoding="utf-8")
        payload = dict(self.request_template)
        payload["operations"] = [
            {
                "path": "src/result.txt",
                "content": "expected content\n",
                "expected_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        ]
        original_replace = source_editing_workflow.os.replace
        altered_content = b"concurrent staging modification\n"

        def alter_staging_before_replace(source: str | Path, destination: str | Path) -> None:
            if Path(destination) == target:
                Path(source).write_bytes(altered_content)
            original_replace(source, destination)

        with patch(
            "scripts.source_editing_workflow.os.replace",
            side_effect=alter_staging_before_replace,
        ):
            status, result, _ = self._invoke(
                json.dumps(payload),
                "src/result.txt",
            )

        self.assertEqual(status, 1)
        self.assertEqual(result["status"], "failed")
        edit_result = result["failure_details"]["source_editing_result"]
        self.assertEqual(edit_result["outcome"], "partial")
        self.assertEqual(
            edit_result["operation_results"][0]["error_code"],
            "source_edit_content_mismatch",
        )
        self.assertEqual(target.read_bytes(), altered_content)

    def test_rejects_unexpected_request_fields(self):
        payload = dict(self.request_template)
        payload["shell_command"] = "not accepted"

        status, result, _ = self._invoke(json.dumps(payload), "src/result.txt")

        self.assertEqual(status, 2)
        self.assertEqual(result["error_code"], "invalid_request")
        self.assertFalse((self.root / "src" / "result.txt").exists())

    def test_sigint_cancels_at_staging_checkpoint_without_replacing_target(self):
        target = self.root / "src" / "result.txt"
        target.write_text("before\n", encoding="utf-8")
        payload = dict(self.request_template)
        payload["operations"] = [
            {
                "path": "src/result.txt",
                "content": "after\n",
                "expected_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        ]
        original_fsync = os.fsync

        def cancel_after_staging(descriptor: int) -> None:
            original_fsync(descriptor)
            signal.raise_signal(signal.SIGINT)

        with patch(
            "scripts.source_editing_workflow.os.fsync",
            side_effect=cancel_after_staging,
        ):
            status, result, _ = self._invoke(
                json.dumps(payload),
                "src/result.txt",
            )

        self.assertEqual(status, 1)
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["error_code"], "source_edit_cancelled")
        edit_result = result["failure_details"]["source_editing_result"]
        self.assertEqual(edit_result["outcome"], "cancelled")
        self.assertEqual(target.read_text(encoding="utf-8"), "before\n")
        self.assertEqual(tuple(target.parent.glob(f".{target.name}.*.tmp")), ())

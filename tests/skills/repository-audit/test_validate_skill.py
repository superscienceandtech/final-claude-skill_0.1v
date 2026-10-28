"""Implementation tests for the dependency-free Skill structure validator."""

from __future__ import annotations

import errno
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
VALIDATOR = REPO / "scripts" / "validate-skill.py"
SOURCE_SKILL = REPO / "skills" / "repository-audit" / "SKILL.md"
EVALUATION_README = REPO / "docs" / "evaluation" / "repository-audit" / "README.md"
EVALUATION_PLAN = REPO / "docs" / "evaluation" / "repository-audit" / "EVALUATION_PLAN.md"
EVIDENCE_TEMPLATE = REPO / "docs" / "evaluation" / "repository-audit" / "EVIDENCE_TEMPLATE.md"
EVALUATION_RUBRIC = REPO / "docs" / "evaluation" / "repository-audit" / "RUBRIC.md"
SPEC = importlib.util.spec_from_file_location("validate_skill", VALIDATOR)
assert SPEC is not None and SPEC.loader is not None
validate_skill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_skill)
SKILL_RELATIVE = Path("skills") / "repository-audit" / "SKILL.md"
REQUIRED_BODY = """# Test Skill

## Purpose
Purpose text.
## Inputs
Input text.
## Repository boundary
Boundary text.
## Allowed operations
Operations text.
## Security and content policy
Security text.
## Output contract
Output text.
## Failure behavior
Failure text.
## Testing status
NOT_RUN.
"""


def valid_text() -> str:
    return (
        '---\nname: "repository-audit"\ndescription: "A test description."\n'
        'version: "0.1.0"\n---\n'
        + REQUIRED_BODY
    )


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="repository-audit-validator-")
        self.root = Path(self.temp.name).resolve()
        self.skill = self.root / SKILL_RELATIVE
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text(valid_text(), encoding="utf-8", newline="\n")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, *args: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), *args],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.stderr, "")
        return result, json.loads(result.stdout)

    def valid_args(self) -> tuple[str, ...]:
        return ("--repo-root", str(self.root), "--skill-path", "skills/repository-audit/SKILL.md")

    def test_valid_skill_has_stable_json_and_exit_zero(self) -> None:
        first_result, first = self.invoke(*self.valid_args())
        second_result, second = self.invoke(*self.valid_args())
        self.assertEqual(first_result.returncode, 0)
        self.assertEqual(first, {"validator_version": "1.0", "status": "VALID", "errors": []})
        self.assertEqual(first_result.stdout, second_result.stdout)
        self.assertEqual(first, second)

    def test_valid_result_stdout_is_single_compact_json_object(self) -> None:
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(set(report.keys()), {"validator_version", "status", "errors"})
        self.assertEqual(report, {"validator_version": "1.0", "status": "VALID", "errors": []})
        self.assertNotIn(": ", result.stdout)
        self.assertNotIn(", ", result.stdout)
        decoder = json.JSONDecoder()
        _, end = decoder.raw_decode(result.stdout)
        self.assertEqual(result.stdout[end:].strip(), "")
        self.assertEqual(
            result.stdout.strip(),
            json.dumps(report, ensure_ascii=False, separators=(",", ":")),
        )

    def test_invalid_and_error_stdout_is_single_compact_json_object(self) -> None:
        cases: dict[str, tuple[tuple[str, ...], int, str, str | None]] = {
            "invalid": (
                self.valid_args(),
                1,
                "INVALID",
                valid_text().replace('name: "repository-audit"', 'name: "another-skill"'),
            ),
            "error": (("--unexpected",), 2, "ERROR", None),
        }
        for label, (args, expected_exit, expected_status, content) in cases.items():
            with self.subTest(case=label):
                if content is not None:
                    self.skill.write_text(content, encoding="utf-8", newline="\n")
                result, report = self.invoke(*args)
                self.assertEqual(result.returncode, expected_exit)
                self.assertEqual(report["status"], expected_status)
                self.assertEqual(set(report.keys()), {"validator_version", "status", "errors"})
                self.assertNotIn(": ", result.stdout)
                self.assertNotIn(", ", result.stdout)
                decoder = json.JSONDecoder()
                _, end = decoder.raw_decode(result.stdout)
                self.assertEqual(result.stdout[end:].strip(), "")
                self.assertEqual(
                    result.stdout.strip(),
                    json.dumps(report, ensure_ascii=False, separators=(",", ":")),
                )

    def test_top_level_json_has_exactly_the_fixed_keys(self) -> None:
        invocations = {
            "VALID": (self.valid_args(), None),
            "INVALID": (
                self.valid_args(),
                valid_text().replace('name: "repository-audit"', 'name: "another-skill"'),
            ),
            "ERROR": (("--unexpected",), None),
        }
        for status, (args, content) in invocations.items():
            with self.subTest(status=status):
                if content is not None:
                    self.skill.write_text(content, encoding="utf-8", newline="\n")
                _, report = self.invoke(*args)
                self.assertEqual(set(report.keys()), {"validator_version", "status", "errors"})
                self.assertEqual(len(report), 3)

    def test_error_objects_contain_only_code_and_line(self) -> None:
        self.skill.write_text(
            '---\nname: "wrong"\ndescription: "' + ("x" * 201) + '"\n'
            'version: "01.0.0"\nextra: "x"\nversion: "0.1.0"\n---\n' + REQUIRED_BODY,
            encoding="utf-8",
            newline="\n",
        )
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 1)
        self.assertTrue(report["errors"])
        for item in report["errors"]:
            with self.subTest(error=item):
                self.assertEqual(set(item.keys()), {"code", "line"})
                self.assertIsInstance(item["code"], str)
                self.assertTrue(item["code"])
                line = item["line"]
                self.assertTrue(
                    line is None
                    or (isinstance(line, int) and not isinstance(line, bool) and line >= 1)
                )

    def test_repeated_invalid_invocations_are_byte_identical(self) -> None:
        """Determinism/established-behavior check; not an explicitly stated §6 byte-ordering requirement."""
        self.skill.write_text(
            valid_text()
            .replace("## Failure behavior\nFailure text.\n", "")
            .replace('name: "repository-audit"', 'name: "another-skill"'),
            encoding="utf-8",
            newline="\n",
        )
        first_result, first = self.invoke(*self.valid_args())
        second_result, second = self.invoke(*self.valid_args())
        self.assertEqual(first_result.returncode, 1)
        self.assertEqual(first_result.returncode, second_result.returncode)
        self.assertEqual(first_result.stdout, second_result.stdout)
        self.assertEqual(first, second)

    def test_status_field_matches_exit_code_with_empty_stderr(self) -> None:
        invocations: dict[str, tuple[tuple[str, ...], int, str | None]] = {
            "VALID": (self.valid_args(), 0, None),
            "INVALID": (
                self.valid_args(),
                1,
                valid_text().replace('name: "repository-audit"', 'name: "another-skill"'),
            ),
            "ERROR": (("--unexpected",), 2, None),
        }
        for status, (args, expected_exit, content) in invocations.items():
            with self.subTest(status=status):
                if content is not None:
                    self.skill.write_text(content, encoding="utf-8", newline="\n")
                result, report = self.invoke(*args)
                self.assertEqual(report["status"], status)
                self.assertEqual(result.returncode, expected_exit)
                self.assertEqual(result.stderr, "")

    def test_invalid_metadata_cases_have_contract_exit_one(self) -> None:
        cases = {
            "missing-name": valid_text().replace('name: "repository-audit"\n', ""),
            "unknown-field": valid_text().replace('name: "repository-audit"\n', 'extra: "x"\nname: "repository-audit"\n'),
            "duplicate-field": valid_text().replace('name: "repository-audit"\n', 'name: "repository-audit"\nname: "repository-audit"\n'),
            "wrong-type": valid_text().replace('version: "0.1.0"', "version: 1"),
            "wrong-name": valid_text().replace('name: "repository-audit"', 'name: "another-skill"'),
            "bad-version": valid_text().replace('version: "0.1.0"', 'version: "01.0.0"'),
            "bad-quote": valid_text().replace('version: "0.1.0"', 'version: "0.1.0'),
            "long-description": valid_text().replace(
                'description: "A test description."', 'description: "' + ("x" * 201) + '"'
            ),
            "control-description": valid_text().replace(
                'description: "A test description."', 'description: "bad\\u0085value"'
            ),
            "bad-delimiter": valid_text().replace("---\n# Test Skill", "...\n# Test Skill", 1),
            "missing-heading": valid_text().replace("## Failure behavior\nFailure text.\n", ""),
        }
        for label, content in cases.items():
            with self.subTest(case=label):
                self.skill.write_text(content, encoding="utf-8", newline="\n")
                result, report = self.invoke(*self.valid_args())
                self.assertEqual(result.returncode, 1)
                self.assertEqual(report["status"], "INVALID")
                self.assertTrue(report["errors"])

    def test_heading_inside_fenced_code_does_not_satisfy_required_heading(self) -> None:
        content = valid_text().replace(
            "## Failure behavior\nFailure text.\n",
            "```markdown\n## Failure behavior\n```\n",
        )
        self.skill.write_text(content, encoding="utf-8", newline="\n")

        result, report = self.invoke(*self.valid_args())

        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "INVALID")
        self.assertIn(
            {"code": "HEADING_MISSING", "line": None},
            report["errors"],
        )

    def test_atx_heading_allows_commonmark_indentation(self) -> None:
        self.skill.write_text(
            valid_text().replace("## Failure behavior", "   ##\tFailure behavior"),
            encoding="utf-8",
            newline="\n",
        )

        result, report = self.invoke(*self.valid_args())

        self.assertEqual(result.returncode, 0)
        self.assertEqual(report, {"validator_version": "1.0", "status": "VALID", "errors": []})

    def test_heading_inside_multiline_html_comment_does_not_satisfy_required_heading(self) -> None:
        content = valid_text().replace(
            "## Failure behavior\nFailure text.\n",
            "<!-- hidden section\n## Failure behavior\n-->\n",
        )
        self.skill.write_text(content, encoding="utf-8", newline="\n")

        result, report = self.invoke(*self.valid_args())

        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "INVALID")
        self.assertIn({"code": "HEADING_MISSING", "line": None}, report["errors"])

    def test_each_required_field_is_required_and_must_be_a_string(self) -> None:
        cases = {
            "missing-description": valid_text().replace('description: "A test description."\n', ""),
            "missing-version": valid_text().replace('version: "0.1.0"\n', ""),
            "name-wrong-type": valid_text().replace('name: "repository-audit"', "name: 7"),
            "description-wrong-type": valid_text().replace(
                'description: "A test description."', "description: false"
            ),
            "version-wrong-type": valid_text().replace('version: "0.1.0"', "version: 7"),
        }
        expected = {
            "missing-description": [{"code": "METADATA_MISSING", "line": None}],
            "missing-version": [{"code": "METADATA_MISSING", "line": None}],
            "name-wrong-type": [{"code": "METADATA_TYPE_INVALID", "line": 2}],
            "description-wrong-type": [{"code": "METADATA_TYPE_INVALID", "line": 3}],
            "version-wrong-type": [{"code": "METADATA_TYPE_INVALID", "line": 4}],
        }
        for label, content in cases.items():
            with self.subTest(case=label):
                self.skill.write_text(content, encoding="utf-8", newline="\n")
                result, report = self.invoke(*self.valid_args())
                self.assertEqual(result.returncode, 1)
                self.assertEqual(report["errors"], expected[label])

    def test_description_limit_counts_unicode_codepoints(self) -> None:
        description = "🧪" * 200
        self.skill.write_text(
            valid_text().replace("A test description.", description),
            encoding="utf-8",
            newline="\n",
        )
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report, {"validator_version": "1.0", "status": "VALID", "errors": []})

        self.skill.write_text(
            valid_text().replace("A test description.", description + "🧪"),
            encoding="utf-8",
            newline="\n",
        )
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["errors"], [{"code": "METADATA_VALUE_INVALID", "line": 3}])

    def test_invalid_utf8_is_reported_without_source_content(self) -> None:
        self.skill.write_bytes(b"---\n\xff\n---\n")
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["errors"], [{"code": "SKILL_UTF8_INVALID", "line": None}])
        self.assertNotIn("xff", result.stdout.lower())

    def test_input_path_and_root_errors_are_exit_two(self) -> None:
        file_root = self.root / "not-a-directory"
        file_root.write_text("fixture", encoding="utf-8")
        cases = [
            ((), "ARGUMENT_REQUIRED"),
            (("--repo-root", "relative", "--skill-path", "skills/repository-audit/SKILL.md"), "ROOT_INVALID"),
            (("--repo-root", str(self.root / "missing-root"), "--skill-path", "skills/repository-audit/SKILL.md"), "ROOT_INVALID"),
            (("--repo-root", str(file_root), "--skill-path", "skills/repository-audit/SKILL.md"), "ROOT_INVALID"),
            (("--repo-root", str(self.root), "--skill-path", "other/SKILL.md"), "SKILL_PATH_INVALID"),
            (("--repo-root", str(self.root), "--skill-path", "../outside/SKILL.md"), "SKILL_PATH_INVALID"),
            (("--repo-root", str(self.root), "--skill-path", "skills/../SKILL.md"), "SKILL_PATH_INVALID"),
            ((*self.valid_args(), "--unexpected"), "ARGUMENT_UNKNOWN"),
        ]
        for args, expected_code in cases:
            with self.subTest(expected=expected_code):
                result, report = self.invoke(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(report["status"], "ERROR")
                self.assertIn(expected_code, {e["code"] for e in report["errors"]})

    def test_invalid_invocation_emits_exactly_one_stable_error(self) -> None:
        result, report = self.invoke("--unexpected")

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "")
        self.assertEqual(len(report["errors"]), 1)
        self.assertEqual(report["errors"][0]["code"], "ARGUMENT_UNKNOWN")

    def test_unc_root_is_rejected_before_filesystem_resolution(self) -> None:
        args = [
            "--repo-root",
            r"\\server\share\repository",
            "--skill-path",
            "skills/repository-audit/SKILL.md",
        ]
        with (
            mock.patch.object(Path, "is_absolute", return_value=True),
            mock.patch.object(Path, "resolve", return_value=self.root) as resolve,
        ):
            root, relative, errors = validate_skill.parse_args(args)

        self.assertIsNone(root)
        self.assertIsNone(relative)
        self.assertEqual(errors, [{"code": "ROOT_INVALID", "line": None}])
        resolve.assert_not_called()

    def test_noncanonical_skill_path_is_rejected_before_file_read(self) -> None:
        output = StringIO()
        args = ["--repo-root", str(self.root), "--skill-path", "other/SKILL.md"]
        with mock.patch.object(validate_skill, "read_skill") as read_skill:
            with redirect_stdout(output):
                exit_code = validate_skill.main(args)

        self.assertEqual(exit_code, 2)
        read_skill.assert_not_called()
        self.assertEqual(
            json.loads(output.getvalue()),
            {
                "validator_version": "1.0",
                "status": "ERROR",
                "errors": [{"code": "SKILL_PATH_INVALID", "line": None}],
            },
        )

    def test_inaccessible_root_and_file_fail_closed(self) -> None:
        args = ["--repo-root", str(self.root), "--skill-path", "skills/repository-audit/SKILL.md"]
        with mock.patch.object(Path, "resolve", side_effect=PermissionError("denied")):
            root, relative, errors = validate_skill.parse_args(args)
        self.assertIsNone(root)
        self.assertIsNone(relative)
        self.assertEqual(errors, [{"code": "ROOT_INVALID", "line": None}])

        original_open = os.open

        def deny_skill_open(path: str | bytes | os.PathLike[str], *open_args: object, **open_kwargs: object):
            if path == "SKILL.md":
                raise PermissionError("denied")
            return original_open(path, *open_args, **open_kwargs)

        with mock.patch.object(validate_skill.os, "open", deny_skill_open):
            raw, errors = validate_skill.read_skill(self.root, "skills/repository-audit/SKILL.md")
        self.assertIsNone(raw)
        self.assertEqual(errors, [{"code": "SKILL_PATH_INVALID", "line": None}])

    def test_os_permission_denied_root_is_rejected(self) -> None:
        if os.name != "posix":
            self.skipTest("genuine POSIX directory permission checks require a POSIX host")
        if os.geteuid() == 0:
            self.skipTest("genuine permission-denied check requires a non-root process")

        try:
            fixture = tempfile.TemporaryDirectory(prefix="repository-audit-v03-", dir="/tmp")
        except OSError as exc:
            self.skipTest(f"cannot create isolated fixture under /tmp: {exc}")

        parent = Path(fixture.name) / "inaccessible-parent"
        root = parent / "repository"
        parent_created = False
        try:
            parent.mkdir()
            parent_created = True
            root.mkdir()
            os.chmod(parent, 0)

            try:
                root.resolve(strict=True)
            except PermissionError as exc:
                if exc.errno != errno.EACCES:
                    self.skipTest(f"permission probe returned errno {exc.errno}, expected EACCES")
            else:
                self.skipTest("mode 000 did not make root resolution fail with PermissionError/EACCES")

            result, report = self.invoke(
                "--repo-root",
                str(root),
                "--skill-path",
                "skills/repository-audit/SKILL.md",
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(report["status"], "ERROR")
            self.assertEqual(report["errors"], [{"code": "ROOT_INVALID", "line": None}])
        finally:
            try:
                if parent_created:
                    os.chmod(parent, 0o700)
            finally:
                fixture.cleanup()

    def test_error_list_order_is_exact_and_stable(self) -> None:
        content = (
            '---\nname: "wrong"\ndescription: "' + ("x" * 201) + '\"\n'
            'version: "01.0.0"\nextra: "x"\nversion: "0.1.0"\n---\n' + REQUIRED_BODY
        )
        self.skill.write_text(content, encoding="utf-8", newline="\n")
        result, report = self.invoke(*self.valid_args())
        repeated_result, repeated_report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(repeated_result.returncode, result.returncode)
        self.assertEqual(repeated_result.stdout, result.stdout)
        self.assertEqual(repeated_report, report)
        self.assertEqual(
            report["errors"],
            [
                {"code": "METADATA_DUPLICATE", "line": 6},
                {"code": "METADATA_UNKNOWN", "line": 5},
                {"code": "METADATA_VALUE_INVALID", "line": 2},
                {"code": "METADATA_VALUE_INVALID", "line": 3},
                {"code": "METADATA_VALUE_INVALID", "line": 4},
            ],
        )

    def test_missing_and_oversized_skill_are_errors(self) -> None:
        self.skill.unlink()
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report["errors"][0]["code"], "SKILL_FILE_MISSING")
        self.skill.write_bytes(b"x" * (64 * 1024 + 1))
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report["errors"][0]["code"], "SKILL_FILE_TOO_LARGE")

    def test_oversized_skill_is_rejected_without_reading_past_file_limit(self) -> None:
        self.skill.write_bytes(b"x" * (validate_skill.MAX_FILE_BYTES + 1))
        original_open = os.fdopen
        read_sizes: list[int] = []

        class ReadTracker:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.stream.close()

            def fileno(self):
                return self.stream.fileno()

            def read(self, size: int) -> bytes:
                read_sizes.append(size)
                return self.stream.read(size)

        def tracked_open(fd: int, *args, **kwargs):
            return ReadTracker(original_open(fd, *args, **kwargs))

        with mock.patch.object(validate_skill.os, "fdopen", tracked_open):
            raw, errors = validate_skill.read_skill(self.root, "skills/repository-audit/SKILL.md")

        self.assertIsNone(raw)
        self.assertEqual(errors, [{"code": "SKILL_FILE_TOO_LARGE", "line": None}])
        self.assertEqual(read_sizes, [])

    def test_file_size_boundary_accepts_limit_and_rejects_one_byte_over(self) -> None:
        valid = valid_text().encode("utf-8")
        self.skill.write_bytes(valid + b"x" * (64 * 1024 - len(valid)))
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report, {"validator_version": "1.0", "status": "VALID", "errors": []})

        self.skill.write_bytes(valid + b"x" * (64 * 1024 + 1 - len(valid)))
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report["errors"], [{"code": "SKILL_FILE_TOO_LARGE", "line": None}])

    def test_symlink_path_is_rejected_when_platform_allows_creation(self) -> None:
        link = self.root / "skills"
        real = self.root / "real-skills"
        link.rename(real)
        try:
            os.symlink(real, link, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")
        result, report = self.invoke(*self.valid_args())
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report["errors"][0]["code"], "SKILL_PATH_INVALID")

    def test_in_root_symlinked_skill_file_is_rejected(self) -> None:
        target = self.root / "repository-audit-copy.md"
        self.skill.rename(target)
        try:
            os.symlink(target, self.skill)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"file symlink unavailable: {exc}")

        result, report = self.invoke(*self.valid_args())

        self.assertEqual(result.returncode, 2)
        self.assertEqual(report["status"], "ERROR")
        self.assertEqual(report["errors"], [{"code": "SKILL_PATH_INVALID", "line": None}])

    def test_skill_path_swap_to_external_symlink_is_rejected_before_read(self) -> None:
        with tempfile.TemporaryDirectory(prefix="repository-audit-outside-") as outside_dir:
            outside_skill = Path(outside_dir) / "outside.md"
            outside_skill.write_bytes(b"outside target must never be read")
            original_os_open = os.open
            original_path_open = Path.open
            swapped = False

            def swap_target() -> None:
                nonlocal swapped
                if not swapped:
                    self.skill.unlink()
                    os.symlink(outside_skill, self.skill)
                    swapped = True

            def racing_os_open(path, flags, *args, **kwargs):
                if path == "SKILL.md":
                    swap_target()
                return original_os_open(path, flags, *args, **kwargs)

            def racing_path_open(path, *args, **kwargs):
                if path == self.skill:
                    swap_target()
                return original_path_open(path, *args, **kwargs)

            with (
                mock.patch.object(validate_skill.os, "open", side_effect=racing_os_open),
                mock.patch.object(Path, "open", racing_path_open),
            ):
                raw, errors = validate_skill.read_skill(self.root, "skills/repository-audit/SKILL.md")

        self.assertTrue(swapped)
        self.assertIsNone(raw)
        self.assertEqual(errors, [{"code": "SKILL_PATH_INVALID", "line": None}])

    def test_parent_directory_swap_to_external_symlink_is_rejected_before_read(self) -> None:
        with tempfile.TemporaryDirectory(prefix="repository-audit-outside-") as outside_dir:
            outside = Path(outside_dir)
            (outside / "SKILL.md").write_bytes(b"outside directory target must never be read")
            original_os_open = os.open
            original_path_open = Path.open
            original_parent = self.skill.parent
            renamed_parent = original_parent.with_name("repository-audit-original")
            swapped = False

            def swap_parent() -> None:
                nonlocal swapped
                if not swapped:
                    original_parent.rename(renamed_parent)
                    os.symlink(outside, original_parent, target_is_directory=True)
                    swapped = True

            def racing_os_open(path, flags, *args, **kwargs):
                if path == "repository-audit":
                    swap_parent()
                return original_os_open(path, flags, *args, **kwargs)

            def racing_path_open(path, *args, **kwargs):
                if path == self.skill:
                    swap_parent()
                return original_path_open(path, *args, **kwargs)

            with (
                mock.patch.object(validate_skill.os, "open", side_effect=racing_os_open),
                mock.patch.object(Path, "open", racing_path_open),
            ):
                raw, errors = validate_skill.read_skill(self.root, "skills/repository-audit/SKILL.md")

        self.assertTrue(swapped)
        self.assertIsNone(raw)
        self.assertEqual(errors, [{"code": "SKILL_PATH_INVALID", "line": None}])

    def test_fifo_at_skill_path_is_rejected_without_blocking(self) -> None:
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO fixtures require os.mkfifo")
        self.skill.unlink()
        os.mkfifo(self.skill)

        result = subprocess.run(
            [sys.executable, str(VALIDATOR), *self.valid_args()],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=2,
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            [{"code": "SKILL_FILE_MISSING", "line": None}],
        )

    def test_non_posix_path_race_fails_closed_before_open(self) -> None:
        with tempfile.TemporaryDirectory(prefix="repository-audit-outside-") as outside_dir:
            outside_skill = Path(outside_dir) / "outside.md"
            outside_skill.write_bytes(b"outside target must never be read")
            original_stat = Path.stat
            swapped = False

            def swap_before_stat(path: Path, *args, **kwargs):
                nonlocal swapped
                if path == self.skill and not swapped:
                    self.skill.unlink()
                    os.symlink(outside_skill, self.skill)
                    swapped = True
                return original_stat(path, *args, **kwargs)

            with (
                mock.patch.object(validate_skill.os, "name", "nt"),
                mock.patch.object(Path, "stat", swap_before_stat),
            ):
                raw, errors = validate_skill.read_skill(self.root, "skills/repository-audit/SKILL.md")

        self.assertFalse(swapped, "unsupported platform path must fail before path-based stat")
        self.assertIsNone(raw)
        self.assertEqual(errors, [{"code": "SKILL_PATH_INVALID", "line": None}])

    def test_validator_does_not_change_fixture_files(self) -> None:
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result, _ = self.invoke(*self.valid_args())
        after = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(result.returncode, 0)
        self.assertEqual(before, after)

    def test_skill_text_documents_fail_closed_host_and_content_policy(self) -> None:
        text = SOURCE_SKILL.read_text(encoding="utf-8")
        self.assertIn("EXECUTION_HOST_UNAVAILABLE", text)
        self.assertIn("If no such host tool is available, stop before running a command", text)
        self.assertIn("Do not use a shell, shell composition, or a broader tool as fallback", text)
        self.assertIn("Do not explicitly open, inspect, summarize, or disclose repository file contents", text)
        self.assertIn("The fixed `git.status` operation may cause necessary Git-internal working-tree reads", text)
        self.assertIn("This does not guarantee zero filesystem content reads", text)
        self.assertIn("No other Git operation may cause working-tree/blob-content reads under this policy", text)
        self.assertIn("limitations.tests` as `NOT_RUN", text)

    def test_skill_documents_root_and_individual_path_containment_outcomes(self) -> None:
        text = SOURCE_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "inability to establish root containment rejects the request with "
            "`REJECTED` + `UNKNOWN` + `PATH_CONTAINMENT_UNPROVEN` and no repository inspection",
            text,
        )
        self.assertIn("No later command may run", text)
        self.assertIn(
            "inability to establish containment for one path after root validation yields "
            "`PARTIAL` + `UNKNOWN` + `PATH_CONTAINMENT_UNPROVEN`, skips that path without accessing it, "
            "and permits continuation only for independently proven paths",
            text,
        )
        self.assertIn("continue only for independently proven paths", text)
        self.assertIn("`PATH_OUTSIDE_ROOT`", text)

    def test_skill_documents_opaque_redacted_output_and_deterministic_ids(self) -> None:
        text = SOURCE_SKILL.read_text(encoding="utf-8")
        self.assertIn("Do not emit raw paths, branch names, command arguments, or caller-controlled strings", text)
        self.assertIn("report-local IDs and counts only", text)
        self.assertIn("(`P001`, `P002`, …)", text)
        self.assertIn("(`B001`, …)", text)
        self.assertIn("sort by ordinal UTF-8 byte order before assigning deterministic report-local IDs", text)
        self.assertIn("leaks represented item counts and relative ordering/membership", text)
        self.assertIn("fixed reason codes", text)

    def test_skill_documents_approved_input_and_output_limits(self) -> None:
        text = SOURCE_SKILL.read_text(encoding="utf-8")
        for required_limit in (
            "UTF-8 JSON request at most 64 KiB",
            "root at most 4 KiB UTF-8",
            "each path at most 1 KiB UTF-8",
            "no more than 500 paths",
            "generated claims/summaries at most 256 Unicode code points",
            "final JSON at most 256 KiB UTF-8",
        ):
            with self.subTest(limit=required_limit):
                self.assertIn(required_limit, text)
        self.assertIn("reject the entire request with `REJECTED`", text)
        self.assertIn("Do not partially accept paths", text)
        self.assertIn("`limitations.truncated: false`", text)
        self.assertIn("`limitations.truncated: true`", text)
        self.assertIn(
            "add an `OUTPUT_LIMIT` limitation, and include deterministic omitted counts by category",
            text,
        )
        self.assertIn(
            "drop ordinary findings and evidence from the end of stable order while reserving space for status, "
            "error, and truncation metadata",
            text,
        )

    def test_skill_documents_scope_list_defaults_and_duplicate_rejection(self) -> None:
        text = SOURCE_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "Omitted `requested_facts` and `requested_paths` lists default to empty",
            text,
        )
        self.assertIn(
            "Unknown facts, wrong field types, duplicate facts, or duplicate requested paths reject the invocation "
            "with `SCOPE_INVALID` before repository inspection; return `REJECTED`, one `UNKNOWN` boundary finding, "
            "no repository-derived facts, and an empty command ledger",
            text,
        )

    def test_skill_documents_partial_state_comparison_failure_semantics(self) -> None:
        text = SOURCE_SKILL.read_text(encoding="utf-8")
        for required_rule in (
            "capture the same approved branch/status queries before and after inspection",
            "Keep each usable query result in its corresponding `before` or `after` snapshot slot",
            "set only a failed or unusable slot to null",
            "skip that paired after query if the before query fails",
            "continue only with other independent approved query pairs",
            "Treat timeout, output-limit, malformed, incomplete, or otherwise unusable output as failed evidence",
            "record the actual process outcome and exit code (or null if none exists)",
            "Make dependent facts `UNKNOWN`",
            "Set `unchanged` to null unless every required before/after query result is successful, complete, and valid",
            "an incomplete comparison is `PARTIAL`",
            "A detected difference makes the overall status `PARTIAL` and adds the concurrent-change limitation",
            "Never present an incomplete comparison as successful or claim that matching snapshots rule out transient changes",
        ):
            with self.subTest(rule=required_rule):
                self.assertIn(required_rule, text)

    def test_skill_documents_aggregate_redaction_output_shape(self) -> None:
        text = SOURCE_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "`limitations.redactions` contains only `reason_code: PATH_DENIED` and a positive denial `count`",
            text,
        )
        self.assertIn("Include the aggregate only when the count is nonzero", text)
        self.assertIn("Do not include a path ID, path string, path-derived value, branch name", text)

    def test_evaluation_docs_label_non_posix_policy_as_unverified(self) -> None:
        readme = EVALUATION_README.read_text(encoding="utf-8")
        plan = EVALUATION_PLAN.read_text(encoding="utf-8")

        self.assertIn("canonical Skill-file validation on Windows is unsupported", readme)
        self.assertIn("NOT VERIFIED", readme)
        self.assertIn("not a native Windows test, independent evaluation, or host-enforcement evidence", readme)
        self.assertIn("V-07 | Non-POSIX fail-closed dispatch", plan)

    def test_evaluation_matrix_and_evidence_template_cover_every_scenario(self) -> None:
        plan = EVALUATION_PLAN.read_text(encoding="utf-8")
        template = EVIDENCE_TEMPLATE.read_text(encoding="utf-8")
        rubric = EVALUATION_RUBRIC.read_text(encoding="utf-8")
        scenario_ids = set(re.findall(r"^\| ((?:V|H|P)-\d{2}) \|", plan, re.MULTILINE))
        evidence_ids = set(re.findall(r"^\| ((?:V|H|P)-\d{2}) \|", template, re.MULTILINE))

        self.assertEqual(scenario_ids, evidence_ids)
        self.assertEqual(len(scenario_ids), 22)
        header = next(line for line in template.splitlines() if line.startswith("| Scenario ID |"))
        for required_field in (
            "Prerequisites",
            "Procedure",
            "Expected outcome",
            "Actual outcome / evidence field",
            "PASS",
            "FAIL",
            "NOT RUN",
            "BLOCKED",
            "INCONCLUSIVE",
        ):
            self.assertIn(required_field, header)
        for scenario_id in scenario_ids:
            row = next(line for line in template.splitlines() if line.startswith(f"| {scenario_id} |"))
            self.assertEqual(row.count("|"), 8, scenario_id)
            self.assertIn("NOT RUN", row)
            self.assertTrue("| BLOCKED |" in row or "| NOT RUN |" in row, scenario_id)
        self.assertIn("**BLOCKED:** scenario was not executed because", rubric)


if __name__ == "__main__":
    unittest.main()

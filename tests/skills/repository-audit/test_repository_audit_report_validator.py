"""Implementation tests for the dependency-free repository-audit report validator.

Coverage is limited to the report structure, field types, nested object
shapes, enum values, and unknown-field rules that Section 5 of
``docs/architecture/repository-audit-skill-spec.md`` explicitly specifies.
Areas the specification leaves undefined are intentionally not asserted here.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
VALIDATOR = REPO / "scripts" / "repository_audit_report_validator.py"
SPEC = importlib.util.spec_from_file_location(
    "repository_audit_report_validator", VALIDATOR
)
assert SPEC is not None and SPEC.loader is not None
report_validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report_validator)


def valid_report() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "overall_status": "COMPLETE",
        "repository": {"root_id": "repo-001", "is_worktree": True},
        "scope": {"requested_facts": ["current_branch"], "requested_paths": ["P001"]},
        "findings": [],
        "evidence": [],
        "command_ledger": [],
        "assumptions": [],
        "unanswered_questions": [],
        "limitations": {
            "redactions": [],
            "access": [],
            "omitted_scope": [],
            "truncated": False,
            "tests": "NOT_RUN",
        },
        "state_comparison": {"before": None, "after": None, "unchanged": None},
    }


def errors_for(report: object) -> list[dict[str, object]]:
    return report_validator.validate_report(report)


def codes(report: object) -> list[str]:
    return [str(item["code"]) for item in errors_for(report)]


def locations(report: object) -> list[str]:
    return [str(item["location"]) for item in errors_for(report)]


class ValidateReportUnitTests(unittest.TestCase):
    def test_valid_minimal_report_has_no_errors(self) -> None:
        self.assertEqual(errors_for(valid_report()), [])

    def test_non_object_report_rejected(self) -> None:
        for value in ([], "report", 1, None, True):
            with self.subTest(value=value):
                self.assertEqual(codes(value), ["REPORT_TYPE_INVALID"])

    def test_missing_required_top_level_fields(self) -> None:
        report = valid_report()
        report.pop("schema_version")
        report.pop("limitations")
        self.assertEqual(
            errors_for(report),
            [
                {"code": "FIELD_MISSING", "location": "$.limitations"},
                {"code": "FIELD_MISSING", "location": "$.schema_version"},
            ],
        )

    def test_top_level_key_order_is_enforced(self) -> None:
        report = valid_report()
        reordered = {
            "overall_status": report["overall_status"],
            "schema_version": report["schema_version"],
        }
        reordered.update(report)
        self.assertIn("FIELD_ORDER_INVALID", codes(reordered))

    def test_schema_version_value(self) -> None:
        report = valid_report()
        report["schema_version"] = "2.0"
        self.assertEqual(
            errors_for(report), [{"code": "FIELD_VALUE_INVALID", "location": "$.schema_version"}]
        )

    def test_overall_status_enum(self) -> None:
        report = valid_report()
        report["overall_status"] = "DONE"
        self.assertIn("ENUM_INVALID", codes(report))
        report["overall_status"] = 1
        self.assertIn("FIELD_TYPE_INVALID", codes(report))

    def test_repository_contract(self) -> None:
        report = valid_report()
        report["repository"] = {"root_id": "repo-002", "is_worktree": "yes"}
        self.assertEqual(
            errors_for(report),
            [
                {"code": "FIELD_TYPE_INVALID", "location": "$.repository.is_worktree"},
                {"code": "FIELD_VALUE_INVALID", "location": "$.repository.root_id"},
            ],
        )
        report["repository"] = {"root_id": "repo-001", "is_worktree": None}
        self.assertEqual(errors_for(report), [])

    def test_scope_contract(self) -> None:
        report = valid_report()
        report["scope"] = {
            "requested_facts": ["current_branch", "nope"],
            "requested_paths": ["P001", 2],
        }
        self.assertEqual(
            errors_for(report),
            [
                {"code": "ENUM_INVALID", "location": "$.scope.requested_facts[1]"},
                {"code": "FIELD_TYPE_INVALID", "location": "$.scope.requested_paths[1]"},
            ],
        )

    def test_scope_arrays_required_types(self) -> None:
        report = valid_report()
        report["scope"] = {"requested_facts": "current_branch", "requested_paths": {}}
        self.assertEqual(
            errors_for(report),
            [
                {"code": "FIELD_TYPE_INVALID", "location": "$.scope.requested_facts"},
                {"code": "FIELD_TYPE_INVALID", "location": "$.scope.requested_paths"},
            ],
        )

    def test_finding_contract(self) -> None:
        report = valid_report()
        report["findings"] = [
            {
                "id": "F001",
                "status": "MAYBE",
                "code": "ROOT_INVALID",
                "path": "P001",
                "claim": "x" * 257,
                "evidence_ids": ["E001"],
            }
        ]
        self.assertEqual(
            errors_for(report),
            [
                {"code": "LENGTH_EXCEEDED", "location": "$.findings[0].claim"},
                {"code": "ENUM_INVALID", "location": "$.findings[0].status"},
            ],
        )

    def test_finding_unknown_and_missing_fields(self) -> None:
        report = valid_report()
        report["findings"] = [
            {"id": "F001", "status": "UNKNOWN", "code": "ROOT_INVALID", "path": None, "extra": 1}
        ]
        self.assertEqual(
            errors_for(report),
            [
                {"code": "FIELD_MISSING", "location": "$.findings[0].claim"},
                {"code": "FIELD_MISSING", "location": "$.findings[0].evidence_ids"},
                {"code": "UNKNOWN_FIELD", "location": "$.findings[0].extra"},
            ],
        )

    def test_finding_key_order_enforced(self) -> None:
        report = valid_report()
        report["findings"] = [
            {
                "status": "UNKNOWN",
                "id": "F001",
                "code": "ROOT_INVALID",
                "path": None,
                "claim": "c",
                "evidence_ids": [],
            }
        ]
        self.assertIn("FIELD_ORDER_INVALID", codes(report))

    def test_finding_path_accepts_null_or_string_only(self) -> None:
        report = valid_report()
        report["findings"] = [
            {
                "id": "F001",
                "status": "UNKNOWN",
                "code": "ROOT_INVALID",
                "path": 3,
                "claim": "c",
                "evidence_ids": [],
            }
        ]
        self.assertEqual(
            errors_for(report),
            [{"code": "FIELD_TYPE_INVALID", "location": "$.findings[0].path"}],
        )

    def test_evidence_contract(self) -> None:
        report = valid_report()
        report["evidence"] = [{"id": "E001", "kind": "command", "command_id": "C001", "note": "x"}]
        self.assertEqual(
            errors_for(report),
            [
                {"code": "UNKNOWN_FIELD", "location": "$.evidence[0].note"},
                {"code": "FIELD_MISSING", "location": "$.evidence[0].summary"},
            ],
        )

    def test_ledger_contract(self) -> None:
        report = valid_report()
        report["command_ledger"] = [
            {
                "id": "C001",
                "command_id": "git.root",
                "arguments": [],
                "outcome": "PENDING",
                "exit_code": True,
                "summary": "s",
                "truncated": "no",
            }
        ]
        self.assertEqual(
            errors_for(report),
            [
                {"code": "FIELD_TYPE_INVALID", "location": "$.command_ledger[0].exit_code"},
                {"code": "ENUM_INVALID", "location": "$.command_ledger[0].outcome"},
                {"code": "FIELD_TYPE_INVALID", "location": "$.command_ledger[0].truncated"},
            ],
        )

    def test_ledger_exit_code_null_and_int_allowed(self) -> None:
        report = valid_report()
        for exit_code in (None, 0, 128):
            with self.subTest(exit_code=exit_code):
                report["command_ledger"] = [
                    {
                        "id": "C001",
                        "command_id": "git.root",
                        "arguments": [],
                        "outcome": "SUCCESS",
                        "exit_code": exit_code,
                        "summary": "s",
                        "truncated": False,
                    }
                ]
                self.assertEqual(errors_for(report), [])

    def test_limitations_contract(self) -> None:
        report = valid_report()
        report["limitations"] = {
            "redactions": [{"reason_code": "OTHER", "count": 0, "extra": 1}],
            "access": "none",
            "omitted_scope": [],
            "truncated": "no",
            "tests": "PASS",
        }
        self.assertEqual(
            errors_for(report),
            [
                {"code": "FIELD_TYPE_INVALID", "location": "$.limitations.access"},
                {"code": "FIELD_VALUE_INVALID", "location": "$.limitations.redactions[0].count"},
                {"code": "UNKNOWN_FIELD", "location": "$.limitations.redactions[0].extra"},
                {"code": "FIELD_VALUE_INVALID", "location": "$.limitations.redactions[0].reason_code"},
                {"code": "FIELD_VALUE_INVALID", "location": "$.limitations.tests"},
                {"code": "FIELD_TYPE_INVALID", "location": "$.limitations.truncated"},
            ],
        )

    def test_redaction_positive_count(self) -> None:
        report = valid_report()
        report["limitations"]["redactions"] = [
            {"reason_code": "PATH_DENIED", "count": 2}
        ]
        self.assertEqual(errors_for(report), [])

    def test_state_comparison_unchanged_type(self) -> None:
        report = valid_report()
        report["state_comparison"] = {"before": {"x": 1}, "after": None, "unchanged": "yes"}
        self.assertEqual(
            errors_for(report),
            [{"code": "FIELD_TYPE_INVALID", "location": "$.state_comparison.unchanged"}],
        )

    def test_assumptions_and_questions_are_arrays(self) -> None:
        report = valid_report()
        report["assumptions"] = "none"
        report["unanswered_questions"] = {}
        self.assertEqual(
            errors_for(report),
            [
                {"code": "FIELD_TYPE_INVALID", "location": "$.assumptions"},
                {"code": "FIELD_TYPE_INVALID", "location": "$.unanswered_questions"},
            ],
        )

    def test_error_order_is_deterministic_by_location_then_code(self) -> None:
        report = valid_report()
        report["overall_status"] = "NOPE"
        report["schema_version"] = "9"
        first = errors_for(report)
        second = errors_for(json.loads(json.dumps(report)))
        self.assertEqual(first, second)
        self.assertEqual(
            first,
            [
                {"code": "ENUM_INVALID", "location": "$.overall_status"},
                {"code": "FIELD_VALUE_INVALID", "location": "$.schema_version"},
            ],
        )

    def test_scope_requested_facts_history_n_boundaries(self) -> None:
        report = valid_report()
        cases = [
            ("history:1", []),
            ("history:20", []),
            ("history", ["ENUM_INVALID"]),
            ("history:0", ["ENUM_INVALID"]),
            ("history:21", ["ENUM_INVALID"]),
            ("history:x", ["ENUM_INVALID"]),
            ("history:01", ["ENUM_INVALID"]),
            ("history:-1", ["ENUM_INVALID"]),
            ("history:+1", ["ENUM_INVALID"]),
            ("history:1.0", ["ENUM_INVALID"]),
            ("history: 1", ["ENUM_INVALID"]),
        ]
        for value, expected_codes in cases:
            with self.subTest(value=value):
                report["scope"]["requested_facts"] = [value]
                codes_list = codes(report)
                self.assertEqual(codes_list, expected_codes)


class ValidatorCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="repository-audit-report-")
        self.path = Path(self.temp.name) / "report.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, report: str) -> None:
        self.path.write_text(report, encoding="utf-8", newline="\n")

    def invoke(self, *args: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.stderr, "")
        return result, json.loads(result.stdout)

    def test_valid_report_exit_zero_and_stable_output(self) -> None:
        self.write(json.dumps(valid_report()))
        first_result, first = self.invoke("--report-path", str(self.path))
        second_result, second = self.invoke("--report-path", str(self.path))
        self.assertEqual(first_result.returncode, 0)
        self.assertEqual(first, {"validator_version": "1.0", "status": "VALID", "errors": []})
        self.assertEqual(first_result.stdout, second_result.stdout)

    def test_invalid_report_exit_one(self) -> None:
        report = valid_report()
        report["overall_status"] = "NOPE"
        self.write(json.dumps(report))
        result, payload = self.invoke("--report-path", str(self.path))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["status"], "INVALID")
        self.assertEqual(
            payload["errors"], [{"code": "ENUM_INVALID", "location": "$.overall_status"}]
        )

    def test_missing_file_exit_two(self) -> None:
        result, payload = self.invoke("--report-path", str(self.path))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["status"], "ERROR")
        self.assertEqual(payload["errors"], [{"code": "REPORT_FILE_MISSING", "location": None}])

    def test_malformed_json_exit_two(self) -> None:
        self.write("{not json")
        result, payload = self.invoke("--report-path", str(self.path))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["errors"], [{"code": "REPORT_JSON_INVALID", "location": None}])

    def test_invalid_argument_exit_two(self) -> None:
        result, payload = self.invoke("--nope")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["errors"], [{"code": "ARGUMENT_INVALID", "location": None}])



if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Dependency-free contract validator for repository-audit JSON reports.

This module validates only the report structure, field types, nested object
shapes, enum values, and unknown-field rules that Section 5 of
``docs/architecture/repository-audit-skill-spec.md`` explicitly specifies.

Areas the specification does not define are intentionally NOT validated, to
avoid inventing schema rules. In particular this validator does not validate:

* the meaning or grammar of ``command_ledger[].arguments``;
* allowed values for ``evidence[].kind``;
* element shapes of ``assumptions``, ``unanswered_questions``,
  ``limitations.access``, and ``limitations.omitted_scope``;
* the shape of ``state_comparison.before`` / ``state_comparison.after``;
* the allowed set of ``findings[].code`` values (the specification lists
  stable codes with "include", so the set is not closed);
* report-local ID format, uniqueness, or sort order (``P001``, ``B001``,
  ``C001``, ``F001``, ``E001``);
* unknown-field policy outside objects the specification enumerates exactly
  (``findings``, ``evidence``, ``command_ledger`` entries and
  ``limitations.redactions`` entries).

Unknown fields are rejected only where the specification states "exactly two
keys" (redaction entries) or gives a complete "keys in order" list (finding,
evidence, and ledger entries). Top-level, ``repository``, ``scope``,
``limitations``, and ``state_comparison`` objects accept checks only for the
specified keys.

The public entry point is :func:`validate_report`, a pure function returning a
deterministically ordered list of ``{"code", "location"}`` error objects. The
module also exposes a thin CLI (``--report-path`` or stdin) that emits the same
compact JSON shape as ``scripts/validate-skill.py``.
"""

from __future__ import annotations

import json
import sys
import re


VERSION = "1.0"
SCHEMA_VERSION = "1.0"
REPO_ROOT_ID = "repo-001"
MAX_SUMMARY_CODE_POINTS = 256

TOP_LEVEL_ORDER = (
    "schema_version",
    "overall_status",
    "repository",
    "scope",
    "findings",
    "evidence",
    "command_ledger",
    "assumptions",
    "unanswered_questions",
    "limitations",
    "state_comparison",
)
OVERALL_STATUSES = ("COMPLETE", "PARTIAL", "REJECTED")
FINDING_STATUSES = ("VERIFIED", "INFERRED", "UNKNOWN")
LEDGER_OUTCOMES = ("SUCCESS", "FAILURE", "TIMEOUT", "SKIPPED")
REQUESTED_FACTS = (
    "current_branch",
    "working_tree_status",
    "local_branches",
    "index",
    )
HISTORY_FACT_RE = re.compile(r"^history:(0|[1-9][0-9]*)$")
MAX_HISTORY_N = 20
REPOSITORY_KEYS = ("root_id", "is_worktree")
SCOPE_KEYS = ("requested_facts", "requested_paths")
FINDING_KEYS = ("id", "status", "code", "path", "claim", "evidence_ids")
EVIDENCE_KEYS = ("id", "kind", "command_id", "summary")
LEDGER_KEYS = (
    "id",
    "command_id",
    "arguments",
    "outcome",
    "exit_code",
    "summary",
    "truncated",
)
LIMITATIONS_KEYS = ("redactions", "access", "omitted_scope", "truncated", "tests")
REDACTION_KEYS = ("reason_code", "count")
STATE_COMPARISON_KEYS = ("before", "after", "unchanged")

REDACTION_REASON_CODE = "PATH_DENIED"
TESTS_VALUE = "NOT_RUN"


def error(code: str, location: str | None = None) -> dict[str, object]:
    """Build one stable contract error object."""
    return {"code": code, "location": location}


def _sort_key(item: dict[str, object]) -> tuple[str, str]:
    location = item["location"]
    return ("" if location is None else str(location), str(item["code"]))


def _ordered(errors: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(errors, key=_sort_key)


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_string(value: object) -> bool:
    return isinstance(value, str)


def _is_object(value: object) -> bool:
    return isinstance(value, dict)


def _is_array(value: object) -> bool:
    return isinstance(value, list)


def _is_bool_or_null(value: object) -> bool:
    return value is None or isinstance(value, bool)


def _child(location: str, key: str) -> str:
    return f"{location}.{key}"


def _index(location: str, position: int) -> str:
    return f"{location}[{position}]"


def _check_keys(
    obj: dict[str, object],
    keys: tuple[str, ...],
    location: str,
    errors: list[dict[str, object]],
    *,
    require_present: bool = True,
    reject_unknown: bool = False,
    enforce_order: bool = False,
) -> None:
    if require_present:
        for key in keys:
            if key not in obj:
                errors.append(error("FIELD_MISSING", _child(location, key)))
    if reject_unknown:
        for key in obj:
            if key not in keys:
                errors.append(error("UNKNOWN_FIELD", _child(location, str(key))))
    if enforce_order:
        present = [key for key in obj if key in keys]
        expected = [key for key in keys if key in obj]
        if present != expected:
            errors.append(error("FIELD_ORDER_INVALID", location))


def _check_string(
    value: object, location: str, errors: list[dict[str, object]]
) -> bool:
    if not _is_string(value):
        errors.append(error("FIELD_TYPE_INVALID", location))
        return False
    return True


def _check_enum(
    value: object,
    allowed: tuple[str, ...],
    location: str,
    errors: list[dict[str, object]],
) -> None:
    if not _is_string(value):
        errors.append(error("FIELD_TYPE_INVALID", location))
    elif value not in allowed:
        errors.append(error("ENUM_INVALID", location))


def _check_bounded_string(
    value: object, location: str, errors: list[dict[str, object]]
) -> None:
    if not _check_string(value, location, errors):
        return
    assert isinstance(value, str)
    if len(value) > MAX_SUMMARY_CODE_POINTS:
        errors.append(error("LENGTH_EXCEEDED", location))


def _check_object(
    value: object, location: str, errors: list[dict[str, object]]
) -> bool:
    if not _is_object(value):
        errors.append(error("FIELD_TYPE_INVALID", location))
        return False
    return True


def _check_array(value: object, location: str, errors: list[dict[str, object]]) -> bool:
    if not _is_array(value):
        errors.append(error("FIELD_TYPE_INVALID", location))
        return False
    return True


def _validate_repository(value: object, errors: list[dict[str, object]]) -> None:
    location = "$.repository"
    if not _check_object(value, location, errors):
        return
    assert isinstance(value, dict)
    if "root_id" in value:
        if _check_string(value["root_id"], _child(location, "root_id"), errors):
            if value["root_id"] != REPO_ROOT_ID:
                errors.append(error("FIELD_VALUE_INVALID", _child(location, "root_id")))
    if "is_worktree" in value and not _is_bool_or_null(value["is_worktree"]):
        errors.append(error("FIELD_TYPE_INVALID", _child(location, "is_worktree")))


def _validate_scope(value: object, errors: list[dict[str, object]]) -> None:
    location = "$.scope"
    if not _check_object(value, location, errors):
        return
    assert isinstance(value, dict)
    if "requested_facts" in value and _check_array(
        value["requested_facts"], _child(location, "requested_facts"), errors
    ):
        for position, fact in enumerate(value["requested_facts"]):
            item_location = _index(_child(location, "requested_facts"), position)
            if not _is_string(fact):
                errors.append(error("FIELD_TYPE_INVALID", item_location))
                continue
            if fact == "history":
                errors.append(error("ENUM_INVALID", item_location))
                continue
            if fact in REQUESTED_FACTS:
                continue
            m = HISTORY_FACT_RE.fullmatch(fact)
            if not m or int(m.group(1)) < 1 or int(m.group(1)) > MAX_HISTORY_N:
                errors.append(error("ENUM_INVALID", item_location))
            # else valid history:N - no error
    if "requested_paths" in value and _check_array(
        value["requested_paths"], _child(location, "requested_paths"), errors
    ):
        for position, path_id in enumerate(value["requested_paths"]):
            if not _is_string(path_id):
                errors.append(
                    error("FIELD_TYPE_INVALID", _index(_child(location, "requested_paths"), position))
                )


def _validate_finding(
    value: object, location: str, errors: list[dict[str, object]]
) -> None:
    if not _check_object(value, location, errors):
        return
    assert isinstance(value, dict)
    _check_keys(
        value,
        FINDING_KEYS,
        location,
        errors,
        reject_unknown=True,
        enforce_order=True,
    )
    if "id" in value:
        _check_string(value["id"], _child(location, "id"), errors)
    if "status" in value:
        _check_enum(value["status"], FINDING_STATUSES, _child(location, "status"), errors)
    if "code" in value:
        _check_string(value["code"], _child(location, "code"), errors)
    if "path" in value and value["path"] is not None and not _is_string(value["path"]):
        errors.append(error("FIELD_TYPE_INVALID", _child(location, "path")))
    if "claim" in value:
        _check_bounded_string(value["claim"], _child(location, "claim"), errors)
    if "evidence_ids" in value and _check_array(
        value["evidence_ids"], _child(location, "evidence_ids"), errors
    ):
        for position, evidence_id in enumerate(value["evidence_ids"]):
            if not _is_string(evidence_id):
                errors.append(
                    error("FIELD_TYPE_INVALID", _index(_child(location, "evidence_ids"), position))
                )


def _validate_evidence(
    value: object, location: str, errors: list[dict[str, object]]
) -> None:
    if not _check_object(value, location, errors):
        return
    assert isinstance(value, dict)
    _check_keys(
        value,
        EVIDENCE_KEYS,
        location,
        errors,
        reject_unknown=True,
        enforce_order=True,
    )
    for key in ("id", "kind", "command_id"):
        if key in value:
            _check_string(value[key], _child(location, key), errors)
    if "summary" in value:
        _check_bounded_string(value["summary"], _child(location, "summary"), errors)


def _validate_ledger_entry(
    value: object, location: str, errors: list[dict[str, object]]
) -> None:
    if not _check_object(value, location, errors):
        return
    assert isinstance(value, dict)
    _check_keys(
        value,
        LEDGER_KEYS,
        location,
        errors,
        reject_unknown=True,
        enforce_order=True,
    )
    for key in ("id", "command_id"):
        if key in value:
            _check_string(value[key], _child(location, key), errors)
    if "outcome" in value:
        _check_enum(value["outcome"], LEDGER_OUTCOMES, _child(location, "outcome"), errors)
    if "exit_code" in value:
        exit_code = value["exit_code"]
        if exit_code is not None and not _is_int(exit_code):
            errors.append(error("FIELD_TYPE_INVALID", _child(location, "exit_code")))
    if "summary" in value:
        _check_bounded_string(value["summary"], _child(location, "summary"), errors)
    if "truncated" in value and not isinstance(value["truncated"], bool):
        errors.append(error("FIELD_TYPE_INVALID", _child(location, "truncated")))


def _validate_redaction(
    value: object, location: str, errors: list[dict[str, object]]
) -> None:
    if not _check_object(value, location, errors):
        return
    assert isinstance(value, dict)
    _check_keys(value, REDACTION_KEYS, location, errors, reject_unknown=True)
    if "reason_code" in value:
        if _check_string(value["reason_code"], _child(location, "reason_code"), errors):
            if value["reason_code"] != REDACTION_REASON_CODE:
                errors.append(
                    error("FIELD_VALUE_INVALID", _child(location, "reason_code"))
                )
    if "count" in value:
        count = value["count"]
        if not _is_int(count):
            errors.append(error("FIELD_TYPE_INVALID", _child(location, "count")))
        elif count <= 0:
            errors.append(error("FIELD_VALUE_INVALID", _child(location, "count")))


def _validate_limitations(value: object, errors: list[dict[str, object]]) -> None:
    location = "$.limitations"
    if not _check_object(value, location, errors):
        return
    assert isinstance(value, dict)
    for key in ("redactions", "access", "omitted_scope"):
        if key in value:
            item_location = _child(location, key)
            if not _check_array(value[key], item_location, errors):
                continue
            if key == "redactions":
                assert isinstance(value[key], list)
                for position, entry in enumerate(value[key]):
                    _validate_redaction(entry, _index(item_location, position), errors)
    if "truncated" in value and not isinstance(value["truncated"], bool):
        errors.append(error("FIELD_TYPE_INVALID", _child(location, "truncated")))
    if "tests" in value:
        if _check_string(value["tests"], _child(location, "tests"), errors):
            if value["tests"] != TESTS_VALUE:
                errors.append(error("FIELD_VALUE_INVALID", _child(location, "tests")))


def _validate_state_comparison(value: object, errors: list[dict[str, object]]) -> None:
    location = "$.state_comparison"
    if not _check_object(value, location, errors):
        return
    assert isinstance(value, dict)
    if "unchanged" in value and not _is_bool_or_null(value["unchanged"]):
        errors.append(error("FIELD_TYPE_INVALID", _child(location, "unchanged")))


def validate_report(report: object) -> list[dict[str, object]]:
    """Validate a decoded repository-audit report object.

    Returns a deterministically ordered list of ``{"code", "location"}`` error
    objects. An empty list means the report satisfies every explicitly
    specified rule this module checks.
    """
    errors: list[dict[str, object]] = []
    if not _is_object(report):
        return [error("REPORT_TYPE_INVALID", "$")]
    assert isinstance(report, dict)
    _check_keys(
        report,
        TOP_LEVEL_ORDER,
        "$",
        errors,
        reject_unknown=False,
        enforce_order=True,
    )

    if "schema_version" in report:
        location = "$.schema_version"
        if _check_string(report["schema_version"], location, errors):
            if report["schema_version"] != SCHEMA_VERSION:
                errors.append(error("FIELD_VALUE_INVALID", location))
    if "overall_status" in report:
        _check_enum(report["overall_status"], OVERALL_STATUSES, "$.overall_status", errors)
    if "repository" in report:
        _validate_repository(report["repository"], errors)
    if "scope" in report:
        _validate_scope(report["scope"], errors)

    if "findings" in report and _check_array(report["findings"], "$.findings", errors):
        for position, finding in enumerate(report["findings"]):
            _validate_finding(finding, _index("$.findings", position), errors)
    if "evidence" in report and _check_array(report["evidence"], "$.evidence", errors):
        for position, entry in enumerate(report["evidence"]):
            _validate_evidence(entry, _index("$.evidence", position), errors)
    if "command_ledger" in report and _check_array(
        report["command_ledger"], "$.command_ledger", errors
    ):
        for position, entry in enumerate(report["command_ledger"]):
            _validate_ledger_entry(entry, _index("$.command_ledger", position), errors)
    if "assumptions" in report:
        _check_array(report["assumptions"], "$.assumptions", errors)
    if "unanswered_questions" in report:
        _check_array(report["unanswered_questions"], "$.unanswered_questions", errors)
    if "limitations" in report:
        _validate_limitations(report["limitations"], errors)
    if "state_comparison" in report:
        _validate_state_comparison(report["state_comparison"], errors)

    return _ordered(errors)


def _emit(status: str, errors: list[dict[str, object]], exit_code: int) -> int:
    sys.stdout.write(
        json.dumps(
            {"validator_version": VERSION, "status": status, "errors": _ordered(errors)},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )
    return exit_code


def _load_report(argv: list[str]) -> tuple[bytes | None, list[dict[str, object]]]:
    path: str | None = None
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument != "--report-path":
            return None, [error("ARGUMENT_INVALID")]
        if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
            return None, [error("ARGUMENT_INVALID")]
        if path is not None:
            return None, [error("ARGUMENT_INVALID")]
        path = argv[index + 1]
        index += 2
    if path is None:
        return sys.stdin.buffer.read(), []
    try:
        with open(path, "rb") as stream:
            return stream.read(), []
    except FileNotFoundError:
        return None, [error("REPORT_FILE_MISSING")]
    except OSError:
        return None, [error("REPORT_FILE_UNREADABLE")]


def main(argv: list[str]) -> int:
    raw, load_errors = _load_report(argv)
    if load_errors:
        status = "ERROR"
        return _emit(status, load_errors, 2)
    assert raw is not None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _emit("ERROR", [error("REPORT_UTF8_INVALID")], 2)
    try:
        report = json.loads(text)
    except json.JSONDecodeError:
        return _emit("ERROR", [error("REPORT_JSON_INVALID")], 2)
    errors = validate_report(report)
    if errors:
        return _emit("INVALID", errors, 1)
    return _emit("VALID", [], 0)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception:
        raise SystemExit(_emit("ERROR", [error("VALIDATOR_INTERNAL_ERROR")], 2))

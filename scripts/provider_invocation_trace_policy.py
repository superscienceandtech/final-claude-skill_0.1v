"""Acceptance policy for canonical provider invocation trace reports."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from scripts.provider_invocation_trace_validator import (
    ProviderInvocationTraceFinding,
    ProviderInvocationTraceValidationReport,
    TraceFindingCategory,
    TraceFindingSeverity,
)


_REASON_CODE_PATTERN = re.compile(r"[A-Z][A-Z0-9_]*\Z")
_FIELD_PATH_PATTERN = re.compile(
    r"\$(?:\.[A-Za-z_][A-Za-z0-9_]*|\[[0-9]+\])*\Z"
)


class TraceAcceptanceDecision(str, Enum):
    ACCEPT = "accept"
    ACCEPT_WITH_WARNINGS = "accept_with_warnings"
    REJECT = "reject"


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePolicyDecision:
    """Immutable acceptance result, not an authorization or trust decision."""

    decision: TraceAcceptanceDecision
    accepted: bool
    reason_codes: tuple[str, ...]
    findings: tuple[ProviderInvocationTraceFinding, ...]
    explanation: str
    establishes_authenticity: bool = False
    authorizes_execution: bool = False
    verifies_execution_correctness: bool = False
    independently_verifies_execution: bool = False


def evaluate_provider_invocation_trace_policy(
    report: object,
) -> ProviderInvocationTracePolicyDecision:
    """Apply the conservative default policy to a canonical validation report.

    Invalid or malformed reports are rejected. Blocking findings are those
    with error severity or structural/semantic error categories. Non-blocking
    warnings and informational findings are accepted with disclosure.
    """
    normalized_findings = _validate_and_copy_findings(report)
    if normalized_findings is None:
        return ProviderInvocationTracePolicyDecision(
            decision=TraceAcceptanceDecision.REJECT,
            accepted=False,
            reason_codes=("MALFORMED_VALIDATION_REPORT",),
            findings=(),
            explanation=(
                "The validation report is malformed or unsupported; the trace "
                "was rejected."
            ),
        )

    is_valid = report.is_valid
    blocking = tuple(
        finding
        for finding in normalized_findings
        if finding.severity is TraceFindingSeverity.ERROR
        or finding.category
        in (
            TraceFindingCategory.STRUCTURAL_ERROR,
            TraceFindingCategory.SEMANTIC_INCONSISTENCY,
        )
    )
    has_non_blocking = any(
        finding not in blocking for finding in normalized_findings
    )

    if not is_valid or blocking:
        reason_codes: list[str] = []
        if not is_valid:
            reason_codes.append("VALIDATION_REPORT_INVALID")
        if blocking:
            reason_codes.append("BLOCKING_FINDINGS_PRESENT")
        return ProviderInvocationTracePolicyDecision(
            decision=TraceAcceptanceDecision.REJECT,
            accepted=False,
            reason_codes=tuple(reason_codes),
            findings=normalized_findings,
            explanation=(
                "The trace does not satisfy the configured structural and "
                "semantic consistency policy."
            ),
        )

    if has_non_blocking:
        return ProviderInvocationTracePolicyDecision(
            decision=TraceAcceptanceDecision.ACCEPT_WITH_WARNINGS,
            accepted=True,
            reason_codes=("NON_BLOCKING_FINDINGS_PRESENT",),
            findings=normalized_findings,
            explanation=(
                "The trace satisfies the consistency policy with non-blocking "
                "limitations that require disclosure."
            ),
        )

    return ProviderInvocationTracePolicyDecision(
        decision=TraceAcceptanceDecision.ACCEPT,
        accepted=True,
        reason_codes=("NO_NON_BLOCKING_FINDINGS",),
        findings=normalized_findings,
        explanation=(
            "The trace satisfies the configured structural-consistency policy."
        ),
    )


def _validate_and_copy_findings(
    report: object,
) -> tuple[ProviderInvocationTraceFinding, ...] | None:
    if type(report) is not ProviderInvocationTraceValidationReport:
        return None
    if type(report.is_valid) is not bool or type(report.findings) is not tuple:
        return None

    copied: list[ProviderInvocationTraceFinding] = []
    for finding in report.findings:
        if type(finding) is not ProviderInvocationTraceFinding:
            return None
        if (
            type(finding.code) is not str
            or not _REASON_CODE_PATTERN.fullmatch(finding.code)
            or type(finding.category) is not TraceFindingCategory
            or type(finding.severity) is not TraceFindingSeverity
            or (
                finding.field_path is not None
                and (
                    type(finding.field_path) is not str
                    or not _FIELD_PATH_PATTERN.fullmatch(finding.field_path)
                )
            )
            or (
                finding.sequence is not None
                and (type(finding.sequence) is not int or finding.sequence < 1)
            )
            or type(finding.message) is not str
        ):
            return None
        copied.append(
            ProviderInvocationTraceFinding(
                code=finding.code,
                category=finding.category,
                severity=finding.severity,
                field_path=finding.field_path,
                sequence=finding.sequence,
                message=_safe_finding_message(finding),
            )
        )
    return tuple(sorted(copied, key=_finding_sort_key))


def _safe_finding_message(finding: ProviderInvocationTraceFinding) -> str:
    if (
        finding.severity is TraceFindingSeverity.ERROR
        or finding.category
        in (
            TraceFindingCategory.STRUCTURAL_ERROR,
            TraceFindingCategory.SEMANTIC_INCONSISTENCY,
        )
    ):
        return "A blocking consistency finding was reported."
    if finding.severity is TraceFindingSeverity.WARNING:
        return "A non-blocking warning was reported."
    return "An informational limitation was reported."


def _finding_sort_key(
    finding: ProviderInvocationTraceFinding,
) -> tuple[int, int, str, str]:
    category_order = {
        TraceFindingCategory.STRUCTURAL_ERROR: 0,
        TraceFindingCategory.SEMANTIC_INCONSISTENCY: 1,
        TraceFindingCategory.INFORMATIONAL_LIMITATION: 2,
    }
    severity_order = {
        TraceFindingSeverity.ERROR: 0,
        TraceFindingSeverity.WARNING: 1,
        TraceFindingSeverity.INFO: 2,
    }
    return (
        category_order[finding.category],
        severity_order[finding.severity],
        finding.sequence if finding.sequence is not None else -1,
        finding.code,
    )

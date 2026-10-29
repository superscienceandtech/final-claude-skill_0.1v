"""Read-only integrity and consistency validation for invocation traces."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType

from scripts.provider_invocation_trace import ProviderInvocationTrace
from scripts.provider_invocation_trace_export import (
    ProviderInvocationTraceExportError,
    export_provider_invocation_trace,
)
from scripts.provider_invocation_trace_import import (
    ImportedProviderInvocationTrace,
    ImportedProviderInvocationTraceEvent,
    ProviderInvocationTraceImportError,
    import_provider_invocation_trace,
)


class TraceFindingCategory(str, Enum):
    STRUCTURAL_ERROR = "structural_error"
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"
    INFORMATIONAL_LIMITATION = "informational_limitation"


class TraceFindingSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True, slots=True)
class ProviderInvocationTraceFinding:
    """Safe, deterministic finding for a trace validation report."""

    code: str
    category: TraceFindingCategory
    severity: TraceFindingSeverity
    field_path: str | None
    sequence: int | None
    message: str


@dataclass(frozen=True, slots=True)
class ProviderInvocationTraceValidationReport:
    """Immutable validation outcome; validity means structural consistency only."""

    is_valid: bool
    findings: tuple[ProviderInvocationTraceFinding, ...]


_SEMANTIC_IMPORT_CODES = frozenset(
    {"invalid_event_order", "invalid_event_semantics"}
)
_IDENTITY_FIELDS = ("provider_id", "capability_id", "operation_id")
_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")


def validate_provider_invocation_trace(
    trace: object,
) -> ProviderInvocationTraceValidationReport:
    """Validate a canonical snapshot or validated imported trace representation.

    The report evaluates structure and internal consistency only. It does not
    authenticate imported data, authorize execution, or verify provider claims.
    """
    is_imported = type(trace) is ImportedProviderInvocationTrace
    try:
        normalized = _normalize_trace(trace)
    except ProviderInvocationTraceExportError:
        return _failure(
            "INVALID_CANONICAL_TRACE",
            TraceFindingCategory.STRUCTURAL_ERROR,
            "trace does not satisfy the canonical trace snapshot contract.",
        )
    except ProviderInvocationTraceImportError as error:
        category = (
            TraceFindingCategory.SEMANTIC_INCONSISTENCY
            if error.code in _SEMANTIC_IMPORT_CODES
            else TraceFindingCategory.STRUCTURAL_ERROR
        )
        return _failure(
            f"IMPORT_{error.code.upper()}",
            category,
            "trace data does not satisfy the canonical import contract.",
            field_path=error.path,
        )
    except (TypeError, ValueError, AttributeError):
        return _failure(
            "UNSUPPORTED_TRACE_REPRESENTATION",
            TraceFindingCategory.STRUCTURAL_ERROR,
            "trace must be a supported canonical snapshot or imported record.",
        )

    findings = _validate_optional_identity_consistency(
        normalized.events,
        trace if type(trace) is ProviderInvocationTrace else None,
    )
    if any(event.execution_independently_verified for event in normalized.events):
        findings.append(
            ProviderInvocationTraceFinding(
                code="INDEPENDENT_VERIFICATION_UNSUPPORTED",
                category=TraceFindingCategory.SEMANTIC_INCONSISTENCY,
                severity=TraceFindingSeverity.ERROR,
                field_path="$.events",
                sequence=None,
                message=(
                    "the trace contract has no independent verification mechanism."
                ),
            )
        )
    if is_imported:
        findings.append(
            ProviderInvocationTraceFinding(
                code="IMPORTED_TRACE_NOT_AUTHENTICATED",
                category=TraceFindingCategory.INFORMATIONAL_LIMITATION,
                severity=TraceFindingSeverity.INFO,
                field_path=None,
                sequence=None,
                message=(
                    "schema validation does not authenticate imported trace data."
                ),
            )
        )
    if any(event.provider_execution_reported for event in normalized.events):
        findings.append(
            ProviderInvocationTraceFinding(
                code="PROVIDER_EXECUTION_CLAIM_UNVERIFIED",
                category=TraceFindingCategory.INFORMATIONAL_LIMITATION,
                severity=TraceFindingSeverity.INFO,
                field_path="$.events",
                sequence=None,
                message=(
                    "provider-reported execution is not independently verified."
                ),
            )
        )
    ordered = tuple(sorted(findings, key=_finding_sort_key))
    return ProviderInvocationTraceValidationReport(
        is_valid=not any(
            finding.severity is TraceFindingSeverity.ERROR for finding in ordered
        ),
        findings=ordered,
    )


def _normalize_trace(
    trace: object,
) -> ImportedProviderInvocationTrace:
    if type(trace) is ProviderInvocationTrace:
        exported = export_provider_invocation_trace(trace)
        return import_provider_invocation_trace(exported.to_dict())
    if type(trace) is ImportedProviderInvocationTrace:
        if type(trace.events) is not tuple:
            raise ProviderInvocationTraceImportError(
                "invalid_type",
                "$.events",
                "imported event collection must be an immutable tuple.",
            )
        event_mappings: list[dict[str, object]] = []
        for index, event in enumerate(trace.events):
            if type(event) is not ImportedProviderInvocationTraceEvent:
                raise ProviderInvocationTraceImportError(
                    "invalid_type",
                    f"$.events[{index}]",
                    "imported event must use the canonical imported event record.",
                )
            if type(event.details) not in (dict, MappingProxyType):
                raise ProviderInvocationTraceImportError(
                    "invalid_type",
                    f"$.events[{index}].details",
                    "event details must use a supported mapping representation.",
                )
            event_mappings.append(
                {
                    "event_id": event.event_id,
                    "correlation_id": event.correlation_id,
                    "sequence": event.sequence,
                    "event_type": event.event_type,
                    "lifecycle_state": event.lifecycle_state,
                    "issue_codes": event.issue_codes,
                    "provider_id": event.provider_id,
                    "capability_id": event.capability_id,
                    "operation_id": event.operation_id,
                    "provider_execution_reported": event.provider_execution_reported,
                    "execution_independently_verified": (
                        event.execution_independently_verified
                    ),
                    "details": event.details,
                }
            )
        return import_provider_invocation_trace(
            {
                "correlation_id": trace.correlation_id,
                "events": event_mappings,
            }
        )
    raise TypeError("unsupported trace representation")


def _validate_optional_identity_consistency(
    events: tuple[ImportedProviderInvocationTraceEvent, ...],
    canonical_trace: ProviderInvocationTrace | None,
) -> list[ProviderInvocationTraceFinding]:
    findings: list[ProviderInvocationTraceFinding] = []
    for field_name in _IDENTITY_FIELDS:
        trace_value = (
            getattr(canonical_trace, field_name)
            if canonical_trace is not None
            else None
        )
        if trace_value is not None and (
            type(trace_value) is not str
            or not _IDENTIFIER_PATTERN.fullmatch(trace_value)
        ):
            findings.append(
                ProviderInvocationTraceFinding(
                    code=f"INVALID_TRACE_{field_name.upper()}",
                    category=TraceFindingCategory.STRUCTURAL_ERROR,
                    severity=TraceFindingSeverity.ERROR,
                    field_path=f"$.{field_name}",
                    sequence=None,
                    message=f"trace {field_name} is not a canonical identifier.",
                )
            )
        first_value: str | None = None
        first_event_index: int | None = None
        for event_index, event in enumerate(events):
            value = getattr(event, field_name)
            if value is None:
                continue
            if first_value is None:
                first_value = value
                first_event_index = event_index
            elif value != first_value:
                findings.append(
                    ProviderInvocationTraceFinding(
                        code=f"INCONSISTENT_{field_name.upper()}",
                        category=TraceFindingCategory.SEMANTIC_INCONSISTENCY,
                        severity=TraceFindingSeverity.ERROR,
                        field_path=f"$.events[{event_index}].{field_name}",
                        sequence=event.sequence,
                        message=(
                            f"non-null {field_name} values differ across trace events."
                        ),
                    )
                )
                break
        if (
            canonical_trace is not None
            and trace_value is not None
            and first_value is not None
            and first_event_index is not None
            and trace_value != first_value
        ):
            findings.append(
                ProviderInvocationTraceFinding(
                    code=f"TRACE_EVENT_{field_name.upper()}_MISMATCH",
                    category=TraceFindingCategory.SEMANTIC_INCONSISTENCY,
                    severity=TraceFindingSeverity.ERROR,
                    field_path=(
                        f"$.events[{first_event_index}].{field_name}"
                    ),
                    sequence=events[first_event_index].sequence,
                    message=(
                        f"event {field_name} does not match the canonical trace."
                    ),
                )
            )
    return findings


def _finding_sort_key(
    finding: ProviderInvocationTraceFinding,
) -> tuple[int, int, str, str]:
    category_order = {
        TraceFindingCategory.STRUCTURAL_ERROR: 0,
        TraceFindingCategory.SEMANTIC_INCONSISTENCY: 1,
        TraceFindingCategory.INFORMATIONAL_LIMITATION: 2,
    }
    return (
        category_order[finding.category],
        finding.sequence if finding.sequence is not None else -1,
        finding.field_path or "",
        finding.code,
    )


def _failure(
    code: str,
    category: TraceFindingCategory,
    message: str,
    *,
    field_path: str | None = None,
) -> ProviderInvocationTraceValidationReport:
    return ProviderInvocationTraceValidationReport(
        is_valid=False,
        findings=(
            ProviderInvocationTraceFinding(
                code=code,
                category=category,
                severity=TraceFindingSeverity.ERROR,
                field_path=field_path,
                sequence=None,
                message=message,
            ),
        ),
    )

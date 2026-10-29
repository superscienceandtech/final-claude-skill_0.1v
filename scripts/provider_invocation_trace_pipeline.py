"""Thin deterministic composition of provider invocation trace contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar

from scripts.provider_invocation_trace import ProviderInvocationTrace
from scripts.provider_invocation_trace_export import (
    ProviderInvocationTraceExport,
    ProviderInvocationTraceExportError,
    export_provider_invocation_trace,
)
from scripts.provider_invocation_trace_import import (
    ImportedProviderInvocationTrace,
    ProviderInvocationTraceImportError,
    import_provider_invocation_trace,
)
from scripts.provider_invocation_trace_policy import (
    ProviderInvocationTracePolicyDecision,
    TraceAcceptanceDecision,
    evaluate_provider_invocation_trace_policy,
)
from scripts.provider_invocation_trace_validator import (
    ProviderInvocationTraceFinding,
    ProviderInvocationTraceValidationReport,
    TraceFindingCategory,
    TraceFindingSeverity,
    validate_provider_invocation_trace,
)

_SAFE_FIELD_PATH_PATTERN = re.compile(
    r"\$(?:\.[A-Za-z_][A-Za-z0-9_]*|\[[0-9]+\])*\Z"
)
_EnumValue = TypeVar("_EnumValue", bound=Enum)
_SAFE_FINDING_MESSAGES = frozenset(
    {
        "A blocking consistency finding was reported.",
        "A non-blocking warning was reported.",
        "An informational limitation was reported.",
    }
)


class TracePipelineStatus(str, Enum):
    ACCEPTED = "accepted"
    ACCEPTED_WITH_WARNINGS = "accepted_with_warnings"
    REJECTED = "rejected"


class TracePipelineStage(str, Enum):
    EXPORT = "export"
    IMPORT = "import"
    VALIDATION = "validation"
    POLICY = "policy"


class TracePipelineStageStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class DiagnosticSummaryRoundTripStatus(str, Enum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    FAILED = "failed"


class DiagnosticSummaryComparisonStatus(str, Enum):
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"


class DiagnosticSummaryComparisonRoundTripStatus(str, Enum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    FAILED = "failed"


class ComparisonRoundTripDiagnosticSummaryRoundTripStatus(str, Enum):
    CONSISTENT = "consistent"
    SERIALIZATION_FAILED = "serialization_failed"
    DESERIALIZATION_FAILED = "deserialization_failed"
    SEMANTIC_MISMATCH = "semantic_mismatch"


class ComparisonRoundTripResultRoundTripStatus(str, Enum):
    CONSISTENT = "consistent"
    SERIALIZATION_FAILED = "serialization_failed"
    DESERIALIZATION_FAILED = "deserialization_failed"
    SEMANTIC_MISMATCH = "semantic_mismatch"


class ProviderInvocationTracePipelineSerializationError(ValueError):
    """Raised when a diagnostic summary cannot be safely serialized."""

    def __init__(self) -> None:
        self.code = "DIAGNOSTIC_SUMMARY_MALFORMED"
        super().__init__(
            "diagnostic summary does not satisfy the supported serialization contract."
        )


class ProviderInvocationTracePipelineComparisonSerializationError(ValueError):
    """Raised when a comparison result is outside its serialization contract."""

    def __init__(self) -> None:
        self.code = "DIAGNOSTIC_COMPARISON_MALFORMED"
        super().__init__(
            "diagnostic comparison does not satisfy the supported serialization contract."
        )


class ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummarySerializationError(
    ValueError
):
    """Raised when a comparison round-trip diagnostic summary is malformed."""

    def __init__(self) -> None:
        self.code = "COMPARISON_ROUND_TRIP_DIAGNOSTIC_SUMMARY_MALFORMED"
        super().__init__(
            "comparison round-trip diagnostic summary is outside the supported contract."
        )


class ProviderInvocationTracePipelineComparisonRoundTripResultSerializationError(
    ValueError
):
    """Raised when a comparison round-trip result cannot be serialized."""

    def __init__(self) -> None:
        self.code = "COMPARISON_ROUND_TRIP_RESULT_MALFORMED"
        super().__init__(
            "comparison round-trip result is outside the supported serialization contract."
        )


class ProviderInvocationTracePipelineComparisonRoundTripResultDeserializationError(
    ValueError
):
    """Raised when serialized comparison round-trip result data is malformed."""

    def __init__(self) -> None:
        self.code = "COMPARISON_ROUND_TRIP_RESULT_DESERIALIZATION_MALFORMED"
        super().__init__(
            "serialized comparison round-trip result is outside the supported contract."
        )


@dataclass(frozen=True, slots=True)
class TracePipelineStageOutcome:
    """Safe, stable outcome for one processing stage."""

    stage: TracePipelineStage
    status: TracePipelineStageStatus
    issue_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineResult:
    """Immutable results from export, import, validation, and policy stages."""

    status: TracePipelineStatus
    export_result: ProviderInvocationTraceExport | None
    import_result: ImportedProviderInvocationTrace | None
    validation_report: ProviderInvocationTraceValidationReport | None
    policy_decision: ProviderInvocationTracePolicyDecision | None
    stage_outcomes: tuple[TracePipelineStageOutcome, ...]
    rejected_at: TracePipelineStage | None
    provenance_authenticated: bool = False
    authorizes_provider_execution: bool = False
    independently_verifies_execution: bool = False


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineDiagnosticSummary:
    """Safe, immutable overview of a pipeline result's recorded stage progress."""

    status: TracePipelineStatus
    failed_stage: TracePipelineStage | None
    stage_outcomes: tuple[TracePipelineStageOutcome, ...]
    stage_issue_codes: tuple[tuple[TracePipelineStage, tuple[str, ...]], ...]
    stages_skipped: bool
    validation_completed: bool
    policy_evaluation_completed: bool
    policy_decision: ProviderInvocationTracePolicyDecision | None
    provenance_authenticated: bool
    authorizes_provider_execution: bool
    independently_verifies_execution: bool
    summary_issue_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineDiagnosticSummaryRoundTrip:
    """Immutable result of serializing and reconstructing a diagnostic summary."""

    status: DiagnosticSummaryRoundTripStatus
    original_summary: ProviderInvocationTracePipelineDiagnosticSummary | None
    reconstructed_summary: ProviderInvocationTracePipelineDiagnosticSummary | None
    semantic_consistency_established: bool
    issue_code: str | None


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineDiagnosticSummaryComparison:
    """Immutable semantic comparison result for two diagnostic summaries."""

    status: DiagnosticSummaryComparisonStatus
    comparison_completed: bool
    semantically_equivalent: bool
    differing_fields: tuple[str, ...]
    issue_code: str | None


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTrip:
    """Immutable result of a comparison-result serialization round trip."""

    status: DiagnosticSummaryComparisonRoundTripStatus
    operation_completed: bool
    semantic_consistency_established: bool
    original_comparison: ProviderInvocationTracePipelineDiagnosticSummaryComparison | None
    reconstructed_comparison: ProviderInvocationTracePipelineDiagnosticSummaryComparison | None
    issue_code: str | None


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary:
    """Safe overview of an existing comparison round-trip result."""

    diagnostic_summary_produced: bool
    status: DiagnosticSummaryComparisonRoundTripStatus
    operation_completed: bool
    semantic_consistency_established: bool
    issue_code: str | None


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip:
    """Immutable result of a diagnostic-summary representation round trip."""

    status: ComparisonRoundTripDiagnosticSummaryRoundTripStatus
    operation_completed: bool
    semantically_equivalent: bool
    original_summary: ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary | None
    reconstructed_summary: ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary | None
    issue_code: str | None


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTripValidation:
    """Structural validation outcome for a comparison-summary round-trip result."""

    is_valid: bool
    issue_code: str | None


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineComparisonRoundTripResultRoundTripValidation:
    """Structural validation outcome for a P081 result."""

    is_valid: bool
    issue_code: str | None


@dataclass(frozen=True, slots=True)
class ProviderInvocationTracePipelineComparisonRoundTripResultRoundTrip:
    """Immutable result of a P077 result representation round trip."""

    status: ComparisonRoundTripResultRoundTripStatus
    operation_completed: bool
    semantically_equivalent: bool
    original_result: ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip | None
    reconstructed_result: ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip | None
    issue_code: str | None


def process_provider_invocation_trace(
    trace: ProviderInvocationTrace,
) -> ProviderInvocationTracePipelineResult:
    """Process a canonical snapshot through the existing trace contracts.

    The sequence is export, import/schema validation, consistency validation
    against the immutable imported record, then acceptance policy. A failed
    export or import stops later stages and marks them skipped.
    """
    outcomes: list[TracePipelineStageOutcome] = []

    try:
        exported = export_provider_invocation_trace(trace)
    except ProviderInvocationTraceExportError:
        outcomes.append(
            TracePipelineStageOutcome(
                stage=TracePipelineStage.EXPORT,
                status=TracePipelineStageStatus.FAILED,
                issue_codes=("EXPORT_CONTRACT_REJECTED",),
            )
        )
        outcomes.extend(_skipped_stages(TracePipelineStage.IMPORT))
        return ProviderInvocationTracePipelineResult(
            status=TracePipelineStatus.REJECTED,
            export_result=None,
            import_result=None,
            validation_report=None,
            policy_decision=None,
            stage_outcomes=tuple(outcomes),
            rejected_at=TracePipelineStage.EXPORT,
        )
    outcomes.append(
        TracePipelineStageOutcome(
            stage=TracePipelineStage.EXPORT,
            status=TracePipelineStageStatus.SUCCEEDED,
        )
    )

    try:
        imported = import_provider_invocation_trace(exported.to_dict())
    except ProviderInvocationTraceImportError:
        outcomes.append(
            TracePipelineStageOutcome(
                stage=TracePipelineStage.IMPORT,
                status=TracePipelineStageStatus.FAILED,
                issue_codes=("IMPORT_SCHEMA_REJECTED",),
            )
        )
        outcomes.extend(_skipped_stages(TracePipelineStage.VALIDATION))
        return ProviderInvocationTracePipelineResult(
            status=TracePipelineStatus.REJECTED,
            export_result=exported,
            import_result=None,
            validation_report=None,
            policy_decision=None,
            stage_outcomes=tuple(outcomes),
            rejected_at=TracePipelineStage.IMPORT,
        )
    outcomes.append(
        TracePipelineStageOutcome(
            stage=TracePipelineStage.IMPORT,
            status=TracePipelineStageStatus.SUCCEEDED,
        )
    )

    report = validate_provider_invocation_trace(imported)
    validation_issue_codes = tuple(
        finding.code for finding in report.findings
    )
    outcomes.append(
        TracePipelineStageOutcome(
            stage=TracePipelineStage.VALIDATION,
            status=TracePipelineStageStatus.SUCCEEDED,
            issue_codes=validation_issue_codes,
        )
    )

    decision = evaluate_provider_invocation_trace_policy(report)
    if decision.decision is TraceAcceptanceDecision.ACCEPT:
        status = TracePipelineStatus.ACCEPTED
        rejected_at = None
    elif decision.decision is TraceAcceptanceDecision.ACCEPT_WITH_WARNINGS:
        status = TracePipelineStatus.ACCEPTED_WITH_WARNINGS
        rejected_at = None
    else:
        status = TracePipelineStatus.REJECTED
        rejected_at = TracePipelineStage.POLICY
    policy_status = (
        TracePipelineStageStatus.FAILED
        if decision.decision is TraceAcceptanceDecision.REJECT
        else TracePipelineStageStatus.SUCCEEDED
    )
    outcomes.append(
        TracePipelineStageOutcome(
            stage=TracePipelineStage.POLICY,
            status=policy_status,
            issue_codes=decision.reason_codes,
        )
    )

    return ProviderInvocationTracePipelineResult(
        status=status,
        export_result=exported,
        import_result=imported,
        validation_report=report,
        policy_decision=decision,
        stage_outcomes=tuple(outcomes),
        rejected_at=rejected_at,
    )


def summarize_provider_invocation_trace_pipeline(
    result: ProviderInvocationTracePipelineResult,
) -> ProviderInvocationTracePipelineDiagnosticSummary:
    """Summarize public stage outcomes without rerunning any pipeline stage.

    Unsupported or malformed results produce a fail-closed rejected summary
    with a stable issue code and no untrusted fields copied into the report.
    """
    if not _is_well_formed_pipeline_result(result):
        return _invalid_pipeline_summary()

    outcomes = result.stage_outcomes
    stage_issue_codes = tuple(
        (outcome.stage, outcome.issue_codes) for outcome in outcomes
    )
    skipped = any(
        outcome.status is TracePipelineStageStatus.SKIPPED
        for outcome in outcomes
    )
    stage_statuses = {outcome.stage: outcome.status for outcome in outcomes}
    validation_status = stage_statuses[TracePipelineStage.VALIDATION]
    policy_status = stage_statuses[TracePipelineStage.POLICY]
    return ProviderInvocationTracePipelineDiagnosticSummary(
        status=result.status,
        failed_stage=result.rejected_at,
        stage_outcomes=tuple(outcomes),
        stage_issue_codes=stage_issue_codes,
        stages_skipped=skipped,
        validation_completed=(
            validation_status is not TracePipelineStageStatus.SKIPPED
        ),
        policy_evaluation_completed=(
            policy_status is not TracePipelineStageStatus.SKIPPED
        ),
        policy_decision=result.policy_decision,
        provenance_authenticated=result.provenance_authenticated,
        authorizes_provider_execution=result.authorizes_provider_execution,
        independently_verifies_execution=result.independently_verifies_execution,
    )


def serialize_provider_invocation_trace_pipeline_diagnostic_summary(
    summary: ProviderInvocationTracePipelineDiagnosticSummary,
) -> dict[str, object]:
    """Serialize a validated diagnostic summary to fresh JSON-compatible data.

    This function only validates and represents the supplied summary. It does
    not rerun or modify any pipeline stage.
    """
    if not _is_well_formed_diagnostic_summary(summary):
        raise ProviderInvocationTracePipelineSerializationError()

    policy_decision = summary.policy_decision
    serialized_policy_decision: dict[str, object] | None = None
    if policy_decision is not None:
        serialized_policy_decision = {
            "decision": policy_decision.decision.value,
            "accepted": policy_decision.accepted,
            "reason_codes": list(policy_decision.reason_codes),
            "findings": [
                {
                    "code": finding.code,
                    "category": finding.category.value,
                    "severity": finding.severity.value,
                    "field_path": finding.field_path,
                    "sequence": finding.sequence,
                    "message": finding.message,
                }
                for finding in policy_decision.findings
            ],
            "explanation": policy_decision.explanation,
            "establishes_authenticity": (
                policy_decision.establishes_authenticity
            ),
            "authorizes_execution": policy_decision.authorizes_execution,
            "verifies_execution_correctness": (
                policy_decision.verifies_execution_correctness
            ),
            "independently_verifies_execution": (
                policy_decision.independently_verifies_execution
            ),
        }

    return {
        "status": summary.status.value,
        "failed_stage": (
            summary.failed_stage.value if summary.failed_stage is not None else None
        ),
        "stage_outcomes": [
            {
                "stage": outcome.stage.value,
                "status": outcome.status.value,
                "issue_codes": list(outcome.issue_codes),
            }
            for outcome in summary.stage_outcomes
        ],
        "stage_issue_codes": [
            {"stage": stage.value, "issue_codes": list(issue_codes)}
            for stage, issue_codes in summary.stage_issue_codes
        ],
        "stages_skipped": summary.stages_skipped,
        "validation_completed": summary.validation_completed,
        "policy_evaluation_completed": summary.policy_evaluation_completed,
        "policy_decision": serialized_policy_decision,
        "provenance_authenticated": summary.provenance_authenticated,
        "authorizes_provider_execution": summary.authorizes_provider_execution,
        "independently_verifies_execution": (
            summary.independently_verifies_execution
        ),
        "summary_issue_codes": list(summary.summary_issue_codes),
    }


def deserialize_provider_invocation_trace_pipeline_diagnostic_summary(
    value: object,
) -> ProviderInvocationTracePipelineDiagnosticSummary:
    """Reconstruct an immutable diagnostic summary from the supported schema.

    The input is parsed as untrusted data. Deserialization does not authenticate
    the summary or rerun any export, import, validation, or policy stage.
    """
    try:
        source = _require_exact_dict(
            value,
            {
                "status",
                "failed_stage",
                "stage_outcomes",
                "stage_issue_codes",
                "stages_skipped",
                "validation_completed",
                "policy_evaluation_completed",
                "policy_decision",
                "provenance_authenticated",
                "authorizes_provider_execution",
                "independently_verifies_execution",
                "summary_issue_codes",
            },
        )
        status = _require_enum(source["status"], TracePipelineStatus)
        failed_stage_value = source["failed_stage"]
        failed_stage = (
            None
            if failed_stage_value is None
            else _require_enum(failed_stage_value, TracePipelineStage)
        )

        raw_outcomes = _require_list(source["stage_outcomes"])
        outcomes = tuple(
            _deserialize_stage_outcome(item) for item in raw_outcomes
        )
        raw_stage_issue_codes = _require_list(source["stage_issue_codes"])
        stage_issue_codes = tuple(
            _deserialize_stage_issue_codes(item)
            for item in raw_stage_issue_codes
        )
        raw_summary_issue_codes = _require_list(source["summary_issue_codes"])
        summary_issue_codes = tuple(
            _require_string(code) for code in raw_summary_issue_codes
        )
        policy_value = source["policy_decision"]
        policy_decision = (
            None
            if policy_value is None
            else _deserialize_policy_decision(policy_value)
        )

        summary = ProviderInvocationTracePipelineDiagnosticSummary(
            status=status,
            failed_stage=failed_stage,
            stage_outcomes=outcomes,
            stage_issue_codes=stage_issue_codes,
            stages_skipped=_require_bool(source["stages_skipped"]),
            validation_completed=_require_bool(source["validation_completed"]),
            policy_evaluation_completed=_require_bool(
                source["policy_evaluation_completed"]
            ),
            policy_decision=policy_decision,
            provenance_authenticated=_require_bool(
                source["provenance_authenticated"]
            ),
            authorizes_provider_execution=_require_bool(
                source["authorizes_provider_execution"]
            ),
            independently_verifies_execution=_require_bool(
                source["independently_verifies_execution"]
            ),
            summary_issue_codes=summary_issue_codes,
        )
    except (KeyError, TypeError, ValueError):
        raise ProviderInvocationTracePipelineSerializationError() from None

    if not _is_well_formed_diagnostic_summary(summary):
        raise ProviderInvocationTracePipelineSerializationError()
    return summary


def round_trip_provider_invocation_trace_pipeline_diagnostic_summary(
    summary: ProviderInvocationTracePipelineDiagnosticSummary,
) -> ProviderInvocationTracePipelineDiagnosticSummaryRoundTrip:
    """Round-trip a summary through the canonical serializer and deserializer.

    No trace-processing stage is executed. Only expected serialization-contract
    failures are converted to stable issue codes; unexpected errors propagate.
    """
    try:
        serialized = (
            serialize_provider_invocation_trace_pipeline_diagnostic_summary(
                summary
            )
        )
    except ProviderInvocationTracePipelineSerializationError:
        return ProviderInvocationTracePipelineDiagnosticSummaryRoundTrip(
            status=DiagnosticSummaryRoundTripStatus.FAILED,
            original_summary=None,
            reconstructed_summary=None,
            semantic_consistency_established=False,
            issue_code="SUMMARY_SERIALIZATION_FAILED",
        )

    try:
        reconstructed = (
            deserialize_provider_invocation_trace_pipeline_diagnostic_summary(
                serialized
            )
        )
    except ProviderInvocationTracePipelineSerializationError:
        return ProviderInvocationTracePipelineDiagnosticSummaryRoundTrip(
            status=DiagnosticSummaryRoundTripStatus.FAILED,
            original_summary=summary,
            reconstructed_summary=None,
            semantic_consistency_established=False,
            issue_code="SUMMARY_DESERIALIZATION_FAILED",
        )

    if not _summaries_are_semantically_equal(summary, reconstructed):
        return ProviderInvocationTracePipelineDiagnosticSummaryRoundTrip(
            status=DiagnosticSummaryRoundTripStatus.INCONSISTENT,
            original_summary=summary,
            reconstructed_summary=reconstructed,
            semantic_consistency_established=False,
            issue_code="SUMMARY_SEMANTIC_MISMATCH",
        )

    return ProviderInvocationTracePipelineDiagnosticSummaryRoundTrip(
        status=DiagnosticSummaryRoundTripStatus.CONSISTENT,
        original_summary=summary,
        reconstructed_summary=reconstructed,
        semantic_consistency_established=True,
        issue_code=None,
    )


def compare_provider_invocation_trace_pipeline_diagnostic_summaries(
    left: ProviderInvocationTracePipelineDiagnosticSummary,
    right: ProviderInvocationTracePipelineDiagnosticSummary,
) -> ProviderInvocationTracePipelineDiagnosticSummaryComparison:
    """Compare complete canonical diagnostic meaning without rerunning stages."""
    if not _is_well_formed_diagnostic_summary(left):
        return ProviderInvocationTracePipelineDiagnosticSummaryComparison(
            status=DiagnosticSummaryComparisonStatus.INCOMPLETE,
            comparison_completed=False,
            semantically_equivalent=False,
            differing_fields=(),
            issue_code="LEFT_SUMMARY_INVALID",
        )
    if not _is_well_formed_diagnostic_summary(right):
        return ProviderInvocationTracePipelineDiagnosticSummaryComparison(
            status=DiagnosticSummaryComparisonStatus.INCOMPLETE,
            comparison_completed=False,
            semantically_equivalent=False,
            differing_fields=(),
            issue_code="RIGHT_SUMMARY_INVALID",
        )

    differences: list[str] = []
    for field_name in (
        "status",
        "failed_stage",
        "stage_outcomes",
        "stage_issue_codes",
        "summary_issue_codes",
        "stages_skipped",
        "validation_completed",
        "policy_evaluation_completed",
        "policy_decision",
        "provenance_authenticated",
        "authorizes_provider_execution",
        "independently_verifies_execution",
    ):
        if field_name == "stage_outcomes":
            _compare_stage_outcomes(left.stage_outcomes, right.stage_outcomes, differences)
        elif field_name == "stage_issue_codes":
            _compare_stage_issue_codes(
                left.stage_issue_codes, right.stage_issue_codes, differences
            )
        elif field_name == "policy_decision":
            _compare_policy_decisions(
                left.policy_decision, right.policy_decision, differences
            )
        elif getattr(left, field_name) != getattr(right, field_name):
            differences.append(field_name)

    differing_fields = tuple(differences)
    return ProviderInvocationTracePipelineDiagnosticSummaryComparison(
        status=DiagnosticSummaryComparisonStatus.COMPLETED,
        comparison_completed=True,
        semantically_equivalent=not differing_fields,
        differing_fields=differing_fields,
        issue_code=None,
    )


def serialize_provider_invocation_trace_pipeline_diagnostic_summary_comparison(
    comparison: ProviderInvocationTracePipelineDiagnosticSummaryComparison,
) -> dict[str, object]:
    """Serialize a validated comparison result to fresh plain data."""
    if not _is_well_formed_comparison_result(comparison):
        raise ProviderInvocationTracePipelineComparisonSerializationError()
    return {
        "status": comparison.status.value,
        "comparison_completed": comparison.comparison_completed,
        "semantically_equivalent": comparison.semantically_equivalent,
        "differing_fields": list(comparison.differing_fields),
        "issue_code": comparison.issue_code,
    }


def deserialize_provider_invocation_trace_pipeline_diagnostic_summary_comparison(
    value: object,
) -> ProviderInvocationTracePipelineDiagnosticSummaryComparison:
    """Reconstruct a canonical comparison result from its exact serialized form."""
    try:
        source = _require_exact_dict(
            value,
            {
                "status",
                "comparison_completed",
                "semantically_equivalent",
                "differing_fields",
                "issue_code",
            },
        )
        status_value = _require_string(source["status"])
        status = DiagnosticSummaryComparisonStatus(status_value)
        comparison_completed = _require_bool(source["comparison_completed"])
        semantically_equivalent = _require_bool(
            source["semantically_equivalent"]
        )
        differing_fields = tuple(
            _require_string(field)
            for field in _require_list(source["differing_fields"])
        )
        issue_code_value = source["issue_code"]
        issue_code = (
            None
            if issue_code_value is None
            else _require_string(issue_code_value)
        )
        comparison = ProviderInvocationTracePipelineDiagnosticSummaryComparison(
            status=status,
            comparison_completed=comparison_completed,
            semantically_equivalent=semantically_equivalent,
            differing_fields=differing_fields,
            issue_code=issue_code,
        )
    except (KeyError, TypeError, ValueError):
        raise ProviderInvocationTracePipelineComparisonSerializationError() from None

    if not _is_well_formed_comparison_result(comparison):
        raise ProviderInvocationTracePipelineComparisonSerializationError()
    return comparison


def round_trip_provider_invocation_trace_pipeline_diagnostic_summary_comparison(
    comparison: ProviderInvocationTracePipelineDiagnosticSummaryComparison,
) -> ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTrip:
    """Round-trip a comparison result through its canonical public codecs."""
    try:
        serialized = (
            serialize_provider_invocation_trace_pipeline_diagnostic_summary_comparison(
                comparison
            )
        )
    except ProviderInvocationTracePipelineComparisonSerializationError:
        return ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTrip(
            status=DiagnosticSummaryComparisonRoundTripStatus.FAILED,
            operation_completed=False,
            semantic_consistency_established=False,
            original_comparison=None,
            reconstructed_comparison=None,
            issue_code="COMPARISON_SERIALIZATION_FAILED",
        )

    try:
        reconstructed = (
            deserialize_provider_invocation_trace_pipeline_diagnostic_summary_comparison(
                serialized
            )
        )
    except ProviderInvocationTracePipelineComparisonSerializationError:
        return ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTrip(
            status=DiagnosticSummaryComparisonRoundTripStatus.FAILED,
            operation_completed=False,
            semantic_consistency_established=False,
            original_comparison=comparison,
            reconstructed_comparison=None,
            issue_code="COMPARISON_DESERIALIZATION_FAILED",
        )

    if not _comparison_results_are_semantically_equal(comparison, reconstructed):
        return ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTrip(
            status=DiagnosticSummaryComparisonRoundTripStatus.INCONSISTENT,
            operation_completed=True,
            semantic_consistency_established=False,
            original_comparison=comparison,
            reconstructed_comparison=reconstructed,
            issue_code="COMPARISON_SEMANTIC_MISMATCH",
        )

    return ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTrip(
        status=DiagnosticSummaryComparisonRoundTripStatus.CONSISTENT,
        operation_completed=True,
        semantic_consistency_established=True,
        original_comparison=comparison,
        reconstructed_comparison=reconstructed,
        issue_code=None,
    )


def summarize_provider_invocation_trace_pipeline_diagnostic_summary_comparison_round_trip(
    result: ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTrip,
) -> ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary:
    """Summarize a supplied comparison round trip without reprocessing it."""
    if not _is_well_formed_comparison_round_trip(result):
        return (
            ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary(
                diagnostic_summary_produced=False,
                status=DiagnosticSummaryComparisonRoundTripStatus.FAILED,
                operation_completed=False,
                semantic_consistency_established=False,
                issue_code="COMPARISON_ROUND_TRIP_RESULT_MALFORMED",
            )
        )
    return (
        ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary(
            diagnostic_summary_produced=True,
            status=result.status,
            operation_completed=result.operation_completed,
            semantic_consistency_established=(
                result.semantic_consistency_established
            ),
            issue_code=result.issue_code,
        )
    )


def serialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary(
    summary: ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary,
) -> dict[str, object]:
    """Serialize a valid comparison round-trip diagnostic summary to plain data."""
    if not _is_well_formed_comparison_round_trip_diagnostic_summary(summary):
        raise (
            ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummarySerializationError()
        )
    return {
        "diagnostic_summary_produced": summary.diagnostic_summary_produced,
        "status": summary.status.value,
        "operation_completed": summary.operation_completed,
        "semantic_consistency_established": (
            summary.semantic_consistency_established
        ),
        "issue_code": summary.issue_code,
    }


def deserialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary(
    value: object,
) -> ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary:
    """Reconstruct a diagnostic summary from the exact P075 dictionary schema."""
    try:
        source = _require_exact_dict(
            value,
            {
                "diagnostic_summary_produced",
                "status",
                "operation_completed",
                "semantic_consistency_established",
                "issue_code",
            },
        )
        issue_code_value = source["issue_code"]
        summary = (
            ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary(
                diagnostic_summary_produced=_require_bool(
                    source["diagnostic_summary_produced"]
                ),
                status=_require_enum(
                    source["status"], DiagnosticSummaryComparisonRoundTripStatus
                ),
                operation_completed=_require_bool(source["operation_completed"]),
                semantic_consistency_established=_require_bool(
                    source["semantic_consistency_established"]
                ),
                issue_code=(
                    None
                    if issue_code_value is None
                    else _require_string(issue_code_value)
                ),
            )
        )
    except (KeyError, TypeError, ValueError):
        raise (
            ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummarySerializationError()
        ) from None

    if not _is_well_formed_comparison_round_trip_diagnostic_summary(summary):
        raise (
            ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummarySerializationError()
        )
    return summary


def round_trip_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary(
    summary: ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary,
) -> ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip:
    """Round-trip a P074 summary through its canonical P075/P076 codecs only."""
    try:
        serialized = (
            serialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary(
                summary
            )
        )
    except (
        ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummarySerializationError
    ):
        return (
            ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip(
                status=ComparisonRoundTripDiagnosticSummaryRoundTripStatus.SERIALIZATION_FAILED,
                operation_completed=False,
                semantically_equivalent=False,
                original_summary=None,
                reconstructed_summary=None,
                issue_code="COMPARISON_ROUND_TRIP_DIAGNOSTIC_SUMMARY_SERIALIZATION_FAILED",
            )
        )

    try:
        reconstructed = (
            deserialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary(
                serialized
            )
        )
    except (
        ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummarySerializationError
    ):
        return (
            ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip(
                status=ComparisonRoundTripDiagnosticSummaryRoundTripStatus.DESERIALIZATION_FAILED,
                operation_completed=False,
                semantically_equivalent=False,
                original_summary=summary,
                reconstructed_summary=None,
                issue_code="COMPARISON_ROUND_TRIP_DIAGNOSTIC_SUMMARY_DESERIALIZATION_FAILED",
            )
        )

    if not _comparison_round_trip_diagnostic_summaries_equal(
        summary, reconstructed
    ):
        return (
            ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip(
                status=ComparisonRoundTripDiagnosticSummaryRoundTripStatus.SEMANTIC_MISMATCH,
                operation_completed=True,
                semantically_equivalent=False,
                original_summary=summary,
                reconstructed_summary=reconstructed,
                issue_code="COMPARISON_ROUND_TRIP_DIAGNOSTIC_SUMMARY_SEMANTIC_MISMATCH",
            )
        )

    return (
        ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip(
            status=ComparisonRoundTripDiagnosticSummaryRoundTripStatus.CONSISTENT,
            operation_completed=True,
            semantically_equivalent=True,
            original_summary=summary,
            reconstructed_summary=reconstructed,
            issue_code=None,
        )
    )


def validate_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
    result: object,
) -> ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTripValidation:
    """Validate a P077 result's canonical fields without rerunning its operation."""
    is_valid = _is_well_formed_comparison_diagnostic_summary_round_trip(result)
    return (
        ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTripValidation(
            is_valid=is_valid,
            issue_code=(
                None
                if is_valid
                else "COMPARISON_ROUND_TRIP_RESULT_MALFORMED"
            ),
        )
    )


def serialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
    result: ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip,
) -> dict[str, object]:
    """Serialize a P077 result after canonical P078 contract validation."""
    validation = (
        validate_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
            result
        )
    )
    if not validation.is_valid:
        raise ProviderInvocationTracePipelineComparisonRoundTripResultSerializationError()

    try:
        original_summary = (
            None
            if result.original_summary is None
            else serialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary(
                result.original_summary
            )
        )
        reconstructed_summary = (
            None
            if result.reconstructed_summary is None
            else serialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary(
                result.reconstructed_summary
            )
        )
    except (
        ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummarySerializationError
    ):
        raise ProviderInvocationTracePipelineComparisonRoundTripResultSerializationError() from None

    return {
        "status": result.status.value,
        "operation_completed": result.operation_completed,
        "semantically_equivalent": result.semantically_equivalent,
        "original_summary": original_summary,
        "reconstructed_summary": reconstructed_summary,
        "issue_code": result.issue_code,
    }


def deserialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
    value: object,
) -> ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip:
    """Reconstruct and validate a P079 serialized P077 result."""
    try:
        source = _require_exact_dict(
            value,
            {
                "status",
                "operation_completed",
                "semantically_equivalent",
                "original_summary",
                "reconstructed_summary",
                "issue_code",
            },
        )
        original_value = source["original_summary"]
        reconstructed_value = source["reconstructed_summary"]
        issue_code_value = source["issue_code"]
        result = (
            ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip(
                status=_require_enum(
                    source["status"],
                    ComparisonRoundTripDiagnosticSummaryRoundTripStatus,
                ),
                operation_completed=_require_bool(
                    source["operation_completed"]
                ),
                semantically_equivalent=_require_bool(
                    source["semantically_equivalent"]
                ),
                original_summary=(
                    None
                    if original_value is None
                    else deserialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary(
                        original_value
                    )
                ),
                reconstructed_summary=(
                    None
                    if reconstructed_value is None
                    else deserialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary(
                        reconstructed_value
                    )
                ),
                issue_code=(
                    None
                    if issue_code_value is None
                    else _require_string(issue_code_value)
                ),
            )
        )
    except (
        KeyError,
        TypeError,
        ValueError,
        ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummarySerializationError,
    ):
        raise (
            ProviderInvocationTracePipelineComparisonRoundTripResultDeserializationError()
        ) from None

    validation = (
        validate_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
            result
        )
    )
    if not validation.is_valid:
        raise (
            ProviderInvocationTracePipelineComparisonRoundTripResultDeserializationError()
        )
    return result


def round_trip_provider_invocation_trace_pipeline_comparison_round_trip_result(
    result: ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip,
) -> ProviderInvocationTracePipelineComparisonRoundTripResultRoundTrip:
    """Round-trip a P077 result through its canonical P079/P080 codecs only."""
    try:
        serialized = (
            serialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
                result
            )
        )
    except ProviderInvocationTracePipelineComparisonRoundTripResultSerializationError:
        return ProviderInvocationTracePipelineComparisonRoundTripResultRoundTrip(
            status=ComparisonRoundTripResultRoundTripStatus.SERIALIZATION_FAILED,
            operation_completed=False,
            semantically_equivalent=False,
            original_result=None,
            reconstructed_result=None,
            issue_code="COMPARISON_ROUND_TRIP_RESULT_SERIALIZATION_FAILED",
        )

    try:
        reconstructed = (
            deserialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
                serialized
            )
        )
    except (
        ProviderInvocationTracePipelineComparisonRoundTripResultDeserializationError
    ):
        return ProviderInvocationTracePipelineComparisonRoundTripResultRoundTrip(
            status=ComparisonRoundTripResultRoundTripStatus.DESERIALIZATION_FAILED,
            operation_completed=False,
            semantically_equivalent=False,
            original_result=result,
            reconstructed_result=None,
            issue_code="COMPARISON_ROUND_TRIP_RESULT_DESERIALIZATION_FAILED",
        )

    if not _comparison_round_trip_results_are_semantically_equal(
        result, reconstructed
    ):
        return ProviderInvocationTracePipelineComparisonRoundTripResultRoundTrip(
            status=ComparisonRoundTripResultRoundTripStatus.SEMANTIC_MISMATCH,
            operation_completed=True,
            semantically_equivalent=False,
            original_result=result,
            reconstructed_result=reconstructed,
            issue_code="COMPARISON_ROUND_TRIP_RESULT_SEMANTIC_MISMATCH",
        )

    return ProviderInvocationTracePipelineComparisonRoundTripResultRoundTrip(
        status=ComparisonRoundTripResultRoundTripStatus.CONSISTENT,
        operation_completed=True,
        semantically_equivalent=True,
        original_result=result,
        reconstructed_result=reconstructed,
        issue_code=None,
    )


def _comparison_round_trip_results_are_semantically_equal(
    original: ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip,
    reconstructed: ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip,
) -> bool:
    if (
        original.status is not reconstructed.status
        or original.operation_completed is not reconstructed.operation_completed
        or original.semantically_equivalent
        is not reconstructed.semantically_equivalent
        or original.issue_code != reconstructed.issue_code
    ):
        return False

    original_summary = original.original_summary
    reconstructed_summary = reconstructed.original_summary
    if original_summary is None or reconstructed_summary is None:
        if original_summary is not reconstructed_summary:
            return False
    elif not _comparison_round_trip_diagnostic_summaries_equal(
        original_summary, reconstructed_summary
    ):
        return False

    original_summary = original.reconstructed_summary
    reconstructed_summary = reconstructed.reconstructed_summary
    if original_summary is None or reconstructed_summary is None:
        return original_summary is reconstructed_summary
    return _comparison_round_trip_diagnostic_summaries_equal(
        original_summary, reconstructed_summary
    )


def validate_provider_invocation_trace_pipeline_comparison_round_trip_result_round_trip(
    result: object,
) -> ProviderInvocationTracePipelineComparisonRoundTripResultRoundTripValidation:
    """Validate a P081 result without rerunning its representation round trip."""
    is_valid = _is_well_formed_comparison_round_trip_result_round_trip(result)
    return ProviderInvocationTracePipelineComparisonRoundTripResultRoundTripValidation(
        is_valid=is_valid,
        issue_code=(
            None if is_valid else "COMPARISON_ROUND_TRIP_RESULT_MALFORMED"
        ),
    )


def serialize_provider_invocation_trace_pipeline_comparison_round_trip_result_round_trip(
    result: ProviderInvocationTracePipelineComparisonRoundTripResultRoundTrip,
) -> dict[str, object]:
    """Serialize a P081 result after validating its canonical contract."""
    validation = (
        validate_provider_invocation_trace_pipeline_comparison_round_trip_result_round_trip(
            result
        )
    )
    if not validation.is_valid:
        raise ProviderInvocationTracePipelineComparisonRoundTripResultSerializationError()

    try:
        original_result = (
            None
            if result.original_result is None
            else serialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
                result.original_result
            )
        )
        reconstructed_result = (
            None
            if result.reconstructed_result is None
            else serialize_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
                result.reconstructed_result
            )
        )
    except (
        ProviderInvocationTracePipelineComparisonRoundTripResultSerializationError
    ):
        raise ProviderInvocationTracePipelineComparisonRoundTripResultSerializationError() from None

    return {
        "status": result.status.value,
        "operation_completed": result.operation_completed,
        "semantically_equivalent": result.semantically_equivalent,
        "original_result": original_result,
        "reconstructed_result": reconstructed_result,
        "issue_code": result.issue_code,
    }


def _is_well_formed_comparison_round_trip_result_round_trip(
    value: object,
) -> bool:
    if (
        type(value)
        is not ProviderInvocationTracePipelineComparisonRoundTripResultRoundTrip
        or type(value.status) is not ComparisonRoundTripResultRoundTripStatus
        or type(value.operation_completed) is not bool
        or type(value.semantically_equivalent) is not bool
        or (
            value.issue_code is not None
            and not _is_stable_code(value.issue_code)
        )
    ):
        return False

    original = value.original_result
    reconstructed = value.reconstructed_result
    if original is not None:
        original_validation = (
            validate_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
                original
            )
        )
        if not original_validation.is_valid:
            return False
    if reconstructed is not None:
        reconstructed_validation = (
            validate_provider_invocation_trace_pipeline_comparison_round_trip_diagnostic_summary_round_trip(
                reconstructed
            )
        )
        if not reconstructed_validation.is_valid:
            return False

    if value.status is ComparisonRoundTripResultRoundTripStatus.CONSISTENT:
        return (
            value.operation_completed
            and value.semantically_equivalent
            and value.issue_code is None
            and original is not None
            and reconstructed is not None
            and _comparison_round_trip_results_are_semantically_equal(
                original, reconstructed
            )
        )
    if (
        value.status
        is ComparisonRoundTripResultRoundTripStatus.SERIALIZATION_FAILED
    ):
        return (
            not value.operation_completed
            and not value.semantically_equivalent
            and value.issue_code
            == "COMPARISON_ROUND_TRIP_RESULT_SERIALIZATION_FAILED"
            and original is None
            and reconstructed is None
        )
    if (
        value.status
        is ComparisonRoundTripResultRoundTripStatus.DESERIALIZATION_FAILED
    ):
        return (
            not value.operation_completed
            and not value.semantically_equivalent
            and value.issue_code
            == "COMPARISON_ROUND_TRIP_RESULT_DESERIALIZATION_FAILED"
            and original is not None
            and reconstructed is None
        )
    if (
        value.status
        is ComparisonRoundTripResultRoundTripStatus.SEMANTIC_MISMATCH
    ):
        return (
            value.operation_completed
            and not value.semantically_equivalent
            and value.issue_code
            == "COMPARISON_ROUND_TRIP_RESULT_SEMANTIC_MISMATCH"
            and original is not None
            and reconstructed is not None
            and not _comparison_round_trip_results_are_semantically_equal(
                original, reconstructed
            )
        )
    return False


def _is_well_formed_comparison_diagnostic_summary_round_trip(
    value: object,
) -> bool:
    if (
        type(value)
        is not ProviderInvocationTracePipelineComparisonRoundTripDiagnosticSummaryRoundTrip
    ):
        return False
    if (
        type(value.status) is not ComparisonRoundTripDiagnosticSummaryRoundTripStatus
        or type(value.operation_completed) is not bool
        or type(value.semantically_equivalent) is not bool
        or (
            value.issue_code is not None
            and not _is_stable_code(value.issue_code)
        )
    ):
        return False

    original = value.original_summary
    reconstructed = value.reconstructed_summary
    if original is not None and not (
        _is_well_formed_comparison_round_trip_diagnostic_summary(original)
    ):
        return False
    if reconstructed is not None and not (
        _is_well_formed_comparison_round_trip_diagnostic_summary(reconstructed)
    ):
        return False

    if (
        value.status
        is ComparisonRoundTripDiagnosticSummaryRoundTripStatus.CONSISTENT
    ):
        return (
            value.operation_completed
            and value.semantically_equivalent
            and value.issue_code is None
            and original is not None
            and reconstructed is not None
            and _comparison_round_trip_diagnostic_summaries_equal(
                original, reconstructed
            )
        )
    if (
        value.status
        is ComparisonRoundTripDiagnosticSummaryRoundTripStatus.SERIALIZATION_FAILED
    ):
        return (
            not value.operation_completed
            and not value.semantically_equivalent
            and value.issue_code
            == "COMPARISON_ROUND_TRIP_DIAGNOSTIC_SUMMARY_SERIALIZATION_FAILED"
            and original is None
            and reconstructed is None
        )
    if (
        value.status
        is ComparisonRoundTripDiagnosticSummaryRoundTripStatus.DESERIALIZATION_FAILED
    ):
        return (
            not value.operation_completed
            and not value.semantically_equivalent
            and value.issue_code
            == "COMPARISON_ROUND_TRIP_DIAGNOSTIC_SUMMARY_DESERIALIZATION_FAILED"
            and original is not None
            and reconstructed is None
        )
    if (
        value.status
        is ComparisonRoundTripDiagnosticSummaryRoundTripStatus.SEMANTIC_MISMATCH
    ):
        return (
            value.operation_completed
            and not value.semantically_equivalent
            and value.issue_code
            == "COMPARISON_ROUND_TRIP_DIAGNOSTIC_SUMMARY_SEMANTIC_MISMATCH"
            and original is not None
            and reconstructed is not None
            and not _comparison_round_trip_diagnostic_summaries_equal(
                original, reconstructed
            )
        )
    return False


def _comparison_round_trip_diagnostic_summaries_equal(
    left: object,
    right: object,
) -> bool:
    if not _is_well_formed_comparison_round_trip_diagnostic_summary(
        left
    ) or not _is_well_formed_comparison_round_trip_diagnostic_summary(right):
        return False
    return (
        left.diagnostic_summary_produced
        is right.diagnostic_summary_produced
        and left.status is right.status
        and left.operation_completed is right.operation_completed
        and left.semantic_consistency_established
        is right.semantic_consistency_established
        and left.issue_code == right.issue_code
    )


def _is_well_formed_comparison_round_trip_diagnostic_summary(
    value: object,
) -> bool:
    if (
        type(value)
        is not ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTripDiagnosticSummary
    ):
        return False
    if (
        type(value.diagnostic_summary_produced) is not bool
        or type(value.status) is not DiagnosticSummaryComparisonRoundTripStatus
        or type(value.operation_completed) is not bool
        or type(value.semantic_consistency_established) is not bool
        or (
            value.issue_code is not None
            and not _is_stable_code(value.issue_code)
        )
    ):
        return False

    if not value.diagnostic_summary_produced:
        return (
            value.status is DiagnosticSummaryComparisonRoundTripStatus.FAILED
            and not value.operation_completed
            and not value.semantic_consistency_established
            and value.issue_code == "COMPARISON_ROUND_TRIP_RESULT_MALFORMED"
        )
    if value.status is DiagnosticSummaryComparisonRoundTripStatus.CONSISTENT:
        return (
            value.operation_completed
            and value.semantic_consistency_established
            and value.issue_code is None
        )
    if value.status is DiagnosticSummaryComparisonRoundTripStatus.INCONSISTENT:
        return (
            value.operation_completed
            and not value.semantic_consistency_established
            and value.issue_code == "COMPARISON_SEMANTIC_MISMATCH"
        )
    if value.status is DiagnosticSummaryComparisonRoundTripStatus.FAILED:
        return (
            not value.operation_completed
            and not value.semantic_consistency_established
            and value.issue_code
            in (
                "COMPARISON_SERIALIZATION_FAILED",
                "COMPARISON_DESERIALIZATION_FAILED",
            )
        )
    return False


def _is_well_formed_comparison_round_trip(value: object) -> bool:
    if type(value) is not ProviderInvocationTracePipelineDiagnosticSummaryComparisonRoundTrip:
        return False
    if (
        type(value.status) is not DiagnosticSummaryComparisonRoundTripStatus
        or type(value.operation_completed) is not bool
        or type(value.semantic_consistency_established) is not bool
        or (
            value.issue_code is not None
            and type(value.issue_code) is not str
        )
    ):
        return False

    original = value.original_comparison
    reconstructed = value.reconstructed_comparison
    if original is not None and not _is_well_formed_comparison_result(original):
        return False
    if reconstructed is not None and not _is_well_formed_comparison_result(
        reconstructed
    ):
        return False

    if value.status is DiagnosticSummaryComparisonRoundTripStatus.CONSISTENT:
        return (
            value.operation_completed
            and value.semantic_consistency_established
            and value.issue_code is None
            and original is not None
            and reconstructed is not None
            and _comparison_results_are_semantically_equal(
                original, reconstructed
            )
        )
    if value.status is DiagnosticSummaryComparisonRoundTripStatus.INCONSISTENT:
        return (
            value.operation_completed
            and not value.semantic_consistency_established
            and value.issue_code == "COMPARISON_SEMANTIC_MISMATCH"
            and original is not None
            and reconstructed is not None
            and not _comparison_results_are_semantically_equal(
                original, reconstructed
            )
        )
    if value.status is DiagnosticSummaryComparisonRoundTripStatus.FAILED:
        if (
            value.operation_completed
            or value.semantic_consistency_established
            or reconstructed is not None
        ):
            return False
        if value.issue_code == "COMPARISON_SERIALIZATION_FAILED":
            return original is None
        if value.issue_code == "COMPARISON_DESERIALIZATION_FAILED":
            return original is not None
        return False
    return False


def _comparison_results_are_semantically_equal(
    original: object,
    reconstructed: object,
) -> bool:
    if not _is_well_formed_comparison_result(original) or not (
        _is_well_formed_comparison_result(reconstructed)
    ):
        return False
    return (
        original.status is reconstructed.status
        and original.comparison_completed is reconstructed.comparison_completed
        and original.semantically_equivalent
        is reconstructed.semantically_equivalent
        and original.differing_fields == reconstructed.differing_fields
        and original.issue_code == reconstructed.issue_code
    )


def _is_well_formed_comparison_result(value: object) -> bool:
    if type(value) is not ProviderInvocationTracePipelineDiagnosticSummaryComparison:
        return False
    if (
        type(value.status) is not DiagnosticSummaryComparisonStatus
        or type(value.comparison_completed) is not bool
        or type(value.semantically_equivalent) is not bool
        or type(value.differing_fields) is not tuple
        or any(
            not _is_canonical_difference_field(field)
            for field in value.differing_fields
        )
    ):
        return False
    if len(set(value.differing_fields)) != len(value.differing_fields):
        return False

    if value.status is DiagnosticSummaryComparisonStatus.COMPLETED:
        return (
            value.comparison_completed
            and value.issue_code is None
            and value.semantically_equivalent is (not value.differing_fields)
            and value.differing_fields
            == tuple(sorted(value.differing_fields, key=_difference_field_sort_key))
        )
    return (
        value.status is DiagnosticSummaryComparisonStatus.INCOMPLETE
        and not value.comparison_completed
        and not value.semantically_equivalent
        and not value.differing_fields
        and type(value.issue_code) is str
        and value.issue_code
        in ("LEFT_SUMMARY_INVALID", "RIGHT_SUMMARY_INVALID")
    )


def _is_canonical_difference_field(value: object) -> bool:
    if type(value) is not str:
        return False
    simple_fields = {
        "status",
        "failed_stage",
        "summary_issue_codes",
        "stages_skipped",
        "validation_completed",
        "policy_evaluation_completed",
        "provenance_authenticated",
        "authorizes_provider_execution",
        "independently_verifies_execution",
        "stage_outcomes",
        "stage_issue_codes",
        "policy_decision",
    }
    if value in simple_fields:
        return True

    match = re.fullmatch(r"stage_outcomes\[([0-9]+)\]\.(stage|status|issue_codes)", value)
    if match is not None:
        return True
    match = re.fullmatch(
        r"stage_issue_codes\[([0-9]+)\]\.(stage|issue_codes)", value
    )
    if match is not None:
        return True
    policy_fields = {
        "decision",
        "accepted",
        "reason_codes",
        "explanation",
        "establishes_authenticity",
        "authorizes_execution",
        "verifies_execution_correctness",
        "independently_verifies_execution",
    }
    if value.startswith("policy_decision.") and value[len("policy_decision.") :] in policy_fields:
        return True
    return bool(
        re.fullmatch(
            r"policy_decision\.findings\[[0-9]+\]\."
            r"(code|category|severity|field_path|sequence|message)",
            value,
        )
    )


def _difference_field_sort_key(value: str) -> tuple[int, int, int, int]:
    ordered_fields = (
        "status",
        "failed_stage",
        "stage_outcomes",
        "stage_issue_codes",
        "summary_issue_codes",
        "stages_skipped",
        "validation_completed",
        "policy_evaluation_completed",
        "policy_decision",
        "provenance_authenticated",
        "authorizes_provider_execution",
        "independently_verifies_execution",
    )
    for field_order, field_name in enumerate(ordered_fields):
        if value == field_name:
            return (field_order, -1, -1, -1)

    for field_order, collection_name in (
        (2, "stage_outcomes"),
        (3, "stage_issue_codes"),
    ):
        match = re.fullmatch(
            rf"{collection_name}\[([0-9]+)\]\.(stage|status|issue_codes)", value
        )
        if match is not None:
            nested_order = {
                "stage": 0,
                "status": 1,
                "issue_codes": 2,
            }[match.group(2)]
            return (field_order, int(match.group(1)), nested_order, -1)

    if value == "policy_decision":
        return (8, -1, -1, -1)
    if value.startswith("policy_decision."):
        nested_name = value[len("policy_decision.") :]
        policy_fields = (
            "decision",
            "accepted",
            "reason_codes",
            "explanation",
            "establishes_authenticity",
            "authorizes_execution",
            "verifies_execution_correctness",
            "independently_verifies_execution",
        )
        if nested_name in policy_fields:
            return (8, 0, policy_fields.index(nested_name), -1)
        if nested_name == "findings":
            return (8, 1, -1, -1)
        match = re.fullmatch(
            r"findings\[([0-9]+)\]\."
            r"(code|category|severity|field_path|sequence|message)",
            nested_name,
        )
        if match is not None:
            finding_fields = (
                "code",
                "category",
                "severity",
                "field_path",
                "sequence",
                "message",
            )
            finding_field_order = finding_fields.index(match.group(2))
            return (8, 2, int(match.group(1)), finding_field_order)
    return (len(ordered_fields), -1, -1, -1)


def _compare_stage_outcomes(
    left: tuple[TracePipelineStageOutcome, ...],
    right: tuple[TracePipelineStageOutcome, ...],
    differences: list[str],
) -> None:
    if len(left) != len(right):
        differences.append("stage_outcomes")
    for index in range(min(len(left), len(right))):
        left_item = left[index]
        right_item = right[index]
        for field_name in ("stage", "status", "issue_codes"):
            if getattr(left_item, field_name) != getattr(right_item, field_name):
                differences.append(f"stage_outcomes[{index}].{field_name}")


def _compare_stage_issue_codes(
    left: tuple[tuple[TracePipelineStage, tuple[str, ...]], ...],
    right: tuple[tuple[TracePipelineStage, tuple[str, ...]], ...],
    differences: list[str],
) -> None:
    if len(left) != len(right):
        differences.append("stage_issue_codes")
    for index in range(min(len(left), len(right))):
        if left[index][0] != right[index][0]:
            differences.append(f"stage_issue_codes[{index}].stage")
        if left[index][1] != right[index][1]:
            differences.append(f"stage_issue_codes[{index}].issue_codes")


def _compare_policy_decisions(
    left: ProviderInvocationTracePolicyDecision | None,
    right: ProviderInvocationTracePolicyDecision | None,
    differences: list[str],
) -> None:
    if left is None or right is None:
        if left is not right:
            differences.append("policy_decision")
        return
    for field_name in (
        "decision",
        "accepted",
        "reason_codes",
        "explanation",
        "establishes_authenticity",
        "authorizes_execution",
        "verifies_execution_correctness",
        "independently_verifies_execution",
    ):
        if getattr(left, field_name) != getattr(right, field_name):
            differences.append(f"policy_decision.{field_name}")
    if len(left.findings) != len(right.findings):
        differences.append("policy_decision.findings")
    for index in range(min(len(left.findings), len(right.findings))):
        left_finding = left.findings[index]
        right_finding = right.findings[index]
        for field_name in (
            "code",
            "category",
            "severity",
            "field_path",
            "sequence",
            "message",
        ):
            if getattr(left_finding, field_name) != getattr(right_finding, field_name):
                differences.append(
                    f"policy_decision.findings[{index}].{field_name}"
                )


def _summaries_are_semantically_equal(
    original: ProviderInvocationTracePipelineDiagnosticSummary,
    reconstructed: ProviderInvocationTracePipelineDiagnosticSummary,
) -> bool:
    if (
        original.status is not reconstructed.status
        or original.failed_stage is not reconstructed.failed_stage
        or original.stages_skipped is not reconstructed.stages_skipped
        or original.validation_completed is not reconstructed.validation_completed
        or original.policy_evaluation_completed
        is not reconstructed.policy_evaluation_completed
        or original.provenance_authenticated is not reconstructed.provenance_authenticated
        or original.authorizes_provider_execution
        is not reconstructed.authorizes_provider_execution
        or original.independently_verifies_execution
        is not reconstructed.independently_verifies_execution
        or original.summary_issue_codes != reconstructed.summary_issue_codes
        or len(original.stage_outcomes) != len(reconstructed.stage_outcomes)
        or len(original.stage_issue_codes) != len(reconstructed.stage_issue_codes)
    ):
        return False

    for left, right in zip(original.stage_outcomes, reconstructed.stage_outcomes):
        if (
            left.stage is not right.stage
            or left.status is not right.status
            or left.issue_codes != right.issue_codes
        ):
            return False
    for left, right in zip(original.stage_issue_codes, reconstructed.stage_issue_codes):
        if left[0] is not right[0] or left[1] != right[1]:
            return False

    original_decision = original.policy_decision
    reconstructed_decision = reconstructed.policy_decision
    if original_decision is None or reconstructed_decision is None:
        return original_decision is None and reconstructed_decision is None
    if (
        original_decision.decision is not reconstructed_decision.decision
        or original_decision.accepted is not reconstructed_decision.accepted
        or original_decision.reason_codes != reconstructed_decision.reason_codes
        or original_decision.explanation != reconstructed_decision.explanation
        or original_decision.establishes_authenticity
        is not reconstructed_decision.establishes_authenticity
        or original_decision.authorizes_execution
        is not reconstructed_decision.authorizes_execution
        or original_decision.verifies_execution_correctness
        is not reconstructed_decision.verifies_execution_correctness
        or original_decision.independently_verifies_execution
        is not reconstructed_decision.independently_verifies_execution
        or len(original_decision.findings) != len(reconstructed_decision.findings)
    ):
        return False
    return all(
        left.code == right.code
        and left.category is right.category
        and left.severity is right.severity
        and left.field_path == right.field_path
        and left.sequence == right.sequence
        and left.message == right.message
        for left, right in zip(
            original_decision.findings, reconstructed_decision.findings
        )
    )


def _deserialize_stage_outcome(value: object) -> TracePipelineStageOutcome:
    source = _require_exact_dict(
        value, {"stage", "status", "issue_codes"}
    )
    return TracePipelineStageOutcome(
        stage=_require_enum(source["stage"], TracePipelineStage),
        status=_require_enum(source["status"], TracePipelineStageStatus),
        issue_codes=tuple(
            _require_string(code) for code in _require_list(source["issue_codes"])
        ),
    )


def _deserialize_stage_issue_codes(
    value: object,
) -> tuple[TracePipelineStage, tuple[str, ...]]:
    source = _require_exact_dict(value, {"stage", "issue_codes"})
    return (
        _require_enum(source["stage"], TracePipelineStage),
        tuple(
            _require_string(code) for code in _require_list(source["issue_codes"])
        ),
    )


def _deserialize_policy_decision(value: object) -> ProviderInvocationTracePolicyDecision:
    source = _require_exact_dict(
        value,
        {
            "decision",
            "accepted",
            "reason_codes",
            "findings",
            "explanation",
            "establishes_authenticity",
            "authorizes_execution",
            "verifies_execution_correctness",
            "independently_verifies_execution",
        },
    )
    findings = tuple(
        _deserialize_policy_finding(item)
        for item in _require_list(source["findings"])
    )
    return ProviderInvocationTracePolicyDecision(
        decision=_require_enum(source["decision"], TraceAcceptanceDecision),
        accepted=_require_bool(source["accepted"]),
        reason_codes=tuple(
            _require_string(code)
            for code in _require_list(source["reason_codes"])
        ),
        findings=findings,
        explanation=_require_string(source["explanation"]),
        establishes_authenticity=_require_bool(
            source["establishes_authenticity"]
        ),
        authorizes_execution=_require_bool(source["authorizes_execution"]),
        verifies_execution_correctness=_require_bool(
            source["verifies_execution_correctness"]
        ),
        independently_verifies_execution=_require_bool(
            source["independently_verifies_execution"]
        ),
    )


def _deserialize_policy_finding(value: object) -> ProviderInvocationTraceFinding:
    source = _require_exact_dict(
        value,
        {"code", "category", "severity", "field_path", "sequence", "message"},
    )
    field_path = source["field_path"]
    if field_path is not None:
        field_path = _require_string(field_path)
    sequence = source["sequence"]
    if sequence is not None and type(sequence) is not int:
        raise TypeError("invalid finding sequence")
    return ProviderInvocationTraceFinding(
        code=_require_string(source["code"]),
        category=_require_enum(source["category"], TraceFindingCategory),
        severity=_require_enum(source["severity"], TraceFindingSeverity),
        field_path=field_path,
        sequence=sequence,
        message=_require_string(source["message"]),
    )


def _require_exact_dict(
    value: object, expected_fields: set[str]
) -> dict[str, object]:
    if type(value) is not dict:
        raise TypeError("expected dictionary")
    if any(type(key) is not str for key in value):
        raise ValueError("invalid field name")
    if value.keys() != expected_fields:
        raise ValueError("invalid fields")
    return value


def _require_list(value: object) -> list[object]:
    if type(value) is not list:
        raise TypeError("expected list")
    return value


def _require_string(value: object) -> str:
    if type(value) is not str:
        raise TypeError("expected string")
    return value


def _require_bool(value: object) -> bool:
    if type(value) is not bool:
        raise TypeError("expected boolean")
    return value


def _require_enum(
    value: object, enum_type: type[_EnumValue]
) -> _EnumValue:
    if type(value) is not str:
        raise TypeError("expected enum string")
    return enum_type(value)


def _is_well_formed_diagnostic_summary(value: object) -> bool:
    if type(value) is not ProviderInvocationTracePipelineDiagnosticSummary:
        return False
    if (
        type(value.status) is not TracePipelineStatus
        or (
            value.failed_stage is not None
            and type(value.failed_stage) is not TracePipelineStage
        )
        or type(value.stage_outcomes) is not tuple
        or type(value.stage_issue_codes) is not tuple
        or type(value.stages_skipped) is not bool
        or type(value.validation_completed) is not bool
        or type(value.policy_evaluation_completed) is not bool
        or type(value.provenance_authenticated) is not bool
        or type(value.authorizes_provider_execution) is not bool
        or type(value.independently_verifies_execution) is not bool
        or value.provenance_authenticated
        or value.authorizes_provider_execution
        or value.independently_verifies_execution
        or type(value.summary_issue_codes) is not tuple
        or any(not _is_stable_code(code) for code in value.summary_issue_codes)
    ):
        return False

    if value.summary_issue_codes:
        return (
            value.summary_issue_codes == ("PIPELINE_RESULT_MALFORMED",)
            and value.status is TracePipelineStatus.REJECTED
            and value.failed_stage is None
            and not value.stage_outcomes
            and not value.stage_issue_codes
            and not value.stages_skipped
            and not value.validation_completed
            and not value.policy_evaluation_completed
            and value.policy_decision is None
        )

    expected_stages = (
        TracePipelineStage.EXPORT,
        TracePipelineStage.IMPORT,
        TracePipelineStage.VALIDATION,
        TracePipelineStage.POLICY,
    )
    if (
        len(value.stage_outcomes) != len(expected_stages)
        or len(value.stage_issue_codes) != len(expected_stages)
    ):
        return False
    for index, (outcome, stage, issue_entry) in enumerate(
        zip(value.stage_outcomes, expected_stages, value.stage_issue_codes)
    ):
        if (
            type(outcome) is not TracePipelineStageOutcome
            or outcome.stage is not stage
            or type(outcome.status) is not TracePipelineStageStatus
            or type(outcome.issue_codes) is not tuple
            or any(not _is_stable_code(code) for code in outcome.issue_codes)
            or type(issue_entry) is not tuple
            or len(issue_entry) != 2
            or issue_entry[0] is not stage
            or type(issue_entry[1]) is not tuple
            or any(not _is_stable_code(code) for code in issue_entry[1])
            or issue_entry[1] != outcome.issue_codes
            or not _stage_codes_are_valid(outcome)
        ):
            return False
        if index < 3 and outcome.status is TracePipelineStageStatus.FAILED:
            if value.failed_stage is not stage:
                return False

    failed_indexes = tuple(
        index
        for index, outcome in enumerate(value.stage_outcomes)
        if outcome.status is TracePipelineStageStatus.FAILED
    )
    if value.failed_stage is None:
        if failed_indexes or any(
            outcome.status is TracePipelineStageStatus.SKIPPED
            for outcome in value.stage_outcomes
        ):
            return False
    elif (
        len(failed_indexes) != 1
        or value.stage_outcomes[failed_indexes[0]].stage is not value.failed_stage
        or any(
            outcome.status is not TracePipelineStageStatus.SKIPPED
            for outcome in value.stage_outcomes[failed_indexes[0] + 1 :]
        )
        or any(
            outcome.status is not TracePipelineStageStatus.SUCCEEDED
            for outcome in value.stage_outcomes[: failed_indexes[0]]
        )
    ):
        return False

    skipped = any(
        outcome.status is TracePipelineStageStatus.SKIPPED
        for outcome in value.stage_outcomes
    )
    if (
        value.stages_skipped is not skipped
        or value.validation_completed
        is not (
            value.stage_outcomes[2].status is not TracePipelineStageStatus.SKIPPED
        )
        or value.policy_evaluation_completed
        is not (
            value.stage_outcomes[3].status is not TracePipelineStageStatus.SKIPPED
        )
    ):
        return False

    decision = value.policy_decision
    if decision is None:
        return (
            value.status is TracePipelineStatus.REJECTED
            and value.failed_stage in (TracePipelineStage.EXPORT, TracePipelineStage.IMPORT)
            and not value.validation_completed
            and not value.policy_evaluation_completed
        )
    if (
        type(decision) is not ProviderInvocationTracePolicyDecision
        or type(decision.decision) is not TraceAcceptanceDecision
        or type(decision.accepted) is not bool
        or type(decision.reason_codes) is not tuple
        or any(not _is_stable_code(code) for code in decision.reason_codes)
        or type(decision.findings) is not tuple
        or any(not _is_safe_policy_finding(finding) for finding in decision.findings)
        or type(decision.explanation) is not str
        or type(decision.establishes_authenticity) is not bool
        or type(decision.authorizes_execution) is not bool
        or type(decision.verifies_execution_correctness) is not bool
        or type(decision.independently_verifies_execution) is not bool
        or decision.establishes_authenticity
        or decision.authorizes_execution
        or decision.verifies_execution_correctness
        or decision.independently_verifies_execution
        or not value.validation_completed
        or not value.policy_evaluation_completed
        or value.stage_outcomes[2].issue_codes
        != tuple(finding.code for finding in decision.findings)
        or not _is_canonical_policy_decision(decision)
    ):
        return False
    expected_decision_status = {
        TraceAcceptanceDecision.ACCEPT: TracePipelineStatus.ACCEPTED,
        TraceAcceptanceDecision.ACCEPT_WITH_WARNINGS: (
            TracePipelineStatus.ACCEPTED_WITH_WARNINGS
        ),
        TraceAcceptanceDecision.REJECT: TracePipelineStatus.REJECTED,
    }[decision.decision]
    return (
        decision.accepted is (decision.decision is not TraceAcceptanceDecision.REJECT)
        and value.status is expected_decision_status
        and value.failed_stage
        is (
            TracePipelineStage.POLICY
            if decision.decision is TraceAcceptanceDecision.REJECT
            else None
        )
    )


def _is_canonical_policy_decision(
    decision: ProviderInvocationTracePolicyDecision,
) -> bool:
    if decision.decision is TraceAcceptanceDecision.ACCEPT:
        return (
            decision.reason_codes == ("NO_NON_BLOCKING_FINDINGS",)
            and not decision.findings
            and decision.explanation
            == "The trace satisfies the configured structural-consistency policy."
        )
    if decision.decision is TraceAcceptanceDecision.ACCEPT_WITH_WARNINGS:
        return (
            decision.reason_codes == ("NON_BLOCKING_FINDINGS_PRESENT",)
            and bool(decision.findings)
            and all(
                finding.severity is not TraceFindingSeverity.ERROR
                and finding.category
                not in (
                    TraceFindingCategory.STRUCTURAL_ERROR,
                    TraceFindingCategory.SEMANTIC_INCONSISTENCY,
                )
                for finding in decision.findings
            )
            and decision.explanation
            == (
                "The trace satisfies the consistency policy with non-blocking "
                "limitations that require disclosure."
            )
        )
    if decision.decision is TraceAcceptanceDecision.REJECT:
        return (
            decision.reason_codes
            in (
                ("VALIDATION_REPORT_INVALID", "BLOCKING_FINDINGS_PRESENT"),
                ("VALIDATION_REPORT_INVALID",),
                ("BLOCKING_FINDINGS_PRESENT",),
            )
            and (
                "BLOCKING_FINDINGS_PRESENT" not in decision.reason_codes
                or any(
                    finding.severity is TraceFindingSeverity.ERROR
                    or finding.category
                    in (
                        TraceFindingCategory.STRUCTURAL_ERROR,
                        TraceFindingCategory.SEMANTIC_INCONSISTENCY,
                    )
                    for finding in decision.findings
                )
            )
            and decision.explanation
            == (
                "The trace does not satisfy the configured structural and "
                "semantic consistency policy."
            )
        )
    return False


def _is_well_formed_pipeline_result(value: object) -> bool:
    if type(value) is not ProviderInvocationTracePipelineResult:
        return False
    if (
        type(value.status) is not TracePipelineStatus
        or type(value.stage_outcomes) is not tuple
        or (
            value.rejected_at is not None
            and type(value.rejected_at) is not TracePipelineStage
        )
        or type(value.provenance_authenticated) is not bool
        or type(value.authorizes_provider_execution) is not bool
        or type(value.independently_verifies_execution) is not bool
        or value.provenance_authenticated
        or value.authorizes_provider_execution
        or value.independently_verifies_execution
    ):
        return False

    expected_stages = (
        TracePipelineStage.EXPORT,
        TracePipelineStage.IMPORT,
        TracePipelineStage.VALIDATION,
        TracePipelineStage.POLICY,
    )
    if len(value.stage_outcomes) != len(expected_stages):
        return False
    for outcome, expected_stage in zip(value.stage_outcomes, expected_stages):
        if (
            type(outcome) is not TracePipelineStageOutcome
            or outcome.stage is not expected_stage
            or type(outcome.status) is not TracePipelineStageStatus
            or type(outcome.issue_codes) is not tuple
            or any(
                not _is_stable_code(code)
                for code in outcome.issue_codes
            )
        ):
            return False
        if not _stage_codes_are_valid(outcome):
            return False

    if value.rejected_at is None:
        if any(
            outcome.status is not TracePipelineStageStatus.SUCCEEDED
            for outcome in value.stage_outcomes
        ):
            return False
    else:
        failed_indexes = tuple(
            index
            for index, outcome in enumerate(value.stage_outcomes)
            if outcome.status is TracePipelineStageStatus.FAILED
        )
        if (
            len(failed_indexes) != 1
            or value.stage_outcomes[failed_indexes[0]].stage is not value.rejected_at
            or any(
                outcome.status is not TracePipelineStageStatus.SKIPPED
                for outcome in value.stage_outcomes[failed_indexes[0] + 1 :]
            )
            or any(
                outcome.status is not TracePipelineStageStatus.SUCCEEDED
                for outcome in value.stage_outcomes[: failed_indexes[0]]
            )
        ):
            return False

    stage_statuses = {
        outcome.stage: outcome.status for outcome in value.stage_outcomes
    }
    if (
        (value.export_result is not None)
        != (
            stage_statuses[TracePipelineStage.EXPORT]
            is TracePipelineStageStatus.SUCCEEDED
        )
        or (value.import_result is not None)
        != (
            stage_statuses[TracePipelineStage.IMPORT]
            is TracePipelineStageStatus.SUCCEEDED
        )
        or (value.validation_report is not None)
        != (
            stage_statuses[TracePipelineStage.VALIDATION]
            is TracePipelineStageStatus.SUCCEEDED
        )
        or (value.policy_decision is not None)
        != (
            stage_statuses[TracePipelineStage.POLICY]
            is not TracePipelineStageStatus.SKIPPED
        )
    ):
        return False
    if (
        value.export_result is not None
        and type(value.export_result) is not ProviderInvocationTraceExport
    ):
        return False
    if (
        value.import_result is not None
        and type(value.import_result) is not ImportedProviderInvocationTrace
    ):
        return False
    if (
        value.validation_report is not None
        and type(value.validation_report)
        is not ProviderInvocationTraceValidationReport
    ):
        return False

    if value.policy_decision is None:
        return (
            value.status is TracePipelineStatus.REJECTED
            and value.rejected_at in (TracePipelineStage.EXPORT, TracePipelineStage.IMPORT)
            and value.validation_report is None
            and value.import_result is None
        )
    if type(value.policy_decision) is not ProviderInvocationTracePolicyDecision:
        return False
    if (
        type(value.policy_decision.decision) is not TraceAcceptanceDecision
        or type(value.policy_decision.accepted) is not bool
        or type(value.policy_decision.reason_codes) is not tuple
        or any(
            not _is_stable_code(code)
            for code in value.policy_decision.reason_codes
        )
        or type(value.policy_decision.findings) is not tuple
        or type(value.policy_decision.explanation) is not str
        or type(value.policy_decision.establishes_authenticity) is not bool
        or type(value.policy_decision.authorizes_execution) is not bool
        or type(value.policy_decision.verifies_execution_correctness) is not bool
        or type(value.policy_decision.independently_verifies_execution) is not bool
        or value.policy_decision.establishes_authenticity
        or value.policy_decision.authorizes_execution
        or value.policy_decision.verifies_execution_correctness
        or value.policy_decision.independently_verifies_execution
    ):
        return False
    if any(
        not _is_safe_policy_finding(finding)
        for finding in value.policy_decision.findings
    ):
        return False
    if value.policy_decision.accepted is not (
        value.policy_decision.decision is not TraceAcceptanceDecision.REJECT
    ):
        return False
    if value.stage_outcomes[2].issue_codes != tuple(
        finding.code for finding in value.policy_decision.findings
    ):
        return False
    expected_reason_codes = {
        TraceAcceptanceDecision.ACCEPT: ("NO_NON_BLOCKING_FINDINGS",),
        TraceAcceptanceDecision.ACCEPT_WITH_WARNINGS: (
            "NON_BLOCKING_FINDINGS_PRESENT",
        ),
        TraceAcceptanceDecision.REJECT: (
            ("VALIDATION_REPORT_INVALID", "BLOCKING_FINDINGS_PRESENT"),
            ("VALIDATION_REPORT_INVALID",),
            ("BLOCKING_FINDINGS_PRESENT",),
        ),
    }[value.policy_decision.decision]
    if value.policy_decision.decision is TraceAcceptanceDecision.REJECT:
        if value.policy_decision.reason_codes not in expected_reason_codes:
            return False
    elif value.policy_decision.reason_codes != expected_reason_codes:
        return False
    if value.policy_decision.explanation not in {
        "The validation report is malformed or unsupported; the trace was rejected.",
        (
            "The trace does not satisfy the configured structural and semantic "
            "consistency policy."
        ),
        (
            "The trace satisfies the consistency policy with non-blocking "
            "limitations that require disclosure."
        ),
        "The trace satisfies the configured structural-consistency policy.",
    }:
        return False
    expected_status = {
        TraceAcceptanceDecision.ACCEPT: TracePipelineStatus.ACCEPTED,
        TraceAcceptanceDecision.ACCEPT_WITH_WARNINGS: (
            TracePipelineStatus.ACCEPTED_WITH_WARNINGS
        ),
        TraceAcceptanceDecision.REJECT: TracePipelineStatus.REJECTED,
    }[value.policy_decision.decision]
    return (
        value.status is expected_status
        and value.validation_report is not None
        and value.import_result is not None
        and value.export_result is not None
        and value.rejected_at
        is (
            TracePipelineStage.POLICY
            if value.policy_decision.decision is TraceAcceptanceDecision.REJECT
            else None
        )
    )


def _is_stable_code(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and all(
            character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
            for character in value
        )
    )


def _stage_codes_are_valid(outcome: TracePipelineStageOutcome) -> bool:
    if outcome.status is TracePipelineStageStatus.SKIPPED:
        return outcome.issue_codes == ("PRIOR_STAGE_FAILED",)
    if outcome.stage is TracePipelineStage.EXPORT:
        expected = (
            ("EXPORT_CONTRACT_REJECTED",)
            if outcome.status is TracePipelineStageStatus.FAILED
            else ()
        )
        return outcome.issue_codes == expected
    if outcome.stage is TracePipelineStage.IMPORT:
        expected = (
            ("IMPORT_SCHEMA_REJECTED",)
            if outcome.status is TracePipelineStageStatus.FAILED
            else ()
        )
        return outcome.issue_codes == expected
    if outcome.stage is TracePipelineStage.VALIDATION:
        return outcome.status is TracePipelineStageStatus.SUCCEEDED
    return outcome.status in (
        TracePipelineStageStatus.SUCCEEDED,
        TracePipelineStageStatus.FAILED,
    )


def _is_safe_policy_finding(value: object) -> bool:
    return (
        type(value) is ProviderInvocationTraceFinding
        and _is_stable_code(value.code)
        and type(value.category) is TraceFindingCategory
        and type(value.severity) is TraceFindingSeverity
        and (
            value.field_path is None
            or (
                type(value.field_path) is str
                and bool(_SAFE_FIELD_PATH_PATTERN.fullmatch(value.field_path))
            )
        )
        and (
            value.sequence is None
            or (type(value.sequence) is int and value.sequence >= 1)
        )
        and type(value.message) is str
        and value.message in _SAFE_FINDING_MESSAGES
    )


def _invalid_pipeline_summary(
) -> ProviderInvocationTracePipelineDiagnosticSummary:
    return ProviderInvocationTracePipelineDiagnosticSummary(
        status=TracePipelineStatus.REJECTED,
        failed_stage=None,
        stage_outcomes=(),
        stage_issue_codes=(),
        stages_skipped=False,
        validation_completed=False,
        policy_evaluation_completed=False,
        policy_decision=None,
        provenance_authenticated=False,
        authorizes_provider_execution=False,
        independently_verifies_execution=False,
        summary_issue_codes=("PIPELINE_RESULT_MALFORMED",),
    )


def _skipped_stages(
    first_skipped_stage: TracePipelineStage,
) -> tuple[TracePipelineStageOutcome, ...]:
    stages = (
        TracePipelineStage.EXPORT,
        TracePipelineStage.IMPORT,
        TracePipelineStage.VALIDATION,
        TracePipelineStage.POLICY,
    )
    start_index = stages.index(first_skipped_stage)
    return tuple(
        TracePipelineStageOutcome(
            stage=stage,
            status=TracePipelineStageStatus.SKIPPED,
            issue_codes=("PRIOR_STAGE_FAILED",),
        )
        for stage in stages[start_index:]
    )

"""In-memory, provider-neutral traces for coordinator lifecycle results.

Trace events contain lifecycle metadata only. They do not execute providers,
record invocation payloads, or independently verify provider-reported outcomes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from types import MappingProxyType
from typing import Mapping

from scripts.provider_adapter import ExecutionState
from scripts.provider_capability_resolver import (
    CapabilityResolutionStatus,
    ProviderCapabilityCandidate,
    ProviderCapabilityResolution,
    ProviderCandidateStatus,
)
from scripts.provider_invocation import ProviderInvocation
from scripts.provider_invocation_coordinator import (
    InvocationLifecycleIssue,
    InvocationLifecycleIssueCode,
    InvocationLifecycleState,
    InvocationLifecycleResult,
    is_valid_invocation_lifecycle_transition,
)
from scripts.provider_invocation_result import (
    ProviderInvocationResultRecord,
    ProviderInvocationResultValidationError,
    validate_provider_invocation_result,
)
from scripts.provider_adapter import ProviderInvocationResult


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")
_UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z"
)
_DETAIL_FIELD_TYPES = {
    "candidate_count": int,
    "reason_code": str,
    "resolution_status": str,
}
_RESOLUTION_STATUS_VALUES = frozenset(
    status.value for status in CapabilityResolutionStatus
)


class ProviderInvocationTraceError(ValueError):
    """Base class for trace creation, recording, and retrieval errors."""


class InvalidTraceInputError(ProviderInvocationTraceError):
    """Raised when an invocation or lifecycle input is malformed."""


class DuplicateTraceError(ProviderInvocationTraceError):
    """Raised when a trace already exists for a correlation identifier."""


class TraceNotFoundError(ProviderInvocationTraceError):
    """Raised when a requested correlation identifier has no trace."""


class InvalidTraceSequenceError(ProviderInvocationTraceError):
    """Raised when lifecycle events are duplicated or out of sequence."""


class TraceEventType(str, Enum):
    LIFECYCLE_STATE = "lifecycle_state"
    ISSUE_REPORTED = "issue_reported"
    RESULT_VALIDATED = "result_validated"


@dataclass(frozen=True, slots=True)
class ProviderInvocationTraceEvent:
    """Immutable lifecycle event; execution confirmation is provider-reported."""

    event_id: str
    correlation_id: str
    sequence: int
    event_type: TraceEventType
    lifecycle_state: InvocationLifecycleState
    issue_codes: tuple[str, ...]
    provider_id: str | None
    capability_id: str
    operation_id: str
    provider_execution_reported: bool
    execution_independently_verified: bool
    details: Mapping[str, str | int]


@dataclass(frozen=True, slots=True)
class ProviderInvocationTrace:
    """Read-only ordered snapshot for one invocation correlation identifier."""

    correlation_id: str
    provider_id: str | None
    capability_id: str
    operation_id: str
    events: tuple[ProviderInvocationTraceEvent, ...]


@dataclass(slots=True)
class _TraceState:
    request: ProviderInvocation
    events: list[ProviderInvocationTraceEvent]
    lifecycle_history: tuple[InvocationLifecycleState, ...] = ()
    issues: tuple[InvocationLifecycleIssue, ...] = ()
    validated_result: ProviderInvocationResultRecord | None = None


class ProviderInvocationTraceRecorder:
    """Thread-safe in-memory recorder for explicit coordinator lifecycle results."""

    def __init__(self) -> None:
        self._traces: dict[str, _TraceState] = {}
        self._lock = Lock()

    def start_trace(self, request: ProviderInvocation) -> ProviderInvocationTrace:
        """Create an empty trace for a canonical invocation request.

        Calling this twice for the same request ID is an error; no trace is
        silently replaced or reset.
        """
        self._validate_request(request)
        correlation_id = request.request_id
        with self._lock:
            if correlation_id in self._traces:
                raise DuplicateTraceError(
                    f"trace already exists for correlation identifier {correlation_id!r}."
                )
            self._traces[correlation_id] = _TraceState(
                request=request,
                events=[],
            )
            return self._snapshot(correlation_id, self._traces[correlation_id])

    def append_lifecycle(
        self,
        request: ProviderInvocation,
        lifecycle: InvocationLifecycleResult,
        *,
        details: Mapping[str, object] | None = None,
        reported_result: ProviderInvocationResult | None = None,
    ) -> tuple[ProviderInvocationTraceEvent, ...]:
        """Append new lifecycle states and issues without invoking an adapter.

        ``details`` accepts only allowlisted metadata keys. Request payload,
        context, grants, cancellation state, result output, and arbitrary object
        representations are never copied into trace events.
        """
        self._validate_request(request)
        safe_details = self._validate_details(details)
        if type(lifecycle) is not InvocationLifecycleResult:
            raise InvalidTraceInputError(
                "lifecycle must use the canonical InvocationLifecycleResult type."
            )
        self._validate_lifecycle(lifecycle, request)
        correlation_id = request.request_id

        with self._lock:
            trace = self._traces.get(correlation_id)
            if trace is None:
                raise TraceNotFoundError(
                    f"trace not found for correlation identifier {correlation_id!r}."
                )
            if not self._same_request(trace.request, request):
                raise InvalidTraceInputError(
                    "request does not match the trace's original invocation."
                )
            if lifecycle.state_history[: len(trace.lifecycle_history)] != (
                trace.lifecycle_history
            ):
                raise InvalidTraceSequenceError(
                    "lifecycle history does not extend the recorded state sequence."
                )
            if lifecycle.issues[: len(trace.issues)] != trace.issues:
                raise InvalidTraceSequenceError(
                    "lifecycle issues do not extend the recorded issue sequence."
                )
            if trace.validated_result is not None and (
                lifecycle.validated_result != trace.validated_result
            ):
                raise InvalidTraceSequenceError(
                    "validated result cannot be replaced after it is recorded."
                )
            if (
                len(lifecycle.state_history) == len(trace.lifecycle_history)
                and len(lifecycle.issues) == len(trace.issues)
            ):
                raise InvalidTraceSequenceError(
                    "lifecycle update contains no new states or issues."
                )

            validated_result = self._validate_lifecycle_result(
                lifecycle, request, reported_result
            )
            added_states = lifecycle.state_history[len(trace.lifecycle_history) :]
            added_issues = lifecycle.issues[len(trace.issues) :]
            pending_events: list[ProviderInvocationTraceEvent] = []
            sequence = len(trace.events) + 1

            for state in added_states:
                event_details = dict(safe_details)
                if lifecycle.resolution is not None:
                    event_details.setdefault(
                        "resolution_status", lifecycle.resolution.status.value
                    )
                    event_details.setdefault(
                        "candidate_count",
                        len(lifecycle.resolution.candidates),
                    )
                pending_events.append(
                    self._new_event(
                        correlation_id=correlation_id,
                        sequence=sequence,
                        event_type=TraceEventType.LIFECYCLE_STATE,
                        lifecycle_state=state,
                        issue_codes=(),
                        provider_id=request.provider_id,
                        request=request,
                        provider_execution_reported=False,
                        details=event_details,
                    )
                )
                sequence += 1

            for issue in added_issues:
                pending_events.append(
                    self._new_event(
                        correlation_id=correlation_id,
                        sequence=sequence,
                        event_type=TraceEventType.ISSUE_REPORTED,
                        lifecycle_state=lifecycle.state,
                        issue_codes=(issue.code.value,),
                        provider_id=request.provider_id,
                        request=request,
                        provider_execution_reported=False,
                        details=safe_details,
                    )
                )
                sequence += 1

            if validated_result is not None and trace.validated_result is None:
                pending_events.append(
                    self._new_event(
                        correlation_id=correlation_id,
                        sequence=sequence,
                        event_type=TraceEventType.RESULT_VALIDATED,
                        lifecycle_state=lifecycle.state,
                        issue_codes=(),
                        provider_id=validated_result.outcome.provenance.provider_id,
                        request=request,
                        provider_execution_reported=(
                            validated_result.outcome.execution_state
                            is ExecutionState.EXECUTED
                        ),
                        details=safe_details,
                    )
                )
                sequence += 1

            if not pending_events:
                raise InvalidTraceSequenceError(
                    "lifecycle update did not produce any trace events."
                )
            trace.events.extend(pending_events)
            trace.lifecycle_history = lifecycle.state_history
            trace.issues = lifecycle.issues
            if validated_result is not None:
                trace.validated_result = validated_result
            return tuple(pending_events)

    def get_trace(self, correlation_id: str) -> ProviderInvocationTrace:
        """Return one deterministic immutable trace snapshot."""
        self._validate_correlation_id(correlation_id)
        with self._lock:
            trace = self._traces.get(correlation_id)
            if trace is None:
                raise TraceNotFoundError(
                    f"trace not found for correlation identifier {correlation_id!r}."
                )
            return self._snapshot(correlation_id, trace)

    def list_traces(self) -> tuple[ProviderInvocationTrace, ...]:
        """Return snapshots ordered lexically by canonical correlation ID."""
        with self._lock:
            return tuple(
                self._snapshot(correlation_id, self._traces[correlation_id])
                for correlation_id in sorted(self._traces)
            )

    @staticmethod
    def _validate_request(request: object) -> None:
        if type(request) is not ProviderInvocation:
            raise InvalidTraceInputError(
                "request must use the canonical ProviderInvocation type."
            )
        if not isinstance(request.request_id, str) or not _UUID_PATTERN.fullmatch(
            request.request_id
        ):
            raise InvalidTraceInputError(
                "request correlation identifier must be a canonical UUID."
            )
        for field_name in ("capability_id", "operation_id"):
            value = getattr(request, field_name)
            if not isinstance(value, str) or not _IDENTIFIER_PATTERN.fullmatch(value):
                raise InvalidTraceInputError(
                    f"request {field_name} must be a valid canonical identifier."
                )
        if request.provider_id is not None and (
            not isinstance(request.provider_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(request.provider_id)
        ):
            raise InvalidTraceInputError(
                "request provider_id must be a valid canonical identifier."
            )

    @staticmethod
    def _validate_correlation_id(correlation_id: object) -> None:
        if not isinstance(correlation_id, str) or not _UUID_PATTERN.fullmatch(
            correlation_id
        ):
            raise InvalidTraceInputError(
                "correlation identifier must be a lowercase canonical UUID."
            )

    @staticmethod
    def _validate_lifecycle(
        lifecycle: InvocationLifecycleResult,
        request: ProviderInvocation,
    ) -> None:
        if lifecycle.request_id != request.request_id:
            raise InvalidTraceInputError(
                "lifecycle request identifier does not match the invocation."
            )
        if type(lifecycle.state_history) is not tuple or not lifecycle.state_history:
            raise InvalidTraceInputError(
                "lifecycle state history must be a non-empty tuple."
            )
        if lifecycle.state_history[0] is not InvocationLifecycleState.REQUEST_RECEIVED:
            raise InvalidTraceInputError(
                "lifecycle history must begin at REQUEST_RECEIVED."
            )
        if lifecycle.state_history[-1] is not lifecycle.state:
            raise InvalidTraceInputError(
                "lifecycle current state must match its final state-history entry."
            )
        checked_history = [lifecycle.state_history[0]]
        try:
            for state in lifecycle.state_history[1:]:
                if not is_valid_invocation_lifecycle_transition(
                    checked_history[-1], state
                ):
                    raise ValueError("invalid lifecycle transition")
                checked_history.append(state)
        except ValueError as error:
            raise InvalidTraceSequenceError(
                "lifecycle history contains an invalid state transition."
            ) from error
        if type(lifecycle.issues) is not tuple or any(
            type(issue) is not InvocationLifecycleIssue
            or type(issue.code) is not InvocationLifecycleIssueCode
            or not isinstance(issue.message, str)
            for issue in lifecycle.issues
        ):
            raise InvalidTraceInputError(
                "lifecycle issues must be canonical structured issue values."
            )
        if lifecycle.resolution is not None:
            if type(lifecycle.resolution) is not ProviderCapabilityResolution:
                raise InvalidTraceInputError(
                    "lifecycle resolution must use the canonical resolver result."
                )
            if (
                type(lifecycle.resolution.status) is not CapabilityResolutionStatus
                or type(lifecycle.resolution.candidates) is not tuple
                or any(
                    type(candidate) is not ProviderCapabilityCandidate
                    or type(candidate.status) is not ProviderCandidateStatus
                    or (
                        candidate.provider_id is not None
                        and (
                            not isinstance(candidate.provider_id, str)
                            or not _IDENTIFIER_PATTERN.fullmatch(
                                candidate.provider_id
                            )
                        )
                    )
                    for candidate in lifecycle.resolution.candidates
                )
            ):
                raise InvalidTraceInputError(
                    "lifecycle resolution fields are malformed."
                )
            if (
                lifecycle.resolution.capability_id != request.capability_id
                or lifecycle.resolution.operation_id != request.operation_id
            ):
                raise InvalidTraceInputError(
                    "lifecycle resolution does not match the invocation request."
                )
        if lifecycle.validated_result is not None:
            if type(lifecycle.validated_result) is not ProviderInvocationResultRecord:
                raise InvalidTraceInputError(
                    "validated result must use the canonical result record."
                )
            if (
                lifecycle.state
                is not InvocationLifecycleState.COMPLETED_WITH_VALIDATED_RESULT
            ):
                raise InvalidTraceSequenceError(
                    "a validated result requires the completed lifecycle state."
                )
        if (
            lifecycle.state
            is InvocationLifecycleState.COMPLETED_WITH_VALIDATED_RESULT
            and lifecycle.validated_result is None
        ):
            raise InvalidTraceSequenceError(
                "completed lifecycle requires a supplied, validated result record."
            )
        if type(lifecycle.compatible_provider_ids) is not tuple or any(
            not isinstance(provider_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(provider_id)
            for provider_id in lifecycle.compatible_provider_ids
        ):
            raise InvalidTraceInputError(
                "compatible provider identifiers must be a tuple of canonical identifiers."
            )
        if len(set(lifecycle.compatible_provider_ids)) != len(
            lifecycle.compatible_provider_ids
        ):
            raise InvalidTraceInputError(
                "compatible provider identifiers must not contain duplicates."
            )
        if lifecycle.resolution is not None:
            expected_compatible_ids = tuple(
                candidate.provider_id
                for candidate in lifecycle.resolution.compatible_candidates
                if candidate.provider_id is not None
            )
            if lifecycle.compatible_provider_ids != expected_compatible_ids:
                raise InvalidTraceInputError(
                    "compatible provider identifiers do not match the resolution."
                )

    @staticmethod
    def _validate_details(
        details: Mapping[str, object] | None,
    ) -> Mapping[str, str | int]:
        if details is None:
            return MappingProxyType({})
        if type(details) not in (dict, MappingProxyType):
            raise InvalidTraceInputError(
                "details must be a plain dictionary or immutable mapping."
            )
        if any(type(key) is not str for key in details):
            raise InvalidTraceInputError("details keys must be strings.")
        safe: dict[str, str | int] = {}
        for key in sorted(details):
            if not isinstance(key, str) or key not in _DETAIL_FIELD_TYPES:
                raise InvalidTraceInputError(
                    "details contain an unsupported field."
                )
            value = details[key]
            expected_type = _DETAIL_FIELD_TYPES[key]
            if type(value) is not expected_type:
                raise InvalidTraceInputError(
                    f"detail {key!r} must use its supported scalar type."
                )
            if key == "candidate_count" and value < 0:
                raise InvalidTraceInputError(
                    "candidate_count must not be negative."
                )
            if key == "reason_code" and not _IDENTIFIER_PATTERN.fullmatch(value):
                raise InvalidTraceInputError(
                    f"detail {key!r} must be a supported structured code."
                )
            if key == "resolution_status" and value not in _RESOLUTION_STATUS_VALUES:
                raise InvalidTraceInputError(
                    f"detail {key!r} must be a supported structured code."
                )
            safe[key] = value
        return MappingProxyType(safe)

    @staticmethod
    def _validate_lifecycle_result(
        lifecycle: InvocationLifecycleResult,
        request: ProviderInvocation,
        reported_result: ProviderInvocationResult | None,
    ) -> ProviderInvocationResultRecord | None:
        record = lifecycle.validated_result
        if record is None:
            if reported_result is not None:
                raise InvalidTraceInputError(
                    "reported result is not present in the coordinator lifecycle result."
                )
            return None
        if type(reported_result) is not ProviderInvocationResult:
            raise InvalidTraceInputError(
                "completed lifecycle recording requires the supplied canonical "
                "provider-reported result."
            )
        try:
            validated = validate_provider_invocation_result(
                reported_result,
                request,
                capability_id=record.capability_id,
            )
        except (ProviderInvocationResultValidationError, TypeError, ValueError) as error:
            raise InvalidTraceInputError(
                "lifecycle validated result did not pass canonical result validation."
            ) from error
        provider_id = validated.outcome.provenance.provider_id
        if provider_id not in lifecycle.compatible_provider_ids:
            raise InvalidTraceInputError(
                "validated result provider is not in the compatible candidate list."
            )
        if validated != record:
            raise InvalidTraceInputError(
                "lifecycle result record differs from its validated snapshot."
            )
        return validated

    @staticmethod
    def _same_request(
        stored: ProviderInvocation,
        supplied: ProviderInvocation,
    ) -> bool:
        return stored == supplied

    @staticmethod
    def _new_event(
        *,
        correlation_id: str,
        sequence: int,
        event_type: TraceEventType,
        lifecycle_state: InvocationLifecycleState,
        issue_codes: tuple[str, ...],
        provider_id: str | None,
        request: ProviderInvocation,
        provider_execution_reported: bool,
        details: Mapping[str, str | int],
    ) -> ProviderInvocationTraceEvent:
        if provider_id is not None and not _IDENTIFIER_PATTERN.fullmatch(provider_id):
            raise InvalidTraceInputError(
                "event provider identifier must be valid or None."
            )
        return ProviderInvocationTraceEvent(
            event_id=f"{correlation_id}:{sequence}",
            correlation_id=correlation_id,
            sequence=sequence,
            event_type=event_type,
            lifecycle_state=lifecycle_state,
            issue_codes=issue_codes,
            provider_id=provider_id,
            capability_id=request.capability_id,
            operation_id=request.operation_id,
            provider_execution_reported=provider_execution_reported,
            execution_independently_verified=False,
            details=MappingProxyType(dict(details)),
        )

    @staticmethod
    def _snapshot(
        correlation_id: str, trace: _TraceState
    ) -> ProviderInvocationTrace:
        return ProviderInvocationTrace(
            correlation_id=correlation_id,
            provider_id=trace.request.provider_id,
            capability_id=trace.request.capability_id,
            operation_id=trace.request.operation_id,
            events=tuple(trace.events),
        )

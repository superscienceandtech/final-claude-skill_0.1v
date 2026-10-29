"""Strict in-memory validation for provider invocation trace exports.

Imported records are immutable, untrusted data. They are not canonical live
traces, authorization evidence, or proof that a provider executed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from scripts.provider_capability_resolver import CapabilityResolutionStatus
from scripts.provider_invocation_coordinator import (
    InvocationLifecycleIssueCode,
    InvocationLifecycleState,
    is_valid_invocation_lifecycle_transition,
)
from scripts.provider_invocation_trace import TraceEventType


_UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z"
)
_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")
_TRACE_FIELDS = frozenset({"correlation_id", "events"})
_EVENT_FIELDS = frozenset(
    {
        "event_id",
        "correlation_id",
        "sequence",
        "event_type",
        "lifecycle_state",
        "issue_codes",
        "provider_id",
        "capability_id",
        "operation_id",
        "provider_execution_reported",
        "execution_independently_verified",
        "details",
    }
)
_DETAIL_FIELDS = frozenset(
    {"candidate_count", "reason_code", "resolution_status"}
)
_EVENT_TYPE_VALUES = frozenset(event_type.value for event_type in TraceEventType)
_LIFECYCLE_STATE_VALUES = frozenset(
    state.value for state in InvocationLifecycleState
)
_ISSUE_CODE_VALUES = frozenset(code.value for code in InvocationLifecycleIssueCode)
_RESOLUTION_STATUS_VALUES = frozenset(
    status.value for status in CapabilityResolutionStatus
)


class ProviderInvocationTraceImportError(ValueError):
    """Schema-validation error containing a safe code and field path."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code} at {path}: {message}")


@dataclass(frozen=True, slots=True)
class ImportedProviderInvocationTraceEvent:
    """Immutable imported event; claims remain untrusted and unverified."""

    event_id: str
    correlation_id: str
    sequence: int
    event_type: str
    lifecycle_state: str
    issue_codes: tuple[str, ...]
    provider_id: str | None
    capability_id: str | None
    operation_id: str | None
    provider_execution_reported: bool
    execution_independently_verified: bool
    details: Mapping[str, str | int]

    def to_dict(self) -> dict[str, object]:
        """Return a fresh plain-data event mapping."""
        return {
            "event_id": self.event_id,
            "correlation_id": self.correlation_id,
            "sequence": self.sequence,
            "event_type": self.event_type,
            "lifecycle_state": self.lifecycle_state,
            "issue_codes": list(self.issue_codes),
            "provider_id": self.provider_id,
            "capability_id": self.capability_id,
            "operation_id": self.operation_id,
            "provider_execution_reported": self.provider_execution_reported,
            "execution_independently_verified": (
                self.execution_independently_verified
            ),
            "details": {key: self.details[key] for key in sorted(self.details)},
        }


@dataclass(frozen=True, slots=True)
class ImportedProviderInvocationTrace:
    """Immutable imported export data, separate from recorder-owned traces."""

    correlation_id: str
    events: tuple[ImportedProviderInvocationTraceEvent, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a fresh plain-data representation matching the export schema."""
        return {
            "correlation_id": self.correlation_id,
            "events": [event.to_dict() for event in self.events],
        }


def import_provider_invocation_trace(
    value: Mapping[str, object],
) -> ImportedProviderInvocationTrace:
    """Validate a supported in-memory mapping against the canonical export schema.

    Only built-in dictionaries and read-only mapping proxies are accepted, so
    validation never invokes user-defined mapping or serialization hooks.
    """
    trace_mapping = _require_mapping(value, "$")
    _require_exact_fields(trace_mapping, _TRACE_FIELDS, "$")
    correlation_id = _require_uuid(trace_mapping["correlation_id"], "$.correlation_id")
    raw_events = trace_mapping["events"]
    if type(raw_events) not in (list, tuple):
        _error(
            "invalid_type",
            "$.events",
            "expected a list or tuple of event mappings.",
        )

    imported_events: list[ImportedProviderInvocationTraceEvent] = []
    seen_event_ids: set[str] = set()
    previous_sequence = 0
    previous_lifecycle_state: InvocationLifecycleState | None = None
    result_event_seen = False

    for index, raw_event in enumerate(raw_events):
        path = f"$.events[{index}]"
        event_mapping = _require_mapping(raw_event, path)
        _require_exact_fields(event_mapping, _EVENT_FIELDS, path)

        event_correlation_id = _require_uuid(
            event_mapping["correlation_id"], f"{path}.correlation_id"
        )
        if event_correlation_id != correlation_id:
            _error(
                "correlation_mismatch",
                f"{path}.correlation_id",
                "event correlation identifier must match the trace.",
            )

        sequence = event_mapping["sequence"]
        if type(sequence) is not int or sequence <= 0:
            _error(
                "invalid_sequence",
                f"{path}.sequence",
                "sequence must be a positive integer.",
            )
        if sequence <= previous_sequence:
            _error(
                "invalid_sequence",
                f"{path}.sequence",
                "sequence numbers must strictly increase in event order.",
            )
        previous_sequence = sequence

        event_id = event_mapping["event_id"]
        expected_event_id = f"{correlation_id}:{sequence}"
        if type(event_id) is not str or event_id != expected_event_id:
            _error(
                "invalid_event_id",
                f"{path}.event_id",
                "event identifier must match its trace correlation and sequence.",
            )
        if event_id in seen_event_ids:
            _error(
                "duplicate_event_id",
                f"{path}.event_id",
                "event identifiers must be unique within the trace.",
            )
        seen_event_ids.add(event_id)

        event_type_value = _require_enum_value(
            event_mapping["event_type"],
            _EVENT_TYPE_VALUES,
            f"{path}.event_type",
        )
        lifecycle_value = _require_enum_value(
            event_mapping["lifecycle_state"],
            _LIFECYCLE_STATE_VALUES,
            f"{path}.lifecycle_state",
        )
        event_type = TraceEventType(event_type_value)
        lifecycle_state = InvocationLifecycleState(lifecycle_value)

        issue_codes_value = event_mapping["issue_codes"]
        if type(issue_codes_value) not in (list, tuple):
            _error(
                "invalid_type",
                f"{path}.issue_codes",
                "issue codes must be a list or tuple of canonical codes.",
            )
        issue_codes: list[str] = []
        for issue_index, code in enumerate(issue_codes_value):
            if type(code) is not str or code not in _ISSUE_CODE_VALUES:
                _error(
                    "invalid_issue_code",
                    f"{path}.issue_codes[{issue_index}]",
                    "issue code is not defined by the canonical contract.",
                )
            issue_codes.append(code)

        provider_id = _optional_identifier(
            event_mapping["provider_id"], f"{path}.provider_id"
        )
        capability_id = _optional_identifier(
            event_mapping["capability_id"], f"{path}.capability_id"
        )
        operation_id = _optional_identifier(
            event_mapping["operation_id"], f"{path}.operation_id"
        )

        provider_reported = event_mapping["provider_execution_reported"]
        independently_verified = event_mapping["execution_independently_verified"]
        if type(provider_reported) is not bool:
            _error(
                "invalid_type",
                f"{path}.provider_execution_reported",
                "execution indicator must be a boolean.",
            )
        if type(independently_verified) is not bool:
            _error(
                "invalid_type",
                f"{path}.execution_independently_verified",
                "verification indicator must be a boolean.",
            )

        details = _validate_details(event_mapping["details"], f"{path}.details")
        previous_lifecycle_state, result_event_seen = _validate_event_semantics(
            event_type,
            lifecycle_state,
            tuple(issue_codes),
            provider_reported,
            previous_lifecycle_state,
            result_event_seen,
            path,
        )

        imported_events.append(
            ImportedProviderInvocationTraceEvent(
                event_id=event_id,
                correlation_id=event_correlation_id,
                sequence=sequence,
                event_type=event_type_value,
                lifecycle_state=lifecycle_value,
                issue_codes=tuple(issue_codes),
                provider_id=provider_id,
                capability_id=capability_id,
                operation_id=operation_id,
                provider_execution_reported=provider_reported,
                execution_independently_verified=independently_verified,
                details=MappingProxyType(details),
            )
        )

    return ImportedProviderInvocationTrace(
        correlation_id=correlation_id,
        events=tuple(imported_events),
    )


def _validate_event_semantics(
    event_type: TraceEventType,
    lifecycle_state: InvocationLifecycleState,
    issue_codes: tuple[str, ...],
    provider_reported: bool,
    previous_lifecycle_state: InvocationLifecycleState | None,
    result_event_seen: bool,
    path: str,
) -> tuple[InvocationLifecycleState | None, bool]:
    if result_event_seen:
        _error(
            "invalid_event_order",
            path,
            "no events may follow a result-validation event.",
        )

    if event_type is TraceEventType.LIFECYCLE_STATE:
        if issue_codes:
            _error(
                "invalid_event_semantics",
                f"{path}.issue_codes",
                "lifecycle-state events cannot contain issue codes.",
            )
        if provider_reported:
            _error(
                "invalid_event_semantics",
                f"{path}.provider_execution_reported",
                "execution claims are permitted only on result-validation events.",
            )
        if previous_lifecycle_state is None:
            if lifecycle_state is not InvocationLifecycleState.REQUEST_RECEIVED:
                _error(
                    "invalid_event_order",
                    f"{path}.lifecycle_state",
                    "the first lifecycle-state event must be request_received.",
                )
        elif not is_valid_invocation_lifecycle_transition(
            previous_lifecycle_state, lifecycle_state
        ):
            _error(
                "invalid_event_order",
                f"{path}.lifecycle_state",
                "lifecycle state does not follow the canonical transition contract.",
            )
        return lifecycle_state, result_event_seen

    if event_type is TraceEventType.ISSUE_REPORTED:
        if len(issue_codes) != 1:
            _error(
                "invalid_event_semantics",
                f"{path}.issue_codes",
                "issue events must contain exactly one canonical issue code.",
            )
        if provider_reported:
            _error(
                "invalid_event_semantics",
                f"{path}.provider_execution_reported",
                "execution claims are permitted only on result-validation events.",
            )
        if (
            previous_lifecycle_state is None
            or lifecycle_state is not previous_lifecycle_state
        ):
            _error(
                "invalid_event_order",
                f"{path}.lifecycle_state",
                "issue event state must match the latest lifecycle-state event.",
            )
        return previous_lifecycle_state, result_event_seen

    if issue_codes:
        _error(
            "invalid_event_semantics",
            f"{path}.issue_codes",
            "result-validation events cannot contain issue codes.",
        )
    if (
        previous_lifecycle_state
        is not InvocationLifecycleState.COMPLETED_WITH_VALIDATED_RESULT
        or lifecycle_state is not previous_lifecycle_state
    ):
        _error(
            "invalid_event_order",
            f"{path}.lifecycle_state",
            "result validation requires the completed lifecycle state.",
        )
    return previous_lifecycle_state, True


def _validate_details(value: object, path: str) -> dict[str, str | int]:
    details = _require_mapping(value, path)
    if any(type(key) is not str or key not in _DETAIL_FIELDS for key in details):
        _error(
            "unexpected_field",
            path,
            "details contain a field outside the canonical allowlist.",
        )
    validated: dict[str, str | int] = {}
    for key in sorted(details):
        item = details[key]
        item_path = f"{path}.{key}"
        if key == "candidate_count":
            if type(item) is not int or item < 0:
                _error(
                    "invalid_value",
                    item_path,
                    "candidate_count must be a non-negative integer.",
                )
        elif key == "reason_code":
            if not _is_identifier(item):
                _error(
                    "invalid_value",
                    item_path,
                    "reason_code must be a canonical structured identifier.",
                )
        elif key == "resolution_status":
            if type(item) is not str or item not in _RESOLUTION_STATUS_VALUES:
                _error(
                    "invalid_value",
                    item_path,
                    "resolution_status must be a canonical resolver status.",
                )
        validated[key] = item
    return validated


def _require_mapping(value: object, path: str) -> Mapping[str, object]:
    if type(value) not in (dict, MappingProxyType):
        _error(
            "invalid_type",
            path,
            "expected a built-in dictionary or read-only mapping proxy.",
        )
    return value


def _require_exact_fields(
    mapping: Mapping[str, object], expected_fields: frozenset[str], path: str
) -> None:
    keys = tuple(mapping.keys())
    if any(type(key) is not str for key in keys):
        _error("invalid_field_name", path, "mapping field names must be strings.")
    actual_fields = frozenset(keys)
    missing = expected_fields - actual_fields
    unexpected = actual_fields - expected_fields
    if missing:
        _error(
            "missing_field",
            path,
            f"required field {sorted(missing)[0]!r} is missing.",
        )
    if unexpected:
        _error(
            "unexpected_field",
            path,
            f"field {sorted(unexpected)[0]!r} is not part of the export schema.",
        )


def _require_uuid(value: object, path: str) -> str:
    if type(value) is not str or not _UUID_PATTERN.fullmatch(value):
        _error(
            "invalid_identifier",
            path,
            "value must be a lowercase canonical UUID.",
        )
    return value


def _optional_identifier(value: object, path: str) -> str | None:
    if value is None:
        return None
    if not _is_identifier(value):
        _error(
            "invalid_identifier",
            path,
            "value must be a canonical identifier or null.",
        )
    return value


def _is_identifier(value: object) -> bool:
    return type(value) is str and bool(_IDENTIFIER_PATTERN.fullmatch(value))


def _require_enum_value(
    value: object, allowed_values: frozenset[str], path: str
) -> str:
    if type(value) is not str or value not in allowed_values:
        _error(
            "invalid_enum_value",
            path,
            "value is not defined by the canonical contract.",
        )
    return value


def _error(code: str, path: str, message: str) -> None:
    raise ProviderInvocationTraceImportError(code, path, message)

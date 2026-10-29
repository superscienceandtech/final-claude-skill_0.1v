"""Deterministic, provider-neutral export of invocation trace snapshots.

The exported records contain only lifecycle metadata. Export is not
authorization to transmit data and does not verify provider execution or output.
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
)
from scripts.provider_invocation_trace import (
    ProviderInvocationTrace,
    ProviderInvocationTraceEvent,
    TraceEventType,
)


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")
_DETAIL_FIELD_NAMES = frozenset(
    {"candidate_count", "reason_code", "resolution_status"}
)
_ISSUE_CODE_VALUES = frozenset(code.value for code in InvocationLifecycleIssueCode)
_RESOLUTION_STATUS_VALUES = frozenset(
    status.value for status in CapabilityResolutionStatus
)
_UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z"
)


class ProviderInvocationTraceExportError(ValueError):
    """Raised when a trace cannot be represented by the export contract."""


@dataclass(frozen=True, slots=True)
class ProviderInvocationTraceEventExport:
    """Immutable serialization-safe representation of one canonical event."""

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
        """Return a fresh plain-data structure suitable for explicit encoding."""
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
class ProviderInvocationTraceExport:
    """Immutable export snapshot preserving the canonical event order."""

    correlation_id: str
    events: tuple[ProviderInvocationTraceEventExport, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a fresh plain-data structure suitable for explicit encoding."""
        return {
            "correlation_id": self.correlation_id,
            "events": [event.to_dict() for event in self.events],
        }


def export_provider_invocation_trace(
    trace: ProviderInvocationTrace,
) -> ProviderInvocationTraceExport:
    """Convert a canonical trace snapshot to immutable, deterministic data.

    Event order is copied exactly as supplied by the canonical trace. Only
    allowlisted trace details and explicit event fields are included.
    """
    if type(trace) is not ProviderInvocationTrace:
        raise ProviderInvocationTraceExportError(
            "trace must use the canonical ProviderInvocationTrace type."
        )
    if type(trace.correlation_id) is not str or not _UUID_PATTERN.fullmatch(
        trace.correlation_id
    ):
        raise ProviderInvocationTraceExportError(
            "trace correlation identifier must be a canonical UUID."
        )
    if type(trace.events) is not tuple:
        raise ProviderInvocationTraceExportError(
            "trace events must be an immutable tuple."
        )

    exported_events: list[ProviderInvocationTraceEventExport] = []
    expected_sequence = 1
    for event in trace.events:
        _validate_event(event, trace.correlation_id, expected_sequence)
        exported_events.append(
            ProviderInvocationTraceEventExport(
                event_id=event.event_id,
                correlation_id=event.correlation_id,
                sequence=event.sequence,
                event_type=event.event_type.value,
                lifecycle_state=event.lifecycle_state.value,
                issue_codes=tuple(event.issue_codes),
                provider_id=event.provider_id,
                capability_id=event.capability_id,
                operation_id=event.operation_id,
                provider_execution_reported=event.provider_execution_reported,
                execution_independently_verified=(
                    event.execution_independently_verified
                ),
                details=MappingProxyType(_validated_details(event.details)),
            )
        )
        expected_sequence += 1
    return ProviderInvocationTraceExport(
        correlation_id=trace.correlation_id,
        events=tuple(exported_events),
    )


def _validate_event(
    event: object, correlation_id: str, expected_sequence: int
) -> None:
    if type(event) is not ProviderInvocationTraceEvent:
        raise ProviderInvocationTraceExportError(
            "each trace event must use the canonical event type."
        )
    if type(event.event_type) is not TraceEventType:
        raise ProviderInvocationTraceExportError(
            "trace event type must use the canonical event enum."
        )
    if type(event.lifecycle_state) is not InvocationLifecycleState:
        raise ProviderInvocationTraceExportError(
            "trace lifecycle state must use the canonical state enum."
        )
    if (
        type(event.event_id) is not str
        or event.event_id != f"{correlation_id}:{expected_sequence}"
        or type(event.correlation_id) is not str
        or event.correlation_id != correlation_id
        or type(event.sequence) is not int
        or event.sequence != expected_sequence
    ):
        raise ProviderInvocationTraceExportError(
            "trace event identifiers and sequence must match canonical ordering."
        )
    for name in ("provider_id", "capability_id", "operation_id"):
        value = getattr(event, name)
        if value is not None and not _is_identifier(value):
            raise ProviderInvocationTraceExportError(
                f"trace event {name} must be a canonical identifier or None."
            )
    if type(event.issue_codes) is not tuple or any(
        type(code) is not str or code not in _ISSUE_CODE_VALUES
        for code in event.issue_codes
    ):
        raise ProviderInvocationTraceExportError(
            "trace event issue codes must be canonical structured identifiers."
        )
    if (
        type(event.provider_execution_reported) is not bool
        or type(event.execution_independently_verified) is not bool
    ):
        raise ProviderInvocationTraceExportError(
            "trace execution indicators must be booleans."
        )
    _validated_details(event.details)


def _validated_details(
    details: object,
) -> dict[str, str | int]:
    if type(details) not in (dict, MappingProxyType):
        raise ProviderInvocationTraceExportError(
            "trace event details must use the recorder's immutable mapping form."
        )
    if any(type(key) is not str or key not in _DETAIL_FIELD_NAMES for key in details):
        raise ProviderInvocationTraceExportError(
            "trace event details contain a field outside the export allowlist."
        )
    copied: dict[str, str | int] = {}
    for key in sorted(details):
        value = details[key]
        if key == "candidate_count":
            if type(value) is not int or value < 0:
                raise ProviderInvocationTraceExportError(
                    "candidate_count must be a non-negative integer."
                )
        elif key == "reason_code":
            if type(value) is not str or not _IDENTIFIER_PATTERN.fullmatch(value):
                raise ProviderInvocationTraceExportError(
                    "reason_code must be a canonical structured identifier."
                )
        elif key == "resolution_status":
            if type(value) is not str or value not in _RESOLUTION_STATUS_VALUES:
                raise ProviderInvocationTraceExportError(
                    "resolution_status must use a canonical resolver status."
                )
        copied[key] = value
    return copied


def _is_identifier(value: object) -> bool:
    return type(value) is str and bool(_IDENTIFIER_PATTERN.fullmatch(value))

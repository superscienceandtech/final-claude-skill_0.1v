"""Validation and immutable snapshots for canonical provider invocation results.

The canonical status, execution-state, error, provenance, and result types remain
defined in ``provider_adapter``. Validation does not verify provider-reported
success, output correctness, or execution state.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, replace
from datetime import datetime
from math import isfinite
from types import MappingProxyType
from typing import Mapping

from scripts.provider_adapter import (
    ExecutionState,
    InvocationProvenance,
    InvocationStatus,
    ProviderInvocationError,
    ProviderInvocationResult,
)
from scripts.provider_invocation import ProviderInvocation


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")
_VERSION_PATTERN = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z"
)


class ProviderInvocationResultValidationError(ValueError):
    """Raised when a result or its optional request relationship is invalid."""


@dataclass(frozen=True, slots=True)
class ProviderInvocationResultRecord:
    """Canonical adapter outcome plus the request capability when available.

    The outcome remains the canonical ``ProviderInvocationResult``; this record
    adds only the capability identifier absent from that adapter result type.
    """

    outcome: ProviderInvocationResult
    capability_id: str | None = None

    def __post_init__(self) -> None:
        if type(self.outcome) is not ProviderInvocationResult:
            raise ProviderInvocationResultValidationError(
                "outcome must use the canonical ProviderInvocationResult type."
            )
        if self.capability_id is not None and (
            not isinstance(self.capability_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(self.capability_id)
        ):
            raise ProviderInvocationResultValidationError(
                "capability_id must be a valid canonical identifier or None."
            )


def _freeze_value(value: object, active_ids: set[int]) -> object:
    value_type = type(value)
    if value is None or value_type in (str, bool, int):
        return value
    if value_type is float:
        if not isfinite(value):
            raise ProviderInvocationResultValidationError(
                "result output numbers must be finite."
            )
        return value
    if value_type in (dict, list, tuple):
        value_id = id(value)
        if value_id in active_ids:
            raise ProviderInvocationResultValidationError(
                "result output must not contain cyclic data."
            )
        active_ids.add(value_id)
        try:
            if value_type is dict:
                if any(type(key) is not str or not key.strip() for key in value):
                    raise ProviderInvocationResultValidationError(
                        "result output object keys must be non-empty strings."
                    )
                return MappingProxyType(
                    {
                        key: _freeze_value(value[key], active_ids)
                        for key in sorted(value)
                    }
                )
            return tuple(_freeze_value(item, active_ids) for item in value)
        finally:
            active_ids.remove(value_id)
    if value_type is MappingProxyType:
        value_id = id(value)
        if value_id in active_ids:
            raise ProviderInvocationResultValidationError(
                "result output must not contain cyclic data."
            )
        active_ids.add(value_id)
        try:
            if any(type(key) is not str or not key.strip() for key in value):
                raise ProviderInvocationResultValidationError(
                    "result output object keys must be non-empty strings."
                )
            return MappingProxyType(
                {
                    key: _freeze_value(value[key], active_ids)
                    for key in sorted(value)
                }
            )
        finally:
            active_ids.remove(value_id)
    raise ProviderInvocationResultValidationError(
        "result output must use supported built-in data types."
    )


def _canonical_uuid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return str(parsed) == value.lower() and value == value.lower()


def _aware_datetime(value: object) -> bool:
    return (
        type(value) is datetime
        and value.tzinfo is not None
        and value.utcoffset() is not None
    )


def validate_provider_invocation_result(
    result: ProviderInvocationResult,
    request: ProviderInvocation | None = None,
    *,
    capability_id: str | None = None,
) -> ProviderInvocationResultRecord:
    """Validate an outcome and return its deep-frozen canonical result record.

    When ``request`` is provided, request ID and operation must match, and
    provider and trace identifiers must match when the request supplied them.
    The request supplies the capability identifier when ``capability_id`` is
    omitted; neither value is inferred from provider metadata.
    This function preserves provider-reported outcome and execution state without
    treating either as independently verified.
    """
    if type(result) is not ProviderInvocationResult:
        raise ProviderInvocationResultValidationError(
            "result must use the canonical ProviderInvocationResult type."
        )
    if request is not None and type(request) is not ProviderInvocation:
        raise ProviderInvocationResultValidationError(
            "request must use the canonical ProviderInvocation type or be None."
        )
    if capability_id is not None and (
        not isinstance(capability_id, str)
        or not _IDENTIFIER_PATTERN.fullmatch(capability_id)
    ):
        raise ProviderInvocationResultValidationError(
            "capability_id must be a valid canonical identifier or None."
        )
    if request is not None:
        if (
            not isinstance(request.capability_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(request.capability_id)
            or not isinstance(request.operation_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(request.operation_id)
            or not _canonical_uuid(request.request_id)
            or (
                request.provider_id is not None
                and (
                    not isinstance(request.provider_id, str)
                    or not _IDENTIFIER_PATTERN.fullmatch(request.provider_id)
                )
            )
        ):
            raise ProviderInvocationResultValidationError(
                "request identifiers are malformed."
            )
        if capability_id is not None and capability_id != request.capability_id:
            raise ProviderInvocationResultValidationError(
                "capability identifier does not match the invocation request."
            )
        capability_id = request.capability_id

    if type(result.status) is not InvocationStatus:
        raise ProviderInvocationResultValidationError(
            "result status must be a canonical InvocationStatus."
        )
    if type(result.execution_state) is not ExecutionState:
        raise ProviderInvocationResultValidationError(
            "execution_state must be a canonical ExecutionState."
        )

    provenance = result.provenance
    if type(provenance) is not InvocationProvenance:
        raise ProviderInvocationResultValidationError(
            "provenance must use the canonical InvocationProvenance type."
        )
    for field_name in ("provider_id", "adapter_id", "operation_id"):
        value = getattr(provenance, field_name)
        if not isinstance(value, str) or not _IDENTIFIER_PATTERN.fullmatch(value):
            raise ProviderInvocationResultValidationError(
                f"provenance {field_name} must be a valid canonical identifier."
            )
    if not isinstance(provenance.contract_version, str) or not _VERSION_PATTERN.fullmatch(
        provenance.contract_version
    ):
        raise ProviderInvocationResultValidationError(
            "provenance contract_version must use numeric major.minor.patch format."
        )
    if not _canonical_uuid(provenance.request_id):
        raise ProviderInvocationResultValidationError(
            "provenance request_id must be a canonical UUID."
        )
    if provenance.trace_id is not None and (
        not isinstance(provenance.trace_id, str) or not provenance.trace_id.strip()
    ):
        raise ProviderInvocationResultValidationError(
            "provenance trace_id must be non-empty when supplied."
        )
    if not _aware_datetime(provenance.started_at) or not _aware_datetime(
        provenance.completed_at
    ):
        raise ProviderInvocationResultValidationError(
            "provenance timestamps must be timezone-aware."
        )

    if result.status is InvocationStatus.SUCCEEDED:
        if result.error is not None or type(result.output) not in (
            dict,
            MappingProxyType,
        ):
            raise ProviderInvocationResultValidationError(
                "successful results require structured output and no error."
            )
    elif result.error is None or result.output is not None:
        raise ProviderInvocationResultValidationError(
            "unsuccessful results require an error and must not expose output."
        )

    error_snapshot: ProviderInvocationError | None = None
    if result.error is not None:
        if type(result.error) is not ProviderInvocationError:
            raise ProviderInvocationResultValidationError(
                "error must use the canonical ProviderInvocationError type."
            )
        if (
            not isinstance(result.error.code, str)
            or not _IDENTIFIER_PATTERN.fullmatch(result.error.code)
            or not isinstance(result.error.message, str)
            or not result.error.message.strip()
            or not isinstance(result.error.retryable, bool)
        ):
            raise ProviderInvocationResultValidationError(
                "error code, message, or retryable flag is invalid."
            )
        try:
            error_snapshot = replace(result.error)
        except (TypeError, ValueError, AttributeError) as error:
            raise ProviderInvocationResultValidationError(
                "error structure is malformed."
            ) from error

    output_snapshot: Mapping[str, object] | None = None
    if result.output is not None:
        frozen = _freeze_value(result.output, set())
        if type(frozen) is not MappingProxyType:
            raise ProviderInvocationResultValidationError(
                "result output must be an object mapping."
            )
        output_snapshot = frozen

    if request is not None:
        if provenance.request_id != request.request_id:
            raise ProviderInvocationResultValidationError(
                "result request identifier does not match the invocation request."
            )
        if provenance.operation_id != request.operation_id:
            raise ProviderInvocationResultValidationError(
                "result operation identifier does not match the invocation request."
            )
        if request.provider_id is not None and (
            provenance.provider_id != request.provider_id
        ):
            raise ProviderInvocationResultValidationError(
                "result provider identifier does not match the invocation request."
            )
        if request.trace_id is not None and provenance.trace_id is not None and (
            provenance.trace_id != request.trace_id
        ):
            raise ProviderInvocationResultValidationError(
                "result trace identifier does not match the invocation request."
            )

    try:
        provenance_snapshot = replace(provenance)
        result_snapshot = replace(
            result,
            provenance=provenance_snapshot,
            output=output_snapshot,
            error=error_snapshot,
        )
        return ProviderInvocationResultRecord(
            outcome=result_snapshot,
            capability_id=capability_id,
        )
    except (TypeError, ValueError, AttributeError) as error:
        raise ProviderInvocationResultValidationError(
            "result could not be copied into a validated immutable snapshot."
        ) from error

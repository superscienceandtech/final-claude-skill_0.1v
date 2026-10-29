"""Immutable, provider-neutral descriptions of proposed provider invocations.

Constructing a request does not resolve a provider, authorize an operation, or
invoke an adapter. Payload and context values are limited to recursively frozen
built-in data types so validation does not call arbitrary input-object methods.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, replace
from math import isfinite
from types import MappingProxyType
from typing import Mapping

from scripts.provider_adapter import (
    AuthorizationGrant,
    CancellationToken,
    ExecutionContext,
)


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")
_UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z"
)


class ProviderInvocationValidationError(ValueError):
    """Raised when a proposed invocation request is structurally invalid."""


def _freeze_value(value: object, active_ids: set[int]) -> object:
    value_type = type(value)
    if value is None or value_type in (str, bool, int):
        return value
    if value_type is float:
        if not isfinite(value):
            raise ProviderInvocationValidationError(
                "payload and context numbers must be finite."
            )
        return value
    if value_type in (dict, list, tuple):
        value_id = id(value)
        if value_id in active_ids:
            raise ProviderInvocationValidationError(
                "payload and context must not contain cyclic data."
            )
        active_ids.add(value_id)
        try:
            if value_type is dict:
                if any(type(key) is not str for key in value):
                    raise ProviderInvocationValidationError(
                        "payload and context object keys must be strings."
                    )
                frozen = {
                    key: _freeze_value(value[key], active_ids)
                    for key in sorted(value)
                }
                return MappingProxyType(frozen)
            return tuple(_freeze_value(item, active_ids) for item in value)
        finally:
            active_ids.remove(value_id)
    raise ProviderInvocationValidationError(
        "payload and context values must use supported built-in data types."
    )


def _freeze_object_mapping(values: object, label: str) -> Mapping[str, object]:
    if type(values) is not dict and type(values) is not MappingProxyType:
        raise ProviderInvocationValidationError(
            f"{label} must be a plain dictionary or immutable mapping."
        )
    if any(type(key) is not str or not key.strip() for key in values):
        raise ProviderInvocationValidationError(
            f"{label} keys must be non-empty strings."
        )
    frozen = _freeze_value(dict(values), set())
    if type(frozen) is not MappingProxyType:
        raise ProviderInvocationValidationError(
            f"{label} must be an object mapping."
        )
    return frozen


@dataclass(frozen=True, slots=True)
class ProviderInvocation:
    """Validated request describing a proposed provider operation.

    ``provider_id`` may be omitted when a later caller will resolve candidates.
    Capability/operation compatibility and authorization remain separate steps.
    A supplied cancellation token remains a mutable cooperative signal; changing
    its state does not alter the request's declared invocation parameters.
    """

    capability_id: str
    operation_id: str
    inputs: Mapping[str, object]
    provider_id: str | None = None
    context: ExecutionContext = field(default_factory=ExecutionContext)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str | None = None
    timeout_seconds: float | None = None
    cancellation: CancellationToken | None = None

    def __post_init__(self) -> None:
        for field_name in ("capability_id", "operation_id"):
            identifier = getattr(self, field_name)
            if (
                not isinstance(identifier, str)
                or not _IDENTIFIER_PATTERN.fullmatch(identifier)
            ):
                raise ProviderInvocationValidationError(
                    f"{field_name} must be a valid canonical identifier."
                )
        if self.provider_id is not None and (
            not isinstance(self.provider_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(self.provider_id)
        ):
            raise ProviderInvocationValidationError(
                "provider_id must be a valid canonical identifier or None."
            )
        if not isinstance(self.request_id, str) or not _UUID_PATTERN.fullmatch(
            self.request_id
        ):
            raise ProviderInvocationValidationError(
                "request_id must be a lowercase canonical UUID."
            )
        if self.trace_id is not None and (
            not isinstance(self.trace_id, str) or not self.trace_id.strip()
        ):
            raise ProviderInvocationValidationError(
                "trace_id must be a non-empty string or None."
            )
        timeout_is_valid = (
            isinstance(self.timeout_seconds, int)
            and not isinstance(self.timeout_seconds, bool)
            and self.timeout_seconds > 0
        ) or (
            type(self.timeout_seconds) is float
            and self.timeout_seconds > 0
            and isfinite(self.timeout_seconds)
        )
        if self.timeout_seconds is not None and not timeout_is_valid:
            raise ProviderInvocationValidationError(
                "timeout_seconds must be finite and greater than zero."
            )
        if self.cancellation is not None and type(self.cancellation) is not CancellationToken:
            raise ProviderInvocationValidationError(
                "cancellation must be a canonical CancellationToken or None."
            )
        if type(self.context) is not ExecutionContext:
            raise ProviderInvocationValidationError(
                "context must be a canonical ExecutionContext."
            )

        inputs = _freeze_object_mapping(self.inputs, "inputs")
        try:
            context_values = object.__getattribute__(self.context, "values")
            grants = object.__getattribute__(
                self.context, "authorization_grants"
            )
        except AttributeError as error:
            raise ProviderInvocationValidationError(
                "context is missing canonical execution-context data."
            ) from error
        frozen_context_values = _freeze_object_mapping(context_values, "context values")
        if type(grants) is not tuple:
            raise ProviderInvocationValidationError(
                "context authorization grants must be a tuple."
            )
        if any(type(grant) is not AuthorizationGrant for grant in grants):
            raise ProviderInvocationValidationError(
                "context authorization grants must use the canonical contract type."
            )
        try:
            copied_grants = tuple(replace(grant) for grant in grants)
            frozen_context = ExecutionContext(
                values=frozen_context_values,
                authorization_grants=copied_grants,
            )
        except (TypeError, ValueError, AttributeError) as error:
            raise ProviderInvocationValidationError(
                "context authorization grants are malformed."
            ) from error

        object.__setattr__(self, "inputs", inputs)
        object.__setattr__(self, "context", frozen_context)

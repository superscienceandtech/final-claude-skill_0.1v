"""Provider-neutral contracts for explicitly supplied provider adapters.

This module defines metadata, capability and operation declarations, invocation
validation, authorization context, and structured outcomes. It does not discover
credentials, access the network or filesystem, execute shell commands, load
provider implementations, or independently verify provider claims.
"""

from __future__ import annotations

import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from threading import Event, Lock
from types import MappingProxyType
from typing import Mapping


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")
_VERSION_PATTERN = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z"
)


class ProviderAdapterContractError(ValueError):
    """Raised when adapter metadata or declarations violate this contract."""


class ProviderAdapterExecutionError(Exception):
    """Safe, structured failure raised by an adapter implementation."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        if not isinstance(code, str) or not _IDENTIFIER_PATTERN.fullmatch(code):
            raise ProviderAdapterContractError("error code must be a valid identifier.")
        if not isinstance(message, str) or not message.strip():
            raise ProviderAdapterContractError("error message must not be empty.")
        if not isinstance(retryable, bool):
            raise ProviderAdapterContractError("retryable must be a boolean.")
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


class ProviderAdapterTimeoutError(ProviderAdapterExecutionError):
    """Raised when an adapter-enforced operation timeout expires."""

    def __init__(self, message: str = "operation timed out.") -> None:
        super().__init__("operation_timed_out", message)


class ProviderAdapterCancelledError(ProviderAdapterExecutionError):
    """Raised when an adapter honors a cooperative cancellation request."""

    def __init__(self, message: str = "operation was cancelled.") -> None:
        super().__init__("operation_cancelled", message)


class AdapterAvailability(str, Enum):
    DECLARED = "declared"
    READY = "ready"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"


class OperationEffect(str, Enum):
    READ_ONLY = "read_only"
    REPOSITORY_MUTATION = "repository_mutation"
    EXTERNAL_EFFECT = "external_effect"


class CapabilityEvidenceState(str, Enum):
    DECLARED = "declared"
    VERIFICATION_EVIDENCE_REPORTED = "verification_evidence_reported"


class InvocationStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNSUPPORTED = "unsupported"
    REJECTED = "rejected"
    UNAVAILABLE = "unavailable"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class ExecutionState(str, Enum):
    NOT_EXECUTED = "not_executed"
    EXECUTED = "executed"
    UNKNOWN = "unknown"


class ProviderValueType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


@dataclass(frozen=True, slots=True)
class ProviderIdentity:
    """Provider-neutral identity; the identifier is not restricted to vendors."""

    identifier: str
    display_name: str
    version: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.identifier
        ):
            raise ProviderAdapterContractError(
                "provider identifier must be a lowercase identifier."
            )
        if not isinstance(self.display_name, str) or not self.display_name.strip():
            raise ProviderAdapterContractError("provider display_name must not be empty.")
        if self.version is not None and (
            not isinstance(self.version, str) or not self.version.strip()
        ):
            raise ProviderAdapterContractError(
                "provider version must be a non-empty string when supplied."
            )


@dataclass(frozen=True, slots=True)
class AdapterMetadata:
    """Identity and version information for one explicitly supplied adapter."""

    provider: ProviderIdentity
    adapter_id: str
    contract_version: str
    implementation_version: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.provider, ProviderIdentity):
            raise ProviderAdapterContractError("provider must be a ProviderIdentity.")
        if not isinstance(self.adapter_id, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.adapter_id
        ):
            raise ProviderAdapterContractError("adapter_id must be a valid identifier.")
        if not isinstance(self.contract_version, str) or not _VERSION_PATTERN.fullmatch(
            self.contract_version
        ):
            raise ProviderAdapterContractError(
                "contract_version must use numeric major.minor.patch format."
            )
        if self.implementation_version is not None and (
            not isinstance(self.implementation_version, str)
            or not self.implementation_version.strip()
        ):
            raise ProviderAdapterContractError(
                "implementation_version must be non-empty when supplied."
            )


@dataclass(frozen=True, slots=True)
class ProviderDataField:
    """One shallowly validated field in a provider-neutral data contract."""

    name: str
    value_type: ProviderValueType
    required: bool = True
    nullable: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _IDENTIFIER_PATTERN.fullmatch(self.name):
            raise ProviderAdapterContractError("data field name must be a valid identifier.")
        if not isinstance(self.value_type, ProviderValueType):
            raise ProviderAdapterContractError("value_type must be a ProviderValueType.")
        if not isinstance(self.required, bool) or not isinstance(self.nullable, bool):
            raise ProviderAdapterContractError("required and nullable must be booleans.")


def _matches_value_type(value_type: ProviderValueType, value: object) -> bool:
    if value_type is ProviderValueType.STRING:
        return isinstance(value, str)
    if value_type is ProviderValueType.INTEGER:
        return isinstance(value, int) and not isinstance(value, bool)
    if value_type is ProviderValueType.NUMBER:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and isfinite(value)
        )
    if value_type is ProviderValueType.BOOLEAN:
        return isinstance(value, bool)
    if value_type is ProviderValueType.OBJECT:
        return isinstance(value, Mapping)
    if value_type is ProviderValueType.ARRAY:
        return isinstance(value, (list, tuple))
    return False


@dataclass(frozen=True, slots=True)
class ProviderDataContract:
    """Shallow object schema for operation inputs or outputs."""

    fields: tuple[ProviderDataField, ...] = ()
    allow_additional_fields: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.fields, tuple) or any(
            not isinstance(item, ProviderDataField) for item in self.fields
        ):
            raise ProviderAdapterContractError(
                "fields must be a tuple of ProviderDataField values."
            )
        names = [item.name for item in self.fields]
        if len(names) != len(set(names)):
            raise ProviderAdapterContractError("data contract contains duplicate fields.")
        if not isinstance(self.allow_additional_fields, bool):
            raise ProviderAdapterContractError("allow_additional_fields must be a boolean.")

    def validate(self, values: Mapping[str, object]) -> str | None:
        """Return a stable validation error code, or None when valid."""
        if not isinstance(values, Mapping) or any(
            not isinstance(name, str) or not name.strip() for name in values
        ):
            return "invalid_data_object"
        declared = {item.name: item for item in self.fields}
        if any(item.required and item.name not in values for item in self.fields):
            return "missing_required_field"
        if not self.allow_additional_fields and set(values).difference(declared):
            return "unexpected_field"
        for name, value in values.items():
            item = declared.get(name)
            if item is None:
                continue
            if value is None:
                if not item.nullable:
                    return "null_not_allowed"
            elif not _matches_value_type(item.value_type, value):
                return "invalid_field_type"
        return None


@dataclass(frozen=True, slots=True)
class CapabilityVerification:
    """Reference supplied with a capability verification claim.

    The reference is metadata, not independent proof that verification occurred.
    """

    evidence_reference: str
    scope: str

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_reference, str) or not self.evidence_reference.strip():
            raise ProviderAdapterContractError("evidence_reference must not be empty.")
        if not isinstance(self.scope, str) or not self.scope.strip():
            raise ProviderAdapterContractError("verification scope must not be empty.")


@dataclass(frozen=True, slots=True)
class CapabilityDeclaration:
    """Capability declaration with optional, explicitly scoped evidence metadata."""

    identifier: str
    description: str
    verification: CapabilityVerification | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.identifier
        ):
            raise ProviderAdapterContractError("capability identifier must be valid.")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ProviderAdapterContractError("capability description must not be empty.")
        if self.verification is not None and not isinstance(
            self.verification, CapabilityVerification
        ):
            raise ProviderAdapterContractError(
                "verification must be a CapabilityVerification or None."
            )

    @property
    def evidence_state(self) -> CapabilityEvidenceState:
        if self.verification is None:
            return CapabilityEvidenceState.DECLARED
        return CapabilityEvidenceState.VERIFICATION_EVIDENCE_REPORTED


@dataclass(frozen=True, slots=True)
class ProviderOperation:
    """One declared provider-neutral operation and its execution constraints."""

    identifier: str
    description: str
    capability_ids: tuple[str, ...]
    input_contract: ProviderDataContract
    output_contract: ProviderDataContract
    required_context: tuple[str, ...] = ()
    required_permissions: tuple[str, ...] = ()
    effect: OperationEffect = OperationEffect.READ_ONLY
    supports_timeout: bool = False
    supports_cancellation: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.identifier
        ):
            raise ProviderAdapterContractError("operation identifier must be valid.")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ProviderAdapterContractError("operation description must not be empty.")
        for field_name in ("capability_ids", "required_context", "required_permissions"):
            values = getattr(self, field_name)
            if not isinstance(values, tuple) or any(
                not isinstance(value, str) or not _IDENTIFIER_PATTERN.fullmatch(value)
                for value in values
            ):
                raise ProviderAdapterContractError(
                    f"{field_name} must be a tuple of valid identifiers."
                )
            if len(values) != len(set(values)):
                raise ProviderAdapterContractError(f"{field_name} contains duplicates.")
        if not isinstance(self.input_contract, ProviderDataContract) or not isinstance(
            self.output_contract, ProviderDataContract
        ):
            raise ProviderAdapterContractError(
                "input_contract and output_contract must be ProviderDataContract values."
            )
        if not isinstance(self.effect, OperationEffect):
            raise ProviderAdapterContractError("effect must be an OperationEffect.")
        if not isinstance(self.supports_timeout, bool) or not isinstance(
            self.supports_cancellation, bool
        ):
            raise ProviderAdapterContractError(
                "supports_timeout and supports_cancellation must be booleans."
            )


@dataclass(frozen=True, slots=True)
class ProviderAdapterDeclarations:
    """Validated immutable registration declarations from the adapter contract.

    Capability verification references remain reported evidence metadata; this
    object does not independently verify implementation or operational status.
    """

    metadata: AdapterMetadata
    capabilities: tuple[CapabilityDeclaration, ...]
    operations: tuple[ProviderOperation, ...]
    availability: AdapterAvailability

    def __post_init__(self) -> None:
        if type(self.metadata) is not AdapterMetadata:
            raise ProviderAdapterContractError("declarations require AdapterMetadata.")
        if type(self.metadata.provider) is not ProviderIdentity:
            raise ProviderAdapterContractError(
                "declarations require a valid ProviderIdentity."
            )
        if type(self.capabilities) is not tuple or any(
            type(item) is not CapabilityDeclaration for item in self.capabilities
        ):
            raise ProviderAdapterContractError(
                "capabilities must be a tuple of canonical CapabilityDeclaration values."
            )
        if type(self.operations) is not tuple or any(
            type(item) is not ProviderOperation for item in self.operations
        ):
            raise ProviderAdapterContractError(
                "operations must be a tuple of canonical ProviderOperation values."
            )
        if type(self.availability) is not AdapterAvailability:
            raise ProviderAdapterContractError(
                "availability must be an AdapterAvailability value."
            )
        capability_ids = [item.identifier for item in self.capabilities]
        operation_ids = [item.identifier for item in self.operations]
        if len(capability_ids) != len(set(capability_ids)):
            raise ProviderAdapterContractError(
                "capability identifiers must be unique."
            )
        if len(operation_ids) != len(set(operation_ids)):
            raise ProviderAdapterContractError("operation identifiers must be unique.")
        declared_capabilities = set(capability_ids)
        if any(
            not set(operation.capability_ids).issubset(declared_capabilities)
            for operation in self.operations
        ):
            raise ProviderAdapterContractError(
                "each operation capability must have a matching declaration."
            )


@dataclass(frozen=True, slots=True)
class AuthorizationGrant:
    """Caller-supplied authorization scoped to one provider operation."""

    provider_id: str
    operation_id: str
    permissions: tuple[str, ...]
    authority_reference: str

    def __post_init__(self) -> None:
        for field_name in ("provider_id", "operation_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not _IDENTIFIER_PATTERN.fullmatch(value):
                raise ProviderAdapterContractError(f"{field_name} must be a valid identifier.")
        if not isinstance(self.permissions, tuple) or any(
            not isinstance(value, str) or not _IDENTIFIER_PATTERN.fullmatch(value)
            for value in self.permissions
        ):
            raise ProviderAdapterContractError("permissions must be valid identifiers.")
        if len(self.permissions) != len(set(self.permissions)):
            raise ProviderAdapterContractError("permissions must not contain duplicates.")
        if (
            not isinstance(self.authority_reference, str)
            or not self.authority_reference.strip()
        ):
            raise ProviderAdapterContractError("authority_reference must not be empty.")


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    """Explicit, caller-provided context and scoped authorization grants."""

    values: Mapping[str, object] = field(default_factory=dict)
    authorization_grants: tuple[AuthorizationGrant, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.values, Mapping) or any(
            not isinstance(name, str) or not name.strip() for name in self.values
        ):
            raise ProviderAdapterContractError("context values must have non-empty string keys.")
        if not isinstance(self.authorization_grants, tuple) or any(
            not isinstance(grant, AuthorizationGrant)
            for grant in self.authorization_grants
        ):
            raise ProviderAdapterContractError(
                "authorization_grants must be a tuple of AuthorizationGrant values."
            )
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))


class CancellationToken:
    """Cooperative cancellation signal for adapters that declare support."""

    def __init__(self) -> None:
        self._event = Event()
        self._lock = Lock()

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> bool:
        """Set cancellation once; return whether this call changed its state."""
        with self._lock:
            if self._event.is_set():
                return False
            self._event.set()
            return True


@dataclass(frozen=True, slots=True)
class ProviderInvocationRequest:
    """Provider-independent invocation request; construction performs no I/O."""

    provider_id: str
    operation_id: str
    inputs: Mapping[str, object]
    context: ExecutionContext = field(default_factory=ExecutionContext)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str | None = None
    timeout_seconds: float | None = None
    cancellation: CancellationToken | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        for field_name in ("provider_id", "operation_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not _IDENTIFIER_PATTERN.fullmatch(value):
                raise ProviderAdapterContractError(f"{field_name} must be a valid identifier.")
        if not isinstance(self.inputs, Mapping) or any(
            not isinstance(name, str) or not name.strip() for name in self.inputs
        ):
            raise ProviderAdapterContractError("inputs must be a mapping with string keys.")
        if not isinstance(self.context, ExecutionContext):
            raise ProviderAdapterContractError("context must be an ExecutionContext.")
        try:
            parsed_request_id = uuid.UUID(self.request_id)
        except (ValueError, AttributeError, TypeError) as error:
            raise ProviderAdapterContractError("request_id must be a UUID.") from error
        if str(parsed_request_id) != self.request_id.lower():
            raise ProviderAdapterContractError("request_id must use canonical UUID format.")
        if self.trace_id is not None and (
            not isinstance(self.trace_id, str) or not self.trace_id.strip()
        ):
            raise ProviderAdapterContractError("trace_id must be non-empty when supplied.")
        if self.timeout_seconds is not None and (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or self.timeout_seconds <= 0
            or not isfinite(self.timeout_seconds)
        ):
            raise ProviderAdapterContractError("timeout_seconds must be positive.")
        if self.cancellation is not None and not isinstance(
            self.cancellation, CancellationToken
        ):
            raise ProviderAdapterContractError(
                "cancellation must be a CancellationToken or None."
            )
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise ProviderAdapterContractError("created_at must be timezone-aware.")
        object.__setattr__(self, "inputs", MappingProxyType(dict(self.inputs)))


@dataclass(frozen=True, slots=True)
class CompatibilityReport:
    """Compatibility result for the adapter contract version and optional operation."""

    compatible: bool
    requested_contract_version: str
    adapter_contract_version: str
    operation_id: str | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ProviderInvocationError:
    """Payload-free structured error suitable for reporting and audit metadata."""

    code: str
    message: str
    retryable: bool = False


@dataclass(frozen=True, slots=True)
class InvocationProvenance:
    """Provider, adapter, operation, and timing metadata for one invocation."""

    provider_id: str
    adapter_id: str
    contract_version: str
    operation_id: str
    request_id: str
    trace_id: str | None
    started_at: datetime
    completed_at: datetime


@dataclass(frozen=True, slots=True)
class ProviderInvocationResult:
    """Structured invocation outcome with explicit execution and provenance state."""

    status: InvocationStatus
    execution_state: ExecutionState
    provenance: InvocationProvenance
    output: Mapping[str, object] | None = None
    error: ProviderInvocationError | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, InvocationStatus) or not isinstance(
            self.execution_state, ExecutionState
        ):
            raise ProviderAdapterContractError("result status values are invalid.")
        if not isinstance(self.provenance, InvocationProvenance):
            raise ProviderAdapterContractError("provenance must be an InvocationProvenance.")
        if self.output is not None:
            if not isinstance(self.output, Mapping) or any(
                not isinstance(name, str) for name in self.output
            ):
                raise ProviderAdapterContractError("output must be a mapping or None.")
            object.__setattr__(self, "output", MappingProxyType(dict(self.output)))
        if self.error is not None and not isinstance(self.error, ProviderInvocationError):
            raise ProviderAdapterContractError(
                "error must be a ProviderInvocationError or None."
            )
        if (self.status is InvocationStatus.SUCCEEDED) != (self.error is None):
            raise ProviderAdapterContractError(
                "successful results must have no error; all other results require one."
            )
        if self.status is InvocationStatus.SUCCEEDED and self.output is None:
            raise ProviderAdapterContractError("successful results require an output mapping.")
        if self.status is not InvocationStatus.SUCCEEDED and self.output is not None:
            raise ProviderAdapterContractError("failed results must not expose output.")


class ProviderAdapter(ABC):
    """Provider-neutral contract implemented by separately supplied adapters."""

    def __init__(
        self,
        metadata: AdapterMetadata,
        capabilities: tuple[CapabilityDeclaration, ...],
        operations: tuple[ProviderOperation, ...],
        *,
        availability: AdapterAvailability = AdapterAvailability.UNAVAILABLE,
    ) -> None:
        if not isinstance(metadata, AdapterMetadata):
            raise ProviderAdapterContractError("metadata must be AdapterMetadata.")
        if not isinstance(capabilities, tuple) or any(
            not isinstance(item, CapabilityDeclaration) for item in capabilities
        ):
            raise ProviderAdapterContractError(
                "capabilities must be a tuple of CapabilityDeclaration values."
            )
        if not isinstance(operations, tuple) or any(
            not isinstance(item, ProviderOperation) for item in operations
        ):
            raise ProviderAdapterContractError(
                "operations must be a tuple of ProviderOperation values."
            )
        if not isinstance(availability, AdapterAvailability):
            raise ProviderAdapterContractError("availability must be an AdapterAvailability.")
        self._registration_declarations = ProviderAdapterDeclarations(
            metadata=metadata,
            capabilities=tuple(sorted(capabilities, key=lambda item: item.identifier)),
            operations=tuple(sorted(operations, key=lambda item: item.identifier)),
            availability=availability,
        )

    def get_registration_declarations(self) -> ProviderAdapterDeclarations:
        """Return the initialized immutable declarations without performing I/O.

        Registries should call this base implementation explicitly rather than
        dispatching to an adapter override during registration or discovery.
        """
        try:
            declarations = object.__getattribute__(
                self, "_registration_declarations"
            )
        except AttributeError as error:
            raise ProviderAdapterContractError(
                "adapter registration declarations are not initialized."
            ) from error
        if type(declarations) is not ProviderAdapterDeclarations:
            raise ProviderAdapterContractError(
                "adapter registration declarations are malformed."
            )
        try:
            return ProviderAdapterDeclarations(
                metadata=declarations.metadata,
                capabilities=declarations.capabilities,
                operations=declarations.operations,
                availability=declarations.availability,
            )
        except AttributeError as error:
            raise ProviderAdapterContractError(
                "adapter registration declarations are malformed."
            ) from error

    @property
    def metadata(self) -> AdapterMetadata:
        return self.get_registration_declarations().metadata

    @property
    def availability(self) -> AdapterAvailability:
        return self.get_registration_declarations().availability

    @property
    def capabilities(self) -> tuple[CapabilityDeclaration, ...]:
        return self.get_registration_declarations().capabilities

    @property
    def operations(self) -> tuple[ProviderOperation, ...]:
        return self.get_registration_declarations().operations

    def discover_capabilities(self) -> tuple[CapabilityDeclaration, ...]:
        """Return declarations only; this does not contact or execute a provider."""
        return self.capabilities

    def discover_operations(self) -> tuple[ProviderOperation, ...]:
        """Return declared operations only; unsupported operations remain unsupported."""
        return self.operations

    def check_compatibility(
        self, contract_version: str, operation_id: str | None = None
    ) -> CompatibilityReport:
        if not isinstance(contract_version, str) or not _VERSION_PATTERN.fullmatch(
            contract_version
        ):
            raise ProviderAdapterContractError(
                "contract_version must use numeric major.minor.patch format."
            )
        if operation_id is not None and (
            not isinstance(operation_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(operation_id)
        ):
            raise ProviderAdapterContractError("operation_id must be a valid identifier.")
        reason = None
        if contract_version != self.metadata.contract_version:
            reason = "contract_version_mismatch"
        elif operation_id is not None and not self.supports_operation(operation_id):
            reason = "operation_unsupported"
        return CompatibilityReport(
            compatible=reason is None,
            requested_contract_version=contract_version,
            adapter_contract_version=self.metadata.contract_version,
            operation_id=operation_id,
            reason=reason,
        )

    def supports_operation(self, operation_id: str) -> bool:
        return any(operation.identifier == operation_id for operation in self.operations)

    def invoke(self, request: ProviderInvocationRequest) -> ProviderInvocationResult:
        """Validate, authorize, and invoke one declared operation explicitly."""
        if not isinstance(request, ProviderInvocationRequest):
            raise ProviderAdapterContractError(
                "request must be a ProviderInvocationRequest."
            )
        started_at = datetime.now(timezone.utc)
        operation = next(
            (
                item
                for item in self.operations
                if item.identifier == request.operation_id
            ),
            None,
        )
        if request.provider_id != self.metadata.provider.identifier:
            return self._failure(
                request,
                started_at,
                InvocationStatus.REJECTED,
                "provider_mismatch",
                "request provider does not match this adapter.",
            )
        if operation is None:
            return self._failure(
                request,
                started_at,
                InvocationStatus.UNSUPPORTED,
                "operation_unsupported",
                "operation is not declared by this adapter.",
            )
        if self.availability is not AdapterAvailability.READY:
            return self._failure(
                request,
                started_at,
                InvocationStatus.UNAVAILABLE,
                "adapter_unavailable",
                "adapter is not marked ready for invocation.",
            )
        input_error = operation.input_contract.validate(request.inputs)
        if input_error is not None:
            return self._failure(
                request,
                started_at,
                InvocationStatus.REJECTED,
                input_error,
                "request inputs do not satisfy the operation contract.",
            )
        if any(key not in request.context.values for key in operation.required_context):
            return self._failure(
                request,
                started_at,
                InvocationStatus.REJECTED,
                "execution_context_missing",
                "required execution context is missing.",
            )
        if request.timeout_seconds is not None and not operation.supports_timeout:
            return self._failure(
                request,
                started_at,
                InvocationStatus.REJECTED,
                "timeout_unsupported",
                "operation does not declare timeout support.",
            )
        if request.cancellation is not None and not operation.supports_cancellation:
            return self._failure(
                request,
                started_at,
                InvocationStatus.REJECTED,
                "cancellation_unsupported",
                "operation does not declare cancellation support.",
            )
        if request.cancellation is not None and request.cancellation.is_cancelled:
            return self._failure(
                request,
                started_at,
                InvocationStatus.CANCELLED,
                "cancelled_before_execution",
                "cancellation was requested before operation execution.",
            )
        authorization_error = self._authorization_error(operation, request.context)
        if authorization_error is not None:
            return self._failure(
                request,
                started_at,
                InvocationStatus.REJECTED,
                authorization_error,
                "required operation authorization was not supplied.",
            )

        try:
            output = self._execute(operation, request)
        except ProviderAdapterTimeoutError as error:
            return self._failure(
                request,
                started_at,
                InvocationStatus.TIMED_OUT,
                error.code,
                error.message,
                execution_state=ExecutionState.UNKNOWN,
            )
        except ProviderAdapterCancelledError as error:
            return self._failure(
                request,
                started_at,
                InvocationStatus.CANCELLED,
                error.code,
                error.message,
                execution_state=ExecutionState.UNKNOWN,
            )
        except ProviderAdapterExecutionError as error:
            return self._failure(
                request,
                started_at,
                InvocationStatus.FAILED,
                error.code,
                error.message,
                retryable=error.retryable,
                execution_state=ExecutionState.UNKNOWN,
            )
        if not isinstance(output, Mapping):
            return self._failure(
                request,
                started_at,
                InvocationStatus.FAILED,
                "invalid_adapter_output",
                "adapter returned an output that is not a mapping.",
                execution_state=ExecutionState.EXECUTED,
            )
        output_error = operation.output_contract.validate(output)
        if output_error is not None:
            return self._failure(
                request,
                started_at,
                InvocationStatus.FAILED,
                output_error,
                "adapter output does not satisfy the operation contract.",
                execution_state=ExecutionState.EXECUTED,
            )
        return ProviderInvocationResult(
            status=InvocationStatus.SUCCEEDED,
            execution_state=ExecutionState.EXECUTED,
            provenance=self._provenance(request, started_at),
            output=output,
        )

    def _authorization_error(
        self, operation: ProviderOperation, context: ExecutionContext
    ) -> str | None:
        if operation.effect is OperationEffect.READ_ONLY and not operation.required_permissions:
            return None
        grants = tuple(
            grant
            for grant in context.authorization_grants
            if grant.provider_id == self.metadata.provider.identifier
            and grant.operation_id == operation.identifier
            and grant.authority_reference.strip()
        )
        if not grants:
            return "authorization_required"
        granted_permissions = {
            permission for grant in grants for permission in grant.permissions
        }
        if not set(operation.required_permissions).issubset(granted_permissions):
            return "permission_missing"
        return None

    def _provenance(
        self, request: ProviderInvocationRequest, started_at: datetime
    ) -> InvocationProvenance:
        return InvocationProvenance(
            provider_id=self.metadata.provider.identifier,
            adapter_id=self.metadata.adapter_id,
            contract_version=self.metadata.contract_version,
            operation_id=request.operation_id,
            request_id=request.request_id,
            trace_id=request.trace_id,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
        )

    def _failure(
        self,
        request: ProviderInvocationRequest,
        started_at: datetime,
        status: InvocationStatus,
        code: str,
        message: str,
        *,
        retryable: bool = False,
        execution_state: ExecutionState = ExecutionState.NOT_EXECUTED,
    ) -> ProviderInvocationResult:
        return ProviderInvocationResult(
            status=status,
            execution_state=execution_state,
            provenance=self._provenance(request, started_at),
            error=ProviderInvocationError(code, message, retryable),
        )

    @abstractmethod
    def _execute(
        self, operation: ProviderOperation, request: ProviderInvocationRequest
    ) -> Mapping[str, object]:
        """Execute using explicit adapter logic and return contract-shaped output.

        Subclasses own timeout enforcement and cooperative cancellation when
        declared. They must not infer permissions or access ambient credentials.
        """

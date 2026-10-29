"""Deterministic declaration-based provider capability compatibility resolution.

Resolution does not select a provider, authorize execution, invoke adapters,
or verify declared capability or availability claims.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from scripts.provider_adapter import (
    AdapterAvailability,
    AdapterMetadata,
    ProviderAdapter,
    ProviderAdapterContractError,
    ProviderIdentity,
)
from scripts.provider_contract_validator import validate_provider_adapter
from scripts.provider_registry import (
    ProviderRegistration,
    ProviderRegistry,
)


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")


class CapabilityResolutionStatus(str, Enum):
    COMPATIBLE = "compatible"
    AMBIGUOUS = "ambiguous"
    CAPABILITY_NOT_DECLARED = "capability_not_declared"
    OPERATION_NOT_DECLARED = "operation_not_declared"
    AVAILABILITY_UNSATISFIED = "availability_unsatisfied"
    DECLARATION_INVALID = "declaration_invalid"
    REGISTRY_INCOMPATIBLE = "registry_incompatible"
    INVALID_REQUEST = "invalid_request"
    INVALID_REGISTRY = "invalid_registry"


class ProviderCandidateStatus(str, Enum):
    COMPATIBLE = "compatible"
    DECLARATION_INVALID = "declaration_invalid"
    REGISTRY_INCOMPATIBLE = "registry_incompatible"
    SNAPSHOT_MISMATCH = "snapshot_mismatch"
    OPERATION_NOT_DECLARED = "operation_not_declared"
    AVAILABILITY_UNSATISFIED = "availability_unsatisfied"


@dataclass(frozen=True, slots=True)
class ProviderCapabilityCandidate:
    """One registered provider's result for a requested capability."""

    provider_id: str | None
    status: ProviderCandidateStatus
    message: str


@dataclass(frozen=True, slots=True)
class ProviderCapabilityResolution:
    """Resolution outcome and all matching-capability provider candidates."""

    status: CapabilityResolutionStatus
    capability_id: str | None
    operation_id: str | None
    required_availability: AdapterAvailability | None
    candidates: tuple[ProviderCapabilityCandidate, ...] = ()
    message: str = ""

    @property
    def compatible_candidates(self) -> tuple[ProviderCapabilityCandidate, ...]:
        """Return every compatible declaration without choosing among them."""
        return tuple(
            candidate
            for candidate in self.candidates
            if candidate.status is ProviderCandidateStatus.COMPATIBLE
        )


def resolve_provider_capability(
    registry: ProviderRegistry,
    capability_id: str,
    operation_id: str | None = None,
    required_availability: AdapterAvailability | None = None,
) -> ProviderCapabilityResolution:
    """Resolve declarations for a capability and optional related operation.

    Provider results retain the deterministic order returned by the canonical
    registry. A successful declaration match is not execution authorization,
    a live availability check, or evidence that the capability works.
    """
    invalid_request = _validate_request(
        registry, capability_id, operation_id, required_availability
    )
    if invalid_request is not None:
        return invalid_request

    try:
        registrations = ProviderRegistry.list_providers(
            registry, capability_id=capability_id
        )
    except Exception:
        return ProviderCapabilityResolution(
            status=CapabilityResolutionStatus.INVALID_REGISTRY,
            capability_id=capability_id,
            operation_id=operation_id,
            required_availability=required_availability,
            message="canonical registry discovery could not provide valid declarations.",
        )

    if not registrations:
        return ProviderCapabilityResolution(
            status=CapabilityResolutionStatus.CAPABILITY_NOT_DECLARED,
            capability_id=capability_id,
            operation_id=operation_id,
            required_availability=required_availability,
            message="no registered provider declares the requested capability.",
        )

    candidates = tuple(
        _resolve_candidate(
            registration,
            capability_id,
            operation_id,
            required_availability,
        )
        for registration in registrations
    )
    compatible = tuple(
        candidate
        for candidate in candidates
        if candidate.status is ProviderCandidateStatus.COMPATIBLE
    )
    if len(compatible) > 1:
        status = CapabilityResolutionStatus.AMBIGUOUS
        message = (
            "multiple registered providers declare a compatible capability; "
            "no provider was selected."
        )
    elif len(compatible) == 1:
        status = CapabilityResolutionStatus.COMPATIBLE
        message = (
            "a registered provider declaration matches the requested constraints; "
            "this does not authorize execution."
        )
    elif any(
        candidate.status is ProviderCandidateStatus.REGISTRY_INCOMPATIBLE
        for candidate in candidates
    ):
        status = CapabilityResolutionStatus.REGISTRY_INCOMPATIBLE
        message = "one or more provider declarations are incompatible with the registry."
    elif any(
        candidate.status
        in (
            ProviderCandidateStatus.DECLARATION_INVALID,
            ProviderCandidateStatus.SNAPSHOT_MISMATCH,
        )
        for candidate in candidates
    ):
        status = CapabilityResolutionStatus.DECLARATION_INVALID
        message = "one or more registered provider declarations failed validation."
    elif any(
        candidate.status is ProviderCandidateStatus.OPERATION_NOT_DECLARED
        for candidate in candidates
    ):
        status = CapabilityResolutionStatus.OPERATION_NOT_DECLARED
        message = (
            "no validated candidate declares the requested operation for "
            "the capability."
        )
    else:
        status = CapabilityResolutionStatus.AVAILABILITY_UNSATISFIED
        message = (
            "declared availability does not satisfy the requested availability."
        )

    return ProviderCapabilityResolution(
        status=status,
        capability_id=capability_id,
        operation_id=operation_id,
        required_availability=required_availability,
        candidates=candidates,
        message=message,
    )


def _validate_request(
    registry: object,
    capability_id: object,
    operation_id: object,
    required_availability: object,
) -> ProviderCapabilityResolution | None:
    if type(registry) is not ProviderRegistry:
        return ProviderCapabilityResolution(
            CapabilityResolutionStatus.INVALID_REQUEST,
            capability_id if isinstance(capability_id, str) else None,
            operation_id if isinstance(operation_id, str) else None,
            (
                required_availability
                if isinstance(required_availability, AdapterAvailability)
                else None
            ),
            message="registry must be an instance of the canonical ProviderRegistry.",
        )
    if not isinstance(capability_id, str) or not _IDENTIFIER_PATTERN.fullmatch(
        capability_id
    ):
        return ProviderCapabilityResolution(
            CapabilityResolutionStatus.INVALID_REQUEST,
            None,
            operation_id if isinstance(operation_id, str) else None,
            required_availability
            if isinstance(required_availability, AdapterAvailability)
            else None,
            message="capability_id must be a valid canonical identifier.",
        )
    if operation_id is not None and (
        not isinstance(operation_id, str)
        or not _IDENTIFIER_PATTERN.fullmatch(operation_id)
    ):
        return ProviderCapabilityResolution(
            CapabilityResolutionStatus.INVALID_REQUEST,
            capability_id,
            None,
            required_availability
            if isinstance(required_availability, AdapterAvailability)
            else None,
            message="operation_id must be a valid canonical identifier or None.",
        )
    if required_availability is not None and not isinstance(
        required_availability, AdapterAvailability
    ):
        return ProviderCapabilityResolution(
            CapabilityResolutionStatus.INVALID_REQUEST,
            capability_id,
            operation_id,
            None,
            message=(
                "required_availability must be an AdapterAvailability value or None."
            ),
        )
    return None


def _resolve_candidate(
    registration: ProviderRegistration,
    capability_id: str,
    operation_id: str | None,
    required_availability: AdapterAvailability | None,
) -> ProviderCapabilityCandidate:
    provider_id = _registration_provider_id(registration)
    if provider_id is None:
        return ProviderCapabilityCandidate(
            provider_id=None,
            status=ProviderCandidateStatus.REGISTRY_INCOMPATIBLE,
            message="registry returned a malformed provider registration.",
        )

    adapter = registration.adapter
    validation = validate_provider_adapter(adapter)
    if not validation.registry_compatible:
        return ProviderCapabilityCandidate(
            provider_id,
            ProviderCandidateStatus.REGISTRY_INCOMPATIBLE,
            "provider declarations do not satisfy the canonical registry contract.",
        )
    if not validation.conformant:
        return ProviderCapabilityCandidate(
            provider_id,
            ProviderCandidateStatus.DECLARATION_INVALID,
            "provider declarations failed canonical structural validation.",
        )

    try:
        declarations = ProviderAdapter.get_registration_declarations(adapter)
    except ProviderAdapterContractError:
        return ProviderCapabilityCandidate(
            provider_id,
            ProviderCandidateStatus.DECLARATION_INVALID,
            "provider registration declarations are missing or malformed.",
        )
    except Exception:
        return ProviderCapabilityCandidate(
            provider_id,
            ProviderCandidateStatus.DECLARATION_INVALID,
            "provider registration declarations could not be read safely.",
        )

    if (
        registration.metadata != declarations.metadata
        or registration.capabilities != declarations.capabilities
        or registration.operations != declarations.operations
        or registration.availability != declarations.availability
    ):
        return ProviderCapabilityCandidate(
            provider_id,
            ProviderCandidateStatus.SNAPSHOT_MISMATCH,
            "current adapter declarations differ from the registry snapshot.",
        )

    if operation_id is not None and not any(
        operation.identifier == operation_id
        and capability_id in operation.capability_ids
        for operation in registration.operations
    ):
        return ProviderCapabilityCandidate(
            provider_id,
            ProviderCandidateStatus.OPERATION_NOT_DECLARED,
            "provider does not declare the requested operation for this capability.",
        )

    if (
        required_availability is not None
        and registration.availability is not required_availability
    ):
        return ProviderCapabilityCandidate(
            provider_id,
            ProviderCandidateStatus.AVAILABILITY_UNSATISFIED,
            "provider's registration-time availability declaration does not match.",
        )

    return ProviderCapabilityCandidate(
        provider_id,
        ProviderCandidateStatus.COMPATIBLE,
        "provider declarations match the requested capability constraints.",
    )


def _registration_provider_id(registration: object) -> str | None:
    if type(registration) is not ProviderRegistration:
        return None
    metadata = registration.metadata
    if type(metadata) is not AdapterMetadata or type(
        metadata.provider
    ) is not ProviderIdentity:
        return None
    try:
        provider_id = metadata.provider.identifier
    except (AttributeError, TypeError):
        return None
    if not isinstance(provider_id, str) or not _IDENTIFIER_PATTERN.fullmatch(
        provider_id
    ):
        return None
    adapter_type = type(registration.adapter)
    if ProviderAdapter not in type.__getattribute__(adapter_type, "__mro__"):
        return None
    return provider_id

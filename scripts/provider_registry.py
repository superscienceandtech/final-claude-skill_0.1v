"""Canonical in-memory registration and metadata discovery for provider adapters.

The registry stores declarations from the provider-adapter contract. Registration
and discovery do not invoke adapter operations or independently verify claims.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from threading import Lock
from types import MappingProxyType
from typing import Mapping

from scripts.provider_adapter import (
    AdapterAvailability,
    AdapterMetadata,
    CapabilityDeclaration,
    ProviderAdapter,
    ProviderAdapterContractError,
    ProviderAdapterDeclarations,
    ProviderOperation,
)


_PROVIDER_ID_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")


class ProviderRegistryError(ValueError):
    """Base class for provider registration and discovery errors."""


class InvalidProviderRegistrationError(ProviderRegistryError):
    """Raised when an adapter does not contain valid contract metadata."""


class DuplicateProviderError(ProviderRegistryError):
    """Raised when a provider identifier is already registered."""


class ConflictingProviderMetadataError(DuplicateProviderError):
    """Raised when a duplicate provider identifier has different metadata."""


class InvalidProviderIdentifierError(ProviderRegistryError):
    """Raised when a provider identifier is malformed."""


class ProviderNotFoundError(ProviderRegistryError):
    """Raised when an operation requests an unregistered provider identifier."""


class ProviderCapabilityNotDeclaredError(ProviderRegistryError):
    """Raised when a registered provider does not declare a requested capability."""


class UnsupportedProviderFilterError(ProviderRegistryError):
    """Raised when a provider discovery filter is malformed or unsupported."""


@dataclass(frozen=True, slots=True)
class ProviderRegistration:
    """Immutable registration-time snapshot of canonical adapter declarations.

    The availability value is a registration-time declaration, not a live health
    check. The adapter reference is retained for explicit future invocation only.
    """

    adapter: ProviderAdapter
    metadata: AdapterMetadata
    capabilities: tuple[CapabilityDeclaration, ...]
    availability: AdapterAvailability
    operations: tuple[ProviderOperation, ...] = ()


class ProviderRegistry:
    """Thread-safe, per-instance registry for explicitly supplied adapters."""

    def __init__(self) -> None:
        self._providers: dict[str, ProviderRegistration] = {}
        self._lock = Lock()

    @property
    def providers(self) -> Mapping[str, ProviderRegistration]:
        """Return a read-only snapshot keyed by canonical provider identifier."""
        with self._lock:
            return MappingProxyType(
                {key: self._providers[key] for key in sorted(self._providers)}
            )

    def register(self, adapter: ProviderAdapter) -> ProviderRegistration:
        """Register one adapter without invoking it or replacing prior entries."""
        registration = self._snapshot_adapter(adapter)
        provider_id = registration.metadata.provider.identifier
        with self._lock:
            existing = self._providers.get(provider_id)
            if existing is not None:
                if existing.metadata != registration.metadata:
                    raise ConflictingProviderMetadataError(
                        f"provider identifier {provider_id!r} is already registered "
                        "with different adapter metadata."
                    )
                raise DuplicateProviderError(
                    f"provider identifier {provider_id!r} is already registered."
                )
            self._providers[provider_id] = registration
        return registration

    def get_provider(
        self, provider_id: str, *, capability_id: str | None = None
    ) -> ProviderAdapter:
        """Return the registered adapter or raise for an unknown identifier."""
        return self.get_registration(provider_id, capability_id=capability_id).adapter

    def get_registration(
        self, provider_id: str, *, capability_id: str | None = None
    ) -> ProviderRegistration:
        """Return the immutable declaration snapshot for a registered provider."""
        self._validate_provider_id(provider_id)
        if capability_id is not None and (
            not isinstance(capability_id, str)
            or not _PROVIDER_ID_PATTERN.fullmatch(capability_id)
        ):
            raise UnsupportedProviderFilterError(
                "capability_id must be a valid declared capability identifier or None."
            )
        with self._lock:
            registration = self._providers.get(provider_id)
        if registration is None:
            raise ProviderNotFoundError(
                f"provider identifier {provider_id!r} is not registered."
            )
        if capability_id is not None and not any(
            capability.identifier == capability_id
            for capability in registration.capabilities
        ):
            raise ProviderCapabilityNotDeclaredError(
                f"provider identifier {provider_id!r} does not declare capability "
                f"{capability_id!r}."
            )
        return registration

    def list_providers(
        self,
        *,
        capability_id: str | None = None,
        availability: AdapterAvailability | None = None,
    ) -> tuple[ProviderRegistration, ...]:
        """List declaration snapshots in provider-id order with exact filters."""
        if capability_id is not None and (
            not isinstance(capability_id, str)
            or not _PROVIDER_ID_PATTERN.fullmatch(capability_id)
        ):
            raise UnsupportedProviderFilterError(
                "capability_id must be a valid declared capability identifier or None."
            )
        if availability is not None and not isinstance(
            availability, AdapterAvailability
        ):
            raise UnsupportedProviderFilterError(
                "availability must be an AdapterAvailability value or None."
            )
        with self._lock:
            registrations = tuple(
                self._providers[key] for key in sorted(self._providers)
            )

        return tuple(
            registration
            for registration in registrations
            if (availability is None or registration.availability is availability)
            and (
                capability_id is None
                or any(
                    capability.identifier == capability_id
                    for capability in registration.capabilities
                )
            )
        )

    def remove(self, provider_id: str) -> ProviderRegistration:
        """Remove and return a registration; unknown identifiers raise explicitly."""
        self._validate_provider_id(provider_id)
        with self._lock:
            registration = self._providers.pop(provider_id, None)
        if registration is None:
            raise ProviderNotFoundError(
                f"provider identifier {provider_id!r} is not registered."
            )
        return registration

    @staticmethod
    def _validate_provider_id(provider_id: str) -> None:
        if not isinstance(provider_id, str) or not _PROVIDER_ID_PATTERN.fullmatch(
            provider_id
        ):
            raise InvalidProviderIdentifierError(
                "provider identifier must be a valid lowercase identifier."
            )

    @staticmethod
    def _snapshot_adapter(adapter: ProviderAdapter) -> ProviderRegistration:
        adapter_type = type(adapter)
        if ProviderAdapter not in type.__getattribute__(adapter_type, "__mro__"):
            raise InvalidProviderRegistrationError(
                "adapter must be an instance of the canonical ProviderAdapter contract."
            )

        try:
            declarations = ProviderAdapter.get_registration_declarations(adapter)
        except ProviderAdapterContractError as error:
            raise InvalidProviderRegistrationError(
                "adapter does not expose valid initialized registration declarations."
            ) from error

        if type(declarations) is not ProviderAdapterDeclarations:
            raise InvalidProviderRegistrationError(
                "adapter registration declarations must use the canonical contract type."
            )
        provider_id = declarations.metadata.provider.identifier
        if not isinstance(provider_id, str) or not _PROVIDER_ID_PATTERN.fullmatch(
            provider_id
        ):
            raise InvalidProviderRegistrationError(
                "adapter declarations contain an invalid provider identifier."
            )
        return ProviderRegistration(
            adapter=adapter,
            metadata=declarations.metadata,
            capabilities=declarations.capabilities,
            availability=declarations.availability,
            operations=declarations.operations,
        )

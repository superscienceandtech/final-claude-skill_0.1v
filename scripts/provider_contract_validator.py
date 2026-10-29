"""Structural conformance checks for canonical provider adapters.

Validation inspects canonical declarations only. It does not invoke adapter
operations, verify provider functionality, or mutate a provider registry.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from scripts.provider_adapter import (
    AdapterAvailability,
    AdapterMetadata,
    CapabilityDeclaration,
    CapabilityVerification,
    ProviderAdapter,
    ProviderAdapterContractError,
    ProviderAdapterDeclarations,
    ProviderDataContract,
    ProviderDataField,
    ProviderIdentity,
    ProviderOperation,
)
from scripts.provider_registry import (
    InvalidProviderRegistrationError,
    ProviderRegistry,
)


class ValidationIssueCode(str, Enum):
    INVALID_ADAPTER = "invalid_adapter"
    DECLARATION_ACCESSOR_MISSING = "declaration_accessor_missing"
    DECLARATIONS_MISSING_OR_MALFORMED = "declarations_missing_or_malformed"
    INVALID_METADATA = "invalid_metadata"
    INVALID_CAPABILITIES = "invalid_capabilities"
    INVALID_OPERATIONS = "invalid_operations"
    INVALID_AVAILABILITY = "invalid_availability"
    REGISTRY_INCOMPATIBLE = "registry_incompatible"


@dataclass(frozen=True, slots=True)
class ProviderContractValidationIssue:
    """One deterministic structural-conformance finding."""

    code: ValidationIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class ProviderContractValidationResult:
    """Structural validation result; conformance does not imply runtime behavior."""

    conformant: bool
    registry_compatible: bool
    issues: tuple[ProviderContractValidationIssue, ...]


def validate_provider_adapter(adapter: object) -> ProviderContractValidationResult:
    """Validate canonical adapter declarations without executing provider behavior.

    The registry's base-class registration path is mirrored structurally:
    adapters must inherit the canonical contract, expose its canonical immutable
    declaration value, and provide declarations accepted by that value's
    validation rules. No registry instance or state is created or modified.
    """
    issues: list[ProviderContractValidationIssue] = []
    adapter_type = type(adapter)
    if ProviderAdapter not in type.__getattribute__(adapter_type, "__mro__"):
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.INVALID_ADAPTER,
                "object does not inherit from the canonical ProviderAdapter contract.",
            )
        )
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.REGISTRY_INCOMPATIBLE,
                "the provider registry accepts only canonical ProviderAdapter instances.",
            )
        )
        return ProviderContractValidationResult(False, False, tuple(issues))

    accessor = ProviderAdapter.get_registration_declarations
    if not callable(accessor):
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.DECLARATION_ACCESSOR_MISSING,
                "canonical registration-declaration accessor is unavailable.",
            )
        )
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.REGISTRY_INCOMPATIBLE,
                "the provider registry cannot obtain canonical registration declarations.",
            )
        )
        return ProviderContractValidationResult(False, False, tuple(issues))

    try:
        declarations = accessor(adapter)
    except ProviderAdapterContractError:
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.DECLARATIONS_MISSING_OR_MALFORMED,
                "canonical registration declarations are missing or malformed.",
            )
        )
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.REGISTRY_INCOMPATIBLE,
                "the provider registry cannot consume the adapter's declarations.",
            )
        )
        return ProviderContractValidationResult(False, False, tuple(issues))
    except Exception:
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.DECLARATIONS_MISSING_OR_MALFORMED,
                "canonical registration declarations could not be read safely.",
            )
        )
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.REGISTRY_INCOMPATIBLE,
                "the provider registry cannot consume the adapter's declarations.",
            )
        )
        return ProviderContractValidationResult(False, False, tuple(issues))

    if type(declarations) is not ProviderAdapterDeclarations:
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.DECLARATIONS_MISSING_OR_MALFORMED,
                "accessor did not return the canonical ProviderAdapterDeclarations type.",
            )
        )
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.REGISTRY_INCOMPATIBLE,
                "the provider registry requires canonical declaration snapshots.",
            )
        )
        return ProviderContractValidationResult(False, False, tuple(issues))

    declaration_type_parameters = getattr(
        ProviderAdapterDeclarations, "__dataclass_params__", None
    )
    if declaration_type_parameters is None or not declaration_type_parameters.frozen:
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.DECLARATIONS_MISSING_OR_MALFORMED,
                "canonical declaration snapshots are not immutable.",
            )
        )

    metadata_valid = _validate_metadata(declarations.metadata)
    if not metadata_valid:
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.INVALID_METADATA,
                "provider identity or adapter metadata is invalid.",
            )
        )

    capabilities_valid = _validate_capabilities(declarations.capabilities)
    if not capabilities_valid:
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.INVALID_CAPABILITIES,
                "capability declarations are malformed or duplicated.",
            )
        )

    operations_valid = _validate_operations(
        declarations.operations, declarations.capabilities
    )
    if not operations_valid:
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.INVALID_OPERATIONS,
                "operation declarations are malformed, duplicated, or reference "
                "undeclared capabilities.",
            )
        )

    availability_valid = type(declarations.availability) is AdapterAvailability
    if not availability_valid:
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.INVALID_AVAILABILITY,
                "availability is not a canonical AdapterAvailability value.",
            )
        )

    declarations_valid = (
        metadata_valid
        and capabilities_valid
        and operations_valid
        and availability_valid
        and declaration_type_parameters is not None
        and declaration_type_parameters.frozen
    )
    registry_compatible = False
    registry_failure_message = (
        "provider declarations do not satisfy the canonical registry contract."
    )
    if declarations_valid:
        try:
            # This is the registry's non-mutating structural registration path.
            ProviderRegistry._snapshot_adapter(adapter)
            registry_compatible = True
        except InvalidProviderRegistrationError:
            registry_failure_message = (
                "the canonical provider registry rejected the adapter declarations."
            )
        except Exception:
            registry_failure_message = (
                "the canonical provider registry could not validate the declarations."
            )
    if not registry_compatible:
        issues.append(
            ProviderContractValidationIssue(
                ValidationIssueCode.REGISTRY_INCOMPATIBLE,
                registry_failure_message,
            )
        )
    return ProviderContractValidationResult(
        conformant=declarations_valid and registry_compatible,
        registry_compatible=registry_compatible,
        issues=tuple(issues),
    )


def _validate_metadata(metadata: object) -> bool:
    if type(metadata) is not AdapterMetadata:
        return False
    provider = metadata.provider
    if type(provider) is not ProviderIdentity:
        return False
    try:
        replace(provider)
        replace(metadata, provider=replace(provider))
    except (TypeError, ValueError, AttributeError):
        return False
    return True


def _validate_capabilities(capabilities: object) -> bool:
    if type(capabilities) is not tuple:
        return False
    identifiers: list[str] = []
    for capability in capabilities:
        if type(capability) is not CapabilityDeclaration:
            return False
        verification = capability.verification
        if verification is not None:
            if type(verification) is not CapabilityVerification:
                return False
            try:
                verification = replace(verification)
            except (TypeError, ValueError, AttributeError):
                return False
        try:
            checked = replace(capability, verification=verification)
        except (TypeError, ValueError, AttributeError):
            return False
        identifiers.append(checked.identifier)
    return len(identifiers) == len(set(identifiers))


def _validate_data_contract(contract: object) -> bool:
    if type(contract) is not ProviderDataContract or type(contract.fields) is not tuple:
        return False
    fields: list[ProviderDataField] = []
    for item in contract.fields:
        if type(item) is not ProviderDataField:
            return False
        try:
            fields.append(replace(item))
        except (TypeError, ValueError, AttributeError):
            return False
    try:
        replace(contract, fields=tuple(fields))
    except (TypeError, ValueError, AttributeError):
        return False
    return True


def _validate_operations(
    operations: object, capabilities: object
) -> bool:
    if type(operations) is not tuple or type(capabilities) is not tuple:
        return False
    capability_ids = {
        item.identifier
        for item in capabilities
        if type(item) is CapabilityDeclaration
    }
    identifiers: list[str] = []
    for operation in operations:
        if type(operation) is not ProviderOperation:
            return False
        if not _validate_data_contract(operation.input_contract) or not (
            _validate_data_contract(operation.output_contract)
        ):
            return False
        try:
            checked = replace(operation)
        except (TypeError, ValueError, AttributeError):
            return False
        identifiers.append(checked.identifier)
        if not set(checked.capability_ids).issubset(capability_ids):
            return False
    return len(identifiers) == len(set(identifiers))

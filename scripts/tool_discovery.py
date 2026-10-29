"""Metadata-only discovery and deterministic selection for registered tools.

This module reads validated :class:`ToolContract` values only. It does not
inspect adapters, call tool implementations, or invoke the execution API.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from scripts.tool_framework import (
    ExecutionAvailability,
    ToolContract,
    ToolRegistry,
)


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")


class ToolDiscoveryError(ValueError):
    """Base class for discovery and selection configuration errors."""


class InvalidToolRequirementsError(ToolDiscoveryError):
    """Raised when a requirements or filter contract is malformed."""


class UnsupportedDiscoveryFilterError(ToolDiscoveryError):
    """Raised when discovery receives an unsupported filter object."""


class RegistryCompatibilityError(ToolDiscoveryError):
    """Raised when the registry does not provide the expected P076 API."""


class InvalidMatchingConfigurationError(ToolDiscoveryError):
    """Raised when a matching call receives incompatible arguments."""


class MatchClassification(str, Enum):
    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    NO_MATCH = "no_match"


class MinimumMatchQuality(str, Enum):
    PARTIAL = "partial_match"
    EXACT = "exact_match"


class SelectionStatus(str, Enum):
    SELECTED = "selected"
    AMBIGUOUS = "ambiguous"
    NO_MATCH = "no_match"
    DISCOVERY_ONLY = "discovery_only"


@dataclass(frozen=True, slots=True)
class ToolRequirements:
    """Hard constraints and soft preferences for choosing one registered tool.

    Required tool identifiers are alternatives: a candidate must have one of
    the listed identifiers. Required input names mean the tool contract must
    declare each name; they do not specify or validate caller input values.
    Inclusion flags allow disabled or unavailable contracts to participate in
    discovery and selection, but never change their execution state.
    """

    required_capabilities: tuple[str, ...] = ()
    preferred_capabilities: tuple[str, ...] = ()
    required_adapter_id: str | None = None
    required_tool_identifiers: tuple[str, ...] = ()
    required_input_names: tuple[str, ...] = ()
    include_disabled: bool = False
    include_unavailable: bool = False
    minimum_match_quality: MinimumMatchQuality = MinimumMatchQuality.PARTIAL

    def __post_init__(self) -> None:
        _validate_values(self.required_capabilities, "required_capabilities")
        _validate_values(self.preferred_capabilities, "preferred_capabilities")
        _validate_identifiers(
            self.required_tool_identifiers, "required_tool_identifiers"
        )
        _validate_identifiers(self.required_input_names, "required_input_names")
        if set(self.required_capabilities).intersection(self.preferred_capabilities):
            raise InvalidToolRequirementsError(
                "a capability cannot be both required and preferred."
            )
        if self.required_adapter_id is not None and (
            not isinstance(self.required_adapter_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(self.required_adapter_id)
        ):
            raise InvalidToolRequirementsError(
                "required_adapter_id must be a valid lowercase identifier or None."
            )
        if not isinstance(self.include_disabled, bool):
            raise InvalidToolRequirementsError("include_disabled must be a boolean.")
        if not isinstance(self.include_unavailable, bool):
            raise InvalidToolRequirementsError("include_unavailable must be a boolean.")
        if not isinstance(self.minimum_match_quality, MinimumMatchQuality):
            raise InvalidToolRequirementsError(
                "minimum_match_quality must be a MinimumMatchQuality value."
            )


@dataclass(frozen=True, slots=True)
class DiscoveryFilters:
    """Exact metadata filters for listing contracts without selecting one.

    All required capabilities and input names must be declared. Listed tool
    identifiers are alternatives. Preferred capabilities do not exclude a
    contract; they sort contracts with more preference matches first.
    """

    required_capabilities: tuple[str, ...] = ()
    preferred_capabilities: tuple[str, ...] = ()
    required_adapter_id: str | None = None
    tool_identifiers: tuple[str, ...] = ()
    required_input_names: tuple[str, ...] = ()
    include_disabled: bool = False
    include_unavailable: bool = False

    def __post_init__(self) -> None:
        _validate_values(self.required_capabilities, "required_capabilities")
        _validate_values(self.preferred_capabilities, "preferred_capabilities")
        _validate_identifiers(self.tool_identifiers, "tool_identifiers")
        _validate_identifiers(self.required_input_names, "required_input_names")
        if set(self.required_capabilities).intersection(self.preferred_capabilities):
            raise InvalidToolRequirementsError(
                "a capability cannot be both required and preferred."
            )
        if self.required_adapter_id is not None and (
            not isinstance(self.required_adapter_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(self.required_adapter_id)
        ):
            raise InvalidToolRequirementsError(
                "required_adapter_id must be a valid lowercase identifier or None."
            )
        if not isinstance(self.include_disabled, bool):
            raise InvalidToolRequirementsError("include_disabled must be a boolean.")
        if not isinstance(self.include_unavailable, bool):
            raise InvalidToolRequirementsError("include_unavailable must be a boolean.")


@dataclass(frozen=True, slots=True)
class ToolDiscoveryResult:
    """Contracts returned by metadata filters in deterministic order."""

    tools: tuple[ToolContract, ...]


@dataclass(frozen=True, slots=True)
class ToolMatch:
    """Explainable per-contract match; ambiguity belongs to selection plans."""

    tool_identifier: str
    tool_name: str
    tool_description: str
    declared_capabilities: tuple[str, ...]
    adapter_id: str | None
    enabled: bool
    execution_availability: ExecutionAvailability
    classification: MatchClassification
    matched_required_capabilities: tuple[str, ...]
    missing_required_capabilities: tuple[str, ...]
    missing_required_input_names: tuple[str, ...]
    required_adapter_matched: bool
    required_tool_identifier_matched: bool
    matched_preferred_capabilities: tuple[str, ...]
    unmet_preferred_capabilities: tuple[str, ...]
    eligible: bool
    contract_execution_state_available: bool
    score: int
    qualifies: bool
    reason_codes: tuple[str, ...]
    explanation: str


@dataclass(frozen=True, slots=True)
class ToolSelectionPlan:
    """Selection decision containing metadata only, never an execution result."""

    requirements: ToolRequirements
    candidates: tuple[ToolMatch, ...]
    status: SelectionStatus
    selected_tool_identifier: str | None
    reason_code: str
    explanation: str


def discover_tools(
    registry: ToolRegistry,
    filters: DiscoveryFilters | None = None,
) -> ToolDiscoveryResult:
    """List contracts matching exact filters; preference matches sort first."""
    if filters is None:
        filters = DiscoveryFilters()
    if not isinstance(filters, DiscoveryFilters):
        raise UnsupportedDiscoveryFilterError(
            "filters must be a DiscoveryFilters instance or None."
        )

    candidates = _read_registry_tools(registry)
    matched = [
        tool for tool in candidates if _matches_discovery_filters(tool, filters)
    ]
    matched.sort(
        key=lambda tool: (
            -sum(
                capability in tool.capabilities
                for capability in filters.preferred_capabilities
            ),
            tool.identifier,
        )
    )
    return ToolDiscoveryResult(tuple(matched))


def match_tool(tool: ToolContract, requirements: ToolRequirements) -> ToolMatch:
    """Match one contract; required constraints always outrank preferences."""
    if not isinstance(tool, ToolContract):
        raise InvalidMatchingConfigurationError(
            "tool must be a validated ToolContract."
        )
    if not isinstance(requirements, ToolRequirements):
        raise InvalidMatchingConfigurationError(
            "requirements must be a ToolRequirements instance."
        )

    capabilities = set(tool.capabilities)
    declared_inputs = {field.name for field in tool.input_schema}
    matched_required = tuple(
        item for item in requirements.required_capabilities if item in capabilities
    )
    missing_required = tuple(
        item for item in requirements.required_capabilities if item not in capabilities
    )
    matched_preferred = tuple(
        item for item in requirements.preferred_capabilities if item in capabilities
    )
    unmet_preferred = tuple(
        item for item in requirements.preferred_capabilities if item not in capabilities
    )
    missing_inputs = tuple(
        item
        for item in requirements.required_input_names
        if item not in declared_inputs
    )
    requested_id_matches = (
        not requirements.required_tool_identifiers
        or tool.identifier in requirements.required_tool_identifiers
    )
    adapter_matches = (
        requirements.required_adapter_id is None
        or tool.adapter_id == requirements.required_adapter_id
    )
    execution_eligible = (
        tool.enabled
        and tool.execution_availability is ExecutionAvailability.AVAILABLE
    )
    state_allowed = (
        (tool.enabled or requirements.include_disabled)
        and (
            tool.execution_availability is ExecutionAvailability.AVAILABLE
            or requirements.include_unavailable
        )
    )
    eligible = (
        state_allowed
        and not missing_required
        and not missing_inputs
        and requested_id_matches
        and adapter_matches
    )

    reasons: list[str] = []
    if matched_required:
        reasons.append("required_capabilities_matched")
    if missing_required:
        reasons.append("required_capabilities_missing")
    if matched_preferred:
        reasons.append("preferred_capabilities_matched")
    if unmet_preferred:
        reasons.append("preferred_capabilities_unmet")
    if not requested_id_matches:
        reasons.append("tool_identifier_not_requested")
    if not adapter_matches:
        reasons.append("required_adapter_mismatch")
    if missing_inputs:
        reasons.append("required_inputs_missing")
    if not tool.enabled:
        reasons.append("disabled_tool")
    if tool.execution_availability is ExecutionAvailability.UNAVAILABLE:
        reasons.append("execution_unavailable")
    if not state_allowed:
        reasons.append("tool_state_excluded")
    if eligible:
        classification = (
            MatchClassification.EXACT_MATCH
            if not unmet_preferred
            else MatchClassification.PARTIAL_MATCH
        )
        qualifies = not (
            requirements.minimum_match_quality is MinimumMatchQuality.EXACT
            and classification is MatchClassification.PARTIAL_MATCH
        )
        reasons.append(
            "exact_match"
            if classification is MatchClassification.EXACT_MATCH
            else "partial_match"
        )
        if not qualifies:
            reasons.append("below_minimum_match_quality")
    else:
        classification = MatchClassification.NO_MATCH
        qualifies = False
        reasons.append("hard_requirement_or_eligibility_failed")
    if eligible and not execution_eligible:
        reasons.append("selection_does_not_imply_executable")

    if classification is MatchClassification.NO_MATCH:
        failures: list[str] = []
        if missing_required:
            failures.append(
                "missing required capabilities: " + ", ".join(missing_required)
            )
        if missing_inputs:
            failures.append(
                "missing declared input names: " + ", ".join(missing_inputs)
            )
        if not requested_id_matches:
            failures.append("tool identifier is not in the requested alternatives")
        if not adapter_matches:
            failures.append("required adapter identifier does not match")
        if not state_allowed:
            failures.append("tool enabled/availability state is excluded by policy")
        explanation = "No match: " + "; ".join(failures) + "."
    elif classification is MatchClassification.EXACT_MATCH:
        explanation = "All hard requirements and specified preferences are satisfied."
    else:
        explanation = (
            f"Hard requirements are satisfied; {len(unmet_preferred)} preferred "
            "capability/capabilities are not declared."
        )
        if not qualifies:
            explanation += " This is below the configured minimum match quality."
    if eligible and not execution_eligible:
        explanation += " The contract is selectable by policy but not execution-eligible."

    return ToolMatch(
        tool_identifier=tool.identifier,
        tool_name=tool.name,
        tool_description=tool.description,
        declared_capabilities=tool.capabilities,
        adapter_id=tool.adapter_id,
        enabled=tool.enabled,
        execution_availability=tool.execution_availability,
        classification=classification,
        matched_required_capabilities=matched_required,
        missing_required_capabilities=missing_required,
        missing_required_input_names=missing_inputs,
        required_adapter_matched=adapter_matches,
        required_tool_identifier_matched=requested_id_matches,
        matched_preferred_capabilities=matched_preferred,
        unmet_preferred_capabilities=unmet_preferred,
        eligible=eligible,
        contract_execution_state_available=execution_eligible,
        score=len(matched_preferred),
        qualifies=qualifies,
        reason_codes=tuple(reasons),
        explanation=explanation,
    )


def plan_tool_selection(
    registry: ToolRegistry,
    requirements: ToolRequirements,
    *,
    discovery_only: bool = False,
) -> ToolSelectionPlan:
    """Create an explainable plan without calling adapters or implementations."""
    if not isinstance(requirements, ToolRequirements):
        raise InvalidMatchingConfigurationError(
            "requirements must be a ToolRequirements instance."
        )
    if not isinstance(discovery_only, bool):
        raise InvalidMatchingConfigurationError("discovery_only must be a boolean.")

    contracts = _read_registry_tools(registry)
    candidates = tuple(match_tool(tool, requirements) for tool in contracts)
    if discovery_only:
        return ToolSelectionPlan(
            requirements,
            candidates,
            SelectionStatus.DISCOVERY_ONLY,
            None,
            "discovery_only",
            "Contracts were matched for inspection; no tool was selected or invoked.",
        )

    qualifying = [candidate for candidate in candidates if candidate.qualifies]
    if not qualifying:
        return ToolSelectionPlan(
            requirements,
            candidates,
            SelectionStatus.NO_MATCH,
            None,
            "no_qualifying_candidate",
            "No registered tool satisfies the hard requirements and minimum quality.",
        )
    best_score = max(candidate.score for candidate in qualifying)
    best = [
        candidate for candidate in qualifying if candidate.score == best_score
    ]
    if len(best) != 1:
        return ToolSelectionPlan(
            requirements,
            candidates,
            SelectionStatus.AMBIGUOUS,
            None,
            "top_candidates_tied",
            "Multiple tools share the highest documented match score; choose one explicitly.",
        )
    selected = best[0]
    return ToolSelectionPlan(
        requirements,
        candidates,
        SelectionStatus.SELECTED,
        selected.tool_identifier,
        "unique_highest_match",
        (
            f"Selected '{selected.tool_identifier}' as the unique qualifying candidate "
            f"with {selected.score} matched preferred capability/capabilities. "
            "This plan does not invoke the tool."
        ),
    )


def _read_registry_tools(registry: ToolRegistry) -> tuple[ToolContract, ...]:
    if not isinstance(registry, ToolRegistry):
        raise RegistryCompatibilityError(
            "registry must implement the P076 ToolRegistry API."
        )
    tools = registry.list_tools()
    if not isinstance(tools, tuple) or any(
        not isinstance(tool, ToolContract) for tool in tools
    ):
        raise RegistryCompatibilityError(
            "registry.list_tools() must return a tuple of ToolContract values."
        )
    identifiers = [tool.identifier for tool in tools]
    if len(identifiers) != len(set(identifiers)):
        raise RegistryCompatibilityError(
            "registry.list_tools() returned duplicate tool identifiers."
        )
    return tuple(sorted(tools, key=lambda tool: tool.identifier))


def _matches_discovery_filters(
    tool: ToolContract, filters: DiscoveryFilters
) -> bool:
    capabilities = set(tool.capabilities)
    inputs = {field.name for field in tool.input_schema}
    return (
        (not filters.tool_identifiers or tool.identifier in filters.tool_identifiers)
        and (
            filters.required_adapter_id is None
            or tool.adapter_id == filters.required_adapter_id
        )
        and all(item in capabilities for item in filters.required_capabilities)
        and all(item in inputs for item in filters.required_input_names)
        and (tool.enabled or filters.include_disabled)
        and (
            tool.execution_availability is ExecutionAvailability.AVAILABLE
            or filters.include_unavailable
        )
    )


def _validate_values(values: tuple[str, ...], field_name: str) -> None:
    if not isinstance(values, tuple) or any(
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        for value in values
    ):
        raise InvalidToolRequirementsError(
            f"{field_name} must be a tuple of non-empty strings."
        )
    if len(values) != len(set(values)):
        raise InvalidToolRequirementsError(f"{field_name} cannot contain duplicates.")


def _validate_identifiers(values: tuple[str, ...], field_name: str) -> None:
    _validate_values(values, field_name)
    if any(not _IDENTIFIER_PATTERN.fullmatch(value) for value in values):
        raise InvalidToolRequirementsError(
            f"{field_name} must contain valid lowercase identifiers."
        )

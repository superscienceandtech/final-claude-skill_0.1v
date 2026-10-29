"""Tests for metadata-only Tool capability discovery and selection."""

from __future__ import annotations

import unittest
from typing import Any, cast

from scripts.tool_discovery import (
    DiscoveryFilters,
    InvalidMatchingConfigurationError,
    InvalidToolRequirementsError,
    MatchClassification,
    MinimumMatchQuality,
    RegistryCompatibilityError,
    SelectionStatus,
    ToolRequirements,
    UnsupportedDiscoveryFilterError,
    discover_tools,
    match_tool,
    plan_tool_selection,
)
from scripts.tool_framework import (
    ExecutionAvailability,
    InputField,
    InputType,
    LocalToolAdapter,
    ToolContract,
    ToolExecutor,
    ToolRegistry,
    register_text_statistics,
)


def make_tool(
    identifier: str,
    *,
    capabilities: tuple[str, ...] = (),
    adapter_id: str | None = "local.adapter",
    enabled: bool = True,
    availability: ExecutionAvailability = ExecutionAvailability.AVAILABLE,
    input_names: tuple[str, ...] = (),
) -> ToolContract:
    return ToolContract(
        identifier=identifier,
        name=identifier.replace(".", " ").title(),
        description=f"Tool {identifier}.",
        input_schema=tuple(
            InputField(name, InputType.STRING) for name in input_names
        ),
        capabilities=capabilities,
        adapter_id=adapter_id,
        enabled=enabled,
        execution_availability=availability,
    )


class ToolRequirementsTests(unittest.TestCase):
    def test_accepts_valid_constraints_and_defaults_to_partial_quality(self):
        requirements = ToolRequirements(
            required_capabilities=("text",),
            preferred_capabilities=("statistics",),
            required_adapter_id="local.adapter",
            required_tool_identifiers=("local.alpha", "local.beta"),
            required_input_names=("text",),
        )

        self.assertEqual(requirements.minimum_match_quality, MinimumMatchQuality.PARTIAL)
        self.assertEqual(requirements.required_capabilities, ("text",))

    def test_rejects_invalid_values_and_types(self):
        for kwargs in (
            {"required_capabilities": "text"},
            {"preferred_capabilities": (1,)},
            {"required_tool_identifiers": ("Bad_ID",)},
            {"required_input_names": ("bad name",)},
            {"required_adapter_id": "Bad_ID"},
            {"include_disabled": 1},
            {"minimum_match_quality": "exact"},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(InvalidToolRequirementsError):
                    ToolRequirements(**cast(Any, kwargs))

    def test_rejects_duplicate_and_contradictory_capabilities(self):
        with self.assertRaisesRegex(InvalidToolRequirementsError, "duplicates"):
            ToolRequirements(required_capabilities=("text", "text"))
        with self.assertRaisesRegex(InvalidToolRequirementsError, "both required"):
            ToolRequirements(
                required_capabilities=("text",),
                preferred_capabilities=("text",),
            )


class ToolDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.alpha = make_tool(
            "local.alpha",
            capabilities=("text", "statistics"),
            input_names=("text",),
        )
        self.beta = make_tool(
            "local.beta",
            capabilities=("text",),
            adapter_id="local.other",
            input_names=("text", "format"),
        )
        self.disabled = make_tool(
            "local.disabled",
            capabilities=("text",),
            enabled=False,
            input_names=("text",),
        )
        self.unavailable = make_tool(
            "local.unavailable",
            capabilities=("text",),
            availability=ExecutionAvailability.UNAVAILABLE,
            input_names=("text",),
        )
        for tool in (self.beta, self.unavailable, self.disabled, self.alpha):
            self.registry.register(tool)

    def test_discovery_order_is_deterministic_and_preference_aware(self):
        result = discover_tools(self.registry)
        self.assertEqual(
            [tool.identifier for tool in result.tools],
            ["local.alpha", "local.beta"],
        )

        preferred = discover_tools(
            self.registry,
            DiscoveryFilters(preferred_capabilities=("statistics",)),
        )
        self.assertEqual(
            [tool.identifier for tool in preferred.tools],
            ["local.alpha", "local.beta"],
        )

    def test_filters_by_tool_adapter_capability_and_input(self):
        by_identifier = discover_tools(
            self.registry,
            DiscoveryFilters(tool_identifiers=("local.beta",)),
        )
        by_adapter = discover_tools(
            self.registry,
            DiscoveryFilters(required_adapter_id="local.other"),
        )
        by_capability_and_input = discover_tools(
            self.registry,
            DiscoveryFilters(
                required_capabilities=("text",),
                required_input_names=("format",),
            ),
        )

        self.assertEqual([tool.identifier for tool in by_identifier.tools], ["local.beta"])
        self.assertEqual([tool.identifier for tool in by_adapter.tools], ["local.beta"])
        self.assertEqual(
            [tool.identifier for tool in by_capability_and_input.tools],
            ["local.beta"],
        )

    def test_status_flags_expose_but_do_not_change_execution_availability(self):
        default = discover_tools(self.registry)
        inclusive = discover_tools(
            self.registry,
            DiscoveryFilters(include_disabled=True, include_unavailable=True),
        )

        self.assertEqual(len(default.tools), 2)
        self.assertEqual(
            [tool.identifier for tool in inclusive.tools],
            [
                "local.alpha",
                "local.beta",
                "local.disabled",
                "local.unavailable",
            ],
        )
        self.assertFalse(self.disabled.enabled)
        self.assertIs(
            self.unavailable.execution_availability,
            ExecutionAvailability.UNAVAILABLE,
        )

    def test_rejects_unsupported_filters_and_incompatible_registry_results(self):
        with self.assertRaises(UnsupportedDiscoveryFilterError):
            discover_tools(self.registry, cast(Any, {"enabled": True}))

        class MalformedRegistry(ToolRegistry):
            def list_tools(
                self,
                *,
                enabled: bool | None = None,
                execution_availability: ExecutionAvailability | None = None,
            ) -> tuple[ToolContract, ...]:
                return cast(Any, (enabled, execution_availability))

        malformed = MalformedRegistry()
        with self.assertRaises(RegistryCompatibilityError):
            discover_tools(malformed)

        with self.assertRaises(RegistryCompatibilityError):
            discover_tools(cast(Any, object()))


class ToolMatchingTests(unittest.TestCase):
    def test_exact_partial_and_no_match_classification(self):
        tool = make_tool(
            "local.stats",
            capabilities=("text", "statistics"),
        )
        exact = match_tool(
            tool,
            ToolRequirements(
                required_capabilities=("text",),
                preferred_capabilities=("statistics",),
            ),
        )
        partial = match_tool(
            tool,
            ToolRequirements(
                required_capabilities=("text",),
                preferred_capabilities=("statistics", "json"),
            ),
        )
        no_match = match_tool(
            tool,
            ToolRequirements(required_capabilities=("network",)),
        )

        self.assertEqual(exact.classification, MatchClassification.EXACT_MATCH)
        self.assertEqual(exact.matched_required_capabilities, ("text",))
        self.assertEqual(exact.matched_preferred_capabilities, ("statistics",))
        self.assertEqual(partial.classification, MatchClassification.PARTIAL_MATCH)
        self.assertEqual(partial.missing_required_capabilities, ())
        self.assertEqual(partial.unmet_preferred_capabilities, ("json",))
        self.assertEqual(no_match.classification, MatchClassification.NO_MATCH)
        self.assertEqual(no_match.missing_required_capabilities, ("network",))
        self.assertFalse(no_match.qualifies)

    def test_missing_adapter_identifier_tool_identifier_or_input_is_hard_failure(self):
        tool = make_tool(
            "local.stats",
            capabilities=("text",),
            adapter_id="local.adapter",
            input_names=("text",),
        )
        cases = (
            ToolRequirements(required_adapter_id="local.other"),
            ToolRequirements(required_tool_identifiers=("local.other",)),
            ToolRequirements(required_input_names=("format",)),
        )
        for requirements in cases:
            with self.subTest(requirements=requirements):
                result = match_tool(tool, requirements)
                self.assertEqual(result.classification, MatchClassification.NO_MATCH)
                self.assertFalse(result.eligible)

    def test_minimum_quality_can_decline_partial_match(self):
        result = match_tool(
            make_tool("local.stats", capabilities=("text",)),
            ToolRequirements(
                required_capabilities=("text",),
                preferred_capabilities=("statistics",),
                minimum_match_quality=MinimumMatchQuality.EXACT,
            ),
        )

        self.assertEqual(result.classification, MatchClassification.PARTIAL_MATCH)
        self.assertFalse(result.qualifies)
        self.assertIn("below_minimum_match_quality", result.reason_codes)

    def test_empty_preferences_do_not_downgrade_hard_requirement_match(self):
        result = match_tool(
            make_tool("local.text", capabilities=("text",)),
            ToolRequirements(required_capabilities=("text",)),
        )

        self.assertEqual(result.classification, MatchClassification.EXACT_MATCH)
        self.assertTrue(result.qualifies)
        self.assertEqual(result.score, 0)

    def test_reason_codes_have_stable_documented_order(self):
        result = match_tool(
            make_tool("local.disabled", capabilities=("text",), enabled=False),
            ToolRequirements(
                required_capabilities=("text",),
                preferred_capabilities=("statistics",),
            ),
        )

        self.assertEqual(
            result.reason_codes,
            (
                "required_capabilities_matched",
                "preferred_capabilities_unmet",
                "disabled_tool",
                "tool_state_excluded",
                "hard_requirement_or_eligibility_failed",
            ),
        )

    def test_incompatible_match_configuration_is_typed(self):
        with self.assertRaises(InvalidMatchingConfigurationError):
            match_tool(cast(Any, object()), ToolRequirements())
        with self.assertRaises(InvalidMatchingConfigurationError):
            match_tool(make_tool("local.tool"), cast(Any, object()))


class ToolSelectionPlanTests(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.registry.register(
            make_tool("local.alpha", capabilities=("text", "statistics"))
        )
        self.registry.register(make_tool("local.beta", capabilities=("text",)))

    def test_selects_unique_best_candidate_by_preference_score(self):
        plan = plan_tool_selection(
            self.registry,
            ToolRequirements(
                required_capabilities=("text",),
                preferred_capabilities=("statistics",),
            ),
        )

        self.assertEqual(plan.status, SelectionStatus.SELECTED)
        self.assertEqual(plan.selected_tool_identifier, "local.alpha")
        self.assertEqual(plan.reason_code, "unique_highest_match")

    def test_equal_top_candidates_are_ambiguous_not_first_selected(self):
        plan = plan_tool_selection(
            self.registry,
            ToolRequirements(required_capabilities=("text",)),
        )

        self.assertEqual(plan.status, SelectionStatus.AMBIGUOUS)
        self.assertIsNone(plan.selected_tool_identifier)
        self.assertEqual(
            [candidate.tool_identifier for candidate in plan.candidates],
            ["local.alpha", "local.beta"],
        )

    def test_no_hard_requirement_match_has_explicit_no_match_result(self):
        plan = plan_tool_selection(
            self.registry,
            ToolRequirements(required_capabilities=("network",)),
        )

        self.assertEqual(plan.status, SelectionStatus.NO_MATCH)
        self.assertIsNone(plan.selected_tool_identifier)
        self.assertEqual(plan.reason_code, "no_qualifying_candidate")

    def test_disabled_and_unavailable_selection_is_explicit_and_non_executable(self):
        registry = ToolRegistry()
        disabled = make_tool("local.disabled", enabled=False)
        unavailable = make_tool(
            "local.unavailable",
            availability=ExecutionAvailability.UNAVAILABLE,
        )
        registry.register(disabled)
        registry.register(unavailable)

        excluded = plan_tool_selection(registry, ToolRequirements())
        included_disabled = plan_tool_selection(
            registry,
            ToolRequirements(include_disabled=True),
        )
        included_unavailable = plan_tool_selection(
            registry,
            ToolRequirements(include_unavailable=True),
        )

        self.assertEqual(excluded.status, SelectionStatus.NO_MATCH)
        self.assertEqual(included_disabled.status, SelectionStatus.SELECTED)
        self.assertEqual(
            included_disabled.selected_tool_identifier, "local.disabled"
        )
        disabled_match = included_disabled.candidates[0]
        self.assertTrue(disabled_match.eligible)
        self.assertFalse(disabled_match.contract_execution_state_available)
        self.assertIn(
            "selection_does_not_imply_executable", disabled_match.reason_codes
        )
        self.assertEqual(included_unavailable.status, SelectionStatus.SELECTED)
        unavailable_match = included_unavailable.candidates[1]
        self.assertTrue(unavailable_match.eligible)
        self.assertFalse(unavailable_match.contract_execution_state_available)

    def test_discovery_only_reports_matches_without_selecting_or_invoking(self):
        calls: list[str] = []
        registry = ToolRegistry()
        contract = ToolContract(
            "local.counted",
            "Counted",
            "Counter proving the planner is metadata-only.",
            input_schema=(InputField("text", InputType.STRING),),
            capabilities=("text",),
            adapter_id="local.counted",
            execution_availability=ExecutionAvailability.AVAILABLE,
        )
        registry.register(contract)
        executor = ToolExecutor(registry)

        def implementation(inputs):
            calls.append(str(inputs["text"]))
            return {"ok": True}

        executor.register_adapter(
            LocalToolAdapter("local.counted", {"local.counted": implementation})
        )

        discovery = discover_tools(registry)
        plan = plan_tool_selection(
            registry,
            ToolRequirements(required_capabilities=("text",)),
            discovery_only=True,
        )

        self.assertEqual(discovery.tools, (contract,))
        self.assertEqual(plan.status, SelectionStatus.DISCOVERY_ONLY)
        self.assertIsNone(plan.selected_tool_identifier)
        self.assertEqual(plan.candidates[0].classification, MatchClassification.EXACT_MATCH)
        self.assertEqual(plan.candidates[0].tool_name, contract.name)
        self.assertEqual(plan.candidates[0].declared_capabilities, ("text",))
        self.assertTrue(plan.candidates[0].contract_execution_state_available)
        self.assertEqual(calls, [])

    def test_existing_p076_registration_and_execution_api_remains_compatible(self):
        registry = ToolRegistry()
        executor = ToolExecutor(registry)
        register_text_statistics(registry, executor)

        result = plan_tool_selection(
            registry,
            ToolRequirements(
                required_tool_identifiers=("local.text-statistics",),
                required_input_names=("text",),
            ),
        )

        self.assertEqual(result.status, SelectionStatus.SELECTED)
        self.assertEqual(
            result.selected_tool_identifier,
            "local.text-statistics",
        )
        self.assertEqual(
            discover_tools(registry).tools[0].identifier,
            "local.text-statistics",
        )


if __name__ == "__main__":
    unittest.main()

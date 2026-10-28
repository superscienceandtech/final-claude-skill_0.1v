"""Tests for preflighted, sequential tool workflow execution."""

from __future__ import annotations

import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Any, Mapping, cast
from unittest.mock import patch

import scripts.tool_workflow as workflow_module
from scripts.tool_framework import (
    ExecutionAvailability,
    InputField,
    InputType,
    LocalToolAdapter,
    ToolContract,
    ToolExecutionResult,
    ToolExecutor,
    ToolRegistry,
    ToolRuntimeError,
    ToolStatus,
    UnknownToolError,
)
from scripts.tool_workflow import (
    DuplicateWorkflowError,
    EvictedWorkflowRunError,
    FailureCategory,
    InvalidStepInputMappingError,
    InvalidWorkflowDefinitionError,
    StepOutputRef,
    StepStatus,
    UnknownWorkflowError,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowEventType,
    WorkflowCancellationRequested,
    WorkflowCancellationToken,
    WorkflowFailurePolicy,
    WorkflowInputRef,
    WorkflowObservabilityIssue,
    WorkflowRegistry,
    WorkflowResult,
    UnknownWorkflowRunError,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStepResult,
    WorkflowValidationCategory,
    _resolve_step_inputs,
    validate_workflow,
)


def _contract(
    identifier: str,
    inputs: tuple[tuple[str, InputType], ...],
    *,
    enabled: bool = True,
    availability: ExecutionAvailability = ExecutionAvailability.AVAILABLE,
) -> ToolContract:
    return ToolContract(
        identifier=identifier,
        name=identifier,
        description=f"Test tool {identifier}.",
        input_schema=tuple(InputField(name, kind) for name, kind in inputs),
        adapter_id="local.workflow",
        enabled=enabled,
        execution_availability=availability,
    )


class WorkflowDefinitionTests(unittest.TestCase):
    def test_valid_definition_is_immutable_and_ordered(self):
        mapping = {"text": WorkflowInputRef("source")}
        step = WorkflowStep("first", "local.stats", mapping)
        workflow = WorkflowDefinition("example", "Example", (step,))
        cast(Any, mapping)["text"] = "changed"

        self.assertIsInstance(step.input_mapping["text"], WorkflowInputRef)
        self.assertEqual(workflow.steps, (step,))
        with self.assertRaises(TypeError):
            cast(Any, step.input_mapping)["text"] = "mutated"

    def test_rejects_invalid_workflow_identifiers_policies_and_empty_steps(self):
        step = WorkflowStep("first", "local.stats", {})
        for identifier in ("", "Bad_ID"):
            with self.subTest(identifier=identifier):
                with self.assertRaises(InvalidWorkflowDefinitionError):
                    WorkflowDefinition(identifier, "Example", (step,))
        with self.assertRaises(InvalidWorkflowDefinitionError):
            WorkflowDefinition("example", "Example", ())
        with self.assertRaises(InvalidWorkflowDefinitionError):
            WorkflowDefinition(
                "example",
                "Example",
                (step,),
                failure_policy=cast(Any, "continue"),
            )

    def test_rejects_duplicate_steps_unknown_dependencies_and_self_dependency(self):
        first = WorkflowStep("same", "local.stats", {})
        with self.assertRaisesRegex(InvalidWorkflowDefinitionError, "duplicate step"):
            WorkflowDefinition("example", "Example", (first, first))
        with self.assertRaisesRegex(InvalidWorkflowDefinitionError, "unknown dependency"):
            WorkflowDefinition(
                "example",
                "Example",
                (WorkflowStep("first", "local.stats", {}, depends_on=("missing",)),),
            )
        with self.assertRaisesRegex(InvalidWorkflowDefinitionError, "itself"):
            WorkflowDefinition(
                "example",
                "Example",
                (WorkflowStep("first", "local.stats", {}, depends_on=("first",)),),
            )

    def test_rejects_circular_and_forward_dependencies(self):
        a = WorkflowStep("a", "local.stats", {}, depends_on=("b",))
        b = WorkflowStep("b", "local.stats", {}, depends_on=("a",))
        with self.assertRaisesRegex(InvalidWorkflowDefinitionError, "circular"):
            WorkflowDefinition("example", "Example", (a, b))

        with self.assertRaisesRegex(InvalidWorkflowDefinitionError, "must appear before"):
            WorkflowDefinition(
                "example",
                "Example",
                (
                    WorkflowStep("first", "local.stats", {}, depends_on=("later",)),
                    WorkflowStep("later", "local.stats", {}),
                ),
            )

    def test_rejects_malformed_mappings_and_nested_reference_expressions(self):
        with self.assertRaises(InvalidStepInputMappingError):
            WorkflowStep("first", "local.stats", cast(Any, "not a mapping"))
        with self.assertRaises(InvalidStepInputMappingError):
            WorkflowStep("first", "local.stats", {"bad name": "value"})
        with self.assertRaisesRegex(InvalidStepInputMappingError, "top-level"):
            WorkflowStep("first", "local.stats", {"tags": [WorkflowInputRef("tag")]})
        with self.assertRaises(InvalidStepInputMappingError):
            WorkflowStep("first", "local.stats", {"value": object()})
        with self.assertRaisesRegex(InvalidStepInputMappingError, "unsupported literal"):
            WorkflowStep("first", "local.stats", {"value": ("not", "json")})


class WorkflowValidationTests(unittest.TestCase):
    def _workflow_with_steps(
        self, steps: tuple[WorkflowStep, ...]
    ) -> WorkflowDefinition:
        workflow = WorkflowDefinition(
            "validation.example",
            "Validation example",
            (WorkflowStep("placeholder", "local.stats", {}),),
        )
        object.__setattr__(workflow, "steps", steps)
        return workflow

    def test_valid_one_step_chain_and_independent_workflows_report_graph(self):
        one_step = WorkflowDefinition(
            "validation.one",
            "One step",
            (WorkflowStep("first", "local.stats", {}),),
        )
        chain = WorkflowDefinition(
            "validation.chain",
            "Chain",
            (
                WorkflowStep("first", "local.stats", {}),
                WorkflowStep(
                    "second",
                    "local.stats",
                    {"text": StepOutputRef("first", "characters")},
                ),
                WorkflowStep("third", "local.stats", {}, depends_on=("second",)),
            ),
        )
        independent = WorkflowDefinition(
            "validation.independent",
            "Independent",
            (
                WorkflowStep("alpha", "local.stats", {}),
                WorkflowStep("beta", "local.stats", {}),
            ),
        )

        one_result = validate_workflow(one_step)
        chain_result = validate_workflow(chain)
        independent_result = validate_workflow(independent)

        self.assertTrue(one_result.valid)
        self.assertEqual(one_result.dependency_graph, {"first": ()})
        self.assertTrue(chain_result.valid)
        self.assertEqual(
            chain_result.dependency_graph,
            {"first": (), "second": ("first",), "third": ("second",)},
        )
        self.assertEqual(
            chain_result.declared_step_order,
            ("first", "second", "third"),
        )
        self.assertTrue(independent_result.valid)
        self.assertEqual(
            independent_result.dependency_graph,
            {"alpha": (), "beta": ()},
        )
        with self.assertRaises(TypeError):
            cast(Any, chain_result.dependency_graph)["first"] = ("third",)

    def test_validation_reports_unknown_self_and_duplicate_dependencies(self):
        unknown = WorkflowStep("step", "local.stats", {}, depends_on=("missing",))
        unknown_result = validate_workflow(self._workflow_with_steps((unknown,)))
        self.assertIn("unknown_dependency", [i.error_code for i in unknown_result.issues])

        self_dependent = WorkflowStep("step", "local.stats", {})
        object.__setattr__(self_dependent, "depends_on", ("step",))
        self_result = validate_workflow(self._workflow_with_steps((self_dependent,)))
        self.assertIn("self_dependency", [i.error_code for i in self_result.issues])

        duplicate_dependencies = WorkflowStep("step", "local.stats", {})
        object.__setattr__(
            duplicate_dependencies, "depends_on", ("other", "other")
        )
        duplicate_result = validate_workflow(
            self._workflow_with_steps((duplicate_dependencies,))
        )
        self.assertIn(
            "duplicate_dependency",
            [i.error_code for i in duplicate_result.issues],
        )
        self.assertEqual(
            duplicate_result.issues[0].category,
            WorkflowValidationCategory.DEPENDENCY,
        )

    def test_validation_detects_direct_and_indirect_cycles(self):
        two_node = self._workflow_with_steps(
            (
                WorkflowStep("alpha", "local.stats", {}, depends_on=("beta",)),
                WorkflowStep("beta", "local.stats", {}, depends_on=("alpha",)),
            )
        )
        three_node = self._workflow_with_steps(
            (
                WorkflowStep("alpha", "local.stats", {}, depends_on=("gamma",)),
                WorkflowStep("beta", "local.stats", {}, depends_on=("alpha",)),
                WorkflowStep("gamma", "local.stats", {}, depends_on=("beta",)),
            )
        )

        direct_codes = {i.error_code for i in validate_workflow(two_node).issues}
        indirect = validate_workflow(three_node)
        indirect_cycle_steps = {
            issue.step_id
            for issue in indirect.issues
            if issue.error_code == "dependency_cycle"
        }

        self.assertIn("dependency_cycle", direct_codes)
        self.assertEqual(indirect_cycle_steps, {"alpha", "beta", "gamma"})

    def test_invalid_structure_duplicate_ids_and_bad_dependency_are_machine_readable(self):
        missing_id = WorkflowStep("valid", "local.stats", {})
        object.__delattr__(missing_id, "step_id")
        missing_id_result = validate_workflow(
            self._workflow_with_steps((missing_id,))
        )
        self.assertIn(
            "invalid_step_identifier",
            [issue.error_code for issue in missing_id_result.issues],
        )

        invalid_id = WorkflowStep("valid", "local.stats", {})
        object.__setattr__(invalid_id, "step_id", "SECRET MARKER")
        invalid_id_result = validate_workflow(
            self._workflow_with_steps((invalid_id,))
        )
        self.assertIn(
            "invalid_step_identifier",
            [issue.error_code for issue in invalid_id_result.issues],
        )
        self.assertNotIn("SECRET MARKER", repr(invalid_id_result.issues))

        duplicate = self._workflow_with_steps(
            (
                WorkflowStep("same", "local.stats", {}),
                WorkflowStep("other", "local.stats", {}),
            )
        )
        object.__setattr__(duplicate.steps[1], "step_id", "same")
        duplicate_result = validate_workflow(duplicate)
        self.assertIn(
            "duplicate_step_identifier",
            [issue.error_code for issue in duplicate_result.issues],
        )

        bad_dependency = WorkflowStep("step", "local.stats", {})
        object.__setattr__(bad_dependency, "depends_on", ("SECRET MARKER",))
        bad_dependency_result = validate_workflow(
            self._workflow_with_steps((bad_dependency,))
        )
        self.assertIn(
            "invalid_dependency_identifier",
            [issue.error_code for issue in bad_dependency_result.issues],
        )
        self.assertNotIn("SECRET MARKER", repr(bad_dependency_result.issues))

        unsupported_literal = WorkflowStep("step", "local.stats", {})
        object.__setattr__(
            unsupported_literal,
            "input_mapping",
            {"text": object()},
        )
        literal_result = validate_workflow(
            self._workflow_with_steps((unsupported_literal,))
        )
        self.assertIn(
            "invalid_literal_input",
            [issue.error_code for issue in literal_result.issues],
        )

    def test_results_are_deterministic_and_graph_walk_is_iterative(self):
        cyclic = self._workflow_with_steps(
            (
                WorkflowStep("alpha", "local.stats", {}, depends_on=("gamma",)),
                WorkflowStep("beta", "local.stats", {}, depends_on=("alpha",)),
                WorkflowStep("gamma", "local.stats", {}, depends_on=("beta",)),
            )
        )
        first = validate_workflow(cyclic)
        second = validate_workflow(cyclic)
        self.assertEqual(first.issues, second.issues)
        self.assertEqual(first.dependency_graph, second.dependency_graph)

        steps = tuple(
            WorkflowStep(
                f"step-{index}",
                "local.stats",
                {},
                depends_on=(f"step-{index - 1}",) if index else (),
            )
            for index in range(1400)
        )
        deep_chain = WorkflowDefinition(
            "validation.deep-chain",
            "Deep chain",
            steps,
        )
        self.assertTrue(validate_workflow(deep_chain).valid)

    def test_constructor_still_rejects_empty_and_forward_dependency_workflows(self):
        with self.assertRaisesRegex(InvalidWorkflowDefinitionError, "at least one step"):
            WorkflowDefinition("validation.empty", "Empty", ())
        forward = self._workflow_with_steps(
            (
                WorkflowStep("first", "local.stats", {}, depends_on=("second",)),
                WorkflowStep("second", "local.stats", {}),
            )
        )
        forward_result = validate_workflow(forward)
        self.assertIn(
            "forward_dependency",
            [issue.error_code for issue in forward_result.issues],
        )
        with self.assertRaisesRegex(InvalidWorkflowDefinitionError, "must appear before"):
            WorkflowDefinition(
                "validation.forward",
                "Forward dependency",
                (
                    WorkflowStep("first", "local.stats", {}, depends_on=("second",)),
                    WorkflowStep("second", "local.stats", {}),
                ),
            )


class WorkflowRegistryTests(unittest.TestCase):
    def test_registers_lists_deterministically_and_reports_duplicates_or_unknown(self):
        registry = WorkflowRegistry()
        first = WorkflowDefinition(
            "workflow.zeta",
            "Zeta",
            (WorkflowStep("step", "local.stats", {}),),
        )
        second = WorkflowDefinition(
            "workflow.alpha",
            "Alpha",
            (WorkflowStep("step", "local.stats", {}),),
        )
        registry.register(first)
        registry.register(second)
        self.assertEqual(
            [workflow.identifier for workflow in registry.list_workflows()],
            ["workflow.alpha", "workflow.zeta"],
        )
        with self.assertRaises(DuplicateWorkflowError):
            registry.register(first)
        with self.assertRaises(UnknownWorkflowError):
            registry.get("missing")


class WorkflowEngineTests(unittest.TestCase):
    def setUp(self):
        self.calls: list[tuple[str, object]] = []
        self.tools = ToolRegistry()
        self.executor = ToolExecutor(self.tools)
        self.workflows = WorkflowRegistry()
        self._register(
            _contract("local.stats", (("text", InputType.STRING),)),
            self._statistics,
        )
        self._register(
            _contract("local.describe-count", (("count", InputType.INTEGER),)),
            self._describe_count,
        )
        self._register(
            _contract("local.failure", (("text", InputType.STRING),)),
            self._failure,
        )
        self._register(
            _contract("local.independent", (("text", InputType.STRING),)),
            self._independent,
        )
        self.engine = WorkflowEngine(self.workflows, self.tools, self.executor)

    def test_engine_rejects_executor_bound_to_a_different_tool_registry(self):
        with self.assertRaisesRegex(
            InvalidWorkflowDefinitionError, "must share the same ToolRegistry"
        ):
            WorkflowEngine(
                self.workflows,
                self.tools,
                ToolExecutor(ToolRegistry()),
            )

    def _register(self, contract: ToolContract, implementation) -> None:
        self.tools.register(contract)
        self._implementations = getattr(self, "_implementations", {})
        self._implementations[contract.identifier] = implementation
        if len(self._implementations) == 4:
            self.executor.register_adapter(
                LocalToolAdapter("local.workflow", self._implementations)
            )

    def _statistics(self, inputs):
        text = inputs["text"]
        self.calls.append(("stats", text))
        return {"characters": len(text), "words": len(text.split())}

    def _describe_count(self, inputs):
        count = inputs["count"]
        self.calls.append(("describe", count))
        return {"summary": f"{count} characters"}

    def _failure(self, inputs):
        self.calls.append(("failure", inputs["text"]))
        raise RuntimeError("private implementation detail")

    def _independent(self, inputs):
        self.calls.append(("independent", inputs["text"]))
        return {"ok": True}

    def _workflow(
        self,
        steps: tuple[WorkflowStep, ...],
        *,
        policy: WorkflowFailurePolicy = WorkflowFailurePolicy.STOP_ON_FAILURE,
        identifier: str = "workflow.example",
    ) -> WorkflowDefinition:
        workflow = WorkflowDefinition(
            identifier,
            "Example workflow",
            steps,
            failure_policy=policy,
        )
        self.workflows.register(workflow)
        return workflow

    def test_unknown_tool_and_invalid_mapping_preflight_without_execution(self):
        self._workflow(
            (WorkflowStep("step", "local.unknown", {"text": "hello"}),)
        )
        result = self.engine.execute("workflow.example")
        self.assertEqual(result.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertFalse(result.execution_began)
        self.assertEqual(result.preflight_issues[0].error_code, "unknown_tool")
        self.assertEqual(self.calls, [])

        self.workflows = WorkflowRegistry()
        self.engine = WorkflowEngine(self.workflows, self.tools, self.executor)
        self._workflow(
            (WorkflowStep("step", "local.stats", {"wrong": "value"}),),
            identifier="workflow.invalid-input",
        )
        invalid = self.engine.execute("workflow.invalid-input")
        self.assertEqual(invalid.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertEqual(self.calls, [])

    def test_literal_and_workflow_input_mapping_preflight_and_execute(self):
        self._workflow(
            (
                WorkflowStep(
                    "stats",
                    "local.stats",
                    {"text": WorkflowInputRef("message")},
                ),
                WorkflowStep(
                    "describe",
                    "local.describe-count",
                    {"count": StepOutputRef("stats", "characters")},
                ),
            )
        )

        preflight = self.engine.preflight(
            "workflow.example", {"message": "hello world"}
        )
        with patch.object(
            self.executor, "invoke", wraps=self.executor.invoke
        ) as invoke:
            result = self.engine.execute(
                "workflow.example", {"message": "hello world"}
            )

        self.assertTrue(preflight.valid)
        self.assertEqual(invoke.call_count, 2)
        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)
        self.assertTrue(result.success)
        self.assertEqual(
            result.successful_step_count
            + result.failed_step_count
            + result.skipped_step_count,
            len(result.step_results),
        )
        self.assertEqual(
            [call[0] for call in self.calls],
            ["stats", "describe"],
        )
        self.assertEqual(self.calls[1], ("describe", 11))
        self.assertEqual(result.successful_step_count, 2)
        self.assertEqual(result.failed_step_count, 0)
        self.assertEqual(result.skipped_step_count, 0)
        self.assertTrue(result.execution_began)
        self.assertTrue(result.execution_completed)
        self.assertEqual(
            result.step_results[0].output_metadata[0].name,
            "characters",
        )
        tool_result = result.step_results[0].tool_result
        self.assertIsInstance(tool_result, ToolExecutionResult)
        if tool_result is None:
            self.fail("successful step should include a structured Tool result")
        self.assertIsNone(tool_result.output)
        self.assertFalse(result.outputs_included)

    def test_literal_input_is_passed_and_opted_in_outputs_are_available(self):
        self._workflow(
            (
                WorkflowStep("stats", "local.stats", {"text": "literal"}),
                WorkflowStep(
                    "describe",
                    "local.describe-count",
                    {"count": StepOutputRef("stats", "characters")},
                ),
            )
        )

        result = self.engine.execute("workflow.example", include_outputs=True)

        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)
        self.assertEqual(self.calls[0], ("stats", "literal"))
        tool_result = result.step_results[0].tool_result
        self.assertIsInstance(tool_result, ToolExecutionResult)
        if tool_result is None or tool_result.output is None:
            self.fail("opted-in trace should retain successful Tool output")
        self.assertEqual(tool_result.output["characters"], 7)
        self.assertTrue(result.outputs_included)

    def test_workflow_input_string_list_is_copied_and_type_checked(self):
        tools = ToolRegistry()
        contract = _contract(
            "local.list",
            (("items", InputType.STRING_LIST),),
        )
        tools.register(contract)
        executor = ToolExecutor(tools)
        observed: list[list[str]] = []

        def capture_items(inputs: Mapping[str, object]) -> Mapping[str, object]:
            items = inputs["items"]
            if not isinstance(items, list) or any(
                not isinstance(item, str) for item in items
            ):
                raise ValueError("items must be a list of strings")
            observed.append(list(items))
            return {"count": len(items)}

        executor.register_adapter(
            LocalToolAdapter(
                "local.workflow",
                {"local.list": capture_items},
            )
        )
        workflows = WorkflowRegistry()
        workflows.register(
            WorkflowDefinition(
                "workflow.list",
                "List workflow",
                (
                    WorkflowStep(
                        "list",
                        "local.list",
                        {"items": WorkflowInputRef("items")},
                    ),
                ),
            )
        )
        engine = WorkflowEngine(workflows, tools, executor)
        provided = ["one", "two"]
        preflight = engine.preflight("workflow.list", {"items": provided})
        result = engine.execute("workflow.list", {"items": provided})

        self.assertTrue(preflight.valid)
        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)
        self.assertEqual(observed, [["one", "two"]])

    def test_missing_workflow_input_and_output_field_are_reported(self):
        self._workflow(
            (WorkflowStep("stats", "local.stats", {"text": WorkflowInputRef("message")}),)
        )
        missing_input = self.engine.execute("workflow.example")
        self.assertEqual(missing_input.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertEqual(
            missing_input.preflight_issues[0].error_code,
            "missing_workflow_input",
        )
        self.assertFalse(missing_input.execution_began)
        self.assertEqual(self.calls, [])

        self.workflows = WorkflowRegistry()
        self.engine = WorkflowEngine(self.workflows, self.tools, self.executor)
        self._workflow(
            (
                WorkflowStep("stats", "local.stats", {"text": "hello"}),
                WorkflowStep(
                    "describe",
                    "local.describe-count",
                    {"count": StepOutputRef("stats", "missing")},
                ),
            )
        )
        missing_output = self.engine.execute("workflow.example")
        self.assertEqual(missing_output.status, WorkflowStatus.PARTIAL)
        self.assertEqual(
            missing_output.step_results[1].status,
            StepStatus.INPUT_RESOLUTION_FAILED,
        )
        self.assertEqual(
            missing_output.step_results[1].error_code,
            "missing_step_output",
        )
        self.assertIsNone(missing_output.step_results[1].tool_result)

    def test_stop_on_failure_stops_and_marks_remaining_steps(self):
        self._workflow(
            (
                WorkflowStep("fail", "local.failure", {"text": "bad"}),
                WorkflowStep("later", "local.independent", {"text": "not run"}),
            )
        )

        result = self.engine.execute("workflow.example")

        self.assertEqual(result.status, WorkflowStatus.FAILED)
        self.assertEqual(result.failed_step_count, 1)
        self.assertEqual(result.skipped_step_count, 1)
        self.assertEqual(
            [step.status for step in result.step_results],
            [StepStatus.TOOL_FAILED, StepStatus.SKIPPED_POLICY],
        )
        self.assertEqual(self.calls, [("failure", "bad")])
        tool_result = result.step_results[0].tool_result
        self.assertIsInstance(tool_result, ToolExecutionResult)
        if tool_result is None:
            self.fail("failed invocation should retain its structured Tool result")
        self.assertNotIn("private implementation detail", str(tool_result.error))

    def test_continue_independent_skips_dependents_but_runs_independent_steps(self):
        self._workflow(
            (
                WorkflowStep("fail", "local.failure", {"text": "bad"}),
                WorkflowStep(
                    "dependent",
                    "local.describe-count",
                    {"count": StepOutputRef("fail", "characters")},
                ),
                WorkflowStep(
                    "independent",
                    "local.independent",
                    {"text": "safe"},
                    depends_on=("fail",),
                ),
                WorkflowStep(
                    "unrelated",
                    "local.independent",
                    {"text": "also safe"},
                ),
            ),
            policy=WorkflowFailurePolicy.CONTINUE_INDEPENDENT,
        )
        # The explicit dependency intentionally makes step 3 dependent; step 4
        # proves truly independent work can continue.

        result = self.engine.execute("workflow.example")

        self.assertEqual(result.status, WorkflowStatus.PARTIAL)
        self.assertEqual(result.failed_step_count, 1)
        self.assertEqual(result.skipped_step_count, 2)
        self.assertEqual(
            [step.status for step in result.step_results],
            [
                StepStatus.TOOL_FAILED,
                StepStatus.SKIPPED_DEPENDENCY,
                StepStatus.SKIPPED_DEPENDENCY,
                StepStatus.SUCCEEDED,
            ],
        )
        self.assertEqual(
            self.calls,
            [("failure", "bad"), ("independent", "also safe")],
        )

    def test_preflight_type_or_contract_state_failure_prevents_every_call(self):
        self._workflow(
            (
                WorkflowStep("first", "local.stats", {"text": 123}),
                WorkflowStep("second", "local.independent", {"text": "not run"}),
            )
        )
        mismatch = self.engine.execute("workflow.example")
        self.assertEqual(mismatch.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertFalse(mismatch.execution_began)
        self.assertEqual(self.calls, [])

        self.tools.register(
            _contract(
                "local.disabled",
                (("text", InputType.STRING),),
                enabled=False,
            )
        )
        self.workflows = WorkflowRegistry()
        self.engine = WorkflowEngine(self.workflows, self.tools, self.executor)
        self._workflow(
            (WorkflowStep("disabled", "local.disabled", {"text": "no"}),),
            identifier="workflow.disabled",
        )
        disabled = self.engine.execute("workflow.disabled")
        self.assertEqual(disabled.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertIn("tool_disabled", [issue.error_code for issue in disabled.preflight_issues])
        self.assertEqual(self.calls, [])

        self.tools.register(
            _contract(
                "local.unavailable",
                (("text", InputType.STRING),),
                availability=ExecutionAvailability.UNAVAILABLE,
            )
        )
        self.workflows = WorkflowRegistry()
        self.engine = WorkflowEngine(self.workflows, self.tools, self.executor)
        self._workflow(
            (WorkflowStep("unavailable", "local.unavailable", {"text": "no"}),),
            identifier="workflow.unavailable",
        )
        unavailable = self.engine.execute("workflow.unavailable")
        self.assertEqual(unavailable.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertIn(
            "execution_unavailable",
            [issue.error_code for issue in unavailable.preflight_issues],
        )
        self.assertEqual(self.calls, [])

    def test_missing_adapter_is_reported_as_tool_invocation_failure(self):
        unavailable_registry = ToolRegistry()
        contract = ToolContract(
            "local.no-adapter",
            "No adapter",
            "Available contract but no registered adapter.",
            input_schema=(InputField("text", InputType.STRING),),
            adapter_id="local.missing",
            execution_availability=ExecutionAvailability.AVAILABLE,
        )
        unavailable_registry.register(contract)
        executor = ToolExecutor(unavailable_registry)
        workflows = WorkflowRegistry()
        workflows.register(
            WorkflowDefinition(
                "workflow.missing-adapter",
                "Missing adapter",
                (WorkflowStep("step", "local.no-adapter", {"text": "hello"}),),
            )
        )
        engine = WorkflowEngine(workflows, unavailable_registry, executor)

        result = engine.execute("workflow.missing-adapter")

        self.assertEqual(result.status, WorkflowStatus.FAILED)
        self.assertEqual(result.step_results[0].status, StepStatus.TOOL_FAILED)
        self.assertEqual(result.step_results[0].error_code, "adapter_missing")
        self.assertEqual(
            result.step_results[0].failure_category,
            FailureCategory.TOOL_INVOCATION,
        )

    def test_sensitive_inputs_are_not_in_default_trace_metadata(self):
        secret = "private user payload"
        self._workflow(
            (WorkflowStep("stats", "local.stats", {"text": WorkflowInputRef("message")}),)
        )

        result = self.engine.execute("workflow.example", {"message": secret})
        serialized_trace = repr(result)

        self.assertNotIn(secret, serialized_trace)
        self.assertEqual(result.step_results[0].input_metadata[0].name, "text")
        self.assertEqual(
            result.step_results[0].input_metadata[0].source.value,
            "workflow_input",
        )

    def test_no_invocation_during_definition_or_preflight_validation(self):
        calls: list[str] = []
        contract = _contract("local.counted", (("text", InputType.STRING),))
        self.tools.register(contract)
        # Existing adapter cannot add implementations after registration, so
        # use a separate executor/registry to instrument an isolated tool.
        isolated_tools = ToolRegistry()
        isolated_tools.register(contract)
        isolated_executor = ToolExecutor(isolated_tools)
        isolated_executor.register_adapter(
            LocalToolAdapter(
                "local.workflow",
                {
                    "local.counted": lambda inputs: calls.append(
                        str(inputs["text"])
                    )
                    or {"ok": True}
                },
            )
        )
        isolated_workflows = WorkflowRegistry()
        definition = WorkflowDefinition(
            "workflow.counted",
            "Counted",
            (WorkflowStep("step", "local.counted", {"text": "literal"}),),
        )
        isolated_workflows.register(definition)
        engine = WorkflowEngine(isolated_workflows, isolated_tools, isolated_executor)

        self.assertTrue(engine.preflight("workflow.counted").valid)
        self.assertEqual(calls, [])

    def test_invalid_registered_workflow_is_rejected_before_executor_invocation(self):
        workflow = self._workflow(
            (
                WorkflowStep("first", "local.stats", {"text": "secret input"}),
                WorkflowStep("second", "local.independent", {"text": "not run"}),
            )
        )
        object.__setattr__(
            workflow,
            "steps",
            (
                WorkflowStep(
                    "first",
                    "local.stats",
                    {"text": "secret input"},
                    depends_on=("second",),
                ),
                WorkflowStep(
                    "second",
                    "local.independent",
                    {"text": "not run"},
                    depends_on=("first",),
                ),
            ),
        )

        with patch.object(
            self.executor, "invoke", wraps=self.executor.invoke
        ) as invoke:
            result = self.engine.execute("workflow.example")

        self.assertEqual(invoke.call_count, 0)
        self.assertEqual(self.calls, [])
        self.assertEqual(result.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertFalse(result.execution_began)
        self.assertTrue(result.validation_issues)
        self.assertEqual(result.events[1].error_code, "workflow_validation_failed")
        self.assertEqual(result.events[-1].event_type, WorkflowEventType.WORKFLOW_FAILED)
        self.assertEqual(result.events[-1].error_code, "workflow_validation_failed")
        snapshot = self.engine.inspect_run(result.run_id)
        self.assertEqual(snapshot.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertIn("dependency_cycle", snapshot.failure_codes)
        self.assertNotIn("secret input", repr(result.validation_issues))

    def test_workflow_registry_revalidates_definitions_before_registering(self):
        workflow = WorkflowDefinition(
            "workflow.registry-validation",
            "Registry validation",
            (WorkflowStep("first", "local.stats", {}),),
        )
        object.__setattr__(
            workflow,
            "steps",
            (WorkflowStep("first", "local.stats", {}, depends_on=("missing",)),),
        )
        registry = WorkflowRegistry()

        with self.assertRaisesRegex(InvalidWorkflowDefinitionError, "unknown dependency"):
            registry.register(workflow)
        self.assertEqual(registry.list_workflows(), ())

    def test_ordered_results_and_counts_are_deterministic(self):
        self._workflow(
            (
                WorkflowStep("first", "local.stats", {"text": "a"}),
                WorkflowStep("second", "local.independent", {"text": "b"}),
            )
        )
        result = self.engine.execute("workflow.example")

        self.assertEqual(
            [step.step_id for step in result.step_results],
            ["first", "second"],
        )
        self.assertEqual(
            (result.successful_step_count, result.failed_step_count, result.skipped_step_count),
            (2, 0, 0),
        )
        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)

    def test_successful_run_emits_ordered_lifecycle_events_and_snapshot(self):
        self._workflow(
            (
                WorkflowStep("first", "local.stats", {"text": "hello"}),
                WorkflowStep("second", "local.independent", {"text": "safe"}),
            )
        )

        result = self.engine.execute("workflow.example")
        expected_types = (
            WorkflowEventType.RUN_STARTED,
            WorkflowEventType.PREFLIGHT_COMPLETED,
            WorkflowEventType.STEP_STARTED,
            WorkflowEventType.STEP_SUCCEEDED,
            WorkflowEventType.STEP_STARTED,
            WorkflowEventType.STEP_SUCCEEDED,
            WorkflowEventType.WORKFLOW_COMPLETED,
        )

        self.assertEqual(tuple(event.event_type for event in result.events), expected_types)
        self.assertEqual(
            tuple(event.sequence_number for event in result.events),
            tuple(range(1, len(result.events) + 1)),
        )
        self.assertEqual(result.events[-1].status, WorkflowStatus.SUCCEEDED.value)
        self.assertEqual(
            sum(
                event.event_type
                in (
                    WorkflowEventType.WORKFLOW_COMPLETED,
                    WorkflowEventType.WORKFLOW_FAILED,
                    WorkflowEventType.WORKFLOW_PARTIAL,
                )
                for event in result.events
            ),
            1,
        )
        snapshot = self.engine.inspect_run(result.run_id)
        self.assertEqual(snapshot.events, result.events)
        self.assertEqual(snapshot.status, WorkflowStatus.SUCCEEDED)
        self.assertEqual(snapshot.step_counts[StepStatus.SUCCEEDED], 2)
        self.assertEqual(snapshot.step_counts[StepStatus.TOOL_FAILED], 0)
        self.assertGreaterEqual(snapshot.elapsed_seconds, 0)
        with self.assertRaises(TypeError):
            cast(Any, snapshot.step_counts)[StepStatus.SUCCEEDED] = 10
        with self.assertRaises((AttributeError, TypeError)):
            cast(Any, snapshot).status = WorkflowStatus.FAILED

    def test_structured_tool_failures_are_normalized_and_redacted(self):
        secret = "sensitive adapter diagnostic"
        self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "private input"}),)
        )

        def failed_result(request):
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_identifier=request.tool_identifier,
                status=ToolStatus.FAILED,
                error_code="runtime_failure",
                error=ToolRuntimeError(secret),
            )

        with patch.object(self.executor, "invoke", side_effect=failed_result):
            result = self.engine.execute("workflow.example")

        step_result = result.step_results[0]
        self.assertEqual(result.status, WorkflowStatus.FAILED)
        self.assertFalse(result.success)
        self.assertEqual(step_result.status, StepStatus.TOOL_FAILED)
        self.assertEqual(step_result.error_code, "runtime_failure")
        tool_result = step_result.tool_result
        if tool_result is None:
            self.fail("structured Tool result should be retained for a failed step")
        self.assertIsNone(tool_result.error)
        self.assertNotIn(secret, repr(result))
        self.assertNotIn("private input", repr(result))
        snapshot = self.engine.inspect_run(result.run_id)
        self.assertEqual(snapshot.status, result.status)
        self.assertEqual(snapshot.events, result.events)

    def test_malformed_results_and_invalid_outputs_cannot_report_success(self):
        self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "hello"}),)
        )
        malformed = object()
        with patch.object(self.executor, "invoke", return_value=malformed):
            malformed_result = self.engine.execute("workflow.example")

        self.assertEqual(malformed_result.status, WorkflowStatus.FAILED)
        self.assertEqual(
            malformed_result.step_results[0].error_code,
            "malformed_tool_result",
        )
        self.assertFalse(malformed_result.success)

        def invalid_output(request):
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_identifier=request.tool_identifier,
                status=ToolStatus.SUCCEEDED,
                output={"unsafe": object()},
            )

        with patch.object(self.executor, "invoke", side_effect=invalid_output):
            invalid_output_result = self.engine.execute("workflow.example")

        self.assertEqual(invalid_output_result.status, WorkflowStatus.FAILED)
        self.assertEqual(
            invalid_output_result.step_results[0].error_code,
            "invalid_tool_output",
        )
        self.assertFalse(invalid_output_result.success)

    def test_executor_exception_is_a_terminal_safe_step_failure(self):
        secret = "authorization bearer hidden-value"
        self._workflow(
            (
                WorkflowStep("step", "local.stats", {"text": "safe"}),
                WorkflowStep("later", "local.independent", {"text": "not run"}),
            )
        )
        with patch.object(
            self.executor,
            "invoke",
            side_effect=RuntimeError(secret),
        ):
            result = self.engine.execute("workflow.example")

        self.assertEqual(result.status, WorkflowStatus.FAILED)
        self.assertTrue(result.execution_completed)
        self.assertEqual(
            [step.status for step in result.step_results],
            [StepStatus.INVOCATION_ERROR, StepStatus.SKIPPED_POLICY],
        )
        self.assertEqual(result.step_results[0].error_code, "tool_execution_exception")
        self.assertNotIn(secret, repr(result))
        terminal_events = [
            event
            for event in result.events
            if event.event_type
            in (
                WorkflowEventType.WORKFLOW_COMPLETED,
                WorkflowEventType.WORKFLOW_FAILED,
                WorkflowEventType.WORKFLOW_PARTIAL,
            )
        ]
        self.assertEqual(len(terminal_events), 1)
        self.assertIs(terminal_events[0], result.events[-1])
        snapshot = self.engine.inspect_run(result.run_id)
        self.assertEqual(snapshot.status, result.status)
        self.assertEqual(snapshot.events, result.events)

    def test_tool_removed_after_preflight_is_normalized(self):
        self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "hello"}),)
        )
        original_get = self.tools.get
        calls = 0

        def remove_after_preflight(identifier):
            nonlocal calls
            calls += 1
            if calls == 1:
                return original_get(identifier)
            raise UnknownToolError("removed during execution")

        with patch.object(self.tools, "get", side_effect=remove_after_preflight):
            result = self.engine.execute("workflow.example")

        self.assertEqual(result.status, WorkflowStatus.FAILED)
        self.assertEqual(
            result.step_results[0].error_code,
            "missing_tool_after_preflight",
        )
        self.assertEqual(result.events[-1].event_type, WorkflowEventType.WORKFLOW_FAILED)
        self.assertEqual(self.calls, [])

    def test_unexpected_preflight_error_is_reported_without_execution(self):
        self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "safe"}),)
        )
        secret = "private token diagnostic"
        with patch(
            "scripts.tool_workflow.validate_workflow",
            side_effect=RuntimeError(secret),
        ):
            result = self.engine.execute("workflow.example")

        self.assertEqual(result.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertEqual(result.failure_category, FailureCategory.WORKFLOW_RUNTIME)
        self.assertEqual(result.error_code, "workflow_internal_failure")
        self.assertFalse(result.execution_began)
        self.assertFalse(result.execution_completed)
        self.assertEqual(self.calls, [])
        self.assertNotIn(secret, repr(result))
        snapshot = self.engine.inspect_run(result.run_id)
        self.assertEqual(snapshot.status, result.status)
        self.assertIn("workflow_internal_failure", snapshot.failure_codes)

    def test_snapshot_retention_failure_is_explicit_and_does_not_rewrite_outcome(self):
        self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "hello"}),)
        )
        secret = "private storage diagnostic"
        with patch.object(
            self.engine,
            "_retain_snapshot",
            side_effect=RuntimeError(secret),
        ):
            result = self.engine.execute("workflow.example")

        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)
        self.assertTrue(result.success)
        self.assertEqual(
            result.observability_issues,
            (
                WorkflowObservabilityIssue(
                    "snapshot_retention_failed",
                    "RuntimeError",
                    False,
                ),
            ),
        )
        self.assertEqual(result.events[-1].event_type, WorkflowEventType.WORKFLOW_COMPLETED)
        self.assertNotIn(secret, repr(result))

    def test_snapshot_retention_failure_reports_snapshot_if_already_stored(self):
        self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "hello"}),)
        )
        retain_snapshot = self.engine._retain_snapshot

        def retain_then_raise(snapshot):
            retain_snapshot(snapshot)
            raise RuntimeError("retention reported a late failure")

        with patch.object(
            self.engine,
            "_retain_snapshot",
            side_effect=retain_then_raise,
        ):
            result = self.engine.execute("workflow.example")

        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)
        self.assertEqual(len(result.observability_issues), 1)
        self.assertTrue(result.observability_issues[0].snapshot_available)
        self.assertEqual(self.engine.inspect_run(result.run_id).events, result.events)

    def test_cancellation_before_first_invocation_preserves_preflight_gate(self):
        self._workflow(
            (
                WorkflowStep("first", "local.stats", {"text": "first"}),
                WorkflowStep("second", "local.independent", {"text": "second"}),
            )
        )
        token = WorkflowCancellationToken()
        self.assertTrue(token.request_cancel())
        self.assertFalse(token.request_cancel())
        with patch.object(
            self.executor,
            "invoke",
            wraps=self.executor.invoke,
        ) as invoke:
            result = self.engine.execute(
                "workflow.example",
                cancellation_token=token,
            )

        self.assertEqual(invoke.call_count, 0)
        self.assertEqual(self.calls, [])
        self.assertEqual(result.status, WorkflowStatus.CANCELLED)
        self.assertEqual(result.failure_category, FailureCategory.CANCELLATION)
        self.assertEqual(result.error_code, "workflow_cancelled")
        self.assertTrue(result.cancellation_observed)
        self.assertTrue(result.execution_completed)
        self.assertEqual(result.successful_step_count, 0)
        self.assertEqual(result.failed_step_count, 0)
        self.assertEqual(result.skipped_step_count, 0)
        self.assertEqual(result.cancelled_step_count, 2)
        self.assertEqual(
            [step.status for step in result.step_results],
            [StepStatus.CANCELLED, StepStatus.CANCELLED],
        )
        self.assertEqual(
            [event.event_type for event in result.events],
            [
                WorkflowEventType.RUN_STARTED,
                WorkflowEventType.PREFLIGHT_COMPLETED,
                WorkflowEventType.STEP_CANCELLED,
                WorkflowEventType.STEP_CANCELLED,
                WorkflowEventType.WORKFLOW_CANCELLED,
            ],
        )
        snapshot = self.engine.inspect_run(result.run_id)
        self.assertEqual(snapshot.status, result.status)
        self.assertEqual(snapshot.events, result.events)
        self.assertEqual(snapshot.step_counts[StepStatus.CANCELLED], 2)
        self.assertEqual(
            sum(
                event.event_type
                in (
                    WorkflowEventType.WORKFLOW_COMPLETED,
                    WorkflowEventType.WORKFLOW_FAILED,
                    WorkflowEventType.WORKFLOW_PARTIAL,
                    WorkflowEventType.WORKFLOW_CANCELLED,
                )
                for event in result.events
            ),
            1,
        )

    def test_preflight_failure_takes_precedence_over_pre_requested_cancellation(self):
        workflow = self._workflow(
            (WorkflowStep("step", "local.stats", {"text": WorkflowInputRef("missing")}),)
        )
        token = WorkflowCancellationToken()
        token.request_cancel()
        with patch.object(self.executor, "invoke", wraps=self.executor.invoke) as invoke:
            result = self.engine.execute(
                workflow.identifier,
                cancellation_token=token,
            )

        self.assertEqual(invoke.call_count, 0)
        self.assertEqual(result.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertEqual(result.preflight_issues[0].error_code, "missing_workflow_input")
        self.assertFalse(result.cancellation_observed)
        self.assertFalse(result.execution_began)
        self.assertFalse(token.request_cancel())

    def test_executor_cancellation_is_observed_after_sync_call_returns(self):
        token = WorkflowCancellationToken()
        workflow = self._workflow(
            (
                WorkflowStep("running", "local.stats", {"text": "active"}),
                WorkflowStep("pending", "local.independent", {"text": "not-started"}),
            )
        )
        original_invoke = self.executor.invoke
        call_order: list[str] = []

        def synchronous_executor(request):
            call_order.append("entered")
            result = original_invoke(request)
            token.request_cancel()
            call_order.append("returned")
            return result

        with patch.object(self.executor, "invoke", side_effect=synchronous_executor):
            result = self.engine.execute(
                workflow.identifier,
                cancellation_token=token,
            )

        self.assertEqual(call_order, ["entered", "returned"])
        self.assertEqual(self.calls, [("stats", "active")])
        self.assertEqual(result.status, WorkflowStatus.CANCELLED)
        self.assertEqual(result.successful_step_count, 1)
        self.assertEqual(result.cancelled_step_count, 1)
        self.assertEqual(
            [step.status for step in result.step_results],
            [StepStatus.SUCCEEDED, StepStatus.CANCELLED],
        )
        self.assertEqual(result.events[-1].event_type, WorkflowEventType.WORKFLOW_CANCELLED)
        self.assertEqual(self.engine.inspect_run(result.run_id).events, result.events)

    def test_cooperative_cancellation_exception_cancels_current_and_pending_steps(self):
        self._workflow(
            (
                WorkflowStep("current", "local.stats", {"text": "active"}),
                WorkflowStep("pending", "local.independent", {"text": "not-started"}),
            )
        )
        token = WorkflowCancellationToken()
        secret = "private cooperative cancellation diagnostic"
        with patch.object(
            self.executor,
            "invoke",
            side_effect=WorkflowCancellationRequested(secret),
        ) as invoke:
            result = self.engine.execute(
                "workflow.example",
                cancellation_token=token,
            )

        self.assertEqual(invoke.call_count, 1)
        self.assertTrue(token.is_cancelled)
        self.assertEqual(result.status, WorkflowStatus.CANCELLED)
        self.assertEqual(result.cancelled_step_count, 2)
        self.assertEqual(result.failed_step_count, 0)
        self.assertNotIn(secret, repr(result))
        self.assertEqual(
            [
                (event.event_type, event.step_id)
                for event in result.events
                if event.step_id is not None
            ],
            [
                (WorkflowEventType.STEP_STARTED, "current"),
                (WorkflowEventType.STEP_CANCELLED, "current"),
                (WorkflowEventType.STEP_CANCELLED, "pending"),
            ],
        )

    def test_cancellation_before_invocation_checkpoint_does_not_start_tool(self):
        token = WorkflowCancellationToken()
        self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "safe"}),)
        )
        original_resolve = _resolve_step_inputs

        def cancel_during_input_resolution(*args, **kwargs):
            resolved = original_resolve(*args, **kwargs)
            token.request_cancel()
            return resolved

        with (
            patch(
                "scripts.tool_workflow._resolve_step_inputs",
                side_effect=cancel_during_input_resolution,
            ),
            patch.object(self.executor, "invoke", wraps=self.executor.invoke) as invoke,
        ):
            result = self.engine.execute(
                "workflow.example",
                cancellation_token=token,
            )

        self.assertEqual(invoke.call_count, 0)
        self.assertEqual(result.status, WorkflowStatus.CANCELLED)
        self.assertEqual(result.cancelled_step_count, 1)
        self.assertEqual(result.events[-2].event_type, WorkflowEventType.STEP_CANCELLED)

    def test_cancellation_during_continue_independent_blocks_dependent_and_independent_steps(self):
        workflow = self._workflow(
            (
                WorkflowStep("first", "local.stats", {"text": "one"}),
                WorkflowStep(
                    "dependent",
                    "local.describe-count",
                    {"count": StepOutputRef("first", "characters")},
                ),
                WorkflowStep("independent", "local.independent", {"text": "two"}),
                WorkflowStep("later", "local.stats", {"text": "three"}),
            ),
            policy=WorkflowFailurePolicy.CONTINUE_INDEPENDENT,
        )
        token = WorkflowCancellationToken()
        original_invoke = self.executor.invoke

        def cancel_after_first(request):
            result = original_invoke(request)
            token.request_cancel()
            return result

        with patch.object(self.executor, "invoke", side_effect=cancel_after_first) as invoke:
            result = self.engine.execute(
                workflow.identifier,
                cancellation_token=token,
            )

        self.assertEqual(invoke.call_count, 1)
        self.assertEqual(result.status, WorkflowStatus.CANCELLED)
        self.assertEqual(result.successful_step_count, 1)
        self.assertEqual(result.cancelled_step_count, 3)
        self.assertEqual(
            [step.status for step in result.step_results],
            [
                StepStatus.SUCCEEDED,
                StepStatus.CANCELLED,
                StepStatus.CANCELLED,
                StepStatus.CANCELLED,
            ],
        )
        self.assertEqual(self.calls, [("stats", "one")])

    def test_failure_dependency_then_cancellation_keeps_all_outcomes_consistent(self):
        workflow = self._workflow(
            (
                WorkflowStep("fails", "local.failure", {"text": "bad"}),
                WorkflowStep(
                    "dependent",
                    "local.describe-count",
                    {"count": StepOutputRef("fails", "characters")},
                ),
                WorkflowStep("independent", "local.independent", {"text": "runs"}),
                WorkflowStep("later", "local.stats", {"text": "not-started"}),
            ),
            policy=WorkflowFailurePolicy.CONTINUE_INDEPENDENT,
        )
        token = WorkflowCancellationToken()
        original_invoke = self.executor.invoke

        def cancel_after_independent(request):
            result = original_invoke(request)
            if request.tool_identifier == "local.independent":
                token.request_cancel()
            return result

        with patch.object(self.executor, "invoke", side_effect=cancel_after_independent):
            result = self.engine.execute(
                workflow.identifier,
                cancellation_token=token,
            )

        self.assertEqual(result.status, WorkflowStatus.PARTIAL)
        self.assertEqual(
            (
                result.successful_step_count,
                result.failed_step_count,
                result.skipped_step_count,
                result.cancelled_step_count,
            ),
            (1, 1, 1, 1),
        )
        self.assertEqual(
            [step.status for step in result.step_results],
            [
                StepStatus.TOOL_FAILED,
                StepStatus.SKIPPED_DEPENDENCY,
                StepStatus.SUCCEEDED,
                StepStatus.CANCELLED,
            ],
        )
        snapshot = self.engine.inspect_run(result.run_id)
        self.assertEqual(snapshot.status, WorkflowStatus.PARTIAL)
        self.assertEqual(snapshot.events, result.events)
        self.assertEqual(snapshot.step_counts[StepStatus.CANCELLED], 1)

    def test_stop_on_failure_remains_primary_when_executor_also_requests_cancellation(self):
        workflow = self._workflow(
            (
                WorkflowStep("fails", "local.failure", {"text": "bad"}),
                WorkflowStep("not-run", "local.independent", {"text": "later"}),
            ),
        )
        token = WorkflowCancellationToken()
        original_invoke = self.executor.invoke

        def fail_and_request_cancel(request):
            result = original_invoke(request)
            token.request_cancel()
            return result

        with patch.object(
            self.executor,
            "invoke",
            side_effect=fail_and_request_cancel,
        ):
            result = self.engine.execute(
                workflow.identifier,
                cancellation_token=token,
            )

        self.assertEqual(result.status, WorkflowStatus.FAILED)
        self.assertEqual(result.error_code, "runtime_failure")
        self.assertEqual(result.failed_step_count, 1)
        self.assertEqual(result.skipped_step_count, 1)
        self.assertEqual(result.cancelled_step_count, 0)
        self.assertTrue(result.cancellation_observed)
        self.assertEqual(
            result.step_results[1].status,
            StepStatus.SKIPPED_POLICY,
        )

    def test_cancellation_after_terminal_completion_cannot_rewrite_result(self):
        workflow = self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "done"}),)
        )
        token = WorkflowCancellationToken()
        result = self.engine.execute(
            workflow.identifier,
            cancellation_token=token,
        )
        event_history = result.events

        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)
        self.assertFalse(token.is_cancelled)
        self.assertFalse(token.request_cancel())
        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)
        self.assertEqual(result.events, event_history)
        self.assertEqual(result.events[-1].event_type, WorkflowEventType.WORKFLOW_COMPLETED)
        with self.assertRaisesRegex(
            InvalidWorkflowDefinitionError,
            "only one workflow execution",
        ):
            self.engine.execute(
                workflow.identifier,
                cancellation_token=token,
            )

    def test_process_level_interrupt_is_not_normalized_as_tool_failure(self):
        workflow = self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "safe"}),)
        )
        secret = "process-level detail"
        with patch.object(
            self.executor,
            "invoke",
            side_effect=KeyboardInterrupt(secret),
        ):
            with self.assertRaisesRegex(KeyboardInterrupt, secret):
                self.engine.execute(workflow.identifier)

    def test_terminal_event_recording_failure_is_not_reported_as_success(self):
        workflow = self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "completed"}),)
        )
        original_monotonic = workflow_module.monotonic
        calls = 0

        def fail_while_recording_terminal():
            nonlocal calls
            calls += 1
            if calls == 6:
                raise RuntimeError("event clock failure")
            return original_monotonic()

        with (
            patch(
                "scripts.tool_workflow.monotonic",
                side_effect=fail_while_recording_terminal,
            ),
            self.assertRaisesRegex(RuntimeError, "event clock failure"),
        ):
            self.engine.execute(workflow.identifier)

        self.assertEqual(self.calls, [("stats", "completed")])

    def test_concurrent_cancellation_requests_are_idempotent(self):
        token = WorkflowCancellationToken()
        barrier = Barrier(8)

        def request_after_barrier() -> bool:
            barrier.wait()
            return token.request_cancel()

        with ThreadPoolExecutor(max_workers=8) as workers:
            requests = list(workers.map(lambda _: request_after_barrier(), range(8)))

        self.assertEqual(sum(requests), 1)
        self.assertTrue(token.is_cancelled)

    def test_cancellation_finalization_preserves_snapshot_retention_diagnostic(self):
        workflow = self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "safe"}),)
        )
        token = WorkflowCancellationToken()
        token.request_cancel()
        secret = "private snapshot backend detail"
        with patch.object(
            self.engine,
            "_retain_snapshot",
            side_effect=RuntimeError(secret),
        ):
            result = self.engine.execute(
                workflow.identifier,
                cancellation_token=token,
            )

        self.assertEqual(result.status, WorkflowStatus.CANCELLED)
        self.assertEqual(result.error_code, "workflow_cancelled")
        self.assertEqual(result.cancelled_step_count, 1)
        self.assertEqual(len(result.observability_issues), 1)
        self.assertEqual(
            result.observability_issues[0].error_code,
            "snapshot_retention_failed",
        )
        self.assertFalse(result.observability_issues[0].snapshot_available)
        self.assertNotIn(secret, repr(result))

    def test_snapshot_retention_failure_does_not_mask_tool_failure(self):
        workflow = self._workflow(
            (WorkflowStep("fails", "local.failure", {"text": "private"}),)
        )
        with patch.object(
            self.engine,
            "_retain_snapshot",
            side_effect=RuntimeError("secondary cleanup secret"),
        ):
            result = self.engine.execute(workflow.identifier)

        self.assertEqual(result.status, WorkflowStatus.FAILED)
        self.assertEqual(result.failure_category, FailureCategory.TOOL_INVOCATION)
        self.assertEqual(result.error_code, "runtime_failure")
        self.assertEqual(result.failed_step_count, 1)
        self.assertEqual(
            result.observability_issues[0].error_code,
            "snapshot_retention_failed",
        )
        self.assertNotIn("secondary cleanup secret", repr(result))

    def test_workflow_result_existing_positional_constructor_remains_compatible(self):
        result = WorkflowResult(
            "workflow.compat",
            WorkflowStatus.SUCCEEDED,
            (
                WorkflowStepResult(
                    "step",
                    "local.stats",
                    StepStatus.SUCCEEDED,
                    tool_result=ToolExecutionResult(
                        request_id="compat-request",
                        tool_identifier="local.stats",
                        status=ToolStatus.SUCCEEDED,
                        output={},
                    ),
                ),
            ),
            (),
            1,
            0,
            0,
            True,
            True,
            "success",
        )
        self.assertTrue(result.success)
        self.assertEqual(result.cancelled_step_count, 0)

    def test_failed_and_skipped_steps_have_terminal_events_before_workflow_failure(self):
        self._workflow(
            (
                WorkflowStep("fail", "local.failure", {"text": "secret-input"}),
                WorkflowStep("later", "local.independent", {"text": "not run"}),
            )
        )

        result = self.engine.execute("workflow.example")
        self.assertEqual(
            tuple(event.event_type for event in result.events),
            (
                WorkflowEventType.RUN_STARTED,
                WorkflowEventType.PREFLIGHT_COMPLETED,
                WorkflowEventType.STEP_STARTED,
                WorkflowEventType.STEP_FAILED,
                WorkflowEventType.STEP_SKIPPED,
                WorkflowEventType.WORKFLOW_FAILED,
            ),
        )
        self.assertEqual(
            result.events[-1].sequence_number,
            max(event.sequence_number for event in result.events),
        )
        self.assertEqual(result.events[3].error_code, "runtime_failure")
        self.assertNotIn("private implementation detail", repr(result.events))
        self.assertNotIn("secret-input", repr(result.events))
        snapshot = self.engine.inspect_run(result.run_id)
        self.assertEqual(snapshot.step_counts[StepStatus.TOOL_FAILED], 1)
        self.assertEqual(snapshot.step_counts[StepStatus.SKIPPED_POLICY], 1)
        self.assertIn("runtime_failure", snapshot.failure_codes)
        self.assertIn("stopped_after_failure", snapshot.failure_codes)

    def test_continue_independent_event_order_reflects_skips_and_actual_execution(self):
        self._workflow(
            (
                WorkflowStep("fail", "local.failure", {"text": "bad"}),
                WorkflowStep(
                    "dependent",
                    "local.describe-count",
                    {"count": StepOutputRef("fail", "characters")},
                ),
                WorkflowStep("independent", "local.independent", {"text": "runs"}),
            ),
            policy=WorkflowFailurePolicy.CONTINUE_INDEPENDENT,
        )

        result = self.engine.execute("workflow.example")
        step_events = tuple(
            (event.event_type, event.step_id)
            for event in result.events
            if event.step_id is not None
        )
        self.assertEqual(
            step_events,
            (
                (WorkflowEventType.STEP_STARTED, "fail"),
                (WorkflowEventType.STEP_FAILED, "fail"),
                (WorkflowEventType.STEP_SKIPPED, "dependent"),
                (WorkflowEventType.STEP_STARTED, "independent"),
                (WorkflowEventType.STEP_SUCCEEDED, "independent"),
            ),
        )
        self.assertEqual(result.status, WorkflowStatus.PARTIAL)
        self.assertEqual(result.events[-1].event_type, WorkflowEventType.WORKFLOW_PARTIAL)
        self.assertEqual(self.calls[-1], ("independent", "runs"))

    def test_preflight_failure_is_inspectable_and_invokes_no_tools(self):
        self._workflow(
            (WorkflowStep("stats", "local.stats", {"text": WorkflowInputRef("missing")}),)
        )

        result = self.engine.execute("workflow.example")

        self.assertEqual(result.status, WorkflowStatus.PREFLIGHT_FAILED)
        self.assertFalse(result.execution_began)
        self.assertEqual(self.calls, [])
        self.assertEqual(
            tuple(event.event_type for event in result.events),
            (
                WorkflowEventType.RUN_STARTED,
                WorkflowEventType.PREFLIGHT_COMPLETED,
                WorkflowEventType.WORKFLOW_FAILED,
            ),
        )
        snapshot = self.engine.inspect_run(result.run_id)
        self.assertEqual(snapshot.steps, ())
        self.assertEqual(snapshot.failure_codes, ("missing_workflow_input",))

    def test_empty_workflows_remain_rejected_without_creating_runs(self):
        with self.assertRaisesRegex(
            InvalidWorkflowDefinitionError, "at least one step"
        ):
            WorkflowDefinition("workflow.empty", "Empty", ())
        self.assertEqual(self.calls, [])

    def test_output_values_are_excluded_from_default_events_and_snapshots(self):
        secret_output = "distinctive-output-secret-7c91"
        tools = ToolRegistry()
        tools.register(_contract("local.secret-output", (("text", InputType.STRING),)))
        executor = ToolExecutor(tools)
        executor.register_adapter(
            LocalToolAdapter(
                "local.workflow",
                {
                    "local.secret-output": lambda inputs: {
                        "value": secret_output,
                        "input_length": len(str(inputs["text"])),
                    }
                },
            )
        )
        workflows = WorkflowRegistry()
        workflows.register(
            WorkflowDefinition(
                "workflow.private-output",
                "Private output",
                (
                    WorkflowStep(
                        "produce",
                        "local.secret-output",
                        {"text": WorkflowInputRef("message")},
                    ),
                ),
            )
        )
        engine = WorkflowEngine(workflows, tools, executor)
        secret_input = "distinctive-input-secret-b82a"

        result = engine.execute(
            "workflow.private-output",
            {"message": secret_input},
        )
        inspected = engine.inspect_run(result.run_id)

        self.assertNotIn(secret_input, repr(result.events))
        self.assertNotIn(secret_output, repr(result.events))
        self.assertNotIn(secret_input, repr(inspected))
        self.assertNotIn(secret_output, repr(inspected))
        self.assertNotIn(secret_output, repr(result))

    def test_unknown_and_evicted_run_ids_are_distinguished(self):
        workflows = WorkflowRegistry()
        workflows.register(
            WorkflowDefinition(
                "workflow.retained",
                "Retained",
                (WorkflowStep("step", "local.stats", {"text": "x"}),),
            )
        )
        engine = WorkflowEngine(
            workflows,
            self.tools,
            self.executor,
            max_retained_runs=1,
        )
        first = engine.execute("workflow.retained")
        second = engine.execute("workflow.retained")

        with self.assertRaises(EvictedWorkflowRunError):
            engine.inspect_run(first.run_id)
        with self.assertRaises(UnknownWorkflowRunError):
            engine.inspect_run("never-seen")
        self.assertEqual(engine.inspect_run(second.run_id).run_id, second.run_id)

    def test_separate_runs_have_independent_event_sequences_and_ids(self):
        self._workflow(
            (WorkflowStep("step", "local.stats", {"text": WorkflowInputRef("message")}),)
        )

        first = self.engine.execute("workflow.example", {"message": "first"})
        second = self.engine.execute("workflow.example", {"message": "second"})

        self.assertNotEqual(first.run_id, second.run_id)
        for result in (first, second):
            self.assertEqual(
                [event.sequence_number for event in result.events],
                list(range(1, len(result.events) + 1)),
            )
            self.assertEqual({event.run_id for event in result.events}, {result.run_id})
            self.assertEqual(
                self.engine.inspect_run(result.run_id).events,
                result.events,
            )

    def test_event_recording_does_not_repeat_tool_invocations(self):
        self._workflow(
            (WorkflowStep("step", "local.stats", {"text": "only once"}),)
        )
        with patch.object(
            self.executor, "invoke", wraps=self.executor.invoke
        ) as invoke:
            result = self.engine.execute("workflow.example")

        self.assertEqual(invoke.call_count, 1)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(
            sum(
                event.event_type is WorkflowEventType.STEP_STARTED
                for event in result.events
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()

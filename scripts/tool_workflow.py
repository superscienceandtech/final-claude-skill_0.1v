"""Validated sequential workflows composed from explicitly registered tools.

Workflow configuration is inert data. Validation never invokes tools; execution
delegates exclusively to the supplied P076 ``ToolExecutor``. Raw step outputs
are kept only while a run is active for dependency resolution and are omitted
from returned traces unless the caller opts in.
"""

from __future__ import annotations

import math
import re
from collections import deque
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from threading import Event, Lock, RLock
from time import monotonic
from types import MappingProxyType
from typing import Callable, Iterator, Mapping
from uuid import uuid4

from scripts.tool_framework import (
    ExecutionAvailability,
    InputType,
    InvalidToolInputError,
    ToolContract,
    ToolExecutionResult,
    ToolExecutor,
    ToolInvocationRequest,
    ToolRegistry,
    ToolStatus,
    UnknownToolError,
)


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")
_FIELD_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")


class WorkflowError(Exception):
    """Base class for workflow definition and execution errors."""


class InvalidWorkflowDefinitionError(WorkflowError, ValueError):
    """Raised when workflow configuration is malformed or contradictory."""


class DuplicateWorkflowError(WorkflowError):
    """Raised when a workflow identifier is already registered."""


class UnknownWorkflowError(WorkflowError, LookupError):
    """Raised when the requested workflow is not registered."""


class InvalidStepInputMappingError(InvalidWorkflowDefinitionError):
    """Raised when a step's explicit input mapping is malformed."""


class MissingWorkflowInputError(WorkflowError):
    """Raised internally when a referenced caller input is missing."""


class MissingStepOutputError(WorkflowError):
    """Raised internally when a referenced successful output field is missing."""


class WorkflowCancellationRequested(WorkflowError):
    """Cooperative signal for an executor to end its current tool operation."""


class WorkflowCancellationToken:
    """Thread-safe, idempotent cancellation signal for one workflow execution.

    Cancellation is observed at workflow checkpoints; it cannot interrupt a
    synchronous executor invocation that is already running.
    """

    def __init__(self) -> None:
        self._event = Event()
        self._lock = Lock()
        self._closed = False
        self._claimed = False

    @property
    def is_cancelled(self) -> bool:
        """Whether cancellation has been requested."""
        return self._event.is_set()

    def request_cancel(self) -> bool:
        """Request cancellation; return true only for the first request."""
        with self._lock:
            if self._closed or self._event.is_set():
                return False
            self._event.set()
            return True

    def _close(self) -> bool:
        """Atomically close cancellation at terminalization and return its state."""
        with self._lock:
            self._closed = True
            return self._event.is_set()

    def _claim(self) -> bool:
        """Claim this token for one workflow run."""
        with self._lock:
            if self._claimed or self._closed:
                return False
            self._claimed = True
            return True


class WorkflowFailurePolicy(str, Enum):
    STOP_ON_FAILURE = "stop_on_failure"
    CONTINUE_INDEPENDENT = "continue_independent"


class WorkflowStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PARTIAL = "partial"
    PREFLIGHT_FAILED = "preflight_failed"
    CANCELLED = "cancelled"


class WorkflowProgressStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PARTIAL = "partial"
    PREFLIGHT_FAILED = "preflight_failed"
    CANCELLED = "cancelled"


class WorkflowEventType(str, Enum):
    RUN_STARTED = "workflow_run_started"
    PREFLIGHT_COMPLETED = "preflight_completed"
    STEP_STARTED = "step_started"
    STEP_SUCCEEDED = "step_succeeded"
    STEP_FAILED = "step_failed"
    STEP_SKIPPED = "step_skipped"
    STEP_CANCELLED = "step_cancelled"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_PARTIAL = "workflow_completed_with_partial_failures"
    WORKFLOW_CANCELLED = "workflow_cancelled"


class StepStatus(str, Enum):
    SUCCEEDED = "succeeded"
    TOOL_FAILED = "tool_failed"
    INPUT_RESOLUTION_FAILED = "input_resolution_failed"
    INVOCATION_ERROR = "invocation_error"
    SKIPPED_DEPENDENCY = "skipped_dependency"
    SKIPPED_POLICY = "skipped_policy"
    CANCELLED = "cancelled"


class WorkflowStepLifecycleStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class FailureCategory(str, Enum):
    PREFLIGHT = "preflight"
    WORKFLOW_VALIDATION = "workflow_validation"
    WORKFLOW_RUNTIME = "workflow_runtime"
    CANCELLATION = "cancellation"
    INPUT_RESOLUTION = "input_resolution"
    TOOL_INVOCATION = "tool_invocation"
    DEPENDENCY = "dependency"
    FAILURE_POLICY = "failure_policy"


class WorkflowValidationCategory(str, Enum):
    STRUCTURE = "structure"
    STEP = "step"
    DEPENDENCY = "dependency"
    CYCLE = "cycle"
    ORDER = "order"


@dataclass(frozen=True, slots=True)
class WorkflowValidationIssue:
    """One stable, payload-free workflow definition validation diagnostic."""

    error_code: str
    category: WorkflowValidationCategory
    message: str
    workflow_identifier: str | None = None
    step_id: str | None = None
    dependency_id: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowValidationResult:
    """Deterministic validation report and declared dependency graph."""

    workflow_identifier: str | None
    valid: bool
    issues: tuple[WorkflowValidationIssue, ...]
    dependency_graph: Mapping[str, tuple[str, ...]]
    declared_step_order: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "issues", tuple(self.issues))
        object.__setattr__(
            self,
            "dependency_graph",
            MappingProxyType(
                {
                    step_id: tuple(dependencies)
                    for step_id, dependencies in self.dependency_graph.items()
                }
            ),
        )
        object.__setattr__(self, "declared_step_order", tuple(self.declared_step_order))


class InputSourceKind(str, Enum):
    LITERAL = "literal"
    WORKFLOW_INPUT = "workflow_input"
    STEP_OUTPUT = "step_output"


@dataclass(frozen=True, slots=True)
class WorkflowInputRef:
    """Reference one named value from the caller's workflow input mapping."""

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _FIELD_PATTERN.fullmatch(self.name):
            raise InvalidStepInputMappingError(
                "workflow input reference name must be a valid lowercase identifier."
            )


@dataclass(frozen=True, slots=True)
class StepOutputRef:
    """Reference one top-level field from an earlier successful step output."""

    step_id: str
    field: str

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.step_id
        ):
            raise InvalidStepInputMappingError(
                "step output reference must use a valid step identifier."
            )
        if not isinstance(self.field, str) or not _FIELD_PATTERN.fullmatch(self.field):
            raise InvalidStepInputMappingError(
                "step output reference must use a valid top-level field identifier."
            )


InputMappingValue = object


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """One ordered tool invocation with explicit, non-executable input mapping."""

    step_id: str
    tool_identifier: str
    input_mapping: Mapping[str, InputMappingValue]
    depends_on: tuple[str, ...] = ()
    display_name: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.step_id
        ):
            raise InvalidWorkflowDefinitionError(
                "step_id must be a lowercase identifier."
            )
        if not isinstance(self.tool_identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.tool_identifier
        ):
            raise InvalidWorkflowDefinitionError(
                f"step '{self.step_id}' must reference a valid Tool identifier."
            )
        if not isinstance(self.input_mapping, Mapping):
            raise InvalidStepInputMappingError(
                f"step '{self.step_id}' input_mapping must be a mapping."
            )
        copied: dict[str, object] = {}
        for name, value in self.input_mapping.items():
            if not isinstance(name, str) or not _FIELD_PATTERN.fullmatch(name):
                raise InvalidStepInputMappingError(
                    f"step '{self.step_id}' has an invalid input field name."
                )
            if not isinstance(value, (WorkflowInputRef, StepOutputRef)) and (
                _contains_reference(value)
            ):
                raise InvalidStepInputMappingError(
                    "workflow and step-output references must occupy a complete "
                    "top-level input mapping value."
                )
            copied[name] = _freeze_mapping_value(value)
        object.__setattr__(self, "input_mapping", MappingProxyType(copied))
        if not isinstance(self.depends_on, tuple) or any(
            not isinstance(dependency, str)
            or not _IDENTIFIER_PATTERN.fullmatch(dependency)
            for dependency in self.depends_on
        ):
            raise InvalidWorkflowDefinitionError(
                f"step '{self.step_id}' depends_on must be a tuple of valid step identifiers."
            )
        if len(self.depends_on) != len(set(self.depends_on)):
            raise InvalidWorkflowDefinitionError(
                f"step '{self.step_id}' contains duplicate dependencies."
            )
        if self.step_id in self.depends_on:
            raise InvalidWorkflowDefinitionError(
                f"step '{self.step_id}' cannot depend on itself."
            )
        if self.display_name is not None and (
            not isinstance(self.display_name, str) or not self.display_name.strip()
        ):
            raise InvalidWorkflowDefinitionError(
                "display_name must be a non-empty string when supplied."
            )
        if self.description is not None and not isinstance(self.description, str):
            raise InvalidWorkflowDefinitionError("step description must be a string.")


@dataclass(frozen=True, slots=True)
class WorkflowDefinition:
    """Immutable ordered workflow configuration; no tools run during creation."""

    identifier: str
    name: str
    steps: tuple[WorkflowStep, ...]
    description: str = ""
    failure_policy: WorkflowFailurePolicy = WorkflowFailurePolicy.STOP_ON_FAILURE

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.identifier
        ):
            raise InvalidWorkflowDefinitionError(
                "workflow identifier must be a lowercase identifier."
            )
        if not isinstance(self.name, str) or not self.name.strip():
            raise InvalidWorkflowDefinitionError("workflow name must be non-empty.")
        if not isinstance(self.description, str):
            raise InvalidWorkflowDefinitionError("workflow description must be a string.")
        if not isinstance(self.steps, tuple) or any(
            not isinstance(step, WorkflowStep) for step in self.steps
        ):
            raise InvalidWorkflowDefinitionError(
                "steps must be a tuple of WorkflowStep values."
            )
        if not self.steps:
            raise InvalidWorkflowDefinitionError(
                "workflow must contain at least one step."
            )
        step_ids = [step.step_id for step in self.steps]
        if len(step_ids) != len(set(step_ids)):
            raise InvalidWorkflowDefinitionError(
                "workflow contains duplicate step identifiers."
            )
        if not isinstance(self.failure_policy, WorkflowFailurePolicy):
            raise InvalidWorkflowDefinitionError(
                "failure_policy must be a WorkflowFailurePolicy value."
            )
        validation = validate_workflow(self)
        if not validation.valid:
            raise InvalidWorkflowDefinitionError(validation.issues[0].message)


def validate_workflow(
    workflow: object,
    *,
    expected_identifier: str | None = None,
) -> WorkflowValidationResult:
    """Validate a workflow and its graph without resolving or invoking tools.

    Dependencies include explicit ``depends_on`` entries and top-level
    ``StepOutputRef`` values. Valid workflows retain their declared sequential
    order; this function never reorders steps.
    """
    if not isinstance(workflow, WorkflowDefinition):
        issue = WorkflowValidationIssue(
            "invalid_workflow_type",
            WorkflowValidationCategory.STRUCTURE,
            "workflow must be a WorkflowDefinition.",
        )
        return WorkflowValidationResult(None, False, (issue,), {}, ())

    raw_identifier = getattr(workflow, "identifier", None)
    workflow_identifier = (
        raw_identifier
        if isinstance(raw_identifier, str)
        and _IDENTIFIER_PATTERN.fullmatch(raw_identifier)
        else None
    )
    issues: list[WorkflowValidationIssue] = []

    def add_issue(
        error_code: str,
        category: WorkflowValidationCategory,
        message: str,
        *,
        step_id: str | None = None,
        dependency_id: str | None = None,
    ) -> None:
        issues.append(
            WorkflowValidationIssue(
                error_code,
                category,
                message,
                workflow_identifier,
                step_id,
                dependency_id,
            )
        )

    if workflow_identifier is None:
        add_issue(
            "invalid_workflow_identifier",
            WorkflowValidationCategory.STRUCTURE,
            "workflow identifier must be a lowercase identifier.",
        )
    elif expected_identifier is not None and workflow_identifier != expected_identifier:
        add_issue(
            "workflow_identifier_mismatch",
            WorkflowValidationCategory.STRUCTURE,
            "workflow identifier does not match the registered identifier.",
        )
    name = getattr(workflow, "name", None)
    if not isinstance(name, str) or not name.strip():
        add_issue(
            "invalid_workflow_name",
            WorkflowValidationCategory.STRUCTURE,
            "workflow name must be non-empty.",
        )
    if not isinstance(getattr(workflow, "description", None), str):
        add_issue(
            "invalid_workflow_description",
            WorkflowValidationCategory.STRUCTURE,
            "workflow description must be a string.",
        )
    if not isinstance(
        getattr(workflow, "failure_policy", None), WorkflowFailurePolicy
    ):
        add_issue(
            "invalid_failure_policy",
            WorkflowValidationCategory.STRUCTURE,
            "failure_policy must be a WorkflowFailurePolicy value.",
        )

    steps = getattr(workflow, "steps", None)
    if not isinstance(steps, tuple):
        add_issue(
            "invalid_steps",
            WorkflowValidationCategory.STRUCTURE,
            "steps must be a tuple of WorkflowStep values.",
        )
        steps = ()
    elif not steps:
        add_issue(
            "empty_workflow",
            WorkflowValidationCategory.STRUCTURE,
            "workflow must contain at least one step.",
        )

    step_order: list[str] = []
    step_positions: dict[str, int] = {}
    step_dependencies: dict[str, set[str]] = {}
    seen_step_ids: set[str] = set()

    for index, step in enumerate(steps):
        if not isinstance(step, WorkflowStep):
            add_issue(
                "invalid_step",
                WorkflowValidationCategory.STEP,
                "each workflow step must be a WorkflowStep.",
            )
            continue
        step_id = getattr(step, "step_id", None)
        if not isinstance(step_id, str) or not _IDENTIFIER_PATTERN.fullmatch(step_id):
            add_issue(
                "invalid_step_identifier",
                WorkflowValidationCategory.STEP,
                "step identifier must be a lowercase identifier.",
            )
            continue
        if step_id in seen_step_ids:
            add_issue(
                "duplicate_step_identifier",
                WorkflowValidationCategory.STEP,
                f"workflow contains duplicate step identifier '{step_id}'.",
                step_id=step_id,
            )
            continue
        seen_step_ids.add(step_id)
        step_order.append(step_id)
        step_positions[step_id] = index

        tool_identifier = getattr(step, "tool_identifier", None)
        if not isinstance(tool_identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
            tool_identifier
        ):
            add_issue(
                "invalid_tool_identifier",
                WorkflowValidationCategory.STEP,
                f"step '{step_id}' must reference a valid Tool identifier.",
                step_id=step_id,
            )

        raw_dependencies = getattr(step, "depends_on", None)
        dependencies: set[str] = set()
        if not isinstance(raw_dependencies, tuple):
            add_issue(
                "invalid_dependencies",
                WorkflowValidationCategory.DEPENDENCY,
                f"step '{step_id}' depends_on must be a tuple of step identifiers.",
                step_id=step_id,
            )
        else:
            valid_explicit: list[str] = []
            for dependency in raw_dependencies:
                if not isinstance(dependency, str) or not _IDENTIFIER_PATTERN.fullmatch(
                    dependency
                ):
                    add_issue(
                        "invalid_dependency_identifier",
                        WorkflowValidationCategory.DEPENDENCY,
                        f"step '{step_id}' contains an invalid dependency identifier.",
                        step_id=step_id,
                    )
                    continue
                valid_explicit.append(dependency)
                dependencies.add(dependency)
            if len(valid_explicit) != len(set(valid_explicit)):
                add_issue(
                    "duplicate_dependency",
                    WorkflowValidationCategory.DEPENDENCY,
                    f"step '{step_id}' contains duplicate dependencies.",
                    step_id=step_id,
                )

        input_mapping = getattr(step, "input_mapping", None)
        if not isinstance(input_mapping, Mapping):
            add_issue(
                "invalid_input_mapping",
                WorkflowValidationCategory.STEP,
                f"step '{step_id}' input_mapping must be a mapping.",
                step_id=step_id,
            )
        else:
            for input_name, value in input_mapping.items():
                if not isinstance(input_name, str) or not _FIELD_PATTERN.fullmatch(
                    input_name
                ):
                    add_issue(
                        "invalid_input_name",
                        WorkflowValidationCategory.STEP,
                        f"step '{step_id}' contains an invalid Tool input name.",
                        step_id=step_id,
                    )
                if isinstance(value, StepOutputRef):
                    reference_step_id = getattr(value, "step_id", None)
                    reference_field = getattr(value, "field", None)
                    if (
                        not isinstance(reference_step_id, str)
                        or not _IDENTIFIER_PATTERN.fullmatch(reference_step_id)
                        or not isinstance(reference_field, str)
                        or not _FIELD_PATTERN.fullmatch(reference_field)
                    ):
                        add_issue(
                            "invalid_step_output_reference",
                            WorkflowValidationCategory.DEPENDENCY,
                            f"step '{step_id}' contains an invalid step-output reference.",
                            step_id=step_id,
                        )
                    else:
                        dependencies.add(reference_step_id)
                elif isinstance(value, WorkflowInputRef):
                    reference_name = getattr(value, "name", None)
                    if not isinstance(reference_name, str) or not _FIELD_PATTERN.fullmatch(
                        reference_name
                    ):
                        add_issue(
                            "invalid_workflow_input_reference",
                            WorkflowValidationCategory.STEP,
                            f"step '{step_id}' contains an invalid workflow-input reference.",
                            step_id=step_id,
                        )
                elif _contains_nested_reference(value):
                    add_issue(
                        "nested_reference",
                        WorkflowValidationCategory.STEP,
                        "workflow and step-output references must occupy a complete "
                        "top-level input mapping value.",
                        step_id=step_id,
                    )
                elif not _is_supported_literal(value):
                    add_issue(
                        "invalid_literal_input",
                        WorkflowValidationCategory.STEP,
                        f"step '{step_id}' contains an unsupported literal input value.",
                        step_id=step_id,
                    )
        display_name = getattr(step, "display_name", None)
        if display_name is not None and (
            not isinstance(display_name, str) or not display_name.strip()
        ):
            add_issue(
                "invalid_display_name",
                WorkflowValidationCategory.STEP,
                f"step '{step_id}' display_name must be non-empty when supplied.",
                step_id=step_id,
            )
        if not isinstance(getattr(step, "description", None), (str, type(None))):
            add_issue(
                "invalid_step_description",
                WorkflowValidationCategory.STEP,
                f"step '{step_id}' description must be a string when supplied.",
                step_id=step_id,
            )
        if step_id in dependencies:
            add_issue(
                "self_dependency",
                WorkflowValidationCategory.DEPENDENCY,
                f"step '{step_id}' cannot depend on itself.",
                step_id=step_id,
                dependency_id=step_id,
            )
            dependencies.discard(step_id)
        step_dependencies[step_id] = dependencies

    known_ids = set(step_order)
    graph: dict[str, tuple[str, ...]] = {}
    for step_id in step_order:
        known_dependencies: list[str] = []
        for dependency in sorted(step_dependencies.get(step_id, set())):
            if dependency not in known_ids:
                add_issue(
                    "unknown_dependency",
                    WorkflowValidationCategory.DEPENDENCY,
                    f"step '{step_id}' references unknown dependency '{dependency}'.",
                    step_id=step_id,
                    dependency_id=dependency,
                )
                continue
            known_dependencies.append(dependency)
            if step_positions[dependency] >= step_positions[step_id]:
                add_issue(
                    "forward_dependency",
                    WorkflowValidationCategory.ORDER,
                    f"dependency '{dependency}' must appear before step '{step_id}' "
                    "in the declared sequential order.",
                    step_id=step_id,
                    dependency_id=dependency,
                )
        graph[step_id] = tuple(known_dependencies)

    for component in _dependency_cycle_components(graph):
        for step_id in component:
            add_issue(
                "dependency_cycle",
                WorkflowValidationCategory.CYCLE,
                f"workflow contains a circular dependency involving '{step_id}'.",
                step_id=step_id,
            )

    category_order = {
        WorkflowValidationCategory.STRUCTURE: 0,
        WorkflowValidationCategory.STEP: 1,
        WorkflowValidationCategory.DEPENDENCY: 2,
        WorkflowValidationCategory.CYCLE: 3,
        WorkflowValidationCategory.ORDER: 4,
    }
    issues.sort(
        key=lambda issue: (
            category_order[issue.category],
            step_positions.get(issue.step_id or "", -1),
            issue.dependency_id or "",
            issue.error_code,
        )
    )
    return WorkflowValidationResult(
        workflow_identifier=workflow_identifier,
        valid=not issues,
        issues=tuple(issues),
        dependency_graph=graph,
        declared_step_order=tuple(step_order),
    )


def _contains_nested_reference(value: object) -> bool:
    pending = [value]
    visited_containers: set[int] = set()
    while pending:
        current = pending.pop()
        if isinstance(current, (WorkflowInputRef, StepOutputRef)):
            return True
        if isinstance(current, Mapping):
            identity = id(current)
            if identity in visited_containers:
                continue
            visited_containers.add(identity)
            pending.extend(current.values())
        elif isinstance(current, (list, tuple)):
            identity = id(current)
            if identity in visited_containers:
                continue
            visited_containers.add(identity)
            pending.extend(current)
    return False


def _is_supported_literal(value: object) -> bool:
    pending: list[tuple[object, bool]] = [(value, False)]
    active_containers: set[int] = set()
    while pending:
        current, exiting = pending.pop()
        if current is None or isinstance(current, (str, bool, int)):
            continue
        if isinstance(current, float):
            if not math.isfinite(current):
                return False
            continue
        if isinstance(current, Mapping):
            identity = id(current)
            if exiting:
                active_containers.remove(identity)
                continue
            if identity in active_containers or any(
                not isinstance(key, str) for key in current
            ):
                return False
            active_containers.add(identity)
            pending.append((current, True))
            pending.extend((item, False) for item in current.values())
            continue
        if isinstance(current, (list, tuple)):
            identity = id(current)
            if exiting:
                active_containers.remove(identity)
                continue
            if identity in active_containers:
                return False
            active_containers.add(identity)
            pending.append((current, True))
            pending.extend((item, False) for item in current)
            continue
        return False
    return True


def _dependency_cycle_components(
    graph: Mapping[str, tuple[str, ...]],
) -> tuple[tuple[str, ...], ...]:
    """Return cyclic strongly connected components using iterative Kosaraju."""
    reverse: dict[str, list[str]] = {node: [] for node in graph}
    for node, dependencies in graph.items():
        for dependency in dependencies:
            if dependency in reverse:
                reverse[dependency].append(node)
    for dependents in reverse.values():
        dependents.sort()

    visited: set[str] = set()
    finish_order: list[str] = []
    for root in sorted(graph):
        if root in visited:
            continue
        visited.add(root)
        stack: list[tuple[str, Iterator[str]]] = [
            (root, iter(sorted(graph[root])))
        ]
        while stack:
            node, neighbors = stack[-1]
            try:
                neighbor = next(neighbors)
            except StopIteration:
                finish_order.append(node)
                stack.pop()
                continue
            if neighbor not in graph or neighbor in visited:
                continue
            visited.add(neighbor)
            stack.append((neighbor, iter(sorted(graph[neighbor]))))

    assigned: set[str] = set()
    cyclic_components: list[tuple[str, ...]] = []
    for root in reversed(finish_order):
        if root in assigned:
            continue
        component: list[str] = []
        pending = [root]
        assigned.add(root)
        while pending:
            node = pending.pop()
            component.append(node)
            for neighbor in reversed(reverse[node]):
                if neighbor not in assigned:
                    assigned.add(neighbor)
                    pending.append(neighbor)
        if len(component) > 1:
            cyclic_components.append(tuple(sorted(component)))
    return tuple(sorted(cyclic_components))


class WorkflowRegistry:
    """Small deterministic in-memory registry of workflow definitions."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}

    def register(self, workflow: WorkflowDefinition) -> None:
        if not isinstance(workflow, WorkflowDefinition):
            raise InvalidWorkflowDefinitionError(
                "workflow must be a WorkflowDefinition."
            )
        validation = validate_workflow(workflow)
        if not validation.valid:
            raise InvalidWorkflowDefinitionError(validation.issues[0].message)
        if workflow.identifier in self._workflows:
            raise DuplicateWorkflowError(
                f"workflow is already registered: {workflow.identifier}"
            )
        self._workflows[workflow.identifier] = workflow

    def get(self, identifier: str) -> WorkflowDefinition:
        if not isinstance(identifier, str):
            raise UnknownWorkflowError("workflow identifier must be a string.")
        try:
            return self._workflows[identifier]
        except KeyError as error:
            raise UnknownWorkflowError(
                f"unknown workflow identifier: {identifier}"
            ) from error

    def list_workflows(self) -> tuple[WorkflowDefinition, ...]:
        return tuple(self._workflows[key] for key in sorted(self._workflows))


@dataclass(frozen=True, slots=True)
class PreflightIssue:
    """One validation problem found before any step is invoked."""

    step_id: str | None
    category: FailureCategory
    error_code: str
    explanation: str


@dataclass(frozen=True, slots=True)
class WorkflowPreflightResult:
    """Full pre-execution validation report; it never runs tools."""

    workflow_identifier: str
    valid: bool
    issues: tuple[PreflightIssue, ...]
    validation_issues: tuple[WorkflowValidationIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class InputValueMetadata:
    """Privacy-safe metadata describing a resolved input without its value."""

    name: str
    source: InputSourceKind
    value_type: str


@dataclass(frozen=True, slots=True)
class OutputValueMetadata:
    """Privacy-safe summary of a successful tool output field."""

    name: str
    value_type: str


@dataclass(frozen=True, slots=True)
class WorkflowStepResult:
    """One ordered step outcome; inputs are never copied into the trace."""

    step_id: str
    tool_identifier: str
    status: StepStatus
    tool_result: ToolExecutionResult | None = None
    input_metadata: tuple[InputValueMetadata, ...] = ()
    output_metadata: tuple[OutputValueMetadata, ...] = ()
    failure_category: FailureCategory | None = None
    error_code: str | None = None
    explanation: str = ""

    def __post_init__(self) -> None:
        if self.status is StepStatus.SUCCEEDED:
            if (
                self.failure_category is not None
                or self.error_code is not None
                or self.tool_result is None
                or self.tool_result.status is not ToolStatus.SUCCEEDED
            ):
                raise ValueError("successful step result has contradictory failure data.")
        elif (
            self.failure_category is None
            or not self.error_code
            or (
                self.status is StepStatus.TOOL_FAILED
                and (
                    self.tool_result is None
                    or self.tool_result.status is ToolStatus.SUCCEEDED
                )
            )
            or (
                self.status is not StepStatus.TOOL_FAILED
                and self.tool_result is not None
            )
        ):
            raise ValueError("failed or skipped step result is incomplete or contradictory.")


@dataclass(frozen=True, slots=True)
class WorkflowStepProgress:
    """Privacy-safe lifecycle state for one planned step."""

    step_id: str
    status: WorkflowStepLifecycleStatus
    error_code: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowProgressSnapshot:
    """Immutable point-in-time progress for one sequential workflow run."""

    run_id: str
    workflow_identifier: str
    status: WorkflowProgressStatus
    current_step_id: str | None
    total_step_count: int
    completed_step_count: int
    failed_step_count: int
    skipped_step_count: int
    cancelled_step_count: int
    pending_step_count: int
    started_at: datetime
    finished_at: datetime | None
    execution_started: bool
    terminal: bool
    steps: tuple[WorkflowStepProgress, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "steps", tuple(self.steps))
        if self.total_step_count != len(self.steps):
            raise ValueError("progress total_step_count must match planned steps.")
        if any(
            not isinstance(count, int) or isinstance(count, bool) or count < 0
            for count in (
                self.completed_step_count,
                self.failed_step_count,
                self.skipped_step_count,
                self.cancelled_step_count,
                self.pending_step_count,
            )
        ):
            raise ValueError("workflow progress counts must be non-negative integers.")
        if (
            self.completed_step_count + self.pending_step_count
            > self.total_step_count
        ):
            raise ValueError("workflow progress counts exceed the planned steps.")
        if self.terminal != (self.finished_at is not None):
            raise ValueError("terminal progress must have exactly one finish timestamp.")
        if self.terminal == (self.status is WorkflowProgressStatus.RUNNING):
            raise ValueError("workflow progress status contradicts terminal state.")
        expected_counts = {
            "completed_step_count": sum(
                step.status
                in (
                    WorkflowStepLifecycleStatus.SUCCEEDED,
                    WorkflowStepLifecycleStatus.FAILED,
                    WorkflowStepLifecycleStatus.SKIPPED,
                    WorkflowStepLifecycleStatus.CANCELLED,
                )
                for step in self.steps
            ),
            "failed_step_count": sum(
                step.status is WorkflowStepLifecycleStatus.FAILED
                for step in self.steps
            ),
            "skipped_step_count": sum(
                step.status is WorkflowStepLifecycleStatus.SKIPPED
                for step in self.steps
            ),
            "cancelled_step_count": sum(
                step.status is WorkflowStepLifecycleStatus.CANCELLED
                for step in self.steps
            ),
            "pending_step_count": sum(
                step.status is WorkflowStepLifecycleStatus.PENDING
                for step in self.steps
            ),
        }
        if any(
            getattr(self, name) != count for name, count in expected_counts.items()
        ):
            raise ValueError("workflow progress counts do not match step lifecycles.")
        running_steps = tuple(
            step.step_id
            for step in self.steps
            if step.status is WorkflowStepLifecycleStatus.RUNNING
        )
        if (
            len(running_steps) > 1
            or self.current_step_id
            != (running_steps[0] if running_steps else None)
        ):
            raise ValueError("current_step_id does not match running step lifecycle.")


@dataclass(frozen=True, slots=True)
class WorkflowProgressNotificationIssue:
    """Safe diagnostic for a progress subscriber callback failure."""

    subscription_id: int
    error_type: str


@dataclass(frozen=True, slots=True)
class WorkflowProgressNotificationDiagnostics:
    """Immutable, privacy-safe summary of notification delivery health.

    Dispatch attempts count callbacks actually entered. Successful deliveries
    count callbacks returning normally; callback failures count ordinary
    ``Exception`` instances raised by entered callbacks. The issue-count
    mapping contains the stable ``subscriber_callback_failed`` code, including
    a zero count. Active subscribers are registrations not yet unsubscribed;
    terminal notification dispatch may still be in progress after finalization
    and before cleanup completes.
    """

    dispatch_attempt_count: int
    successful_delivery_count: int
    callback_failure_count: int
    active_subscriber_count: int
    finalized: bool
    cleanup_completed: bool
    issue_counts: Mapping[str, int]

    def __post_init__(self) -> None:
        object.__setattr__(self, "issue_counts", MappingProxyType(dict(self.issue_counts)))


class _WorkflowProgressSubscriber:
    def __init__(
        self,
        subscription_id: int,
        callback: Callable[[WorkflowProgressSnapshot], None],
    ) -> None:
        self.subscription_id = subscription_id
        self._callback: Callable[[WorkflowProgressSnapshot], None] | None = callback
        self._lock = RLock()
        self._active = True

    def dispatch(
        self,
        snapshot: WorkflowProgressSnapshot,
        on_attempt: Callable[[], None],
    ) -> tuple[bool, type[Exception] | None]:
        with self._lock:
            callback = self._callback
            if not self._active or callback is None:
                return False, None
            on_attempt()
            try:
                callback(snapshot)
            except Exception as error:
                return True, type(error)
        return True, None

    def unsubscribe(self) -> None:
        with self._lock:
            self._active = False
            self._callback = None


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    """Honest workflow outcome; prior side effects are not rolled back."""

    workflow_identifier: str
    status: WorkflowStatus
    step_results: tuple[WorkflowStepResult, ...]
    preflight_issues: tuple[PreflightIssue, ...]
    successful_step_count: int
    failed_step_count: int
    skipped_step_count: int
    execution_began: bool
    execution_completed: bool
    summary: str
    outputs_included: bool = False
    run_id: str = ""
    events: tuple[WorkflowEvent, ...] = ()
    validation_issues: tuple[WorkflowValidationIssue, ...] = ()
    failure_category: FailureCategory | None = None
    error_code: str | None = None
    observability_issues: tuple[WorkflowObservabilityIssue, ...] = ()
    cancelled_step_count: int = 0
    cancellation_observed: bool = False
    progress: WorkflowProgressSnapshot | None = None
    notification_diagnostics: WorkflowProgressNotificationDiagnostics | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "step_results", tuple(self.step_results))
        object.__setattr__(self, "preflight_issues", tuple(self.preflight_issues))
        object.__setattr__(self, "events", tuple(self.events))
        object.__setattr__(self, "validation_issues", tuple(self.validation_issues))
        object.__setattr__(
            self, "observability_issues", tuple(self.observability_issues)
        )
        if any(
            not isinstance(count, int) or isinstance(count, bool) or count < 0
            for count in (
                self.successful_step_count,
                self.failed_step_count,
                self.skipped_step_count,
            )
        ):
            raise ValueError("workflow step counts must be non-negative integers.")
        actual_counts = {
            "successful_step_count": sum(
                step.status is StepStatus.SUCCEEDED for step in self.step_results
            ),
            "failed_step_count": sum(
                step.status
                in (
                    StepStatus.TOOL_FAILED,
                    StepStatus.INPUT_RESOLUTION_FAILED,
                    StepStatus.INVOCATION_ERROR,
                )
                for step in self.step_results
            ),
            "skipped_step_count": sum(
                step.status
                in (StepStatus.SKIPPED_DEPENDENCY, StepStatus.SKIPPED_POLICY)
                for step in self.step_results
            ),
            "cancelled_step_count": sum(
                step.status is StepStatus.CANCELLED for step in self.step_results
            ),
        }
        if (
            not isinstance(self.cancelled_step_count, int)
            or isinstance(self.cancelled_step_count, bool)
            or self.cancelled_step_count < 0
        ):
            raise ValueError("cancelled_step_count must be a non-negative integer.")
        if any(
            getattr(self, count_name) != count
            for count_name, count in actual_counts.items()
            if count_name != "cancelled_step_count"
        ):
            raise ValueError("workflow step counts do not match step results.")
        if self.cancelled_step_count != actual_counts["cancelled_step_count"]:
            raise ValueError("cancelled_step_count does not match step results.")
        if self.status is WorkflowStatus.PREFLIGHT_FAILED:
            if (
                self.execution_began
                or self.execution_completed
                or self.step_results
                or any(actual_counts.values())
                or self.cancellation_observed
            ):
                raise ValueError("preflight failure cannot contain executed step outcomes.")
        elif self.execution_completed:
            if sum(actual_counts.values()) != len(self.step_results):
                raise ValueError("completed workflow must report every step outcome.")
        if self.status in (
            WorkflowStatus.FAILED,
            WorkflowStatus.PARTIAL,
            WorkflowStatus.CANCELLED,
        ) and (not self.execution_began or not self.execution_completed):
            raise ValueError("terminal runtime outcomes must be fully executed results.")
        if self.status is WorkflowStatus.SUCCEEDED and (
            not self.execution_began
            or not self.execution_completed
            or actual_counts["failed_step_count"]
            or actual_counts["skipped_step_count"]
            or actual_counts["successful_step_count"] != len(self.step_results)
        ):
            raise ValueError("successful workflow result contains unsuccessful outcomes.")
        if self.status is WorkflowStatus.FAILED and (
            actual_counts["successful_step_count"]
            or not actual_counts["failed_step_count"]
        ):
            raise ValueError("failed workflow result must contain failures and no successes.")
        if self.status is WorkflowStatus.PARTIAL and (
            not actual_counts["successful_step_count"]
            or not actual_counts["failed_step_count"]
        ):
            raise ValueError("partial workflow result must contain both success and failure.")
        if self.status is WorkflowStatus.CANCELLED and not self.cancellation_observed:
            raise ValueError("cancelled workflow result must record observed cancellation.")
        if self.status is WorkflowStatus.SUCCEEDED and self.cancellation_observed:
            raise ValueError("successful workflow cannot claim observed cancellation.")
        if self.progress is not None:
            if (
                self.progress.workflow_identifier != self.workflow_identifier
                or self.progress.status.value != self.status.value
                or not self.progress.terminal
                or self.progress.execution_started != self.execution_began
                or self.progress.completed_step_count
                != sum(actual_counts.values())
                or self.progress.failed_step_count
                != actual_counts["failed_step_count"]
                or self.progress.skipped_step_count
                != actual_counts["skipped_step_count"]
                or self.progress.cancelled_step_count
                != actual_counts["cancelled_step_count"]
            ):
                raise ValueError("workflow progress does not match the final result.")
        if self.notification_diagnostics is not None and (
            not self.notification_diagnostics.finalized
            or not self.notification_diagnostics.cleanup_completed
        ):
            raise ValueError(
                "final workflow result requires completed notification cleanup."
            )

    @property
    def success(self) -> bool:
        """Whether every required workflow step completed successfully."""
        return self.status is WorkflowStatus.SUCCEEDED

    def step_result(self, step_id: str) -> WorkflowStepResult | None:
        """Return the outcome for a step ID, or ``None`` if it has no result."""
        if not isinstance(step_id, str):
            raise TypeError("step_id must be a string.")
        return next(
            (result for result in self.step_results if result.step_id == step_id),
            None,
        )


class WorkflowRunInspectionError(WorkflowError):
    """Base class for run-inspection failures."""


class UnknownWorkflowRunError(WorkflowRunInspectionError, LookupError):
    """Raised when a run identifier has never been retained."""


class EvictedWorkflowRunError(WorkflowRunInspectionError, LookupError):
    """Raised when a recently evicted run is inspected."""


@dataclass(frozen=True, slots=True)
class WorkflowEvent:
    """Privacy-safe lifecycle event; raw inputs and outputs are never included."""

    event_type: WorkflowEventType
    workflow_identifier: str
    run_id: str
    sequence_number: int
    elapsed_seconds: float
    step_id: str | None = None
    status: str | None = None
    error_code: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowStepSnapshot:
    """Safe status summary for one workflow step."""

    step_id: str
    tool_identifier: str
    status: StepStatus
    reason_code: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowRunSnapshot:
    """Immutable inspection snapshot for one retained workflow run."""

    run_id: str
    workflow_identifier: str
    status: WorkflowStatus
    elapsed_seconds: float
    steps: tuple[WorkflowStepSnapshot, ...]
    step_counts: Mapping[StepStatus, int]
    events: tuple[WorkflowEvent, ...]
    failure_codes: tuple[str, ...]
    progress: WorkflowProgressSnapshot | None = None
    notification_diagnostics: WorkflowProgressNotificationDiagnostics | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(
            self, "step_counts", MappingProxyType(dict(self.step_counts))
        )
        object.__setattr__(self, "events", tuple(self.events))
        object.__setattr__(self, "failure_codes", tuple(self.failure_codes))
        if self.progress is not None and (
            self.progress.run_id != self.run_id
            or self.progress.workflow_identifier != self.workflow_identifier
            or self.progress.status.value != self.status.value
            or not self.progress.terminal
            or self.progress.completed_step_count
            != sum(self.step_counts.values())
        ):
            raise ValueError("run snapshot progress does not match the workflow run.")
        if self.notification_diagnostics is not None and (
            not self.notification_diagnostics.finalized
            or not self.notification_diagnostics.cleanup_completed
        ):
            raise ValueError(
                "retained run snapshot requires completed notification cleanup."
            )


class WorkflowProgressTracker:
    """Thread-safe live access to immutable workflow progress snapshots.

    A tracker belongs to exactly one execution. Its snapshots contain status
    and safe error codes only; exception messages and tool values are excluded.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._snapshot: WorkflowProgressSnapshot | None = None
        self._run_id: str | None = None
        self._workflow_identifier: str | None = None
        self._started_at: datetime | None = None
        self._execution_started = False
        self._terminal = False
        self._step_statuses: list[WorkflowStepProgress] = []
        self._status = WorkflowProgressStatus.RUNNING
        self._current_step_id: str | None = None
        self._subscribers: dict[int, _WorkflowProgressSubscriber] = {}
        self._next_subscription_id = 1
        self._notification_issues: list[WorkflowProgressNotificationIssue] = []
        self._dispatch_attempt_count = 0
        self._successful_delivery_count = 0
        self._callback_failure_count = 0
        self._cleanup_in_progress = False
        self._cleanup_completed = False

    @property
    def progress(self) -> WorkflowProgressSnapshot | None:
        """Return the latest immutable progress snapshot, if a run has begun."""
        with self._lock:
            return self._snapshot

    @property
    def notification_issues(self) -> tuple[WorkflowProgressNotificationIssue, ...]:
        """Return safe diagnostics for subscriber callbacks that raised."""
        with self._lock:
            return tuple(self._notification_issues)

    @property
    def notification_diagnostics(self) -> WorkflowProgressNotificationDiagnostics:
        """Return an atomic immutable snapshot of notification and cleanup state."""
        with self._lock:
            issue_counts = {
                "subscriber_callback_failed": self._callback_failure_count,
            }
            return WorkflowProgressNotificationDiagnostics(
                dispatch_attempt_count=self._dispatch_attempt_count,
                successful_delivery_count=self._successful_delivery_count,
                callback_failure_count=self._callback_failure_count,
                active_subscriber_count=len(self._subscribers),
                finalized=self._terminal,
                cleanup_completed=self._cleanup_completed,
                issue_counts=issue_counts,
            )

    def subscribe(
        self, callback: Callable[[WorkflowProgressSnapshot], None]
    ) -> Callable[[], None]:
        """Subscribe to subsequent progress changes and return an unsubscribe function.

        The current snapshot, if any, is not delivered at subscription time.
        """
        if not callable(callback):
            raise TypeError("progress callback must be callable.")
        with self._lock:
            if self._terminal:
                raise RuntimeError("cannot subscribe to a finalized progress tracker.")
            subscription_id = self._next_subscription_id
            self._next_subscription_id += 1
            subscriber = _WorkflowProgressSubscriber(subscription_id, callback)
            self._subscribers[subscription_id] = subscriber

        def unsubscribe() -> None:
            with self._lock:
                if self._subscribers.get(subscription_id) is subscriber:
                    del self._subscribers[subscription_id]
            subscriber.unsubscribe()

        return unsubscribe

    def _begin(
        self,
        run_id: str,
        workflow: WorkflowDefinition,
        workflow_identifier: str,
    ) -> WorkflowProgressSnapshot:
        with self._lock:
            if self._snapshot is not None:
                raise InvalidWorkflowDefinitionError(
                    "WorkflowProgressTracker can be used for only one workflow run."
                )
            previous = self._snapshot
            self._run_id = run_id
            self._workflow_identifier = workflow_identifier
            self._started_at = datetime.now(timezone.utc)
            self._step_statuses = [
                WorkflowStepProgress(
                    step.step_id, WorkflowStepLifecycleStatus.PENDING
                )
                for step in workflow.steps
            ]
            snapshot = self._publish()
            subscribers = (
                tuple(self._subscribers.values())
                if snapshot != previous
                else ()
            )
        self._dispatch(snapshot, subscribers)
        return snapshot

    def _mark_execution_started(self) -> None:
        with self._lock:
            if self._terminal:
                raise RuntimeError("terminal workflow progress cannot be restarted.")
            previous = self._snapshot
            self._execution_started = True
            snapshot = self._publish()
            subscribers = (
                tuple(self._subscribers.values())
                if snapshot != previous
                else ()
            )
        self._dispatch(snapshot, subscribers)

    def _observe_event(
        self,
        event_type: WorkflowEventType,
        *,
        step_id: str | None,
        status: str | None,
        error_code: str | None,
    ) -> None:
        with self._lock:
            if self._snapshot is None:
                raise RuntimeError("workflow progress has not begun.")
            if self._terminal:
                raise RuntimeError("terminal workflow progress cannot change.")
            previous = self._snapshot
            if event_type is WorkflowEventType.STEP_STARTED:
                self._transition_step(
                    step_id, WorkflowStepLifecycleStatus.RUNNING, None
                )
            elif event_type in (
                WorkflowEventType.STEP_SUCCEEDED,
                WorkflowEventType.STEP_FAILED,
                WorkflowEventType.STEP_SKIPPED,
                WorkflowEventType.STEP_CANCELLED,
            ):
                lifecycle = {
                    WorkflowEventType.STEP_SUCCEEDED: (
                        WorkflowStepLifecycleStatus.SUCCEEDED
                    ),
                    WorkflowEventType.STEP_FAILED: WorkflowStepLifecycleStatus.FAILED,
                    WorkflowEventType.STEP_SKIPPED: (
                        WorkflowStepLifecycleStatus.SKIPPED
                    ),
                    WorkflowEventType.STEP_CANCELLED: (
                        WorkflowStepLifecycleStatus.CANCELLED
                    ),
                }[event_type]
                self._transition_step(step_id, lifecycle, error_code)
            elif event_type in (
                WorkflowEventType.WORKFLOW_COMPLETED,
                WorkflowEventType.WORKFLOW_FAILED,
                WorkflowEventType.WORKFLOW_PARTIAL,
                WorkflowEventType.WORKFLOW_CANCELLED,
            ):
                if status is None:
                    raise RuntimeError("terminal event is missing workflow status.")
                self._status = WorkflowProgressStatus(status)
                if self._status is WorkflowProgressStatus.RUNNING:
                    raise RuntimeError("workflow cannot terminalize as running.")
                self._terminal = True
                self._current_step_id = None
                self._publish(finished_at=datetime.now(timezone.utc))
            snapshot = self._snapshot
            subscribers = (
                tuple(self._subscribers.values())
                if snapshot is not previous and snapshot is not None
                else ()
            )
        if snapshot is not None:
            try:
                self._dispatch(snapshot, subscribers)
            finally:
                if snapshot.terminal:
                    self._finalize_subscribers()

    def _finalize_subscribers(self) -> None:
        with self._lock:
            if self._cleanup_completed or self._cleanup_in_progress:
                return
            self._cleanup_in_progress = True
            subscribers = tuple(self._subscribers.values())
            self._subscribers.clear()
        try:
            for subscriber in subscribers:
                subscriber.unsubscribe()
        finally:
            with self._lock:
                self._cleanup_in_progress = False
                self._cleanup_completed = True

    def _dispatch(
        self,
        snapshot: WorkflowProgressSnapshot,
        subscribers: tuple[_WorkflowProgressSubscriber, ...],
    ) -> None:
        for subscriber in subscribers:
            invoked, error_type = subscriber.dispatch(
                snapshot, self._record_dispatch_attempt
            )
            if not invoked:
                continue
            if error_type is not None:
                with self._lock:
                    self._callback_failure_count += 1
                    self._notification_issues.append(
                        WorkflowProgressNotificationIssue(
                            subscription_id=subscriber.subscription_id,
                            error_type=error_type.__name__,
                        )
                    )
            else:
                with self._lock:
                    self._successful_delivery_count += 1

    def _record_dispatch_attempt(self) -> None:
        with self._lock:
            self._dispatch_attempt_count += 1

    def _transition_step(
        self,
        step_id: str | None,
        status: WorkflowStepLifecycleStatus,
        error_code: str | None,
    ) -> None:
        if step_id is None:
            raise RuntimeError("step lifecycle event references an unknown step.")
        candidate_indexes = [
            index
            for index, step in enumerate(self._step_statuses)
            if step.step_id == step_id
        ]
        target_index = next(
            (
                index
                for index in candidate_indexes
                if self._step_statuses[index].status
                is WorkflowStepLifecycleStatus.RUNNING
            ),
            None,
        )
        if target_index is None:
            target_index = next(
                (
                    index
                    for index in candidate_indexes
                    if self._step_statuses[index].status
                    is WorkflowStepLifecycleStatus.PENDING
                ),
                None,
            )
        if target_index is None:
            raise RuntimeError("step lifecycle event references an unknown step.")
        previous = self._step_statuses[target_index].status
        if previous in (
            WorkflowStepLifecycleStatus.SUCCEEDED,
            WorkflowStepLifecycleStatus.FAILED,
            WorkflowStepLifecycleStatus.SKIPPED,
            WorkflowStepLifecycleStatus.CANCELLED,
        ):
            raise RuntimeError("completed step lifecycle cannot transition again.")
        if (
            status is WorkflowStepLifecycleStatus.RUNNING
            and previous is not WorkflowStepLifecycleStatus.PENDING
        ) or (
            status is not WorkflowStepLifecycleStatus.RUNNING
            and previous
            not in (
                WorkflowStepLifecycleStatus.PENDING,
                WorkflowStepLifecycleStatus.RUNNING,
            )
        ):
            raise RuntimeError("invalid workflow step lifecycle transition.")
        self._step_statuses[target_index] = WorkflowStepProgress(
            step_id, status, error_code
        )
        self._current_step_id = (
            step_id if status is WorkflowStepLifecycleStatus.RUNNING else None
        )
        self._publish()

    def _publish(
        self, *, finished_at: datetime | None = None
    ) -> WorkflowProgressSnapshot:
        steps = tuple(self._step_statuses)
        counts = {
            status: sum(step.status is status for step in steps)
            for status in WorkflowStepLifecycleStatus
        }
        snapshot = WorkflowProgressSnapshot(
            run_id=self._run_id or "",
            workflow_identifier=self._workflow_identifier or "",
            status=self._status,
            current_step_id=self._current_step_id,
            total_step_count=len(steps),
            completed_step_count=sum(
                counts[status]
                for status in (
                    WorkflowStepLifecycleStatus.SUCCEEDED,
                    WorkflowStepLifecycleStatus.FAILED,
                    WorkflowStepLifecycleStatus.SKIPPED,
                    WorkflowStepLifecycleStatus.CANCELLED,
                )
            ),
            failed_step_count=counts[WorkflowStepLifecycleStatus.FAILED],
            skipped_step_count=counts[WorkflowStepLifecycleStatus.SKIPPED],
            cancelled_step_count=counts[WorkflowStepLifecycleStatus.CANCELLED],
            pending_step_count=counts[WorkflowStepLifecycleStatus.PENDING],
            started_at=self._started_at or datetime.now(timezone.utc),
            finished_at=finished_at,
            execution_started=self._execution_started,
            terminal=self._terminal,
            steps=steps,
        )
        self._snapshot = snapshot
        return snapshot


@dataclass(frozen=True, slots=True)
class WorkflowObservabilityIssue:
    """Safe diagnostic when optional in-memory snapshot retention fails."""

    error_code: str
    error_type: str
    snapshot_available: bool


class WorkflowEngine:
    """Preflights workflows and executes them sequentially through ToolExecutor."""

    def __init__(
        self,
        workflows: WorkflowRegistry,
        tools: ToolRegistry,
        executor: ToolExecutor,
        *,
        max_retained_runs: int = 100,
    ) -> None:
        if not isinstance(workflows, WorkflowRegistry):
            raise InvalidWorkflowDefinitionError(
                "workflows must be a WorkflowRegistry."
            )
        if not isinstance(tools, ToolRegistry):
            raise InvalidWorkflowDefinitionError("tools must be a ToolRegistry.")
        if not isinstance(executor, ToolExecutor):
            raise InvalidWorkflowDefinitionError("executor must be a ToolExecutor.")
        if executor.registry is not tools:
            raise InvalidWorkflowDefinitionError(
                "executor and workflow engine must share the same ToolRegistry instance."
            )
        if (
            not isinstance(max_retained_runs, int)
            or isinstance(max_retained_runs, bool)
            or max_retained_runs < 1
        ):
            raise InvalidWorkflowDefinitionError(
                "max_retained_runs must be a positive integer."
            )
        self._workflows = workflows
        self._tools = tools
        self._executor = executor
        self._max_retained_runs = max_retained_runs
        self._retained_runs: dict[str, WorkflowRunSnapshot] = {}
        self._evicted_run_ids: deque[str] = deque()
        self._evicted_run_id_set: set[str] = set()
        self._run_lock = RLock()

    @property
    def max_retained_runs(self) -> int:
        """Maximum number of completed run snapshots held in memory."""
        return self._max_retained_runs

    def inspect_run(self, run_id: str) -> WorkflowRunSnapshot:
        """Return an immutable snapshot, or identify an unknown/evicted run."""
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string.")
        with self._run_lock:
            snapshot = self._retained_runs.get(run_id)
            if snapshot is not None:
                return snapshot
            if run_id in self._evicted_run_id_set:
                raise EvictedWorkflowRunError(
                    f"workflow run has been evicted from in-memory retention: {run_id}"
                )
        raise UnknownWorkflowRunError(f"unknown workflow run identifier: {run_id}")

    def _retain_snapshot(self, snapshot: WorkflowRunSnapshot) -> None:
        with self._run_lock:
            self._retained_runs[snapshot.run_id] = snapshot
            while len(self._retained_runs) > self._max_retained_runs:
                oldest_run_id = next(iter(self._retained_runs))
                del self._retained_runs[oldest_run_id]
                if len(self._evicted_run_ids) >= self._max_retained_runs:
                    expired_run_id = self._evicted_run_ids.popleft()
                    self._evicted_run_id_set.remove(expired_run_id)
                self._evicted_run_ids.append(oldest_run_id)
                self._evicted_run_id_set.add(oldest_run_id)

    def preflight(
        self,
        workflow_identifier: str,
        workflow_inputs: Mapping[str, object] | None = None,
    ) -> WorkflowPreflightResult:
        """Validate all statically knowable constraints without invoking tools."""
        workflow = self._workflows.get(workflow_identifier)
        safe_inputs, input_issues = _prepare_workflow_inputs(workflow_inputs)
        return self._preflight_with_inputs(
            workflow,
            safe_inputs,
            input_issues,
            expected_identifier=workflow_identifier,
        )

    def _preflight_with_inputs(
        self,
        workflow: WorkflowDefinition,
        safe_inputs: Mapping[str, object],
        input_issues: list[PreflightIssue],
        *,
        expected_identifier: str,
    ) -> WorkflowPreflightResult:
        validation = validate_workflow(
            workflow,
            expected_identifier=expected_identifier,
        )
        if not validation.valid:
            validation_preflight_issues = tuple(
                PreflightIssue(
                    issue.step_id,
                    FailureCategory.WORKFLOW_VALIDATION,
                    issue.error_code,
                    issue.message,
                )
                for issue in validation.issues
            )
            all_issues = tuple(input_issues) + validation_preflight_issues
            return WorkflowPreflightResult(
                validation.workflow_identifier or "invalid-workflow",
                False,
                all_issues,
                validation.issues,
            )
        issues = input_issues
        contracts: dict[str, ToolContract] = {}
        for step in workflow.steps:
            try:
                contracts[step.step_id] = self._tools.get(step.tool_identifier)
            except UnknownToolError:
                issues.append(
                    PreflightIssue(
                        step.step_id,
                        FailureCategory.PREFLIGHT,
                        "unknown_tool",
                        f"Tool '{step.tool_identifier}' is not registered.",
                    )
                )

        for index, step in enumerate(workflow.steps):
            contract = contracts.get(step.step_id)
            if contract is None:
                continue
            issues.extend(
                _validate_step_mapping(
                    workflow,
                    index,
                    step,
                    contract,
                    safe_inputs,
                )
            )
            if not contract.enabled:
                issues.append(
                    PreflightIssue(
                        step.step_id,
                        FailureCategory.PREFLIGHT,
                        "tool_disabled",
                        f"Tool '{contract.identifier}' is disabled.",
                    )
                )
            if contract.execution_availability is ExecutionAvailability.UNAVAILABLE:
                issues.append(
                    PreflightIssue(
                        step.step_id,
                        FailureCategory.PREFLIGHT,
                        "execution_unavailable",
                        f"Tool '{contract.identifier}' is marked execution-unavailable.",
                    )
                )
        ordered_issues = tuple(
            sorted(
                issues,
                key=lambda issue: (
                    -1 if issue.step_id is None else _step_index(workflow, issue.step_id),
                    issue.error_code,
                ),
            )
        )
        return WorkflowPreflightResult(
            workflow.identifier,
            not ordered_issues,
            ordered_issues,
            validation.issues,
        )

    def execute(
        self,
        workflow_identifier: str,
        workflow_inputs: Mapping[str, object] | None = None,
        *,
        include_outputs: bool = False,
        cancellation_token: WorkflowCancellationToken | None = None,
        progress_tracker: WorkflowProgressTracker | None = None,
    ) -> WorkflowResult:
        """Execute declared steps in order after successful whole-workflow preflight.

        The trace omits raw input values and successful tool outputs by default.
        Set ``include_outputs=True`` only when output disclosure is intended.
        A supplied cancellation token is observed after preflight, before each
        invocation, and after each synchronous invocation returns.
        """
        if not isinstance(include_outputs, bool):
            raise InvalidWorkflowDefinitionError("include_outputs must be a boolean.")
        if cancellation_token is not None and not isinstance(
            cancellation_token, WorkflowCancellationToken
        ):
            raise InvalidWorkflowDefinitionError(
                "cancellation_token must be a WorkflowCancellationToken."
            )
        if progress_tracker is None:
            progress_tracker = WorkflowProgressTracker()
        elif type(progress_tracker) is not WorkflowProgressTracker:
            raise InvalidWorkflowDefinitionError(
                "progress_tracker must be a WorkflowProgressTracker."
            )
        token = cancellation_token or WorkflowCancellationToken()
        workflow = self._workflows.get(workflow_identifier)
        if not token._claim():
            raise InvalidWorkflowDefinitionError(
                "cancellation_token can be used for only one workflow execution."
            )
        run_id = uuid4().hex
        started_at = monotonic()
        progress_tracker._begin(run_id, workflow, workflow_identifier)
        events: list[WorkflowEvent] = []
        terminal_recorded = False

        def record_event(
            event_type: WorkflowEventType,
            *,
            step_id: str | None = None,
            status: str | None = None,
            error_code: str | None = None,
        ) -> None:
            nonlocal terminal_recorded
            terminal_types = (
                WorkflowEventType.WORKFLOW_COMPLETED,
                WorkflowEventType.WORKFLOW_FAILED,
                WorkflowEventType.WORKFLOW_PARTIAL,
                WorkflowEventType.WORKFLOW_CANCELLED,
            )
            if terminal_recorded:
                raise RuntimeError("workflow run already has a terminal event.")
            is_terminal = event_type in terminal_types
            events.append(
                WorkflowEvent(
                    event_type=event_type,
                    workflow_identifier=workflow_identifier,
                    run_id=run_id,
                    sequence_number=len(events) + 1,
                    elapsed_seconds=max(0.0, monotonic() - started_at),
                    step_id=step_id,
                    status=status,
                    error_code=error_code,
                )
            )
            progress_tracker._observe_event(
                event_type,
                step_id=step_id,
                status=status,
                error_code=error_code,
            )
            if is_terminal:
                terminal_recorded = True

        def finish(result: WorkflowResult) -> WorkflowResult:
            cancellation_seen = token._close()
            if cancellation_seen and result.status is not WorkflowStatus.PREFLIGHT_FAILED:
                if result.status is WorkflowStatus.SUCCEEDED:
                    result = replace(
                        result,
                        status=WorkflowStatus.CANCELLED,
                        failure_category=FailureCategory.CANCELLATION,
                        error_code="workflow_cancelled",
                        summary=(
                            "Workflow cancellation was observed before terminalization."
                        ),
                        cancellation_observed=True,
                    )
                else:
                    result = replace(result, cancellation_observed=True)
            if result.status is WorkflowStatus.SUCCEEDED:
                terminal_type = WorkflowEventType.WORKFLOW_COMPLETED
                terminal_code = None
            elif result.status is WorkflowStatus.PARTIAL:
                terminal_type = WorkflowEventType.WORKFLOW_PARTIAL
                terminal_code = "workflow_partial_failure"
            elif result.status is WorkflowStatus.CANCELLED:
                terminal_type = WorkflowEventType.WORKFLOW_CANCELLED
                terminal_code = "workflow_cancelled"
            else:
                terminal_type = WorkflowEventType.WORKFLOW_FAILED
                terminal_code = (
                    "workflow_validation_failed"
                    if result.validation_issues
                    else "preflight_failed"
                    if result.status is WorkflowStatus.PREFLIGHT_FAILED
                    else result.error_code
                    if result.error_code is not None
                    else next(
                        (
                            step.error_code
                            for step in result.step_results
                            if step.error_code is not None
                        ),
                        "workflow_failed",
                    )
                )
            record_event(
                terminal_type,
                status=result.status.value,
                error_code=terminal_code,
            )
            progress = progress_tracker.progress
            if progress is None:
                raise RuntimeError("workflow progress was not initialized.")
            notification_diagnostics = progress_tracker.notification_diagnostics
            step_snapshots = tuple(
                WorkflowStepSnapshot(
                    step_id=step.step_id,
                    tool_identifier=step.tool_identifier,
                    status=step.status,
                    reason_code=step.error_code,
                )
                for step in result.step_results
            )
            step_counts = {
                step_status: sum(
                    step.status is step_status for step in step_snapshots
                )
                for step_status in StepStatus
            }
            failure_codes = {
                issue.error_code for issue in result.preflight_issues
            }
            if (
                result.error_code is not None
                and not result.preflight_issues
                and not result.validation_issues
            ):
                failure_codes.add(result.error_code)
            failure_codes.update(
                step.reason_code
                for step in step_snapshots
                if step.reason_code is not None
            )
            snapshot = WorkflowRunSnapshot(
                run_id=run_id,
                workflow_identifier=workflow_identifier,
                status=result.status,
                elapsed_seconds=max(0.0, monotonic() - started_at),
                steps=step_snapshots,
                step_counts=step_counts,
                events=tuple(events),
                failure_codes=tuple(sorted(failure_codes)),
                progress=progress,
                notification_diagnostics=notification_diagnostics,
            )
            finalized_result = replace(
                result,
                run_id=run_id,
                events=tuple(events),
                progress=progress,
                notification_diagnostics=notification_diagnostics,
            )
            try:
                self._retain_snapshot(snapshot)
            except Exception as error:
                with self._run_lock:
                    snapshot_available = self._retained_runs.get(run_id) is snapshot
                finalized_result = replace(
                    finalized_result,
                    observability_issues=(
                        WorkflowObservabilityIssue(
                            "snapshot_retention_failed",
                            type(error).__name__,
                            snapshot_available,
                        ),
                    ),
                )
            return finalized_result

        record_event(
            WorkflowEventType.RUN_STARTED,
            status="started",
        )
        try:
            safe_inputs, input_issues = _prepare_workflow_inputs(workflow_inputs)
            preflight = self._preflight_with_inputs(
                workflow,
                safe_inputs,
                input_issues,
                expected_identifier=workflow_identifier,
            )
        except Exception as error:
            record_event(
                WorkflowEventType.PREFLIGHT_COMPLETED,
                status="internal_error",
                error_code="workflow_internal_failure",
            )
            return finish(
                WorkflowResult(
                    workflow_identifier=workflow_identifier,
                    status=WorkflowStatus.PREFLIGHT_FAILED,
                    step_results=(),
                    preflight_issues=(),
                    successful_step_count=0,
                    failed_step_count=0,
                    skipped_step_count=0,
                    execution_began=False,
                    execution_completed=False,
                    summary=(
                        "Preflight could not be completed because an internal "
                        "workflow error occurred."
                    ),
                    outputs_included=include_outputs,
                    failure_category=FailureCategory.WORKFLOW_RUNTIME,
                    error_code="workflow_internal_failure",
                )
            )
        record_event(
            WorkflowEventType.PREFLIGHT_COMPLETED,
            status="valid" if preflight.valid else "invalid",
            error_code=(
                None
                if preflight.valid
                else "workflow_validation_failed"
                if preflight.validation_issues
                else "preflight_failed"
            ),
        )
        if not preflight.valid:
            return finish(
                WorkflowResult(
                    workflow_identifier=workflow_identifier,
                    status=WorkflowStatus.PREFLIGHT_FAILED,
                    step_results=(),
                    preflight_issues=preflight.issues,
                    successful_step_count=0,
                    failed_step_count=0,
                    skipped_step_count=0,
                    execution_began=False,
                    execution_completed=False,
                    summary="Preflight failed; no tool invocation was attempted.",
                    outputs_included=include_outputs,
                    validation_issues=preflight.validation_issues,
                    failure_category=(
                        FailureCategory.WORKFLOW_VALIDATION
                        if preflight.validation_issues
                        else FailureCategory.PREFLIGHT
                    ),
                    error_code=(
                        "workflow_validation_failed"
                        if preflight.validation_issues
                        else "preflight_failed"
                    ),
                )
            )
        progress_tracker._mark_execution_started()
        completed_outputs: dict[str, Mapping[str, object]] = {}
        failed_steps: set[str] = set()
        results: list[WorkflowStepResult] = []
        stop_requested = False

        for step in workflow.steps:
            if stop_requested:
                result = _skipped_result(
                    step,
                    StepStatus.SKIPPED_POLICY,
                    FailureCategory.FAILURE_POLICY,
                    "stopped_after_failure",
                    "Skipped because STOP_ON_FAILURE halted the workflow.",
                )
                results.append(result)
                record_event(
                    WorkflowEventType.STEP_SKIPPED,
                    step_id=step.step_id,
                    status=result.status.value,
                    error_code=result.error_code,
                )
                failed_steps.add(step.step_id)
                continue
            if token.is_cancelled:
                result = _cancelled_result(step)
                results.append(result)
                record_event(
                    WorkflowEventType.STEP_CANCELLED,
                    step_id=step.step_id,
                    status=result.status.value,
                    error_code=result.error_code,
                )
                continue

            dependencies = _step_dependencies(step)
            failed_dependencies = sorted(dependencies.intersection(failed_steps))
            if failed_dependencies:
                result = _skipped_result(
                    step,
                    StepStatus.SKIPPED_DEPENDENCY,
                    FailureCategory.DEPENDENCY,
                    "dependency_failed",
                    "Skipped because dependency step(s) did not succeed: "
                    + ", ".join(failed_dependencies)
                    + ".",
                )
                results.append(result)
                record_event(
                    WorkflowEventType.STEP_SKIPPED,
                    step_id=step.step_id,
                    status=result.status.value,
                    error_code=result.error_code,
                )
                failed_steps.add(step.step_id)
                continue

            record_event(
                WorkflowEventType.STEP_STARTED,
                step_id=step.step_id,
                status="started",
            )
            try:
                contract = self._tools.get(step.tool_identifier)
                resolved, input_metadata = _resolve_step_inputs(
                    step, safe_inputs, completed_outputs
                )
            except (MissingWorkflowInputError, MissingStepOutputError) as error:
                error_code = (
                    "missing_workflow_input"
                    if isinstance(error, MissingWorkflowInputError)
                    else "missing_step_output"
                )
                results.append(
                    _skipped_result(
                        step,
                        StepStatus.INPUT_RESOLUTION_FAILED,
                        FailureCategory.INPUT_RESOLUTION,
                        error_code,
                        str(error),
                    )
                )
                record_event(
                    WorkflowEventType.STEP_FAILED,
                    step_id=step.step_id,
                    status=StepStatus.INPUT_RESOLUTION_FAILED.value,
                    error_code=error_code,
                )
                failed_steps.add(step.step_id)
                if workflow.failure_policy is WorkflowFailurePolicy.STOP_ON_FAILURE:
                    stop_requested = True
                continue
            except UnknownToolError:
                error_code = "missing_tool_after_preflight"
                results.append(
                    _skipped_result(
                        step,
                        StepStatus.INVOCATION_ERROR,
                        FailureCategory.TOOL_INVOCATION,
                        error_code,
                        "The Tool registration disappeared after workflow preflight.",
                    )
                )
                record_event(
                    WorkflowEventType.STEP_FAILED,
                    step_id=step.step_id,
                    status=StepStatus.INVOCATION_ERROR.value,
                    error_code=error_code,
                )
                failed_steps.add(step.step_id)
                if workflow.failure_policy is WorkflowFailurePolicy.STOP_ON_FAILURE:
                    stop_requested = True
                continue
            except Exception:
                error_code = "workflow_internal_failure"
                results.append(
                    _skipped_result(
                        step,
                        StepStatus.INVOCATION_ERROR,
                        FailureCategory.WORKFLOW_RUNTIME,
                        error_code,
                        "An internal workflow error prevented input resolution.",
                    )
                )
                record_event(
                    WorkflowEventType.STEP_FAILED,
                    step_id=step.step_id,
                    status=StepStatus.INVOCATION_ERROR.value,
                    error_code=error_code,
                )
                failed_steps.add(step.step_id)
                if workflow.failure_policy is WorkflowFailurePolicy.STOP_ON_FAILURE:
                    stop_requested = True
                continue

            if token.is_cancelled:
                result = _cancelled_result(step, input_metadata=input_metadata)
                results.append(result)
                record_event(
                    WorkflowEventType.STEP_CANCELLED,
                    step_id=step.step_id,
                    status=result.status.value,
                    error_code=result.error_code,
                )
                continue

            try:
                request = ToolInvocationRequest(contract.identifier, resolved)
                tool_result = self._executor.invoke(request)
            except WorkflowCancellationRequested:
                token.request_cancel()
                result = _cancelled_result(step, input_metadata=input_metadata)
                results.append(result)
                record_event(
                    WorkflowEventType.STEP_CANCELLED,
                    step_id=step.step_id,
                    status=result.status.value,
                    error_code=result.error_code,
                )
                continue
            except (InvalidToolInputError, UnknownToolError) as error:
                error_code = (
                    "unknown_tool_after_preflight"
                    if isinstance(error, UnknownToolError)
                    else "invalid_tool_input"
                )
                results.append(
                    _skipped_result(
                        step,
                        StepStatus.INVOCATION_ERROR,
                        FailureCategory.TOOL_INVOCATION,
                        error_code,
                        (
                            "Tool registration changed after preflight."
                            if isinstance(error, UnknownToolError)
                            else "The resolved input did not satisfy the Tool invocation contract."
                        ),
                        input_metadata=input_metadata,
                    )
                )
                record_event(
                    WorkflowEventType.STEP_FAILED,
                    step_id=step.step_id,
                    status=StepStatus.INVOCATION_ERROR.value,
                    error_code=error_code,
                )
                failed_steps.add(step.step_id)
                if workflow.failure_policy is WorkflowFailurePolicy.STOP_ON_FAILURE:
                    stop_requested = True
                continue
            except Exception:
                error_code = "tool_execution_exception"
                results.append(
                    _skipped_result(
                        step,
                        StepStatus.INVOCATION_ERROR,
                        FailureCategory.TOOL_INVOCATION,
                        error_code,
                        "The Tool executor raised an unexpected exception.",
                        input_metadata=input_metadata,
                    )
                )
                record_event(
                    WorkflowEventType.STEP_FAILED,
                    step_id=step.step_id,
                    status=StepStatus.INVOCATION_ERROR.value,
                    error_code=error_code,
                )
                failed_steps.add(step.step_id)
                if workflow.failure_policy is WorkflowFailurePolicy.STOP_ON_FAILURE:
                    stop_requested = True
                continue

            tool_result, normalized_output = _normalize_tool_result(
                tool_result,
                request_id=request.request_id,
                tool_identifier=contract.identifier,
            )
            if tool_result.status is ToolStatus.SUCCEEDED:
                output = dict(normalized_output or {})
                completed_outputs[step.step_id] = MappingProxyType(output)
                trace_result = (
                    tool_result
                    if include_outputs
                    else replace(tool_result, output=None)
                )
                results.append(
                    WorkflowStepResult(
                        step_id=step.step_id,
                        tool_identifier=step.tool_identifier,
                        status=StepStatus.SUCCEEDED,
                        tool_result=trace_result,
                        input_metadata=input_metadata,
                        output_metadata=tuple(
                            OutputValueMetadata(name, _value_type(value))
                            for name, value in sorted(output.items())
                        ),
                        explanation="Tool invocation succeeded.",
                    )
                )
                record_event(
                    WorkflowEventType.STEP_SUCCEEDED,
                    step_id=step.step_id,
                    status=StepStatus.SUCCEEDED.value,
                )
            else:
                results.append(
                    WorkflowStepResult(
                        step_id=step.step_id,
                        tool_identifier=step.tool_identifier,
                        status=StepStatus.TOOL_FAILED,
                        tool_result=tool_result,
                        input_metadata=input_metadata,
                        failure_category=FailureCategory.TOOL_INVOCATION,
                        error_code=tool_result.error_code or tool_result.status.value,
                        explanation=(
                            "Tool invocation failed with status "
                            f"'{tool_result.status.value}'."
                        ),
                    )
                )
                record_event(
                    WorkflowEventType.STEP_FAILED,
                    step_id=step.step_id,
                    status=StepStatus.TOOL_FAILED.value,
                    error_code=tool_result.error_code or tool_result.status.value,
                )
                failed_steps.add(step.step_id)
                if workflow.failure_policy is WorkflowFailurePolicy.STOP_ON_FAILURE:
                    stop_requested = True

        successful = sum(result.status is StepStatus.SUCCEEDED for result in results)
        failed = sum(
            result.status
            in (
                StepStatus.TOOL_FAILED,
                StepStatus.INPUT_RESOLUTION_FAILED,
                StepStatus.INVOCATION_ERROR,
            )
            for result in results
        )
        skipped = sum(
            result.status
            in (StepStatus.SKIPPED_DEPENDENCY, StepStatus.SKIPPED_POLICY)
            for result in results
        )
        cancelled = sum(
            result.status is StepStatus.CANCELLED for result in results
        )
        cancellation_observed = token.is_cancelled
        if failed:
            if successful:
                status = WorkflowStatus.PARTIAL
                summary = (
                    "Workflow execution completed with failed or skipped steps."
                )
            else:
                status = WorkflowStatus.FAILED
                summary = "Workflow execution failed before any step succeeded."
        elif cancellation_observed:
            status = WorkflowStatus.CANCELLED
            summary = "Workflow cancellation was observed; no further steps were started."
        else:
            status = WorkflowStatus.SUCCEEDED
            summary = "All workflow steps completed successfully."
        return finish(
            WorkflowResult(
                workflow_identifier=workflow_identifier,
                status=status,
                step_results=tuple(results),
                preflight_issues=(),
                successful_step_count=successful,
                failed_step_count=failed,
                skipped_step_count=skipped,
                execution_began=True,
                execution_completed=True,
                summary=summary
                + " Sequential execution is not atomic; earlier side effects are not rolled back.",
                outputs_included=include_outputs,
                cancelled_step_count=cancelled,
                cancellation_observed=cancellation_observed,
                failure_category=(
                    FailureCategory.CANCELLATION
                    if status is WorkflowStatus.CANCELLED
                    else None
                    if failed == 0
                    else next(
                        (
                            result.failure_category
                            for result in results
                            if result.status
                            in (
                                StepStatus.TOOL_FAILED,
                                StepStatus.INPUT_RESOLUTION_FAILED,
                                StepStatus.INVOCATION_ERROR,
                            )
                            and result.failure_category is not None
                        ),
                        FailureCategory.WORKFLOW_RUNTIME,
                    )
                ),
                error_code=(
                    "workflow_cancelled"
                    if status is WorkflowStatus.CANCELLED
                    else None
                    if failed == 0
                    else next(
                        (
                            result.error_code
                            for result in results
                            if result.error_code is not None
                        ),
                        "workflow_failed",
                    )
                ),
            )
        )


def _validate_step_mapping(
    workflow: WorkflowDefinition,
    step_index: int,
    step: WorkflowStep,
    contract: ToolContract,
    workflow_inputs: Mapping[str, object],
) -> list[PreflightIssue]:
    issues: list[PreflightIssue] = []
    declared = {field.name: field for field in contract.input_schema}
    mapped_names = set(step.input_mapping)
    if not contract.allow_additional_inputs:
        for name in sorted(mapped_names.difference(declared)):
            issues.append(
                PreflightIssue(
                    step.step_id,
                    FailureCategory.PREFLIGHT,
                    "unsupported_tool_input",
                    f"Input '{name}' is not declared by Tool '{contract.identifier}'.",
                )
            )
    for name in sorted(
        field.name
        for field in contract.input_schema
        if field.required and field.name not in mapped_names
    ):
        issues.append(
            PreflightIssue(
                step.step_id,
                FailureCategory.PREFLIGHT,
                "required_tool_input_unmapped",
                f"Required Tool input '{name}' has no workflow mapping.",
            )
        )
    for input_name, source in step.input_mapping.items():
        field = declared.get(input_name)
        if isinstance(source, WorkflowInputRef):
            if source.name not in workflow_inputs:
                issues.append(
                    PreflightIssue(
                        step.step_id,
                        FailureCategory.PREFLIGHT,
                        "missing_workflow_input",
                        f"Workflow input '{source.name}' is not supplied.",
                    )
                )
            elif field is not None and not _matches_input_type(
                field.value_type, _thaw_value(workflow_inputs[source.name])
            ):
                issues.append(
                    PreflightIssue(
                        step.step_id,
                        FailureCategory.PREFLIGHT,
                        "workflow_input_type_mismatch",
                        f"Workflow input reference for '{input_name}' has the wrong type.",
                    )
                )
        elif isinstance(source, StepOutputRef):
            source_index = _step_index(workflow, source.step_id)
            if source_index >= step_index:
                issues.append(
                    PreflightIssue(
                        step.step_id,
                        FailureCategory.PREFLIGHT,
                        "step_output_not_prior",
                        f"Output reference '{source.step_id}.{source.field}' must target "
                        "an earlier step.",
                    )
                )
            # ToolContract does not declare output schemas; output field and type
            # availability are intentionally validated only after that step runs.
        elif field is not None and not _matches_input_type(
            field.value_type, _thaw_value(source)
        ):
            issues.append(
                PreflightIssue(
                    step.step_id,
                    FailureCategory.PREFLIGHT,
                    "literal_input_type_mismatch",
                    f"Literal mapping for Tool input '{input_name}' has the wrong type.",
                )
            )
    return issues


def _resolve_step_inputs(
    step: WorkflowStep,
    workflow_inputs: Mapping[str, object],
    completed_outputs: Mapping[str, Mapping[str, object]],
) -> tuple[dict[str, object], tuple[InputValueMetadata, ...]]:
    resolved: dict[str, object] = {}
    metadata: list[InputValueMetadata] = []
    for name, source in step.input_mapping.items():
        value = _resolve_value(source, workflow_inputs, completed_outputs)
        resolved[name] = value
        metadata.append(
            InputValueMetadata(name, _source_kind(source), _value_type(value))
        )
    return resolved, tuple(sorted(metadata, key=lambda item: item.name))


def _resolve_value(
    source: object,
    workflow_inputs: Mapping[str, object],
    completed_outputs: Mapping[str, Mapping[str, object]],
) -> object:
    if isinstance(source, WorkflowInputRef):
        if source.name not in workflow_inputs:
            raise MissingWorkflowInputError(
                f"workflow input '{source.name}' was not supplied."
            )
        return _thaw_value(workflow_inputs[source.name])
    if isinstance(source, StepOutputRef):
        output = completed_outputs.get(source.step_id)
        if output is None or source.field not in output:
            raise MissingStepOutputError(
                f"successful output '{source.step_id}.{source.field}' is unavailable."
            )
        return output[source.field]
    return _thaw_value(source)


def _freeze_mapping_value(value: object) -> object:
    return _freeze_value(value, set())


def _freeze_value(value: object, ancestors: set[int]) -> object:
    if isinstance(value, (WorkflowInputRef, StepOutputRef)):
        return value
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidStepInputMappingError(
                "literal floating-point values must be finite."
            )
        return value
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in ancestors:
            raise InvalidStepInputMappingError(
                "literal input values cannot contain circular references."
            )
        ancestors.add(identity)
        frozen: dict[str, object] = {}
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise InvalidStepInputMappingError(
                        "literal object keys must be strings."
                    )
                frozen[key] = _freeze_value(item, ancestors)
            return MappingProxyType(frozen)
        finally:
            ancestors.remove(identity)
    if isinstance(value, list):
        identity = id(value)
        if identity in ancestors:
            raise InvalidStepInputMappingError(
                "literal input values cannot contain circular references."
            )
        ancestors.add(identity)
        try:
            return tuple(_freeze_value(item, ancestors) for item in value)
        finally:
            ancestors.remove(identity)
    raise InvalidStepInputMappingError(
        f"unsupported literal input value type: {type(value).__name__}."
    )


def _freeze_input_object(inputs: Mapping[str, object]) -> Mapping[str, object]:
    if not isinstance(inputs, Mapping):
        raise InvalidStepInputMappingError(
            "workflow_inputs must be a mapping with string keys."
        )
    frozen: dict[str, object] = {}
    for key, value in inputs.items():
        if not isinstance(key, str) or not _FIELD_PATTERN.fullmatch(key):
            raise InvalidStepInputMappingError(
                "workflow input names must be valid lowercase identifiers."
            )
        if _contains_reference(value):
            raise InvalidStepInputMappingError(
                "workflow input values must be JSON-compatible data, not references."
            )
        frozen[key] = _freeze_mapping_value(value)
    return MappingProxyType(frozen)


def _prepare_workflow_inputs(
    inputs: Mapping[str, object] | None,
) -> tuple[Mapping[str, object], list[PreflightIssue]]:
    try:
        safe_inputs = _freeze_input_object({} if inputs is None else inputs)
    except InvalidStepInputMappingError as error:
        safe_inputs = MappingProxyType({})
        return safe_inputs, [
            PreflightIssue(
                None,
                FailureCategory.PREFLIGHT,
                "invalid_workflow_inputs",
                str(error),
            )
        ]
    return safe_inputs, []


def _thaw_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_value(item) for item in value]
    return value


def _matches_input_type(value_type: object, value: object) -> bool:
    if value_type is InputType.STRING:
        return isinstance(value, str)
    if value_type is InputType.INTEGER:
        return isinstance(value, int) and not isinstance(value, bool)
    if value_type is InputType.BOOLEAN:
        return isinstance(value, bool)
    if value_type is InputType.STRING_LIST:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
    return False


def _referenced_step_ids(value: object) -> set[str]:
    if isinstance(value, StepOutputRef):
        return {value.step_id}
    if isinstance(value, Mapping):
        referenced: set[str] = set()
        for item in value.values():
            referenced.update(_referenced_step_ids(item))
        return referenced
    if isinstance(value, (list, tuple)):
        referenced = set()
        for item in value:
            referenced.update(_referenced_step_ids(item))
        return referenced
    return set()


def _contains_reference(value: object, ancestors: set[int] | None = None) -> bool:
    if isinstance(value, (WorkflowInputRef, StepOutputRef)):
        return True
    if ancestors is None:
        ancestors = set()
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in ancestors:
            return False
        ancestors.add(identity)
        try:
            return any(
                _contains_reference(item, ancestors) for item in value.values()
            )
        finally:
            ancestors.remove(identity)
    if isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in ancestors:
            return False
        ancestors.add(identity)
        try:
            return any(_contains_reference(item, ancestors) for item in value)
        finally:
            ancestors.remove(identity)
    return False


def _step_dependencies(step: WorkflowStep) -> set[str]:
    return set(step.depends_on).union(_referenced_step_ids(step.input_mapping))


def _step_index(workflow: WorkflowDefinition, step_id: str) -> int:
    for index, step in enumerate(workflow.steps):
        if step.step_id == step_id:
            return index
    return len(workflow.steps)


def _source_kind(source: object) -> InputSourceKind:
    if isinstance(source, WorkflowInputRef):
        return InputSourceKind.WORKFLOW_INPUT
    if isinstance(source, StepOutputRef):
        return InputSourceKind.STEP_OUTPUT
    return InputSourceKind.LITERAL


def _value_type(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, Mapping):
        return "object"
    if isinstance(value, (list, tuple)):
        return "array"
    return "unsupported"


def _skipped_result(
    step: WorkflowStep,
    status: StepStatus,
    category: FailureCategory,
    error_code: str,
    explanation: str,
    *,
    input_metadata: tuple[InputValueMetadata, ...] = (),
) -> WorkflowStepResult:
    return WorkflowStepResult(
        step_id=step.step_id,
        tool_identifier=step.tool_identifier,
        status=status,
        input_metadata=input_metadata,
        failure_category=category,
        error_code=error_code,
        explanation=explanation,
    )


def _cancelled_result(
    step: WorkflowStep,
    *,
    input_metadata: tuple[InputValueMetadata, ...] = (),
) -> WorkflowStepResult:
    return WorkflowStepResult(
        step_id=step.step_id,
        tool_identifier=step.tool_identifier,
        status=StepStatus.CANCELLED,
        input_metadata=input_metadata,
        failure_category=FailureCategory.CANCELLATION,
        error_code="workflow_cancelled",
        explanation="Step was not completed because workflow cancellation was observed.",
    )


def _normalize_tool_result(
    result: object,
    *,
    request_id: str,
    tool_identifier: str,
) -> tuple[ToolExecutionResult, Mapping[str, object] | None]:
    """Validate and sanitize an executor result before it affects run state."""
    if not isinstance(result, ToolExecutionResult):
        return _malformed_tool_result(request_id, tool_identifier), None
    if (
        not isinstance(result.request_id, str)
        or not isinstance(result.tool_identifier, str)
        or result.request_id != request_id
        or result.tool_identifier != tool_identifier
        or not isinstance(result.status, ToolStatus)
    ):
        return _malformed_tool_result(request_id, tool_identifier), None

    if result.status is ToolStatus.SUCCEEDED:
        if result.error_code is not None or result.error is not None:
            return _malformed_tool_result(request_id, tool_identifier), None
        try:
            if (
                not isinstance(result.output, Mapping)
                or _contains_reference(result.output)
            ):
                return _invalid_tool_output(request_id, tool_identifier), None
            output = _freeze_mapping_value(result.output)
        except Exception:
            return _invalid_tool_output(request_id, tool_identifier), None
        if not isinstance(output, Mapping):
            return _invalid_tool_output(request_id, tool_identifier), None
        safe_result = ToolExecutionResult(
            request_id=request_id,
            tool_identifier=tool_identifier,
            status=ToolStatus.SUCCEEDED,
            output=output,
        )
        return safe_result, output

    if result.output is not None:
        return _malformed_tool_result(request_id, tool_identifier), None
    expected_codes = {
        ToolStatus.DISABLED: {"tool_disabled"},
        ToolStatus.UNAVAILABLE: {"execution_unavailable"},
        ToolStatus.INVALID_INPUT: {"invalid_input"},
        ToolStatus.ADAPTER_MISSING: {"adapter_missing"},
        ToolStatus.ADAPTER_INCOMPATIBLE: {"adapter_incompatible"},
        ToolStatus.FAILED: {"runtime_failure", "tool_execution_failed"},
    }
    allowed_codes = expected_codes[result.status]
    code = result.error_code
    if not isinstance(code, str) or code not in allowed_codes:
        code = (
            "tool_execution_failed"
            if result.status is ToolStatus.FAILED
            else next(iter(allowed_codes))
        )
    return (
        ToolExecutionResult(
            request_id=request_id,
            tool_identifier=tool_identifier,
            status=result.status,
            error_code=code,
        ),
        None,
    )


def _malformed_tool_result(
    request_id: str,
    tool_identifier: str,
) -> ToolExecutionResult:
    return ToolExecutionResult(
        request_id=request_id,
        tool_identifier=tool_identifier,
        status=ToolStatus.FAILED,
        error_code="malformed_tool_result",
    )


def _invalid_tool_output(
    request_id: str,
    tool_identifier: str,
) -> ToolExecutionResult:
    return ToolExecutionResult(
        request_id=request_id,
        tool_identifier=tool_identifier,
        status=ToolStatus.FAILED,
        error_code="invalid_tool_output",
    )

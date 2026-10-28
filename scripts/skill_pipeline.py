"""Deterministic Skill discovery, selection, preparation, and explicit execution.

Task matching is lexical overlap, not semantic understanding. Skill source is
supplied only to explicitly configured in-process execution adapters; Markdown
is never interpreted as Python, shell, or provider instructions by this module.
Adapters can invoke only tools declared by the registered Skill and only through
an explicitly configured ToolExecutor.
"""

from __future__ import annotations

import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Mapping

from scripts.skill_registry import (
    DEFAULT_CONTRACT_VERSION,
    DiscoveryIssue,
    DuplicateSkillError,
    SkillContract,
    SkillContractVersionError,
    SkillMetadataError,
    SkillNotFoundError,
    SkillRegistry,
    discover_skills,
    is_valid_contract_version,
)
from scripts.tool_framework import (
    ToolExecutionResult,
    ToolExecutor,
    ToolInvocationRequest,
    ToolStatus,
)


_WORD_PATTERN = re.compile(r"[a-z0-9]+")


class SelectionError(ValueError):
    """Raised when a Skill selection request is malformed or conflicts."""


class InvocationValidationError(ValueError):
    """Raised when invocation request data violates its contract."""


class ExecutionUnavailableError(RuntimeError):
    """Raised when execution is requested without an execution engine."""


class SkillExecutionStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"


class SelectionStatus(str, Enum):
    SELECTED = "selected"
    NO_MATCH = "no_match"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class SelectionCandidate:
    """A Skill candidate with transparent lexical matching evidence."""

    skill: SkillContract
    score: int
    matched_terms: tuple[str, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SelectionResult:
    """Selection outcome; ``selected`` is set only for an unambiguous winner."""

    status: SelectionStatus
    candidates: tuple[SelectionCandidate, ...]
    selected: SkillContract | None = None
    message: str = ""


@dataclass(frozen=True, slots=True)
class PipelineDiscoveryResult:
    """Discovery plus successful registrations and all explicit issues."""

    discovered: tuple[SkillContract, ...]
    registered_identifiers: tuple[str, ...]
    issues: tuple[DiscoveryIssue, ...]


@dataclass(frozen=True, slots=True)
class InvocationRequest:
    """Validated intent to invoke a Skill; creation performs no execution."""

    skill_identifier: str
    task: str
    inputs: Mapping[str, object] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    contract_version: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.skill_identifier, str) or not self.skill_identifier.strip():
            raise InvocationValidationError("skill_identifier must be a non-empty string.")
        if not isinstance(self.task, str) or not self.task.strip():
            raise InvocationValidationError("task must be a non-empty string.")
        if not isinstance(self.request_id, str):
            raise InvocationValidationError("request_id must be a string.")
        try:
            parsed_id = uuid.UUID(self.request_id)
        except (ValueError, AttributeError) as error:
            raise InvocationValidationError("request_id must be a valid UUID.") from error
        if str(parsed_id) != self.request_id.lower():
            raise InvocationValidationError("request_id must use canonical UUID formatting.")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise InvocationValidationError("created_at must be a timezone-aware datetime.")
        if self.contract_version is not None and not is_valid_contract_version(
            self.contract_version
        ):
            raise InvocationValidationError(
                "contract_version must use canonical major.minor.patch format."
            )
        if not isinstance(self.inputs, Mapping):
            raise InvocationValidationError("inputs must be a mapping of string keys to values.")
        copied_inputs = dict(self.inputs)
        if any(not isinstance(key, str) or not key.strip() for key in copied_inputs):
            raise InvocationValidationError("input names must be non-empty strings.")
        object.__setattr__(self, "inputs", MappingProxyType(copied_inputs))


@dataclass(frozen=True, slots=True)
class InvocationPlan:
    """Validated invocation description that explicitly has not been executed."""

    request_id: str
    skill: SkillContract
    source_path: Path
    task: str
    inputs: Mapping[str, object]
    status: str = "PREPARED_NOT_EXECUTED"
    execution_available: bool = False
    contract_version: str | None = None


@dataclass(frozen=True, slots=True)
class SkillExecutionContext:
    """Resolved Skill content and caller intent supplied to an explicit adapter."""

    request_id: str
    skill: SkillContract
    task: str
    source_text: str
    inputs: Mapping[str, object]
    _tool_invoker: Callable[
        [str, Mapping[str, object]], ToolExecutionResult
    ] | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "inputs", MappingProxyType(dict(self.inputs)))

    def invoke_tool(
        self, tool_identifier: str, inputs: Mapping[str, object]
    ) -> ToolExecutionResult:
        """Invoke a tool through the execution boundary and return its outcome."""
        if self._tool_invoker is None:
            raise ExecutionUnavailableError(
                "no ToolExecutor is configured for this Skill invocation."
            )
        return self._tool_invoker(tool_identifier, inputs)


@dataclass(frozen=True, slots=True)
class SkillToolInvocation:
    """Safe trace of one tool-call attempt made during Skill execution."""

    skill_request_id: str
    request_id: str
    tool_identifier: str
    status: ToolStatus | None
    error_code: str | None = None

    def __post_init__(self) -> None:
        if self.status is not None and not isinstance(self.status, ToolStatus):
            raise ValueError("status must be a ToolStatus or None.")
        if self.status is None and self.error_code is None:
            raise ValueError("a rejected tool-call attempt requires a safe error code.")
        safe_error_codes = {
            "tool_disabled",
            "execution_unavailable",
            "invalid_input",
            "adapter_missing",
            "adapter_incompatible",
            "runtime_failure",
            "tool_failed",
            "tool_invocation_failed",
            "invalid_tool_request",
            "tool_not_allowed",
        }
        if self.error_code is not None and (
            not isinstance(self.error_code, str)
            or self.error_code not in safe_error_codes
        ):
            raise ValueError("error_code must be a safe tool error identifier.")


@dataclass(frozen=True, slots=True)
class SkillExecutionResult:
    """Safe structured outcome of one explicitly delegated Skill execution."""

    request_id: str
    skill_identifier: str
    status: SkillExecutionStatus
    started_at: datetime
    completed_at: datetime
    output: Mapping[str, object] | None = None
    error_code: str | None = None
    tool_invocations: tuple[SkillToolInvocation, ...] = ()
    contract_version: str = DEFAULT_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not is_valid_contract_version(self.contract_version):
            raise ValueError("contract_version must use canonical major.minor.patch format.")
        if self.output is not None:
            object.__setattr__(self, "output", MappingProxyType(dict(self.output)))
        if not isinstance(self.tool_invocations, tuple) or any(
            not isinstance(invocation, SkillToolInvocation)
            for invocation in self.tool_invocations
        ):
            raise ValueError("tool_invocations must contain SkillToolInvocation values.")
        if any(
            invocation.skill_request_id != self.request_id
            for invocation in self.tool_invocations
        ):
            raise ValueError("tool invocation traces must belong to this Skill request.")
        if self.completed_at < self.started_at:
            raise ValueError("completed_at cannot precede started_at.")
        if self.status is SkillExecutionStatus.SUCCEEDED:
            if (
                self.output is None
                or self.error_code is not None
                or any(
                    invocation.status is not ToolStatus.SUCCEEDED
                    for invocation in self.tool_invocations
                )
            ):
                raise ValueError("successful Skill execution requires output only.")
        elif self.status is SkillExecutionStatus.UNAVAILABLE:
            if (
                self.output is not None
                or self.error_code != "execution_unavailable"
            ):
                raise ValueError("unavailable Skill execution requires execution_unavailable.")
        elif self.status is SkillExecutionStatus.FAILED:
            if self.output is not None or self.error_code not in {
                "skill_source_unavailable",
                "skill_execution_failed",
                "invalid_skill_output",
                "missing_skill_output",
                "unexpected_skill_output",
                "tool_execution_failed",
            }:
                raise ValueError("failed Skill execution requires a safe error code only.")
        else:
            raise ValueError("status must be a SkillExecutionStatus value.")

    @property
    def success(self) -> bool:
        """Whether valid output was returned without any failed tool attempt."""
        return self.status is SkillExecutionStatus.SUCCEEDED


SkillImplementation = Callable[[SkillExecutionContext], Mapping[str, object]]


class SkillExecutionAdapter(ABC):
    """Explicit in-process boundary for executing one or more Skills."""

    @abstractmethod
    def supports(self, skill: SkillContract) -> bool:
        """Whether this adapter has an explicit implementation for the Skill."""

    @abstractmethod
    def execute(self, context: SkillExecutionContext) -> Mapping[str, object]:
        """Execute the supplied context and return a structured output mapping."""


class LocalSkillExecutionAdapter(SkillExecutionAdapter):
    """Trusted local adapter backed by explicitly supplied Skill callables."""

    def __init__(self, implementations: Mapping[str, SkillImplementation]) -> None:
        if not isinstance(implementations, Mapping) or not implementations:
            raise InvocationValidationError(
                "implementations must be a non-empty Skill-to-callable mapping."
            )
        copied = dict(implementations)
        if any(
            not isinstance(identifier, str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier)
            or not callable(implementation)
            for identifier, implementation in copied.items()
        ):
            raise InvocationValidationError(
                "implementations must map valid Skill identifiers to callables."
            )
        self._implementations = MappingProxyType(copied)

    def supports(self, skill: SkillContract) -> bool:
        return (
            isinstance(skill, SkillContract)
            and skill.identifier in self._implementations
        )

    def execute(self, context: SkillExecutionContext) -> Mapping[str, object]:
        if not isinstance(context, SkillExecutionContext):
            raise InvocationValidationError(
                "context must be a SkillExecutionContext."
            )
        if not self.supports(context.skill):
            raise ExecutionUnavailableError(
                f"no local implementation is registered for Skill '{context.skill.identifier}'."
            )
        return self._implementations[context.skill.identifier](context)


class SkillPipeline:
    """Repository-local facade over discovery, selection, and explicit execution."""

    def __init__(
        self,
        repository_root: Path,
        *,
        execution_adapter: SkillExecutionAdapter | None = None,
        tool_executor: ToolExecutor | None = None,
    ) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.registry = SkillRegistry(self.repository_root)
        if execution_adapter is not None and not isinstance(
            execution_adapter, SkillExecutionAdapter
        ):
            raise InvocationValidationError(
                "execution_adapter must implement SkillExecutionAdapter or be None."
            )
        self._execution_adapter = execution_adapter
        if tool_executor is not None and not isinstance(tool_executor, ToolExecutor):
            raise InvocationValidationError("tool_executor must be a ToolExecutor or None.")
        self._tool_executor = tool_executor

    def discover(self) -> PipelineDiscoveryResult:
        """Discover Skills, register valid unique definitions, and report issues."""
        result = discover_skills(self.repository_root)
        issues = list(result.issues)
        registered: list[str] = []
        for contract in result.skills:
            try:
                self.registry.register(contract)
            except (DuplicateSkillError, SkillMetadataError) as error:
                issues.append(
                    DiscoveryIssue(contract.source_path, f"registration failed: {error}")
                )
            else:
                registered.append(contract.identifier)
        return PipelineDiscoveryResult(
            discovered=result.skills,
            registered_identifiers=tuple(registered),
            issues=tuple(sorted(issues, key=lambda issue: (str(issue.source_path), issue.message))),
        )

    def search(self, query: str) -> tuple[SkillContract, ...]:
        """Find Skills containing ``query`` in identifier, name, description, or tags."""
        if not isinstance(query, str) or not query.strip():
            raise SelectionError("search query must be a non-empty string.")
        needle = query.casefold()
        return tuple(
            skill
            for skill in self.registry.list_skills()
            if needle in skill.identifier.casefold()
            or needle in skill.name.casefold()
            or needle in skill.description.casefold()
            or any(needle in tag.casefold() for tag in skill.tags)
        )

    def select(
        self,
        task: str,
        *,
        skill_identifier: str | None = None,
        allowed_identifiers: tuple[str, ...] | None = None,
    ) -> SelectionResult:
        """Select only an explicit identifier or a unique lexical-overlap winner.

        Automatic scores count distinct task tokens present in each Skill's
        identifier, name, description, or tags. Tokens are lowercase ASCII
        alphanumeric sequences. Zero-overlap Skills are not candidates; equal
        top scores return AMBIGUOUS, with candidates ordered by identifier.
        """
        if not isinstance(task, str) or not task.strip():
            raise SelectionError("task description must be a non-empty string.")
        allowed: set[str] | None = None
        if allowed_identifiers is not None:
            if not isinstance(allowed_identifiers, tuple) or any(
                not isinstance(identifier, str) or not identifier
                for identifier in allowed_identifiers
            ):
                raise SelectionError("allowed_identifiers must be a tuple of non-empty strings.")
            allowed = set(allowed_identifiers)
            unknown = sorted(allowed.difference(
                skill.identifier for skill in self.registry.list_skills()
            ))
            if unknown:
                raise SkillNotFoundError(
                    f"unknown allowed Skill identifier(s): {', '.join(unknown)}"
                )

        if skill_identifier is not None:
            skill = self.registry.get(skill_identifier)
            if allowed is not None and skill.identifier not in allowed:
                raise SelectionError(
                    f"explicit Skill '{skill_identifier}' is excluded by allowed_identifiers."
                )
            candidate = SelectionCandidate(
                skill=skill,
                score=0,
                matched_terms=(),
                reasons=(f"explicitly requested identifier '{skill_identifier}'",),
            )
            return SelectionResult(
                SelectionStatus.SELECTED,
                (candidate,),
                selected=skill,
                message="Selected by explicit identifier; task matching was not used.",
            )

        task_terms = set(_WORD_PATTERN.findall(task.casefold()))
        if not task_terms:
            raise SelectionError("task description must contain at least one searchable term.")

        candidates = [
            candidate
            for skill in self.registry.list_skills()
            if allowed is None or skill.identifier in allowed
            if (candidate := _score_skill(skill, task_terms)) is not None
        ]
        candidates.sort(key=lambda candidate: (-candidate.score, candidate.skill.identifier))
        if not candidates:
            return SelectionResult(
                SelectionStatus.NO_MATCH,
                (),
                message="No Skill metadata contains any task terms.",
            )

        highest_score = candidates[0].score
        leaders = [candidate for candidate in candidates if candidate.score == highest_score]
        if len(leaders) > 1:
            return SelectionResult(
                SelectionStatus.AMBIGUOUS,
                tuple(candidates),
                message=(
                    f"{len(leaders)} Skills share the highest lexical score "
                    f"({highest_score}); specify a Skill identifier."
                ),
            )
        return SelectionResult(
            SelectionStatus.SELECTED,
            tuple(candidates),
            selected=leaders[0].skill,
            message=(
                "Selected by unique lexical-overlap score; this is not semantic "
                "understanding or an execution decision."
            ),
        )

    def prepare_invocation(self, request: InvocationRequest) -> InvocationPlan:
        """Validate request and return a plan without executing the Skill."""
        if not isinstance(request, InvocationRequest):
            raise InvocationValidationError("request must be an InvocationRequest.")
        try:
            skill = self.registry.resolve(
                request.skill_identifier, request.contract_version
            )
        except SkillContractVersionError as error:
            raise InvocationValidationError(
                "requested Skill contract version is unavailable."
            ) from error
        source = skill.resolve_source(self.repository_root)
        try:
            skill.validate_inputs(request.inputs)
        except SkillMetadataError as error:
            raise InvocationValidationError(
                "Skill invocation inputs do not satisfy the registered contract."
            ) from error
        return InvocationPlan(
            request_id=request.request_id,
            skill=skill,
            source_path=source,
            task=request.task,
            inputs=request.inputs,
            execution_available=(
                self._execution_adapter is not None
                and self._execution_adapter.supports(skill)
            ),
            contract_version=skill.contract_version,
        )

    def invoke(self, request: InvocationRequest) -> SkillExecutionResult:
        """Prepare and execute one Skill request through this configured pipeline.

        Request and contract validation errors are raised before execution.
        Once preparation succeeds, execution-time failure or unavailability is
        returned as a :class:`SkillExecutionResult`.
        """
        plan = self.prepare_invocation(request)
        return self.execute(plan)

    def execute(self, plan: InvocationPlan) -> SkillExecutionResult:
        """Execute a validated plan through the explicitly configured adapter.

        Without an adapter supporting the selected Skill, execution remains
        unavailable. Adapter exceptions and invalid results are normalized to
        safe error codes; exception messages are not copied into the result.
        """
        if not isinstance(plan, InvocationPlan):
            raise ExecutionUnavailableError("execution requires a prepared InvocationPlan.")
        if plan.status != "PREPARED_NOT_EXECUTED" or not isinstance(
            plan.skill, SkillContract
        ):
            raise InvocationValidationError("plan is not a prepared Skill invocation.")

        contract_version = (
            plan.skill.contract_version
            if plan.contract_version is None
            else plan.contract_version
        )
        request = InvocationRequest(
            skill_identifier=plan.skill.identifier,
            task=plan.task,
            inputs=plan.inputs,
            request_id=plan.request_id,
            contract_version=contract_version,
        )
        started_at = datetime.now(timezone.utc)
        try:
            validated_plan = self.prepare_invocation(request)
        except SkillMetadataError:
            return _execution_failure(
                request.request_id,
                plan.skill.identifier,
                started_at,
                "skill_source_unavailable",
                contract_version=contract_version,
            )
        if (
            plan.skill != validated_plan.skill
            or plan.source_path != validated_plan.source_path
            or contract_version != validated_plan.skill.contract_version
        ):
            raise InvocationValidationError(
                "plan does not match the registered Skill source."
            )
        adapter = self._execution_adapter
        if adapter is None or not adapter.supports(validated_plan.skill):
            return _execution_failure(
                request.request_id,
                validated_plan.skill.identifier,
                started_at,
                "execution_unavailable",
                status=SkillExecutionStatus.UNAVAILABLE,
                contract_version=validated_plan.skill.contract_version,
            )

        try:
            source_text = validated_plan.source_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return _execution_failure(
                request.request_id,
                validated_plan.skill.identifier,
                started_at,
                "skill_source_unavailable",
                contract_version=validated_plan.skill.contract_version,
            )

        tool_invocations: list[SkillToolInvocation] = []
        allowed_tools = frozenset(validated_plan.skill.tools)
        context = SkillExecutionContext(
            request_id=request.request_id,
            skill=validated_plan.skill,
            task=validated_plan.task,
            source_text=source_text,
            inputs=validated_plan.inputs,
            _tool_invoker=lambda tool_identifier, inputs: self._invoke_declared_tool(
                request.request_id,
                tool_identifier,
                inputs,
                allowed_tools,
                tool_invocations,
            ),
        )
        try:
            raw_output = adapter.execute(context)
        except ExecutionUnavailableError:
            tool_failure_code = _tool_failure_code(tool_invocations)
            if tool_failure_code == "tool_execution_failed":
                return _execution_failure(
                    request.request_id,
                    validated_plan.skill.identifier,
                    started_at,
                    tool_failure_code,
                    tool_invocations=tuple(tool_invocations),
                    contract_version=validated_plan.skill.contract_version,
                )
            return _execution_failure(
                request.request_id,
                validated_plan.skill.identifier,
                started_at,
                "execution_unavailable",
                status=SkillExecutionStatus.UNAVAILABLE,
                tool_invocations=tuple(tool_invocations),
                contract_version=validated_plan.skill.contract_version,
            )
        except Exception:
            return _execution_failure(
                request.request_id,
                validated_plan.skill.identifier,
                started_at,
                _tool_failure_code(tool_invocations) or "skill_execution_failed",
                tool_invocations=tuple(tool_invocations),
                contract_version=validated_plan.skill.contract_version,
            )

        failed_tool_code = _tool_failure_code(tool_invocations)
        if failed_tool_code is not None:
            return _execution_failure(
                request.request_id,
                validated_plan.skill.identifier,
                started_at,
                failed_tool_code,
                status=(
                    SkillExecutionStatus.UNAVAILABLE
                    if failed_tool_code == "execution_unavailable"
                    else SkillExecutionStatus.FAILED
                ),
                tool_invocations=tuple(tool_invocations),
                contract_version=validated_plan.skill.contract_version,
            )
        if not isinstance(raw_output, Mapping):
            return _execution_failure(
                request.request_id,
                validated_plan.skill.identifier,
                started_at,
                "invalid_skill_output",
                tool_invocations=tuple(tool_invocations),
                contract_version=validated_plan.skill.contract_version,
            )
        try:
            output = dict(raw_output)
        except Exception:
            return _execution_failure(
                request.request_id,
                validated_plan.skill.identifier,
                started_at,
                "invalid_skill_output",
                tool_invocations=tuple(tool_invocations),
                contract_version=validated_plan.skill.contract_version,
            )
        if any(not isinstance(name, str) or not name.strip() for name in output):
            return _execution_failure(
                request.request_id,
                validated_plan.skill.identifier,
                started_at,
                "invalid_skill_output",
                tool_invocations=tuple(tool_invocations),
                contract_version=validated_plan.skill.contract_version,
            )
        output_error = validated_plan.skill.validate_outputs(output)
        if output_error is not None:
            return _execution_failure(
                request.request_id,
                validated_plan.skill.identifier,
                started_at,
                output_error,
                tool_invocations=tuple(tool_invocations),
                contract_version=validated_plan.skill.contract_version,
            )
        return SkillExecutionResult(
            request_id=request.request_id,
            skill_identifier=validated_plan.skill.identifier,
            status=SkillExecutionStatus.SUCCEEDED,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            output=output,
            tool_invocations=tuple(tool_invocations),
            contract_version=validated_plan.skill.contract_version,
        )

    def _invoke_declared_tool(
        self,
        skill_request_id: str,
        tool_identifier: str,
        inputs: Mapping[str, object],
        allowed_tools: frozenset[str],
        invocations: list[SkillToolInvocation],
    ) -> ToolExecutionResult:
        request_id = str(uuid.uuid4())
        if not isinstance(tool_identifier, str) or not tool_identifier.strip():
            invocations.append(
                SkillToolInvocation(
                    skill_request_id=skill_request_id,
                    request_id=request_id,
                    tool_identifier="<invalid>",
                    status=None,
                    error_code="invalid_tool_request",
                )
            )
            raise InvocationValidationError("tool_identifier must be a non-empty string.")
        if not isinstance(inputs, Mapping):
            invocations.append(
                SkillToolInvocation(
                    skill_request_id=skill_request_id,
                    request_id=request_id,
                    tool_identifier=tool_identifier,
                    status=None,
                    error_code="invalid_tool_request",
                )
            )
            raise InvocationValidationError("tool inputs must be a mapping.")
        try:
            request = ToolInvocationRequest(
                tool_identifier, inputs, request_id=request_id
            )
        except Exception:
            invocations.append(
                SkillToolInvocation(
                    skill_request_id=skill_request_id,
                    request_id=request_id,
                    tool_identifier=tool_identifier,
                    status=None,
                    error_code="invalid_tool_request",
                )
            )
            raise

        if tool_identifier not in allowed_tools:
            invocations.append(
                SkillToolInvocation(
                    skill_request_id=skill_request_id,
                    request_id=request_id,
                    tool_identifier=tool_identifier,
                    status=None,
                    error_code="tool_not_allowed",
                )
            )
            raise InvocationValidationError(
                "requested tool is not declared by the registered Skill."
            )

        executor = self._tool_executor
        if executor is None:
            invocations.append(
                SkillToolInvocation(
                    skill_request_id=skill_request_id,
                    request_id=request_id,
                    tool_identifier=tool_identifier,
                    status=None,
                    error_code="execution_unavailable",
                )
            )
            raise ExecutionUnavailableError(
                "no ToolExecutor is configured for this Skill invocation."
            )
        try:
            result = executor.invoke(request)
        except Exception:
            invocations.append(
                SkillToolInvocation(
                    skill_request_id=skill_request_id,
                    request_id=request_id,
                    tool_identifier=tool_identifier,
                    status=ToolStatus.FAILED,
                    error_code="tool_invocation_failed",
                )
            )
            raise
        invocations.append(
            SkillToolInvocation(
                skill_request_id=skill_request_id,
                request_id=result.request_id,
                tool_identifier=result.tool_identifier,
                status=result.status,
                error_code=_safe_tool_error_code(
                    result.error_code, result.status
                ),
            )
        )
        return result


def _execution_failure(
    request_id: str,
    skill_identifier: str,
    started_at: datetime,
    error_code: str,
    *,
    status: SkillExecutionStatus = SkillExecutionStatus.FAILED,
    tool_invocations: tuple[SkillToolInvocation, ...] = (),
    contract_version: str = DEFAULT_CONTRACT_VERSION,
) -> SkillExecutionResult:
    return SkillExecutionResult(
        request_id=request_id,
        skill_identifier=skill_identifier,
        status=status,
        started_at=started_at,
        completed_at=datetime.now(timezone.utc),
        error_code=error_code,
        tool_invocations=tool_invocations,
        contract_version=contract_version,
    )


def _tool_failure_code(
    invocations: list[SkillToolInvocation],
) -> str | None:
    if any(
        invocation.error_code == "execution_unavailable"
        or invocation.status
        in {
            ToolStatus.DISABLED,
            ToolStatus.UNAVAILABLE,
            ToolStatus.ADAPTER_MISSING,
            ToolStatus.ADAPTER_INCOMPATIBLE,
        }
        for invocation in invocations
    ):
        return "execution_unavailable"
    if any(
        invocation.status is not ToolStatus.SUCCEEDED
        for invocation in invocations
    ):
        return "tool_execution_failed"
    return None


def _safe_tool_error_code(
    error_code: str | None, status: ToolStatus
) -> str | None:
    safe_codes = {
        "tool_disabled",
        "execution_unavailable",
        "invalid_input",
        "adapter_missing",
        "adapter_incompatible",
        "runtime_failure",
    }
    if error_code is None:
        return None if status is ToolStatus.SUCCEEDED else "tool_failed"
    if isinstance(error_code, str) and error_code in safe_codes:
        return error_code
    return "tool_failed"


def _score_skill(
    skill: SkillContract, task_terms: set[str]
) -> SelectionCandidate | None:
    searchable_fields = (
        ("identifier", skill.identifier),
        ("name", skill.name),
        ("description", skill.description),
        ("tags", " ".join(skill.tags)),
    )
    matched_terms = tuple(
        sorted(
            term
            for term in task_terms
            if any(term in set(_WORD_PATTERN.findall(value.casefold())) for _, value in searchable_fields)
        )
    )
    if not matched_terms:
        return None
    reasons = tuple(
        f"task term '{term}' matched "
        + ", ".join(
            field_name
            for field_name, value in searchable_fields
            if term in set(_WORD_PATTERN.findall(value.casefold()))
        )
        for term in matched_terms
    )
    return SelectionCandidate(skill, len(matched_terms), matched_terms, reasons)

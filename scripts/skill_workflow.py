"""Explicit integration of configured Skill invocations with Tool workflows."""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from scripts.skill_pipeline import (
    InvocationRequest,
    InvocationValidationError,
    PipelineDiscoveryResult,
    SelectionError,
    SelectionResult,
    SelectionStatus,
    SkillExecutionResult,
    SkillPipeline,
)
from scripts.skill_registry import (
    SkillContract,
    SkillContractVersionError,
    SkillMetadataError,
    is_valid_contract_version,
)
from scripts.tool_framework import (
    DuplicateToolError,
    ToolAdapter,
    ToolContract,
    ToolExecutor,
    ToolRuntimeError,
)
from scripts.tool_workflow import (
    DuplicateWorkflowError,
    WorkflowDefinition,
    WorkflowFailurePolicy,
    WorkflowInputRef,
    WorkflowRegistry,
    WorkflowStep,
)


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")


class SkillWorkflowAdapter(ToolAdapter):
    """Adapt one explicitly selected Skill invocation to a registered Tool.

    The returned mapping preserves the Skill outcome as data. A successful Tool
    invocation means the integration completed its Tool protocol; callers must
    inspect ``skill_status`` to determine the embedded Skill outcome.
    """

    def __init__(
        self,
        adapter_id: str,
        tool_identifier: str,
        pipeline: SkillPipeline,
        skill_identifier: str,
        *,
        task: str | None = None,
        task_input: str | None = None,
        input_mapping: Mapping[str, str] | None = None,
        contract_version: str | None = None,
    ) -> None:
        if not isinstance(adapter_id, str) or not _IDENTIFIER_PATTERN.fullmatch(
            adapter_id
        ):
            raise ValueError("adapter_id must be a valid identifier.")
        if not isinstance(tool_identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
            tool_identifier
        ):
            raise ValueError("tool_identifier must be a valid identifier.")
        if not isinstance(pipeline, SkillPipeline):
            raise ValueError("pipeline must be a SkillPipeline.")
        if contract_version is not None and not is_valid_contract_version(
            contract_version
        ):
            raise ValueError(
                "contract_version must use canonical major.minor.patch format."
            )
        try:
            skill = pipeline.registry.resolve(skill_identifier, contract_version)
        except SkillContractVersionError as error:
            raise ValueError(
                "contract_version does not match the registered Skill contract."
            ) from error
        if (task is None) == (task_input is None):
            raise ValueError("provide exactly one of task or task_input.")
        if task is not None and (not isinstance(task, str) or not task.strip()):
            raise ValueError("task must be a non-empty string when supplied.")
        if task_input is not None and (
            not isinstance(task_input, str)
            or not _IDENTIFIER_PATTERN.fullmatch(task_input)
        ):
            raise ValueError("task_input must be a valid input identifier.")
        copied_mapping = _copy_input_mapping(input_mapping)
        declared_skill_inputs = set(skill.inputs).union(
            field.name for field in skill.input_fields
        )
        if declared_skill_inputs and not set(copied_mapping).issubset(
            declared_skill_inputs
        ):
            raise ValueError("input_mapping contains inputs not declared by the Skill.")
        required_typed_inputs = {
            field.name for field in skill.input_fields if field.required
        }
        if not required_typed_inputs.issubset(copied_mapping):
            raise ValueError("input_mapping omits a required Skill input field.")
        manifest_discovery = pipeline.discover_with_manifest_metadata()
        manifest_contract = next(
            (
                resolution.manifest_entry.manifest.contract
                for resolution in manifest_discovery.resolutions
                if resolution.skill.identifier == skill.identifier
                and resolution.manifest_entry is not None
            ),
            None,
        )
        if manifest_contract is not None:
            declared_manifest_inputs = set(manifest_contract.inputs).union(
                field.name for field in manifest_contract.input_fields
            )
            if declared_manifest_inputs and not set(copied_mapping).issubset(
                declared_manifest_inputs
            ):
                raise ValueError(
                    "input_mapping contains inputs not declared by the Skill manifest."
                )
            required_manifest_inputs = {
                field.name
                for field in manifest_contract.input_fields
                if field.required
            }
            if not required_manifest_inputs.issubset(copied_mapping):
                raise ValueError(
                    "input_mapping omits a required Skill manifest input field."
                )
        self._adapter_id = adapter_id
        self._tool_identifier = tool_identifier
        self._pipeline = pipeline
        self._skill_identifier = skill.identifier
        self._manifest_contract: SkillContract | None = manifest_contract
        self._task = task
        self._task_input = task_input
        self._input_mapping = MappingProxyType(copied_mapping)
        self._contract_version = contract_version

    @property
    def adapter_id(self) -> str:
        return self._adapter_id

    @property
    def supported_tool_identifiers(self) -> tuple[str, ...]:
        return (self._tool_identifier,)

    @property
    def skill_identifier(self) -> str:
        return self._skill_identifier

    def supports(self, contract: ToolContract) -> bool:
        if (
            not isinstance(contract, ToolContract)
            or contract.adapter_id != self.adapter_id
            or contract.identifier != self._tool_identifier
        ):
            return False
        declared_inputs = {field.name for field in contract.input_schema}
        configured_inputs = set(self._input_mapping.values())
        if self._task_input is not None:
            configured_inputs.add(self._task_input)
        return configured_inputs == declared_inputs

    def execute(
        self, contract: ToolContract, inputs: Mapping[str, object]
    ) -> Mapping[str, object]:
        if not self.supports(contract):
            raise ToolRuntimeError("Skill workflow adapter does not support this Tool contract.")
        if not isinstance(inputs, Mapping):
            raise ToolRuntimeError("Skill workflow Tool inputs are invalid.")
        required_inputs = set(self._input_mapping.values())
        if self._task_input is not None:
            required_inputs.add(self._task_input)
        if not required_inputs.issubset(inputs):
            raise ToolRuntimeError("Skill workflow Tool inputs are incomplete.")
        if self._task is not None:
            task = self._task
        elif self._task_input is not None:
            task = inputs[self._task_input]
        else:
            raise ToolRuntimeError("Skill workflow task input is not configured.")
        if not isinstance(task, str) or not task.strip():
            raise ToolRuntimeError("Skill workflow task input is invalid.")
        skill_inputs = {
            skill_name: inputs[tool_name]
            for skill_name, tool_name in self._input_mapping.items()
        }
        if self._manifest_contract is not None:
            try:
                self._manifest_contract.validate_inputs(skill_inputs)
            except SkillMetadataError as error:
                raise ToolRuntimeError(
                    "Skill inputs do not satisfy the resolved manifest contract."
                ) from error
        try:
            result = self._pipeline.invoke(
                InvocationRequest(
                    skill_identifier=self._skill_identifier,
                    task=task,
                    inputs=skill_inputs,
                    contract_version=self._contract_version,
                )
            )
        except InvocationValidationError as error:
            raise ToolRuntimeError(
                "Skill invocation was rejected before execution."
            ) from error
        return _skill_result_output(result)


@dataclass(frozen=True, slots=True)
class SkillWorkflowPreparationResult:
    """Discovery and selection outcome with an adapter only for a unique match."""

    discovery: PipelineDiscoveryResult
    selection: SelectionResult
    adapter: SkillWorkflowAdapter | None


@dataclass(frozen=True, slots=True)
class SkillWorkflowRegistrationResult:
    """Preparation outcome and registered workflow, when selection succeeded."""

    preparation: SkillWorkflowPreparationResult
    workflow: WorkflowDefinition | None


def prepare_skill_workflow(
    adapter_id: str,
    tool_identifier: str,
    pipeline: SkillPipeline,
    task: str,
    *,
    skill_identifier: str | None = None,
    task_input: str | None = None,
    input_mapping: Mapping[str, str] | None = None,
    contract_version: str | None = None,
) -> SkillWorkflowPreparationResult:
    """Discover, select, and prepare one Skill adapter without executing it.

    ``task`` is used for Skill selection and, unless ``task_input`` is supplied,
    as the adapter's fixed invocation task. Selection uses the pipeline's
    existing explicit-ID or unique lexical-overlap behavior.
    """
    if not isinstance(adapter_id, str) or not _IDENTIFIER_PATTERN.fullmatch(
        adapter_id
    ):
        raise ValueError("adapter_id must be a valid identifier.")
    if not isinstance(tool_identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
        tool_identifier
    ):
        raise ValueError("tool_identifier must be a valid identifier.")
    if not isinstance(pipeline, SkillPipeline):
        raise ValueError("pipeline must be a SkillPipeline.")
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task description must be a non-empty string.")
    if contract_version is not None and not is_valid_contract_version(
        contract_version
    ):
        raise ValueError(
            "contract_version must use canonical major.minor.patch format."
        )
    if task_input is not None and (
        not isinstance(task_input, str)
        or not _IDENTIFIER_PATTERN.fullmatch(task_input)
    ):
        raise ValueError("task_input must be a valid input identifier.")
    copied_mapping = _copy_input_mapping(input_mapping)

    discovery = pipeline.discover()
    discovered = {skill.identifier: skill for skill in discovery.discovered}
    registered = {
        skill.identifier: skill for skill in pipeline.registry.list_skills()
    }
    eligible_identifiers = tuple(
        identifier
        for identifier in sorted(discovered)
        if registered.get(identifier) == discovered[identifier]
    )
    selection = pipeline.select(
        task,
        skill_identifier=skill_identifier,
        allowed_identifiers=eligible_identifiers,
    )
    if selection.status is not SelectionStatus.SELECTED:
        return SkillWorkflowPreparationResult(discovery, selection, None)
    if selection.selected is None:
        raise SelectionError("selected Skill result is missing canonical metadata.")

    adapter = SkillWorkflowAdapter(
        adapter_id,
        tool_identifier,
        pipeline,
        selection.selected.identifier,
        task=None if task_input is not None else task,
        task_input=task_input,
        input_mapping=copied_mapping,
        contract_version=contract_version,
    )
    return SkillWorkflowPreparationResult(discovery, selection, adapter)


def register_prepared_skill_workflow(
    preparation: SkillWorkflowPreparationResult,
    tool_contract: ToolContract,
    workflow_registry: WorkflowRegistry,
    executor: ToolExecutor,
    workflow_identifier: str,
    workflow_name: str,
    *,
    workflow_description: str = "",
    failure_policy: WorkflowFailurePolicy = WorkflowFailurePolicy.STOP_ON_FAILURE,
) -> SkillWorkflowRegistrationResult:
    """Register a prepared Skill adapter and a one-step Tool workflow.

    The Tool contract is supplied explicitly; this function does not infer a
    Tool schema from Skill or manifest metadata. Workflow inputs map directly
    from caller fields with the same names as the Tool contract fields.
    """
    if not isinstance(preparation, SkillWorkflowPreparationResult):
        raise ValueError("preparation must be a SkillWorkflowPreparationResult.")
    if not isinstance(tool_contract, ToolContract):
        raise ValueError("tool_contract must be a ToolContract.")
    if not isinstance(workflow_registry, WorkflowRegistry):
        raise ValueError("workflow_registry must be a WorkflowRegistry.")
    if not isinstance(executor, ToolExecutor):
        raise ValueError("executor must be a ToolExecutor.")
    if preparation.adapter is None:
        if preparation.selection.status is SelectionStatus.SELECTED:
            raise SelectionError(
                "selected Skill preparation is missing its workflow adapter."
            )
        return SkillWorkflowRegistrationResult(preparation, None)
    if (
        preparation.selection.status is not SelectionStatus.SELECTED
        or preparation.selection.selected is None
    ):
        raise SelectionError(
            "workflow adapter cannot be registered without a selected Skill."
        )

    adapter = preparation.adapter
    if adapter.skill_identifier != preparation.selection.selected.identifier:
        raise SelectionError(
            "prepared adapter does not match the selected canonical Skill."
        )
    if not adapter.supports(tool_contract):
        raise ValueError(
            "tool_contract is incompatible with the prepared Skill workflow adapter."
        )

    registered_tool_ids = {
        contract.identifier for contract in executor.registry.list_tools()
    }
    if tool_contract.identifier in registered_tool_ids:
        raise DuplicateToolError(
            f"tool is already registered: {tool_contract.identifier}"
        )
    if any(
        workflow.identifier == workflow_identifier
        for workflow in workflow_registry.list_workflows()
    ):
        raise DuplicateWorkflowError(
            f"workflow is already registered: {workflow_identifier}"
        )

    workflow = WorkflowDefinition(
        workflow_identifier,
        workflow_name,
        (
            WorkflowStep(
                "invoke-skill",
                tool_contract.identifier,
                {
                    field.name: WorkflowInputRef(field.name)
                    for field in tool_contract.input_schema
                },
            ),
        ),
        description=workflow_description,
        failure_policy=failure_policy,
    )

    executor.register_adapter(adapter)
    executor.registry.register(tool_contract)
    workflow_registry.register(workflow)
    return SkillWorkflowRegistrationResult(preparation, workflow)


def _copy_input_mapping(
    input_mapping: Mapping[str, str] | None,
) -> dict[str, str]:
    if input_mapping is None:
        return {}
    if not isinstance(input_mapping, Mapping):
        raise ValueError("input_mapping must be a mapping.")
    copied_mapping = dict(input_mapping)
    if any(
        not isinstance(skill_input, str)
        or not _IDENTIFIER_PATTERN.fullmatch(skill_input)
        or not isinstance(tool_input, str)
        or not _IDENTIFIER_PATTERN.fullmatch(tool_input)
        for skill_input, tool_input in copied_mapping.items()
    ):
        raise ValueError("input_mapping must map valid Skill input names to Tool input names.")
    return copied_mapping


def _skill_result_output(result: SkillExecutionResult) -> Mapping[str, object]:
    return {
        "skill_status": result.status.value,
        "skill_request_id": result.request_id,
        "skill_identifier": result.skill_identifier,
        "skill_contract_version": result.contract_version,
        "skill_error_code": result.error_code,
        "skill_output": None if result.output is None else dict(result.output),
        "tool_invocations": [
            {
                "skill_request_id": invocation.skill_request_id,
                "request_id": invocation.request_id,
                "tool_identifier": invocation.tool_identifier,
                "status": (
                    None if invocation.status is None else invocation.status.value
                ),
                "error_code": invocation.error_code,
            }
            for invocation in result.tool_invocations
        ],
    }

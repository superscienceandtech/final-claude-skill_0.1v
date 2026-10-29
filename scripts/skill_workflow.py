"""Explicit integration of configured Skill invocations with Tool workflows."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import Mapping

from scripts.skill_pipeline import (
    InvocationRequest,
    InvocationValidationError,
    SkillExecutionResult,
    SkillExecutionStatus,
    SkillPipeline,
)
from scripts.skill_registry import (
    SkillContractVersionError,
    is_valid_contract_version,
)
from scripts.tool_framework import (
    ToolAdapter,
    ToolContract,
    ToolRuntimeError,
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
        if input_mapping is None:
            input_mapping = {}
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
        self._adapter_id = adapter_id
        self._tool_identifier = tool_identifier
        self._pipeline = pipeline
        self._skill_identifier = skill.identifier
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
        if result.status is not SkillExecutionStatus.SUCCEEDED:
            skill_error_code = result.error_code or result.status.value
            if not skill_error_code.startswith("skill_"):
                skill_error_code = f"skill_{skill_error_code}"
            raise ToolRuntimeError(
                "configured Skill execution did not succeed.",
                error_code=skill_error_code,
            )
        return _skill_result_output(result)


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

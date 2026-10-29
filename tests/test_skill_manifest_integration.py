from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Mapping
from unittest.mock import patch

from scripts.skill_manifest import (
    SkillManifestCatalogError,
    SkillManifestError,
    discover_skill_manifests,
    load_skill_manifest,
    load_skill_manifest_catalog,
    register_skill_manifest_catalog,
)
from scripts.skill_pipeline import (
    InvocationRequest,
    InvocationValidationError,
    LocalSkillExecutionAdapter,
    SkillExecutionContext,
    SkillExecutionStatus,
    SkillPipeline,
)
from scripts.skill_registry import (
    SkillContractVersionError,
    SkillNotFoundError,
    discover_skills,
)
from scripts.skill_workflow import SkillWorkflowAdapter
from scripts.tool_framework import (
    ExecutionAvailability,
    InputField,
    InputType,
    ToolContract,
    ToolExecutor,
    ToolRegistry,
    ToolStatus,
    register_text_statistics,
)
from scripts.tool_workflow import (
    StepStatus,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowInputRef,
    WorkflowRegistry,
    WorkflowStatus,
    WorkflowStep,
)


def _analyze_using_statistics_tool(
    context: SkillExecutionContext,
) -> Mapping[str, object]:
    result = context.invoke_tool(
        "local.text-statistics",
        {"text": context.inputs["text"]},
    )
    if result.output is None:
        raise RuntimeError("statistics Tool returned no output")
    return {"statistics": dict(result.output)}


def _manifest(
    identifier: str = "text-analysis",
    *,
    contract_version: str = "1.2.0",
    source_path: str = "skills/instructions.md",
) -> dict[str, object]:
    return {
        "manifest_version": 1,
        "identifier": identifier,
        "name": f"{identifier} display",
        "description": "Analyze supplied text.",
        "source_path": source_path,
        "version": "0.1",
        "contract_version": contract_version,
        "category": "text-processing",
        "tags": ["text", "analysis"],
        "input_fields": [
            {"name": "text", "value_type": "string", "required": True}
        ],
        "output_fields": [
            {"name": "statistics", "value_type": "object", "required": True}
        ],
        "strict_inputs": True,
        "strict_outputs": True,
        "tools": ["local.text-statistics"],
        "capabilities": ["descriptive-only"],
    }


class SkillManifestIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        skills = self.root / "skills"
        skills.mkdir()
        (skills / "instructions.md").write_text(
            "# Declarative instructions\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_committed_manifest_example_references_existing_skill_and_tool(
        self,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        catalog = load_skill_manifest_catalog(repository_root)

        self.assertEqual(len(catalog.entries), 1)
        contract = catalog.entries[0].manifest.contract
        self.assertEqual(contract.identifier, "text-analysis")
        self.assertEqual(
            contract.description,
            "Count characters, words, and lines for supplied text.",
        )
        self.assertEqual(
            contract.source_path,
            Path("skills/implementation/SKILL.md"),
        )
        source = (repository_root / contract.source_path).read_text(encoding="utf-8")
        self.assertIn("name: implementation", source)
        self.assertEqual(contract.tools, ("local.text-statistics",))
        tool_source = (repository_root / "scripts/tool_framework.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('identifier="local.text-statistics"', tool_source)
        self.assertIn("def text_statistics(", tool_source)

    def test_native_discovery_and_manifest_loading_are_separate(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        native_skills = discover_skills(repository_root)
        manifest_catalog = load_skill_manifest_catalog(repository_root)
        pipeline = SkillPipeline(repository_root)
        pipeline_discovery = pipeline.discover()

        self.assertEqual(
            tuple(skill.identifier for skill in native_skills.skills),
            ("implementation", "repository-audit"),
        )
        self.assertEqual(
            tuple(entry.manifest.contract.identifier for entry in manifest_catalog.entries),
            ("text-analysis",),
        )
        self.assertEqual(
            pipeline_discovery.registered_identifiers,
            ("implementation", "repository-audit"),
        )
        with self.assertRaises(SkillNotFoundError):
            pipeline.registry.get("text-analysis")

    def _write_manifest(
        self,
        relative_path: str,
        declaration: dict[str, object] | None = None,
    ) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        content = _manifest() if declaration is None else declaration
        path.write_text(json.dumps(content), encoding="utf-8")
        return path

    def test_manifest_catalog_is_deterministic_and_preserves_contract(self) -> None:
        self._write_manifest(
            "catalog/zeta.manifest.json", _manifest("zeta")
        )
        self._write_manifest(
            "catalog/nested/alpha.manifest.json", _manifest("alpha")
        )
        irrelevant = self.root / "catalog" / "not-a-skill.json"
        irrelevant.write_text("{}", encoding="utf-8")
        ignored = self.root / ".venv" / "hidden.manifest.json"
        ignored.parent.mkdir()
        ignored.write_text("{}", encoding="utf-8")

        discovered = discover_skill_manifests(self.root)
        self.assertEqual(
            tuple(path.relative_to(self.root).as_posix() for path in discovered),
            (
                "catalog/nested/alpha.manifest.json",
                "catalog/zeta.manifest.json",
            ),
        )
        catalog = load_skill_manifest_catalog(self.root)
        self.assertEqual(
            tuple(entry.manifest.contract.identifier for entry in catalog.entries),
            ("alpha", "zeta"),
        )

        contract = catalog.entries[0].manifest.contract
        self.assertEqual(contract.version, "0.1")
        self.assertEqual(contract.contract_version, "1.2.0")
        self.assertEqual(contract.category, "text-processing")
        self.assertEqual(contract.tags, ("text", "analysis"))
        self.assertEqual(contract.input_fields[0].name, "text")
        self.assertEqual(contract.output_fields[0].name, "statistics")
        self.assertTrue(contract.strict_inputs)
        self.assertTrue(contract.strict_outputs)
        self.assertEqual(contract.tools, ("local.text-statistics",))

    def test_manifest_errors_and_root_containment_are_structured(self) -> None:
        outside_manifest = self.root.parent / "outside.manifest.json"
        outside_manifest.write_text(json.dumps(_manifest()), encoding="utf-8")
        try:
            with self.assertRaises(SkillManifestError) as outside_error:
                load_skill_manifest(outside_manifest, self.root)
            self.assertEqual(outside_error.exception.code, "unsafe_manifest_path")

            unsafe_source = _manifest(source_path="../outside.md")
            local_manifest = self._write_manifest(
                "skills/unsafe.manifest.json", unsafe_source
            )
            with self.assertRaises(SkillManifestError) as source_error:
                load_skill_manifest(local_manifest, self.root)
            self.assertEqual(source_error.exception.code, "unsafe_source_path")

            malformed = self.root / "skills" / "malformed.manifest.json"
            malformed.write_text("{", encoding="utf-8")
            with self.assertRaises(SkillManifestError) as json_error:
                load_skill_manifest(malformed, self.root)
            self.assertEqual(json_error.exception.code, "invalid_manifest_json")

            invalid_version = self._write_manifest(
                "skills/invalid-version.manifest.json",
                _manifest("invalid-version", contract_version="01.2.3"),
            )
            with self.assertRaises(SkillManifestError) as version_error:
                load_skill_manifest(invalid_version, self.root)
            self.assertEqual(version_error.exception.code, "invalid_skill_contract")
        finally:
            outside_manifest.unlink(missing_ok=True)

    def test_catalog_preflight_prevents_partial_registration(self) -> None:
        self._write_manifest("skills/a-valid.manifest.json", _manifest("alpha"))
        invalid = self.root / "skills" / "z-invalid.manifest.json"
        invalid.write_text("{", encoding="utf-8")
        registry = SkillPipeline(self.root).registry

        with self.assertRaises(SkillManifestCatalogError) as raised:
            register_skill_manifest_catalog(registry)

        self.assertEqual(
            tuple(issue.manifest_path.as_posix() for issue in raised.exception.issues),
            ("skills/z-invalid.manifest.json",),
        )
        self.assertEqual(registry.list_skills(), ())

    def test_duplicate_and_preexisting_registry_conflicts_are_rejected(self) -> None:
        self._write_manifest("skills/a.manifest.json", _manifest("same"))
        self._write_manifest(
            "skills/b.manifest.json",
            _manifest("same", contract_version="2.0.0"),
        )
        registry = SkillPipeline(self.root).registry

        with self.assertRaises(SkillManifestCatalogError) as duplicate:
            register_skill_manifest_catalog(registry)
        self.assertEqual(
            duplicate.exception.issues[0].code, "duplicate_skill_identifier"
        )
        self.assertEqual(registry.list_skills(), ())

        (self.root / "skills" / "b.manifest.json").unlink()
        manifest = load_skill_manifest(
            self.root / "skills" / "a.manifest.json", self.root
        )
        registry.register(manifest.contract)
        with self.assertRaises(SkillManifestCatalogError) as existing:
            register_skill_manifest_catalog(registry)
        self.assertEqual(
            existing.exception.issues[0].code, "duplicate_skill_identifier"
        )
        self.assertEqual(registry.list_skills(), (manifest.contract,))

    def test_pipeline_validates_inputs_versions_and_outputs(self) -> None:
        manifest_path = self._write_manifest("skills/text-analysis.manifest.json")
        contract = load_skill_manifest(manifest_path, self.root).contract
        calls: list[str] = []

        def implementation(context):
            calls.append(context.inputs["text"])
            return {"statistics": {"characters": len(context.inputs["text"])}}

        pipeline = SkillPipeline(
            self.root,
            execution_adapter=LocalSkillExecutionAdapter(
                {"text-analysis": implementation}
            ),
        )
        pipeline.registry.register(contract)

        result = pipeline.invoke(
            InvocationRequest(
                "text-analysis",
                "analyze",
                {"text": "abc"},
                contract_version="1.2.0",
            )
        )
        self.assertEqual(result.status, SkillExecutionStatus.SUCCEEDED)
        if result.output is None:
            self.fail("successful Skill execution must include output")
        statistics = result.output.get("statistics")
        if not isinstance(statistics, Mapping):
            self.fail("statistics output must be a mapping")
        self.assertEqual(statistics.get("characters"), 3)

        for invalid_inputs in ({}, {"text": 5}):
            with self.subTest(inputs=invalid_inputs):
                with self.assertRaises(InvocationValidationError):
                    pipeline.invoke(
                        InvocationRequest(
                            "text-analysis", "analyze", invalid_inputs
                        )
                    )
        with self.assertRaises(InvocationValidationError):
            pipeline.invoke(
                InvocationRequest(
                    "text-analysis",
                    "analyze",
                    {"text": "abc"},
                    contract_version="9.0.0",
                )
            )
        with self.assertRaises(SkillContractVersionError):
            pipeline.registry.resolve("text-analysis", "9.0.0")
        self.assertEqual(calls, ["abc"])

        broken_pipeline = SkillPipeline(
            self.root,
            execution_adapter=LocalSkillExecutionAdapter(
                {"text-analysis": lambda context: {"statistics": [context.task]}}
            ),
        )
        broken_pipeline.registry.register(contract)
        invalid_output = broken_pipeline.invoke(
            InvocationRequest("text-analysis", "analyze", {"text": "abc"})
        )
        self.assertEqual(invalid_output.status, SkillExecutionStatus.FAILED)
        self.assertEqual(invalid_output.error_code, "invalid_skill_output")

        unavailable_pipeline = SkillPipeline(self.root)
        unavailable_pipeline.registry.register(contract)
        unavailable = unavailable_pipeline.invoke(
            InvocationRequest("text-analysis", "analyze", {"text": "abc"})
        )
        self.assertEqual(unavailable.status, SkillExecutionStatus.UNAVAILABLE)
        self.assertEqual(unavailable.error_code, "execution_unavailable")

    def test_tool_executor_exception_keeps_safe_skill_request_trace(self) -> None:
        manifest_path = self._write_manifest("skills/text-analysis.manifest.json")
        contract = load_skill_manifest(manifest_path, self.root).contract
        tools = ToolRegistry()
        executor = ToolExecutor(tools)

        def invoke_statistics(context):
            tool_result = context.invoke_tool(
                "local.text-statistics",
                {"text": context.inputs["text"]},
            )
            if tool_result.output is None:
                raise RuntimeError("statistics Tool returned no output")
            return {"statistics": dict(tool_result.output)}

        pipeline = SkillPipeline(
            self.root,
            execution_adapter=LocalSkillExecutionAdapter(
                {"text-analysis": invoke_statistics}
            ),
            tool_executor=executor,
        )
        pipeline.registry.register(contract)
        request = InvocationRequest(
            "text-analysis",
            "analyze",
            {"text": "abc"},
            request_id="12345678-1234-5678-1234-567812345678",
        )
        secret = "private executor exception detail"

        with patch.object(executor, "invoke", side_effect=RuntimeError(secret)):
            result = pipeline.invoke(request)

        self.assertEqual(result.status, SkillExecutionStatus.FAILED)
        self.assertEqual(result.error_code, "tool_execution_failed")
        self.assertEqual(len(result.tool_invocations), 1)
        invocation = result.tool_invocations[0]
        self.assertEqual(invocation.skill_request_id, request.request_id)
        self.assertEqual(invocation.status, ToolStatus.FAILED)
        self.assertEqual(invocation.error_code, "tool_invocation_failed")
        self.assertNotIn(secret, repr(result))

        no_executor_pipeline = SkillPipeline(
            self.root,
            execution_adapter=LocalSkillExecutionAdapter(
                {"text-analysis": invoke_statistics}
            ),
        )
        no_executor_pipeline.registry.register(contract)
        no_executor_result = no_executor_pipeline.invoke(request)
        self.assertEqual(no_executor_result.status, SkillExecutionStatus.UNAVAILABLE)
        self.assertEqual(no_executor_result.error_code, "execution_unavailable")
        self.assertEqual(
            no_executor_result.tool_invocations[0].skill_request_id,
            request.request_id,
        )
        self.assertIsNone(no_executor_result.tool_invocations[0].status)
        self.assertEqual(
            no_executor_result.tool_invocations[0].error_code,
            "execution_unavailable",
        )

    def test_manifest_to_workflow_path_preserves_status_and_error_envelope(self) -> None:
        manifest_path = self._write_manifest("skills/text-analysis.manifest.json")
        manifest = load_skill_manifest(manifest_path, self.root)
        tools = ToolRegistry()
        executor = ToolExecutor(tools)
        register_text_statistics(tools, executor)

        pipeline = SkillPipeline(
            self.root,
            execution_adapter=LocalSkillExecutionAdapter(
                {"text-analysis": _analyze_using_statistics_tool}
            ),
            tool_executor=executor,
        )
        registered = register_skill_manifest_catalog(pipeline.registry)
        self.assertEqual(registered, (manifest.contract,))

        with self.assertRaises(ValueError):
            SkillWorkflowAdapter(
                "skill.workflow",
                "skill.invoke.text-analysis",
                pipeline,
                "text-analysis",
                task_input="task",
                input_mapping={"text": "text"},
                contract_version="9.0.0",
            )

        workflow_adapter = SkillWorkflowAdapter(
            "skill.workflow",
            "skill.invoke.text-analysis",
            pipeline,
            "text-analysis",
            task_input="task",
            input_mapping={"text": "text"},
            contract_version="1.2.0",
        )
        tools.register(
            ToolContract(
                identifier="skill.invoke.text-analysis",
                name="Invoke text analysis",
                description="Invoke the explicitly configured text Skill.",
                input_schema=(
                    InputField("task", InputType.STRING),
                    InputField("text", InputType.STRING),
                ),
                adapter_id=workflow_adapter.adapter_id,
                execution_availability=ExecutionAvailability.AVAILABLE,
            )
        )
        executor.register_adapter(workflow_adapter)
        workflows = WorkflowRegistry()
        workflows.register(
            WorkflowDefinition(
                "workflow.text-analysis",
                "Text analysis workflow",
                (
                    WorkflowStep(
                        "analyze",
                        "skill.invoke.text-analysis",
                        {
                            "task": WorkflowInputRef("task"),
                            "text": WorkflowInputRef("text"),
                        },
                    ),
                ),
            )
        )
        engine = WorkflowEngine(workflows, tools, executor)

        result = engine.execute(
            "workflow.text-analysis",
            {"task": "analyze", "text": "hello world"},
            include_outputs=True,
        )

        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)
        step = result.step_result("analyze")
        if step is None:
            self.fail("completed workflow must retain the analyze step")
        self.assertEqual(step.status, StepStatus.SUCCEEDED)
        if step.tool_result is None or step.tool_result.output is None:
            self.fail("successful opted-in workflow step must include Tool output")
        self.assertEqual(step.tool_result.status, ToolStatus.SUCCEEDED)
        envelope = step.tool_result.output
        self.assertEqual(envelope["skill_status"], SkillExecutionStatus.SUCCEEDED.value)
        self.assertEqual(envelope["skill_identifier"], "text-analysis")
        self.assertEqual(envelope["skill_contract_version"], "1.2.0")
        skill_output = envelope.get("skill_output")
        if not isinstance(skill_output, Mapping):
            self.fail("successful embedded Skill result must include its output")
        statistics = skill_output.get("statistics")
        if not isinstance(statistics, Mapping):
            self.fail("embedded statistics output must be a mapping")
        self.assertEqual(statistics.get("words"), 2)

    def test_workflow_tool_success_does_not_mask_skill_failure(self) -> None:
        manifest_path = self._write_manifest("skills/text-analysis.manifest.json")
        contract = load_skill_manifest(manifest_path, self.root).contract
        tools = ToolRegistry()
        executor = ToolExecutor(tools)
        pipeline = SkillPipeline(
            self.root,
            execution_adapter=LocalSkillExecutionAdapter(
                {"text-analysis": lambda context: {"statistics": [context.task]}}
            ),
        )
        pipeline.registry.register(contract)
        workflow_adapter = SkillWorkflowAdapter(
            "skill.workflow",
            "skill.invoke.text-analysis",
            pipeline,
            "text-analysis",
            task_input="task",
            input_mapping={"text": "text"},
        )
        tools.register(
            ToolContract(
                identifier="skill.invoke.text-analysis",
                name="Invoke text analysis",
                description="Invoke the explicitly configured text Skill.",
                input_schema=(
                    InputField("task", InputType.STRING),
                    InputField("text", InputType.STRING),
                ),
                adapter_id=workflow_adapter.adapter_id,
                execution_availability=ExecutionAvailability.AVAILABLE,
            )
        )
        executor.register_adapter(workflow_adapter)
        workflows = WorkflowRegistry()
        workflows.register(
            WorkflowDefinition(
                "workflow.text-analysis",
                "Text analysis workflow",
                (
                    WorkflowStep(
                        "analyze",
                        "skill.invoke.text-analysis",
                        {
                            "task": WorkflowInputRef("task"),
                            "text": WorkflowInputRef("text"),
                        },
                    ),
                ),
            )
        )
        engine = WorkflowEngine(workflows, tools, executor)

        result = engine.execute(
            "workflow.text-analysis",
            {"task": "analyze", "text": "hello"},
            include_outputs=True,
        )

        self.assertEqual(result.status, WorkflowStatus.SUCCEEDED)
        step = result.step_result("analyze")
        if step is None:
            self.fail("completed workflow must retain the analyze step")
        self.assertEqual(step.status, StepStatus.SUCCEEDED)
        if step.tool_result is None or step.tool_result.output is None:
            self.fail("successful opted-in workflow step must include Tool output")
        envelope = step.tool_result.output
        self.assertEqual(envelope["skill_status"], SkillExecutionStatus.FAILED.value)
        self.assertEqual(envelope["skill_error_code"], "invalid_skill_output")


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

from scripts.skill_pipeline import (
    InvocationRequest,
    InvocationValidationError,
    SelectionError,
    SelectionStatus,
    SkillExecutionStatus,
    SkillPipeline,
)
from scripts.skill_registry import SkillContract, SkillNotFoundError


class SkillPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        skills = self.root / "skills"
        skills.mkdir()
        self.skill_dir = skills / "implementation"
        self.skill_dir.mkdir()
        self.side_effect = self.root / "executed.txt"
        self.source = self.skill_dir / "SKILL.md"
        self.source.write_text(
            "---\n"
            "name: implementation\n"
            'description: "Implement and verify software engineering tasks."\n'
            "---\n"
            f"```python\nPath({str(self.side_effect)!r}).write_text('executed')\n```\n",
            encoding="utf-8",
        )
        self.pipeline = SkillPipeline(self.root)
        self.discovery = self.pipeline.discover()
        self.skill = self.pipeline.registry.get("implementation")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_discovery_registers_valid_contracts_and_reports_issues(self):
        self.assertEqual(self.discovery.registered_identifiers, ("implementation",))
        self.assertEqual(self.discovery.issues, ())
        self.assertEqual(
            tuple(skill.identifier for skill in self.pipeline.registry.list_skills()),
            ("implementation",),
        )

    def test_search_includes_identifier_name_description_and_tags(self):
        tagged = SkillContract(
            identifier="release-review",
            name="Release reviewer",
            description="Reviews candidate changes.",
            source_path=self.skill.source_path,
            tags=("ship-it",),
        )
        self.pipeline.registry.register(tagged)

        self.assertEqual(self.pipeline.search("release"), (tagged,))
        self.assertEqual(self.pipeline.search("candidate"), (tagged,))
        self.assertEqual(self.pipeline.search("ship"), (tagged,))
        self.assertEqual(self.pipeline.search("implementation"), (self.skill,))

    def test_selects_unique_lexical_match_with_reasons(self):
        result = self.pipeline.select("implement the software task")

        self.assertEqual(result.status, SelectionStatus.SELECTED)
        self.assertIs(result.selected, self.skill)
        candidate = next(iter(result.candidates))
        self.assertEqual(candidate.matched_terms, ("implement", "software"))
        self.assertTrue(candidate.reasons)
        self.assertIn("not semantic", result.message)

    def test_returns_no_match_without_choosing_arbitrarily(self):
        result = self.pipeline.select("prepare a quarterly budget forecast")

        self.assertEqual(result.status, SelectionStatus.NO_MATCH)
        self.assertIsNone(result.selected)
        self.assertEqual(result.candidates, ())

    def test_ambiguous_top_score_has_deterministic_candidates(self):
        second = SkillContract(
            identifier="software-review",
            name="Software reviewer",
            description="Reviews software tasks.",
            source_path=self.skill.source_path,
        )
        self.pipeline.registry.register(second)

        result = self.pipeline.select("software task")

        self.assertEqual(result.status, SelectionStatus.AMBIGUOUS)
        self.assertIsNone(result.selected)
        self.assertEqual(
            [candidate.skill.identifier for candidate in result.candidates],
            ["implementation", "software-review"],
        )
        self.assertIn("specify a Skill identifier", result.message)

    def test_explicit_identifier_is_validated_and_constraints_applied(self):
        result = self.pipeline.select(
            "unrelated user task",
            skill_identifier="implementation",
            allowed_identifiers=("implementation",),
        )
        self.assertEqual(result.status, SelectionStatus.SELECTED)
        candidate = next(iter(result.candidates))
        self.assertEqual(candidate.score, 0)

        with self.assertRaisesRegex(SkillNotFoundError, "not registered"):
            self.pipeline.select("task", skill_identifier="missing")
        other = SkillContract(
            identifier="other",
            name="Other",
            description="Other skill.",
            source_path=self.skill.source_path,
        )
        self.pipeline.registry.register(other)
        with self.assertRaisesRegex(SelectionError, "excluded"):
            self.pipeline.select(
                "task",
                skill_identifier="implementation",
                allowed_identifiers=("other",),
            )

    def test_invocation_request_validation_and_plan_creation(self):
        request = InvocationRequest(
            skill_identifier="implementation",
            task="Fix the bug",
        )
        plan = self.pipeline.prepare_invocation(request)

        self.assertEqual(plan.request_id, request.request_id)
        self.assertEqual(plan.source_path, self.source.resolve())
        self.assertEqual(plan.status, "PREPARED_NOT_EXECUTED")
        self.assertFalse(plan.execution_available)
        self.assertFalse(self.side_effect.exists())

    def test_rejects_malformed_invocation_requests(self):
        with self.assertRaisesRegex(InvocationValidationError, "task"):
            InvocationRequest(skill_identifier="implementation", task=" ")
        with self.assertRaisesRegex(InvocationValidationError, "UUID"):
            InvocationRequest(
                skill_identifier="implementation",
                task="Task",
                request_id="not-a-uuid",
            )
        with self.assertRaisesRegex(InvocationValidationError, "input names"):
            InvocationRequest(
                skill_identifier="implementation",
                task="Task",
                inputs={" ": "invalid"},
            )

    def test_validates_declared_input_names_without_inventing_schema(self):
        contract = SkillContract(
            identifier="with-inputs",
            name="With inputs",
            description="A Skill with declared input names.",
            source_path=self.skill.source_path,
            inputs=("repository",),
        )
        self.pipeline.registry.register(contract)
        allowed = InvocationRequest(
            skill_identifier="with-inputs",
            task="Inspect repository",
            inputs={"repository": "."},
        )
        self.assertEqual(
            self.pipeline.prepare_invocation(allowed).inputs["repository"],
            ".",
        )

        rejected = InvocationRequest(
            skill_identifier="with-inputs",
            task="Inspect repository",
            inputs={"credential": "secret"},
        )
        with self.assertRaises(InvocationValidationError):
            self.pipeline.prepare_invocation(rejected)

        no_declarations = InvocationRequest(
            skill_identifier="implementation",
            task="Task",
            inputs={"arbitrary-structured-value": {"enabled": True}},
        )
        self.assertEqual(
            self.pipeline.prepare_invocation(no_declarations).inputs,
            {"arbitrary-structured-value": {"enabled": True}},
        )

    def test_execution_is_explicitly_unavailable_and_nothing_runs(self):
        request = InvocationRequest(skill_identifier="implementation", task="Task")
        with (
            patch("subprocess.Popen") as process,
            patch("socket.create_connection") as network,
        ):
            plan = self.pipeline.prepare_invocation(request)
            result = self.pipeline.execute(plan)
        process.assert_not_called()
        network.assert_not_called()
        self.assertEqual(result.status, SkillExecutionStatus.UNAVAILABLE)
        self.assertEqual(result.error_code, "execution_unavailable")
        self.assertFalse(self.side_effect.exists())

    def test_rejects_non_request_and_empty_task_inputs(self):
        with self.assertRaisesRegex(SelectionError, "non-empty"):
            self.pipeline.select(" ")
        with self.assertRaisesRegex(SelectionError, "tuple"):
            self.pipeline.select("task", allowed_identifiers=cast(Any, 42))
        with self.assertRaisesRegex(InvocationValidationError, "InvocationRequest"):
            self.pipeline.prepare_invocation(cast(Any, object()))


if __name__ == "__main__":
    unittest.main()

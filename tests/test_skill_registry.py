import tempfile
import unittest
from pathlib import Path

from scripts.skill_registry import (
    DuplicateSkillError,
    SkillContract,
    SkillMetadataError,
    SkillNotFoundError,
    SkillRegistry,
    discover_skills,
)


class SkillContractTests(unittest.TestCase):
    def test_builds_contract_with_optional_declarations(self):
        contract = SkillContract.from_mapping(
            {
                "identifier": "example-skill",
                "name": "Example Skill",
                "description": "Describes the example.",
                "source_path": "skills/example/SKILL.md",
                "version": "1.2",
                "category": "engineering",
                "tags": ["python", "review"],
                "inputs": ["repository"],
                "outputs": ["report"],
                "tools": ["git"],
                "capabilities": ["read-only"],
            }
        )

        self.assertEqual(contract.identifier, "example-skill")
        self.assertEqual(contract.tags, ("python", "review"))
        self.assertEqual(contract.inputs, ("repository",))
        self.assertEqual(contract.capabilities, ("read-only",))

    def test_rejects_missing_required_metadata(self):
        with self.assertRaisesRegex(SkillMetadataError, "missing required"):
            SkillContract.from_mapping({"identifier": "example"})

    def test_rejects_invalid_identifier_and_field_types(self):
        base = {
            "identifier": "Example_Skill",
            "name": "Example",
            "description": "Description",
            "source_path": "skills/example.md",
        }
        with self.assertRaisesRegex(SkillMetadataError, "kebab-case"):
            SkillContract.from_mapping(base)

        base["identifier"] = "example"
        base["tags"] = "not-a-sequence-of-tags"
        with self.assertRaisesRegex(SkillMetadataError, "tags must be a sequence"):
            SkillContract.from_mapping(base)

        base["tags"] = [1]
        with self.assertRaisesRegex(SkillMetadataError, "tuple of non-empty strings"):
            SkillContract.from_mapping(base)

    def test_rejects_unknown_metadata_fields(self):
        with self.assertRaisesRegex(SkillMetadataError, "unknown metadata field"):
            SkillContract.from_mapping(
                {
                    "identifier": "example",
                    "name": "Example",
                    "description": "Description",
                    "source_path": "skills/example.md",
                    "execute": True,
                }
            )

    def test_resolves_source_under_repository_and_requires_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "skills" / "example.md"
            source.parent.mkdir()
            source.write_text("untrusted Skill content", encoding="utf-8")
            contract = SkillContract.from_mapping(
                {
                    "identifier": "example",
                    "name": "Example",
                    "description": "Description",
                    "source_path": "skills/example.md",
                }
            )

            self.assertEqual(contract.resolve_source(root), source.resolve())

            missing = SkillContract.from_mapping(
                {
                    "identifier": "missing",
                    "name": "Missing",
                    "description": "Description",
                    "source_path": "skills/missing.md",
                }
            )
            with self.assertRaisesRegex(SkillMetadataError, "does not exist"):
                missing.resolve_source(root)

    def test_rejects_path_traversal_outside_repository(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repo"
            root.mkdir()
            contract = SkillContract.from_mapping(
                {
                    "identifier": "outside",
                    "name": "Outside",
                    "description": "Description",
                    "source_path": "../outside.md",
                }
            )

            with self.assertRaisesRegex(SkillMetadataError, "escapes"):
                contract.resolve_source(root)

    def test_rejects_symlink_source_escaping_repository(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repo"
            root.mkdir()
            outside = Path(temporary_directory) / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            skills = root / "skills"
            skills.mkdir()
            source = skills / "linked.md"
            try:
                source.symlink_to(outside)
            except OSError as error:
                self.skipTest(f"symlink creation is unavailable: {error}")

            contract = SkillContract(
                identifier="linked",
                name="Linked",
                description="Description",
                source_path=Path("skills/linked.md"),
            )
            with self.assertRaisesRegex(SkillMetadataError, "escapes"):
                contract.resolve_source(root)


class SkillRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.skills_directory = self.root / "skills"
        self.skills_directory.mkdir()
        (self.skills_directory / "one.md").write_text("# One\n", encoding="utf-8")
        (self.skills_directory / "two.md").write_text("# Two\n", encoding="utf-8")
        self.registry = SkillRegistry(self.root)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def contract(self, identifier, name, description, source_path, tags=()):
        return SkillContract(
            identifier=identifier,
            name=name,
            description=description,
            source_path=Path(source_path),
            tags=tuple(tags),
        )

    def test_register_lookup_and_deterministic_listing(self):
        second = self.contract("zeta", "Zeta", "Last entry", "skills/two.md")
        first = self.contract("alpha", "Alpha", "First entry", "skills/one.md")
        self.registry.register(second)
        self.registry.register(first)

        self.assertIs(self.registry.get("alpha"), first)
        self.assertEqual(
            [skill.identifier for skill in self.registry.list_skills()],
            ["alpha", "zeta"],
        )

    def test_rejects_duplicate_identifier_and_reports_missing_lookup(self):
        contract = self.contract("alpha", "Alpha", "First entry", "skills/one.md")
        self.registry.register(contract)
        with self.assertRaisesRegex(DuplicateSkillError, "already registered"):
            self.registry.register(contract)
        with self.assertRaisesRegex(SkillNotFoundError, "not registered"):
            self.registry.get("missing")

    def test_searches_name_description_and_tags(self):
        contract = self.contract(
            "alpha",
            "Alpha Build",
            "Creates a build report",
            "skills/one.md",
            tags=("release",),
        )
        self.registry.register(contract)

        self.assertEqual(self.registry.search("BUILD"), (contract,))
        self.assertEqual(self.registry.search("report"), (contract,))
        self.assertEqual(self.registry.search("release"), (contract,))
        self.assertEqual(self.registry.search("unmatched"), ())

    def test_rejects_blank_search(self):
        with self.assertRaisesRegex(SkillMetadataError, "search query"):
            self.registry.search(" ")


class SkillDiscoveryTests(unittest.TestCase):
    def test_discovers_existing_style_front_matter_without_execution(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skill_directory = root / "skills" / "example-skill"
            skill_directory.mkdir(parents=True)
            side_effect = root / "executed.txt"
            source = skill_directory / "SKILL.md"
            source.write_text(
                "---\n"
                "name: example-skill\n"
                'description: "A test Skill."\n'
                "---\n"
                "# Example Skill\n"
                f"```python\nPath({str(side_effect)!r}).write_text('executed')\n```\n",
                encoding="utf-8",
            )

            result = discover_skills(root)

            self.assertEqual(result.issues, ())
            self.assertEqual(len(result.skills), 1)
            self.assertEqual(result.skills[0].identifier, "example-skill")
            self.assertEqual(result.skills[0].name, "Example Skill")
            self.assertEqual(result.skills[0].source_path, Path("skills/example-skill/SKILL.md"))
            self.assertFalse(side_effect.exists())

    def test_returns_actionable_issue_for_incomplete_candidate(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skill_directory = root / "skills" / "broken"
            skill_directory.mkdir(parents=True)
            (skill_directory / "SKILL.md").write_text(
                "---\nname: broken\n---\n", encoding="utf-8"
            )

            result = discover_skills(root)

            self.assertEqual(result.skills, ())
            self.assertEqual(len(result.issues), 1)
            self.assertEqual(result.issues[0].source_path, Path("skills/broken/SKILL.md"))
            self.assertIn("description", result.issues[0].message)

    def test_reports_unclosed_front_matter(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skill_directory = root / "skills"
            skill_directory.mkdir()
            (skill_directory / "broken.md").write_text(
                "---\nname: broken\ndescription: Missing end\n", encoding="utf-8"
            )

            result = discover_skills(root)

            self.assertEqual(len(result.issues), 1)
            self.assertIn("no closing", result.issues[0].message)

    def test_rejects_non_string_required_scalars(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skills = root / "skills"
            skills.mkdir()
            (skills / "broken.md").write_text(
                "---\nname: true\ndescription: 12\n---\n", encoding="utf-8"
            )

            result = discover_skills(root)

            self.assertEqual(result.skills, ())
            self.assertEqual(len(result.issues), 1)
            self.assertIn("non-string", result.issues[0].message)

    def test_excludes_skill_index_and_cache_directories(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skills = root / "skills"
            skills.mkdir()
            (skills / "README.md").write_text("---\ninvalid\n", encoding="utf-8")
            cache = skills / "__pycache__"
            cache.mkdir()
            (cache / "cached.md").write_text(
                "---\nname: cached\ndescription: ignored\n---\n", encoding="utf-8"
            )

            result = discover_skills(root)

            self.assertEqual(result.skills, ())
            self.assertEqual(result.issues, ())

    def test_reports_duplicate_identifiers(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skills = root / "skills"
            skills.mkdir()
            for filename in ("a.md", "b.md"):
                (skills / filename).write_text(
                    "---\nname: duplicate\ndescription: Same id\n---\n",
                    encoding="utf-8",
                )

            result = discover_skills(root)

            self.assertEqual([skill.identifier for skill in result.skills], ["duplicate"])
            self.assertEqual(len(result.issues), 1)
            self.assertIn("duplicate Skill identifier", result.issues[0].message)

    def test_rejects_skills_directory_symlink_outside_repository(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repo"
            root.mkdir()
            outside = Path(temporary_directory) / "outside"
            outside.mkdir()
            (outside / "skill.md").write_text(
                "---\nname: outside\ndescription: Outside\n---\n",
                encoding="utf-8",
            )
            try:
                (root / "skills").symlink_to(outside, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symlink creation is unavailable: {error}")

            with self.assertRaisesRegex(SkillMetadataError, "outside the repository root"):
                discover_skills(root)


if __name__ == "__main__":
    unittest.main()

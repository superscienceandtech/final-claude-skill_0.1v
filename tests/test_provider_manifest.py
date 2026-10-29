from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_provider_manifest import validate_provider_manifest


class ProviderManifestValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        plugin_directory = self.root / ".claude-plugin"
        plugin_directory.mkdir()
        (plugin_directory / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "sample-plugin",
                    "description": "A test plugin.",
                }
            ),
            encoding="utf-8",
        )
        skill_directory = self.root / "skills" / "sample"
        skill_directory.mkdir(parents=True)
        (skill_directory / "SKILL.md").write_text(
            "---\nname: sample\ndescription: A sample Skill.\n---\n# Sample\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_accepts_local_manifest_using_one_canonical_skill_source(self) -> None:
        self.assertEqual(validate_provider_manifest(self.root), ())

    def test_reports_malformed_manifest_and_missing_manifest(self) -> None:
        manifest_path = self.root / ".claude-plugin" / "plugin.json"
        manifest_path.write_text("{", encoding="utf-8")
        self.assertEqual(
            validate_provider_manifest(self.root),
            ("plugin manifest cannot be read as JSON: JSONDecodeError",),
        )

        manifest_path.unlink()
        self.assertEqual(
            validate_provider_manifest(self.root),
            ("plugin manifest is missing: .claude-plugin/plugin.json",),
        )

    def test_rejects_duplicate_manifest_keys_at_any_object_depth(self) -> None:
        manifest_path = self.root / ".claude-plugin" / "plugin.json"
        manifest_path.write_text(
            '{"name":"sample-plugin","description":"Valid",'
            '"metadata":{"owner":"first","owner":"second"}}',
            encoding="utf-8",
        )

        self.assertEqual(
            validate_provider_manifest(self.root),
            ("plugin manifest contains a duplicate JSON object key.",),
        )

    def test_rejects_plugin_directory_junction(self) -> None:
        plugin_directory = self.root / ".claude-plugin"
        original_is_junction = Path.is_junction

        def is_junction(path: Path) -> bool:
            if path == plugin_directory:
                return True
            return original_is_junction(path)

        with patch.object(Path, "is_junction", is_junction):
            issues = validate_provider_manifest(self.root)

        self.assertEqual(
            issues,
            ("plugin directory must not be a symlink or junction.",),
        )

    def test_rejects_invalid_manifest_fields_and_noncanonical_skill_path_config(self) -> None:
        manifest_path = self.root / ".claude-plugin" / "plugin.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "name": "Invalid_Name",
                    "description": " ",
                    "skills": ["skills/sample/SKILL.md"],
                }
            ),
            encoding="utf-8",
        )

        issues = validate_provider_manifest(self.root)

        self.assertEqual(
            issues,
            (
                "plugin manifest name must be lowercase kebab-case.",
                "plugin manifest description must be a non-empty string.",
                "plugin manifest must use the default skills/ directory to preserve canonical sources.",
            ),
        )

    def test_rejects_invalid_canonical_skill_and_empty_skill_set(self) -> None:
        skill_path = self.root / "skills" / "sample" / "SKILL.md"
        skill_path.write_text("# Missing front matter\n", encoding="utf-8")
        issues = validate_provider_manifest(self.root)
        self.assertTrue(any("invalid canonical Skill" in issue for issue in issues))

        skill_path.unlink()
        self.assertIn(
            "no valid canonical Skills were discovered under skills/.",
            validate_provider_manifest(self.root),
        )

    def test_rejects_invalid_root_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "pathlib.Path"):
            validate_provider_manifest("not-a-path")  # type: ignore[arg-type]

    def test_repository_configuration_passes_without_provider_runtime(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        self.assertEqual(validate_provider_manifest(repository_root), ())


if __name__ == "__main__":
    unittest.main()

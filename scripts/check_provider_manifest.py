"""Validate local provider-package metadata against canonical Skill discovery.

This checks repository configuration only. It does not invoke or verify a
provider runtime.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from scripts.skill_registry import SkillMetadataError, discover_skills


_PLUGIN_NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class _DuplicateManifestKey(ValueError):
    """Raised when a JSON object repeats a key."""


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateManifestKey(key)
        result[key] = value
    return result


def validate_provider_manifest(repository_root: Path) -> tuple[str, ...]:
    """Return stable diagnostics for the repository's local Claude plugin config."""
    if not isinstance(repository_root, Path):
        raise ValueError("repository_root must be a pathlib.Path.")
    try:
        root = repository_root.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError("repository_root must exist and be accessible.") from error
    if not root.is_dir():
        raise ValueError("repository_root must be a directory.")

    plugin_directory = root / ".claude-plugin"
    manifest_path = plugin_directory / "plugin.json"
    if plugin_directory.is_symlink() or plugin_directory.is_junction():
        return ("plugin directory must not be a symlink or junction.",)
    try:
        if manifest_path.is_symlink() or manifest_path.is_junction():
            return ("plugin manifest must be a regular file inside repository_root.",)
        resolved_manifest = manifest_path.resolve(strict=True)
        if not resolved_manifest.is_relative_to(root) or not resolved_manifest.is_file():
            return ("plugin manifest must be a regular file inside repository_root.",)
    except FileNotFoundError:
        return ("plugin manifest is missing: .claude-plugin/plugin.json",)
    except (OSError, RuntimeError, ValueError):
        return ("plugin manifest cannot be resolved safely.",)

    try:
        with resolved_manifest.open(encoding="utf-8") as manifest_file:
            manifest = json.load(
                manifest_file,
                object_pairs_hook=_unique_json_object,
            )
    except FileNotFoundError:
        return ("plugin manifest is missing: .claude-plugin/plugin.json",)
    except _DuplicateManifestKey:
        return ("plugin manifest contains a duplicate JSON object key.",)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return (f"plugin manifest cannot be read as JSON: {type(error).__name__}",)

    if not isinstance(manifest, dict):
        return ("plugin manifest must contain a JSON object.",)

    issues: list[str] = []
    name = manifest.get("name")
    description = manifest.get("description")
    if not isinstance(name, str) or not _PLUGIN_NAME_PATTERN.fullmatch(name):
        issues.append("plugin manifest name must be lowercase kebab-case.")
    if not isinstance(description, str) or not description.strip():
        issues.append("plugin manifest description must be a non-empty string.")
    if "skills" in manifest:
        issues.append(
            "plugin manifest must use the default skills/ directory to preserve canonical sources."
        )

    skills_directory = root / "skills"
    if skills_directory.is_symlink():
        issues.append("skills directory must not be a symlink.")
    try:
        discovery = discover_skills(root)
    except (OSError, UnicodeError, SkillMetadataError) as error:
        issues.append(f"native Skill discovery failed: {type(error).__name__}")
    else:
        if not discovery.skills:
            issues.append("no valid canonical Skills were discovered under skills/.")
        for issue in discovery.issues:
            issues.append(
                f"invalid canonical Skill at {issue.source_path.as_posix()}: {issue.message}"
            )
        for skill in discovery.skills:
            expected = Path("skills") / skill.identifier / "SKILL.md"
            if skill.source_path != expected:
                issues.append(
                    f"Skill '{skill.identifier}' does not resolve to its canonical path."
                )
    return tuple(issues)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check local Claude plugin metadata and canonical Skill paths; "
            "does not load the provider runtime."
        )
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        issues = validate_provider_manifest(args.repository_root)
    except ValueError as error:
        parser.error(str(error))

    if issues:
        for issue in issues:
            print(f"FAIL: {issue}", file=sys.stderr)
        return 1
    print("PASS: plugin manifest is consistent with canonical Skill discovery.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

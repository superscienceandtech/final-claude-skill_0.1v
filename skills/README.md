# Skills and workflows

Native Skill packages use `skills/<skill-name>/SKILL.md`. The framework
registry's `discover_skills` API follows this convention; other Markdown
documents are not native Skill candidates.

## Claude Code integration

The canonical Skill files remain in `skills/`. The repository root is also a
Claude Code plugin, declared by `.claude-plugin/plugin.json`. Its default
plugin `skills/` component directory points at the same
`skills/<skill-name>/SKILL.md` files without copies, symlinks, or a second
source of truth, following the [documented plugin component
layout](https://code.claude.com/docs/en/plugins/components#skills).

From the repository root, load the plugin for a Claude Code session with:

    claude --plugin-dir .

The documented command form when loaded is
`/claude-skills-library:implementation`. This repository currently documents
the local plugin-development load path; it does not define a marketplace or
permanent installation. The configuration and registry tests do not establish
runtime discovery, which must be checked in Claude Code itself. Loading a Skill
does not grant authorization to run its instructions or any protected
validator.

## Native Skill packages

- [repository-audit](./repository-audit/SKILL.md) — bounded, read-only repository metadata audit instructions. The instructions are not an execution sandbox.
- [implementation](./implementation/SKILL.md) — provider-neutral guidance for carrying out software engineering tasks safely and verifiably. Static package structure does not verify compatibility with any Claude product.

## Workflow guidance

General workflow documents may live outside native Skill entry paths and are
not discovered by `discover_skills`.

## Framework manifest

- [text-analysis.manifest.json](./text-analysis.manifest.json) — framework integration example for the typed text-analysis contract. Its source path references the implementation Skill as metadata; the configured statistics tool is implemented separately in `scripts/tool_framework.py`. A manifest is not a provider-native Skill entry point and is not automatically registered or executed by native Skill discovery.

See [tool setup](../docs/tool-setup/README.md) for how the native Skill package, framework manifest, and explicitly configured tool adapter fit together.

## Design principles

- Keep the workflow reusable across providers and repositories.
- Require inspection and verification before claiming completion.
- Avoid hidden assumptions, scope creep, and unapproved architecture decisions.
- Separate implementation from independently verified acceptance.

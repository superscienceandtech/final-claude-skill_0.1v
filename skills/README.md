# Skills and workflows

Native Skill packages use `skills/<skill-name>/SKILL.md`. The framework
registry's `discover_skills` API follows this convention; other Markdown
documents are not native Skill candidates.

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

# Claude Skills

An evolving, provider-neutral custom Skills engineering project. This repository contains native Skill packages, reusable workflow infrastructure, framework manifests, validators, and tests.

## Included capabilities

- `skills/repository-audit/SKILL.md` — a native Skill package with bounded, read-only audit instructions; its instructions are not an execution sandbox.
- `skills/implementation/SKILL.md` — provider-neutral implementation Skill instructions and the first native Skill package.
- `skills/text-analysis.manifest.json` — framework integration example for a text-analysis contract.
- `scripts/validate-skill.py` — structural validator for the repository-audit Skill.
- `scripts/tool_framework.py` — typed tool contracts and local tool implementations, including text statistics.
- `scripts/skill_pipeline.py` — Skill selection and invocation pipeline.
- `scripts/skill_registry.py` — in-memory Skill metadata registry.
- `scripts/tool_workflow.py` — sequential tool workflow infrastructure.

Native Skill packages use `skills/<skill-name>/SKILL.md`. General Markdown
workflow documents are not registered by native Skill discovery; JSON
framework manifests are loaded separately and do not establish native Skill
packaging or authorize execution. The text-analysis manifest is an integration
example, not a provider-native Skill entry point or a standalone implementation.
Its configured tool is implemented in `scripts/tool_framework.py`.

## Architecture baseline

- [Repository architecture audit](docs/audits/architecture-audit.md)
- [ARC dependency map and status register](docs/architecture/arc-dependency-map.md)
- [Team roles and file ownership](docs/architecture/team-file-ownership.md)
- [Implementation roadmap](docs/architecture/implementation-roadmap.md)
- [Module contract template](docs/architecture/module-contract-template.md)
- [Proposed repository-audit Skill contract](docs/architecture/repository-audit-skill-spec.md)

These documents include proposals and decisions that may require team review. Implementation, evaluation, and approval are separate lifecycle stages.

## Supporting documentation

- [Skill index and design principles](skills/README.md)
- [Tool setup guidance](docs/tool-setup/README.md)
- [Compatibility status](docs/compatibility/README.md)
- [Provider boundary](providers/README.md)
- [Integration boundary](integrations/README.md)
- [Provisional structural validator specification](docs/skills/provisional-structural-validator-spec.md)
- [Member 3 acceptance matrix](docs/member-3-acceptance-matrix.md)
- [Member 3 scope clarification](docs/member-3-scope-clarification.md)

## Validate the repository-audit Skill

The structural validator uses POSIX directory-descriptor operations with
no-follow semantics. It deliberately fails closed on non-POSIX platforms;
canonical Skill validation on Windows is unsupported. CI runs on Ubuntu with
Python 3.12. Other Python/platform combinations are not certified by CI.

POSIX (from the repository root):

    python3 -B scripts/validate-skill.py --repo-root "$PWD" --skill-path skills/repository-audit/SKILL.md
    python3 -B -m unittest discover -s tests/skills/repository-audit -v
    python3 -B -m unittest discover -s tests -v
    python3 -B scripts/check_markdown_links.py

Windows PowerShell (tests and link check only; the Skill validator is unsupported):

    python -B -m unittest discover -s tests -v
    python -B scripts/check_markdown_links.py

The validator checks Skill metadata and required structure. Passing local checks does not prove secure enforcement by an execution host. The tests are implementation tests, not independent evaluation. Do not infer provider compatibility or execution-security guarantees from these checks alone.

## Repository conventions

- Keep implementation work scoped and reviewable.
- Prefer repository-native tooling and verifiable validation commands.
- Treat provider-specific tooling as adapters, not as canonical behavior.
- Report evidence, risks, and blockers explicitly.

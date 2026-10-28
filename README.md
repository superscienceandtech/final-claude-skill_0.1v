# Claude Skills

An evolving, provider-neutral AGI custom Skills engineering system. This repository contains workflow infrastructure, implementation guidance, and the repository-audit Skill with its structural validator and tests.

## Included capabilities

- `skills/implementation/implementation.md` — provider-neutral implementation workflow.
- `skills/repository-audit/SKILL.md` — repository-audit Skill instructions.
- `scripts/validate-skill.py` — structural validator for the repository-audit Skill.
- `scripts/skill_pipeline.py` — Skill selection and invocation pipeline.
- `scripts/skill_registry.py` — in-memory Skill metadata registry.
- `scripts/tool_workflow.py` — sequential tool workflow infrastructure.

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

Run these commands from the repository root using Python 3.

Bash / Linux:

    python3 -B scripts/validate-skill.py --repo-root "$PWD" --skill-path skills/repository-audit/SKILL.md
    python3 -B -m unittest discover -s tests/skills/repository-audit -v

PowerShell:

    python -B scripts/validate-skill.py --repo-root (Get-Location).Path --skill-path skills/repository-audit/SKILL.md
    python -B -m unittest discover -s tests/skills/repository-audit -v

The validator checks Skill metadata and required structure. Passing local checks does not prove secure enforcement by an execution host. The tests are implementation tests, not independent evaluation. Do not infer provider compatibility or execution-security guarantees from these checks alone.

## Repository conventions

- Keep implementation work scoped and reviewable.
- Prefer repository-native tooling and verifiable validation commands.
- Treat provider-specific tooling as adapters, not as canonical behavior.
- Report evidence, risks, and blockers explicitly.

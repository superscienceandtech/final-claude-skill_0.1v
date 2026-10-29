# Team File Ownership

This ownership plan is proposed for team agreement. Every file should have one accountable owner at a time. Reviewers may review another member's work, but simultaneous editing of the same file should be avoided. Ownership is not approval authority unless separately agreed.

## Roles and accountability

| Member | Role | Accountable scope |
|---|---|---|
| Member 1 | Architecture and Integration Lead | Architecture and repository governance; module contracts and architecture decisions; shared-file ownership and integration planning |
| Member 2 | Research, Testing and Evaluation Lead | Research evidence standards; evaluation scenarios and testing; independent verification and security-test coordination |
| Member 3 | Skills and Tooling Engineer | Canonical Skills and implementation workflows; provider compatibility documentation; developer-tool integration documentation |

## Proposed file ownership

| File or path | Accountable owner | Review collaborators |
|---|---|---|
| `README.md` | Member 1 | Members 2 and 3 |
| `docs/audits/architecture-audit.md` | Member 1 | Members 2 and 3 |
| `docs/architecture/arc-dependency-map.md` | Member 1 | Members 2 and 3 |
| `docs/architecture/team-file-ownership.md` | Member 1 | Members 2 and 3 |
| `docs/architecture/implementation-roadmap.md` | Member 1 | Members 2 and 3 |
| `docs/architecture/module-contract-template.md` | Member 1 | Members 2 and 3 |
| `docs/architecture/decisions/*` | Member 1 | Relevant domain owner; team review for cross-cutting decisions |
| `docs/architecture/repository-audit-skill-spec.md` | Member 1 | Members 2 and 3 |
| `docs/research/*` | Member 2 | Member 1 for boundaries; Member 3 for Skill/tool implications |
| `docs/testing/*`, `docs/evaluation/*`, independent evaluation artifacts (if approved) | Member 2 | Member 1 for contracts; Member 3 for implementation feasibility |
| `tests/skills/repository-audit/*` implementation tests | Member 3 | Member 1 for contract alignment; Member 2 for independent evaluation coverage |
| `docs/security/*` | Member 1 | Member 2 coordinates test evidence; Member 3 reviews tooling implications |
| `skills/*` | Member 3 | Member 1 for contract alignment; Member 2 for evaluation evidence |
| `adapters/*`, `integrations/*` | Member 3 | Member 1 for boundaries; Member 2 for test evidence |
| Skill validation scripts, if approved | Member 3 | Member 2 reviews validation cases |
| `skills/repository-audit/SKILL.md` | Member 3 | Member 1 for contract/safety; Member 2 for evaluation coverage |
| `scripts/validate-skill.py` | Member 3 | Member 2 reviews expected validation cases |

OWNER-DECISION-M1-01 assigns implementation tests to Member 3 and independent evaluation fixtures, rubric, and reports to Member 2. The older shared-path assignment above is superseded for this Skill. Member 2's evaluation artifacts must use a distinct agreed path and must not replace or co-own the implementation test directory.

## Change coordination

1. The accountable owner prepares the change on an agreed branch and links acceptance criteria.
2. Reviewers provide feedback without editing the same file concurrently.
3. Cross-ARC or shared-contract changes are coordinated by Member 1 and reviewed by affected owners.
4. A PR author records checks actually run and their results. Review, evaluation and approval remain distinct states.
5. Before implementation begins, the team must decide the integration base because branch histories diverge (see the audit).

Unlisted files remain unassigned until the team names an owner. This proposal does not grant repository or external-service permissions.

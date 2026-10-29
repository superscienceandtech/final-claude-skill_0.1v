# Request: Project Owner Skill-execution authorization

**Status:** DRAFT REQUEST — awaiting an explicit Owner decision. This is not an authorization.

## Exact target and scope to decide

- Approved specification: `docs/architecture/repository-audit-skill-spec.md`, SHA-256 `b33adec843e3550125aceb2af71c07a3d3c09539f4fa732eb145dd6b3d119afd`.
- Implementation commit: **NOT SELECTED**. Member 2 must first confirm the target; do not substitute the current HEAD without an explicit selection.
- Proposed Skill execution: only the synthetic isolated fixtures and H-01–H-05/P-01–P-10 scenarios in `../EVALUATION_PLAN.md`, with the Member 2-confirmed scope and expected outcomes. This request does not authorize local or real-repository execution outside that scope.
- Decision needed: explicitly authorize or decline execution for the exact commit, host, fixture set, scenario IDs, and date/window after those values are filled and the prerequisites below are evidenced.

## Required prerequisites before execution

1. Member 2 confirms evaluator identity, independence, artifact path, fixture ownership, scope, expected outcomes, and exact target commit.
2. A trusted isolated host is identified and evidence shows enforcement of fixed executable/argument arrays, validated cwd/path containment, sanitized child environment, no-shell operation, read-only repository access or equivalent write prevention, and network restrictions.
3. The host demonstrates per-process 5-second and total 30-second deadlines, no more than 20 process invocations, capture-time caps of 16 KiB stdout and 4 KiB stderr per process, termination behavior, and race-resistant path resolution. Evidence must be attributable to the host; mocks and this Skill's instructions are insufficient.
4. Synthetic fixtures and before-state snapshots are prepared outside the project worktree. No project credentials/configuration/content is copied into them.
5. The exact specification hash and selected implementation commit are verified immediately before the evaluation.

## Owner decision field

- Exact commit: NOT SELECTED.
- Host and evidence reference: NOT PROVIDED.
- Scenario scope: awaiting Member 2 confirmation.
- Decision: **PENDING — no execution authorization granted by this draft.**
- Owner response/signature/date: NOT PROVIDED.

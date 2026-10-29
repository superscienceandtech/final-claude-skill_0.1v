# Proposed M2 First Task — Implementation-to-Verification Handoff

**Status:** `PROPOSED — OWNER REVIEW REQUIRED`. This specification is not an
accepted ARC contract, task authorization, independent evaluation, or release
approval. The later completion-gate request authorizes its own bounded
implementation and validation work; that does not retroactively accept or
authorize this separate documentation-only proposal. See
[M2 prerequisite status](./m2-prerequisite-status.md).

## Objective

Make the existing implementation workflow usable by the solo maintainer by
documenting a precise Claude Code-to-Project Owner handoff, including a
separately executed verification procedure, evidence fields, and stop
conditions. The Owner is a different actor from Claude Code when Claude Code
implements, but also directs the work; the verification procedure must not be
called independent until its relationship to ARC-06 is explicitly decided.

## Scope

After the Owner explicitly accepts this proposal and its exact scope, update
only these existing documentation files:

- `workflows/spec-to-implementation/README.md` — replace Member-dependent
  entry/reporting assumptions within the workflow with the accepted solo role
  mapping and handoff.
- `docs/architecture/m2-prerequisite-status.md` — append the task evidence
  record after execution; do not create a duplicate evidence document.

The applied sample is the documentation change itself. Keep it local to the
current branch; do not merge, push, or claim an integration target. The task
must not involve the repository-audit Skill, its validator or evaluation,
external credentials, network access, production systems, or consequential
operations.

Out of scope: `skills/implementation/SKILL.md` (already has pre-existing
worktree changes), any other Skill package, source code, tests, provider
adapters, execution permissions, a test framework, automatic approval, or
repository-audit evaluation evidence. Revisit the Skill only after its
pre-existing diff is reviewed and the relevant canonical-Skill decision and
task scope are explicitly accepted.

## Deliverables

1. A recorded, Owner-accepted handoff contract defining responsibilities,
   required evidence, result states, and stop/escalation behavior.
2. The workflow clearly states the proposed responsibilities of the Project
   Owner, Claude Code implementer, verification operator, and evidence owner.
3. One completed handoff record in the prerequisite-status document, with
   baseline, changed paths, exact commands, exit codes, outputs, and
   limitations.
4. A verification record describing who separately ran the agreed procedure
   and whether it is reproducibility evidence or meets the Owner-approved
   independence criterion.
5. Separate outcomes for implementation, verification, approval, CI, and
   release; no outcome implies another.

## Acceptance criteria

- The sample task has an explicit objective, in/out-of-scope list, inputs,
  observable acceptance criteria, and authorization boundaries before
  implementation begins.
- The implementer record identifies the baseline commit, changed paths,
  exact validation commands, exit outcomes, failures, and limitations; it
  does not imply checks that were not run.
- The handoff contains enough information for the Owner to repeat every
  agreed acceptance check without asking Claude Code to reconstruct missing
  details.
- The verification operator records the second invocation and results
  separately from implementation evidence. If the Owner has not accepted an
  ARC-06 independence criterion, mark it
  `OWNER-OPERATED REPRODUCIBILITY CHECK — INDEPENDENCE NOT ESTABLISHED`;
  unavailable checks are `NOT RUN`, `BLOCKED`, or `INCONCLUSIVE`, as
  applicable.
- ARC-06 remains `PLANNED`/unresolved unless its existing criterion is
  explicitly interpreted and supported by evidence. A second pass by the
  same implementer is not automatically independent.
- Implementation success, solo procedure results, any independent verifier
  findings, Owner approval, CI status, and release authorization are
  represented as separate outcomes.
- The sample is restricted to the two documentation paths above, does not
  execute governed Skills, access secrets, use external services, or expand
  permissions. Any unexpected need for such access stops the task pending
  explicit authorization.
- For the documentation-only sample:
  - `python -B scripts/check_markdown_links.py` must exit 0 with no
    unresolved local Markdown links.
  - `git diff --check` and `git diff --cached --check` must each exit 0.
  Record exact output and exit codes; no CI result is presumed. Tests are not
  required unless code or test instructions change.

## Dependencies and non-applicable gates

- **ARC-02:** Owner disposition of the team-review wording and the applicable
  contract scope is required before execution; this task cannot accept ARC-02
  by itself.
- **ARC-04 / ARC-05 / ARC-10:** Their M2 contracts remain proposed/pending.
  The task is limited to role and workflow documentation and does not claim
  contract acceptance or security enforcement.
- **ARC-06:** The Owner must decide whether the Owner-operated verification
  procedure meets the “verifier other than the implementer” criterion and
  define safeguards before any ARC-06 claim.
- **ADR-M1-01:** Not applicable while the task stays on the current checkout
  with no integration, merge, or publication.
- **ADR-M1-02:** Not applicable while no `skills/` package or provider export
  is changed. If that scope changes, stop and resolve the canonical-source
  decision first.
- **ADR-M1-03:** No validator change is in scope; use only the listed
  existing documentation checks.
- **ADR-M1-06:** No evaluation, approval, or release outcome is in scope.
- **Authorization:** M1 authorization does not cover these paths. Explicit
  task-specific Owner authorization is required and is not granted here.

## Dependencies and stop conditions

**Authorization status: NOT GRANTED by this specification.** Do not begin
until the Project Owner explicitly accepts or revises this proposal, including
the exact two paths, acceptance checks, evidence location, and permitted
operations. The Owner must also decide whether ARC-02's team-review wording
is retained or explicitly revised for solo governance, and record how the
Owner-operated verification procedure relates to ARC-06. This task does not
itself accept ARC-02, ARC-04, ARC-05, ARC-06, or ARC-10, and does not
authorize any gated workflow.

Stop and report `BLOCKED` if the task enters the repository-audit governance
boundary, requires external access or consequential operations, touches
unapproved paths, encounters pre-existing changes in a target path that
cannot be safely preserved, or an acceptance check cannot be reproduced
safely. `skills/implementation/SKILL.md` has pre-existing worktree changes at
the planning baseline and is explicitly out of scope; preserve them. Do not
substitute a second implementation pass for a distinct verification operator
or claim independence without the accepted criterion.

## Estimated effort and risks

- **Effort:** 0.5–1 solo-developer day after Owner review; prerequisite
  architecture decisions are outside this estimate.
- **Primary risk:** A separately executed check may be misrepresented as
  independent despite the same maintainer directing and assessing both passes.
- **Mitigation:** Until the Owner accepts an ARC-06 criterion, label the
  result `OWNER-OPERATED REPRODUCIBILITY CHECK — INDEPENDENCE NOT
  ESTABLISHED`; do not claim independent human review. Record missing
  verification as `NOT RUN`, `BLOCKED`, or `INCONCLUSIVE`.

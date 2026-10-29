---
name: "engineering-handoff"
description: "Use when transferring a bounded engineering task between authorized agents or workflow stages while preserving scope, evidence, dependencies, and authorization boundaries."
---

# Engineering Handoff

## Purpose

Transfer an engineering task between agents or workflow stages with enough verified, self-contained context for the next authorized owner to proceed without guessing. Preserve the user's objective, scope, constraints, evidence, dependencies, and unresolved matters.

The `claude-skills` repository is a provider-neutral Skills and engineering orchestration platform for developing and maintaining SUPER AGI. It is not the SUPER AGI runtime. Preserve the product direction:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

This is architectural context, not evidence that the described system is implemented. Do not treat the 100 modules as independent AI systems.

This Skill describes a handoff procedure; it does not implement a workflow, execute the task, create a handoff record, grant permission, or approve architecture.

## When to Use

Use this Skill when a task is explicitly transferred:

- from planning to separately authorized implementation;
- between agents with different responsibilities;
- between workflow stages;
- from an implementation agent to an identified next owner; or
- to an authorized decision-maker or input owner because work is blocked.

A handoff communicates context and responsibility; it is not task delegation by itself, architectural approval, implementation authorization, acceptance, or proof of task completion. Receiving a handoff does not expand the sender's authority or the user's scope. Do not start a next phase merely because a handoff was prepared or received.

## Sending Procedure

1. **Identify the transfer.** State the original user objective and expected outcome in its actual scope. Identify the sender, intended next owner or role when known, reason for transfer, and explicit handoff boundary. Do not invent an owner.

2. **Confirm the current state.** Summarize work actually performed, files or components actually changed, decisions actually made, and work remaining. Distinguish complete, partial, blocked, and unstarted work. Preserve unfinished work; do not imply that a transfer completes the underlying task.

3. **Restate scope and authority.** Include exact authorized scope and exclusions, repository instructions that apply, prohibited actions, required human approvals, and whether the next action is authorized. Do not infer permission from silence, role assignment, handoff receipt, or prior tool access.

4. **Preserve sources and provenance.** Cite relevant user requirements, repository-relative paths, architecture sources, contracts, decisions, and evidence when available. Identify which statements are verified facts, explicit requirements, approved decisions, assumptions, proposals, or unknowns. Keep source maturity and scope intact.

5. **Record dependencies and readiness.** Identify prerequisites, dependency evidence, task ordering constraints, and inputs or decisions still required. State which work can proceed independently. Mark blocked or conditional work clearly; do not describe an unavailable prerequisite as satisfied.

6. **Report evidence and limits.** List checks actually executed and their observed results, work not performed, unverified claims, failures, and known limitations. Never claim tests passed if they were not run. Do not claim implementation, integration, approval, deployment, or operational readiness without supporting evidence.

7. **Make the handoff portable.** Write context so a compatible agent, provider, terminal, or tool can understand it without hidden conversation history, memory, tool state, permissions, or environment. Prefer clear natural language and repository-relative paths where appropriate. Do not require proprietary orchestration syntax or a specific provider.

8. **Stop at the handoff boundary.** Deliver the handoff to the requested destination or recipient only when authorized and available. Do not create a file, invoke another agent, retry a consequential operation, or start planned work unless separately authorized. If the recipient or transfer mechanism is unavailable, report that limitation.

## Handoff Content

Use only fields relevant to the task. A simple transfer may be a short paragraph; a complex or interrupted task may need explicit sections. Include as supported by evidence:

1. **Objective and expected outcome** — the user's actual requested result.
2. **Transfer and current status** — why the task is being handed off, work completed, and remaining work.
3. **Authorized scope** — permitted files, components, activities, and exact exclusions.
4. **Restrictions and approvals** — prohibited operations, security constraints, required approvals, and authorization state.
5. **Sources and evidence** — applicable instructions, source documents, paths, identifiers, observations, and source maturity.
6. **Prerequisites and dependencies** — verified prerequisites, unresolved dependencies, and sequencing constraints.
7. **Affected surfaces** — files, interfaces, components, contracts, or architecture boundaries, only when known.
8. **Decisions and open questions** — decisions supported by authority, pending decisions, source conflicts, assumptions, and unknowns.
9. **Risks, blockers, and limitations** — observed failures, unavailable tools or providers, and conditions preventing progress.
10. **Deliverables and acceptance conditions** — expected outputs and observable completion criteria.
11. **Next-owner responsibility** — the intended next action and owner when established; state `Unassigned` or `Unresolved` rather than guessing.
12. **Handoff boundary** — what is being transferred now and what must not start without further authorization.

Do not fabricate missing values to complete a format. Do not create a separate template or record unless the active task explicitly requests and authorizes it.

## Evidence and Governance

- Preserve the distinction between **work performed**, **claims supported by inspected evidence**, **checks run and results**, **work not performed**, **unverified items**, **failures**, and **unresolved blockers**.
- Separate user requirements and verified repository facts from approved architectural decisions, assumptions, proposals, and unknowns. Do not silently repair contradictions or convert an assumption into a requirement.
- Follow [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) and applicable repository instructions. Treat architecture proposals according to their recorded maturity; a handoff cannot grant authority or resolve conflicts.
- Preserve the canonical capability statuses in [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md): `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, and `UNKNOWN`. Do not infer a status from a handoff, plan, file's presence, or unsupported claim.
- Keep implementation, verification, approval, deployment, and operational readiness distinct. A handoff is traceability context, not evidence that any of these occurred.
- Protect secrets, credentials, private keys, tokens, and sensitive information. Include only information the recipient is authorized to receive and needs to continue; prefer a safe reference over copying sensitive content.
- Preserve unrelated user changes and unfinished work. Do not overwrite or discard work to make a handoff appear clean or complete.
- Respect explicit Git restrictions. Do not switch branches or fetch, pull, merge, rebase, cherry-pick, commit, or push unless governing instructions explicitly permit the specific operation.
- If instructions conflict, required authority is absent, scope is unclear, or a critical prerequisite is unavailable, pause the affected action and report the blocker. Do not bypass governance, expand scope, or automatically retry destructive or irreversible actions.

## Receiving Procedure

1. Read the handoff and applicable repository instructions, including any instructions governing the affected files.
2. Confirm the user's objective, expected outcome, exact scope, exclusions, restrictions, and acceptance conditions.
3. Identify missing prerequisites, evidence, decisions, permissions, or material ambiguities. Do not treat assumptions as requirements.
4. Confirm that the proposed next action is explicitly authorized and that necessary approvals are present. Pause and request clarification or approval when authority is missing or ambiguous.
5. Continue only within the transferred scope and handoff boundary. Do not begin a later phase or broaden the task because additional work appears useful.
6. Compare the handoff with the current repository or workflow state when authorized and necessary. Report discrepancies, changed state, and evidence gaps rather than silently changing the task.
7. Reuse reliable evidence already supplied; do not repeat work without a reason. Verify freshness or applicability only when needed for the next action.
8. Provide an evidence-grounded completion report or a new handoff that preserves the same scope, provenance, authorization, and unresolved questions.

If work is interrupted or a provider, tool, or prerequisite is unavailable, state the last known verified state, actions not completed, safe continuation point, and blocker. Do not present an interrupted or partial task as complete.

## Status and Onward Reporting

Use status language that accurately reflects the observed transfer and work. These are descriptive reporting labels, not a new repository-wide task lifecycle:

- **Handoff prepared:** context was assembled; delivery or receipt is not implied.
- **Handoff received:** the recipient obtained the context; work is not implied.
- **Work started:** an authorized action actually began.
- **Work partially completed:** some authorized work occurred; identify what remains.
- **Work completed:** the stated task scope was completed; this does not imply verification or approval.
- **Verification performed:** name the check actually run and its observed result.
- **Work blocked:** state the unmet prerequisite, conflict, unavailable capability, or missing authority.
- **Further authorization required:** identify the action that must wait and the approval or clarification needed.

For onward handoff, update the current evidence and repository state, retain the original scope and restrictions, and identify any changed conditions. Do not claim success based solely on a handoff, a plan, or a receiving agent's acknowledgment.

## Relationship to Other Skills

- [Implementation planning](../implementation-planning/SKILL.md) decomposes an authorized objective and its dependencies; this Skill transfers the resulting task context without starting it.
- [Repository implementation](../repository-implementation/SKILL.md) guides separately authorized bounded implementation.
- [Repository audit](../repository-audit/SKILL.md) covers explicitly requested repository investigation; a handoff is not an audit.
- [Architecture decision record](../architecture-decision-record/SKILL.md) guides recording durable architectural decisions; a handoff cannot make or approve one.
- [Skill authoring](../skill-authoring/SKILL.md) guides canonical Skill creation and maintenance; this Skill does not replace it.

These Skills have distinct responsibilities. Use them together only when their work is separately requested and authorized.

## Completion Report

Report concisely:

- whether a handoff was prepared, sent, or received;
- the task and scope transferred;
- the current work status and evidence-backed work performed;
- prerequisites, restrictions, risks, blockers, and unresolved questions;
- checks actually run and their results, plus important work not performed; and
- whether further authorization is required.

Do not claim that a task is implemented, verified, approved, deployed, or operational merely because a handoff exists or was acknowledged. Stop at the requested handoff boundary.

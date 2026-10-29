---
name: "agent-delegation"
description: "Use when deciding whether to delegate bounded engineering work to AI agents and coordinating assignments, dependencies, file ownership, and evidence-grounded results."
---

# Agent Delegation and Coordination

## Purpose and Applicability

Use this Skill to decide whether to delegate explicitly authorized engineering work, define bounded assignments, coordinate their dependencies and ownership, and integrate confirmed outputs within the parent task's scope.

Delegation may help when work separates into independently actionable tasks, when distinct responsibilities can proceed in parallel, or when a bounded task needs specialized context. Keep work with the primary agent when it is small, tightly coupled, requires one continuous trace across components, depends on unresolved decisions, or would cost more to coordinate than to perform directly. Delegate only when a suitable agent and an authorized means to assign work are actually available.

This Skill provides guidance, not an orchestration runtime, provider adapter, permission system, locking mechanism, or approval. Do not claim that agents can execute in parallel, share state, or prevent conflicting edits automatically unless direct evidence establishes that capability.

The `claude-skills` repository is a provider-neutral engineering orchestration platform for building and maintaining SUPER AGI. It is not the SUPER AGI runtime. Preserve the product direction:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

Treat this as architectural context, not proof of implementation. The modules are specialized domains within one intended unified system, not independent AI systems.

## Delegation Readiness

Before assigning work, the coordinating agent must:

1. Identify the user's objective, expected outcome, explicit deliverables, acceptance conditions, and stopping point.
2. Read applicable repository instructions and identify relevant architecture authority, constraints, and security requirements.
3. Define the authorized files, components, and operations, plus explicit exclusions and prohibited actions.
4. Identify prerequisites, actual dependencies, unresolved decisions, material assumptions, and blockers.
5. Confirm the assignment can be understood and completed without the assignee inventing missing requirements or authority.
6. Decide whether work is truly independent or must occur sequentially. A shared topic or preferred order alone is not a dependency.

Do not delegate a task whose essential requirement, permission, interface, or decision authority is missing. Clarify or report the blocker first. A broad objective may be decomposed into proposed bounded assignments only within the user's authorization; decomposition does not approve or authorize additional scope.

## Task Decomposition and Dependencies

- Split work into independently understandable assignments with clear outputs and limited overlap. Keep coupled work together when separation would require guesses or create coordination risk.
- Preserve the parent task's intent, constraints, acceptance conditions, and stop conditions in every assignment. Do not drop a restriction because the assignee is working on a smaller subtask.
- Avoid excessive decomposition. Use the smallest number of assignments that gives a meaningful reduction in context or parallel effort.
- Identify real prerequisites explicitly, explain why the downstream task depends on them, and state what output or evidence satisfies the prerequisite.
- Keep independent tasks independent where practical. Do not represent a suggested order as a dependency.
- Do not let downstream agents rely on unfinished, unconfirmed, or unverified upstream output. Mark dependent work as blocked or conditional until its prerequisite is available.
- Check sequencing for circular dependencies. If a cycle exposes a missing decision or requirement, escalate it rather than concealing it with an arbitrary order.
- Use an existing authoritative dependency notation or task-ID convention if one applies. Otherwise describe dependencies in plain language; do not establish a new canonical notation, ID scheme, lifecycle, or orchestration protocol.
- Do not create or start additional project phases without explicit authorization. A completed assignment does not automatically authorize the next assignment.

## Assigning Responsibility

Assign based on the task's required responsibility, relevant capability, and context that can actually be provided. State one accountable owner for each deliverable when known. Do not assume a particular provider, product, model, tool, or agent role is available or suitable.

Make ownership explicit for:

- the bounded assignment and expected deliverable;
- any files or components the assignee may change;
- dependencies and handoff conditions;
- the coordinator's integration responsibility; and
- any items intentionally left unassigned or unresolved.

Do not assign work to an unavailable agent or imply that assignment means the task has started or completed. If the recipient or delegation mechanism cannot be established, keep the work with the primary agent or report the limitation.

## File Ownership and Conflict Prevention

- Prefer non-overlapping file and component boundaries for concurrent assignments. State exact write ownership where repository evidence and task scope permit.
- Treat exclusive ownership as a coordination instruction, not a technical lock or guarantee. Do not claim that concurrent edits are prevented unless an operational mechanism is evidenced.
- If assignments must touch the same file, serialize the edits or agree explicitly on sections and integration order before work begins. If coordination cannot be confirmed, do not allow overlapping edits to proceed concurrently.
- Before integrating, identify the assignee's actual changes and compare them with existing repository state. Preserve unrelated tracked and untracked work.
- Never silently overwrite, discard, revert, or absorb another agent's or user's changes. Stop and surface a conflict when ownership or state is ambiguous.
- Do not modify adjacent documentation, indexes, registries, configuration, or other files outside the explicit assignment merely to make integration convenient.

## Delegation Instructions

Every assignment must give the receiving agent enough portable context to act without relying on hidden chat history, memory, tool state, permissions, or environment. Include, as applicable:

- **Objective:** the requested bounded outcome and why it belongs to the parent task.
- **Allowed scope:** authorized files, components, and permitted operations.
- **Exclusions:** prohibited files, behaviors, and follow-on phases.
- **Expected deliverable:** concrete output and observable completion conditions.
- **Relevant context:** verified facts, source references, approved decisions, and required repository instructions.
- **Dependencies:** prerequisites, required inputs, sequencing, and how completion is confirmed.
- **Evidence expectations:** what changes, command results, checks, or limitations to report.
- **Stopping conditions:** ambiguity, conflicts, missing authority, errors, or scope expansion that require pausing.
- **Authorization:** explicit statement of what is authorized and which actions require separate approval.

When the repository's implementation-only guidance applies, keep the assignment to its authorized bounded implementation. Do not silently add tests, audit, review, verification, documentation, deployment, or another phase when outside scope or expressly prohibited. A plan or assignment does not authorize implementation.

## Output Integration

1. Receive the assignee's report and distinguish work they confirm performing from recommendations, assumptions, and unresolved matters.
2. Do not claim a file was created, modified, checked, or integrated unless the responsible agent confirms it or the coordinator directly observes it within authorized scope.
3. Preserve relevant source paths, decisions, evidence, and limitations. Do not convert an assignee's proposal into an approved architecture decision.
4. Confirm that the reported result stays within assignment and parent-task scope. If it does not, do not incorporate unauthorized changes; preserve them and escalate the scope conflict.
5. Integrate outputs only when integration is within the coordinator's authorization. Avoid unrelated edits and avoid repeating work already supported by reliable, applicable evidence.
6. Report integration as a distinct action. A returned response, proposed patch, or completed assignment is not proof that changes were applied to the primary worktree.

Do not treat an agent's success-shaped summary as sufficient evidence for consequential claims. Attribute claims to the agent's report when not independently observed, and identify what remains unverified.

## Failures, Conflicts, and Escalation

- **Missing context or unclear requirements:** pause the affected assignment and request clarification; do not invent a requirement.
- **Conflicting instructions or decisions:** preserve the conflict and its sources, do not choose an authority silently, and escalate through the applicable governance path.
- **Agent or tool unavailable:** report the limitation. Do not claim delegation occurred or switch to an unauthorized mechanism.
- **Partial completion or interruption:** record the last confirmed state, completed and remaining work, changes made, failures, and safe continuation point.
- **Unexpected scope expansion:** identify the added work, why it is outside authorization, and whether it is essential or optional. Continue separable authorized work; request approval for the expansion.
- **Blocked dependency:** keep downstream work blocked or conditional until the prerequisite is confirmed. Do not treat intent, assignment, or a proposed output as completion.
- **Repository state or file ownership conflict:** stop overlapping edits, preserve existing work, and request coordination rather than overwriting another contributor's changes.
- **Insufficient authorization:** pause the affected action and seek the required user or human approval. A handoff or agent response never supplies missing authorization.

Do not automatically retry destructive or irreversible actions, widen permissions, or expand the task to bypass a blocker.

## Security and Operational Boundaries

- Follow [`AGENTS.md`](../../AGENTS.md), [`CLAUDE.md`](../../CLAUDE.md), and applicable repository instructions and approved architecture sources.
- Respect source-of-truth, system boundaries, existing contracts, and the maturity of architecture decisions. Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) and [`SYSTEM_BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md) when relevant.
- Apply least privilege and human-approval requirements. Protect secrets, credentials, private keys, tokens, and sensitive information; share only the minimum context the recipient is authorized to receive.
- Do not infer operational capability from documentation or a declared interface. Preserve the canonical capability statuses in [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) and report only statuses supported by evidence.
- Keep implementation, validation, approval, deployment, and operational readiness distinct. Delegation instructions do not establish that any of these occurred.
- Preserve user work and current repository state. Do not change branches, fetch, pull, merge, rebase, cherry-pick, commit, or push unless explicitly authorized by applicable instructions.
- Do not perform destructive or irreversible operations without the required explicit authorization. Stop when scope, authority, security, or repository state makes an action unsafe.

These are coordination instructions, not evidence that shared state, multi-agent execution, authorization controls, or conflict-prevention tooling is implemented.

## Completion and Handoff

Require each assignee to provide a concise, evidence-grounded report stating:

- the assigned objective and scope;
- what was actually performed and any files changed;
- deliverables returned and relevant source references;
- checks actually run and observed results, or checks not performed;
- failures, limitations, assumptions, and unresolved blockers; and
- work remaining or authorization required.

The coordinator must distinguish assignment prepared, assignment received, work started, work partially completed, work completed, validation performed, and work blocked. These are descriptive reporting labels, not a repository-wide lifecycle unless an authoritative source establishes one.

Do not equate implementation with validation, or report successful integration, approval, deployment, or operational readiness without evidence. Stop after the assigned deliverable and parent task boundary; do not automatically start another task.

## Related Skills and Sources

- [Task scope control](../task-scope-control/SKILL.md) — maintains the authorized change boundary.
- [Implementation planning](../implementation-planning/SKILL.md) — decomposes objectives and dependencies.
- [Repository implementation](../repository-implementation/SKILL.md) — guides authorized bounded implementation.
- [Engineering handoff](../engineering-handoff/SKILL.md) — transfers task context and evidence.
- [Evidence reporting](../evidence-reporting/SKILL.md) — supports truthful, traceable reporting.
- [Architecture decision record](../architecture-decision-record/SKILL.md) — documents durable decisions without granting approval.
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Architecture traceability](../../architecture/ARCHITECTURE-TRACEABILITY.md)

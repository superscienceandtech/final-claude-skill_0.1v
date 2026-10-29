---
name: "task-scope-control"
description: "Use when defining or maintaining the authorized boundaries of an engineering task, preventing unrelated changes, and handling scope changes or blockers."
---

# Task Scope Control

## Purpose

Identify, preserve, and enforce the authorized boundaries of one engineering task from intake through completion. Keep work aligned with the user's actual objective, applicable repository instructions, permitted files and operations, and stated stopping point.

The `claude-skills` repository is a provider-neutral Skills and engineering orchestration platform for building and maintaining SUPER AGI. It is not the SUPER AGI runtime. Preserve the product direction:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

This direction is architectural context, not evidence that the described system is implemented. Do not treat the 100 modules as independent AI systems.

This Skill is guidance, not an authorization mechanism, security boundary, or execution control.

## Define the Authorized Scope

Before acting, identify from the user's request and applicable repository instructions:

- **Objective:** the requested outcome, without adding inferred goals.
- **Deliverables:** the specific files, behavior, or outputs requested.
- **Authorized targets:** exact files, directories, components, or subsystems where stated.
- **Permitted operations:** actions allowed by the request and governing instructions.
- **Exclusions:** explicitly excluded files, activities, or phases.
- **Completion conditions:** evidence or observable conditions that define when the task is done.
- **Restrictions and stop conditions:** required approvals, prohibited operations, blockers, and the task boundary.

Separate explicit requirements from inferred preferences, optional improvements, and agent-generated suggestions. A suggestion or apparent improvement is not user authorization.

If the user limits work to one file, component, or activity, treat that as a firm boundary. For planning-only, documentation-only, or no-tests tasks, do not implement code, expand documentation, or run tests unless separately authorized. Do not begin a later phase or subsequent task after completing the stated objective.

## Preserve Scope During Work

1. Follow `AGENTS.md`, `CLAUDE.md`, and any applicable instructions governing the requested target.
2. Keep changes necessary to the requested deliverable. Do not add cleanup, refactoring, adjacent documentation, index, registry, configuration, or dependency changes merely for convenience.
3. Identify the exact authorized target before editing. If it already exists and the task does not authorize overwriting or updating it, preserve it and ask or report the conflict.
4. Preserve unrelated tracked and untracked work. Do not overwrite, delete, rename, or reinterpret existing user changes to make the task easier.
5. Recheck scope when new files, dependencies, operations, or decisions appear necessary. Do not silently expand the target set.
6. Stop when the requested deliverables and completion conditions are met. Do not automatically start related, dependent, or later tasks.

Respect operation restrictions imposed by the user or repository instructions. These may include not running tests, not conducting a separate audit or review phase, and not switching branches, fetching, pulling, merging, rebasing, cherry-picking, committing, pushing, deploying, or performing destructive actions. These restrictions apply when imposed; do not describe them as universally prohibited where no applicable restriction exists. Any required separate approval remains necessary.

## Scope Changes and Unexpected Work

When an additional change or operation appears necessary:

1. Identify the requirement, dependency, conflict, or blocker.
2. Explain why the additional work is outside the current authorized scope.
3. Separate essential work needed to complete the authorized task from optional improvements.
4. Ask for clarification or approval when the scope must change or authority is unclear.
5. Continue only with separable work that remains authorized; leave optional out-of-scope work untouched.

Do not stop unrelated in-scope work solely because an optional enhancement was discovered. If the essential in-scope deliverable can be completed independently and safely, complete it and report the excluded enhancement. If the missing work is a genuine prerequisite, stop the dependent action and report the blocker.

Do not create a new file, modify a neighboring artifact, install a dependency, or change task type as an unapproved workaround. If repository state unexpectedly conflicts with the request, preserve that state and report the observed conflict rather than silently resolving it.

## Architecture and Governance Boundaries

- Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) and relevant approved decisions when they govern the task. Preserve the distinction between approved architecture, proposal, unresolved decision, and implementation evidence.
- Respect [`SYSTEM_BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md), existing system contracts, and authorization boundaries relevant to the requested scope. Do not turn an apparent architectural improvement into permission to change architecture or its governing documents.
- Keep open decisions open unless an authorized decision-maker resolves them. Do not invent approval, select a winner in a source conflict, or expand scope to bypass a governance blocker.
- Protect secrets and sensitive information. Respect least privilege, security requirements, human approval, and restrictions on consequential or irreversible operations.
- Preserve the canonical capability-status vocabulary in [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md): `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, and `UNKNOWN`. Do not infer a capability or operational status from a document, interface, plan, or file's presence.
- Use [`ARCHITECTURE-TRACEABILITY.md`](../../architecture/ARCHITECTURE-TRACEABILITY.md) as relevant for evidence and relationships; links or declarations do not establish implementation or authority.

When instructions conflict, do not invent authorization or silently choose between authoritative requirements. Identify which instructions conflict, avoid the affected action, and request clarification or report the blocker. Continue independent in-scope work only if it remains safe and valid.

## Completion Reporting

Report concisely and accurately:

- the requested objective and authorized scope;
- work actually completed within that scope;
- files changed, using actual paths;
- checks and operations actually performed, and any restrictions observed;
- deviations, failures, blockers, or unresolved scope conflicts;
- additional or optional work intentionally left undone; and
- any approval or clarification still required.

Do not claim full completion when a required in-scope deliverable remains incomplete. Do not imply that excluded work was performed, or that a plan, file, interface, or successful command proves operational behavior.

## Relationship to Other Skills

- [Implementation planning](../implementation-planning/SKILL.md) decomposes authorized objectives and sequences dependent tasks; this Skill preserves the authorized boundary of that plan.
- [Repository implementation](../repository-implementation/SKILL.md) guides separately authorized bounded implementation; this Skill helps prevent scope expansion during that work.
- [Engineering handoff](../engineering-handoff/SKILL.md) transfers task context between owners; this Skill helps preserve scope and authorization across the transfer.
- [Evidence reporting](../evidence-reporting/SKILL.md) supports evidence-based reporting of actual work and limitations; this Skill defines which work was in scope.
- [Repository audit](../repository-audit/SKILL.md) guides explicitly requested repository investigation; this Skill does not authorize an audit.

These Skills have distinct responsibilities. Use them together only when their respective work is requested and authorized.

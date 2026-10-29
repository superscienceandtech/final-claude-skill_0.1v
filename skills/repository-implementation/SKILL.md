---
name: "repository-implementation"
description: "Use when implementing one explicitly requested, bounded engineering task in an existing repository, including changes to existing code or configuration within authorized scope."
---

# Repository Implementation

## Purpose

Implement one clearly requested, bounded engineering task inside an existing repository. Make a minimal, coherent change that follows the repository's existing interfaces and conventions, preserves unrelated work, and reports what was actually changed.

The `claude-skills` repository is the provider-neutral engineering platform for building and maintaining SUPER AGI. It is not the SUPER AGI runtime. Preserve the product direction: one Super AGI, one Unified Brain, 100 specialized intelligence modules, dedicated navbars/workspaces, and shared universal infrastructure. Do not treat the modules as 100 independent AI systems, or assume every planned component exists or operates.

This Skill is an implementation procedure, not an architecture overview, repository audit, testing Skill, deployment process, approval, or execution sandbox.

## When to Use

Use this Skill when the task is to:

- implement one clearly specified feature, fix, or engineering change;
- modify existing source code or configuration within authorized scope;
- create a specifically requested implementation artifact; or
- integrate with an existing interface or shared infrastructure when the repository provides sufficient evidence for its behavior and authority.

Do not use it to initiate repository-wide refactoring, resolve architecture decisions, perform unrelated cleanup, perform destructive operations, start testing or deployment phases, or expand the task beyond its explicit boundary. This Skill does not itself authorize any of those activities.

## Required Inputs and Scope

Before editing, identify:

- the requested outcome and observable completion criteria;
- exact files or directories authorized for modification, if specified;
- applicable repository instructions and relevant source files;
- established interfaces and architecture decisions that govern the change;
- explicit exclusions and stop conditions; and
- dependencies or decisions that remain unresolved.

If a critical requirement, interface, permission, or authority is missing and the implementation cannot be completed safely, state the blocker and stop. Do not invent a design, assume an approval, or expand scope to work around it.

## Implementation Procedure

1. **Read repository instructions.** Follow `AGENTS.md`, `CLAUDE.md`, and any applicable instructions governing the files in scope.

2. **Identify the bounded outcome.** Confirm the requested behavior, allowed files, explicit exclusions, success criteria, and stopping point. Preserve pre-existing work.

3. **Locate relevant sources and decisions.** Inspect the source files and established interfaces needed for the change. Consult architecture documents and decision records as relevant; distinguish explicitly approved decisions from proposals and unresolved questions.

4. **Choose the smallest coherent change.** Determine the minimal implementation that meets the request within authorized scope. Do not turn the task into a general plan, audit, refactor, or architecture redesign.

5. **Reuse evidenced interfaces and shared components.** Reuse existing behavior only when repository evidence establishes the relevant interface and implementation. Do not assume a planned service, library, registry, or integration is available because it is documented.

6. **Implement the requested behavior directly.** Follow the established language, style, error-handling, and compatibility conventions for the affected code. Use explicit interfaces and surface relevant errors; avoid fake success responses, silent defaults, speculative abstractions, and unnecessary dependencies.

7. **Preserve boundaries and existing behavior.** Change only what is required. Keep provider-specific behavior outside provider-neutral components unless the task explicitly requires otherwise. Respect established contracts, data ownership, security restrictions, permissions, and human-approval boundaries.

8. **Stop when the implementation task is complete.** Do not run tests or begin testing, review, deployment, or another implementation phase under this Skill. If the task cannot be completed within scope, stop and report the blocker rather than extending it.

9. **Report facts.** Summarize the delivered behavior, actual changed files, dependencies, limitations, and checks not performed. Do not claim execution, validation, integration, or operational readiness without evidence.

## Architecture and Integration Discipline

Keep these distinctions explicit:

- **Established decision versus proposed architecture:** implement against established, applicable decisions. Do not silently convert a proposal into an accepted decision.
- **Existing interface versus conceptual interface:** use a documented interface only when the repository shows that it exists and is relevant; a proposed interface is not an implementation contract.
- **Available shared infrastructure versus planned infrastructure:** reuse a shared component only when its existence and behavior are evidenced.
- **Actual integration versus placeholder or mock:** identify mock behavior honestly; a stub does not prove a real dependency works.
- **Implemented behavior versus unimplemented capability:** report only the narrow behavior supported by code and observed evidence.
- **Local change versus end-to-end operation:** a local implementation does not prove an integrated workflow or complete system operates.

Do not infer operational implementations of the Master Core, Universal Intelligence Fabric, module registry, context engine, collaboration engine, Model Gateway, or any other planned component from architecture documentation alone. Do not introduce a new architecture decision without the required authority. Record unresolved dependencies and stop when they prevent a safe implementation.

Preserve the canonical capability-status vocabulary and meanings defined in [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md): `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, and `UNKNOWN`. Do not assign or upgrade a capability status merely because code was changed.

## Security and Repository Protection

- Follow the user's explicit scope and all applicable repository instructions.
- Never expose secrets, credentials, tokens, private keys, or sensitive user data in source, logs, or reports.
- Do not bypass authorization, repository protections, security policy, or human-approval boundaries.
- Do not perform destructive or irreversible actions unless separately and explicitly authorized.
- Avoid unrelated file modifications and preserve existing tracked and untracked work.
- Do not switch branches or fetch, pull, merge, rebase, cherry-pick, commit, or push unless separately authorized.
- Do not run tests under this Skill. Report them as not run; do not imply success.
- Do not create additional files unless the active task explicitly requests them.
- Stop and report a blocker when the requested scope conflicts with higher-priority repository instructions or requires unavailable authority.
- Do not start another task or phase after completing the requested change.

## Completion Report

Provide a concise, evidence-based report covering:

1. **Requested outcome:** what was asked and what behavior was actually changed.
2. **Files:** exact files created or modified.
3. **Implementation:** behavior implemented and relevant existing interfaces or dependencies used.
4. **Limitations:** unresolved dependencies, blockers, and behavior not demonstrated.
5. **Tests:** state that tests were not run under this Skill.
6. **Git operations:** state whether any history operations occurred; do not perform them without separate authorization.

Do not claim successful execution, validation, integration, deployment, security enforcement, or operational readiness without direct evidence.

## Relationship to Other Skills

- [Repository audit](../repository-audit/SKILL.md) covers bounded repository inspection and audit reporting, not implementation.
- [Architecture documentation](../architecture-documentation/SKILL.md) covers architecture-documentation tasks, not runtime implementation.
- [Skill authoring](../skill-authoring/SKILL.md) covers creating and maintaining canonical Skills.
- This Skill covers bounded implementation changes only.

For repository-wide architecture context, consult:

- [Skills overview](../README.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Product constitution](../../architecture/PRODUCT_CONSTITUTION.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [Architecture decisions](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open decisions](../../architecture/OPEN-DECISIONS.md)
- [Architecture traceability](../../architecture/ARCHITECTURE-TRACEABILITY.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Module contract](../../architecture/MODULE-CONTRACT.md)

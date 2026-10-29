---
name: "engineering-implementation-planning"
description: "Use when decomposing approved engineering requirements into repository-grounded, dependency-aware implementation tasks or bounded implementation prompts."
---

# Engineering Implementation Planning

## Purpose

Turn approved engineering requirements into a small, evidence-based set of implementation tasks that an authorized coding agent can execute without guessing. When requested, produce a self-contained implementation prompt for one such task.

This Skill organizes implementation work; it does not approve requirements or architecture, grant implementation authority, execute tasks, or establish that a capability works. Keep planning separate from implementation, verification, acceptance, and release.

The `claude-skill_sonjoy` repository is a provider-neutral Skills and engineering-orchestration platform for developing SUPER AGI, not the SUPER AGI runtime. Preserve the target-system direction of one unified platform with specialized intelligence modules and shared infrastructure. Treat that direction and any proposed architecture as intent unless applicable approval and implementation evidence establish otherwise.

## When to Use

Use this Skill when a user asks to:

- decompose an approved feature, change, or multi-phase objective into implementation tasks;
- sequence tasks around evidenced dependencies and prerequisites;
- identify concrete implementation targets from repository evidence; or
- generate a bounded implementation prompt from an agreed task.

Do not use it to conduct an unrestricted repository audit, independently approve or resolve architecture, invent requirements, implement code, perform testing or deployment, or manage a project beyond the requested engineering decomposition. Use the existing [implementation-planning Skill](../implementation-planning/SKILL.md) for broader planning needs; this Skill specializes in actionable task decomposition and prompt preparation. Neither Skill authorizes work by itself.

## Inputs and Boundaries

Identify the following before planning:

- The objective and the source of each requirement.
- Which requirements are approved for the planning scope and the evidence for that approval, where approval is required.
- Expected outcomes and acceptance conditions, if supplied.
- Applicable repository instructions, architecture constraints, contracts, and relevant implementation context.
- Authorized repositories and targets, permitted operations, exclusions, and stopping point.
- Known dependencies, platform or compatibility requirements, and unresolved decisions.

Distinguish a user's explicit request from approval of an architectural choice. Do not treat a proposal, roadmap, example, Skill, registry entry, or implementation behavior as approval evidence. If authority or approval is unresolved, identify it; do not silently make the proposed choice a requirement.

Ask for clarification when a missing or conflicting input materially affects correctness, authority, scope, or task sequencing. If the uncertainty is not blocking, state a bounded assumption or recommendation separately from approved requirements. Do not present assumptions as facts.

## Procedure

1. **Restate the authorized outcome.** Summarize the objective, intended result, acceptance conditions, allowed scope, exclusions, and where planning must stop. Separate planning authorization from implementation authorization.

2. **Establish requirement authority.** For each consequential requirement, record its source and whether it is an explicit approved requirement, an applicable approved architectural constraint, an assumption, a recommendation, or an unresolved question. Preserve the source's status and scope. Consult the repository's [source-of-truth guidance](../../architecture/SOURCE_OF_TRUTH.md), [architecture decisions](../../architecture/ARCHITECTURE-DECISIONS.md), and [open decisions](../../architecture/OPEN-DECISIONS.md) when they apply. Do not resolve a conflict by preferring whichever source is newer, more detailed, or implemented.

3. **Decompose requirements.** Derive only what follows from the approved objective:
   - implementation objectives and intended user or system behavior;
   - functional requirements and relevant non-functional constraints;
   - observable acceptance criteria;
   - dependencies, prerequisites, and integration boundaries;
   - explicit exclusions and constraints; and
   - unresolved questions, assumptions, and risks.

   Keep each criterion specific enough to determine what evidence could satisfy it. Do not invent numerical thresholds, interfaces, file locations, security guarantees, or compatibility promises.

4. **Inspect relevant repository evidence.** Follow [AGENTS.md](../../AGENTS.md), applicable local instructions, and the sources relevant to this objective. Inspect existing contracts, code, tests, configuration, and documentation as needed to determine where the requirement belongs and what already exists. Keep discovery proportional to the task; do not turn planning into a repository-wide audit.

   Classify findings precisely:
   - **Existing implementation:** concrete behavior is present; cite the relevant source and distinguish observed behavior from unverified claims.
   - **Partially implemented:** some required behavior exists, with specific gaps identified.
   - **Documentation-only:** intent or a declaration exists without evidence of corresponding operational behavior.
   - **Adapter-ready:** a usable adapter boundary is evidenced, but this alone does not demonstrate a working provider, tool, or end-to-end integration.
   - **Mocked or experimental:** identify the simulated or exploratory scope and what remains unproven.
   - **Unknown:** available evidence is insufficient to determine implementation state.

   Use capability statuses only as defined in [CAPABILITY-STATUS.md](../../architecture/CAPABILITY-STATUS.md): `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, and `UNKNOWN`. Do not add aliases or infer a status from a file, interface, manifest, registry entry, successful compilation, or documentation mention alone.

5. **Find the actual gap.** Compare approved requirements with evidenced existing behavior and interfaces. Reuse an existing implementation or contract when its relevance and behavior are supported by repository evidence. Identify missing or partial behavior without duplicating functionality. If necessary targets, dependencies, permissions, or decisions cannot be established, mark the task blocked or request clarification rather than guessing.

6. **Build the dependency graph.** Divide only the authorized objective into the smallest meaningful tasks that each deliver a coherent, reviewable result. Record real prerequisites, such as a required decision, contract, interface, or completed task. Keep independent tasks independent; do not imply a dependency merely from list order. Mark tasks conditional or blocked when their prerequisites are unresolved. Sequence tasks topologically where dependencies exist.

7. **Check task boundaries.** Ensure each task has one clear objective and a bounded target. Avoid unrelated cleanup, duplicate functionality, unnecessary abstractions, speculative infrastructure, broad multi-file rewrites, and automatic follow-on phases. Split a task when it combines independently deliverable outcomes or cannot be completed and assessed within a coherent scope.

8. **Prepare an implementation prompt when requested.** Generate a prompt for one bounded task only. Make it self-contained and include:
   - the task identifier and title;
   - approved objective and supporting requirement or contract sources;
   - exact intended target files or directories when repository evidence supports them;
   - expected behavior or artifact and observable acceptance criteria;
   - actual prerequisites and dependencies;
   - explicit exclusions and the stop condition;
   - relevant repository conventions and instructions;
   - verification requirements only when authorized by the task and applicable repository instructions; and
   - truthful completion-report requirements.

   If the exact target is uncertain, state what evidence is missing and request clarification or identify the target as tentative. Do not prescribe a guessed path as certain. Direct the implementer to preserve unrelated tracked and untracked work and not to claim completion before the work and required evidence exist. Do not include later tasks as work to execute.

9. **Label plan maturity.** Label a plan or proposed task breakdown as proposed unless explicit approval evidence covers that plan and scope. A plan does not approve architecture, authorize implementation, or demonstrate implementation status. Identify approvals still required before dependent work can begin.

## Required Task Record

For each task, provide:

1. **Identifier and title** — unique within the plan and concise.
2. **Objective** — the specific result this task is to achieve.
3. **Primary target** — the evidenced file, component, or bounded area; qualify uncertainty.
4. **Expected behavior or artifact** — the concrete deliverable.
5. **Dependencies** — actual prerequisites, or `None` when independent.
6. **Scope exclusions** — related work explicitly left out.
7. **Acceptance criteria** — observable conditions appropriate to the requirement.
8. **Completion evidence** — implementation locations, checks or observations required by scope, and limitations to report.

For a small, self-contained objective, use one task rather than creating decomposition for its own sake. If an essential field cannot be responsibly established, record the gap and whether clarification blocks planning.

## Repository and Git Safety

Unless the user and applicable instructions explicitly authorize otherwise, plans and generated prompts must preserve these boundaries:

- Do not switch branches or fetch, pull, merge, rebase, or cherry-pick.
- Do not stage or unstage, commit, or push.
- Do not reset, clean, discard, or overwrite existing work.
- Preserve unrelated tracked and untracked files.
- Do not install packages, change dependencies, or activate external services unless explicitly in scope and authorized.
- Do not expose secrets, credentials, tokens, private keys, or sensitive data.
- Do not perform destructive, irreversible, externally visible, or consequential actions without required human approval.
- Never recommend `git add .` as a default staging instruction.

These are prompt defaults, not a substitute for the active user's scope or repository-specific requirements. If they conflict with a higher-priority instruction or required approval is missing, surface the conflict and do not direct the affected action.

## Verification and Completion Evidence

Do not require a separate test, audit, or validation phase in every plan or implementation prompt. Determine verification from the explicit task scope, repository instructions, available prerequisites, and required acceptance evidence. If a check is prohibited, unavailable, unsafe, or not requested, state that it is not part of the task or was not performed. Never represent a planned command as executed.

For each task, specify the evidence needed to substantiate its acceptance criteria. Where relevant, evidence should identify the implementation location, behavior actually observed, exact checks performed and their results, dependencies exercised or not exercised, known limitations, and unresolved blockers. Keep code presence, interface availability, compilation, tests, integration, approval, and production readiness distinct.

## SUPER AGI and Provider-Neutral Application

When applying this Skill to SUPER AGI or another modular platform:

- Treat it as one unified platform with specialized modules sharing infrastructure, not as a collection of independent products.
- Respect approved module contracts and evidenced dependencies. Share memory, knowledge, context, tools, or agent infrastructure only where an applicable approved architecture establishes those boundaries.
- Plan incremental slices that produce coherent results within the unified system; do not assume target modules or shared services are implemented merely because architecture documents describe them.
- Separate proposed target architecture from existing implementation and verified behavior.
- Keep canonical requirements, task structures, and planning logic independent of provider-specific syntax, models, IDEs, orchestration frameworks, and proprietary APIs.
- Place provider-specific adaptations outside the canonical planning method and only within separately authorized scope.

## Output and Completion Report

Adapt the output detail to the request. A multi-task plan should include the objective, authority and requirement sources, repository findings relevant to the gap, task records, dependency order, assumptions, risks, unresolved questions, and approval or authorization boundaries. Provide implementation prompts only when requested or clearly included in the requested deliverable.

Report separately and factually:

- **Planned:** objectives and task breakdown actually produced, including plan maturity.
- **Implemented:** work actually performed, if separately authorized; otherwise state that implementation was not performed.
- **Files:** files actually changed by the planning activity or implementation, as applicable.
- **Commands and verification:** exact commands actually executed and observed results, or state that none were run.
- **Limitations:** failures, unavailable evidence, platform constraints, and unresolved issues.
- **Not performed:** explicitly excluded implementation, verification, approval, or later tasks.

Do not claim a capability is implemented, tested, approved, integrated, secure, compatible, or production-ready without evidence appropriate to that claim. Stop after the requested planning deliverable; do not automatically begin implementation or a subsequent task.

## Related Sources

- [Implementation planning](../implementation-planning/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Architecture decisions](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open decisions](../../architecture/OPEN-DECISIONS.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Module contract](../../architecture/MODULE-CONTRACT.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)
- [Specification-to-implementation workflow](../../workflows/spec-to-implementation/README.md)

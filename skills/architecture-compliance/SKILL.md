---
name: "architecture-compliance"
description: "Use when applying relevant documented architecture, system boundaries, and governance constraints to an explicitly authorized engineering task."
---

# Architecture Compliance and Implementation Alignment

## Purpose and Applicability

Apply relevant, evidenced architecture constraints while carrying out an explicitly authorized engineering task. Use this Skill to identify which documented requirements materially govern the task, preserve system boundaries, and surface conflicts or unresolved decisions without expanding implementation scope.

This Skill is not a standalone architecture audit, architecture approval process, or claim of automated compliance enforcement. Do not conduct a separate audit, review, or testing phase unless the active task authorizes it. The `claude-skills` repository is the provider-neutral engineering orchestration platform for building and maintaining SUPER AGI; it is not the SUPER AGI runtime.

Preserve the product direction:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

This direction is architectural context, not evidence that the described system is implemented. The 100 modules are specialized domains within one intended unified system, not 100 independent AI products.

## Architecture Sources and Authority

1. Follow the active user request and applicable repository instructions, including [`AGENTS.md`](../../AGENTS.md) and [`CLAUDE.md`](../../CLAUDE.md).
2. Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) to understand architecture authority, document classification, and required approval evidence.
3. Read only architecture documents and decisions relevant to the assigned task. This may include [`SYSTEM_BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md), [`ARCHITECTURE-PRINCIPLES.md`](../../architecture/ARCHITECTURE-PRINCIPLES.md), applicable contracts, and the decision registers.
4. Apply an architectural decision as binding only when repository evidence establishes its approval, scope, and applicability. Treat proposals, drafts, examples, recommendations, and proposed conventions according to their recorded maturity.
5. If authority, applicability, or interpretation is unclear, record the sources and ambiguity, seek clarification when needed, and avoid actions that depend on an invented resolution.

Do not impose a new precedence rule among sources. Follow explicit governance and approved decisions within their evidenced scope. If source documents conflict and no applicable authority resolves the conflict, preserve it as unresolved rather than silently selecting a winner.

## Apply Architecture to the Authorized Task

1. **Restate the task boundary.** Identify the requested outcome, deliverables, permitted files and operations, explicit exclusions, and completion conditions. Follow [`task-scope-control`](../task-scope-control/SKILL.md) and [`repository-implementation`](../repository-implementation/SKILL.md) where applicable.

2. **Select material constraints.** Identify only those architecture requirements, boundaries, and contracts that affect the assigned outcome. Consult [`ARCHITECTURE-TRACEABILITY.md`](../../architecture/ARCHITECTURE-TRACEABILITY.md) when source relationships or evidence links help establish applicability.

3. **Classify what you find.** Distinguish:
   - approved requirements and decisions supported by explicit evidence;
   - repository instructions that govern the work;
   - documented design intent or proposed architecture;
   - recommendations and proposed conventions;
   - actual implementation facts supported by inspected artifacts or behavior; and
   - unresolved decisions, incomplete mappings, assumptions, and unknowns.

4. **Implement only within scope.** Make the smallest change that satisfies the authorized deliverable while respecting applicable architecture. Do not expand the task because adjacent architecture work appears desirable. If a necessary file, dependency, interface, or decision falls outside the authorization, identify the need and request approval or clarification; proceed only with separable authorized work.

5. **Preserve boundaries and responsibility.** Use [`SYSTEM_BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md) and relevant existing contracts when they materially apply. Distinguish the engineering platform from the SUPER AGI runtime, canonical behavior from provider-specific adapters, shared infrastructure from planned concepts, and existing interfaces from conceptual ones. Do not invent missing APIs, layer mappings, plane responsibilities, or runtime behavior.

6. **Check cross-domain impact proportionately.** Consider layer, plane, infrastructure, module-contract, context, collaboration, model-gateway, and governance documents only when they materially affect the task. Reuse relevant established boundaries; do not restate every architecture document or introduce speculative abstractions.

7. **Stop at the task boundary.** Respect restrictions on files, tests, audit, review, Git operations, deployment, and later phases. Preserve existing tracked and untracked work. Do not automatically start subsequent tasks.

## System Boundaries and Capability Claims

- Treat architecture text as design intent unless approval or implementation evidence establishes more. A directory, file, interface, contract, prototype, mock, or adapter declaration does not by itself prove operational behavior.
- Keep documented architecture, planned capabilities, adapters, prototypes, mocked behavior, implemented functionality, and end-to-end operation distinct.
- Use the capability vocabulary in [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) when making an applicable capability claim: `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, and `UNKNOWN`.
- Assign or repeat a capability status only when the evidence and scope support it. Do not label a capability implemented because code or documentation exists, or because a local component compiles or responds.
- Do not infer that the Master Core, Universal Intelligence Fabric, registry, context engine, collaboration engine, Model Gateway, provider, tool, or other conceptual subsystem is operational without direct, relevant evidence.
- Describe only mappings and behavior established by applicable sources. When evidence is incomplete, say what is known, what remains unverified, and what cannot be concluded.

## Conflicts and Unresolved Decisions

When instructions or architecture sources conflict, a required decision is undocumented, mappings are incomplete, or a proposed requirement is incompatible with an established boundary:

1. Identify the conflicting requirements or missing decision and cite the actual relevant sources.
2. Determine whether an explicit, applicable approved decision resolves the issue; do not infer authority from a document's location or wording alone.
3. Separate the work that remains safely possible within scope from the work that depends on resolution.
4. Consult [`OPEN-DECISIONS.md`](../../architecture/OPEN-DECISIONS.md) and [`ARCHITECTURE-DECISIONS.md`](../../architecture/ARCHITECTURE-DECISIONS.md) where relevant, while preserving their documented maturity and conventions.
5. Pause the affected change and request authorized clarification when the conflict materially changes behavior, scope, or risk. Continue only independent in-scope work.
6. Record the unresolved matter in the completion report. Do not create an ADR, edit architecture registers, change an architecture decision, or expand the task unless explicitly authorized.

Do not silently resolve human-governed decisions, invent approval authority, or bypass a blocker by implementing an unsupported assumption.

## Security, Scope, and Governance

- Follow the active task's explicit scope and applicable repository instructions. Modify only authorized files and preserve unrelated user work.
- Apply relevant security expectations from [`SECURITY-GOVERNANCE.md`](../../architecture/SECURITY-GOVERNANCE.md), including least privilege, sensitive-data protection, and human approval for consequential actions. This document describes architecture guidance; it does not itself prove controls are operational.
- Never expose secrets, credentials, private keys, tokens, or unnecessary sensitive information.
- Do not perform destructive or irreversible actions without explicit authorization.
- Do not switch branches or fetch, pull, merge, rebase, cherry-pick, commit, or push unless explicitly authorized by applicable instructions.
- Do not add a separate audit, review, or testing phase when it is outside scope or prohibited. Do not begin follow-up work automatically.
- Treat provider-specific configuration and behavior as separate from canonical provider-neutral requirements unless the active task and applicable architecture explicitly authorize otherwise.

## Completion and Communication

Report concisely:

- the authorized task and files actually changed;
- architectural constraints that materially affected the implementation;
- relevant evidence and its scope;
- conflicts, assumptions, unresolved decisions, or blockers;
- recommendations or future work as proposals, not completed changes; and
- checks actually performed, plus important checks not run.

Distinguish implemented changes from recommendations and planned work. Do not claim comprehensive architecture compliance, automated enforcement, successful verification, approval, integration, or operational readiness unless the authorized task included that work and evidence supports the claim.

## Related Skills

- [Task scope control](../task-scope-control/SKILL.md) — preserves authorized scope and handles scope changes.
- [Repository implementation](../repository-implementation/SKILL.md) — guides bounded authorized implementation.
- [Implementation planning](../implementation-planning/SKILL.md) — defines source-grounded plans and dependencies.
- [Agent delegation](../agent-delegation/SKILL.md) — coordinates bounded assignments without changing authority.
- [Architecture documentation](../architecture-documentation/SKILL.md) — guides architecture-document changes.
- [Architecture decision record](../architecture-decision-record/SKILL.md) — guides durable decision records without granting approval.
- [Evidence reporting](../evidence-reporting/SKILL.md) — supports evidence-grounded completion reports.

---
name: "architecture-decision-record"
description: "Use when creating, updating, or maintaining a source-grounded Architecture Decision Record (ADR) for a consequential architectural choice, including its alternatives, rationale, authority, and consequences."
---

# Architecture Decision Record

## Purpose

Create or maintain a durable, scoped record of an architectural choice, its context, considered alternatives, rationale, consequences, and supporting evidence. This Skill guides documentation work; it does not grant decision, approval, implementation, or release authority.

The `claude-skills` repository is the provider-neutral engineering platform for building and maintaining SUPER AGI, not the SUPER AGI runtime. Preserve the product direction:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

This is architectural context, not evidence that the described system is implemented. Do not describe the 100 modules as 100 independent AI systems.

## When to Use

Use this Skill when a task requests a durable record of a consequential architectural choice, such as a choice that affects system boundaries, shared infrastructure, architecture contracts, module responsibilities, provider or tool boundaries, security or governance, or compatibility over time. An ADR is useful when readers need to understand the problem, viable alternatives, trade-offs, the bounded outcome, and its consequences.

An ADR is usually unnecessary for a source-grounded clarification, terminology correction, descriptive update, or documentation change that does not make or record an architectural choice. Update the appropriate document directly when that is the requested and sufficient deliverable. Do not turn a documentation update into an ADR merely to add process.

This Skill does not authorize implementation work, provider integrations, changes to architecture decisions, approval, or edits to decision registers and related architecture documents unless the active task explicitly includes them.

## Required Context and Authority

1. Read applicable repository instructions, including [`AGENTS.md`](../../AGENTS.md) and [`CLAUDE.md`](../../CLAUDE.md), and identify the exact requested ADR deliverable, file scope, exclusions, and stopping point.
2. Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) for document authority and approval evidence. Use [`PRODUCT_CONSTITUTION.md`](../../architecture/PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md), and [`ARCHITECTURE-PRINCIPLES.md`](../../architecture/ARCHITECTURE-PRINCIPLES.md) for applicable product direction, boundaries, and source-grounded principles.
3. Read [`ARCHITECTURE-DECISIONS.md`](../../architecture/ARCHITECTURE-DECISIONS.md) and [`OPEN-DECISIONS.md`](../../architecture/OPEN-DECISIONS.md) to understand the repository's proposed decision-record conventions, existing scoped evidence, and unresolved questions. Check relevant affected documents and [`ARCHITECTURE-TRACEABILITY.md`](../../architecture/ARCHITECTURE-TRACEABILITY.md) as needed.
4. Follow relevant guidance in [`DOCUMENTATION-STANDARDS.md`](../../architecture/DOCUMENTATION-STANDARDS.md), while preserving its proposed maturity, and consult [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) or [`SECURITY-GOVERNANCE.md`](../../architecture/SECURITY-GOVERNANCE.md) when capability or security claims are in scope.
5. Identify relevant approval authority only from explicit, applicable repository evidence. The decision register states that a general decision owner, approval hierarchy, and complete conflict-precedence mechanism are not established. Do not infer one.

Do not silently resolve conflicts among canonical documents. Record the conflicting statements and their sources, preserve their maturity and scope, and leave the question unresolved. If the required authority or evidence cannot be established, state the limitation and stop short of presenting an outcome as accepted. Keep unresolved questions in the applicable open-decision process only when that work is explicitly authorized.

## Decision Status and Authority

[`ARCHITECTURE-DECISIONS.md`](../../architecture/ARCHITECTURE-DECISIONS.md) describes the following ADR lifecycle vocabulary as **proposed conventions**, not an approved status system or approval process:

| Status | Use only as supported by evidence |
|---|---|
| **Proposed** | A bounded outcome is recommended for consideration; it is not accepted. |
| **Accepted** | Explicit evidence establishes acceptance, its authority, scope, and effect. |
| **Rejected** | The outcome was explicitly rejected; record the basis and scope when known. |
| **Superseded** | A later, explicitly documented decision replaces it within a stated scope; retain and link the earlier record. |
| **Deferred** | A decision was explicitly postponed; identify the known prerequisite or unresolved question. |

Use these terms only in keeping with the repository's documented convention. Do not imply that the convention itself is formally approved. A status label, author, review, or document location alone does not establish approval authority. Never mark a decision accepted, approved, or binding without explicit evidence. Do not use ADR statuses for document maturity, open-question status, implementation capability, verification, or deployment; the capability vocabulary in `CAPABILITY-STATUS.md` is separate.

If a requested status has no established meaning or the required evidence is absent, mark the status or convention as unresolved/proposed as appropriate, explain the limitation, and do not invent a lifecycle.

## ADR Content

Use the structure appropriate to the decision and task. The following fields are guidance, not a mandatory schema; omit irrelevant fields rather than filling them with speculation:

1. **Identifier and title:** Use an existing identifier only when it is actually assigned. The `ADR-0001` pattern in the decision register is a proposed example, not an established numbering rule. If no identifier convention or number is established, follow an explicitly requested path/name or state that assignment is unresolved; do not fabricate one.
2. **Status, date, and scope:** Record only evidenced status and dates. State affected systems, components, versions, exclusions, and decision authority when known; otherwise use a truthful qualification such as `Unresolved` or `Not recorded`.
3. **Context and problem:** Describe the decision question and only the relevant source-grounded facts, constraints, and circumstances.
4. **Decision drivers and constraints:** Identify requirements, boundaries, compatibility needs, security or governance obligations, and other factors that affect the choice.
5. **Considered alternatives:** Describe meaningful options where evidence supports them, including benefits, limitations, and trade-offs. Do not invent options or claim an exhaustive comparison without evidence; say when alternatives are not established.
6. **Decision and rationale:** State the bounded outcome and explain how it follows from the drivers and evidence. A proposed outcome must be explicitly identified as unaccepted.
7. **Consequences and trade-offs:** Record expected benefits, costs, risks, limitations, compatibility effects, and implementation or migration implications. Distinguish anticipated effects from observed ones.
8. **Security, privacy, safety, and operations:** Address relevant trust boundaries, data handling, permissions, human approval, failure behavior, and operational implications; mark matters outside available evidence unresolved.
9. **Affected architecture and relationships:** Identify relevant layers, planes, interfaces, modules, infrastructure, documents, decisions, or open questions only where their existence and relationship are evidenced.
10. **Evidence, assumptions, and unresolved questions:** Link actual sources and approval evidence where available. Clearly label assumptions, proposals, and unresolved matters; do not fill gaps by inference.

Follow the proposed guidance in [`DOCUMENTATION-STANDARDS.md`](../../architecture/DOCUMENTATION-STANDARDS.md) without treating it as approved policy. Use relative Markdown links to verified, relevant repository paths. A link records a source relationship; it does not establish precedence, implementation dependency, approval, or runtime behavior.

## Decision Quality and Architecture Alignment

- Separate verified facts, documented constraints, assumptions, proposals, hypothetical examples, and unresolved questions. Attribute consequential claims to their actual sources and preserve each source's scope and maturity.
- State the problem narrowly, compare meaningful alternatives when available, and explain material trade-offs. Do not pad the record with unsupported alternatives or make certainty claims beyond the evidence.
- Keep the outcome provider-neutral unless the decision is explicitly and narrowly about a provider-specific adapter. Do not present any model, provider, tool, or conceptual subsystem as universally available without supporting evidence.
- Preserve modular responsibility and shared infrastructure boundaries. Do not silently contradict the intended single unified SUPER AGI architecture or treat its 100 modules as separate products.
- Do not infer that a documented Master Core, module, interface, registry, integration, or shared service exists operationally. File presence, architecture descriptions, or a decision record do not prove implementation or behavior.
- Keep decision status, document maturity, approval, implementation, capability status, verification, deployment, and operational readiness distinct. Recording a decision does not implement it or authorize follow-on work.

## Relationships and Traceability

- An ADR records a bounded decision question and outcome, rationale, consequences, and evidence. It is not the decision index, an open question, an architecture principle, or an implementation task.
- [`ARCHITECTURE-DECISIONS.md`](../../architecture/ARCHITECTURE-DECISIONS.md) is the decision register; [`OPEN-DECISIONS.md`](../../architecture/OPEN-DECISIONS.md) tracks unresolved questions. Their formats and lifecycle terms are described as proposed. Do not imply automatic synchronization or status transitions.
- [`ARCHITECTURE-TRACEABILITY.md`](../../architecture/ARCHITECTURE-TRACEABILITY.md) describes conceptual documentation relationships. Link affected documents and decisions when useful and verified; do not create missing targets or assert a relationship that the sources do not support.
- Do not create or modify a register, open-decision entry, index, template, or other architecture document unless the active task explicitly authorizes that additional file scope.

## Amendments and Supersession

When an existing ADR must change, follow the explicit task scope and preserve its history. Do not silently rewrite an accepted decision's outcome, authority, or rationale. If evidence supports correction or clarification, retain the distinction between editorial correction and a changed decision. If a changed outcome requires a successor record, create or link one only when authorized; update supersession references and lifecycle labels only when supported by the repository's convention and evidence. A new or amended ADR does not itself implement, verify, deploy, or operationalize the decision.

Do not assume an ADR directory, file-naming rule, identifier sequence, template, or record-management process exists. Use the actual path and convention established by the task or verified repository evidence. If it is not established, do not create extra structure; report the uncertainty.

## Safety and Scope

- Follow the active task scope and repository instructions. Modify only authorized files and preserve existing repository content and user work.
- Do not include secrets, credentials, private keys, tokens, or unnecessary sensitive data. Link to protected evidence without copying its sensitive contents.
- Do not bypass authorization, repository protections, security policy, or human-approval boundaries. Keep approval, implementation, deployment, and operational verification as separate activities.
- Do not perform destructive or consequential operations without explicit authorization. Do not switch branches or fetch, pull, merge, rebase, cherry-pick, commit, or push unless separately authorized.
- Do not create supporting files or begin implementation, migration, approval, or another phase unless explicitly requested.
- Stop and report a blocker when required authority, evidence, or scope is missing or conflicts with higher-priority instructions.

## Completion Report

Provide a concise, evidence-based report stating:

- the ADR file created or updated and its bounded subject;
- the substantive content added or changed;
- any unresolved authority, status, identifier, or governance conventions;
- source or evidence limitations and unresolved questions; and
- checks actually performed, including checks not run when relevant.

Do not claim acceptance, approval, implementation, validation, deployment, or operational readiness unless the corresponding evidence was actually established. Do not claim a link check, test, or other check that was not performed.

## Related Skills and Sources

- [Skills overview](../README.md)
- [Skill authoring](../skill-authoring/SKILL.md)
- [Architecture documentation](../architecture-documentation/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Repository audit](../repository-audit/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Architecture decision register](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open architecture decisions](../../architecture/OPEN-DECISIONS.md)

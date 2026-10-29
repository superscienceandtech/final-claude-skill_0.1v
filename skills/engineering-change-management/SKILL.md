---
name: "engineering-change-management"
description: "Use when assessing or handling changes to engineering requirements, scope, dependencies, implementation decisions, or documented constraints."
---

# Engineering Change Management

## Purpose and Applicability

Engineering change management is the source-grounded handling of a proposed or requested change to engineering requirements, deliverables, task boundaries, dependencies, implementation decisions, or documented constraints.

Use this Skill when a request changes or may change the agreed work, when new information affects an active task, or when an existing decision or constraint may need revision. It complements [`task-scope-control`](../task-scope-control/SKILL.md), [`implementation-planning`](../implementation-planning/SKILL.md), [`engineering-workflow-orchestration`](../engineering-workflow-orchestration/SKILL.md), [`engineering-task-lifecycle`](../engineering-task-lifecycle/SKILL.md), [`architecture-compliance`](../architecture-compliance/SKILL.md), and [`architecture-decision-record`](../architecture-decision-record/SKILL.md); use those Skills for their respective detailed procedures.

Keep three things distinct:

- A **change request** proposes or asks for a change; it is not automatically authorized.
- An **approved decision** is established only by evidence from an applicable authority and within its recorded scope.
- An **implemented change** is work actually performed and supported by implementation evidence; it does not by itself establish approval, validation, or operational readiness.

Recording or discussing a proposed change does not authorize or implement it. This Skill is guidance, not a change-control system, approval hierarchy, or runtime capability. The `claude-skill_sonjoy` repository is a provider-neutral Skills and engineering-orchestration platform for SUPER AGI, not the SUPER AGI runtime.

## Identifying and Classifying a Change

Recognize potential changes involving:

- requested requirements, acceptance conditions, deliverables, scope, or priorities;
- architecture, design choices, interfaces, contracts, or module boundaries;
- dependencies, integration assumptions, or execution sequence;
- security, permissions, privacy, safety, and operational constraints;
- documentation, Skills, registries, configuration, workflows, or tooling; and
- provider adapters, external tools, or provider-specific behavior.

Before treating new information as a change, compare it with the existing request and relevant sources:

- A **clarification** makes an existing requirement more precise without necessarily changing its intended outcome.
- A **correction** identifies a factual or interpretive error in existing information.
- An **implementation detail** selects a means of satisfying the existing authorized outcome without changing its externally relevant scope or constraints.
- A **change** alters a requirement, boundary, deliverable, decision, dependency, permission, or constraint, or introduces work not already authorized.
- **Previously documented work** is not automatically newly authorized; establish its current authority and applicability.

These are practical distinctions, not a mandatory repository-wide taxonomy. If the distinction affects permission or scope and remains unclear, preserve that uncertainty and ask.

## Establishing the Applicable Baseline

Determine the baseline from the user's current request and explicit authorizations, applicable `AGENTS.md` and `CLAUDE.md` instructions, relevant Skills, and source-of-truth and architecture documents. Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) and relevant canonical architecture only to the extent they govern the proposed change.

Inspect existing implementation and capability evidence when claims about current behavior or impact depend on it. Use [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) where applicable; do not infer implementation from a document, directory, workflow description, or previous task summary alone.

Do not assume that a document, branch, release, request, or earlier task is authoritative without evidence that it applies. Preserve source maturity, exact scope, approval evidence, and unresolved status. When two sources conflict or authority is unclear, record the conflict and seek resolution rather than silently selecting a baseline.

## Impact and Dependency Analysis

Assess a proposed change only as far as needed to determine its relevance, authorization, and consequences. Consider possible effects on:

- the current deliverable, acceptance conditions, and authorized task boundary;
- related Skills, documentation, registries, or configuration;
- architecture contracts, module boundaries, shared interfaces, and provider neutrality;
- prerequisites, dependencies, and integration assumptions;
- security, permissions, confidentiality, governance, and operational restrictions; and
- previously recorded decisions, open questions, and possible follow-up work.

Separate observed impacts from inferred risks and unknowns. Identify the evidence and scope behind observed claims; label potential consequences as risks or assumptions where they are not established. Do not claim a complete impact assessment unless the authorized task includes and supports one.

Do not modify additional files merely because they appear affected. If additional work is necessary, determine whether it is already authorized, an immediate in-scope dependency, or a proposed scope expansion. Seek authorization before expanding the target set.

## Authorization and Change Decisions

- **Within the active authorization:** Proceed only when the change is clearly within the requested task and applicable instructions.
- **Clarification needed:** Ask when the requested outcome or scope is ambiguous and a reasonable interpretation could materially affect the result.
- **Additional permission needed:** Pause the affected work when the change requires new files, operations, external access, destructive actions, or other authority not already granted.
- **Conflict with authoritative documentation:** Preserve the conflict and avoid the affected implementation. Consult [`architecture-compliance`](../architecture-compliance/SKILL.md) and source-of-truth guidance; do not silently override an applicable approved requirement.
- **Unresolved approval authority:** Do not infer an approver or decision hierarchy. The repository's [`ARCHITECTURE-DECISIONS.md`](../../architecture/ARCHITECTURE-DECISIONS.md) states that general decision ownership and approval hierarchy are unresolved. Seek direction from an explicitly authorized human or preserve the issue as unresolved.
- **Destructive or irreversible change:** Obtain the explicit authorization required by applicable instructions before acting.

A suggestion, plan, approval-shaped label, technical ability, or silence does not grant authorization. Continue only independent work that remains safe and within the original scope.

## Implementing an Authorized Change

Once a change is authorized, implement only the agreed scope and target files. Follow [`task-scope-control`](../task-scope-control/SKILL.md) and applicable implementation guidance. Preserve unrelated tracked and untracked work, existing conventions, and provider-neutral boundaries.

Do not silently bundle unrelated refactoring, cleanup, architecture changes, or follow-up work. If implementation reveals a material new impact that cannot be handled within the authorized scope, preserve current work, explain the impact and dependency, and request further direction rather than expanding the change.

## Architecture and Decision Records

A change may require updating an architecture document or traceability reference only when that documentation work is explicitly authorized and the correct source, scope, and authority are established. A consequential architectural choice may warrant an ADR when requested and in scope; use [`architecture-decision-record`](../architecture-decision-record/SKILL.md) and [`ARCHITECTURE-DECISIONS.md`](../../architecture/ARCHITECTURE-DECISIONS.md). Consult [`OPEN-DECISIONS.md`](../../architecture/OPEN-DECISIONS.md) for relevant unresolved questions and [`ARCHITECTURE-TRACEABILITY.md`](../../architecture/ARCHITECTURE-TRACEABILITY.md) when relationships among requirements, decisions, implementation, and evidence matter.

Revisit a documented decision only when the task authorizes that work and the decision's scope and authority can be established. Do not invent ADR identifiers, approval authority, or decision status vocabulary. If approval evidence or the applicable process is unresolved, keep the proposed outcome explicitly unresolved.

Updating documentation or recording a proposal does not implement a runtime capability, authorize implementation, close an open decision, or establish operational behavior. Keep documentation, approval, implementation, evaluation, and release distinct.

## Change Communication and Traceability

Communicate proportionately and, where material, state:

- what change was requested or observed and why;
- the source, evidence, or explicit authorization supporting it;
- the affected task boundary and files or interfaces in scope;
- observed impacts, potential risks, dependencies, and unknowns;
- the decision or permission state, without overstating authority;
- files actually changed and work actually performed; and
- work not performed and follow-up actions requiring separate authorization.

Use [`engineering-communication`](../engineering-communication/SKILL.md) for clear communication, [`evidence-reporting`](../evidence-reporting/SKILL.md) for claim-to-evidence discipline, and [`ARCHITECTURE-TRACEABILITY.md`](../../architecture/ARCHITECTURE-TRACEABILITY.md) where appropriate. Preserve traceability with existing references and conventions; do not create a new mandatory report format, identifier system, or registry schema.

## Deferred, Rejected, and Unresolved Changes

Communicate whether a change was explicitly deferred, rejected, left unresolved, partly implemented, or not started only when the facts support that description. These are ordinary descriptions, not new canonical change-status labels or lifecycle transitions.

For a deferred or rejected change, preserve the actual decision, its source and scope, and any known reason; do not imply that it was implemented. For missing information or conflicting requests, identify the unresolved question and the decision or authorization needed. For partially implemented work, distinguish completed edits from remaining work and uncertain outcomes. A change that would exceed authorization must remain unimplemented until appropriate direction is obtained.

## Related Skills and Architecture References

- [Task scope control](../task-scope-control/SKILL.md)
- [Implementation planning](../implementation-planning/SKILL.md)
- [Engineering workflow orchestration](../engineering-workflow-orchestration/SKILL.md)
- [Engineering task lifecycle](../engineering-task-lifecycle/SKILL.md)
- [Engineering communication](../engineering-communication/SKILL.md)
- [Engineering handoff](../engineering-handoff/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Architecture decision record](../architecture-decision-record/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Architecture decisions register](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open architecture decisions](../../architecture/OPEN-DECISIONS.md)
- [Architecture traceability](../../architecture/ARCHITECTURE-TRACEABILITY.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)

---
name: "implementation-planning"
description: "Use when turning an explicitly authorized engineering objective into a bounded, dependency-aware implementation plan with clear scope, deliverables, risks, and execution boundaries."
---

# Implementation Planning

## Purpose

Translate an explicitly authorized engineering objective into a concise, source-grounded plan that another authorized agent can execute without guessing. Keep planning separate from implementation, architectural approval, authorization, and verification. This Skill produces a plan; it does not itself authorize any planned action.

The `claude-skills` repository is a provider-neutral engineering and skills orchestration platform for developing and maintaining SUPER AGI. It is not the SUPER AGI runtime. Preserve the product direction:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

Treat architectural descriptions as design intent unless repository evidence establishes a different maturity or implementation status. Do not describe the 100 modules as separate AI systems.

## When to Use

Use this Skill when a user requests an implementation plan, or when an explicitly authorized engineering objective needs decomposition before implementation.

Distinguish these cases before planning:

- **Bounded implementation task:** The outcome, scope, and authority are sufficiently clear. Produce only the plan requested; do not begin implementation unless separately authorized.
- **Broad objective:** The goal is authorized but needs decomposition. Propose bounded tasks and dependencies while preserving the original scope. Ask for clarification or record assumptions when the desired outcome or boundaries are material and unclear.
- **Unresolved requirement or architecture decision:** A required behavior, interface, or architecture choice is unsettled. Identify the question, source conflict, or missing authority; do not select an answer or present a proposal as approved. Stop if the uncertainty blocks responsible planning.
- **Insufficient authorization or inputs:** The objective, permissions, acceptance conditions, or essential context is missing. Request clarification through the available interaction mechanism or report the blocker. Do not infer authorization from a request to plan.

Do not use this Skill to conduct a repository-wide audit, create architecture documentation or an ADR, implement code, approve architecture, run verification, deploy, or expand the user’s requested scope. This Skill is guidance, not an authorization mechanism or execution boundary.

## Source and Evidence Discipline

Use the sources relevant to the objective rather than treating every reference as applicable:

- Follow [`AGENTS.md`](../../AGENTS.md) and [`CLAUDE.md`](../../CLAUDE.md), plus any applicable instructions in the target scope.
- Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) and relevant architecture decisions, principles, boundaries, and contracts. Use [`OPEN-DECISIONS.md`](../../architecture/OPEN-DECISIONS.md) to identify unresolved questions when applicable.
- Inspect relevant source files and established interfaces when planning implementation against an existing repository. Use documentation alone only for claims about documented intent, not for claims about operational behavior.
- Consult [`ARCHITECTURE-TRACEABILITY.md`](../../architecture/ARCHITECTURE-TRACEABILITY.md) when relationships among requirements, decisions, contracts, implementation artifacts, or evidence matter.
- Apply relevant security, module, and capability guidance, including [`MODULE-CONTRACT.md`](../../architecture/MODULE-CONTRACT.md) and [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md), without elevating proposed details to approved requirements.
- Use [`workflows/spec-to-implementation/README.md`](../../workflows/spec-to-implementation/README.md) as workflow context where relevant; do not treat it as authority to expand the requested plan into implementation or verification.

For each consequential planning claim, distinguish:

- **Verified repository fact:** directly observed in relevant files, interfaces, or permitted repository evidence.
- **Explicit user requirement:** stated by the user, with its requested scope and authority preserved.
- **Approved architectural decision:** supported by explicit approval evidence for the relevant scope.
- **Assumption:** a necessary but unverified premise, labeled clearly and not silently made mandatory.
- **Proposal:** a possible approach or decomposition, not an approved decision or requirement.
- **Unresolved question:** missing or conflicting information that remains unanswered.

Do not elevate an assumption, proposal, workflow suggestion, or document’s mere existence into an approved requirement or implementation fact. Preserve source maturity and scope. If sources conflict, cite or describe the conflict and leave it unresolved; do not silently choose precedence. Do not invent file paths, interfaces, capabilities, approvals, ownership, or dependencies.

## Planning Procedure

1. **Identify the outcome and boundary.** Restate the requested objective, expected result, acceptance conditions, and where planning must stop. Distinguish planning-only work from a request that separately authorizes implementation.

2. **Capture scope and constraints.** Record permitted files, components, repositories, environments, and activities when specified. Identify exclusions, security or compatibility constraints, required approvals, and prohibited operations. Do not broaden scope to make the plan easier.

3. **Inspect relevant instructions, sources, and implementation context.** Read applicable repository instructions and the narrow set of architecture documents, contracts, source files, and interfaces needed to support this plan. Use actual repository paths and evidence. Do not perform an audit unless one is explicitly requested.

4. **Establish prerequisites and dependencies.** Identify required decisions, inputs, interfaces, permissions, artifacts, and other tasks. Label each as evidenced, proposed, or unresolved. If a necessary prerequisite is unavailable, state the blocker; do not schedule dependent work as though it were ready.

5. **Decompose only when useful and authorized.** Break a broad or multi-part objective into small, bounded tasks with distinct deliverables. Keep a self-contained task as one task. Do not add independent cleanup, speculative infrastructure, or follow-on phases.

6. **Map affected surfaces where evidence supports them.** Name expected files, components, contracts, architecture layers, planes, modules, or integration points only when relevant and grounded in available evidence. Mark uncertain targets as provisional; do not present guesses as committed scope.

7. **Record risks and unresolved matters.** Capture material assumptions, risks, conflicts, security and governance concerns, compatibility impacts, missing authority, and open questions. State what evidence or decision is required to resolve each blocker when known.

8. **Define deliverables and observable completion conditions.** Specify the output each task should produce and the evidence by which completion can be recognized. Keep implementation, testing, independent verification, approval, deployment, and operational readiness distinct; include them only when authorized and in scope.

9. **State execution and authorization boundaries.** Explicitly identify what the plan does not authorize. Note separately authorized actions or approvals required before implementation, destructive changes, external operations, consequential actions, or other restricted work.

10. **Present a proportionate, executable plan.** Use concise task descriptions and explicit prerequisites so an authorized executor does not have to guess. Label the plan **Proposed** unless approval is evidenced. Stop after delivering the requested plan; do not automatically begin its first or next task.

## Dependencies and Sequencing

- Represent a dependency explicitly by naming the prerequisite task or required input and why the dependent task needs it. Use a repository-established dependency format if one applies; otherwise use plain-language relationships. Do not invent a canonical notation, identifier scheme, or task lifecycle.
- A dependency exists when the dependent work cannot start or produce its intended result until a prerequisite is available. Distinguish this from a preferred order, coordination convenience, or shared topic.
- Keep independent tasks independent where practical. Do not add artificial dependencies merely because tasks appear in a list.
- Sequence dependent work only after its prerequisite is completed or the required input is confirmed. If it is unresolved, mark the dependent task blocked or conditional rather than implying readiness.
- Check that the dependency relationships do not form a cycle. If a cycle exposes a missing decision or circular requirement, state it as a blocker; do not hide it by rearranging task order.
- Do not infer completion of a prerequisite from a document, file, interface declaration, or plan entry alone. Require evidence appropriate to that prerequisite.
- Producing the plan does not start, delegate, or authorize any task. Do not automatically proceed to dependent work.

## Architecture, Integration, and Security Alignment

- Preserve the unified SUPER AGI direction, shared universal infrastructure, provider neutrality, and explicit boundaries between this engineering platform and the target runtime.
- Respect established system boundaries and contracts. Distinguish approved architecture from proposal, existing implementation from conceptual interface, and actual integration from placeholder or mock.
- Do not assume the Master Core, Universal Intelligence Fabric, module registry, context engine, collaboration engine, Model Gateway, any provider, tool, API, or other planned capability is operational without supporting implementation evidence.
- Preserve the canonical capability-status vocabulary in [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md): `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, and `UNKNOWN`. Do not assign or upgrade a capability status as a planning shortcut; a planned task is not implementation evidence.
- Identify security, privacy, safety, authorization, data ownership, least-privilege, and human-approval requirements when relevant. Treat unresolved governance as a constraint or blocker, not as permission to bypass it.
- Protect secrets and sensitive information. Do not copy credentials, tokens, private keys, or unnecessary sensitive data into a plan.
- Preserve unrelated user work. Record exact allowed files and exclusions where evidence supports doing so; do not authorize unrelated modifications.
- Do not switch branches or fetch, pull, merge, rebase, cherry-pick, commit, or push unless governing instructions explicitly permit the specific operation. Identify any operation requiring separate authorization.
- Stop and report when the requested scope conflicts with repository instructions, a required authority is absent, or a critical dependency cannot be established.

## Planning Output

Scale the plan to the task. A small, self-contained change may need only an objective, scope, deliverable, and boundary. For a larger authorized objective, include only the relevant items below:

- **Objective and expected outcome**
- **Plan status:** Proposed unless approval is evidenced; approval scope and evidence if established
- **Scope and exclusions**
- **Authoritative inputs:** Instructions, user requirements, decisions, contracts, and relevant implementation evidence
- **Task breakdown:** Bounded deliverables without unnecessary detail
- **Dependencies and sequencing:** Explicit prerequisites, independent work, and blocked/conditional tasks
- **Expected files or components affected:** Evidence-supported targets, qualified where tentative
- **Risks, assumptions, and unresolved questions**
- **Completion conditions:** Observable deliverables and evidence expectations
- **Authorization and execution boundaries:** Planning-only status, approvals required, prohibited operations, and any separately authorized implementation scope

Do not force a large template onto a simple request. Do not add a separate plan file unless the user explicitly requests one and authorizes its path.

## Handoff and Status Reporting

When handing the plan to an implementation agent, include the requested outcome, exact scope and exclusions, source and authority qualifications, prerequisite tasks or inputs, known blockers, intended deliverables, completion conditions, and authorization limits. Clearly identify what is proposed versus established. Do not pass an unresolved assumption as an instruction to implement.

Report task states precisely:

- **Planning completed:** a plan was produced; no implementation is implied.
- **Implementation authorized:** explicit authorization exists for the stated scope; authorization alone does not mean work occurred.
- **Implementation completed:** the scoped change was actually made and the changed files and behavior are identified.
- **Verification performed:** the named check was actually run and its observed result is reported.
- **Approval, deployment, or operational readiness:** report only when separate evidence establishes the relevant activity and scope.

Never claim a task is implemented, tested, approved, or operational merely because it appears in a plan. State what checks were not run and what remains unresolved.

## Relationship to Other Skills

- Use [repository audit](../repository-audit/SKILL.md) for explicitly requested, bounded repository investigation; planning does not itself authorize an audit.
- Use [architecture documentation](../architecture-documentation/SKILL.md) for authorized architecture-document creation or updates.
- Use [repository implementation](../repository-implementation/SKILL.md) for a separately authorized, bounded implementation task.
- Use [architecture decision record](../architecture-decision-record/SKILL.md) when a durable architectural choice needs to be recorded; this Skill does not decide or approve it.
- Use [skill authoring](../skill-authoring/SKILL.md) when creating or changing canonical Skills.

These Skills have distinct responsibilities. This planning Skill does not replace them or duplicate their full procedures.

## Completion Report

Provide a concise, evidence-based report stating:

- the objective planned and the plan's status;
- the scope, principal tasks, and important dependencies identified;
- relevant assumptions, blockers, risks, or unresolved authority questions;
- whether implementation was separately authorized or performed;
- what verification, approval, or operational checks were actually performed or not run; and
- whether any plan artifact was created, only if the task authorized one.

Do not claim approvals, implementation, testing, or operational results without evidence. Stop after reporting completion of the requested planning task.

---
name: "engineering-workflow-orchestration"
description: "Use when coordinating a bounded, multi-step engineering task across dependencies, implementation work, agents, tools, handoffs, and completion reporting."
---

# Engineering Workflow Orchestration

## Purpose and Applicability

Engineering workflow orchestration is the coordination of related, authorized engineering work items toward a requested outcome: clarifying scope, arranging dependencies, coordinating execution and handoffs, handling blockers, and reporting the actual result.

Use this Skill when an engineering objective has multiple steps, dependencies, owners, agents, or handoffs that need coordination. For a small, self-contained task, keep coordination lightweight and do the work directly when authorized.

This Skill complements [`implementation-planning`](../implementation-planning/SKILL.md), [`task-scope-control`](../task-scope-control/SKILL.md), [`agent-delegation`](../agent-delegation/SKILL.md), [`engineering-handoff`](../engineering-handoff/SKILL.md), and [`engineering-communication`](../engineering-communication/SKILL.md). It helps coordinate their responsibilities; it does not duplicate their full procedures.

Orchestration guidance is not an execution engine, authorization mechanism, agent protocol, or guarantee of task completion. A documented sequence does not establish that agents, tools, shared state, or automatic coordination are available or operational. The `claude-skill_sonjoy` repository is a provider-neutral Skills and engineering-orchestration platform for the SUPER AGI project; it is not the SUPER AGI runtime.

## Workflow Initiation and Scope

Before coordinating work:

1. Establish the user's requested outcome, expected deliverable, and observable completion conditions.
2. Identify the current task boundary, authorized files and operations, explicit exclusions, and stopping point.
3. Read applicable repository instructions and relevant source-of-truth and architecture documentation. Use only sources that materially constrain the task; preserve their authority, maturity, and scope.
4. Identify required inputs, known constraints, prerequisites, dependencies, and unresolved questions.
5. Distinguish operations explicitly authorized from those merely possible or suggested by a plan. A workflow or handoff does not itself authorize implementation, external access, destructive actions, testing, approval, deployment, or follow-on work.

If essential scope, authority, acceptance conditions, or required inputs are missing or contradictory, seek clarification or stop the affected work. Do not invent requirements or treat a plan as permission to execute it.

## Task Decomposition and Dependencies

Decompose only when the objective is sufficiently complex and the decomposition is within the user's authorization. Make each work item coherent, bounded, and independently understandable, with a clear deliverable and stopping condition. Keep a simple task intact when coordination overhead would outweigh useful separation.

Identify prerequisites and dependencies from explicit requirements or observed relationships. Distinguish established dependencies from proposed sequencing, assumptions, and unresolved dependency questions. Do not allow downstream work to rely on an upstream result until that result is completed and confirmed.

Do not invent a canonical task-ID format, dependency syntax, planning schema, or mandatory decomposition rule. Use existing repository conventions when authoritative and applicable; otherwise describe tasks and dependencies in clear natural language.

## Execution Coordination

- Coordinate work in dependency-aware order. Parallelize only when work is genuinely independent, authorization permits it, and available agents or tools can perform it.
- Select existing Skills, agents, and tools based on the work, required context, and actual availability. Do not assume a particular provider, model, tool, or execution capability exists.
- Keep ownership, allowed scope, expected output, dependencies, and stopping conditions clear for each work item.
- Prefer separate file boundaries for concurrent work. Before overlapping edits, coordinate ownership and sequence changes to avoid conflicting writes. Do not assume locking or automatic conflict prevention.
- Preserve unrelated tracked and untracked changes. Do not silently overwrite, discard, or incorporate another owner's work without confirmation and authorization.
- Keep each task within its assigned boundary. Do not silently add later tasks, phases, reviews, audits, tests, or other operations.
- Stop affected work when a prerequisite, permission, scope limit, or required decision prevents safe continuation. Continue only independent work that remains authorized and safe.

Use [`agent-delegation`](../agent-delegation/SKILL.md) when assigning bounded work; delegation does not transfer or expand the user's authorization.

## Workflow State and Progress Communication

Communicate state in terms that accurately describe the work: not started, in progress, completed, blocked, partial, failed, or unconfirmed, as appropriate. These are descriptive terms, not a new canonical status taxonomy. Use another status vocabulary only when an applicable authoritative source defines it.

State completed deliverables and their locations, work still underway, dependencies awaiting resolution, concrete blockers, and outcomes that remain unverified. Distinguish a reported result from independently observed evidence and an intended action from an action actually completed. Use [`engineering-communication`](../engineering-communication/SKILL.md) for concise, audience-appropriate updates and [`evidence-reporting`](../evidence-reporting/SKILL.md) for detailed evidence-grounded claims.

Do not imply task completion from plan completion, agent assignment, a successful command alone, or the presence of a file. Do not claim automatic status synchronization or evidence collection without repository evidence.

## Handoffs and Context Continuity

When transferring work, preserve the original objective and scope; current work state; actual deliverables and their locations; relevant decisions, sources, and constraints; prerequisites, dependencies, and blockers; actions completed and not performed; and permissions and operational boundaries that apply to the next owner.

Use [`engineering-handoff`](../engineering-handoff/SKILL.md) for transfer procedures and [`context-management`](../context-management/SKILL.md) for selecting, preserving, and carrying context. Include enough information for the authorized recipient to proceed without guessing, while omitting unnecessary sensitive information. A handoff does not itself authorize the next step, confirm another agent's unverified claims, or require starting a later task.

## Failure, Blockers, and Recovery

- **Missing prerequisite:** Identify the affected work, the missing input or dependency, and what is needed to proceed. Do not treat it as satisfied until confirmed.
- **Conflicting requirements or sources:** Preserve the conflict and its sources. Follow applicable repository governance; ask for clarification or stop when the conflict blocks responsible work. Do not silently choose a new precedence rule.
- **Unavailable tool, agent, or provider:** State what is unavailable and its effect. Use an alternative only when it is available, suitable, and authorized; otherwise report the blocker.
- **Unexpected existing target:** Do not overwrite or repurpose it when the task requires a new deliverable. Stop and report the conflict for direction.
- **Partial implementation or failed operation:** Preserve work and evidence, report what succeeded, failed, or remains uncertain, and do not describe the intended outcome as achieved.
- **Additional authorization required:** Stop the affected operation and request the necessary clarification or approval. Do not infer permission from technical access, delegation, a plan, or silence.

Retry only when the action is safe, within authorization, and the result can be assessed without risking conflicting or duplicate effects. Never imply success without supporting evidence.

## Completion and Workflow Boundaries

Determine completion against the requested deliverable and its stated acceptance conditions. Report the actual outcome, evidence, limitations, and blockers, then stop at the authorized boundary.

Keep these distinct:

- **File change:** A file was created or modified; this does not establish runtime behavior.
- **Execution:** A program, command, tool, or workflow actually ran; this does not alone establish the intended effect.
- **Validation or verification:** A specified check was performed and its observed result supports a bounded conclusion.
- **Testing:** Tests were actually run, with results and scope reported. Testing is not mandatory for every workflow and must follow the task's authorization and restrictions.
- **Deployment or other operational action:** The operation was explicitly authorized, performed, and evidenced; it must not be inferred from implementation or validation.

A plan that lists an activity does not prove that it occurred or authorize it. Do not claim implementation, testing, approval, deployment, or operational readiness without evidence appropriate to that claim.

## Security and Operational Safety

- Apply least privilege and use only operations authorized for the current task.
- Protect secrets, personal data, and confidential context; share only what an authorized recipient needs.
- Treat provider, agent, tool, external-content, and repository boundaries according to applicable instructions. Availability is not evidence of permission, safety, or equivalent controls.
- Require human intervention or approval where applicable. Do not silently bypass permission checks or unresolved governance decisions.
- Preserve unrelated repository work. Do not switch branches or fetch, pull, merge, rebase, cherry-pick, commit, or push unless explicitly authorized.
- Do not perform destructive, irreversible, sensitive, or externally visible actions without required explicit authorization.

Consult [`SECURITY-GOVERNANCE.md`](../../architecture/SECURITY-GOVERNANCE.md) and [`architecture-compliance`](../architecture-compliance/SKILL.md) where architecture, security, or governance constraints materially affect coordination. These sources document requirements and design intent; do not claim operational security enforcement or implemented orchestration capabilities without direct evidence.

## Related Skills and Architecture References

- [Implementation planning](../implementation-planning/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Agent delegation](../agent-delegation/SKILL.md)
- [Engineering handoff](../engineering-handoff/SKILL.md)
- [Engineering communication](../engineering-communication/SKILL.md)
- [Context management](../context-management/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Architecture traceability](../../architecture/ARCHITECTURE-TRACEABILITY.md)

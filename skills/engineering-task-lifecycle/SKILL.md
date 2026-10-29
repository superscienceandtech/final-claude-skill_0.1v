---
name: "engineering-task-lifecycle"
description: "Use when managing an authorized engineering task from intake through active work, interruption, handoff, completion, or cancellation."
---

# Engineering Task Lifecycle Management

## Purpose and Applicability

Engineering task lifecycle management is the practical handling of one authorized task as its circumstances change: understand the request, determine whether work can begin, preserve scope while acting, respond to pauses or blockers, hand off or resume safely, and report how the task ended.

Use this Skill when a task may span multiple work periods, agents, dependencies, or handoffs, or when a clear boundary between active, paused, and completed work is important. For multi-task coordination, use [`engineering-workflow-orchestration`](../engineering-workflow-orchestration/SKILL.md). This Skill focuses on the lifecycle of the authorized task; it does not duplicate planning, scope-control, workflow coordination, communication, evidence-reporting, or handoff procedures.

This is provider-neutral guidance, not a software execution engine or authorization mechanism. Documented lifecycle concepts do not establish that a runtime task manager, persistent task state, automatic transitions, or cross-agent synchronization exists. The `claude-skill_sonjoy` repository is the provider-neutral Skills and engineering-orchestration platform for SUPER AGI, not the SUPER AGI runtime.

## Task Intake and Initial Understanding

At intake, establish from the user's request and applicable repository instructions:

- the requested outcome and expected deliverable;
- the authorized files, resources, and operations, plus exclusions and stopping point;
- relevant repository instructions and source-of-truth documents;
- required inputs, known constraints, and prerequisites;
- dependencies that are established, proposed, or still unresolved; and
- questions or missing authority that could materially affect the work.

Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) and relevant architecture or decision documents when they constrain the task. Preserve source maturity: a proposal, link, or documented intent is not by itself approval, implementation evidence, or authorization.

Clarify when requirements conflict, a consequential decision is unresolved, a required permission is absent, or proceeding would require guessing about scope or acceptance. Do not silently turn an assumption or recommendation into a user requirement.

## Readiness and Initiation

Begin implementation only when the outcome, scope, required inputs, target availability, relevant dependencies, and authority are sufficient for the planned action. This is a practical judgment, not a mandatory readiness checklist or formal approval process.

Pause before the affected action when:

- an essential input or prerequisite is missing or unconfirmed;
- the target exists unexpectedly and the task does not authorize replacing it;
- requirements or source authority conflict in a way that changes the work;
- the operation exceeds the user's scope or requires additional permission; or
- a required tool, provider, or capability is unavailable.

Continue independent work only when it remains authorized, safe, and does not rely on the unresolved prerequisite. A plan or task description does not authorize every operation it mentions.

## Active Work and Scope Preservation

Keep attention on the requested deliverable and its completion conditions. Separate the current task from adjacent improvements, follow-on work, or subsequent phases. If new requirements or necessary changes appear, assess whether they are within scope; seek authorization rather than silently expanding the task.

Follow [`task-scope-control`](../task-scope-control/SKILL.md) and, when multiple tasks or dependencies need coordination, [`engineering-workflow-orchestration`](../engineering-workflow-orchestration/SKILL.md). Preserve unrelated tracked and untracked work. Keep ownership clear and coordinate before overlapping edits; do not assume concurrent work is protected by locking or automatic conflict prevention.

Describe progress from observable evidence. Distinguish intended changes from edits actually made, completed operations from attempted ones, and reported results from independently confirmed outcomes.

## Paused, Blocked, and Interrupted Tasks

Pause or stop affected work when a dependency is missing, permission is insufficient, requirements conflict, a tool is unavailable, an unexpected target conflict appears, or safe continuation is otherwise uncertain. Record the concrete blocker and what information, decision, resource, or authorization is needed. Do not invent canonical blocked-state codes, transition rules, or a universal lifecycle status taxonomy.

For partial work, preserve the actual changes and evidence, identify what remains incomplete, and report failures and uncertain effects. Do not repeat an operation with possible side effects until its prior outcome is understood or a safe, authorized retry is established.

When a session or agent is interrupted, preserve enough context for safe continuation:

- original objective, deliverable, scope, exclusions, and stopping point;
- applicable instructions, relevant sources, and material decisions;
- files or resources actually affected and work completed;
- remaining work and verified prerequisites;
- blockers, open questions, and assumptions; and
- operations attempted, completed, failed, or not performed.

Avoid including secrets or unnecessary sensitive information in continuation context.

## Handoff and Resumption

Use [`engineering-handoff`](../engineering-handoff/SKILL.md) for transfer procedures and [`context-management`](../context-management/SKILL.md) for selecting and preserving context. A handoff should be sufficient for the next authorized owner to understand what happened and what remains without guessing, while preserving the original scope and authorization boundaries.

Before resuming:

1. Re-establish the original request, deliverable, exclusions, and stopping point.
2. Read current applicable repository instructions and relevant source documents.
3. Inspect the actual current task state and affected files instead of relying solely on a summary or prior claim.
4. Separate confirmed completed work from incomplete, unverified, or merely reported work.
5. Resolve missing prerequisites and permission gaps before dependent actions.
6. Determine whether an earlier operation may have succeeded before repeating it.
7. Record or communicate new decisions only when supported by authority or explicitly authorized.

A receiving agent or session does not gain broader authority merely by receiving a handoff. If the task's authorization, current state, or required decision remains unclear, pause and seek clarification.

## Completion and Cancellation

A task may end because its requested deliverable is complete, the user explicitly stops or cancels it, or a blocker requires user input. Report the actual ending state accurately; do not present a blocked, cancelled, or partial task as complete.

When reporting, state the deliverable actually produced, files actually modified, evidence relevant to the outcome, unresolved limitations or blockers, and work remaining. Distinguish activities performed from activities not performed, including:

- file creation or modification;
- runtime or tool execution;
- validation or verification;
- testing; and
- deployment or other operational actions.

File creation does not establish runtime success, validation, testing, approval, or deployment. Do not require testing for every task; follow the active task's actual requirements and restrictions. Use [`engineering-communication`](../engineering-communication/SKILL.md) for clear status updates and [`evidence-reporting`](../evidence-reporting/SKILL.md) for detailed evidence-grounded claims.

## Lifecycle Boundaries and Safety

- Use least privilege and perform only explicitly authorized operations.
- Protect confidential information and sensitive context; do not expose credentials, tokens, private keys, or unnecessary private data in prompts, logs, summaries, or handoffs.
- Preserve existing work and respect repository-specific scope and operational restrictions.
- Obtain required explicit authorization before destructive, irreversible, sensitive, or externally visible actions. Do not infer approval from technical access, silence, task assignment, or a handoff.
- Treat uncertain or partial outcomes honestly; do not imply success without evidence.
- Do not switch branches or fetch, pull, merge, rebase, cherry-pick, commit, or push unless explicitly authorized by applicable instructions.
- Apply [`SECURITY-GOVERNANCE.md`](../../architecture/SECURITY-GOVERNANCE.md) and [`architecture-compliance`](../architecture-compliance/SKILL.md) where relevant. Do not create conflicting security rules, approval hierarchies, or lifecycle governance.

## Related Skills and Architecture References

- [Implementation planning](../implementation-planning/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Engineering workflow orchestration](../engineering-workflow-orchestration/SKILL.md)
- [Engineering communication](../engineering-communication/SKILL.md)
- [Engineering handoff](../engineering-handoff/SKILL.md)
- [Context management](../context-management/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Agent delegation](../agent-delegation/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Architecture traceability](../../architecture/ARCHITECTURE-TRACEABILITY.md)

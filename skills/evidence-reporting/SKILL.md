---
name: "evidence-reporting"
description: "Use when reporting engineering work, repository observations, executed operations, verification results, or unresolved limitations with claims traceable to evidence."
---

# Evidence Reporting

## Purpose

Produce accurate, concise reports that distinguish what is known, what was done, what evidence supports each claim, and what remains unknown or incomplete. This Skill governs reporting discipline; it does not perform engineering work, authorize operations, or make evidence stronger than it is.

The `claude-skills` repository is a provider-neutral Skills and engineering orchestration platform for building and maintaining SUPER AGI. It is not the SUPER AGI runtime. Preserve the product direction:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

This is architectural context, not evidence that the described system is implemented. Do not treat the 100 modules as separate AI systems.

## When to Use

Use this Skill when reporting engineering changes, repository state, tool or command execution, validation results, capability status, blockers, or a handoff requiring evidence and honest limitations.

Keep the report proportional to the task. A small change may need only a brief summary, changed file, and checks performed or skipped. Do not create a separate report artifact unless explicitly requested and authorized.

## Reporting Procedure

1. **Define the report boundary.** Identify the requested objective, authorized scope, subject, and time or repository scope the report covers. Do not imply repository-wide inspection when only selected files or operations were examined.

2. **Separate claim types.** Distinguish:
   - **Directly observed facts:** what was actually inspected or captured.
   - **Actions performed:** operations actually initiated and completed, partially completed, or failed.
   - **Tool or command results:** output, exit status, or response actually captured.
   - **Evidence-supported conclusions:** conclusions justified by identified observations.
   - **Assumptions and inferences:** interpretations not directly established, labeled as such.
   - **Proposals or recommendations:** suggested future work, not completed work or approved requirements.
   - **Unknowns and unverified claims:** matters for which evidence is insufficient.
   - **Blockers and limitations:** conditions that prevented or constrain work or confidence.

3. **Support significant claims.** For each important conclusion, point to relevant evidence: exact repository-relative paths; relevant sections or line ranges when known; actual command or tool result and exit status when captured; observed changes; or an applicable recorded decision or approved requirement. Use only references that exist and were actually examined. Do not invent citations, line numbers, command output, tool responses, or file states.

4. **Describe execution status precisely.** State whether work was not started, in progress, completed, partially completed, blocked, not performed, not verified, or failed as appropriate. These are descriptive labels unless an established repository convention governs the specific context. Distinguish an attempted operation from one that completed and distinguish command completion from the intended effect being verified.

5. **Report checks and failures.** List checks actually executed and their observed results. Identify checks not run, unable to run, or interrupted. Include material failures and partial execution; do not omit errors that change the meaning of the result. Preserve relevant error details without exposing sensitive data.

6. **Bound conclusions and status claims.** State what evidence establishes and what it does not establish. Describe known risks, limitations, unresolved questions, and remaining work. Avoid stronger claims than the evidence supports.

7. **Protect information and stop at scope.** Redact secrets and sensitive information. Preserve unrelated work and authorization boundaries. Do not alter evidence, retry consequential actions, or begin follow-on work to make the report appear successful. Stop at the requested reporting boundary.

## Claim-to-Evidence Rules

- **A path or file exists** only establishes that the path or file was observed to exist at the inspected time. It does not establish that its contents are correct, complete, approved, executed, or operational.
- **A file was read** supports claims about the inspected contents and scope. It does not establish uninspected content or repository-wide completeness.
- **A command completed** is supported by its captured result and, where available, exit status. It does not alone prove that the intended state change or behavioral effect occurred.
- **A check passed** only when the check was actually run and its observed result supports that conclusion. Report the exact check and relevant scope where practical.
- **A component or interface exists** does not establish that it operates, integrates end to end, is secure, is authorized, or is production-ready.
- **A documented or declared capability** is not proof of implementation. Do not infer behavior, compatibility, security enforcement, or operational readiness from architecture text, interfaces, manifests, directory presence, or a polished report.
- **Absence of evidence** is not proof of absence unless the inspected scope and method were sufficient to establish absence. Otherwise report the matter as unknown or unverified.
- **A scoped inspection** supports conclusions only about that scope. Do not generalize partial inspection into repository-wide claims.
- Preserve the source authority, approval status, maturity, and scope of each referenced requirement or decision. A report does not approve architecture or resolve conflicting sources.

## Capability Status Integrity

Use the repository's canonical capability-status vocabulary from [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) only when the status is appropriate to the capability scope and supported by its evidence:

- `IMPLEMENTED`
- `ADAPTER-READY`
- `MOCKED`
- `EXPERIMENTAL`
- `NOT IMPLEMENTED`
- `BLOCKED`
- `UNKNOWN`

These are capability statuses, not task-progress, approval, test, deployment, or release states. Do not assign or upgrade a capability status merely because a file was created, a plan was written, an interface was documented, a command returned successfully, or a handoff occurred. If evidence is insufficient, report `UNKNOWN` and state what is unknown. Use `NOT IMPLEMENTED` only when available evidence establishes absence or only a placeholder/proposal for the required behavior. Preserve the definitions and evidence expectations in the cited source.

## Report Structure

Use only sections relevant to the request; keep reports concise when scope is small. A report may include:

1. **Objective and scope** — requested outcome and inspected or changed boundary.
2. **Work performed** — actions actually completed, partially completed, or attempted.
3. **Files or components changed** — exact paths when known; distinguish created, modified, and unchanged items only when observed.
4. **Evidence and findings** — significant claims linked to their supporting observations and source authority.
5. **Checks performed and results** — actual commands or tools and observed outcomes.
6. **Checks not performed** — tests, builds, reviews, or operational checks not run or not verified.
7. **Failures and limitations** — error, partial execution, environmental limits, and their impact.
8. **Unknowns, assumptions, and blockers** — clearly classified; identify what evidence or authority is needed when known.
9. **Status** — descriptive task status and, only when supported, the canonical capability status for a defined scope.
10. **Remaining work and authorization** — next action, dependency, or approval needed, without implying it is authorized.

Omit irrelevant sections rather than filling them with speculation or unsupported defaults. Do not create a separate template file as part of applying this Skill.

## Failed, Interrupted, and Incomplete Work

- Report a failed command or tool operation as failed, including its scope and captured error details when safe. Do not recast failure as success because later steps completed.
- For partial execution, specify what ran, what did not, and which outputs are available. Do not infer the final state from an interrupted operation.
- For conflicting, missing, or incomplete evidence, identify the conflict or gap and keep the conclusion qualified. Do not silently select the more convenient source.
- For environmental or tool limitations, state what could not be inspected or verified and how that limits confidence.
- For interrupted work, identify the last known verified state, unfinished activity, and safe continuation point. Do not claim completion.
- Distinguish work that was **not performed** from work that was attempted but **failed**, and from work that was performed but remains **not verified**.
- Do not automatically retry destructive, irreversible, externally visible, or consequential actions. Seek required authorization before any further attempt.

## Security and Evidence Integrity

- Redact secrets, credentials, private keys, tokens, personal data, and other sensitive information. Include only the minimum evidence needed to substantiate a claim.
- Preserve the distinction between observation and inference; label estimates, assumptions, and proposals explicitly.
- Do not manipulate, omit, or selectively summarize evidence to make a result appear successful.
- Respect source-of-truth, repository instructions, user scope, and required human approvals. Preserve unrelated user changes.
- Do not infer approval from silence, a successful command, a handoff, or an artifact's existence.
- Keep implementation, verification, approval, deployment, and operational readiness distinct. Never claim any occurred without supporting evidence.
- Do not claim repository-wide completeness, test success, security enforcement, provider compatibility, or end-to-end operation from partial or indirect evidence.

## Relationship to Other Skills

- [Repository audit](../repository-audit/SKILL.md) guides explicitly requested repository investigation; this Skill supports truthful reporting of its scoped findings.
- [Repository implementation](../repository-implementation/SKILL.md) guides authorized bounded implementation; a change report must not imply tests are run if they are prohibited or skipped.
- [Implementation planning](../implementation-planning/SKILL.md) defines proposed tasks and completion conditions; a plan is not evidence that work occurred.
- [Engineering handoff](../engineering-handoff/SKILL.md) transfers task context and evidence; a handoff or acknowledgment is not task completion.
- [Architecture decision record](../architecture-decision-record/SKILL.md) guides durable decision documentation; a report does not grant decision authority.

These Skills have distinct responsibilities. This Skill supports evidence-based reporting without replacing their procedures.

## Completion and Handoff Reporting

State clearly:

- what is established by evidence and the scope of that evidence;
- what was actually performed and what files or components changed;
- which checks ran, their observed results, and what was not performed or verified;
- what remains incomplete, unknown, blocked, or limited, and how those conditions affect confidence; and
- what further action, prerequisite, or authorization is required, if known.

For onward handoff, preserve the relevant evidence references, current observed state, failures, open questions, and authorization boundary. A polished report is not proof of successful implementation or operational readiness.

## Related Sources

- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Architecture traceability](../../architecture/ARCHITECTURE-TRACEABILITY.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)

# Spec-to-Implementation Workflow Foundation

## Purpose

This workflow defines a minimal, provider-neutral, evidence-driven bridge from a software requirement to a controlled implementation and verification cycle.

It is designed for the solo-maintainer repository: the Project Owner sets scope and authorization, and an explicitly capable coding agent may implement within those bounds. It coordinates requirement readiness, repository inspection, dependency analysis, implementation planning, controlled coding, validation, and evidence-based reporting without expanding into an automation platform or a provider-specific integration layer.

## Canonical Skill Reference

This workflow reuses the implementation Skill at ../../skills/implementation/SKILL.md rather than duplicating its content. The workflow defines the ordered stages and gates; the Skill defines the reusable operating rules for implementation work.

## Intended use

Use this workflow when:

- a task has a clear software objective and an expected deliverable
- the work is bounded to a repository change or a specific implementation path
- repository instructions and existing conventions need to be checked before coding
- validation evidence must be collected before a completion claim is made

This workflow is not for broad platform design, provider integration work, new Skill creation, or later-phase orchestration tasks.

## Entry conditions

A task is eligible only when the following are true:

- the objective is understood well enough to state a concrete deliverable
- the task scope is bounded to repository-local changes or documented dependencies
- the required repository instructions and conventions are inspectable
- relevant validation tools or checks exist or are explicitly identified as unavailable
- the task does not depend on an unresolved Project Owner decision or a separately required independent reviewer

If essential information is missing, the workflow must mark the task as blocked and stop.

## Required inputs

The workflow expects:

- task objective
- expected deliverable or outcome
- acceptance criteria
- authorized scope and exclusions
- security and compatibility constraints
- repository state and current working tree status
- relevant implementation files and docs
- validation commands available in the repo or identified as unavailable

## Stage A — Request intake

Input capture must record:

- task objective
- expected output
- acceptance criteria
- authorized scope
- constraints and dependencies
- security considerations
- required verification evidence

Decision gate:

- If objective, scope, or acceptance criteria are missing or contradictory, request clarification or stop as blocked.

Output:

- a scoped task brief suitable for implementation review

## Stage B — Specification readiness

Review the task for:

- clear requirements
- testable acceptance criteria
- explicit exclusions
- known dependencies and restrictions
- defined completion conditions

Required checks:

- identify mandatory information versus optional context
- distinguish fact from assumption
- reject silent scope expansion

### Specification readiness review checklist

Use this checklist to record evidence and gaps before implementation planning. For each item, record `PASS`, `FAIL`, `UNRESOLVED`, or `NOT APPLICABLE` as a review value, with a source or evidence reference where applicable. These values do not imply automated verification, specification acceptance, or implementation authorization.

- Scope, exclusions, inputs, and outputs are stated; normative requirements are distinguished from assumptions, inferences, and recommendations, with source references for normative requirements.
- Validation rules, ordering or precedence, diagnostics, error behavior, and relevant boundary cases are explicit enough to derive testable outcomes.
- Dependencies and technical prerequisites are identified; security constraints and compatibility claims are evidence-based and limitations are recorded.
- Acceptance criteria can be checked, and each normative requirement is traceable to its acceptance criterion and planned verification evidence. Record unavailable evidence rather than claiming verification.
- Conflicting or incomplete sections are identified. For each unresolved case, record the missing behavior, plausible interpretations where useful, the decision needed, and the evidence required; do not choose an interpretation by implication.
- Specification review status, specification acceptance status, and implementation authorization status are recorded separately. Identify an approving authority only when repository evidence establishes it; otherwise record the authority as unresolved.

Decision gate:

- If the task is not sufficiently specified for safe implementation, stop and report the blocker.

Output:

- a requirement summary and a clear yes/no readiness decision

## Stage C — Repository inspection

Inspect:

- repository instructions and contributor docs if present
- relevant implementation files and tests
- current Git state and working tree changes
- architecture or module contracts in scope
- related Skills, templates, or workflows
- validation commands that are already used by the repository

Safety rules:

- preserve pre-existing user and team work
- do not overwrite unrelated changes
- do not assume a tool exists without checking the repo
- avoid broad cleanup or unrelated refactoring

Output:

- a repository impact map and list of files or subsystems implicated by the change

## Stage D — Dependency and risk analysis

Evaluate:

- required files and components
- external dependencies and their impact
- interfaces, contracts, and compatibility constraints
- likely regressions for the touched area
- security-sensitive operations or data exposure
- file ownership boundaries, required approvals, and whether a genuinely independent reviewer is required

Decision gate:

- If the required dependency or approval cannot be safely resolved, stop the affected operation and record the blocker.

Output:

- dependency list, risk notes, and an explicit approval dependency list

## Stage E — Implementation plan

Create a bounded plan that includes:

- expected files to change
- intended modifications
- validation strategy
- risks and mitigations
- acceptance criteria for the main change

Restrictions:

- no unrelated refactoring
- no unauthorized scope expansion
- no changes outside the task boundary

Output:

- a small implementation plan suitable for review before coding begins

## Stage F — Controlled implementation

Implementation must:

- follow existing repository conventions
- reuse approved contracts and canonical Skills where appropriate
- make small, reviewable changes
- preserve unrelated modifications
- avoid unnecessary dependencies
- avoid unsupported provider-specific assumptions
- stop immediately if the task requires unauthorized decisions

Output:

- small, reviewable code or documentation changes within the approved scope

### Source-editing integration boundary

The current project runtime does not include a production caller that turns
an implementation request into source edits. `scripts.tool_framework.ToolAdapter`
is the existing provider-neutral extension interface:

- register an explicit `ToolContract` in the `ToolRegistry`
- implement `ToolAdapter.supports(contract)` and
  `ToolAdapter.execute(contract, inputs) -> Mapping[str, object]`
- register that adapter with the `ToolExecutor`
- reference the exact tool identifier from a `WorkflowDefinition` executed by
  `WorkflowEngine`

This interface is an integration seam, not an editor and not a permission
boundary. A future editor adapter must be backed by an actually available,
supported editing capability; validate the authorized repository root and
in-root target paths before any write; accept only explicit scoped inputs; and
return structured outcomes that identify changed artifacts and failures. It
must not execute caller-provided shell commands or obtain implicit secret
access. The framework's in-process adapters execute with host-process
permissions and do not provide sandbox isolation.

The existing workflow handoff records workflow results but does not yet
provide an authenticated source-change receipt. The bounded
`scripts.source_change_evidence` module now snapshots explicitly selected
repository-relative regular files and records created, modified, and deleted
paths with SHA-256 digests. Observation is capped at 256 paths, 16 MiB per
file, and 64 MiB total per snapshot. A configured caller can pass
`source_paths=(...)` to `execute_handoff_workflow(...)`; the workflow
snapshots those paths before execution and attaches the observed change report
before validation. Partial changes are still recorded when the workflow fails,
and an unavailable post-workflow snapshot is reported as `incomplete`, not as
“no changes.”

This is an observation of only the named paths. It neither constrains where a
ToolAdapter can write nor proves which actor made the changes; the handoff
marks it `authenticated: false`. It does not make `ToolAdapter` an editor.
Separately, `scripts.source_editing_workflow` provides an explicitly wired
local editor for caller-supplied contents under an exact application-level
path grant, with expected-hash checks, fixed validation operations, and
structured local test coverage. That workflow is not an AI edit generator or
provider integration, and its checks are not a host-enforced sandbox.
`scripts.source_editing_cli` exposes this workflow to a local caller using a
bounded JSON request and explicit command-line path grants. It is a provider-
neutral integration surface and runs only a fixed `git diff --check`; it does
not run caller-selected tests, generate edits, authenticate the caller, or
strengthen filesystem isolation.
Workflow and validation outcomes do not promote implementation, verification,
authorization, acceptance, or release.

## Stage G — Testing and debugging

Select validation based on repository evidence. Relevant options may include:

- existing unit tests
- linting or type-checking commands
- build steps
- focused smoke tests
- repository-local validation scripts

The repository's `scripts.validation_adapter` module provides a constrained
post-implementation CLI:

```text
python -B -m scripts.validation_adapter --repository-root . --task-objective "..." --unittest tests.test_MODULE --provider-manifest-check --git-diff-check
```

Only its explicitly listed fixed operations are accepted. It records real
process outcomes in JSON; a nonzero CLI result means at least one selected
check failed, timed out, or was blocked. This process is not a sandbox and does not edit code. A configured
`WorkflowEngine` caller can use `execute_handoff_workflow(...)` to attach both
actual workflow and validation results. No AI source-editing agent or
production task-to-edit-generation caller is registered; the local editor
accepts complete proposed contents and does not generate them.
The provider-manifest operation checks local configuration against canonical
Skill discovery only; it does not load or exercise the provider runtime.

Requirements:

- do not claim a test passed without evidence that it actually ran
- debug failures using reproducible evidence
- do not weaken tests to obtain a passing status
- disclose unavailable checks honestly as SKIPPED or NOT RUN

Output:

- executed validation commands and their observed results

## Stage H — Verification

Verification must compare actual changes against the requirement and the acceptance criteria.

Review:

- final diff
- changed-file scope
- functional behavior and edge cases
- error handling
- security and regression implications
- validation evidence
- known limitations

Important distinction:

- implementation completion is not equivalent to verified acceptance
- same-agent self-review is not independent verification
- automated tests are test evidence, not independent human review
- approval, authorization, CI, and release are separate outcomes

Output:

- a verification summary tied to the original specification and acceptance criteria

When reporting a tool, provider, or integration capability, distinguish its implementation description from verification status. Terms such as implemented, adapter-ready, mocked, experimental, or unimplemented are illustrative descriptions, not a required or exhaustive status taxonomy; use them only when the evidence supports them. Report verification using the applicable check outcomes and observed evidence, and report compatibility separately using the [repository compatibility status model](../../docs/compatibility/README.md). These descriptions and results do not imply acceptance or approval. Do not infer that a capability works from its documentation, interface, or presence alone; include relevant limitations and blocked or unrun checks.

## Stage I — Evidence report

Produce a final evidence report containing:

1. task and objective
2. specification readiness
3. repository areas inspected
4. files created or modified
5. implementation summary
6. commands actually executed
7. validation results
8. known failures and skipped checks
9. evidence supporting completion claims
10. security and regression risks
11. pending dependencies and approvals
12. final status
13. recommended next action

Minimum reporting format:

Task: <objective>
Status: PASS / PASS_WITH_WARNINGS / BLOCKED / FAIL
Scope: <bounded scope>
Repository areas inspected: <paths>
Files changed: <list>
Validation executed: <commands>
Results: <PASS/FAIL/SKIPPED/NOT RUN>
Evidence: <what was observed>
Known limitations: <notes>
Dependencies: <pending Project Owner decision or separately required verifier>
Next action: <next task without starting it>

## Stage J — Stop gate

The workflow stops after the authorized task and must not automatically:

- start another task
- expand scope beyond the approved change
- commit or push
- merge branches
- open a pull request
- deploy to production
- run destructive operations

These actions require separate authorization and a separate process.

## Failure handling and recovery

Treat the following as stop conditions:

- missing requirements or conflicting acceptance criteria
- repository state that prevents safe work
- missing dependencies or approvals
- failed validation without a safe, evidence-based fix
- security-sensitive operations lacking a safe path
- scope drift outside the approved task boundary

When blocked, report the blocker clearly and stop the affected work without continuing quietly.

## Security and scope constraints

This workflow requires:

- no secret or credential exposure in logs or source files
- no unsupported provider assumptions in the workflow itself
- no undocumented API behavior as default project policy
- no broad file moves or cleanup outside the task scope
- no weakening of tests or validation to reach a passing result

## Ubuntu compatibility and operating rules

The workflow must be expressed in Ubuntu-compatible terms. Documented commands must be appropriate to the actual repository and environment.

Rules:

- prefer repository-local tools and existing validation commands
- do not rely on PowerShell or Windows-specific paths in workflow guidance
- do not use sudo or global system changes without explicit approval
- clearly distinguish between commands actually executed and example commands
- never fabricate execution evidence

## Known limitations

This workflow is intentionally a foundation, not a complete automation system. It does not guarantee independent execution, enforced gates, or provider-specific enforcement. It provides a structured, reviewable process that must be paired with repository-native testing and actual validation evidence.

## Summary

This workflow foundation is designed to establish a disciplined and reviewable path from requirement through implementation and actual validation evidence, while preserving the canonical implementation Skill as the reusable source of implementation rules. If no capable editor is connected or a required independent verifier is unavailable, state that boundary and do not claim the corresponding stage complete.

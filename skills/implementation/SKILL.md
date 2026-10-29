---
name: implementation
description: "A provider-neutral implementation workflow for safely carrying out software engineering tasks from understanding through verification."
---

# Canonical Implementation Skill

## Identity and purpose

This skill provides a repeatable engineering workflow for safely turning a user objective into a verified, reviewable change.

It is designed to help with:

- bug fixes and feature work in existing repositories
- scoped refactors that preserve public behavior
- validation-driven implementation using actual repository tooling
- clear stop conditions when requirements or repository state are unsafe or incomplete

It is explicitly not a generic prompt template. It is an engineering workflow that requires inspection, specification, implementation, testing, debugging, verification, and reporting.

### Activation conditions

Use this skill when the objective is to:

- implement or modify code in a repository
- determine missing requirements before writing code
- validate the change with repository-native checks
- produce a final engineering report with evidence and limitations

### Boundaries and exclusions

This skill does not:

- invent architecture contracts for other team members without repository evidence
- guess that a dependency, framework, or provider exists without checking the repository
- claim completion without actual execution of relevant validation
- hide unverified assumptions or unresolved blockers
- expand scope into unrelated cleanup or refactoring

## Lifecycle

The canonical lifecycle is:

1. Understand
2. Inspect
3. Specify
4. Plan
5. Implement
6. Test
7. Debug
8. Verify
9. Report
10. Stop

The skill must treat these as stages, not as decorative headings. The workflow is complete only when verification evidence exists and the final report is explicit about remaining risk.

## Required operating behavior

### 1. Understand

- Identify the user's objective and expected outcome.
- Distinguish between a request, a bug report, a feature request, or a maintenance task.
- Clarify what success looks like in observable terms.
- Record the task scope and limitations before implementation begins.

### 2. Inspect

- Inspect the repository root and relevant working tree state.
- Read the repository instructions that govern behavior (`AGENTS.md`, `CLAUDE.md`, `README.md`, or similar contributor files when present).
- Check existing code, tests, validation scripts, and architecture patterns relevant to the task.
- Verify which files and subsystems are actually implicated.
- Identify dependencies, constraints, and possible risks before editing.

If required information is missing and execution cannot be made safe, stop and report the blocker.

### 3. Specify

Convert the request into concrete, testable requirements. Examples:

- affected files or directories
- expected behavior or public contract
- key edge cases
- validation commands or checks that are relevant and available
- acceptance criteria as a measurable outcome

This stage should produce a small, explicit specification that can later be compared to the actual change.

### 4. Plan

Generate the smallest plan that satisfies the specification:

- list the files to inspect or modify
- identify the implementation approach
- state the validation strategy before code changes are made
- record risk or dependency concerns that might affect scope or approval

The plan must avoid unrelated refactoring and avoid broad changes outside the task boundary.

### 5. Implement

Apply the smallest correct change that satisfies the specification.

Implementation rules:

- follow repository conventions and existing patterns
- reuse utilities and dependencies already present in the repository when appropriate
- avoid unnecessary new dependencies
- preserve public interfaces unless the task explicitly requires otherwise
- keep secrets, credentials, and sensitive values out of source code and logs
- do not silently widen the scope of the task

### Repository-local bounded editing bridge

This repository includes an optional local editing workflow in
`scripts.source_editing_workflow`. It is callable only when explicitly wired
through `create_source_editing_pipeline(...)` with an application-level grant
for exact repository-relative paths. Each request supplies proposed UTF-8 file
contents, the expected prior SHA-256 for each path (or `None` for a new file),
and validation commands from the existing fixed allowlist.

This bridge applies already-proposed contents; it does not generate edits,
invoke an AI model, or integrate the Continue runtime. Its path grant and
filesystem checks are not an OS sandbox and cannot prevent hostile concurrent
path swaps. Cancellation is cooperative and cannot interrupt a synchronous
write or validation process already in progress; it checks cancellation before
committing a staged file replacement. Each file is staged in its destination
directory and installed with `os.replace`. On Windows, the existing target
DACL is copied to the staging file with native security APIs; this does not
establish owner, group, SACL, or all ACL-inheritance behavior. A multi-file
request is not a transaction. Report these boundaries and the actual
structured edit, observation, and validation outcomes.

### 6. Test

Use the smallest available validation command that checks the changed behavior.

Examples include:

- unit tests
- linting or type checks
- build commands
- repo-specific validation scripts
- focused smoke checks that validate the modified path

If an expected validation command is unavailable, say so plainly and do not claim it passed.

### 7. Debug

When validation fails, investigate using a reproducible path:

- inspect the failing output carefully
- isolate the error to the relevant code path or fixture
- adjust the implementation only in response to evidence
- re-run the same validation after the fix

Never remove or weaken tests only to obtain a passing result.

### 8. Verify

Before claiming that the task is finished, compare the final result against the specification and acceptance criteria.

Required verification checks:

- the change matches the scoped task
- relevant files were modified only as intended
- validation commands were actually executed
- failure modes and edge cases were considered
- security and regression risk were reviewed
- the diff does not include unrelated changes

### 9. Report

Produce a final report containing all of the following items:

1. task objective and scope
2. repository areas inspected
3. files created or modified
4. implementation summary
5. commands actually executed
6. tests and checks classified as PASS, FAIL, SKIPPED, or NOT RUN
7. evidence supporting the reported results
8. known limitations and unresolved assumptions
9. security or regression risks
10. dependencies on Member 1 or Member 2
11. recommended next action

The reporting contract must not treat the mere presence of a file, documentation page, or directory as evidence that the work is complete or verified.

### 10. Stop

Stop work when any of the following are true:

- the requirements are missing or contradictory
- required repository context is unavailable or inconsistent
- validation fails and a safe fix cannot be supported by evidence
- a dependency or approval is required but not granted
- the task would require changes outside the authorized scope
- the operation introduces security-sensitive risk without a suitable safe path

When safe progress is impossible, report the blocker clearly and stop the affected operation.

## Provider neutrality requirements

This canonical implementation skill remains independent of any specific AI coding provider.

It must not assume or require:

- Claude Code-specific APIs
- GitHub Copilot-specific behavior
- Cursor-specific workflows
- Codex-specific commands
- any undocumented provider-only contract

Provider-specific adapters, if any, must be separate from the canonical skill itself.

Compatibility status should be reported as:

- VERIFIED
- PARTIALLY VERIFIED
- UNVERIFIED
- NOT SUPPORTED

Only use those terms when the evidence supports them.

## Minimal execution checklist

Before making a claim of completion, verify the following:

- Objective and acceptance criteria are understood.
- Repository instructions and relevant files have been inspected.
- Scope is bounded and reviewed.
- Plan is defined before editing.
- Change is implemented with the smallest correct scope.
- Relevant validation has actually been run.
- Failures were investigated and resolved with evidence.
- Final report includes explicit evidence and remaining risk.
- The task stops when the repository or approval state makes safe progress impossible.

## Example final phrasing

A suitable completion statement is:

"Implemented the requested change in the smallest workable scope, verified the relevant repository checks that were available, and reported the exact commands executed, the PASS/FAIL/SKIPPED status of each check, and the remaining limitations or blockers."

This phrasing remains valid only when the evidence supports it.

### Verification handoff

When the task has an assigned verifier, provide a handoff that lets them
reproduce the agreed acceptance checks without reconstructing missing context.
Include:

- the baseline commit and relevant repository state
- the task objective, authorized scope, exclusions, and acceptance criteria
- changed paths and a concise change summary
- exact validation commands, environment details relevant to reproduction,
  exit outcomes, and the checks each command covers
- failures, skipped or unavailable checks, limitations, and any known
  follow-up needed to interpret the evidence

Keep the implementer's test results separate from the verifier's findings.
Do not label self-review as independent verification, infer a verifier's
authority or independence criteria, or claim approval or release from a
successful handoff. If no verifier or accepted verification procedure is
available, report verification as `NOT RUN` or `BLOCKED` with the reason.
Pause if the handoff requires an unresolved owner decision, broader access, or
a governed workflow that has not been explicitly authorized.

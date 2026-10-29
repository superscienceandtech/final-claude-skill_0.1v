# Contributing

## Scope and ownership

Contributions must remain inside one bounded objective. Inspect the repository before editing, preserve existing behavior, and do not modify unrelated subsystems or pre-existing user work.

`docs/architecture/team-file-ownership.md` contains proposed ownership coordination. It does not grant approval authority or external-service permissions. Unlisted paths remain unassigned until team ownership is explicitly recorded.

## Architecture and specification alignment

Contributions must follow the approved Final Architecture Baseline and existing repository contracts. Proposal-level architecture documents under `docs/architecture/` are not approved solely because they exist in the repository.

Before implementation:

1. Identify the objective, acceptance criteria, exclusions, and dependencies.
2. Inspect applicable existing Skills, scripts, tests, workflows, and architecture documents.
3. Separate facts, assumptions, implementation evidence, evaluation evidence, and approval status.
4. Stop if requirements conflict or a required decision or authorization is unresolved.
5. Complete only the authorized task.

Do not introduce a new mandatory directory, provider integration, tool dependency, architecture level, or runtime capability through an unrelated change.

## Modification boundaries

- Work only inside the repository.
- Prefer the smallest reviewable change.
- Do not relocate architecture documents as part of a governance change.
- Do not modify provider, integration, agent, registry, template, test, CI, Skill, script, or framework code unless explicitly in scope.
- Keep canonical behavior provider-neutral. Provider adapters must remain separate implementations where introduced by an approved task.
- Do not overwrite substantive existing content without reconciliation.

## Documentation conventions

Use repository-relative Markdown links for repository paths. Mark proposals, provisional decisions, unresolved approvals, and unverified capabilities clearly. Do not present planned work as implemented or verified.

Documentation should distinguish:

- observed repository facts;
- implementation descriptions;
- evaluation or test evidence;
- approval decisions;
- remaining unknowns and blockers.

## Skills, agents, providers, and integrations

A canonical Skill must have a clear purpose, scope, inputs, outputs, stop conditions, permission boundaries, and references to existing repository files. It must not claim provider-specific support without evidence of that provider's adapter and validation.

Agent roles must define responsibility, boundaries, inputs, outputs, delegation, conflict handling, and applicable permissions. Provider compatibility requires a separate adapter or configuration plus compatibility evidence.

Integrations must use least privilege, explicit tool allowlists, bounded input and output behavior, safe failure handling, and human approval for consequential operations. Tool, provider, or credential availability must not be inferred from documentation.

## Traceability and evidence

Every change should link its requirement or issue to:

- the files changed;
- the repository-native validation performed;
- observed PASS, FAIL, SKIPPED, or NOT RUN results;
- known limitations;
- approval or dependency status.

Do not claim tests passed when they were not run. Do not claim implementation completion where only a specification or interface exists. Test and review status remain distinct from approval and release status.

## Review and approval

Changes require human review appropriate to the repository's established ownership and security boundaries. Independent verification should be separate from implementation when the project has adopted that process.

Sensitive, destructive, externally visible, or irreversible operations require explicit human authorization. Reviewers should verify scope, evidence, security implications, documentation consistency, and unresolved claims.

## Git and execution restrictions

Do not switch branches or perform fetch, pull, merge, rebase, cherry-pick, commit, push, deployment, or history rewrite unless the task explicitly authorizes the operation. Do not install packages or dependencies unless separately requested.

For repository-native validation, prefer the smallest relevant existing check. Record the exact command and result; never weaken a check or change a test only to obtain success.

Stop after the assigned task. Do not begin another implementation or expansion automatically.

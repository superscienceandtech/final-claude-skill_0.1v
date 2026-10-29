# Claude Repository Entry Instructions

## Identify and inspect

This repository is Claude Skills: a provider-neutral, skill-driven engineering platform that supports governed implementation and validation. It is not the SUPER AGI runtime.

Start from this file and follow the repository-wide requirements in [`AGENTS.md`](AGENTS.md). `AGENTS.md` is the primary repository instruction for AI agents; this file provides Claude-specific entry guidance only and must not maintain a conflicting copy of repository policy.

## Architecture and documentation

The approved Final Architecture Baseline governs repository requirements. Existing architecture proposals and decisions are currently under:

- [`docs/architecture/`](docs/architecture/)
- [`docs/audits/`](docs/audits/)
- [`docs/compatibility/`](docs/compatibility/)
- [`docs/tool-setup/`](docs/tool-setup/)

Only explicitly approved documents are approved sources of decisions. Architecture documents labeled proposed, provisional, pending, draft, or coordination guidance must be treated as unresolved until separate evidence records approval.

## Skills and workflows

Discover relevant instructions before editing:

1. Inspect `AGENTS.md`, repository documentation, and files in the assigned scope.
2. Check `skills/` for applicable canonical Skill definitions.
3. Check `workflows/` for repository-specific lifecycle guidance.
4. Do not infer provider support or runtime behavior from documentation alone.

The implementation workflow is documented at [`workflows/spec-to-implementation/README.md`](workflows/spec-to-implementation/README.md). Provider-specific behavior belongs in separate provider adapters when those components are authorized.

## Scope and security

- Complete one bounded task per prompt and stop at that task boundary.
- Preserve existing work and the current Git state.
- Do not switch branches or perform history-changing operations without explicit authorization.
- Do not install dependencies, access external services, or modify files outside the repository unless separately authorized.
- Use read-only discovery and least-privilege execution.
- Obtain human approval for destructive, irreversible, sensitive, externally visible, or consequential operations.
- Do not expose secrets or represent unexecuted checks as passed.

Before making a completion claim, compare changes with the requested scope and report actual evidence, limitations, blockers, and unresolved approvals. Validation should not be claimed as run if it was prohibited or skipped.

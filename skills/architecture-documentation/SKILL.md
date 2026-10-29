---
name: "architecture-documentation"
description: "Use when creating or updating source-grounded architecture documentation, documenting proposals or unresolved questions, or improving architecture source attribution and traceability."
---

# Architecture Documentation

## Purpose

Create or update architecture documentation for the `claude-skills` repository with source-grounded statements, explicit authority and maturity boundaries, and traceable references. This Skill is reusable across AI coding providers; it is a procedure, not an execution sandbox, approval, or security boundary.

The repository is the provider-neutral engineering platform for building and maintaining SUPER AGI. It is not the SUPER AGI runtime. Preserve the product direction: one Super AGI, one Unified Brain, 100 specialized intelligence modules, dedicated navbars/workspaces, and shared universal infrastructure. Do not describe the 100 modules as 100 independent AI products.

## When to Use

Use this Skill when the task is to:

- create a bounded architecture specification or technical architecture document;
- update an existing architecture document within explicit scope;
- write a source-grounded explanation of architecture intent or constraints;
- document a proposal or unresolved architecture question without deciding it; or
- improve source attribution, relative links, and documentation-level traceability.

Do not use this Skill to implement runtime functionality, provider adapters, tools, or integrations; create a new architecture direction beyond the request; or change a decision's status or outcome without the required authority and evidence. If documentation depends on an unresolved decision, document the dependency and stop rather than inventing a resolution.

## Required Inputs

Before editing, identify:

- the exact requested document and deliverable;
- authorized files and explicit exclusions;
- required content, acceptance criteria, and stopping point;
- relevant repository instructions and architecture sources; and
- whether the task prohibits validation, tests, or other operations.

If scope or authority is materially unclear, ask for clarification through the available interaction mechanism or report the blocker. Do not expand scope to compensate.

## Workflow

1. **Bound the deliverable.** Record the target path, requested change, allowed file scope, exclusions, completion criteria, and prohibited operations. Confirm whether the file already exists; preserve its substantive content and existing work.

2. **Read applicable instructions and sources.** Read `AGENTS.md` and `CLAUDE.md`, then inspect the target and relevant sources named by the task. Reuse existing architecture material rather than assuming a definition is absent. Read only as much additional material as needed to support the requested document.

3. **Classify source authority and maturity.** For each consequential statement, determine whether it is an established source statement, an explicitly accepted decision within its evidence scope, proposed architecture, an assumption, a hypothetical example, or unresolved. Consult `SOURCE_OF_TRUTH.md`, the relevant decision registers, and `OPEN-DECISIONS.md` as applicable. A document's presence does not establish approval.

4. **Define purpose and boundaries.** State the document's purpose, intended audience, system/component scope, non-goals, and exclusions. Preserve the boundary between the `claude-skills` engineering platform and the SUPER AGI runtime.

5. **Draft to the applicable conventions.** Use `DOCUMENTATION-STANDARDS.md` as proposed guidance where relevant. Include only sections needed for the deliverable; do not make a proposed convention mandatory or create another architecture overview or policy document unless requested.

6. **Preserve canonical terms and identifiers.** Reuse terminology from `ARCHITECTURE-GLOSSARY.md` and relevant source documents. Preserve the exact capability-status vocabulary and meanings in `CAPABILITY-STATUS.md`. Use existing identifiers only within their documented scope; label proposed identifier conventions as proposed. Do not create competing conventions.

7. **Add source references.** Link to actual, existing repository paths using relative Markdown links. Cite relevant sections or established identifiers when available. Ensure each linked statement preserves the source's scope and maturity. Do not invent paths, approvals, line numbers, or evidence references.

8. **Separate claim types.** Clearly distinguish established statements, proposed designs, hypothetical examples, unresolved questions, and evidence-supported implementation claims. Distinguish documentation relationships from runtime dependencies. Label examples hypothetical unless they are actual repository records.

9. **Handle uncertainty and conflicts.** Record missing evidence and unresolved questions with relevant sources and open-decision references when a matching entry exists. If sources conflict or authority is unclear, preserve the qualifications, describe the ambiguity, and do not silently select a winner or change a decision.

10. **Review scope and claims.** Confirm the draft satisfies the request without unrelated changes. Check that no statement upgrades a proposal to accepted architecture or claims implementation, compatibility, security enforcement, operational readiness, AGI, or consciousness without supporting evidence.

11. **Validate only as authorized.** If link checking or another documentation check is permitted and actually performed, record the exact scope and result. Do not run tests or quality gates when prohibited. Do not imply a check occurred because a file exists or because the document looks complete.

12. **Stop at the task boundary.** Do not create supporting files, schemas, scripts, registries, or follow-up work unless explicitly requested. Stop after the requested documentation deliverable is complete.

## Source and Evidence Safeguards

- Never invent approvals, accepted decisions, source references, line numbers, implementation artifacts, or capabilities.
- Never treat a file, directory, identifier, interface, declaration, or generated document as proof of implementation or operational behavior.
- Preserve the canonical capability statuses exactly: `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, and `UNKNOWN`.
- Keep decision-record status, open-decision status, document maturity, capability status, verification, approval, and deployment distinct.
- Label illustrative or hypothetical examples clearly; do not present them as existing records or evidence.
- Record unavailable evidence and unresolved questions honestly. Insufficient evidence is not evidence of absence.
- Describe only the scope actually supported by evidence; do not generalize a component observation to a complete workflow or system.
- Avoid silently resolving conflicts among source documents or elevating proposal-level text to approved architecture.
- Treat provider-specific requirements as adapter-boundary details only where source authority supports them; keep the canonical architecture provider-neutral.

## Scope and Repository Safety

- Follow the user's explicit task scope and the repository's `AGENTS.md` and `CLAUDE.md` instructions.
- Modify only files authorized by the active task; preserve unrelated content and existing untracked files.
- Do not create supporting files unless the active task explicitly requests them.
- Do not switch branches or fetch, pull, merge, rebase, cherry-pick, commit, or push unless separately authorized.
- Do not access external services, install dependencies, or run tests when not authorized.
- Require human approval for destructive, irreversible, sensitive, externally visible, production, or otherwise consequential operations under applicable repository policy.
- Stop if required authority is absent or the task requires an unapproved architecture decision.

## Completion Report

Provide a concise, evidence-based report:

1. **Artifact:** requested document path created or updated.
2. **Substance:** brief summary of the documented change.
3. **Sources and limitations:** material authority/maturity qualifications and unresolved questions.
4. **Links:** link-check result only if checked, with actual scope and outcome.
5. **Scope:** whether any files beyond the authorized scope changed; identify actual changed files.
6. **Validation and Git:** state whether tests and Git history operations were performed; do not claim unrun checks or unauthorized actions.

Never report approval, verification, security enforcement, provider compatibility, or operational readiness unless the corresponding authority or evidence was actually established.

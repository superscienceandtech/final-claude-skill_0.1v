---
name: "skill-authoring"
description: "Use when creating or updating canonical provider-neutral Skills, refining their instructions, or defining their inputs, outputs, scope, and completion criteria."
---

# Skill Authoring

## Purpose

Create or update one canonical Skill for the `claude-skills` repository while preserving repository architecture, scope boundaries, security expectations, and evidence discipline. A canonical Skill is a reusable, provider-neutral set of instructions for a coherent capability or task family.

The `claude-skills` repository is the provider-neutral engineering platform for building and maintaining SUPER AGI; it is not the SUPER AGI runtime. Preserve the product direction: one Super AGI, one Unified Brain, 100 specialized intelligence modules, dedicated navbars/workspaces, and shared universal infrastructure. Do not describe the 100 modules as 100 independent AI systems.

This Skill is a provider-neutral authoring procedure, not an execution sandbox, security boundary, approval, Skill registry, or runtime component.

## When to Use

Use this Skill when:

- creating a new canonical Skill;
- updating an existing canonical Skill;
- improving instructions for a Skill's coherent task family;
- separating reusable instructions from provider-specific behavior; or
- defining a Skill's activation conditions, inputs, outputs, scope boundaries, and completion criteria.

Do not use it to independently authorize unrelated code changes, resolve an architecture decision, create provider adapters or tool integrations, or claim that a Skill is registered, discovered, executed, or supported by a provider. Provider-specific artifacts require explicit task scope and authority.

## Canonical Skill Design Principles

- **Provider-neutral by default:** State shared task logic without requiring a particular coding agent, vendor syntax, or provider API.
- **One coherent responsibility:** Keep one Skill focused on a capability or related task family. Split unrelated responsibilities only when separately authorized; avoid unnecessary duplication.
- **Reusable:** State procedures and boundaries that can be applied across compatible coding agents and repositories where applicable.
- **Explicit activation:** Describe when to use the Skill and when not to use it, including exclusions and stop conditions.
- **Actionable:** Give ordered, imperative instructions rather than only describing goals or principles.
- **Defined interaction:** Identify required inputs, expected outputs, boundaries, and completion conditions.
- **Source-grounded:** Follow authoritative repository sources and preserve their scope, maturity, and terminology.
- **Evidence-aware:** Distinguish declared behavior from observed execution, verification, approval, and operational readiness.
- **Governed:** Preserve security, least-privilege, human-approval, and repository-protection requirements relevant to the task.
- **Extensible:** Refer to existing shared instructions and sources rather than copying them or embedding provider-specific behavior in canonical content.

A Skill is not interchangeable with:

- an **agent role**, which describes a role's responsibilities and handoffs;
- a **workflow**, which coordinates stages and gates;
- a **provider adapter**, which translates canonical behavior into provider-specific form;
- a **tool integration**, which defines access to a local or external capability; or
- an **executable runtime component**, which implements behavior.

These are responsibility distinctions, not claims that every category is implemented. A Skill document does not execute itself or grant permissions.

## Recommended `SKILL.md` Structure

Use the established repository convention: YAML frontmatter with `name` and `description`. Follow any additional metadata only when existing repository evidence and the active task support it; do not invent fields.

The following body sections are practical and may be omitted when irrelevant:

1. **Purpose** — explain the Skill's coherent task responsibility.
2. **Activation conditions** — state when to use it and exclusions.
3. **Scope and exclusions** — identify included work, limits, and stop conditions.
4. **Required inputs and context** — state information needed and how to handle missing inputs.
5. **Ordered procedure** — provide actionable steps for the task.
6. **Decision boundaries and exception handling** — describe when to stop, ask for clarification, or report a blocker.
7. **Output requirements** — define deliverables, format, and evidence boundaries.
8. **Safety, permissions, and repository protection** — include applicable safeguards.
9. **Completion reporting** — specify concise, truthful reporting expectations.
10. **Related sources** — link only to relevant, existing repository documents.

Do not add empty or irrelevant sections just to match this list. Do not create a separate template file unless the active task explicitly requests one.

## Authoring Procedure

1. **Identify the request.** Determine the Skill name, exact target path, requested responsibility, acceptance criteria, authorized files, exclusions, and stopping point.

2. **Inspect instructions and sources.** Read `AGENTS.md` and `CLAUDE.md`; inspect the relevant architecture and Skill sources named by the task. Use only available, relevant source content. Do not assume missing files or instructions.

3. **Check for existing Skills.** Inspect the Skills directory and search for an existing Skill with overlapping purpose. Reuse compatible instructions or update an existing Skill only if authorized. Avoid creating duplicate responsibilities.

4. **Define one responsibility.** State the coherent task family and explicit activation and non-activation conditions. Keep unrelated architecture, implementation, and integration work outside the Skill.

5. **Specify interaction boundaries.** Identify required inputs, expected outputs, permissions, file scope, failure/uncertainty handling, and conditions for stopping. Do not assume missing approvals or dependencies.

6. **Write concise, actionable instructions.** Use direct imperative language and an ordered procedure. Include enough detail for a compatible agent to carry out the task without converting architecture principles into vague aspirations.

7. **Separate shared logic from provider-specific behavior.** Keep canonical task steps, constraints, and output expectations provider-neutral. Put provider invocation syntax, provider-specific metadata or packaging, tool commands, and optional integration requirements in separate provider-specific artifacts only when explicitly authorized. Do not require Cursor, Claude, GitHub Copilot, Codex, Gemini, OpenCode, or another single provider for canonical Skill behavior.

8. **Link verified sources.** Use relative Markdown links to actual repository paths and confirm targets when feasible. Preserve the source's authority and maturity. Do not invent references, approvals, identifiers, line numbers, or implementation evidence.

9. **Preserve governance and evidence boundaries.** Use established terminology. Distinguish established source statements, proposed conventions, unresolved decisions, examples, and evidence-supported claims. Do not silently settle open decisions. Preserve the canonical capability-status vocabulary and meanings in `architecture/CAPABILITY-STATUS.md`.

10. **Keep the change scoped.** Modify only files authorized by the active task. Preserve unrelated work and existing untracked files. Do not create supporting files unless requested.

11. **Report truthfully and stop.** Summarize the Skill artifact and its boundaries; report actual checks, changed files, limitations, and unresolved matters. Stop when the requested Skill task is complete.

## Decision Boundaries and Exception Handling

- If the requested responsibility duplicates or conflicts with an existing Skill, inspect the sources and follow the authorized scope; do not silently redefine another Skill.
- If instructions conflict with an authoritative source or an unresolved decision controls safe work, preserve the conflict, cite the affected sources, and stop or request direction.
- If inputs, permissions, source files, or evidence are unavailable, state what is missing and do not fabricate a successful outcome.
- Do not infer approval authority from authorship, file ownership, a Skill name, or a proposed convention.
- A Skill declaration or file's presence is not proof of registration, discovery, execution, security enforcement, or operational capability.

## Security and Repository Scope

- Follow the user's explicit task scope and applicable `AGENTS.md` and `CLAUDE.md` instructions.
- Do not expose secrets, credentials, private keys, tokens, or sensitive user data; never embed credentials in Skill instructions.
- Do not instruct an agent to bypass authorization, repository protections, security review, or required human approval.
- Do not modify unrelated files; preserve existing untracked work.
- Do not create additional Skills, templates, manifests, scripts, schemas, adapters, or integrations unless the active task explicitly requests them.
- Do not switch branches or fetch, pull, merge, rebase, cherry-pick, commit, or push unless separately authorized.
- Do not run tests or other quality gates when prohibited. Do not claim a check occurred unless it actually occurred.
- Stop after completing the requested Skill task rather than starting another phase.

## Completion Report

Provide a concise, evidence-based report covering:

1. **Skill artifact:** exact file created or updated.
2. **Responsibility and activation:** what the Skill does and when it applies.
3. **Procedure and safeguards:** key workflow steps, provider boundaries, and evidence rules.
4. **Limitations:** source or authority limits and unresolved questions.
5. **Scope:** whether any files beyond the authorized scope changed.
6. **Validation and Git:** checks actually performed, whether tests ran, and whether Git history operations occurred.

Do not claim validation, testing, approval, registration, provider discovery, execution, integration, or operational capability without direct evidence.

## Related Skills and Sources

- [Skills overview](../README.md)
- [Architecture documentation](../architecture-documentation/SKILL.md)
- [Repository audit](../repository-audit/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Product constitution](../../architecture/PRODUCT_CONSTITUTION.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [Architecture glossary](../../architecture/ARCHITECTURE-GLOSSARY.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)
- [Architecture traceability](../../architecture/ARCHITECTURE-TRACEABILITY.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)
- [Module contract](../../architecture/MODULE-CONTRACT.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)

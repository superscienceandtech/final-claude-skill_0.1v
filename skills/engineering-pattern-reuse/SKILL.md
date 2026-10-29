---
name: "engineering-pattern-reuse"
description: "Use when discovering, evaluating, applying, or extending repository patterns without unnecessary duplication, abstraction, or architecture drift."
---

# Engineering Pattern Reuse

## Purpose and Applicability

Use this Skill when implementing an engineering change and deciding whether an existing design or implementation pattern can appropriately solve the current problem. Pattern reuse can apply to architecture, modules, interfaces, adapters, workflows, documentation, configuration, and automation.

A pattern is a way of addressing a recurring problem in a particular context. Reuse does not mean abstracting every repeated line of code, forcing unrelated components into the same implementation, or treating every existing example as a requirement. This Skill complements [`engineering-standards-conventions`](../engineering-standards-conventions/SKILL.md): that Skill focuses on applicable expectations and conventions; this one focuses on finding and deciding whether to reuse a concrete pattern.

## Core Principles

- Start from the authorized requirement and relevant contract, not from a desire to generalize.
- Ground claims about existing patterns in concrete repository evidence.
- Reuse a pattern only when its purpose, assumptions, and boundaries fit the current task.
- Prefer the smallest cohesive solution that satisfies the requirement.
- Preserve module ownership, provider neutrality, security boundaries, and existing behavior.
- Keep documented intent, proposed architecture, prototypes, mocked behavior, and demonstrated implementation distinct.
- Do not treat reuse as approval to expand task scope or modify additional files.

The `claude-skill_sonjoy` repository is the provider-neutral engineering and Skills platform for building and maintaining SUPER AGI, not the SUPER AGI runtime. The product direction is one unified SUPER AGI system with specialized intelligence modules and shared universal infrastructure, not disconnected independent AGI products. This direction does not require identical internal implementations for every module.

## When to Use

Use this Skill before introducing a new abstraction, interface, adapter, workflow, schema, utility, or documentation structure when a similar responsibility may already exist. It is also useful when extending a pattern across components, reviewing apparent duplication, or deciding whether a shared implementation would create inappropriate coupling.

Do not use it to initiate an unrelated refactor, architecture redesign, repository-wide duplication audit, or new framework. Those activities require explicit task scope and authority.

## Pattern Discovery

Before creating or extending a pattern:

1. Identify the specific requirement, affected boundary, expected deliverable, and authorized files.
2. Read applicable repository instructions and relevant canonical architecture or contract documents. Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) for authority and maturity.
3. Inspect existing implementations with similar responsibilities and contexts. Compare actual behavior and interfaces rather than names or surface resemblance alone.
4. Search the relevant Skill, schema, template, registry, script, provider adapter, or documentation only when it materially informs the task and is within permitted access.
5. Note relevant naming, error-handling, configuration, lifecycle, compatibility, ownership, and documentation practices.
6. Record the source of each candidate pattern and distinguish observed evidence from assumptions, recommendations, and proposed designs.

An architecture document can describe intent without demonstrating implementation. A directory, interface, sample, schema, or declaration alone does not establish operational behavior, approval, or suitability for reuse.

## Pattern Classification

For reasoning within a task, it can be useful to describe findings as:

- **Explicit requirement:** a task or applicable authoritative source requires the behavior or boundary.
- **Observed pattern:** a concrete repository implementation or document exhibits the approach; its applicability still needs assessment.
- **Candidate for reuse:** an observed pattern that appears relevant but has not yet been shown to fit.
- **Proposed pattern:** an approach suggested for the current task but not established as repository practice.
- **Legacy or deprecated pattern:** describe it this way only when repository evidence supports that status.
- **Anti-pattern:** describe it this way only when an applicable documented constraint or concrete failure evidence supports the characterization.

These are working descriptions for analysis, not an official repository taxonomy, status system, approval process, or scoring method. An isolated implementation or example does not by itself establish a universal standard. Use [`engineering-standards-conventions`](../engineering-standards-conventions/SKILL.md) when deciding whether a pattern is an established convention or merely observed.

## Reuse Decision Guidance

Decide whether to reuse, adapt, extend, or avoid a candidate by considering:

- whether it solves the same underlying problem under comparable assumptions;
- whether it respects current requirements, contracts, architecture boundaries, and ownership;
- whether it is proportionate to the current task's scope and complexity;
- its maintenance cost, cognitive overhead, and effect on existing behavior;
- provider neutrality and portability where required;
- security, permission, trust-boundary, and data-handling implications; and
- whether sharing it reduces genuine duplication or instead creates unnecessary coupling or premature abstraction.

No numeric score or rigid threshold is required. Reuse a pattern directly when its demonstrated behavior and constraints fit. Adapt it only as much as justified by the task, and make material differences explicit. Avoid or defer reuse when its authority, behavior, dependencies, security properties, or applicability is uncertain in a way that affects correctness.

## Duplication and Abstraction

Distinguish repeated implementation of the same stable responsibility from legitimate independent behavior in different domains. Similar-looking code, configuration, or text may encode different contracts, permissions, lifecycles, or failure behavior.

- Reuse an existing abstraction when it actually satisfies the requirement and its behavior is evidenced.
- Do not add a parallel utility, duplicate schema, competing registry, or redundant configuration mechanism when a suitable authorized implementation already exists.
- Do not generalize solely because two implementations look similar; establish the shared requirement and stable boundary first.
- Keep any new abstraction small, cohesive, explicit, and proportionate to demonstrated needs.
- Preserve independent module boundaries when common implementation would couple unrelated responsibilities or weaken ownership.
- Do not assume shared infrastructure is implemented merely because it is described in architecture documents.

## Implementation Workflow

1. **Identify the requirement and boundary.** Confirm the requested outcome, affected contract, authorized scope, and relevant constraints.
2. **Locate concrete evidence.** Find a relevant pattern and its actual source; record whether it is implementation, documentation, proposal, or example.
3. **Check fit and consequences.** Compare assumptions, dependencies, ownership, compatibility, provider boundaries, security implications, and maintenance costs.
4. **Choose proportionately.** Reuse directly when appropriate, make the smallest justified adaptation, or implement a distinct solution when the pattern does not fit.
5. **Preserve scope and behavior.** Follow [`task-scope-control`](../task-scope-control/SKILL.md); preserve existing behavior and unrelated tracked and untracked changes. Keep new abstractions and dependencies within explicit authorization.
6. **Document material deviations only.** Explain a significant adaptation or non-reuse decision when it affects maintainability, compatibility, or future work. Do not create unnecessary documentation or files.
7. **Report what was actually done.** Identify the source pattern, whether it was reused or adapted, meaningful limitations, and checks actually performed. Do not claim inspection, validation, or operation without evidence.

## Cross-Provider and SUPER AGI Architecture Considerations

Keep canonical Skills and shared engineering behavior provider-neutral, with provider-specific behavior placed in adapters where the applicable architecture and task authorize it. Reuse shared infrastructure where its existence, interface, authority, and behavior are supported; preserve legitimate domain-specific module behavior and explicit ownership.

[`MODULE-CONTRACT.md`](../../architecture/MODULE-CONTRACT.md) describes a proposed common module contract and leaves aspects such as final fields, identifiers, schemas, protocols, conformance authority, and runtime enforcement unresolved. Do not present its proposed details as an approved implementation contract without separate evidence. Likewise, do not claim a proposed or mocked implementation is operational.

Use [`SYSTEM-BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md), [`ARCHITECTURE-PRINCIPLES.md`](../../architecture/ARCHITECTURE-PRINCIPLES.md), and [`UNIVERSAL-INFRASTRUCTURE.md`](../../architecture/UNIVERSAL-INFRASTRUCTURE.md) as relevant while preserving each source's recorded maturity and scope.

## Conflicts and Missing Patterns

If existing patterns conflict, a candidate violates an explicit requirement, applicability is uncertain, or evidence for a claimed convention is missing:

1. Identify the actual sources, the conflicting behavior or assumptions, and what remains unknown.
2. Check the relevant authority and unresolved questions using [`architecture-compliance`](../architecture-compliance/SKILL.md), [`ARCHITECTURE-DECISIONS.md`](../../architecture/ARCHITECTURE-DECISIONS.md), and [`OPEN-DECISIONS.md`](../../architecture/OPEN-DECISIONS.md) where applicable.
3. Do not invent precedence, silently resolve an architectural conflict, or treat a proposed pattern as approved.
4. Continue only independent work that remains authorized and safe. Ask for clarification or stop the affected work when a decision is needed.
5. If a new pattern would require unrelated files, broader architecture changes, or additional permission, describe the dependency and seek authorization rather than expanding scope.

When no suitable pattern exists, a task-local solution may be appropriate if authorized and consistent with established requirements. A new pattern does not become repository-wide convention merely because it was introduced once.

## Evidence and Reporting

Keep reports concise and evidence-based. When relevant, state:

- the pattern reused or considered and its repository source;
- whether it was reused directly, adapted, rejected, or not confirmed;
- material reasons for the choice and alternatives;
- important compatibility, security, or ownership limitations;
- unresolved decisions or dependencies that block implementation; and
- files actually changed and operations or checks actually performed.

Distinguish observed facts from agent-reported claims, assumptions, inferences, and proposals. Use [`evidence-reporting`](../evidence-reporting/SKILL.md) for detailed claim boundaries. Do not imply that a pattern was comprehensively validated or that a component is operational without sufficient evidence.

## Related Skills and Architecture References

- [Engineering standards and conventions](../engineering-standards-conventions/SKILL.md)
- [Engineering quality management](../engineering-quality-management/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Architecture documentation](../architecture-documentation/SKILL.md)
- [Skill authoring](../skill-authoring/SKILL.md)
- [Engineering change management](../engineering-change-management/SKILL.md)
- [Engineering risk management](../engineering-risk-management/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Module contract](../../architecture/MODULE-CONTRACT.md)
- [Universal infrastructure](../../architecture/UNIVERSAL-INFRASTRUCTURE.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)
- [Architecture decisions register](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open architecture decisions](../../architecture/OPEN-DECISIONS.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)

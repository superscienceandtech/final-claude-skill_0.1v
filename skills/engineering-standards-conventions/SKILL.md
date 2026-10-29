---
name: "engineering-standards-conventions"
description: "Use when discovering and applying engineering standards and repository conventions without inventing unsupported rules."
---

# Engineering Standards and Conventions

## Purpose and Applicability

Engineering standards and repository conventions are the applicable instructions, decisions, documented practices, and established patterns that guide work in this repository. Use this Skill when creating or changing repository files and when deciding whether an observed pattern should be followed, adapted, or treated as unresolved.

Discover relevant conventions before introducing a new pattern. Reuse an applicable, authoritative convention where possible, but do not assume a pattern is mandatory merely because it appears in one file. This Skill complements [`engineering-quality-management`](../engineering-quality-management/SKILL.md), [`architecture-documentation`](../architecture-documentation/SKILL.md), [`skill-authoring`](../skill-authoring/SKILL.md), and [`architecture-compliance`](../architecture-compliance/SKILL.md); use those Skills for detailed quality, authoring, and architecture procedures.

A proposed convention is not an established mandatory rule. The existence of a recommendation or example does not by itself establish approval, implementation, or universal applicability. The `claude-skill_sonjoy` repository is a provider-neutral Skills and engineering-orchestration platform for SUPER AGI, not the SUPER AGI runtime.

## Discovering Applicable Standards

Before editing:

1. Read the current user request and applicable task-specific instructions. Preserve explicit deliverables, file limits, exclusions, and operation restrictions.
2. Read [`AGENTS.md`](../../AGENTS.md) and [`CLAUDE.md`](../../CLAUDE.md) for repository-wide guidance and entry instructions.
3. Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) and architecture documents or recorded decisions that materially govern the task.
4. Read applicable canonical Skills for responsibilities relevant to the deliverable.
5. Inspect nearby existing files and patterns to understand local naming, structure, formatting, terminology, and linking.
6. Confirm that an observed pattern is relevant and consistent with authoritative guidance before reusing it.

The applicable authority depends on the repository's documented source-of-truth rules and the scope and evidence of the sources involved. Do not invent a new source-precedence hierarchy or assume every repository example is authoritative.

## Classifying Requirements and Conventions

Keep the following distinctions clear:

- **Explicit requirement:** directly stated in the current task or applicable authoritative instruction.
- **Established convention:** a supported repository practice or requirement applicable to the current scope.
- **Proposed convention:** a recommendation whose authority or adoption remains explicitly proposed or unresolved.
- **Recommendation or example:** illustrative guidance that may inform a choice but does not independently create a requirement.
- **Assumption:** an unverified premise; label it when it materially affects the work.
- **Unresolved decision:** a question not settled by applicable authority or evidence.
- **Legacy pattern:** an existing implementation that may be stale, incidental, or inconsistent with current authoritative guidance.

Do not promote an example, isolated implementation, or proposed document into a universal rule without supporting authority. When convention status is unclear and materially affects the task, preserve the uncertainty and seek clarification.

## Naming and File Organization

Follow actual, relevant repository patterns for file and directory names, Skill directories and `SKILL.md` organization, architecture document names, relative Markdown links, identifiers, and terminology. For registries, schemas, and configuration, inspect the existing authorized contract and nearby examples rather than inferring a format from names alone.

Do not invent a universal naming standard, unsupported metadata field, identifier scheme, or file organization rule. Do not rename or reorganize existing files as part of an unrelated task. Use relative links consistent with nearby repository documents and verify target paths when link correctness matters and checking is permitted.

## Documentation and Skill Conventions

For Skills and documentation, keep purpose and scope clear, terminology consistent, and Markdown navigable. State only what evidence and authority support; distinguish requirements, recommendations, assumptions, and unresolved decisions. Link to relevant canonical sources rather than duplicating their complete instructions.

Describe capabilities according to their actual evidence and maturity. Documentation or a Skill may express guidance or design intent; its presence does not prove that the described behavior is implemented or enforced.

Use [`architecture-documentation`](../architecture-documentation/SKILL.md) for architecture authoring and [`skill-authoring`](../skill-authoring/SKILL.md) for canonical Skill creation. Treat [`DOCUMENTATION-STANDARDS.md`](../../architecture/DOCUMENTATION-STANDARDS.md) according to its recorded status; it describes proposed conventions and does not by itself establish mandatory policy.

## Architecture and Provider Neutrality

Respect applicable system boundaries, recorded decisions, security governance, and responsibility boundaries. Keep provider-neutral guidance independent of a particular model provider or coding agent when the canonical task requires provider neutrality. Reuse established interfaces or contracts only when their applicability and status are supported by evidence.

Use the capability-status distinctions in [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) where applicable. Do not invent interfaces, contracts, status vocabularies, provider requirements, or runtime behavior. Do not treat conceptual architecture, a declaration, or a proposed convention as implemented functionality.

If a convention conflicts with authoritative architecture, use [`architecture-compliance`](../architecture-compliance/SKILL.md): preserve the conflict and its source maturity, avoid silently resolving it, and seek clarification when the conflict materially affects the work.

## Applying Conventions During Implementation

- Inspect nearby relevant files before introducing or changing a pattern.
- Make the smallest change that satisfies the authorized task while following applicable conventions.
- Modify only files authorized by the task and preserve unrelated tracked and untracked changes.
- Avoid unnecessary formatting churn, unrelated refactoring, and duplicated abstractions.
- Reuse existing abstractions when they are applicable and do not conflict with authoritative requirements.
- Do not copy a legacy pattern when authoritative documentation contradicts it.
- Do not prescribe or assume commands, tools, or execution capabilities that are unavailable or unnecessary for the task.

If a required pattern is missing, choose no new repository-wide rule by default. Use a simple, task-local approach only when authorized and consistent with available evidence; otherwise request clarification.

## Missing, Conflicting, or Outdated Conventions

When no applicable convention exists, avoid treating local preference as repository policy. For a low-impact task, follow the simplest approach consistent with explicit requirements and nearby relevant patterns, and label the choice as an implementation decision or assumption if material. Ask when the choice affects broader compatibility, security, architecture, or future work.

When files use inconsistent patterns, documentation conflicts with implementation, a proposed convention has unresolved authority, or task instructions conflict with another applicable instruction:

1. Identify the specific sources and the disagreement.
2. Preserve each source's scope and maturity.
3. Do not silently select a winner, rewrite unrelated files, or establish new policy.
4. Stop the affected work and seek clarification when the conflict changes authorization or materially affects correctness.

Never follow a convention that would violate security requirements or task-scope restrictions. Follow [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md), [`architecture-compliance`](../architecture-compliance/SKILL.md), and [`task-scope-control`](../task-scope-control/SKILL.md) where applicable.

## Communicating Conformance and Limitations

When relevant, report which conventions materially informed the work, any significant deviation and its reason, unresolved ambiguity or source conflict, files actually modified, checks actually performed, and important limitations or actions not performed.

Do not claim comprehensive standards compliance unless the applicable scope was actually assessed with sufficient evidence. Do not require a separate conformance report for every task. Use [`evidence-reporting`](../evidence-reporting/SKILL.md) for claim-to-evidence guidance.

## Related Skills and Architecture References

- [Engineering quality management](../engineering-quality-management/SKILL.md)
- [Architecture documentation](../architecture-documentation/SKILL.md)
- [Skill authoring](../skill-authoring/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Architecture decision record](../architecture-decision-record/SKILL.md)
- [Engineering change management](../engineering-change-management/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [Architecture glossary](../../architecture/ARCHITECTURE-GLOSSARY.md)
- [Architecture decisions register](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open architecture decisions](../../architecture/OPEN-DECISIONS.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)

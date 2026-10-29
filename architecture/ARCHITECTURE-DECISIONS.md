# Architecture Decisions Register

## 1. Purpose and Scope

This register provides a consistent place to document architecture decision outcomes, their context, rationale, scope, consequences, and evidence for the `claude-skills` repository. The repository is a provider-neutral, architecture-governed engineering platform for building, governing, validating, and maintaining SUPER AGI; it is not the SUPER AGI runtime.

Decision records may address architecture boundaries, contracts, shared infrastructure, modules, providers, tools, Skills, agents, workflows, security and governance, or other cross-cutting choices that affect implementation and maintenance. Records should make the scope of each outcome clear so that a decision for one specification, integration, or revision is not generalized to the whole platform.

The register is intended to improve traceability and consistency across providers, tools, Skills, workflows, and SUPER AGI architecture documents. Recording a decision does not implement its outcome, authorize implementation, demonstrate capability, or establish operational readiness.

## 2. Authority and Source of Truth

[`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) governs architecture authority, document classification, and the evidence required for approval. This register is subordinate to that authority model. Its presence does not make its contents approved, grant decision-making authority, or override a separately approved architecture decision.

The other architecture documents provide product intent, boundaries, and proposed or approved material according to their own recorded status. A decision record must cite the exact relevant sources and approval evidence; it must not elevate a proposal, recommendation, example, or unresolved discussion into an accepted decision.

The repository does not establish a general decision owner, approval hierarchy, or complete precedence mechanism for conflicts between architecture documents. These remain unresolved. When the authority or applicable decision cannot be established, record the uncertainty and do not infer acceptance.

## 3. Decision Status Vocabulary

The following lifecycle terms are proposed for decision records in this register. They are not capability-status labels and do not replace the seven canonical capability statuses in [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).

| Decision-record status | Intended meaning |
|---|---|
| **Proposed** | A decision outcome is recommended for consideration; no acceptance is implied. |
| **Accepted** | An outcome is explicitly recorded as accepted, with evidence of the authority, scope, and effect that apply. Use only when repository evidence supports acceptance. |
| **Rejected** | The proposed outcome was explicitly rejected; record the rejection basis and scope when available. |
| **Superseded** | A later, explicitly documented decision replaces this outcome within a stated scope. Retain the earlier record and link the replacement. |
| **Deferred** | A decision was explicitly postponed or left for later consideration; identify the unresolved question or prerequisite where known. |

These are record lifecycle terms, not an approval process. A status label alone does not establish who had authority, what was approved, or whether implementation is authorized. The repository does not establish who may assign these statuses.

Capability implementation status remains separate and uses only:

- `IMPLEMENTED`
- `ADAPTER-READY`
- `MOCKED`
- `EXPERIMENTAL`
- `NOT IMPLEMENTED`
- `BLOCKED`
- `UNKNOWN`

## 4. Architecture Decision Record Format

The following reusable Markdown template and identifier format are proposed documentation conventions; neither has been formally approved as a required schema or process. `ADR-0001` is an example of a proposed stable, human-readable identifier convention, not an assigned decision ID.

```markdown
# ADR-0001 — [Decision title]

- **Decision ID:** ADR-0001
- **Title:** [Concise title]
- **Status:** [Proposed | Accepted | Rejected | Superseded | Deferred]
- **Date:** [YYYY-MM-DD or Unresolved]
- **Scope:** [Systems, components, repositories, versions, and exclusions]
- **Decision owner / approval authority:** [Name and role with evidence, or Unresolved]
- **Supersedes:** [Decision ID(s), or None / Unresolved]
- **Superseded by:** [Decision ID(s), or None / Unresolved]

## Context
[Relevant facts, constraints, architecture sources, and the circumstances
that require a decision. Distinguish evidence from assumptions and proposals.]

## Problem statement
[The specific question or problem this record addresses.]

## Decision drivers
- [Constraint, requirement, or evidence relevant to choosing an outcome]

## Considered options
1. **[Option]** — [Description, benefits, limitations, and evidence]
2. **[Option]** — [Description, benefits, limitations, and evidence]

## Decision outcome
[The bounded outcome. If Proposed, state that it is not accepted.]

## Rationale
[Why the outcome follows from the recorded drivers and evidence.]

## Consequences and trade-offs
- **Positive:** [Expected benefits]
- **Negative / risks:** [Costs, risks, and limitations]
- **Compatibility / migration:** [Affected contracts or existing behavior]

## Security, privacy, and governance implications
[Permissions, trust boundaries, data handling, human approval, and
governance consequences; mark unresolved matters explicitly.]

## Dependencies and affected architecture documents
- [Document or component]: [Relationship and impact]

## Evidence and references
- [Exact source, revision, observation, approval record, or other evidence]

## Implementation status reference
[Optional link to capability-status evidence or implementation record.
Do not treat this decision record as implementation evidence.]

## Open questions
- [Unresolved question, or None identified]
```

For an unknown owner or approving authority, use **Unresolved** rather than inferring a person or role. Dates, identifiers, approval references, and implementation-status links must not be fabricated.

## 5. Existing Decisions and Evidence Boundaries

No accepted ADR entries are recorded in this register yet. This statement concerns this register; it does not erase or broaden scoped decision evidence recorded elsewhere.

The supporting [`M1 Architecture Decision Review`](../docs/architecture/decisions/m1-architecture-decisions.md) states that ADR-M1-01 through ADR-M1-06 remain pending, except for four scoped Owner-accepted contract decisions under ADR-M1-04. Those four choices concern:

1. narrowly limited Git-internal reads for the repository-audit Skill;
2. fail-closed handling when root or individual-path containment is unproven;
3. avoiding raw paths, branch names, command arguments, and caller-controlled strings in output; and
4. specified request, path, count, claim, and output size limits.

That review records the provenance as an Owner decision supplied in the M1 governance conversation and notes that no separate repository approval artifact or time/timezone was supplied. It also states that these choices do not close ADR-M1-04, approve the exact specification revision, authorize integration or release, or establish runtime capability. They are cited here as scoped existing evidence, not adopted as generally applicable or accepted platform-architecture ADRs.

The separate [`M1 exact-revision specification approval pin`](../docs/architecture/decisions/m1-spec-approval-pin.md) records approval of one exact repository-audit specification revision by hash. Its stated scope does not approve architecture generally, authorize implementation, integration, publication, or release, or establish runtime behavior.

The existence of a record, approval pin, architecture document, or stated outcome is not evidence beyond its documented scope. No design principle, architectural aspiration, proposed relationship, or unresolved discussion is listed here as an accepted decision merely because it appears in a repository document.

## 6. Relationship to Open Decisions

`architecture/OPEN-DECISIONS.md` is the intended companion register for unresolved architecture questions; it is absent from the repository at the time this document is created. This task does not create or assume its contents.

The conceptual distinction is:

- **Architecture decision register:** records decision outcomes, their documented rationale, scope, and evidence.
- **Open-decision register:** tracks questions that remain unresolved and need clarification or a future decision.

The relationship is informational. No synchronization mechanism, automated maintenance, or required workflow between the registers is established.

## 7. Decision Quality and Change Management

The following are proposed documentation practices, not an implemented approval workflow:

- Preserve the context and rationale needed to understand an outcome later.
- Record meaningful alternatives and their trade-offs; do not imply that unexamined options were evaluated.
- Distinguish observed facts, accepted decisions, proposals, assumptions, and unknowns.
- Link relevant evidence and affected architecture documents, including exact revisions where scope depends on them.
- Explain the scope and impact of changing or superseding an outcome, including compatibility or migration consequences where known.
- Do not silently rewrite historical outcomes; retain superseded records and identify the replacement and its scope.
- Keep decision documentation distinct from capability implementation, verification, approval, and operational-status claims.
- Avoid duplicating entire architecture documents; record the decision and link its context.
- Record unresolved questions instead of resolving them by implication.

These practices do not establish mandatory reviewers, sign-off requirements, a release gate, or a mechanism for enforcing decision history.

## 8. Initial Register State and Unresolved Governance

This register begins with the template and evidence boundaries above and no accepted ADR entries. It does not declare any architecture proposal accepted.

The following governance questions remain unresolved by available repository evidence:

- Who may propose, accept, reject, or supersede architecture decisions?
- Which decision categories, if any, require formal approval?
- How are conflicts between architecture documents authoritatively resolved?
- Which decision records require review or sign-off, and by whom?
- How should decisions link to implementation, evaluation, and operational evidence?
- Does any automated decision validation or operational decision registry exist?
- What identifier and versioning rules should decision records use?

The proposed lifecycle terms, ADR template, and `ADR-0001`-style identifiers in this document do not answer these questions or grant authority. The repository's source-of-truth rules continue to apply: approval must be explicit, scoped, and supported by evidence.

## 9. Related Documents

The following architecture documents exist and are relevant to this register:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md)
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md)
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md)
- [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md)
- [`FIVE-PLANES.md`](FIVE-PLANES.md)
- [`MASTER-CORE.md`](MASTER-CORE.md)
- [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md)
- [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md)
- [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md)
- [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md)
- [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md)
- [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md)
- [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md)
- [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md)
- [`M1 Architecture Decision Review`](../docs/architecture/decisions/m1-architecture-decisions.md)
- [`M1 exact-revision specification approval pin`](../docs/architecture/decisions/m1-spec-approval-pin.md)

`architecture/OPEN-DECISIONS.md` is a planned companion and is currently absent.

# Architecture Documentation Standards

## 1. Purpose and Scope

This document proposes provider-neutral conventions for future architecture documents and technical specifications in the `claude-skills` repository. Consistent structure, terminology, authority statements, source attribution, traceability, and treatment of unresolved questions can make architecture easier to review and less likely to overstate design or implementation maturity.

The conventions are intended to apply, where relevant, to product and governance documents, architecture specifications and principles, architecture decision records, open-decision registers, glossaries, module contracts and registry specifications, capability specifications and evidence reports, implementation specifications, and operational procedures. Listing a document type does not imply that every type exists or is approved.

This document:

- proposes documentation conventions; it does not itself make them mandatory repository policy;
- does not grant decision, review, or approval authority;
- does not approve architecture decisions or operationalize a governance process;
- does not create implementation requirements unless separately authorized and approved under the repository's authority model;
- does not prove or implement any capability; and
- does not resolve questions recorded in [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md).

Distinguish:

- **Documentation convention:** a suggested way to structure or describe information.
- **Accepted architecture decision:** a scoped outcome supported by explicit approval evidence under [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md).
- **Implementation requirement:** an authorized, sufficiently specified requirement that guides an implementation. A convention or proposal is not an implementation requirement merely because it appears in a document.

The `claude-skills` repository is the architecture-governed engineering platform for building and maintaining SUPER AGI; it is not the SUPER AGI runtime. Preserve the product direction:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

The 100 modules are specialized domains within one intended unified system, not 100 independent AI systems.

## 2. Document Classification

The following classification is **proposed** for documentation organization. It does not replace the authority and document classifications in [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), imply that each type exists, or assign approval status.

| Document type | Intended purpose | Authority and maturity qualification |
|---|---|---|
| Product and governance documents | State product identity, scope, repository rules, security expectations, and governance boundaries | Authority depends on explicit source and approval evidence; policy text does not prove technical enforcement |
| Architecture specifications | Describe intended system structure, responsibilities, boundaries, interfaces, dependencies, and constraints | May be proposed, approved, or otherwise classified under the source-of-truth rules; document presence alone is not approval |
| Architecture principles | Consolidate source-grounded constraints and engineering principles | Must cite supporting sources and preserve proposed or unresolved qualifications |
| Architecture decision records | Record a scoped decision question, outcome, rationale, consequences, and evidence | Decision lifecycle terms and identifier convention in [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) are proposed; status alone does not establish authority |
| Open-decision registers | Track unresolved questions, pending choices, missing definitions, and dependencies | Lifecycle and identifier conventions in [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) are proposed; listing an issue does not resolve it |
| Glossaries | Provide consistent terminology, source references, and ambiguity notes | Do not override authoritative documents or turn named concepts into implementation claims |
| Module contracts and registry specifications | Describe proposed module identity, responsibilities, interfaces, dependencies, lifecycle, and capability metadata | Proposed schemas and declarations do not establish a runtime module, registry service, or operational behavior |
| Capability specifications and evidence reports | Define a bounded capability or report supporting evidence, limitations, and status | Use the canonical statuses from [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md); distinguish evidence from approval and deployment |
| Implementation specifications | State actionable behavior, constraints, interfaces, acceptance criteria, and verification evidence | Their approval and authorization status must be explicit; a specification does not implement its behavior |
| Operational procedures | Describe bounded steps, permissions, preconditions, failure handling, and reporting for an operation | A documented procedure does not prove that the operation was executed, safe in every environment, or technically enforced |

## 3. Recommended Document Structure

The following section guidance is **proposed** and should be adapted to document purpose. It is not a mandatory template. Small or narrowly scoped documents should omit irrelevant sections rather than add empty headings.

| Section | Recommended use |
|---|---|
| Title | **Required:** concise title that identifies the document topic |
| Purpose | **Required:** state why the document exists and what it governs or describes |
| Scope and boundaries | **Required:** identify the systems, components, audience, inclusions, and exclusions |
| Authority and maturity | **Required:** state source authority, document status, and whether content is established, proposed, unresolved, hypothetical, or evidence-backed |
| Source documents | **Recommended:** link the relevant governing, product, contract, and supporting sources |
| Terminology and definitions | **Conditional:** define terms that are specialized, ambiguous, or necessary to understand the document; otherwise link to [`ARCHITECTURE-GLOSSARY.md`](ARCHITECTURE-GLOSSARY.md) |
| Main specification | **Required:** present the actual principles, requirements, boundaries, decision, or procedure the document covers |
| Relationships and dependencies | **Conditional:** distinguish conceptual/documentation relationships from implementation dependencies |
| Security and governance implications | **Conditional:** include where data, permissions, providers, tools, safety, human approval, or consequential actions are in scope |
| Evidence and validation status | **Conditional:** include where implementation, verification, evaluation, compatibility, security, or operational claims are made |
| Unresolved questions | **Recommended:** link open questions that constrain the document; state explicitly when relevant uncertainty remains |
| Related documents | **Recommended:** link existing sources needed for interpretation without implying that they approve the current document |
| Change history | **Optional:** may be included if useful and separately supported by project convention; it is not required by this proposed standard |

An appropriate document should communicate the applicable status without suggesting that all sections are mandatory or that a document structure creates authority.

## 4. Authority and Maturity

Documents should identify what kind of statement they make and preserve its evidence boundary:

- **Established source statement:** a fact, constraint, or principle explicitly stated by a source with the relevant authority and scope.
- **Accepted decision:** an outcome supported by explicit approval evidence identifying its authority and scope.
- **Proposed architecture:** a design or recommendation that has not been elevated to accepted architecture by sufficient approval evidence.
- **Hypothetical example:** an illustrative scenario that is not an existing record, decision, implementation, or evidence artifact.
- **Unresolved question:** a matter lacking a supported outcome; link to [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) when a matching entry exists.
- **Documented implementation claim:** a statement about an artifact or behavior, which must identify what evidence supports it and its limitations.
- **Evidence-supported capability:** a bounded capability claim whose status and evidence are appropriate to the observed behavior and scope.

Document maturity, architecture decision status, and capability status are separate dimensions:

- A document can exist without being approved.
- An accepted decision does not prove that its outcome is implemented.
- An implemented artifact does not itself prove approval, evaluation, compatibility, or operational readiness.
- A capability status does not record architecture approval or decision lifecycle.

Use the seven canonical capability statuses and their existing meanings from [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md): `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, and `UNKNOWN`. Do not rename, add to, or redefine these statuses in a document.

A file's existence, directory placement, successful compilation, or declaration is not by itself evidence of approval, implementation, operational behavior, or verification.

## 5. Terminology and Naming

These are proposed documentation conventions and do not imply automated enforcement:

- Reuse existing canonical terms and definitions from [`ARCHITECTURE-GLOSSARY.md`](ARCHITECTURE-GLOSSARY.md) rather than inventing synonyms.
- Explain a specialized term on first use when its meaning is not obvious from context; qualify terms whose architecture remains proposed or unresolved.
- Expand acronyms and abbreviations at first use unless the term is widely established and unambiguous in the document's audience.
- Use a consistent heading hierarchy: one document title, major sections at the next level, and nested subsections in order without skipping levels.
- Preserve existing filenames and naming conventions. Do not rename existing sources to make them conform to a new convention without separate authorization.
- Use relative Markdown links for repository documents; link to a specific section when practical and when the target is stable.
- Verify link targets when feasible. Do not invent paths or imply a planned target exists.
- Preserve existing identifier conventions only within their documented scope. `ADR-0001`, `OPEN-0001`, `PRINCIPLE-001`, and `TRACE-0001` patterns are described in their respective documents as proposed conventions, not a unified approved identifier standard.
- Avoid creating competing identifiers for architecture decisions, open decisions, principles, or traceability records.
- Avoid using “implemented,” “operational,” “approved,” “AGI,” or “conscious” as unsupported maturity claims.
- Do not define a term more strongly than its cited source permits.

## 6. Source Attribution and Traceability

Document authors should:

1. Identify the governing authority and source documents relevant to the subject.
2. Link to existing files using correct repository-relative paths; link to specific sections where practical.
3. Preserve the source's approval status, scope, and qualifications in any summary.
4. Distinguish source-derived statements from proposals, assumptions, examples, and unresolved questions.
5. Cite exact evidence only when it has been observed and is relevant to the claim.
6. Record unavailable evidence as unavailable rather than fabricating a citation, approval, line number, implementation artifact, or capability.
7. Keep conceptual document relationships separate from implementation or runtime dependencies.

[`ARCHITECTURE-TRACEABILITY.md`](ARCHITECTURE-TRACEABILITY.md) describes a proposed documentation-level relationship model and record structure. It does not establish an operational traceability registry, automatic discovery, or change-impact process.

## 7. Scope and Boundary Discipline

Each document should make clear:

- what it covers and explicitly excludes;
- which statements are established source constraints;
- which statements describe proposed future architecture;
- which decisions remain unresolved;
- whether a relationship is conceptual, documentation-level, or an established implementation dependency; and
- what additional evidence would be needed to support a stronger claim.

Do not resolve open architecture questions by implication, repeated proposal, implementation activity, file creation, or example text. Do not treat a proposed interface as an implemented integration, a registry entry as permission, or a policy statement as enforced runtime control.

When a relevant source conflict or authority gap exists, preserve the differing claims and qualifications, cite the affected sources, and refer to an applicable open-decision entry when one actually exists. Do not invent a precedence rule.

## 8. Illustrative Examples

The examples below are **hypothetical illustrations** of the proposed documentation conventions. They are not existing records, accepted policy, or evidence of implementation.

### Example A — Purpose and scope

> **Purpose:** Describe the proposed responsibilities of a bounded component.<br>
> **Scope:** This document covers the component's conceptual inputs and outputs; it does not define a runtime API, deployment topology, or operational behavior.

### Example B — Proposed architecture statement

> **Proposed:** A future provider-neutral gateway may translate canonical model requests to provider-specific adapters. This statement describes an architectural proposal and does not establish an approved interface or working provider integration.

### Example C — Unresolved question

> **Unresolved:** The context hierarchy is proposed, but inheritance and precedence rules are not established. See [`OPEN-0008`](OPEN-DECISIONS.md) and [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md).

### Example D — Capability claim

> A design document describes the intended Model Gateway behavior; it is documentation evidence, not implementation evidence. Assign a capability status only when observed evidence supports the bounded gateway behavior being claimed, as described in [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).

### Example E — Relative link

> The authority model is described in [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md).

## 9. Adoption and Governance

This document proposes conventions only. Repository-wide mandatory adoption may require explicit approval from an authorized party; this document does not identify or appoint that party.

The following remain unresolved unless a separate authoritative source establishes them:

- who may approve this standard;
- whether the standard is mandatory or advisory;
- whether reusable templates should be created;
- whether automated documentation or terminology enforcement is desired;
- how exceptions are requested, reviewed, and recorded; and
- how future revisions are governed and approved.

No automated enforcement or repository-wide adoption is claimed.

## 10. Related Documents

The following existing sources inform this proposed standard:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md)
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md)
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md)
- [`ARCHITECTURE-PRINCIPLES.md`](ARCHITECTURE-PRINCIPLES.md)
- [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md)
- [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md)
- [`ARCHITECTURE-GLOSSARY.md`](ARCHITECTURE-GLOSSARY.md)
- [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md)
- [`ARCHITECTURE-TRACEABILITY.md`](ARCHITECTURE-TRACEABILITY.md)
- [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md)
- [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md)
- [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md)
- [`AGENTS.md`](../AGENTS.md)
- [`CLAUDE.md`](../CLAUDE.md)

# Architecture Principles

## 1. Purpose and Authority

This document consolidates source-grounded architecture principles to improve consistency across future specifications, implementation prompts, provider adapters, Skills, agents, workflows, and engineering contributions.

Principles in this document must be traceable to existing repository sources. This document consolidates existing material; it does not independently approve new architectural decisions, supersede [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md), or other governing documents, or implement or prove any capability.

Unresolved questions remain subject to the boundaries and evidence recorded in [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md). A principle may state an established repository constraint while the component mappings or runtime designs that would realize it remain proposed.

The `claude-skills` repository is the provider-neutral engineering platform for building and maintaining SUPER AGI. It is not the SUPER AGI runtime. The product direction is one unified SUPER AGI with 100 specialized intelligence modules, dedicated navigation/workspaces, and shared universal infrastructure, not 100 independent AI products.

## 2. Source and Principle Maturity

The entries below distinguish:

- **Established repository principle:** explicitly stated in repository governance or a source-of-truth document. Its implementation is not implied.
- **Established product direction:** explicit product intent, not evidence that the target system exists or operates.
- **Proposed architecture:** a design, allocation, or relationship described as proposed or unresolved. It may guide discussion but is not an approved requirement unless separate evidence establishes approval.
- **Unresolved question:** a matter explicitly left open in source documents and, where a matching entry exists, linked to [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md).

The identifiers below follow the proposed `PRINCIPLE-001` convention. This convention is for document organization only and is not an approved repository schema or authority model. No owner, approval date, or approval evidence is inferred.

## 3. Source-Grounded Principles

### A. Product and System Identity

#### PRINCIPLE-001 — Keep the engineering platform distinct from the target runtime

- **Principle statement:** Treat `claude-skills` as the provider-neutral engineering platform for building, governing, validating, and maintaining SUPER AGI; do not describe this repository as the SUPER AGI runtime.
- **Rationale:** The system boundary prevents confusion between engineering methods and the product being engineered.
- **Scope and applicability:** Product descriptions, architecture documents, implementation prompts, capability reports, and contributor guidance.
- **Sources:** [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`AGENTS.md`](../AGENTS.md).
- **Status or qualification:** Established repository boundary; it does not establish implementation of the target runtime.
- **Related unresolved questions:** None required to state this boundary.

#### PRINCIPLE-002 — Preserve the single unified SUPER AGI product direction

- **Principle statement:** Describe the intended system as one SUPER AGI with specialized intelligence domains/modules and shared infrastructure, not as 100 independent AI products.
- **Rationale:** The product constitution and source of truth explicitly state that the 100 modules are domains within one unified system.
- **Scope and applicability:** Product and module architecture, portfolios, workspaces, infrastructure, and system claims.
- **Sources:** [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md).
- **Status or qualification:** Established product direction; no authoritative list of 100 operational modules or runtime implementation is established.
- **Related unresolved questions:** [`OPEN-0009`](OPEN-DECISIONS.md) — Module Registry authority and identity.

#### PRINCIPLE-003 — Do not infer an independent system from a dedicated workspace

- **Principle statement:** Treat a dedicated module workspace or navigation surface as an interaction or organization concept, not as evidence of a separate AI product or independent runtime.
- **Rationale:** The product principle connects module workspaces to one unified system; the Module Registry distinguishes workspace metadata from module identity and behavior.
- **Scope and applicability:** Module descriptions, navigation, registry metadata, and system boundaries.
- **Sources:** [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`ARCHITECTURE-GLOSSARY.md`](ARCHITECTURE-GLOSSARY.md).
- **Status or qualification:** Product-boundary interpretation; exact workspace representation and mapping remain unresolved.
- **Related unresolved questions:** [`OPEN-0009`](OPEN-DECISIONS.md) — Module Registry authority and identity.

### B. Shared Infrastructure and Modularity

#### PRINCIPLE-004 — Make responsibilities and boundaries explicit

- **Principle statement:** State primary responsibilities, non-responsibilities, dependencies, inputs, outputs, and interfaces rather than relying on directory placement or names to imply them.
- **Rationale:** Explicit boundaries reduce duplicated responsibility, hidden coupling, unauthorized behavior, and misleading capability claims.
- **Scope and applicability:** Architecture components, modules, planes, layers, providers, tools, Skills, agents, workflows, and registries.
- **Sources:** [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md).
- **Status or qualification:** Established engineering principle; the specific layer, plane, and module assignments remain proposed or unresolved where the source documents say so.
- **Related unresolved questions:** [`OPEN-0003`](OPEN-DECISIONS.md) — L0–L15 boundaries and inter-layer contracts; [`OPEN-0004`](OPEN-DECISIONS.md) — Five-plane responsibilities and interactions.

#### PRINCIPLE-005 — Reuse shared responsibilities without assuming an implementation topology

- **Principle statement:** Preserve the documented intent for shared infrastructure to support multiple modules, while avoiding duplicate authorities and unrestricted sharing; do not assume that each responsibility is a separate service, process, or deployment unit.
- **Rationale:** The architecture describes shared infrastructure as a unified-system concept and explicitly leaves component form and topology open.
- **Scope and applicability:** Cross-module infrastructure, memory, knowledge, context, routing, security, observability, and verification.
- **Sources:** [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md).
- **Status or qualification:** Shared-support direction is documented; component boundaries, ownership, interfaces, persistence, and topology are proposed or unresolved. No operational shared runtime is established.
- **Related unresolved questions:** [`OPEN-0006`](OPEN-DECISIONS.md) — Shared infrastructure interfaces and ownership; [`OPEN-0007`](OPEN-DECISIONS.md) — Data ownership, persistence, retention, and lifecycle.

#### PRINCIPLE-006 — Keep coordination bounded and do not infer Master Core authority

- **Principle statement:** Describe Master Core coordination only within explicit task, module, permission, and human-approval boundaries; do not infer unrestricted authority or a monolithic runtime from the name.
- **Rationale:** The Master Core proposal leaves its form, decomposition, interfaces, and authority unresolved and emphasizes bounded coordination.
- **Scope and applicability:** Master Core proposals, module coordination, shared services, configuration changes, and consequential actions.
- **Sources:** [`MASTER-CORE.md`](MASTER-CORE.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md).
- **Status or qualification:** Proposed architecture; no operational Master Core or approved control interface is demonstrated.
- **Related unresolved questions:** [`OPEN-0005`](OPEN-DECISIONS.md) — Master Core decomposition and control boundaries.

### C. Provider Independence

#### PRINCIPLE-007 — Keep canonical behavior provider-neutral

- **Principle statement:** Express canonical requirements and contracts independently of a single provider, model backend, coding agent, vendor format, or proprietary API.
- **Rationale:** Provider neutrality supports reuse and avoids provider-specific definitions becoming competing sources of canonical behavior.
- **Scope and applicability:** Architecture, Skills, workflows, module contracts, model requests, and capability declarations.
- **Sources:** [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md).
- **Status or qualification:** Established repository and product principle; it does not establish provider compatibility or adapter support.
- **Related unresolved questions:** [`OPEN-0012`](OPEN-DECISIONS.md) — Model Gateway and provider routing.

#### PRINCIPLE-008 — Isolate provider-specific translation behind explicit boundaries

- **Principle statement:** Where provider-specific behavior is authorized, keep it in adapters or gateway boundaries that translate canonical contracts without silently changing canonical meaning.
- **Rationale:** Explicit translation boundaries make provider limitations, data disclosure, credentials, and compatibility reviewable.
- **Scope and applicability:** Provider adapters, model access, routing, authentication, and provider-specific Skill packaging.
- **Sources:** [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md), [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md).
- **Status or qualification:** Provider boundary is established as a principle; the Model Gateway, adapters, routing, and fallback behaviors remain proposed or unresolved unless independently evidenced.
- **Related unresolved questions:** [`OPEN-0012`](OPEN-DECISIONS.md) — Model Gateway and provider routing.
- **Related unresolved questions:** [`OPEN-0012`](OPEN-DECISIONS.md) — Model Gateway and provider routing.

### D. Context and Collaboration

#### PRINCIPLE-009 — Preserve context scope as proposed until its rules are approved

- **Principle statement:** Treat `Global → Organization → User → Project → Domain → Task → Agent` as a proposed context hierarchy; do not infer inheritance, visibility, precedence, merge, or override rules.
- **Rationale:** The Universal Context document explicitly withholds approval of the hierarchy and its access semantics.
- **Scope and applicability:** Context assembly, memory, knowledge, module handoffs, tool calls, and provider requests.
- **Sources:** [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md).
- **Status or qualification:** Hierarchy is proposed; identity, access, propagation, and isolation rules remain unresolved. No context engine is demonstrated.
- **Related unresolved questions:** [`OPEN-0008`](OPEN-DECISIONS.md) — Universal Context hierarchy and propagation.

#### PRINCIPLE-010 — Treat collaboration and context propagation as concepts until evidenced

- **Principle statement:** Describe cross-module collaboration and context propagation as proposed architecture unless interfaces, permissions, execution, and relevant failure behavior are supported by implementation evidence.
- **Rationale:** Collaboration can cross trust and data boundaries; a named pattern or handoff concept does not establish a working protocol.
- **Scope and applicability:** Cross-AGI collaboration, module routing, handoffs, result synthesis, and shared context.
- **Sources:** [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).
- **Status or qualification:** Proposed architecture; no operational cross-module collaboration runtime, permission enforcement, or context-propagation mechanism is demonstrated.
- **Related unresolved questions:** [`OPEN-0011`](OPEN-DECISIONS.md) — Cross-AGI collaboration contracts; [`OPEN-0008`](OPEN-DECISIONS.md) — Universal Context hierarchy and propagation.

### E. Security, Governance, and Human Control

#### PRINCIPLE-011 — Apply least privilege and explicit authorization

- **Principle statement:** Scope access to the authorized task and required capability; do not treat module registration, a declaration, agent role, or tool allowlist as permission by itself.
- **Rationale:** Repository governance and security architecture require least privilege and explicit authority at provider, tool, module, data, and operation boundaries.
- **Scope and applicability:** Repository changes, external tools, providers, context, module interactions, and consequential operations.
- **Sources:** [`AGENTS.md`](../AGENTS.md), [`SECURITY.md`](../SECURITY.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md).
- **Status or qualification:** Established policy principle; runtime authorization and technical enforcement are not thereby demonstrated.
- **Related unresolved questions:** [`OPEN-0013`](OPEN-DECISIONS.md) — Identity, authorization, enforcement, and incident governance.

#### PRINCIPLE-012 — Preserve human approval boundaries

- **Principle statement:** Require explicit human authorization for destructive, irreversible, sensitive, externally visible, production, account-changing, or otherwise consequential operations where repository policy applies; do not treat model output as approval.
- **Rationale:** Human authority is distinct from recommendations, authentication, implementation, and evaluation.
- **Scope and applicability:** Repository operations, deployment, publication, provider/tool use, and other actions identified by applicable policy.
- **Sources:** [`AGENTS.md`](../AGENTS.md), [`SECURITY.md`](../SECURITY.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md).
- **Status or qualification:** Approval expectation is established; no general approval hierarchy, named approver, or automated approval gate is established.
- **Related unresolved questions:** [`OPEN-0001`](OPEN-DECISIONS.md) — Decision authority and sign-off requirements; [`OPEN-0013`](OPEN-DECISIONS.md) — Identity, authorization, enforcement, and incident governance.

#### PRINCIPLE-013 — Distinguish documented policy from enforced control

- **Principle statement:** Do not claim security enforcement, audit completeness, compliance, or incident-response capability from policy documentation alone.
- **Rationale:** Security and governance sources distinguish stated requirements from implemented and verified runtime controls.
- **Scope and applicability:** Security architecture, integrations, authorization, audit, privacy, and capability reporting.
- **Sources:** [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md), [`SECURITY.md`](../SECURITY.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).
- **Status or qualification:** Established evidence principle; specific enforcement and incident mechanisms remain unresolved unless separately evidenced.
- **Related unresolved questions:** [`OPEN-0013`](OPEN-DECISIONS.md) — Identity, authorization, enforcement, and incident governance.

### F. Evidence and Implementation Claims

#### PRINCIPLE-014 — Preserve the canonical capability-status vocabulary

- **Principle statement:** Use exactly `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, and `UNKNOWN` with the meanings defined in [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).
- **Rationale:** A shared status vocabulary supports consistent reporting without conflating implementation, adapter readiness, experiments, blockers, and insufficient evidence.
- **Scope and applicability:** Capabilities, integrations, components, workflows, modules, and system claims.
- **Sources:** [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md), [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md).
- **Status or qualification:** Vocabulary and meanings are established; evidence schemas, freshness, verification authority, and dependency-aware aggregation remain unresolved.
- **Related unresolved questions:** [`OPEN-0014`](OPEN-DECISIONS.md) — Capability evidence, freshness, and readiness.

#### PRINCIPLE-015 — Separate intent, artifacts, execution, verification, approval, and readiness

- **Principle statement:** Distinguish documentation and proposed design from implementation artifacts, executable integrations, observed behavior, verification, evaluation, approval, and operational readiness.
- **Rationale:** Each supports a different kind of claim; evidence for one must not be generalized to another without basis.
- **Scope and applicability:** Architecture records, code and configuration, provider/tool integrations, workflow reports, security claims, and system capability statements.
- **Sources:** [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).
- **Status or qualification:** Established evidence principle; evidence requirements and authority for broader readiness claims remain unresolved.
- **Related unresolved questions:** [`OPEN-0014`](OPEN-DECISIONS.md) — Capability evidence, freshness, and readiness; [`OPEN-0015`](OPEN-DECISIONS.md) — Decision-to-implementation traceability.

#### PRINCIPLE-016 — Do not infer capability from repository presence

- **Principle statement:** File names, directories, comments, examples, generated documentation, declarations, successful compilation, or agent assertions are not sufficient alone to establish that a capability works.
- **Rationale:** Presence may evidence an artifact or intent, not usable behavior or operational readiness.
- **Scope and applicability:** Repository inspection, registries, Skills, agent roles, tools, providers, modules, and system claims.
- **Sources:** [`AGENTS.md`](../AGENTS.md), [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).
- **Status or qualification:** Established repository governance principle.
- **Related unresolved questions:** [`OPEN-0014`](OPEN-DECISIONS.md) — Capability evidence, freshness, and readiness.

#### PRINCIPLE-017 — Keep work bounded and uncertainty explicit

- **Principle statement:** Preserve authorized task scope and stopping conditions; report uncertainty, blockers, limitations, and unexecuted checks rather than guessing or overstating results.
- **Rationale:** Bounded work and honest evidence protect user work and prevent assumptions from becoming implicit architecture or capability claims.
- **Scope and applicability:** Architecture changes, implementation prompts, coding-agent work, validation, and completion reports.
- **Sources:** [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md), [`../workflows/spec-to-implementation/README.md`](../workflows/spec-to-implementation/README.md).
- **Status or qualification:** Established repository governance principle; no automated scope or status enforcement is implied.
- **Related unresolved questions:** [`OPEN-0016`](OPEN-DECISIONS.md) — Criteria for accepting proposed architecture.

## 4. Established Principles Versus Proposed Architecture

An established principle is not the same as an approved detailed design or an implemented control. The sources support the repository/runtime boundary, unified-product direction, provider neutrality, explicit responsibility boundaries, least privilege, human authorization for consequential operations, bounded work, and evidence-based capability claims as principles or product constraints.

Other material remains qualified:

- The **five plane names** are established baseline terminology, but detailed plane interfaces, ownership, and mapping remain proposed or unresolved.
- **L0** and **L15** have established endpoint descriptions; the full layer map, intermediate definitions, dependency matrix, and plane-to-layer mapping remain proposed or unresolved.
- The **Master Core**, **Universal Infrastructure**, **Universal Context**, **Model Gateway**, and **Cross-AGI Collaboration** documents describe proposed architecture concepts; their presence does not establish approved interfaces or operational components.
- The context hierarchy remains proposed; no inheritance, visibility, precedence, or override rules are established.
- Capability labels describe evidence-supported status. They do not establish decision approval, release, compatibility, security enforcement, or system readiness.

Runtime capabilities require independent implementation and behavior evidence appropriate to their stated scope. These principles do not assert that SUPER AGI, its 100 modules, or any named shared runtime capability is implemented.

## 5. Conflicts and Ambiguities

This document does not establish a new precedence rule for resolving source conflicts. [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) governs authority classification; statements must be interpreted within their recorded approval scope.

The architecture sources deliberately leave detailed layer boundaries, plane interactions, component ownership, Master Core decomposition, provider routing, context semantics, module contracts, security enforcement, and evidence authority unresolved. Those qualifications are preserved above rather than reconciled by inference. Where a matching open-decision entry exists, it is linked from the relevant principle.

No separate source conflict is resolved or architecture decision created by this document.

## 6. Applying the Principles

When preparing architecture specifications or implementation prompts:

1. Identify applicable principles and cite the source documents that support them.
2. Link consequential architecture claims to relevant sources and approval evidence.
3. Separate established constraints from proposed designs and assumptions.
4. Record unresolved questions in the appropriate register rather than guessing.
5. Preserve task scope, repository governance, security boundaries, and stop conditions.
6. Distinguish design, implementation, execution, verification, evaluation, approval, and operational readiness in reporting.
7. Avoid unsupported claims that a capability is implemented or operational, or that AGI or consciousness has been achieved.

These are documentation and engineering guidance. No automated policy or terminology enforcement is claimed.

## 7. Related Documents

The following existing sources support this principles reference:

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
- [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md)
- [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md)
- [`ARCHITECTURE-GLOSSARY.md`](ARCHITECTURE-GLOSSARY.md)
- [`AGENTS.md`](../AGENTS.md)
- [`CLAUDE.md`](../CLAUDE.md)
- [`SECURITY.md`](../SECURITY.md)
- [`spec-to-implementation workflow`](../workflows/spec-to-implementation/README.md)

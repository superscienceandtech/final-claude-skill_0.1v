# Open Architecture Decisions Register

## 1. Purpose and Scope

This register records unresolved architecture questions, pending choices, missing governance definitions, and dependencies that need clarification for the `claude-skills` repository. The repository is a provider-neutral, architecture-governed engineering platform for building and maintaining SUPER AGI; it is not the SUPER AGI runtime.

The register is intended to help maintain traceability as architecture work proceeds across layers, planes, modules, shared infrastructure, providers, tools, Skills, agents, workflows, security, and capability evidence.

- Recording a question does not resolve it.
- Listing a possible solution does not approve it.
- Documenting an unresolved feature does not prove that the feature is implemented.
- This register does not grant decision-making, approval, implementation, or release authority.

The product boundary remains one unified SUPER AGI with 100 specialized intelligence modules and shared universal infrastructure, not 100 independent AI products. This register does not claim that the target runtime or its modules are implemented or operational.

## 2. Relationship to the Architecture Decision Register

[`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) is the companion register for documented decision outcomes and their rationale. This document tracks unresolved questions, pending choices, and missing architectural definitions.

The intended distinction is:

- **Architecture decision register:** records decision outcomes, their rationale, scope, and evidence.
- **Open-decision register:** tracks questions that remain unresolved and may require clarification or a future decision.

The relationship is conceptual. No automatic synchronization, approval workflow, status-transition process, or decision-management tooling between the registers is established.

## 3. Open-Decision Record Format

The following reusable Markdown template and `OPEN-0001`-style identifiers are proposed documentation conventions. The identifier convention and template have not been formally approved as a required schema or process. An example identifier in the template is not an assigned decision ID.

```markdown
# OPEN-0001 — [Question title]

- **Decision ID:** OPEN-0001
- **Title:** [Concise question]
- **Status:** [Open | Under Consideration | Blocked | Resolved | Withdrawn]
- **Date identified:** [YYYY-MM-DD, if evidenced; otherwise Not recorded]
- **Architectural scope:** [Affected system, component, versions, and exclusions]

## Problem or unresolved question
[State the question without implying an answer.]

## Why it matters
[Explain affected responsibilities, implementation, compatibility, security,
or governance.]

## Known facts and authoritative references
- [Fact supported by an authoritative source; distinguish proposal from approval]

## Existing constraints
- [Established boundary or requirement]

## Possible options
[Include only options supported by repository evidence; otherwise state that
no options are established.]

## Trade-offs and consequences requiring evaluation
- [Known or anticipated consequence; label assumptions]

## Dependencies and affected documents
- [Document or component and its relationship]

## Security, privacy, safety, and governance implications
[State applicable concerns and unresolved implications.]

## Required evidence or information
- [Information, decision, or evidence needed to resolve the question]

## Decision owner or approval authority
[Name and authority with evidence, or Unresolved.]

## Resolution criteria
[Evidence and scope required to record a resolution; do not imply approval.]

## Related decision IDs
[IDs that exist in the repository, or None identified.]

## Resolution outcome and reference
[Complete only after an evidenced decision; otherwise Not resolved.]
```

For owners, authorities, dates, options, or related decision IDs that are not established, state **Unresolved**, **Not recorded**, or **None identified** as appropriate. Do not invent values to complete the template.

## 4. Status Vocabulary

The following minimal lifecycle terms are proposed for entries in this unresolved-decision register:

| Status | Intended meaning |
|---|---|
| **Open** | The question is recorded and no resolution is evidenced. |
| **Under Consideration** | Evidence shows that the question is actively being evaluated; the outcome remains unresolved. |
| **Blocked** | Progress toward resolution depends on a missing prerequisite, authority, or evidence that is identified in the entry. |
| **Resolved** | A decision outcome is documented with supporting authority and evidence; link the corresponding decision record where one exists. |
| **Withdrawn** | The question is explicitly no longer being pursued; record the reason and supporting reference when available. |

These are proposed open-decision record statuses, not automated transitions or approval states. They do not replace the decision-record lifecycle in [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md), nor the seven capability statuses in [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md):

- `IMPLEMENTED`
- `ADAPTER-READY`
- `MOCKED`
- `EXPERIMENTAL`
- `NOT IMPLEMENTED`
- `BLOCKED`
- `UNKNOWN`

No status assignment or transition mechanism is established.

## 5. Initial Open Questions

The entries below are derived from unresolved matters explicitly identified in available architecture documents. Each entry is **Open** because no resolution is evidenced here. The IDs follow the proposed convention above and are local register references, not approved identifiers. Dates and owners are not supplied where the sources do not establish them. No priority or deadline is implied.

### OPEN-0001 — Decision authority and sign-off requirements

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Architecture decisions and governance across the platform
- **Unresolved question:** Who may propose, accept, reject, defer, or supersede architecture decisions, and which decision categories require formal review or sign-off?
- **Why it matters:** A decision record must not be treated as approved without evidence of the authority, scope, and effect that apply.
- **Known facts and references:** [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) requires explicit approval evidence identifying the approved document or revision, authority, date or durable record, scope, and separate implementation or release authorization. [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) states that general decision ownership and approval hierarchy are not established.
- **Existing constraints:** Do not infer approvers from team roles, file ownership, or document authorship.
- **Possible options:** No authoritative options are established.
- **Dependencies and affected documents:** Source-of-truth governance; decision register; any future open-decision process.
- **Security, privacy, safety, and governance implications:** Approval authority must be explicit, bounded, and distinguishable from implementation or deployment authority.
- **Required evidence or information:** An authoritative governance decision identifying decision roles, scope, and any sign-off requirements.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** Record an explicitly authorized outcome and its scope in a decision record with supporting evidence.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0002 — Architecture precedence and conflict resolution

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Canonical architecture documents and conflicting requirements
- **Unresolved question:** How should conflicts between architecture documents be identified and authoritatively resolved when the applicable approval scope or precedence is unclear?
- **Why it matters:** Contributors must avoid silently choosing between contradictory requirements or elevating a proposal over an approved decision.
- **Known facts and references:** [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) defines approval evidence and document classifications. [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) describes conflict handling and escalation but does not establish a general approving authority.
- **Existing constraints:** Approved decisions govern only their recorded scope; proposal-level material is not approval evidence.
- **Possible options:** No complete conflict-resolution hierarchy is established.
- **Dependencies and affected documents:** Source-of-truth document; all affected architecture and decision records.
- **Security, privacy, safety, and governance implications:** Conflicts affecting permissions, safety, or sensitive actions require stopping dependent work when authority cannot be established.
- **Required evidence or information:** An approved precedence and escalation rule, including how scope and approval evidence are assessed.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** A documented authoritative process and a traceable outcome for the conflict classes it covers.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0003 — L0–L15 boundaries and inter-layer contracts

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** L0 through L15 architecture layers
- **Unresolved question:** What are the approved responsibilities, interfaces, dependency directions, and boundaries for intermediate layers and for dependencies between all layers?
- **Why it matters:** The current map is insufficient to infer implementation placement or safe dependencies for layers whose definitions and contracts remain proposed.
- **Known facts and references:** [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md) identifies L0 as the physical/compute boundary and L15 as the Master Control boundary; intermediate names and responsibilities are not approved, and an exact dependency matrix remains unresolved.
- **Existing constraints:** Do not treat proposed intermediate layer names or dependency patterns as canonical or enforced.
- **Possible options:** The layer map presents candidate responsibilities, but no complete option set or accepted mapping is established.
- **Dependencies and affected documents:** [`FIVE-PLANES.md`](FIVE-PLANES.md), [`MASTER-CORE.md`](MASTER-CORE.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md).
- **Security, privacy, safety, and governance implications:** Layer boundaries may affect control placement, trust boundaries, and authorization; no security guarantee follows from the layer model alone.
- **Required evidence or information:** Explicitly approved layer definitions, interfaces, dependency rules, exceptions, and evidence boundaries.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** A scoped decision that identifies approved layers and contracts without relying on unapproved mappings.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0004 — Five-plane responsibilities and interactions

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Intelligence, Knowledge, Agent, Domain, and Control planes
- **Unresolved question:** What are the definitive responsibilities, cross-plane interfaces, dependencies, and interaction protocols for the five planes, and how do those responsibilities relate to L0–L15?
- **Why it matters:** The plane names are established, but assigning implementation or authority based on an assumed one-to-one mapping could create conflicting ownership or hidden coupling.
- **Known facts and references:** [`FIVE-PLANES.md`](FIVE-PLANES.md) establishes the five names as architectural groupings and marks detailed responsibilities, interactions, and plane-to-layer mappings proposed or unresolved. [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md) likewise does not establish a definitive mapping.
- **Existing constraints:** Do not add a sixth plane, merge the five planes, or assume planes map one-to-one to layers, directories, or deployment units.
- **Possible options:** No definitive interaction or mapping alternatives are recorded.
- **Dependencies and affected documents:** [`FIVE-PLANES.md`](FIVE-PLANES.md), [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), and component architecture documents.
- **Security, privacy, safety, and governance implications:** Control responsibilities and boundaries must not be bypassed by plane interactions; separation alone does not ensure security.
- **Required evidence or information:** Approved responsibility boundaries, interfaces, dependency constraints, and relationship to layers.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** Explicitly approved definitions and interaction boundaries for the intended scope.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0005 — Master Core decomposition and control boundaries

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Proposed Master Core and its relationship to L15, shared infrastructure, and the five planes
- **Unresolved question:** Is the Master Core a runtime service, coordination library, governance process, contract boundary, or future combination, and what interfaces, internal responsibilities, and control boundaries apply?
- **Why it matters:** Implementation form and authority cannot safely be inferred from the “Master Core” name or from conceptual responsibilities.
- **Known facts and references:** [`MASTER-CORE.md`](MASTER-CORE.md) lists these alternatives and leaves component names, ownership, interfaces, schemas, lifecycle authority, and placement relative to L15 unresolved.
- **Existing constraints:** No operational Master Core or approved interface is established.
- **Possible options:** The cited document lists service, library, process, contract boundary, or a future combination as possibilities; none is selected.
- **Dependencies and affected documents:** [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`FIVE-PLANES.md`](FIVE-PLANES.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md).
- **Security, privacy, safety, and governance implications:** Coordinator authority, permission checks, human approval, configuration changes, and audit boundaries require explicit definition.
- **Required evidence or information:** Approved responsibilities, component decomposition, interfaces, ownership, lifecycle, and authority limits.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** A scoped decision resolving the form and boundaries required by dependent implementation.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0006 — Shared infrastructure interfaces and ownership

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Universal Infrastructure and shared cross-module capabilities
- **Unresolved question:** Which shared infrastructure responsibilities are capabilities, libraries, services, processes, or combinations, and who owns their interfaces, lifecycle, and dependencies?
- **Why it matters:** Shared infrastructure should support the unified system without creating duplicate authorities or unbounded coupling between modules.
- **Known facts and references:** [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) describes proposed responsibility areas and explicitly leaves component form, boundaries, ownership, interfaces, topology, and dependencies unresolved.
- **Existing constraints:** The document is a proposal and does not establish an operational infrastructure runtime.
- **Possible options:** Component form is expressly left open among capabilities, libraries, services, processes, or combinations; no selection is established.
- **Dependencies and affected documents:** [`MASTER-CORE.md`](MASTER-CORE.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md).
- **Security, privacy, safety, and governance implications:** Trust boundaries, least privilege, failure containment, and audit responsibility depend on component boundaries and ownership.
- **Required evidence or information:** Approved component inventory, responsibility ownership, interfaces, lifecycle, and trust/deployment boundaries.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** Approved boundaries and contracts sufficient for the affected implementation scope.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0007 — Data ownership, persistence, retention, and lifecycle

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Shared infrastructure, memory, knowledge, context, World Model, and module data
- **Unresolved question:** Who owns each data class, where and how may it persist, and what access, provenance, retention, deletion, update, and lifecycle rules apply?
- **Why it matters:** Data handling affects privacy, security, cross-module boundaries, provider disclosure, auditability, and safe operation.
- **Known facts and references:** [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) lists persistence, storage, ownership, retention, deletion, and lineage as unresolved. [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md) and [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) do not establish operational retention or deletion guarantees.
- **Existing constraints:** Context, memory, knowledge, and World Model are distinct concepts; documentation does not establish persistence or access enforcement.
- **Possible options:** No approved storage, ownership, or retention options are established.
- **Dependencies and affected documents:** [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md).
- **Security, privacy, safety, and governance implications:** Data minimization, scope isolation, disclosure, deletion, and audit access require explicit policy and evidence.
- **Required evidence or information:** Data categories, owners, authorized purposes, lifecycle rules, storage boundaries, and applicable approval.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** Approved data lifecycle and access rules for each relevant capability and scope.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0008 — Universal Context hierarchy and propagation

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Context identity, assembly, propagation, isolation, and use across tasks, modules, agents, tools, and providers
- **Unresolved question:** Is the proposed `Global → Organization → User → Project → Domain → Task → Agent` hierarchy adopted, and what identity, inheritance, visibility, precedence, merge, override, isolation, and propagation rules govern it?
- **Why it matters:** Incorrect assumptions about scope inheritance or propagation could disclose information or allow one context to override another without authority.
- **Known facts and references:** [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) labels the hierarchy proposed and leaves identity, authorization, inheritance, visibility, precedence, assembly, conflict, serialization, and propagation rules unresolved.
- **Existing constraints:** No child scope may be assumed to inherit all parent information; no broader scope may be assumed to override a narrower one.
- **Possible options:** The hierarchy is a documented proposal; no approved alternative or adoption decision is established.
- **Dependencies and affected documents:** [`MASTER-CORE.md`](MASTER-CORE.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md), [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md).
- **Security, privacy, safety, and governance implications:** Authorization, minimization, data disclosure, cross-scope isolation, and human control must be resolved before relying on context propagation.
- **Required evidence or information:** Approved scope and identity model, access rules, precedence behavior, propagation contract, and verification evidence.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** An approved context contract that resolves the relevant scopes and failure behavior.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0009 — Module Registry authority and identity

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Module catalog, identity, portfolio, extensibility, ownership, and discovery
- **Unresolved question:** What is the authoritative source of the module portfolio, and what identifier, schema, ownership, extensibility, and update rules govern registry entries?
- **Why it matters:** Module identity and registry metadata affect contracts, dependencies, evidence references, compatibility, and preventing duplicate or misleading capability claims.
- **Known facts and references:** [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) leaves the identifier convention, authoritative list of 100 modules, schema, ownership, versioning, storage, access, and lifecycle authority unresolved.
- **Existing constraints:** No authoritative list of 100 operational modules or operational registry service is established; registry membership is not permission.
- **Possible options:** No authoritative portfolio or identifier alternatives are established.
- **Dependencies and affected documents:** [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`MASTER-CORE.md`](MASTER-CORE.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md).
- **Security, privacy, safety, and governance implications:** Registry access, identity authenticity, permission boundaries, and update approval require explicit definition.
- **Required evidence or information:** Authoritative portfolio source, identity convention, schema, ownership, lifecycle, and discovery boundaries.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** An approved registry contract with scoped identity and lifecycle authority; it must not imply module implementation.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0010 — Module contract schema and conformance governance

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Module declarations, interfaces, dependencies, conformance, versioning, and lifecycle
- **Unresolved question:** What schema and interface conventions define a module contract, how is conformance assessed, and who governs versioning, compatibility, lifecycle, and approval?
- **Why it matters:** Modules need reviewable, compatible responsibility and interaction boundaries without treating a declaration as runtime behavior.
- **Known facts and references:** [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md) leaves schema, identity, API or message interfaces, serialization, versioning, conformance criteria, Registry integration, and approval authority unresolved.
- **Existing constraints:** Contract status is distinct from capability status; no contract validator or runtime interface is established.
- **Possible options:** No final schema or conformance options are approved.
- **Dependencies and affected documents:** [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`MASTER-CORE.md`](MASTER-CORE.md), [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).
- **Security, privacy, safety, and governance implications:** Permission, input/output validation, context handling, and evidence rules are part of the contract boundary but lack enforcement decisions.
- **Required evidence or information:** Approved schema/interface, versioning and compatibility rules, conformance criteria, and governance authority.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** An explicitly approved contract and validation scope that separates declaration, implementation, and runtime evidence.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0011 — Cross-AGI collaboration contracts

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Module discovery, routing, task decomposition, handoffs, execution, synthesis, and failure handling
- **Unresolved question:** What protocols and authority boundaries govern module matching, collaboration, handoffs, sequential or parallel execution, result synthesis, failure, retry, cancellation, fallback, and escalation?
- **Why it matters:** Collaboration can create cross-module data disclosure, authority expansion, inconsistent results, and ambiguous responsibility if protocols are implicit.
- **Known facts and references:** [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md) describes proposed patterns but leaves interfaces, routing, coordinator authority, context authorization, conflict resolution, failure semantics, and approval authority unresolved.
- **Existing constraints:** Module outputs remain untrusted until verified; registry membership does not authorize invocation; no operational cross-module collaboration runtime is demonstrated.
- **Possible options:** The document describes patterns but establishes no definitive protocol or arbitration option.
- **Dependencies and affected documents:** [`MASTER-CORE.md`](MASTER-CORE.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md).
- **Security, privacy, safety, and governance implications:** Least privilege, authorized handoffs, data minimization, untrusted output handling, human approval, and traceability need explicit contracts.
- **Required evidence or information:** Approved interfaces and authority model, failure semantics, permission rules, and verification criteria.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** A scoped, approved collaboration contract addressing relevant handoffs, trust, and failure paths.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0012 — Model Gateway and provider routing

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Provider-neutral requests, provider/model capability metadata, adapters, routing, and fallback
- **Unresolved question:** What request/response and error interfaces, provider capability normalization, routing eligibility, selection policy, fallback rules, and adapter lifecycle govern model access?
- **Why it matters:** Provider-neutral behavior depends on explicit contracts and compatible, authorized routing; silent fallback may change data handling or behavior.
- **Known facts and references:** [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md) leaves request/response contracts, identity, capability evidence, routing policy, adapter lifecycle, provider eligibility, fallback, credentials, evaluation, and governance unresolved.
- **Existing constraints:** A provider-neutral interface does not prove an adapter works. Sensitive data must not be sent to a different provider automatically merely because another provider failed.
- **Possible options:** No routing or fallback option is approved.
- **Dependencies and affected documents:** [`MASTER-CORE.md`](MASTER-CORE.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).
- **Security, privacy, safety, and governance implications:** Credential isolation, data disclosure, authorization, provider retention, output trust, and fallback scope require explicit decisions and evidence.
- **Required evidence or information:** Approved contracts, capability representation, routing and fallback rules, provider eligibility, security constraints, and evaluation scope.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** An approved provider-neutral contract and scoped routing policy with separate evidence requirements for each adapter.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0013 — Identity, authorization, enforcement, and incident governance

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Users, organizations, projects, modules, agents, workflows, tools, providers, data, runtime actions, and security response
- **Unresolved question:** What identity and authentication model, authorization and policy enforcement mechanisms, audit controls, incident response ownership, and human-approval boundaries apply?
- **Why it matters:** Authentication, authorization, policy evaluation, and approval are distinct; missing rules can result in unauthorized access, disclosure, or consequential actions.
- **Known facts and references:** [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md) separates these concepts and identifies identity, permission representation, enforcement, audit, incident response, and authority as unresolved. [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) and [`SECURITY.md`](../SECURITY.md) state security expectations but do not establish runtime enforcement.
- **Existing constraints:** Policy documentation is not proof of enforcement; consequential operations require explicit human authorization under applicable repository policy.
- **Possible options:** No identity provider, role hierarchy, or enforcement engine is selected.
- **Dependencies and affected documents:** [`MASTER-CORE.md`](MASTER-CORE.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md).
- **Security, privacy, safety, and governance implications:** This question is directly security-sensitive and must not be resolved by implied authority or policy text alone.
- **Required evidence or information:** Explicit identity and permission contracts, authority boundaries, enforcement design, audit and incident responsibilities, and verification criteria.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** A scoped, explicitly authorized security and governance decision; implementation and operational effectiveness remain separate evidence requirements.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0014 — Capability evidence, freshness, and readiness

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Capability claims, dependencies, verification, evaluation, and status publication
- **Unresolved question:** What evidence is sufficient for each class of capability claim, who verifies it, how freshness is assessed, and how component evidence relates to dependency-aware and end-to-end readiness?
- **Why it matters:** Status claims must not overstate what was observed or imply that a component, interface, or one test proves a complete workflow or system.
- **Known facts and references:** [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) preserves the seven canonical labels and lists evidence schema, identity conventions, freshness, verification authority, dependency-aware readiness, status authority, and reporting as unresolved. [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) distinguishes implementation, execution, validation, evaluation, approval, and operational readiness.
- **Existing constraints:** Do not infer functioning behavior from documentation, interface presence, registry entries, successful compilation, or unexecuted checks.
- **Possible options:** No universal evidence schema, expiry interval, readiness score, or dependency algorithm is established.
- **Dependencies and affected documents:** [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md).
- **Security, privacy, safety, and governance implications:** Evidence must avoid unnecessary sensitive data and distinguish policy documentation from enforced controls.
- **Required evidence or information:** Claim-specific evidence criteria, verification authority, freshness and invalidation policy, dependency scope, and reporting authority.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** An approved evidence policy that preserves status meanings and distinguishes component, integration, and system claims.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0015 — Decision-to-implementation traceability

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Architecture decisions, implementation work, capability evidence, evaluation, and release claims
- **Unresolved question:** How should an accepted decision be linked to implementation artifacts, verification and evaluation evidence, capability status, and any separate approval or deployment authorization?
- **Why it matters:** A decision outcome is not implementation evidence, and implementation evidence does not itself approve architecture or release.
- **Known facts and references:** [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) provides a proposed implementation-status reference field but leaves decision governance and links unresolved. [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) distinguishes status from approval and deployment. [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) requires approval records to identify scope and whether implementation, evaluation, integration, or release remains separate.
- **Existing constraints:** Do not mark an issue resolved because implementation started or a file was created; do not infer approval from successful implementation.
- **Possible options:** No linking format, storage mechanism, or automated traceability system is established.
- **Dependencies and affected documents:** Decision register, capability-status document, affected architecture specifications, implementation and verification records.
- **Security, privacy, safety, and governance implications:** Traceability should preserve authority and provenance without exposing secrets or unnecessary sensitive data.
- **Required evidence or information:** Approved traceability conventions, decision-to-evidence references, and separation of implementation, verification, approval, and release.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** A documented, scope-appropriate method supported by actual evidence; no automation is implied.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

### OPEN-0016 — Criteria for accepting proposed architecture

- **Status:** Open
- **Date identified:** Not recorded
- **Architectural scope:** Promotion of architecture proposals and unresolved designs into accepted decisions
- **Unresolved question:** What criteria, evidence, reviews, and authority are required before a proposed architecture detail may be recorded as accepted?
- **Why it matters:** Repeated proposals or implementation activity must not be mistaken for approval, and dependent work may otherwise rely on unapproved assumptions.
- **Known facts and references:** [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) requires explicit approval evidence and separates approval from implementation, evaluation, integration, and release. [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) states that the general approval hierarchy and decision lifecycle authority remain unresolved.
- **Existing constraints:** Proposal-level architecture remains proposed until separate approval evidence exists; the narrow M1 specification pin applies only to its exact specification revision.
- **Possible options:** No general acceptance criteria or approval workflow are established.
- **Dependencies and affected documents:** [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md), all architecture proposals relying on acceptance.
- **Security, privacy, safety, and governance implications:** Decisions affecting security, data, permissions, or consequential operations may require evidence and review, but no category-specific authority is established.
- **Required evidence or information:** Explicit acceptance criteria, applicable review requirements, decision authority, scope, and durable approval record.
- **Decision owner or approval authority:** Unresolved.
- **Resolution criteria:** An evidenced governance decision defining how proposals are accepted without conflating approval, implementation, and release.
- **Related decision IDs:** None identified.
- **Resolution outcome and reference:** Not resolved.

## 6. Evidence and Resolution Rules

The following are proposed documentation practices, not an operational approval or automation system:

- Cite authoritative source material and identify the scope of any approval evidence.
- Separate observed facts from assumptions, proposed solutions, and unknowns.
- Record meaningful alternatives and trade-offs only when the sources support them.
- Identify affected architecture documents and dependencies.
- Record an actual outcome and its supporting reference only after a decision is evidenced.
- Link a resolved question to the corresponding architecture decision record when one exists.
- Preserve traceability if a resolution is later superseded; do not erase or silently rewrite the earlier outcome.
- Do not mark an entry resolved merely because implementation began, a file was created, or a test ran.
- Keep decision resolution separate from capability implementation, verification, approval, and deployment.

## 7. Initial Register State and Limitations

The initial entries are derived from unresolved matters explicitly documented in the available architecture sources. Their inclusion does not select a solution, establish priority, assign an owner, or imply approval. No approval authority should be inferred where none is established.

The repository does not establish an automated status-transition mechanism, resolution workflow, prioritization system, or operational open-decision registry. This document does not implement any such mechanism, and it is not asserted that one exists elsewhere.

This register is a point-in-time documentation aid, not a complete or permanently exhaustive inventory of architectural uncertainty. New evidence may clarify, add, split, or supersede questions. Any such change requires evidence and must remain within the repository's authority and scope rules.

The narrow M1 approval evidence is not a general architecture approval: the four scoped Owner-accepted contract choices documented in the M1 review and the exact-revision repository-audit specification approval pin do not resolve the architecture questions listed here.

## 8. Related Documents

The following referenced documents exist in the repository:

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
- [`M1 Architecture Decision Review`](../docs/architecture/decisions/m1-architecture-decisions.md)
- [`M1 exact-revision specification approval pin`](../docs/architecture/decisions/m1-spec-approval-pin.md)

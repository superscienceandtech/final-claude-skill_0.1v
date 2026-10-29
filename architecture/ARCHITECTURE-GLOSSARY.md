# Canonical Architecture Glossary

## 1. Purpose and Scope

This glossary provides shared terminology for architecture documents, implementation prompts, engineering workflows, provider adapters, and future contributors to the `claude-skills` repository and its SUPER AGI engineering architecture.

The glossary:

- defines terminology for consistency;
- does not independently approve architecture decisions;
- does not implement the concepts it describes;
- does not override the authority model in [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md); and
- does not resolve questions recorded in [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md).

The repository is the provider-neutral engineering platform for building and maintaining SUPER AGI; it is not the SUPER AGI runtime. The product direction remains one unified SUPER AGI with 100 specialized intelligence modules, dedicated navigation/workspaces, and shared universal infrastructure, not 100 independent AI products.

## 2. Source and Authority Rules

Terms in this glossary are derived from existing repository documents. A definition should be interpreted no more strongly than its cited source and approval evidence permit.

The following classifications guide interpretation:

- **Established terminology or principle:** Explicitly stated in repository governance or a source-of-truth document. This does not mean every detailed implementation mapping is approved.
- **Proposed architectural terminology:** A concept or responsibility described as proposed, planned, or unresolved. It may aid discussion but does not establish approval or implementation.
- **Capability status:** One of the seven labels whose meanings are defined in [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md). These are not architecture-decision lifecycle states.
- **Decision-record lifecycle:** Proposed lifecycle labels in [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md). Their use does not establish decision authority.
- **Open-decision lifecycle:** Proposed labels in [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md). They do not automate resolution or replace capability statuses.

When sources conflict, a term has multiple plausible meanings, or approval authority is unclear, record the ambiguity and refer to the applicable open question. Do not silently choose a stronger definition or create a new decision in the glossary.

## 3. Canonical Terms

Definitions below summarize relevant repository sources. Status notes describe the evidence boundary; a documented term does not prove a working capability.

### Repository and governance

| Term | Definition and role | Status or ambiguity | Source |
|---|---|---|---|
| `claude-skills` | Provider-neutral, skill-driven engineering platform for designing, building, governing, validating, and maintaining software systems, including SUPER AGI. | Established product identity; it is not the SUPER AGI runtime. | [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) |
| **SUPER AGI** | Separate target product/system that the engineering platform helps design and maintain. Its stated direction is one unified system with specialized modules and shared infrastructure. | Product direction is documented; runtime achievement and operational state are not established. | [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) |
| **Architecture governance** | Rules for architecture authority, proposal classification, explicit approval evidence, scope, and change traceability. | Governance policy is documented; a centralized operational governance service is not established. | [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md) |
| **Source of truth** | The authority-entry point that defines architecture classifications and how approval evidence determines authority. | Refers specifically to [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md); it does not approve proposals merely by existing. | [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) |
| **Architecture decision record (ADR)** | A scoped record of a decision question, outcome, rationale, consequences, and supporting evidence. | The `ADR-0001` identifier and reusable template are proposed conventions; authority and approval ownership remain unresolved. | [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md), [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) |
| **Open architecture decision** | An unresolved architecture question or pending choice requiring clarification, evidence, or an authorized outcome. | `OPEN-0001` identifiers and lifecycle labels are proposed conventions, not an automated workflow. | [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) |
| **Capability status** | One of the canonical labels describing evidence for a bounded capability: `IMPLEMENTED`, `ADAPTER-READY`, `MOCKED`, `EXPERIMENTAL`, `NOT IMPLEMENTED`, `BLOCKED`, or `UNKNOWN`. | Status applies only to its evidenced scope and is distinct from approval, lifecycle, compatibility, or release. | [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| **Evidence** | Observed material used to support a bounded claim, such as a source artifact, command result, test, trace, evaluation, or approval record. | Evidence supports only the scope actually observed; evidence does not itself approve architecture. | [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| **Proposed design** | A recommendation or architecture description intended for consideration that lacks sufficient explicit approval evidence to be treated as accepted architecture. | Must not be silently promoted to canonical behavior. | [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) |
| **Accepted decision** | A decision outcome recorded with explicit evidence of the approving authority, date or durable record, scope, and what was authorized. | Approval only applies within the evidenced scope; implementation, evaluation, integration, and release may remain separate. | [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) |

### System architecture

| Term | Definition and role | Status or ambiguity | Source |
|---|---|---|---|
| **Unified Brain** | Part of the stated product principle for one unified SUPER AGI system, containing specialized intelligence domains rather than independent AI products. | Product-level phrase; no operational brain component or detailed contract is established. | [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md) |
| **Super AGI OS** | The requested phrase is not defined as an architecture component in the reviewed canonical documents. | Unresolved terminology; do not infer an operating system, runtime, or platform contract from the name. | [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) |
| **Master Core** | Proposed coordinating core for the intended unified SUPER AGI architecture, with conceptual responsibilities across bounded tasks and shared capabilities. | Form, interfaces, decomposition, authority, and L15 placement remain unresolved; no operational Master Core is demonstrated. | [`MASTER-CORE.md`](MASTER-CORE.md), [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) |
| **Universal Intelligence Fabric** | A named shared-intelligence concept in the architecture direction for common intelligence capabilities. | Exact scope, interfaces, placement, and relationship to routing or shared infrastructure remain unresolved; no operational fabric is established. | [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`MASTER-CORE.md`](MASTER-CORE.md) |
| **Universal Infrastructure** | Proposed shared capabilities intended to support modules and the unified system without turning modules into independent products. | Component boundaries, implementation forms, ownership, interfaces, and runtime status remain unresolved. | [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) |
| **Intelligence Plane** | Responsibility grouping for provider-neutral intelligence contracts, reasoning workflows, model-selection boundaries, and shared intelligence services. | Plane name is established; detailed interfaces, ownership, and implementation are proposed or unresolved. | [`FIVE-PLANES.md`](FIVE-PLANES.md) |
| **Knowledge Plane** | Responsibility grouping for knowledge resources, context, memory, retrieval, provenance, and related data infrastructure. | Plane name is established; persistent knowledge infrastructure and exact boundaries are not demonstrated or fully approved. | [`FIVE-PLANES.md`](FIVE-PLANES.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) |
| **Agent Plane** | Responsibility grouping for agent roles, canonical Skills, bounded task coordination, handoffs, and tool invocation boundaries. | Plane name is established; it does not imply all agent roles or execution systems exist. | [`FIVE-PLANES.md`](FIVE-PLANES.md) |
| **Domain Plane** | Responsibility grouping for specialized engineering and project domains, domain capabilities, and module boundaries. | Plane name is established; engineering domains are not thereby complete SUPER AGI runtime modules. | [`FIVE-PLANES.md`](FIVE-PLANES.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md) |
| **Control Plane** | Responsibility grouping for governance, authorization, security policy, architecture decisions, capability status, traceability, and execution constraints. | Plane name and governance intent are documented; a fully operational centralized control system is not demonstrated. | [`FIVE-PLANES.md`](FIVE-PLANES.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md) |
| **L0–L15 Layer Map** | Proposed organization of the platform/system into 16 numbered layers, with L0 as the physical/compute boundary and L15 as the Master Control boundary. | The endpoints are grounded; intermediate layer names, contracts, dependencies, and plane mappings are proposed or unresolved. | [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) |
| **Global Shell** | The phrase is not defined as a component or contract in the reviewed architecture documents. | Unresolved terminology; no UI shell, process boundary, or capability should be inferred. | [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) |

### Shared intelligence infrastructure

| Term | Definition and role | Status or ambiguity | Source |
|---|---|---|---|
| **Universal Context** | Proposed architecture for selecting, scoping, handling, and propagating context relevant to an operation. | No context engine or persistent context service is demonstrated; hierarchy and propagation rules remain unresolved. | [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) |
| **Context hierarchy** | Proposed scope sequence `Global → Organization → User → Project → Domain → Task → Agent`. | Not an approved contract; identity, inheritance, visibility, precedence, merge, and override rules remain unresolved. | [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) |
| **Universal Intelligence Router** | Proposed selection boundary for relevant reasoning or intelligence capabilities across modules and shared services. | Matching algorithm, authority, and relationship to model/provider routing remain unresolved; no router implementation is demonstrated. | [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md) |
| **Cross-AGI Collaboration Engine** | Requested name for collaboration infrastructure among modules. Existing sources describe cross-AGI collaboration as a proposed responsibility, but do not establish this exact named component contract. | Component naming, protocol, topology, and authority are unresolved; do not treat it as an implemented engine. | [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) |
| **Universal Intelligence Bus** | The term is not defined as an approved interface or component in the reviewed architecture documents. | Unresolved terminology; no message bus, transport, or event protocol is established. | [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) |
| **Model Gateway** | Proposed provider-neutral boundary for model requests, provider/model capability evidence, routing policy, adapters, and normalized results. | Request contracts, routing, adapters, credentials, and runtime behavior remain unresolved or unimplemented. | [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md) |
| **Provider adapter** | Provider-specific translation or configuration that maps canonical behavior to a provider's API, format, authentication, and capabilities. | A usable boundary may be `ADAPTER-READY`; operational integration requires separate evidence for configuration, credentials, authorization, invocation, and behavior. | [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| **Model routing** | Selection of a provider/model for a request under capability, policy, permission, and data-disclosure constraints. | Routing policy, eligibility, fallback, and evaluation remain proposed or unresolved; no operational router is established. | [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md) |
| **Shared memory** | Proposed retention of authorized information for potential later use, distinct from transient context and curated knowledge. | Persistence, ownership, retention, deletion, provenance, and write authorization remain unresolved; no persistent shared memory is demonstrated. | [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) |
| **Knowledge infrastructure** | Data and retrieval capabilities for curated or structured knowledge, with provenance and access boundaries. | Storage, ownership, retrieval, freshness, and enforcement are not established as an operational shared system. | [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`FIVE-PLANES.md`](FIVE-PLANES.md) |
| **World Model** | Proposed representation of entities, states, relationships, or dynamics used as a potential knowledge/context source. | Scope, authority, provenance, update semantics, and evidence requirements remain unresolved; the name is not evidence of a working model. | [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) |
| **Agent** | A bounded execution role or process that uses instructions, context, and authorized capabilities to perform work or handoffs. | Role definitions and execution are distinct; a role description does not prove runtime behavior or permissions. | [`FIVE-PLANES.md`](FIVE-PLANES.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) |
| **Tool** | A local or external development utility accessed through an explicitly defined interface and permissions. | Declaration, discovery, integration readiness, and authenticated operational readiness are distinct states. | [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md) |
| **Skill** | Reusable engineering instructions or a declared execution contract that encodes a bounded procedure. | A Skill definition does not execute itself or prove successful execution. | [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) |
| **Workflow** | An ordered, bounded process that coordinates work stages, gates, validation, and evidence reporting. | Workflow documentation expresses procedure; it does not prove an execution engine or end-to-end operation. | [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`../workflows/spec-to-implementation/README.md`](../workflows/spec-to-implementation/README.md) |

### Domain and module architecture

| Term | Definition and role | Status or ambiguity | Source |
|---|---|---|---|
| **Major AGI module** | One of the intended specialized intelligence domains within the single unified SUPER AGI product. | The “100” portfolio is product direction; no authoritative list of 100 operational modules is established. | [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) |
| **Module registry** | Proposed inventory of module identity, classification, responsibilities, dependencies, capabilities, lifecycle, security, and evidence metadata. | Schema, identifiers, authority, storage, and operational service remain unresolved or absent. | [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) |
| **Module contract** | Proposed description of a module's identity, responsibilities, boundaries, inputs/outputs, dependencies, permissions, and evidence expectations. | No finalized schema, runtime API, conformance system, or operational module interface is established. | [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md) |
| **Dedicated AGI workspace** | Product-direction phrase for a workspace/navigation surface associated with a specialized module. | A workspace is not an independent AI product or proof of a functioning module; exact representation and mapping remain unresolved. | [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) |
| **Cross-AGI collaboration** | Proposed governed cooperation and information exchange among modules, agents, providers, or external systems where authorized. | Protocols, routing, permissions, context sharing, arbitration, and failure handling remain unresolved; no operational collaboration runtime is demonstrated. | [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md) |
| **Module extensibility** | Intended ability to add or evolve specialized module definitions while preserving one unified system and shared responsibility boundaries. | Identity, compatibility, lifecycle, and portfolio governance remain unresolved; no extension mechanism is established. | [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md) |
| **Shared infrastructure** | Common capabilities proposed to support multiple modules or planes under explicit boundaries. | Shared availability does not imply unrestricted access, automatic memory sharing, or separate operational services. | [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md) |
| **Domain-specific capability** | A bounded behavior belonging to a specialized engineering or project domain/module responsibility. | Must be assessed by evidence for its own scope; a domain label does not establish a SUPER AGI runtime capability. | [`FIVE-PLANES.md`](FIVE-PLANES.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |

### Evidence and implementation maturity

| Term | Definition and role | Status or ambiguity | Source |
|---|---|---|---|
| `IMPLEMENTED` | Concrete implementation exists and sufficient behavior evidence supports it. | Does not by itself establish complete workflow operation, approval, compatibility, security enforcement, or production readiness. | [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| `ADAPTER-READY` | A usable adapter boundary exists without demonstrated full runtime behavior. | Does not establish an operational external integration, credentials, authentication, authorization, or end-to-end operation. | [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| `MOCKED` | Behavior is simulated by a stub or replacement. | Mock behavior does not prove the replaced dependency or real integration works. | [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| `EXPERIMENTAL` | Implementation exists but is incomplete or limited in validation. | Scope and limitations must be disclosed; not a claim of general or production readiness. | [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| `NOT IMPLEMENTED` | Required functionality is absent or only placeholder/proposal content. | Use only where available evidence supports absence or placeholder status. | [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| `BLOCKED` | Implementation or validation is stopped by a recorded prerequisite. | Identify the blocking prerequisite; do not imply implementation or validation succeeded. | [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| `UNKNOWN` | Available evidence is insufficient for a stronger status. | Unknown is not proof of success, failure, or absence. | [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| **Documentation evidence** | Architecture text, contracts, manifests, policies, or other documents that support claims about recorded intent or declared requirements. | Does not by itself prove implementation, execution, enforcement, approval, or operational readiness. | [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| **Implementation artifact** | Source code, configuration, executable, or other artifact intended to realize specified behavior. | Presence alone does not demonstrate that behavior runs or is correct. | [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| **Executable integration** | A component that can be invoked in a stated environment with required dependencies, configuration, permissions, and authorization. | Execution readiness and actual operational behavior require direct evidence; declarations are insufficient. | [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| **Operational evidence** | Observed behavior in a stated environment, including relevant dependency, authentication, authorization, execution, and failure behavior for the claim. | Evidence is bounded to the observed scope and does not establish universal reliability or readiness. | [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) |
| **Verification authority** | The person, process, or source authorized to determine whether specified criteria have been met. | Authority and independence criteria are unresolved unless an applicable record explicitly establishes them. | [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md), [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) |

## 4. Important Distinctions

| Distinction | Correct interpretation |
|---|---|
| `claude-skills` engineering repository vs. SUPER AGI runtime | The repository supports governed engineering; it is not the runtime being engineered. |
| One unified SUPER AGI vs. 100 independent AI products | The intended 100 modules are specialized domains within one unified product, not 100 independent products. |
| Architectural concept vs. implemented capability | A concept describes intent; implementation and behavior require separate artifacts and evidence. |
| Proposal vs. accepted decision | A proposal is not accepted without explicit approval evidence within scope. Repetition or implementation does not silently approve it. |
| Capability status vs. decision-record status | Capability labels describe bounded implementation evidence; decision lifecycle labels describe a decision record's state. |
| Prepared provider adapter vs. operational integration | An adapter boundary may be usable without proving authentication, authorization, provider behavior, or end-to-end operation. |
| Module definition vs. working module | A registry entry or contract describes identity and intent; it does not instantiate or prove a functioning module. |
| Shared infrastructure vs. domain-specific capability | Shared infrastructure provides cross-cutting responsibilities; domain capabilities address specialized responsibility. Neither implies the other is operational. |
| Documentation evidence vs. executable or operational evidence | Documents support claims about intent and requirements; execution evidence supports only observed behavior in its stated scope. |
| Dedicated workspace vs. independent AI system | A workspace is a navigation or interaction surface associated with a domain; it does not create an independent product or prove a module runtime. |

## 5. Naming and Terminology Conventions

These are documentation conventions, not automated checks:

- Prefer existing canonical terms over newly invented synonyms.
- Preserve capitalization of named architecture components and plane names.
- Use the exact canonical capability-status labels as written in [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md).
- Use relative links to authoritative or relevant existing architecture documents.
- Mark proposed concepts, assumptions, and unresolved behavior explicitly.
- Do not use “implemented,” “operational,” “approved,” “AGI,” or “conscious” as maturity claims without supporting evidence appropriate to the claim.
- Define abbreviations before reuse.
- Do not define a term more strongly than its source document permits.
- Distinguish provider-neutral contracts from provider-specific adapters and behavior.
- Keep documented design, implementation, verification, evaluation, approval, and deployment separate.

No automated terminology enforcement is established.

## 6. Ambiguity and Unresolved Terminology

The terms **Super AGI OS**, **Global Shell**, and **Universal Intelligence Bus** do not have authoritative definitions in the reviewed architecture documents. They are included in Section 3 only to identify that ambiguity; no operating-system, shell, transport, or bus architecture is implied.

**Cross-AGI Collaboration Engine** is also not established as a named component contract. Existing sources describe cross-AGI collaboration infrastructure and patterns as proposed concepts, but do not establish an engine's implementation, interfaces, or authority.

**Universal Intelligence Router** appears as a proposed concept. Its relationship to the **Model Gateway** is explicitly unresolved: selecting among intelligence or module capabilities is distinct in scope from selecting a provider/model, but ownership and contracts are not settled.

The context hierarchy, layer assignments, plane responsibilities, shared-memory behavior, knowledge infrastructure, module/workspace mapping, and verification authority also depend on unresolved architecture choices. Relevant records include:

- [`OPEN-0003`](OPEN-DECISIONS.md) — L0–L15 boundaries and inter-layer contracts
- [`OPEN-0004`](OPEN-DECISIONS.md) — Five-plane responsibilities and interactions
- [`OPEN-0006`](OPEN-DECISIONS.md) — Shared infrastructure interfaces and ownership
- [`OPEN-0007`](OPEN-DECISIONS.md) — Data ownership, persistence, retention, and lifecycle
- [`OPEN-0008`](OPEN-DECISIONS.md) — Universal Context hierarchy and propagation
- [`OPEN-0011`](OPEN-DECISIONS.md) — Cross-AGI collaboration contracts
- [`OPEN-0012`](OPEN-DECISIONS.md) — Model Gateway and provider routing
- [`OPEN-0014`](OPEN-DECISIONS.md) — Capability evidence, freshness, and readiness

The presence of an entry in an open-decision register identifies uncertainty; it does not select an answer or imply the associated capability exists.

## 7. Related Documents

The following existing sources inform this glossary:

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
- [`spec-to-implementation workflow`](../workflows/spec-to-implementation/README.md)

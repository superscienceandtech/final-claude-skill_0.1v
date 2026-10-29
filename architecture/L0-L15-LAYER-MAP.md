# L0–L15 Architecture Layer Map

## A. Purpose and Architecture Status

This document defines the intended organization of the `claude-skills` engineering platform into 16 numbered architecture layers. It helps future work identify responsibility boundaries, dependency direction, interfaces, and implementation placement. It does not create a runtime, introduce an additional mandatory directory, or redefine the five-plane architecture.

Authority for this map is subordinate to [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md). The [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md) supplies product intent, and [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) supplies responsibility boundaries.

The overall L0–L15 sequence is not approved as a complete architectural specification. Repository evidence establishes only the following firmly identified endpoints:

- L0 is the foundational physical/compute boundary.
- L15 is the Master Control boundary.

Intermediate names and responsibilities below are planning proposals derived from existing repository concepts and proposed ARC dependencies. They are not canonical decisions until separately approved. A layer's existence in this document does not establish implementation, evaluation, or operational readiness.

## B. Layer Design Principles

1. **Responsibility separation** — one concern has a primary owner; similar components do not silently become new sources of authority or behavior.
2. **Explicit dependencies** — dependencies, inputs, outputs, interfaces, and forbidden directions must be stated rather than inferred.
3. **Defined interfaces** — provider-neutral contracts precede provider-specific translations. Declaration registries do not imply execution capability.
4. **Provider neutrality** — canonical behavior must not depend on one model backend, coding agent, provider API, or vendor format.
5. **Security and control boundaries** — credentials, sensitive data, subprocesses, network access, repository writes, and consequential actions require explicit authorization and least privilege.
6. **Evidence-based status** — documentation, source presence, tests, independent evaluation, approval, and operational readiness remain separate states.
7. **Low coupling** — higher layers should not require provider, tool, filesystem, or vendor knowledge that belongs at lower adapter boundaries.
8. **Intent versus implementation** — planned components, source artifacts, implemented capabilities, evaluated results, approvals, and operational verification are reported independently.
9. **Human authority** — AI-generated proposals do not authorize irreversible or sensitive operations.
10. **One task per layer change** — implementation and migration work should remain bounded and preserve the repository's stop conditions.

## C. L0–L15 Layer Map

The table uses three status patterns:

- **Established endpoint** — evidence explicitly grounds the boundary.
- **Evidence-grounded proposal** — repository material supports a responsibility, but no separate approval establishes the exact layer assignment.
- **Unresolved/PROPOSED** — a useful placeholder exists, but the repository lacks a decision sufficient to canonicalize it.

| Layer | Proposed name | Primary responsibility | Inputs | Outputs | Dependencies | Boundary and non-responsibilities | Approval status / evidence level |
|---|---|---|---|---|---|---|---|
| L0 | Physical and Compute Boundary | Represent the machines, operating environments, processes, repository worktrees, and external execution resources on which engineering work runs. | Local or remote execution environment; filesystem; operating-system capabilities; process boundaries | Available execution context; file and process access | None at the conceptual platform layer | Does not select a provider, authorize operations, implement memory, or make tools operational. L0 also does not prove installation or authentication from source presence. | **Established boundary name:** repository baseline explicitly identifies L0 as foundational physical/compute boundary; exact host model remains unresolved. |
| L1 | Repository and Execution Foundation | Provide repository integrity, source inspection, bounded worktrees, developer conventions, and the foundation for repository-native execution. | Repository instructions; current working tree; source files; existing scripts and tests | Repository facts; scoped changes; validation invocation context | L0 | Does not grant Git history operations, external access, deployment, or approval. Ownership guidance is coordination, not authority. | **Evidence-grounded proposal:** repository governance and proposed ARC-00 are supported, but exact L1 approval is unresolved. |
| L2 | Architecture and Contract Foundation | Preserve architecture authority, responsibility boundaries, module contracts, interfaces, schemas, decisions, and unresolved architecture questions. | Governance documents; product requirements; proposal records; approved decisions | Canonical requirements; contracts; decision records; conflict reports | L0–L1 | Does not implement runtime modules, approve proposals by its own presence, or convert an implementation into architecture approval. | **Evidence-grounded proposal:** canonical architecture documents and ARC-02 identify this role; L2 mapping is not separately approved. |
| L3 | Security, Identity, and Permission Governance | Define secrets handling, trust boundaries, least privilege, authorization requirements, auditability, redaction, human-control gates, and integration permissions. | Tasks; sensitive-data declarations; tool/provider contracts; repository policy | Permission boundaries; approval dependencies; security review requirements; sanitized evidence | L1–L2 | Policy documentation is not a runtime enforcement guarantee. Does not implement an identity system or replace human approval. | **Evidence-grounded proposal:** governance and Security material support the responsibility; exact L3 mechanics are unresolved. |
| L4 | Canonical Skill and Knowledge Contracts | Define canonical reusable engineering procedures, Skill contracts, metadata, versioning, discovery rules, and source relationships. | Requirements; approved contracts; Skill sources and manifests; lifecycle rules | Validated Skill declarations; bounded procedure definitions; discovery/registry metadata | L2–L3 | Does not execute provider behavior, infer a tool implementation, or treat registration as operational capability. | **Evidence-grounded proposal:** `skills/` and ARC-01 establish a repository concern here; exact layer placement remains unresolved. Existing source artifacts are present, but end-to-end authorization is unverified without direct execution evidence. |
| L5 | Agent Role and Handoff Contracts | Define specialized agent-role scope, inputs, outputs, escalation, permissions, delegation, and handoffs. | Canonical architecture; Skill contracts; task context; security boundaries | Agent-role contracts; bounded handoff records; permission and stop conditions | L2–L4 | Does not create implicit tool permissions or verify an agent implementation merely from a role description. | **UNRESOLVED:** proposed ARC-04 establishes an intended concern, but no canonical agent-role definitions or approved mapping are present. |
| L6 | Context, Memory, and Knowledge Fabric | Manage bounded context sources, provenance, retention, retrieval, deletion, and access policy for engineering and platform knowledge. | Authorized repository context; specifications; source provenance; user/task context | Scoped context; knowledge records; retrieval evidence; retention/deletion outcomes | L2–L4, conditionally L3 | Does not imply permanent memory, universal memory, unrestricted retention, or implemented persistent storage. | **UNRESOLVED / PROPOSED:** ARC-09 and SUPER AGI concepts establish the concept; no approved data model or implementation is shown. |
| L7 | Model and Reasoning Gateway Boundary | Separate canonical requests from provider-specific model APIs, model capabilities, authentication, routing policy, and unsupported behavior. | Canonical prompts/contracts; provider configuration; authorized credentials | Provider-ready requests; normalized results; compatibility and unsupported-operation information | L3–L5; conditionally L6 | Does not make provider adapters operational and does not choose provider semantics as architecture authority. | **UNRESOLVED / PROPOSED:** provider-neutral gateway concepts are established, but no provider adapter is proven and no exact gateway contract is approved. |
| L8 | Agent Coordination and Orchestration | Coordinate bounded workflows, stages, dependencies, handoffs, retries where approved, and stop behavior across Skills and agent roles. | Scoped task; workflow definition; agent/Skill availability; security decisions | Ordered workflow state; handoff evidence; bounded execution outputs; stop/block records | L3–L7 | Does not imply autonomous control, universal orchestration, persistent service state, or deployment readiness. | **UNRESOLVED / PROPOSED:** the specification-to-implementation workflow establishes a bounded orchestration concept, but no complete orchestration runtime or approved layer assignment is demonstrated. |
| L9 | Tool Discovery and Integration Boundary | Discover tool contracts and expose explicitly registered capabilities without granting execution capability. | Tool requirements; registered contracts; adapter metadata; permissions | Tool catalog; match/selection plans; authorized execution requests | L3, L7–L8 | Discovery does not verify installation, authentication, adapter implementation, or operational readiness. It does not contain provider behavior itself. | **Evidence-grounded proposal:** tool-framework and tool-discovery source artifacts exist, but the repository does not show all mandatory tools integrated or operational. |
| L10 | Developer Tool and External Action Boundary | Define adapter and integration-facing interfaces to approved local or external developer tools and account/network resources. | Authorized tool requests; integration configuration; credentials supplied by approved mechanisms | Tool results; failures; audit metadata; revocation/unsupported-operation evidence | L3, L9 | Does not claim the 14 mandatory tools are installed, integrated, authenticated, or externally reachable. It does not grant account or network access. | **UNRESOLVED / PROPOSED:** ARC-08 and integration guidance establish the concern; provider/tool implementations are not complete. |
| L11 | Research, World-Model, and Evidence Services | Support sourced research, provenance, world-model representations, hypothesis tracking, and traceable claims. | Questions; approved sources; context; evidence records | Source-linked findings; uncertainty records; evaluable claims; provenance | L3, L6, L8–L10 where authorized | Does not treat generated summaries as facts, merge inference with observation, or establish a runtime world model. | **UNRESOLVED / PROPOSED:** research/world-model concepts exist in product and proposed architecture material, but no implementation or exact layer mapping is established. |
| L12 | Verification, Evaluation, and Capability Evidence | Verify implementation behavior and independently evaluate properties against defined acceptance criteria and benchmark scope. | Specifications; implementations; fixtures; contracts; validation commands; test and evaluation results | PASS, FAIL, SKIPPED, or NOT RUN evidence; capability-status recommendations; limitations | L2–L3, L8–L11 as applicable | Does not replace implementation review, approval, or release. It does not imply that passing source tests prove end-to-end operational or security readiness. | **Evidence-grounded proposal:** verification workflow and proposed ARC-06/ARC-11 establish the role; approval/evaluation evidence for all capabilities is incomplete. |
| L13 | Controlled Evolution and Release Governance | Compare evidence, manage approved changes, record migrations/deprecations, and govern evaluation, integration, publication, and release gates. | Approved decisions; implementation/evaluation evidence; compatibility and security review | Traced change record; release recommendation; deprecation/migration plan | L2–L3, L12 | Does not itself approve a change, alter Git history, deploy software, publish artifacts, or bypass human authority. | **UNRESOLVED / PROPOSED:** evolution concepts exist, but lifecycle authority and release mechanics are unresolved. |
| L14 | Product and SUPER AGI Domain Coordination | Coordinate modular domain work for the unified SUPER AGI target while keeping modules as specialized domains of one system. Preserve shared infrastructure and prevent module boundaries from becoming independent products. | Canonical architecture; module contracts; domain requirements; evidence records | Coordinated module plans; registry inputs; cross-module compatibility requirements | L4–L13 as required | Does not implement the unified brain, the 100 modules, a SUPER AGI runtime, or shared universal infrastructure by documentation alone. | **UNRESOLVED / PROPOSED:** target-system concept is established by the constitution, but module registries, contracts, and implementation evidence do not exist. |
| L15 | Master Control Boundary | Represent the authoritative control boundary that can coordinate the intended platform and target-system domains while preserving approvals, evidence, safety gates, and bounded stopping behavior. | Approved architecture and task scope; domain/module state; authorization evidence; verification and security state | Authorized control decisions; bounded orchestration directives; stop/escalation outcomes; audit evidence | All lower layers that are actually approved and implemented, subject to architecture | Must not bypass human authority, silently grant permissions, or be inferred from the existence of documentation. It does not establish that a Master Control runtime exists. | **Established boundary name / UNRESOLVED implementation:** repository evidence identifies L15 as the Master Control boundary; its authority and implementation are not approved. |

## D. Dependency Direction

The intended conceptual dependency direction is from foundational and contract layers toward higher coordination and governance layers:

`L0 → L1 → L2 → L3, with later cross-cutting and orchestration concerns consuming lower-layer contracts without replacing them.`

More precisely, current evidence supports cautious dependencies such as:

- L1 repository foundations support L2 architecture and contracts.
- L2 contracts support L4 Skill definitions, L5 role contracts, L6 context rules, and future orchestration contracts.
- L3 security and permission policy should constrain L5–L15 actions involving sensitive data, tools, providers, credentials, or external effects.
- L4 canonical definitions should feed provider-neutral workflow coordination and should precede provider adapter translation at L7/L9/L10.
- L12 verification should consume implementation and contract evidence but must remain separate from the implementation owner and approval authority.
- L15 should be a control boundary, not a bypass around canonical architecture, human approval, or lower-layer validation.

The following patterns are dangerous unless an explicit approved contract authorizes and enforces them:

- Providers or tools becoming sources of canonical architecture or repository instructions.
- High-level orchestration reading or writing files outside lower-layer repository or security boundaries.
- Agent, workflow, or Master Control code claiming approval or implementation authorization from generated output.
- L0–L3 or L9–L10 concepts being imported directly into product code without provider-neutral contracts.
- Verification-dependent status being inferred from documentation, compilation, file presence, or interface declarations.
- Cyclic authority where an implementation rewrites the architecture that authorized it without a separate approval process.

The repository does not presently demonstrate dependency enforcement. Therefore, layer dependencies describe intended architecture, not enforced runtime topology.

## E. Relationship to the Five Architectural Planes

The five architectural planes are planned cross-cutting views. Their exact names and boundaries are not established by an existing document, so this map does not assign each plane a fixed layer range and does not claim a one-to-one mapping.

The intended relationship is:

- Layers express vertical responsibility and dependency organization from physical foundation to Master Control.
- Architectural planes express horizontal cross-cutting concerns that may span multiple layers.
- A plane can cut through contracts, execution, security, context, providers, tools, validation, or governance; it is not a replacement for a layer.
- A future `FIVE-PLANES.md` must define the exact plane names and layer intersections before they are treated as approved architecture.

No existing repository file currently provides authoritative evidence sufficient to establish a definitive plane-to-layer matrix.

## F. Relationship to Shared Infrastructure

### Master Core

The Master Core remains a planned shared coordination concept beneath or across the intended unified SUPER AGI organization. This layer map places only Master Control explicitly at L15 and does not assign the Master Core an exact layer or claim that it is implemented. The future `MASTER-CORE.md` must define that relationship.

### Universal Intelligence Fabric

The Universal Intelligence Fabric is a planned shared infrastructure concept. It is not represented here as an implemented communication bus, service, protocol, or mandatory runtime. If approved later, placement must account for evidence, security, performance, context, and modular ownership rather than automatic placement across every layer.

### Shared Memory and Knowledge

L6 is the proposed planning boundary for bounded context, memory, knowledge provenance, access, and retention. It is not proof of a persistent memory or universal knowledge implementation. Sensitive-data and deletion requirements remain under L3 and must be approved separately.

### World Model

L11 is proposed as a research and world-model/evidence responsibility. This does not establish an implemented model, factuality guarantee, or autonomous reasoning capability.

### Agent, Tool, and Skill Infrastructure

- Skills occupy the planning relationship at L4.
- Agent roles occupy the proposed L5 relationship.
- Tool discovery occupies L9.
- External action and tool integrations occupy L10.
- Workflows coordinate them at L8 with security constraints from L3.

### Universal Context

Universal Context is a planned architecture concept, not evidence of implemented universal context. It should be constrained by provenance, authorization, retention, isolation, and clear source boundaries before any relationship to L6 or higher coordination layers is approved.

### Cross-AGI Collaboration

Cross-AGI collaboration is unresolved and proposed only. It must not be interpreted as an implemented multi-agent runtime, federation protocol, or shared-memory guarantee.

### Model Gateway

L7 represents a proposed provider/model boundary. It must remain separate from canonical Skills and repository architecture. No adapter should become a canonical definition or grant capabilities absent from the canonical contract.

### Security and Governance

Security and governance cross-cut L3 and constrain all layers. They are also relevant to approval, auditability, evidence, evolution, and Master Control at L12–L15. A cross-cutting control does not prove technical enforcement.

### Capability-Status Reporting

Capability status belongs primarily in verification/evidence and reporting, represented at L12. Status is consumed by governance and evolution layers but cannot be self-awarded by implementation or documentation.

## G. Provider and Tool Boundaries

Provider adapters belong outside canonical Skill behavior and should map provider-neutral contracts into provider-specific formats only at approved provider and gateway boundaries, conceptually around L7 and L9–L10. Provider credentials, account access, network access, and consequential operations require explicit authorization.

Tool integration contracts should separate:

1. tool declaration or metadata;
2. discovery and selection;
3. adapter registration;
4. execution authorization;
5. observed execution; and
6. authenticated operational readiness.

The repository contains source artifacts for tool contracts, discovery, workflow, and local framework behavior, and a Skill implementation source. It does not demonstrate the 14 mandatory tools as all installed, integrated, authenticated, or operational. The `integrations/` documentation states that broad integrations are not defined by default.

A provider or tool declaration must not be treated as adapter-ready solely because it is discoverable or registered. Compatibility status and operational status require their own evidence.

## H. Security and Control Boundaries

Authorization and permissions should be explicit at the lowest appropriate layer and propagated into tool and provider execution boundaries:

- L1 protects repository and filesystem scope.
- L2 separates authoritative decisions and contracts from proposals.
- L3 defines trust, secret, permission, audit, redaction, and approval requirements.
- L7 prevents provider-specific behavior from silently changing canonical semantics.
- L9–L10 require explicit tool and external-action boundaries.
- L12 records validation and unresolved risk rather than granting approval.
- L13/L15 enforce stopping, escalation, and human-control conditions only to the extent that approved mechanisms exist.

The architecture should retain evidence of denied actions, uncertain authorization, failures, and partial results. It should not silently ignore a security conflict or reinterpret missing approval as consent.

This map is descriptive documentation. It does not guarantee access containment, secret protection, prompt-injection resistance, audit logging, provenance, sandboxing, secure subprocess handling, or operational security controls.

## I. Implementation Mapping

Future implementation work can use the following evidence classes when assigning repository components to layers:

- **Planned component:** named by a proposal or architecture document but absent from the repository or without approved contracts.
- **Existing source artifact:** source, documentation, or schema that is present and inspectable but not yet verified or authorized as an end-to-end capability.
- **Implemented capability:** source behavior demonstrated through focused execution and reproducible evidence.
- **Operationally verified capability:** installation, authentication, authorization, execution, failure behavior, compatibility, and environment readiness observed in the applicable host.

Current repository examples include:

| Component | Evidence class | Relevant layer relationship | Current limitation |
|---|---|---|---|
| Architecture governance documents | Existing source artifact / documentation | L2 | Do not by themselves approve proposals, implementation, or runtime behavior. |
| Canonical implementation Skill | Existing source artifact | L4 and L8 | Presence does not prove execution or provider compatibility without observed evidence. |
| Skill registry and manifest/source framework | Existing source artifact | L4 and supporting contract infrastructure | Source behavior requires validation evidence separate from implementation status. |
| Tool framework, discovery, and workflow source | Existing source artifact | L9, with possible interfaces to L10 | Contracts do not prove tool installation, authentication, adapter registration, or invocation readiness. |
| Specification-to-implementation workflow | Existing source artifact | L8/L12 relationship | Workflow is process documentation and source framework evidence, not proof of independent runtime enforcement. |
| Tests | Existing source artifacts | L12 evidence layer | Tests were not executed for this task and must not be cited here as passing evidence for this map. |
| Providers and mandatory tool integrations | Planned components | L7/L9/L10 | No complete adapter or 14-tool integration readiness is established. |

Future mapping must identify exact paths only after they exist. A directory, source module, manifest, or test file should not be assigned an architectural layer merely by presence.

## J. Unresolved Decisions

The following decisions require separate approval or evidence:

- the authoritative names and responsibilities of intermediate layers L1–L14;
- whether L7, L9, and L10 should be separate physical or conceptual layers rather than cross-cutting boundaries;
- an exact dependency matrix between L0–L15;
- an exact relationship between the layers and the five architectural planes;
- the authority and implementation model for L15 Master Control;
- the exact contract and placement of the Master Core;
- whether Universal Intelligence Fabric is a runtime, set of contracts, shared service boundary, or non-implemented concept;
- the persistence, access, retention, and provenance model for memory and knowledge;
- the exact World Model contract and evidence requirements;
- agent-role format, lifecycle, and execution evidence;
- canonical Skill approval beyond the existing scoped records;
- provider selection, adapter contracts, and compatibility guarantees;
- installation, authentication, permissions, and operational readiness for the 14 mandatory tools;
- the independent verification and evaluation authority;
- capability-status acceptance and publication rules;
- controlled-evolution, migration, and release gates;
- the exact SUPER AGI module-registry and module-contract model;
- approval hierarchy and integration base, which remain unestablished; and
- technical security enforcement evidence, which must not be inferred from policy documents.

The repository should not proceed to implementation that depends on a missing layer decision when that decision is required for safe scope. The exact approved pin of the repository-audit specification authorizes that exact specification revision only; it does not authorize implementation, execution-host qualification, integration, publication, or release.

## K. Relationship to Other Canonical Documents

Existing documents:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) — architecture authority and document classification entry point.
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md) — product identity, scope, principles, and SUPER AGI boundary.
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) — responsibility and interaction boundaries.

Planned canonical targets, which do not exist and must not be presented as authoritative documentation:

- `architecture/FIVE-PLANES.md`
- `architecture/MASTER-CORE.md`
- `architecture/UNIVERSAL-INFRASTRUCTURE.md`
- `architecture/MODULE-REGISTRY.md`
- `architecture/MODULE-CONTRACT.md`
- `architecture/UNIVERSAL-CONTEXT.md`
- `architecture/CROSS-AGI-COLLABORATION.md`
- `architecture/MODEL-GATEWAY.md`
- `architecture/SECURITY-GOVERNANCE.md`
- `architecture/CAPABILITY-STATUS.md`
- `architecture/ARCHITECTURE-DECISIONS.md`
- `architecture/OPEN-DECISIONS.md`

Existing supporting evidence and proposal documents include:

- [`docs/architecture/arc-dependency-map.md`](../docs/architecture/arc-dependency-map.md) — proposed ARC dependencies and planned components.
- [`docs/architecture/team-file-ownership.md`](../docs/architecture/team-file-ownership.md) — proposed ownership coordination, not approval authority.
- [`docs/architecture/m1-contract-decisions.md`](../docs/architecture/m1-contract-decisions.md) — working proposal, not approved architecture.
- [`docs/architecture/decisions/m1-spec-approval-pin.md`](../docs/architecture/decisions/m1-spec-approval-pin.md) — narrow specification revision approval, with implementation and evaluation explicitly excluded.
- [`docs/audits/architecture-audit.md`](../docs/audits/architecture-audit.md) — historical audit evidence, not implementation or approval evidence.
- [`workflows/spec-to-implementation/README.md`](../workflows/spec-to-implementation/README.md) — bounded implementation and verification process.

This document is useful as an implementation-planning map only. Its proposed layer names and intermediate responsibilities become architecture authority only through the repository's separate approval process.

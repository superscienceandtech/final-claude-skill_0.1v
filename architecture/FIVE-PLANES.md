# Five Architectural Planes

## A. Purpose and Status

This document defines the five architectural responsibility planes of the `claude-skills` engineering platform:

1. Intelligence Plane
2. Knowledge Plane
3. Agent Plane
4. Domain Plane
5. Control Plane

The plane names are established baseline terminology. This document gives them responsibility-level definitions for future implementation planning. It does not claim that the planes are implemented, deployed, independently serviceable, or connected by approved protocols.

Authority is subordinate to [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md). This document is consistent with [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), and [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md).

The following distinctions apply:

- **Established baseline principle:** the repository requires exactly these five planes and treats them as architectural responsibility groupings.
- **Evidence-grounded proposal:** a plane responsibility is supported by existing repository concepts, source artifacts, proposals, or workflows.
- **Unresolved:** exact interfaces, ownership, execution topology, cross-plane dependencies, plane-to-layer mappings, and technical implementation mechanisms are not established.

The planes are cross-cutting views. They do not correspond one-to-one with L0–L15 layers, repository directories, services, runtime processes, or deployment units.

## B. Five-Plane Overview

| Plane | Primary responsibility | Intended capabilities | Inputs | Outputs | Owns / does not own | Dependencies | Security and governance | Status |
|---|---|---|---|---|---|---|---|---|
| Intelligence Plane | Provider-neutral intelligence contracts, reasoning workflows, model selection boundaries, and shared intelligence services. | Canonical reasoning requests; provider-neutral capability contracts; model routing policy; prompt and result normalization where approved. | Task intent; canonical contracts; authorized context; provider capability metadata | Provider-neutral requests; normalized outputs; compatibility or unsupported-operation information | Owns capability and reasoning contracts. Does not own canonical architecture, secrets, provider execution, persistent knowledge, or human approval. | Knowledge for grounded context; Agent for bounded execution coordination; Control for authorization; Domain for task meaning | Least privilege, provider boundaries, untrusted prompt handling, data disclosure review, and explicit approval for consequential actions | **Names established; implementation PROPOSED/UNRESOLVED** |
| Knowledge Plane | Knowledge resources, context, memory, retrieval, provenance, and data infrastructure. | Knowledge ingestion rules; bounded retrieval; provenance; retention and deletion; source-quality metadata where approved. | Repository specifications; approved sources; task context; provenance records | Scoped context; evidence records; retrieval results; retention and deletion status | Owns knowledge and memory contracts. Does not own intelligence behavior, executable provider routing, agent permissions, or SUPER AGI runtime authority. | Intelligence for retrieval requests; Agent for authorized access; Domain for domain data; Control for retention and access policy | Data classification, source authorization, retention, redaction, sensitive-data isolation, deletion, and auditability | **PROPOSED/UNRESOLVED; no persistent universal knowledge fabric is demonstrated** |
| Agent Plane | Agent roles, canonical Skills, bounded task coordination, handoffs, and tool invocation boundaries. | Role contracts; reusable procedures; bounded execution; delegation; stop and escalation behavior. | Task scope; canonical Skills; role contracts; permissions; context; tool declarations | Bounded work plans; reviewable changes; handoffs; execution evidence; tool requests within authorization | Owns agent and Skill responsibility contracts. Does not own architecture authority, model credentials, persistent knowledge policy, or external tool operational readiness. | Intelligence for model-mediated reasoning; Knowledge for scoped context; Domain for domain-specific requirements; Control for permission and approval | Least privilege, explicit tool allowlists, no implicit permissions, prompt-injection resistance, and human approval for sensitive operations | **Partially represented by existing source artifacts; operational agent roles UNRESOLVED** |
| Domain Plane | Engineering and project-domain capabilities, module contracts, and the relationship between the engineering platform and planned SUPER AGI domains. | Domain-specific Skills; module contracts; domain boundaries; reusable domain capabilities; cross-module compatibility rules. | Canonical architecture; domain specifications; module contracts; registry metadata | Domain plans; contract declarations; module compatibility results; engineering deliverables | Owns domain behavior definitions and module boundaries. Does not own platform-wide governance, provider credentials, shared memory policy, or SUPER AGI runtime implementation. | All execution and knowledge planes as needed; Intelligence for reasoning; Knowledge for domain context; Agent for execution; Control for authority | Domain access control, data boundaries, module isolation, change traceability, and review of cross-domain coupling | **PROPOSED/UNRESOLVED; current claude-skills engineering domains are not complete SUPER AGI modules** |
| Control Plane | Governance, authorization, security policy, architecture decisions, capability status, auditability, and execution constraints. | Architecture authority; permissions; approval gates; evidence status; policy conflict handling; bounded stop behavior. | Architecture documents; implementation and validation evidence; task scope; permissions; external conflicts | Decisions; approval dependencies; status reports; stop/escalation records; audit evidence; governance requirements | Owns repository authority and control policy. Does not own business-domain intelligence, provider execution, tool implementation, or factual knowledge evidence. | Cross-cutting dependency on every plane; must not be bypassed by any plane | Human authorization, least privilege, separation of approval/evaluation/release, redaction, traceability, and conflict handling | **Governance policy exists; a fully operational centralized control system is NOT demonstrated** |

## C. Intelligence Plane

The Intelligence Plane owns provider-neutral reasoning and intelligence contracts. It is the intended responsibility boundary for model selection concepts, prompt/result normalization, capability negotiation, reasoning orchestration, provider routing policy, and shared intelligence services.

Canonical definitions should describe expected behavior without embedding provider-specific APIs, provider syntax, proprietary instruction formats, or vendor assumptions. Provider adapters belong in provider-specific boundaries and may translate canonical contracts only when explicitly authorized. Adapter outputs must disclose unsupported behavior and compatibility limitations.

The plane may receive:

- task and user intent;
- canonical engineering requirements;
- authorized context and knowledge; and
- provider capability metadata.

It may produce:

- provider-neutral requests;
- normalized results;
- capability and unsupported-operation reports;
- bounded reasoning plans or summaries.

It does not own:

- source architecture authority;
- credentials or account access;
- tool execution;
- persistent memory;
- human approval;
- final capability status; or
- proof that provider behavior or general intelligence has been achieved.

The repository does not demonstrate a working universal reasoning engine. Existing source behavior may support narrower provider-neutral workflows, but that capability must not be expanded into claims of general intelligence or runtime provider autonomy.

## D. Knowledge Plane

The Knowledge Plane owns information resources and context responsibilities, including knowledge boundaries, memory concepts, retrieval, provenance, retention, deletion, access, and source quality. Its intended output is scoped, traceable information that other planes can use.

Repository evidence supports the concept through architecture proposals for context, memory, knowledge, world-model, and universal-context work. ARC-09 identifies context and knowledge as planned rather than implemented. No persistent universal memory or complete knowledge fabric has been demonstrated.

The plane does not own:

- model reasoning;
- agent permission;
- tool authorization;
- provider routing;
- domain execution authority;
- architecture approval; or
- factual correctness merely because a source was retrieved.

Planned knowledge responsibilities include:

- source, scope, access, and retention metadata;
- content classification and redaction policy;
- retrieval provenance;
- deletion and correction behavior;
- explicit separation between observed evidence, inference, and generated summaries.

These responsibilities describe architecture intent. They are not evidence of persistent storage, retrieval quality, memory enforcement, or universal context infrastructure.

## E. Agent Plane

The Agent Plane owns specialized agent-role responsibility, reusable Skills, bounded task coordination, delegation limits, handoffs, and tool invocation boundaries.

An agent role should define:

- purpose and scope;
- inputs and outputs;
- permitted providers and tools;
- explicit stop conditions;
- escalation and human approval requirements;
- handoff behavior and evidence retention.

Canonical Skills belong in a provider-neutral contract boundary within this plane. Existing repository artifacts include an implementation Skill and supporting workflow documentation. No complete set of agent roles or provider-specific agent definitions is established.

Tool invocation must remain separate from Skill declarations. A manifest, registry entry, capabilities list, or documentation link is descriptive metadata, not permission or proof of execution. Existing tool-framework and discovery source artifacts do not prove tool installation, authentication, adapter readiness, or operational execution.

The Agent Plane may coordinate bounded work but does not grant itself authority. It must consume permissions and stop rules from the Control Plane and use scoped context from the Knowledge Plane.

## F. Domain Plane

The Domain Plane owns specialized engineering and project-domain responsibilities and reusable domain capabilities. It includes repository domains and proposed SUPER AGI module-domain boundaries.

For `claude-skills`, the Domain Plane may include future engineering domains that are represented through canonical contracts, Skills, workflows, templates, registries, or validation capabilities. Each domain must state scope, interfaces, dependencies, security requirements, and evidence.

For SUPER AGI, domain boundaries represent specialized intelligence domains within one unified system:

> One Super AGI — One Unified Brain — 100 Major AGI Intelligence Modules — 100 Dedicated Navbars/Workspaces — Shared Universal Infrastructure.

The 100 modules are intended specialized domains, not 100 independent AI products. A module registry, module contract, domain implementation, or engineering document does not prove that the corresponding SUPER AGI runtime module exists.

The Domain Plane does not own:

- provider-neutral architecture authority;
- global security or approval policy;
- shared memory implementation;
- cross-domain infrastructure policy;
- provider credentials;
- the unified SUPER AGI runtime; or
- deployment and release authority.

Existing repository architecture documents are engineering proposals unless independently approved. No 100-module runtime or complete domain registry is demonstrated.

## G. Control Plane

The Control Plane owns repository governance, authorization, architecture authority, security policy, capability status, traceability, and execution constraints.

Its intended responsibilities include:

- distinguishing evidence, specification, implementation, evaluation, and approval;
- enforcing scope boundaries through policy and human review;
- retaining capability status without allowing documentation to imply functionality;
- managing change conflicts and unresolved decisions;
- requiring human authorization for consequential actions;
- recording stop and escalation conditions; and
- separating implementation, verification, release, and publication decisions.

The Control Plane should consume evidence from implementation, evaluation, provider compatibility, tool readiness, and security review processes. It must not infer readiness merely from source presence, successful compilation, registry registration, or passing source tests.

The repository has governance documents, architecture classifiers, bounded implementation workflow guidance, and evidence conventions. It does not demonstrate a fully operational centralized controller, policy engine, durable audit service, or approval workflow. Policy-document existence is not technical enforcement evidence.

## H. Plane Interactions

The intended cooperation model is:

- **Control Plane → all planes:** defines authority, permission boundaries, stop conditions, evidence requirements, and unresolved-conflict handling.
- **Knowledge Plane → Intelligence and Agent planes:** supplies authorized context and provenance while preserving access and retention rules.
- **Intelligence Plane → Agent and Domain planes:** supplies provider-neutral reasoning capability boundaries and normalized provider results.
- **Agent Plane → Domain and Knowledge planes:** executes bounded domain work using scoped procedures and authorized context.
- **Domain Plane → Intelligence, Knowledge, and Agent planes:** defines domain-specific requirements and consumes capabilities without becoming a competing architecture authority.
- **Control Plane receives evidence from all planes:** verification, limitations, failures, security review, compatibility, and operational readiness remain distinguishable.

No exact message protocol, service dependency, synchronous sequence, bus, workflow engine, or persistence mechanism is established. Communication between planes should use explicit approved contracts rather than implicit shared mutable state.

Potential dependency constraints are:

- Canonical Intelligence definitions should consume Knowledge only through scoped, authorized interfaces.
- Provider-specific execution should not redefine Intelligence contracts or bypass Control policy.
- Agent actions should be governed by role scope, explicit tool permissions, and task authorization.
- Domain modules should not self-approve architecture or cross-domain authority.
- Generated or external content should be treated as untrusted input unless separately established as an authorized source.
- Evidence flows to Control for status and approval decisions; evidence does not automatically create approval.

These dependencies are proposed responsibility relationships, not proven runtime connections.

## I. Relationship to L0–L15

The five planes are cross-cutting responsibility views, while [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md) is a proposed vertical responsibility organization. Exact one-to-one or fixed-range mappings are not approved.

A future approved mapping should preserve the following general relationships:

| Plane | Proposed L0–L15 relationship | Relationship status |
|---|---|---|
| Intelligence Plane | Likely spans provider-neutral contracts at proposed L4/L7, reasoning coordination at L8, and evidence use at L12, subject to future approval. | PROPOSED and unresolved |
| Knowledge Plane | Likely spans context and knowledge responsibilities at proposed L4/L6, with storage/security/capability dependencies across lower and higher layers. | PROPOSED and unresolved |
| Agent Plane | Likely spans canonical Skills and agent-role contracts at proposed L4/L5, orchestration at L8, tool boundaries at L9/L10, and verification at L12. | Evidence-grounded proposal; exact mapping unresolved |
| Domain Plane | Likely participates at proposed domain coordination and module-contract layers, with infrastructure and shared concepts around L14 and below as approved. | PROPOSED and unresolved |
| Control Plane | Cross-cuts architecture, security, repository, tool, evidence, evolution, and Master Control responsibilities from L2–L15 rather than occupying one layer alone. | Evidence-grounded cross-cutting responsibility; exact mapping unresolved |

L0 is a physical/compute foundation and L15 is the Master Control boundary. Neither endpoint establishes a one-to-one plane assignment. L15 Master Control must not be represented as a plane-wide bypass; it remains part of the Control Plane only through approved authority and implementation.

## J. Relationship to Shared Infrastructure

### Master Core

The Master Core is a planned coordination concept for the unified one-Super-AGI design. It does not establish implementation or placement within the five planes. The future `architecture/MASTER-CORE.md` must define whether and how Master Core responsibilities span the Intelligence, Knowledge, Agent, Domain, or Control planes.

### Universal Intelligence Fabric

The Universal Intelligence Fabric is a planned shared infrastructure concept. It may require cross-plane contracts involving intelligence, knowledge, context, tool, and governance services, but this must be approved before any runtime topology is implied. The repository does not demonstrate a fabric implementation.

### Memory and Knowledge Resources

Persistent memory, retrieval, provenance, and deletion belong primarily to the Knowledge Plane. These capabilities may support other planes only through explicit access and retention policy. No complete memory or knowledge fabric is demonstrated.

### World Model

A World Model is a planned knowledge/evidence concept rather than an implemented intelligence capability. Its placement must remain unresolved until source, evidence, uncertainty, update, and security contracts are approved.

### Universal Context

Universal Context is planned infrastructure and must not be confused with ordinary repository context or session context. It belongs primarily to the Knowledge Plane with explicit cross-plane authorization but has no approved implementation.

### Agents, Skills, and Tools

Agents and Skills are primarily Agent Plane responsibilities. Tool declarations and execution boundaries may bridge the Agent and Intelligence planes to external resources, while the Control Plane constrains authorization. No broad platform integration exists by default.

### Cross-AGI Collaboration

Cross-AGI collaboration is unresolved. It is not evidence of a federation protocol, shared runtime, collaborative memory, or multi-agent implementation.

### Model Gateway

The Model Gateway is a planned provider/model boundary and belongs primarily to the Intelligence Plane, with provider-specific translation kept separate from canonical definitions. It may interact with Agent and Knowledge responsibilities but requires explicit contracts and compatibility evidence.

### Security and Governance

Security and governance are primarily Control Plane responsibilities but cross-cut every plane. They do not create an implicit runtime enforcement guarantee merely because policy appears in documentation.

### Capability-Status Reporting

Capability status is primarily a Control Plane concern, using verification evidence and declared implementation state from other planes. Status must not be inferred from documentation, source presence, interface declaration, compilation, or a registry alone.

## K. Security and Trust Boundaries

Each plane must respect repository-wide security and trust rules:

- **Intelligence:** isolate provider-specific behavior and disclose unsupported capabilities, secrets exposure, model data handling, and generated output uncertainty.
- **Knowledge:** enforce source authorization, data classification, retention, redaction, deletion, and provenance.
- **Agent:** bind every role and invocation to bounded scope, explicit tool permissions, stop conditions, and human approval where required.
- **Domain:** isolate domain data and contracts, prevent cross-domain authority expansion, and record compatibility and approval.
- **Control:** separate decisions from implementation and evaluation evidence; require explicit human authorization for destructive, irreversible, sensitive, externally visible, production, account, credential, network, deployment, or publication actions.

External and generated content is untrusted data. It must not silently expand permissions, expose secrets, change repository state, override repository instructions, or bypass human approval. Tool and provider manifests are declarations, not permission grants.

Auditability requires traceable ownership, inputs, outputs, authorization state, and evidence. Plane separation alone does not guarantee security. Technical controls, path containment, subprocess safety, provider isolation, access control, prompt-injection resistance, and audit storage require separate implementation and verification.

## L. Implementation Mapping

Future implementation work should associate components with planes by their primary responsibility and not by directory name alone.

Actual repository evidence currently provides these associations:

- Architecture governance documents, including this file and `SOURCE_OF_TRUTH.md`, map primarily to the Control Plane.
- Canonical implementation Skill and workflow documentation map primarily to the Agent Plane, with bounded workflow and verification interactions from the Control Plane.
- Skill registry and manifest source artifacts map primarily to the Agent Plane and may support controlled capability metadata used by Intelligence, Knowledge, or Domain planes where approved.
- Tool framework and discovery source artifacts map primarily across Agent and external execution boundaries; they do not prove integration readiness.
- Tests and validation scripts map primarily to Control/evidence support and Verification responsibilities associated with the Agent and Domain implementation lifecycle.
- Repository context and specification documents map primarily to Knowledge and Control responsibilities depending on whether they are data sources or governing decisions.

Component mappings use four evidence classes:

1. **Planned component** — named by proposal only.
2. **Existing source artifact** — code, documentation, schema, or manifest is present but not necessarily approved or operationally verified.
3. **Implemented capability** — behavior is demonstrated through reproducible execution evidence.
4. **Operationally verified capability** — installation, authentication, authorization, execution, failure behavior, compatibility, and environment readiness are observed.

No repository file should be assigned to all five planes. Cross-cutting dependencies should be declared explicitly rather than inferred from broad directory ownership.

## M. Unresolved Decisions

The following decisions require separate approval or evidence:

- exact responsibilities and interfaces for each plane;
- canonical cross-plane dependency and interaction protocols;
- exact mapping between each plane and the L0–L15 layer proposal;
- the authority and implementation model for centralized Control Plane services;
- persistent Knowledge Plane storage, provenance, retention, deletion, and access model;
- World Model scope and evidence requirements;
- Universal Context implementation and isolation model;
- Intelligence Plane model-selection and gateway contracts;
- Agent role format, lifecycle, handoffs, and invocation evidence;
- canonical Skill approval and provider compatibility beyond existing source artifacts;
- Domain and SUPER AGI module contracts and registry format;
- Master Core and Universal Intelligence Fabric contracts;
- Cross-AGI collaboration protocol and trust model;
- tool and provider selection, authentication, and operational readiness;
- independent verification, capability-status publication, and release authority;
- exact security-enforcement mechanisms and audit evidence; and
- integration-base and approving-authority decisions that remain unresolved elsewhere.

The narrowly scoped repository-audit specification approval pin does not authorize implementation, execution-host qualification, integration, evaluation, publication, or release. It should not be used to resolve missing plane responsibilities.

## N. Relationship to Other Canonical Documents

Existing canonical and supporting documents:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md)
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md)
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md)
- [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md)

Existing supporting proposals and evidence:

- [`docs/architecture/arc-dependency-map.md`](../docs/architecture/arc-dependency-map.md)
- [`docs/architecture/team-file-ownership.md`](../docs/architecture/team-file-ownership.md)
- [`docs/architecture/m1-contract-decisions.md`](../docs/architecture/m1-contract-decisions.md)
- [`docs/architecture/decisions/m1-spec-approval-pin.md`](../docs/architecture/decisions/m1-spec-approval-pin.md)
- [`docs/audits/architecture-audit.md`](../docs/audits/architecture-audit.md)
- [`workflows/spec-to-implementation/README.md`](../workflows/spec-to-implementation/README.md)

Planned canonical targets, which do not exist and must not be presented as authoritative documentation or implementation evidence:

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

This document defines responsibility boundaries only. Approval, implementation, verification, evaluation, integration, publication, and release remain separate states requiring their own evidence.

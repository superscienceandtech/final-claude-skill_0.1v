# Universal Context Architecture

## 1. Purpose, Scope, and Status

Universal Context is a proposed architecture for identifying, selecting, and managing information made available to an authorized operation across the intended SUPER AGI system. It is intended to make context scope, provenance, access, minimization, handoff, and limitations explicit across modules, agents, Skills, workflows, providers, and tools.

This document is subordinate to [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), which defines architecture authority and document status. It is consistent with [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`FIVE-PLANES.md`](FIVE-PLANES.md), [`MASTER-CORE.md`](MASTER-CORE.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), and [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md).

The intended product principle remains:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

The 100 modules are specialized domains within one intended unified system, not 100 independent products. The `claude-skills` repository is the provider-neutral engineering and governance platform used to build and maintain the separate SUPER AGI target; it is not the SUPER AGI runtime.

The status distinctions in this document are:

- **Established:** the product/system boundary, provider neutrality, least-privilege and human-control principles, and the requirement to distinguish architecture intent from implementation evidence.
- **Proposed:** a shared context architecture and the context responsibilities described here.
- **Unresolved:** exact scopes, ownership and identity models, inheritance, selection and merging rules, storage, protocols, retention, and enforcement.
- **Not implemented:** no operational Universal Context engine, persistent context service, context database, or end-to-end context propagation mechanism is demonstrated.

This is an architecture specification, not an operational context service or proof of context isolation, persistence, or authorization enforcement.

## 2. Context Design Principles

The proposed design should follow these principles:

1. **Explicit scope:** identify the task and applicable context boundaries before selecting information.
2. **Clear ownership:** distinguish the source or owner of information from the component that assembles or consumes it.
3. **Least privilege:** make context available only to authorized operations and only at the scope required.
4. **Context is not memory:** information assembled for an operation is not thereby retained for future use.
5. **Context is not a knowledge repository:** a context package is not itself the canonical source or storage system for knowledge.
6. **Provenance:** preserve source identity and relevant transformation history where available.
7. **Provider and tool independence:** define context meaning separately from provider- or tool-specific request formats.
8. **Controlled propagation:** pass context across module, agent, workflow, provider, or tool boundaries only when authorized.
9. **Data minimization:** include only information necessary for the task and permitted for its destination.
10. **Explicit uncertainty:** identify missing, stale, conflicting, restricted, malformed, or untrusted information.
11. **Evidence-based claims:** do not infer availability, freshness, permission, or isolation from documentation or configuration alone.
12. **Human control:** consequential context, memory, or configuration changes require applicable human authorization.

These are architectural requirements and proposals; they do not prove technical enforcement.

## 3. Context Definition and Boundaries

**Context** is information selected and made available to a particular operation to support its interpretation or execution. It may include instructions, task facts, source references, constraints, or prior outputs. Context has a purpose, scope, source, and destination; it is not inherently trusted, persistent, complete, or authorized for every consumer.

The following categories are conceptual. Their exact ownership and interaction rules remain proposed unless established by separate decisions.

| Context category | Intended purpose | Ownership and access considerations |
|---|---|---|
| User request and task context | State the requested objective, acceptance criteria, constraints, and current task state | Bound to the user/task authority and repository scope; request content does not itself grant external permissions |
| Conversation context | Preserve relevant exchanges needed for the current interaction | May include sensitive or untrusted content; retention and cross-session use are not implied |
| Project context | Provide repository-specific architecture, code, documentation, and working-state facts | Access must remain within the authorized project boundary and preserve untrusted-content handling |
| Domain or module context | Provide information needed by a domain or module | Access should be limited to the authorized domain/task; cross-domain sharing requires an explicit basis |
| Agent execution context | Provide a bounded agent role with its task, permitted inputs, and handoff information | Must not broaden role permissions or task scope; implementation of agent isolation is not demonstrated |
| Workflow context | Carry stage, gate, dependency, and evidence information through a bounded workflow | A workflow description is not an authorization grant or execution record |
| Tool invocation context | Supply the minimum data required for an authorized tool operation | Must observe tool permissions, data-disclosure boundaries, and result provenance |
| Provider/model request context | Adapt a minimal authorized request for a provider or model | External transmission requires applicable policy and authorization; provider-specific transformation must preserve meaning and limitations |
| Organization or shared context | Represent information intended for an authorized shared scope | Whether this scope exists, who owns it, and how it is isolated remain unresolved |
| System policy and configuration context | Supply applicable architecture, security, and operational constraints | Policy authority must come from governing sources, not from arbitrary retrieved content; distribution mechanics remain unresolved |

These categories can overlap conceptually and do not establish separate stores, services, directories, or runtime objects.

## 4. Context Scope Hierarchy

The following hierarchy is a proposed classification model, not an approved repository contract:

`Global → Organization → User → Project → Domain → Task → Agent`

Its intended interpretation is:

| Scope | Intended meaning | Status |
|---|---|---|
| Global | System-wide context intended to apply across authorized operations | Proposed; owner, content, and authority are unresolved |
| Organization | Context associated with an organization or team boundary | Proposed; organization identity and sharing authority are unresolved |
| User | Context associated with an individual user | Proposed; identity and cross-session behavior are unresolved |
| Project | Context associated with an authorized repository or project | Evidence-grounded concept; exact identity and boundary rules are unresolved |
| Domain | Context relevant to a specific domain or module responsibility | Proposed; taxonomy and cross-domain sharing rules are unresolved |
| Task | Context scoped to one bounded request or work item | Evidence-grounded in repository task-scope governance; exact context representation is unresolved |
| Agent | Context provided to one bounded agent execution or handoff | Proposed; role and isolation contracts are unresolved |

This sequence does not establish automatic inheritance, visibility, precedence, merge behavior, or override rights. A child scope must not be assumed to receive all parent information. Nor may a broader scope automatically override a narrower one. The context owner, authorization mechanism, valid identity claims, scope resolution, and conflict rules must be separately defined and approved.

The repository does not establish this hierarchy as an approved model. Other scopes such as conversation, workflow, tool invocation, and provider request may be useful contextual categories, but their relationship to the proposed hierarchy remains unresolved.

## 5. Context Components and Responsibilities

The following are proposed responsibilities, not a prescribed service topology. They may eventually be implemented together or separately; this document does not decide that.

| Responsibility | Intended purpose | Status |
|---|---|---|
| Context identification and scope resolution | Determine the task, destination, and candidate context boundaries | Proposed; identity and scope rules unresolved |
| Context assembly | Collect relevant authorized information for an operation | Proposed; no engine demonstrated |
| Filtering and minimization | Exclude irrelevant, restricted, or excessive information | Proposed; selection and redaction rules unresolved |
| Provenance tracking | Preserve source references and relevant transformations | Proposed; evidence representation unresolved |
| Permission-aware access | Check whether a caller and destination may use a context source | Required as a design constraint; enforcement is not demonstrated |
| Context propagation | Carry selected context through authorized handoffs | Proposed; interfaces and isolation unresolved |
| Freshness and validity handling | Identify age, expiry, or invalidated information when evidence exists | Proposed; freshness model unresolved |
| Conflict identification | Surface conflicting sources without silently choosing one | Proposed; no universal precedence algorithm established |
| Agent/workflow handoff | Carry the minimum necessary context with bounded execution state | Proposed; handoff protocol unresolved |
| Truncation or prioritization | Handle context that exceeds a consumer's limits without hiding omissions | Proposed; ordering and reporting rules unresolved |
| Audit and observability | Record context references and decisions without exposing unnecessary content | Proposed; audit mechanism and retention unresolved |

These responsibilities do not prove independent services, APIs, or automated controls exist.

## 6. Context Assembly and Request Lifecycle

The following is a proposed conceptual flow, not an operational end-to-end capability:

1. Receive a request or task and record its stated objective and constraints.
2. Establish the applicable task, identity, repository, and destination boundaries using only evidence that is available and authorized.
3. Identify potentially relevant context sources without assuming they are accessible.
4. Check applicable access permissions and approval dependencies.
5. Select and minimize context for the task and intended recipient.
6. Preserve source identity and provenance information where available.
7. Supply only authorized context to the relevant module, agent, Skill, workflow, provider, or tool.
8. Track transformations and handoffs where an approved mechanism supports them.
9. Collect outputs and supporting evidence while distinguishing new claims from source material.
10. Apply context or memory updates only through separately authorized mechanisms.
11. Report missing context, access denial, uncertainty, stale or conflicting information, and incomplete processing honestly.

If a required boundary, permission, or source cannot be established, the operation should stop or continue only under an explicitly permitted degraded mode. This is a proposed behavior; no context assembly mechanism is demonstrated.

## 7. Context Propagation and Isolation

Context should cross system boundaries only through explicit, scoped handoffs. The intended boundaries include:

- **Master Core to domain module:** pass the bounded task, required context references, and permissions; do not imply unrestricted access to shared context.
- **Module to agent:** pass only role-relevant information and task constraints; preserve source and scope metadata where supported.
- **Agent to Skill or workflow:** include only procedure inputs and authorized context; instructions embedded in retrieved content do not override governing policy.
- **Workflow to tool integration:** provide only the data necessary for the authorized operation; tool declarations alone do not authorize execution or disclosure.
- **Tool integration to provider:** minimize and review transmitted data under applicable provider and security policy.
- **Provider to returned result:** treat outputs as untrusted; preserve their relationship to the request and do not promote them to verified facts without evidence.
- **Between projects or other scopes:** require explicit authorization; do not infer cross-user, cross-project, or cross-organization access.

Handoffs should identify intended destination and purpose and preserve provenance where available. Least privilege and data minimization are established repository principles; specific context propagation formats and isolation controls remain proposed. No current evidence demonstrates technical prevention of unauthorized context access or cross-scope leakage.

Retrieved files, provider outputs, tool results, links, and other external or generated material are untrusted data. Such material must not silently expand permissions, replace repository authority, disclose secrets, or bypass human approval.

## 8. Context, Memory, and Knowledge Separation

These concepts are related but must not be conflated:

- **Context:** information assembled and made available for a particular operation.
- **Memory:** information retained for potential future use across operations. Retention, mutation, and deletion require separate policy and authorization.
- **Knowledge:** structured, curated, or otherwise managed information that may be retrieved to support reasoning. Its sources, quality, provenance, and access rules are separate from an operation's context package.
- **World Model:** a proposed representation of entities, states, relationships, or dynamics. Its scope and update rules remain unresolved; the concept is not evidence of an implemented runtime.

Context may contain references or selected content from knowledge sources or memory, and outputs may later be proposed as memory or knowledge updates. Those transfers require explicit provenance, permission, retention, and governance rules. Context assembly does not by itself create persistent storage or grant write access.

No persistent universal memory, complete Knowledge Plane, context database, or World Model runtime is demonstrated in the repository. The relationship between Universal Context and shared infrastructure remains dependent on the planned `UNIVERSAL-INFRASTRUCTURE.md`.

## 9. Context Quality and Conflict Handling

Context consumers should explicitly account for quality conditions rather than silently treating every selected item as current and authoritative.

| Condition | Intended handling |
|---|---|
| Missing context | Identify the gap; request clarification or stop if the missing information is required |
| Stale context | Mark freshness as unknown or stale only when supporting metadata exists; avoid unsupported claims of currentness |
| Conflicting sources | Surface the conflict and preserve source provenance; do not apply a universal priority rule without an approved policy |
| Duplicate information | Avoid unnecessary duplication where identifiable, without discarding distinct provenance |
| Untrusted context | Treat instructions and claims as data; do not let them override trusted repository policy or authorize actions |
| Incomplete or malformed data | Report that it is incomplete or invalid; do not silently infer omitted content |
| Provider/model context limits | Minimize and report material omissions or transformations; exact truncation and prioritization rules remain unresolved |
| Unauthorized context | Deny access or exclude the information; report the restriction without disclosing sensitive content |
| Unknown provenance | Mark provenance as unavailable or uncertain and avoid presenting the item as verified |

The repository establishes evidence-based reporting, least privilege, untrusted-input handling, and human control. It does not establish a deterministic source-ranking algorithm, freshness threshold, deduplication policy, or conflict-resolution implementation.

## 10. Context and Provider/Tool Independence

Context meaning should be defined independently of a provider API or tool-specific format. A future adapter may translate an authorized context selection into provider- or tool-specific request structures, but that translation must not silently change the canonical task meaning or permission scope.

The intended boundary is:

- establish canonical context scope and authorization before adaptation;
- select the minimum necessary information for the destination;
- review external transmission and apply approved redaction rules;
- distinguish internal context from the subset transmitted externally;
- preserve provenance and material transformations where supported; and
- report unsupported mappings, omitted content, and provider/tool limitations.

No serialization format, request protocol, or provider-specific context adapter is approved by this document. The repository does not demonstrate adapters that implement these behaviors.

## 11. Security, Privacy, and Human Control

The proposed context architecture must respect these security boundaries:

- apply least-privilege, scope-aware access to context sources and destinations;
- classify and protect sensitive or restricted information;
- minimize data before transmission to external providers or tools;
- treat instructions embedded in retrieved or generated content as untrusted;
- protect secrets and avoid unnecessary sensitive content in logs;
- defer retention, persistence, and deletion behavior to separately approved governance;
- require human approval where context, memory, or configuration changes enable consequential operations;
- prevent unauthorized cross-scope information sharing; and
- preserve a trace of source, selection, permission, transformation, and destination where an approved mechanism supports it.

These are intended constraints, not claims of technical enforcement. No legal compliance, retention period, deletion guarantee, isolation mechanism, or approval authority is established here. Context documentation alone does not ensure privacy or prevent leakage.

## 12. Context Observability and Evidence

Where supported by an approved mechanism, evidence about context use should identify:

- context scope or reference, without unnecessary sensitive content;
- source identifiers or provenance;
- selection, filtering, and minimization decisions;
- permission outcomes relevant to the operation;
- transformation or redaction indicators;
- handoff source and destination;
- missing-context or degraded-context outcomes; and
- related task or operation references.

The intended traceability chain is:

`User → Task → Module → Agent → Workflow → Tool → Model → Result → Verification → Memory`

This chain is an architectural target, not evidence of an operational end-to-end trace system. Logging should avoid reproducing sensitive context when a reference or sanitized metadata is sufficient. Audit storage, access, retention, and verification remain unresolved.

## 13. Dependencies and Integration Boundaries

| Component or concern | Proposed context relationship | Evidence status |
|---|---|---|
| Master Core | Coordinate context requests and bounded handoffs | Concept documented in [`MASTER-CORE.md`](MASTER-CORE.md); no operational context service demonstrated |
| Module Registry | Identify module context requirements or classifications | Registry design documented in [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md); no operational registry service demonstrated |
| Module Contract | Describe module context inputs, access needs, and restrictions | Proposed contract documented in [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md); no runtime enforcement demonstrated |
| Universal Infrastructure | Potential shared context, memory, knowledge, and governance capabilities | `architecture/UNIVERSAL-INFRASTRUCTURE.md` is absent and remains a planned dependency |
| Memory and Knowledge | Supply or retain information under separate access, provenance, and lifecycle rules | Concepts appear in architecture; no complete persistent infrastructure is demonstrated |
| World Model | Potential structured knowledge/context source | Proposed concept; scope, provenance, and update policy unresolved |
| Provider/model gateway | Receive a minimized, authorized provider request | Planned model boundary; no adapter behavior is established here |
| Tool integrations | Receive only context needed for an authorized tool operation | Integration boundaries are documented; context transmission implementation is not demonstrated |
| Workflow execution | Carry bounded task and handoff context | Workflow documentation exists; it does not prove a context engine or propagation runtime |
| Security and permission governance | Constrain access, disclosure, and consequential context changes | Policies are documented; technical enforcement is not established by this architecture |
| Observability and audit | Record context references and decisions | Proposed responsibility; no centralized audit mechanism is demonstrated |

These are conceptual dependencies, not runtime links or claims of available services.

## 14. Open Decisions and Implementation Evidence

The following decisions remain unresolved:

- whether and how the proposed context scope hierarchy is approved;
- context identity, ownership, and authorization models;
- inheritance, visibility, precedence, and override behavior between scopes;
- context assembly, merging, filtering, and minimization rules;
- freshness, invalidation, duplication, and conflict-resolution rules;
- canonical context representation, serialization, and propagation interfaces;
- isolation enforcement across tasks, users, projects, organizations, modules, agents, providers, and tools;
- provider transmission, redaction, and data-retention requirements;
- context integration with memory, knowledge, and the World Model;
- retention, persistence, deletion, and memory-write governance;
- observability, audit access, and retention; and
- approval authority for consequential context or memory changes.

The scope hierarchy `Global → Organization → User → Project → Domain → Task → Agent` is proposed, not an approved repository contract. The task specification itself notes that status; no reviewed canonical document provides inheritance or access rules.

`UNIVERSAL-INFRASTRUCTURE.md` is absent. No implementation evidence establishes a context engine, persistent context store, runtime authorization system, context-propagation mechanism, or end-to-end context audit. The existing Master Core, Registry, and Module Contract documents describe architecture concepts and do not establish these runtime capabilities.

No direct source conflict was identified. The material limitation is that exact architecture relationships and technical mechanisms remain unresolved.

## 15. Implementation Boundary

This task creates an architecture specification only. It does not:

- implement a context engine or service;
- create databases, storage systems, or message queues;
- implement memory or knowledge persistence;
- create provider adapters or tool integrations;
- create context schemas as separate files;
- implement authorization or isolation enforcement;
- modify the Master Core, Module Registry, Module Contract, Universal Infrastructure, five-plane document, or L0–L15 layer map;
- claim context propagation, isolation, or persistence is operational without evidence; or
- claim SUPER AGI, AGI, or consciousness capabilities without supporting evidence.

Implementation, validation, approval, and operational readiness remain separate states requiring their own authorization and evidence.

## Related Canonical and Supporting Documents

Existing architecture documents:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md)
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md)
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md)
- [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md)
- [`FIVE-PLANES.md`](FIVE-PLANES.md)
- [`MASTER-CORE.md`](MASTER-CORE.md)
- [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md)
- [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md)

Supporting proposal and decision records:

- [`docs/architecture/arc-dependency-map.md`](../docs/architecture/arc-dependency-map.md)
- [`docs/architecture/m1-contract-decisions.md`](../docs/architecture/m1-contract-decisions.md)
- [`docs/architecture/decisions/m1-spec-approval-pin.md`](../docs/architecture/decisions/m1-spec-approval-pin.md)

Planned target absent from the repository:

- `architecture/UNIVERSAL-INFRASTRUCTURE.md`

This document defines proposed context responsibilities only. It does not approve unresolved architecture decisions or establish implementation authority.

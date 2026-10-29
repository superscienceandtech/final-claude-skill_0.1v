# Cross-AGI Collaboration Architecture

## 1. Document Identity and Architectural Status

This document describes proposed collaboration among specialized intelligence modules within the intended unified SUPER AGI target system. It defines conceptual participants, patterns, handoffs, trust boundaries, failure behavior, and evidence expectations for planning and future implementation.

The document is subordinate to [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), which defines architecture authority and document status. It is intended to remain consistent with [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`FIVE-PLANES.md`](FIVE-PLANES.md), [`MASTER-CORE.md`](MASTER-CORE.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), and [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md).

The established product principle is:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

The modules are specialized domains within one intended system, not 100 independent AI products. The `claude-skills` repository is the provider-neutral engineering and governance platform used to develop that separate target; it is not the SUPER AGI runtime.

Status distinctions:

- **Established:** the unified-system principle, five plane names, provider neutrality, least-privilege expectations, human control for consequential actions, and evidence-based capability claims.
- **Proposed:** collaboration patterns, module handoffs, routing responsibilities, and collaboration lifecycle described here.
- **Unresolved:** collaboration interfaces, routing and arbitration policies, security enforcement, context-sharing rules, execution semantics, and approval authority unless established by a separate approved decision.
- **Not implemented or unknown:** no operational cross-module collaboration runtime, universal router, or end-to-end collaboration trace is demonstrated by this document or the reviewed architecture sources.

This document defines an architectural proposal. It does not formally approve all collaboration mechanisms or prove that modules currently communicate or execute together.

## 2. Collaboration Purpose and Principles

Specialized modules may need to contribute to tasks whose requirements span domain boundaries. Collaboration is intended to make such contributions explicit and coordinated while retaining a single unified system and clear ownership. Not every request requires more than one module; use a single module when its declared responsibilities and evidence are sufficient.

Proposed principles:

1. **One unified target system:** collaboration connects specialized modules; it does not turn them into independent AI products.
2. **Specialized responsibilities:** each module remains accountable for its declared domain and does not silently absorb another module's role.
3. **Shared infrastructure reuse:** modules use common context, knowledge, security, provider, tool, and evidence capabilities through approved boundaries rather than creating duplicate systems.
4. **Explicit task and capability boundaries:** scope, expected contributions, capability limits, and dependencies are stated before delegated work.
5. **Controlled information exchange:** only necessary, authorized context is shared, with provenance preserved where possible.
6. **Provider and model independence:** collaboration contracts do not depend on one provider, model, or vendor-specific format.
7. **Permission-aware execution:** module selection or membership does not grant data, tool, provider, or cross-domain permissions.
8. **Traceability and evidence:** record contributing modules, handoffs, results, limitations, and verification evidence when an approved mechanism supports it.
9. **Human control:** generated plans or consensus do not authorize consequential actions; required human approval remains external to module outputs.
10. **Graceful handling of unavailable capabilities:** report missing or unsuitable modules honestly; fallback is allowed only when within scope and supported by an approved contract.

These are architectural principles and proposed design requirements. They do not prove a collaboration mechanism is implemented or enforced.

## 3. Collaboration Participants

Participants describe responsibility boundaries, not necessarily separate services, processes, agents, or deployment units.

| Participant | Conceptual role | Status and boundary |
|---|---|---|
| User or authorized initiating actor | States the task, scope, constraints, and any explicit direction or approval | Human authority remains external; an initiating request is not blanket authorization for consequential actions |
| Master Core | May coordinate task interpretation, module selection, handoffs, result aggregation, and evidence-aware reporting | Proposed in [`MASTER-CORE.md`](MASTER-CORE.md); no operational dispatcher is demonstrated |
| Universal Intelligence Router | May identify relevant provider-neutral reasoning or module capabilities | Proposed infrastructure concept in [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md); no router implementation or approved matching algorithm is demonstrated |
| Originating module | Holds the originating task responsibility and may request a bounded contribution from another module | Module identity and contract are proposed by [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) and [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md); runtime participation is not established |
| Collaborating module | Supplies a defined contribution within its declared responsibility, scope, capability, and permissions | Does not acquire the originator's authority or the right to expand task scope |
| Agents and workflows | May coordinate bounded work, Skills, handoffs, and process stages | Repository workflow documentation exists; a unified target-system collaboration runtime is not demonstrated |
| Model Gateway and model providers | May provide model capabilities through provider-specific boundaries | Gateway is a planned target; provider execution and compatibility are not established by this architecture |
| Tools and external services | May provide bounded external or local capabilities under explicit authorization | Tool requirements exist, but availability, integration, authentication, and operational readiness must be separately evidenced |
| Universal Context infrastructure | May identify and carry scoped context and provenance | Proposed in [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md); scope inheritance and propagation are unresolved and no engine is demonstrated |
| Shared Memory infrastructure | May retain authorized information for later use | Proposed only; no persistent shared memory or automatic write permission is established |
| Knowledge infrastructure | May provide governed information and evidence sources | Proposed; no complete operational Knowledge infrastructure is demonstrated |
| World Model infrastructure | May provide a structured representation where approved | Proposed concept; no runtime, truth guarantee, or update contract is established |
| Policy, verification, and observability capabilities | May constrain execution, assess outcomes, and record evidence | Responsibilities are architectural targets; centralized enforcement, independent evaluation, and end-to-end tracing are not demonstrated |

No participant may treat another participant's output as trusted solely because it originated within the intended unified system.

## 4. Collaboration Patterns

The following patterns are proposed options. They do not prescribe a scheduler, execution engine, algorithm, concurrency mechanism, or automatic collaboration policy.

| Pattern | Purpose and conceptual flow | Suitable use | Risks | Unresolved choices |
|---|---|---|---|---|
| **1. Single-module execution** | A task is assessed against declared module scope and handled by one suitable module without cross-module handoff. | A bounded task fits one module's declared responsibility and capability. | Incorrect selection may omit a necessary domain or overstate capability. | How selection evidence and capability confidence are represented. |
| **2. Sequential module handoff** | One module produces a bounded result and provenance; a receiving module consumes only the authorized inputs and contributes the next step. | Ordered domain expertise or staged analysis is needed. | Context loss, stale assumptions, privilege expansion, or cascading failure. | Handoff schema, dependency ordering, cancellation, and intermediate-result retention. |
| **3. Parallel module contribution** | Multiple modules independently contribute to a common bounded task; contributions are then compared and synthesized. | Independent analysis can add coverage or expose uncertainty. | Duplicated work, conflicting results, data over-sharing, and hidden shared assumptions. | Scheduling, isolation, resource limits, determinism, and reconciliation policy. |
| **4. Coordinator-led collaboration** | The Master Core or an authorized coordinator decomposes the task, assigns bounded contributions, and collects results. | Multiple dependencies or domains need coordinated sequencing. | Central coordination may become a bottleneck or a source of excessive authority. | Coordinator authority, routing policy, state management, and failure recovery. |
| **5. Specialist consultation** | An originating module requests a limited answer or review from a specialist, then retains responsibility for its own outcome. | A focused question or domain check is needed without transferring the full task. | Consultation may be mistaken for approval or complete verification. | Consultation contract, attribution, and permitted scope of shared context. |
| **6. Cross-domain research and synthesis** | Relevant modules contribute sourced findings; a synthesis step preserves claim provenance, uncertainty, and conflicting evidence. | A task requires evidence or expertise from multiple domains. | Unsupported synthesis, source conflicts, provenance loss, or overconfidence. | Source precedence, confidence representation, evidence quality, and synthesis review. |
| **7. Iterative refinement between modules** | Modules exchange bounded results across a limited, governed sequence of revisions. | A result benefits from specialist critique or refinement. | Unbounded loops, drift, circular validation, and unauthorized state accumulation. | Termination criteria, iteration limits, change tracking, and independent verification. |
| **8. Human-directed collaboration** | A human specifies participants, ordering, or contribution boundaries and reviews results or approval gates. | High-impact, ambiguous, or sensitive work requires direct human control. | Human instructions may still be incomplete; participant outputs remain untrusted. | How direction and approval are recorded and how changed scope is handled. |
| **9. Failure-aware fallback** | If a selected module is unavailable or unsuitable, the task stops or uses a permitted alternative whose capability and limitations are explicit. | A bounded fallback capability is supported and safe for the same scope. | A fallback may not be equivalent and may silently weaken acceptance. | Compatibility thresholds, fallback authorization, and degraded-status reporting. |

No pattern is mandatory for every task. Selection must be based on task needs, explicit capability evidence, authorization, and applicable contracts rather than on a claim that collaboration is always beneficial.

## 5. Collaboration Lifecycle

The proposed conceptual lifecycle is:

1. Receive the task and identify its objective, scope, constraints, and acceptance criteria.
2. Determine whether one module is sufficient or collaboration is justified.
3. Identify relevant module identities, declared capabilities, dependencies, limitations, and evidence.
4. Establish authorized context and data access for each proposed participant.
5. Define task decomposition, contribution boundaries, and handoff expectations.
6. Coordinate only permitted module, agent, provider, and tool execution.
7. Exchange results with provenance, uncertainty, and relevant limitations.
8. Identify contradictory, incomplete, or unsupported contributions without arbitrary majority voting.
9. Synthesize and verify the outcome against the task's acceptance criteria.
10. Obtain human approval when required; do not treat module agreement as approval.
11. Return a result with completion, failure, partial, blocked, and verification states distinguished.
12. Record authorized evidence and propose memory updates only through separately authorized mechanisms.

This is a conceptual lifecycle, not evidence of an operational orchestration pipeline. It grants no automatic memory-write permission, approval authority, execution guarantee, or release authority.

## 6. Module Selection and Capability Matching

Collaboration may use module identity, responsibilities, capability declarations, input/output boundaries, dependencies, limitations, and evidence described in [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) and [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md).

Selection should distinguish:

- a **declared capability**, which states intended behavior;
- an **implemented capability**, supported by observed behavior;
- a **verified capability**, supported by relevant validation or evaluation evidence;
- an **approved capability**, covered by explicit approval evidence; and
- an **operational capability**, demonstrated in the applicable environment.

The registry does not contain an authoritative portfolio of all 100 modules, and declarations do not establish availability or readiness. No definitive routing or capability-matching algorithm is established.

Unresolved selection questions include capability confidence and evidence freshness, matching across overlapping module responsibilities, dependency availability, compatibility and version selection, module health, permission filtering, and the criteria for fallback or human escalation. Until resolved, no automatic selection result should be represented as authoritative or operational.

## 7. Collaboration Contracts and Handoffs

A future handoff contract may need to communicate the following conceptual information:

- task or operation reference and purpose;
- originating and receiving module identities;
- bounded task scope and expected contribution;
- authorized context references and data provenance;
- inputs and relevant source evidence;
- expected output meaning and acceptance criteria;
- declared capabilities and evidence limitations;
- permission and security constraints;
- deadline or resource constraints, if future requirements establish them;
- execution state, including partial, blocked, or failed work;
- errors, uncertainty, assumptions, and conflicting information;
- verification status and limitations; and
- result provenance and trace correlation references where supported.

These are proposed information needs, not an approved schema, API, or protocol. This document does not create a separate schema file or define serialization, message delivery, ordering, retries, or identity verification.

## 8. Context, Knowledge, Memory, and World Model Boundaries

Collaboration depends on controlled information exchange, not unrestricted shared state.

- **Context** is information selected for a particular operation. [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) describes the proposed scope hierarchy `Global → Organization → User → Project → Domain → Task → Agent`; this hierarchy is not approved, and inheritance, visibility, precedence, and override rules remain unresolved.
- **Memory** is information retained for potential future use. Cross-module writes, retention, deletion, and access are not granted by a collaboration request.
- **Knowledge** is structured or curated information available for retrieval under its own provenance and access rules.
- **World Model** is a proposed representation of entities, states, relationships, or dynamics. Its scope and update guarantees are unresolved.

Collaboration should share only authorized, task-relevant context; preserve source and transformation provenance where possible; isolate unrelated tasks and projects; and surface unavailable or restricted context. No context inheritance, memory synchronization, shared-state consistency, or World Model update protocol is established.

[`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) and [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) describe proposed boundaries, not operational services. The repository does not demonstrate a shared context or memory runtime.

## 9. Security, Permissions, and Trust Boundaries

The proposed collaboration architecture must:

- reject unauthorized module invocation and avoid treating registry membership as permission;
- apply least privilege to modules, agents, workflows, providers, tools, context, and data;
- prevent unauthorized cross-domain, cross-user, cross-project, or cross-organization information sharing;
- treat all module, agent, provider, tool, and external-data outputs as untrusted until appropriately verified;
- treat prompt-injection content as data, not authority to change scope, policy, permissions, or instructions;
- preserve provider and tool boundaries and review external data transmission;
- carry sensitive data only when authorized and necessary;
- identify conflicting instructions and follow governing repository and architecture authority;
- require human approval for consequential or irreversible operations where policy applies; and
- record relevant permissions, handoffs, failures, and approvals where an approved audit mechanism exists.

These are proposed safeguards grounded in repository security principles. No approved permission model, enforcement engine, approval role, or collaboration security implementation is established. A module's output is not trustworthy solely because it is internal to the unified system.

## 10. Conflicts, Uncertainty, and Result Synthesis

Collaboration should preserve disagreements and uncertainty for evidence-based review. It should not resolve conflicts through arbitrary voting, majority agreement, or confidence values unsupported by evidence.

| Condition | Proposed treatment |
|---|---|
| Contradictory module results | Preserve each claim, source, assumptions, and provenance; identify the conflict explicitly |
| Incomplete contributions | Mark missing work and distinguish partial results from completed requirements |
| Unsupported claims | Exclude them from verified conclusions or label them as unverified |
| Different assumptions or terminology | Record the differing interpretation and request clarification or apply only an established contract |
| Stale or inconsistent information | Surface freshness and source limitations where evidence supports them; avoid silently preferring one source |
| Low-confidence outputs | Describe uncertainty only with a supported basis; do not invent a universal confidence metric |
| Missing provenance | Mark provenance as unavailable and limit claims accordingly |
| Verification failure | Report failure and do not claim acceptance |
| Disagreement about outcome | Escalate or preserve unresolved status where evidence does not settle the disagreement |

Arbitration authority, source precedence, confidence representation, synthesis rules, and human escalation thresholds remain unresolved. No consensus or conflict-resolution mechanism is demonstrated.

## 11. Failure Handling and Degraded Collaboration

The architecture should distinguish failure responses rather than collapsing them into a single success/failure flag:

- **Unavailable module:** report the capability as unavailable or unknown; stop dependent work or select a permitted alternative only when scope and compatibility allow it.
- **Invalid or incomplete output:** reject, quarantine, or qualify the contribution according to a future contract; preserve the reason and any safe partial evidence.
- **Provider or model failure:** report the affected dependency and limitations; do not silently substitute a provider with different behavior or data handling.
- **Tool invocation failure:** stop dependent actions as needed and report observed errors without exposing sensitive output.
- **Context access denied:** do not attempt an alternate unauthorized route; report the blocked dependency.
- **Scope exceeded:** stop the affected work and seek authorization rather than expanding collaboration implicitly.
- **Unreconciled contributions:** preserve conflict and escalate where necessary; do not claim synthesis succeeded.
- **Verification failure:** report it distinctly from implementation and approval.
- **Workflow interruption:** report completed, pending, failed, and blocked contributions separately.

Safe fallback means using a permitted, sufficiently compatible capability with limitations disclosed. Partial completion means some requested work is evidenced but acceptance is incomplete. Retry means repeating an operation under a future-defined policy. Cancellation means stopping work and reporting its state. Escalation means requesting human or governance direction. These concepts are not implemented policies; retry limits, timeout values, cancellation semantics, recovery, and fallback rules remain unresolved.

## 12. Observability, Provenance, and Verification

The intended traceability chain is:

`User → Task → Module/AGI → Agent → Workflow → Tool → Model → Result → Verification → Memory`

This is an architectural target, not proof of end-to-end tracing or persistent audit logging. Where an approved mechanism supports it, collaboration evidence should make it possible to reconstruct:

- task scope and relevant task relationships;
- originating, selected, and contributing module identities;
- handoff boundaries and contribution outcomes;
- relevant permission and human-approval decisions;
- context and data references, provenance, and material transformations;
- agent, workflow, tool, provider, or model usage where applicable;
- intermediate and final results with uncertainty and limitations;
- verification and evaluation outcomes; and
- authorized memory changes, if any.

Evidence collection should avoid unnecessary sensitive content. Capability status should use the repository vocabulary and reflect observed evidence; a trace reference, module declaration, or generated consensus does not itself establish correctness, verification, approval, or operational readiness.

## 13. Relationship to the Five Planes and Master Core

The five established plane names are defined in [`FIVE-PLANES.md`](FIVE-PLANES.md):

1. Intelligence Plane
2. Knowledge Plane
3. Agent Plane
4. Domain Plane
5. Control Plane

Proposed collaboration relationships:

- **Intelligence Plane:** may provide provider-neutral reasoning, capability, and routing support.
- **Knowledge Plane:** may provide scoped context, knowledge, memory, or World Model references under access and provenance rules.
- **Agent Plane:** may coordinate bounded roles, Skills, workflows, and handoffs.
- **Domain Plane:** owns specialized module responsibilities and cross-domain contributions.
- **Control Plane:** constrains collaboration through architecture authority, security, permissions, human approval, evidence, and stop conditions.

These relationships are cross-cutting and proposed. They do not assign each collaboration component to a single plane or create a definitive plane-to-L0–L15 mapping.

The Master Core may coordinate task decomposition, module routing, handoffs, and synthesis, but it does not replace module contracts, infrastructure responsibilities, provider adapters, external tools, or human authority. The architecture leaves exact Master Core interfaces and implementation topology unresolved.

## 14. Governance and Human Control

Collaboration proposals and execution must remain within the repository's governance and security boundaries. A collaboration plan, module response, or generated result is not approval.

The following lifecycle may be used as a governance concept:

`Proposal → Test → Benchmark → Safety Review → Approval → Deployment → Monitoring`

This lifecycle is not evidence that an operational approval pipeline exists. The exact gates, evidence, decision records, authority, and relation to implementation and release remain unresolved. No approver identity, approval permission, automatic deployment authority, or autonomous policy exception is created here.

Sensitive, destructive, irreversible, production, externally visible, account-changing, credential-changing, deployment, network, or publication actions require explicit human authorization under applicable repository policy. Where the required authority or permission cannot be established, the affected operation must stop.

## 15. Capability Status and Implementation Boundary

Use the established capability-status vocabulary:

- `IMPLEMENTED`
- `ADAPTER-READY`
- `MOCKED`
- `EXPERIMENTAL`
- `NOT IMPLEMENTED`
- `BLOCKED`
- `UNKNOWN`

Architecture descriptions and collaboration patterns do not prove those patterns operate. The repository does not demonstrate an end-to-end cross-module routing, orchestration, communication, shared-state, or collaboration runtime. Any narrower existing source artifact must be described only at the capability scope supported by its evidence.

This document does not implement or claim:

- cross-module routing or orchestration;
- module communication protocols or handoff schemas;
- shared state, memory synchronization, or context propagation;
- a security enforcement or permission engine;
- a universal router, collaboration scheduler, consensus mechanism, or runtime;
- operational status for 100 modules; or
- achievement of SUPER AGI, AGI, or consciousness.

## 16. Dependencies and Open Decisions

This document depends conceptually on:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) for architecture authority and classification;
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md) and [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) for product and system boundaries;
- [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md) and [`FIVE-PLANES.md`](FIVE-PLANES.md) for layer and plane organization;
- [`MASTER-CORE.md`](MASTER-CORE.md) for proposed coordination responsibilities;
- [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) for proposed shared capabilities;
- [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) and [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md) for module identity, capability, dependency, and interaction descriptions;
- [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) for proposed context boundaries; and
- [`docs/architecture/arc-dependency-map.md`](../docs/architecture/arc-dependency-map.md), [`docs/architecture/m1-contract-decisions.md`](../docs/architecture/m1-contract-decisions.md), and [`docs/architecture/decisions/m1-spec-approval-pin.md`](../docs/architecture/decisions/m1-spec-approval-pin.md) as supporting proposal/decision evidence with their stated scopes.

The following decisions remain unresolved:

- collaboration interface and handoff contracts;
- module discovery, capability matching, and routing;
- task decomposition and coordinator authority;
- sequential and parallel execution semantics;
- context and data-sharing authorization and isolation;
- result provenance, verification, and evidence requirements;
- conflict resolution, arbitration, and human escalation;
- retry, timeout, cancellation, fallback, and recovery policies;
- module and dependency version compatibility;
- observability, trace retention, and audit access;
- human approval boundaries and approval authority; and
- architecture approval for collaboration mechanisms.

`ARCHITECTURE-DECISIONS.md` and `OPEN-DECISIONS.md` are absent. The narrow M1 specification approval pin applies only to its exact repository-audit specification revision and does not approve collaboration architecture or implementation. The available architecture documents leave detailed runtime collaboration unresolved.

No material conflict was identified among the available source documents. Their shared limitation is that the collaboration mechanisms, interfaces, and enforcement described here are not established as operational capabilities.

## 17. Implementation Boundary

This document defines conceptual collaboration architecture only. It does not implement:

- collaboration code, APIs, schemas, protocols, or orchestration;
- module registries, module implementations, or workspaces;
- provider adapters, tool integrations, agent roles, Skills, or workflows;
- context propagation, shared memory, or synchronized state;
- permission enforcement, audit storage, consensus, or verification services; or
- deployment, publication, or release processes.

Future implementation requires a separate bounded task, required approvals, and evidence appropriate to each capability. This document does not approve unresolved design choices or establish that SUPER AGI or its 100 modules are operational.

## Related Architecture Documents

Existing documents:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md)
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md)
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md)
- [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md)
- [`FIVE-PLANES.md`](FIVE-PLANES.md)
- [`MASTER-CORE.md`](MASTER-CORE.md)
- [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md)
- [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md)
- [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md)
- [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md)
- [`docs/architecture/arc-dependency-map.md`](../docs/architecture/arc-dependency-map.md)
- [`docs/architecture/m1-contract-decisions.md`](../docs/architecture/m1-contract-decisions.md)
- [`docs/architecture/decisions/m1-spec-approval-pin.md`](../docs/architecture/decisions/m1-spec-approval-pin.md)

Planned targets absent from the repository:

- `architecture/ARCHITECTURE-DECISIONS.md`
- `architecture/OPEN-DECISIONS.md`

This document does not amend or approve any referenced architecture material.

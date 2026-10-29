# Universal AGI Module Contract

## 1. Purpose, Scope, and Status

This document defines the proposed common contract that SUPER AGI intelligence modules should follow to describe their responsibilities and interact with the intended unified system. A shared contract is intended to make module boundaries, capabilities, dependencies, permissions, evidence, and compatibility explicit, while avoiding duplicated infrastructure and unsupported claims of readiness.

The contract is subordinate to [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), which governs architecture authority and document status. It is consistent with [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`FIVE-PLANES.md`](FIVE-PLANES.md), [`MASTER-CORE.md`](MASTER-CORE.md), and [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md).

The intended product principle remains:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

The modules are specialized domains within one intended system, not 100 independent AI products. The `claude-skills` repository is the provider-neutral engineering and governance platform used to build and maintain the separate SUPER AGI target system; it is not that system's runtime.

The following status distinctions apply:

- **Established:** product identity and system boundaries, provider neutrality, human authority for consequential actions, and evidence-based capability claims.
- **Proposed:** a common module contract and the conceptual categories described here.
- **Unresolved:** final fields, identifier and version conventions, schemas, protocols, conformance authority, and runtime enforcement.
- **Not implemented:** no module runtime, contract validator, registry service, or complete operational module portfolio is demonstrated by this document or the cited architecture sources.

This document specifies architecture intent only. It does not prove a module runtime exists, approve all proposed contract details, or claim any module is deployed or operational.

## 2. Contract Design Principles

A module contract should preserve these principles:

1. **Consistent identity:** use one stable module identity across its definition, registry entry, implementation evidence, and workspace reference.
2. **Explicit responsibilities:** define what a module owns, what it delegates, and what it does not claim.
3. **Defined interaction boundaries:** describe intended inputs, outputs, dependencies, errors, and evidence without pretending an API or serialization format is approved.
4. **Shared infrastructure reuse:** modules should declare and use shared capabilities where approved rather than implementing independent copies by default.
5. **Provider and tool independence:** module definitions express canonical behavior without hard-coding one provider or tool vendor.
6. **Least privilege:** context, data, providers, tools, memory, and other capabilities require explicit scope and permission.
7. **Observable, evidence-aware execution:** distinguish declared behavior from observed implementation, verification, approval, and operational readiness.
8. **Versioning and compatibility:** identify changes and compatibility impacts without inventing a final versioning scheme.
9. **Extensibility:** support the intended 100-module portfolio and future additions without creating independent systems or duplicate identities.
10. **Specification separate from implementation:** a contract, registry record, workspace, and runtime module are different artifacts and states.
11. **Honest capability claims:** a declaration, document, or registry entry does not prove implementation or operation.

These principles follow the repository's stated architecture direction. The details below remain proposals until separately approved under the repository's authority model.

## 3. Module Identity and Metadata

Each module definition should describe the module consistently with its Module Registry entry. The Registry's current identity fields are proposals and do not establish an identifier convention or finalized schema.

| Field or field group | Intended use | Status |
|---|---|---|
| Stable module identifier | Distinguish the module from all other modules | Required in concept; convention unresolved |
| Module name and description | Human-readable identity and purpose | Required in concept; exact fields proposed |
| Domain and subdomain | Classify the module's subject responsibility | Proposed; taxonomy unresolved |
| Contract version | Identify the applicable contract revision | Required when versioning is adopted; scheme unresolved |
| Module definition version | Identify changes to the module specification separately from contract changes | Optional, proposed; relationship to contract version unresolved |
| Intended responsibilities and non-responsibilities | Define ownership and boundaries | Required in concept |
| Lifecycle status | Describe specification or deployment lifecycle | Proposed; lifecycle vocabulary and authority unresolved |
| Capability status | Describe implementation evidence using the repository vocabulary | Required for capability claims |
| Registry reference | Link the definition to its registry entry | Proposed; registry reference form unresolved |
| Documentation references | Link relevant governing and supporting documents | Optional, proposed |
| Implementation references | Identify implementation artifacts when they exist | Optional; must be evidence-backed |
| Workspace metadata | Associate a module with its intended workspace/navigation surface | Optional, proposed; representation unresolved |
| Dependencies and compatibility | Declare shared services, modules, and version constraints | Required in concept where dependencies exist |
| Evidence references | Support implementation, verification, evaluation, approval, and operational claims | Required for the corresponding claims |

The Module Registry explicitly leaves the stable identifier convention, ownership model, versioning, schema, and workspace reference unresolved. This contract does not select values or invent owners, authorities, release versions, or implementation evidence.

## 4. Responsibilities and Boundaries

Each module definition should state:

- its purpose and the problems or tasks it is intended to address;
- responsibilities it owns and the boundaries of those responsibilities;
- responsibilities delegated to shared infrastructure;
- responsibilities delegated to or coordinated with other modules;
- expected inputs, outputs, and completion conditions;
- capabilities it does not provide or cannot claim;
- conditions requiring refusal, deferral, clarification, or escalation; and
- relevant domain, data, security, and compatibility constraints.

Modules should not duplicate system-wide responsibilities merely to appear self-contained. In particular, a module is not required by this document to implement its own memory, model gateway, agent framework, tool infrastructure, security authority, or independent governance system.

The registry describes and discovers modules; the module contract describes intended interaction and responsibility boundaries; an implementation supplies behavior; and a workspace supplies a user-facing navigation or interaction surface. None substitutes for the others. Module boundaries must preserve the single unified system principle and must not imply independent products or autonomous runtime services.

The exact allocation of responsibility between a module, shared infrastructure, and the Master Core remains proposed and may require domain-specific decisions.

## 5. Capability Declaration

A module should declare capabilities in a way that identifies their purpose, requirements, restrictions, and evidence. A capability declaration states intended or observed behavior; it does not itself prove implementation or operational readiness.

For each capability, the conceptual declaration should include:

- a stable capability identifier, if an approved convention is later established;
- a concise description and intended outcome;
- whether the capability is required or optional for the module;
- required inputs and expected outputs;
- relevant module, shared infrastructure, provider, or tool dependencies;
- security, data, and permission restrictions;
- known limitations and unsupported cases;
- evidence references for implementation, verification, compatibility, or approval claims; and
- one status from the canonical capability vocabulary.

Use only these capability statuses:

- `IMPLEMENTED`
- `ADAPTER-READY`
- `MOCKED`
- `EXPERIMENTAL`
- `NOT IMPLEMENTED`
- `BLOCKED`
- `UNKNOWN`

The appropriate status must be supported by evidence. Do not introduce a separate capability status vocabulary or infer status from a name, interface, registry entry, or documentation.

Capability status is distinct from lifecycle status. For example, a module may be specified while its capabilities remain `NOT IMPLEMENTED`; an implementation may exist while deployment approval is absent; and an adapter may be described without evidence that it is installed, authenticated, or operational.

## 6. Inputs, Outputs, and Interaction Contracts

The module contract should describe interaction semantics without claiming a finalized API, message protocol, or machine-readable schema.

### Input expectations

A module's definition should identify, as applicable:

- the request or task objective;
- the authority and scope under which work is requested;
- the context and data classes required;
- input validation expectations and unsupported input conditions;
- dependency and capability assumptions;
- applicable permissions and approval dependencies; and
- provenance required to interpret the input safely.

### Output expectations

A module's definition should explain how its outputs communicate, as applicable:

- results and their interpretation limits;
- successful, partial, blocked, or failed work;
- uncertainty, conflicting information, and known limitations;
- errors, invalid inputs, missing dependencies, and unsupported requests;
- provenance and evidence supporting material claims;
- verification outcomes and unrun or unavailable checks; and
- permission denials or approval requirements.

Outputs should not present generated claims as verified facts without evidence. If execution is partial, uncertain, denied, interrupted, or unsupported, that state should remain explicit rather than being converted to success-shaped output.

These are conceptual requirements. The repository does not establish a mandatory serialization format, field schema, error code set, or communication protocol for module interactions. Those decisions remain open.

## 7. Relationship to the Master Core

The proposed Master Core would coordinate module use while respecting module and system boundaries. Conceptual interactions include:

1. discover module descriptions through the registry;
2. compare a task with declared module responsibilities and capabilities;
3. route only work permitted by the task scope and applicable policies;
4. propagate authorized context and permission constraints;
5. coordinate execution through future defined interfaces;
6. receive results, failures, limitations, and supporting evidence;
7. report degraded capability or partial completion honestly; and
8. coordinate cross-module work only through declared, authorized boundaries.

These interactions are proposed, not implemented. The repository does not demonstrate Master Core dispatch, module selection, permission propagation, runtime coordination, or cross-module execution. This document does not redefine the Master Core described in [`MASTER-CORE.md`](MASTER-CORE.md).

## 8. Relationship to Shared Universal Infrastructure

Modules may depend on shared capabilities, but the dependencies and permissions must be declared rather than assumed. Relevant concepts include:

- **Context:** scoped task or domain information supplied under authorization.
- **Memory:** read/write behavior, persistence, retention, and deletion policy where separately approved.
- **Knowledge:** source authorization, retrieval, provenance, and evidence handling.
- **World Model:** any model or representation dependency, including provenance and uncertainty requirements.
- **Skills and agents:** reusable procedures and bounded execution roles, with explicit handoffs and permissions.
- **Providers and models:** provider-neutral capability requirements and adapter boundaries.
- **Tools:** explicit tool dependencies, operations, permission scope, and failure behavior.
- **Workflows:** process references that coordinate bounded stages but do not grant runtime authority.
- **Data and artifacts:** input/output ownership, classification, provenance, and handling restrictions.
- **Evaluation and verification:** evidence references and criteria separate from module implementation.
- **Observability and audit:** trace and audit references where an approved mechanism exists.
- **Security and governance:** least-privilege requirements, approval dependencies, and restrictions.

The repository does not demonstrate these as a complete operational shared-infrastructure service. In particular, `architecture/UNIVERSAL-INFRASTRUCTURE.md` is absent and remains a planned architecture dependency. Naming a dependency does not establish its implementation, availability, authentication, permission enforcement, or compatibility.

## 9. Relationship to the Five Architectural Planes

The five plane names are established in [`FIVE-PLANES.md`](FIVE-PLANES.md):

1. Intelligence Plane
2. Knowledge Plane
3. Agent Plane
4. Domain Plane
5. Control Plane

A module may interact with one or more planes according to its responsibilities. For example, domain behavior may rely on Intelligence capabilities, Knowledge resources, Agent execution, and Control constraints. A module should describe relevant plane relationships where useful but must not be forced into exactly one plane.

Plane relationships are cross-cutting responsibility views, not proof of services, deployments, directories, or runtime components. Exact module-to-plane ownership and module-to-L0–L15 placement remain unresolved. This document does not create a definitive layer mapping or alter the five-plane definitions.

## 10. Context, Memory, and Data Boundaries

Module definitions should state the context required for their operation, the context they may access, and any restrictions on storing, returning, or sharing data.

The task specification for this document names the following possible context hierarchy:

`Global → Organization → User → Project → Domain → Task → Agent`

This hierarchy is not established by the reviewed canonical architecture documents as an approved contract. It may be considered a proposed classification for future review, but its scopes, inheritance rules, precedence, access controls, and relationship to provider or session context remain unresolved.

For context and data, a module definition should address:

- required and optional context sources;
- permitted scope and purpose of access;
- source provenance and confidence or uncertainty where relevant;
- sensitive-data restrictions and redaction requirements;
- authorization and scope enforcement dependencies;
- ownership and provenance of generated outputs;
- memory read/write needs, if any;
- retention, persistence, and deletion dependencies; and
- restrictions on cross-domain or cross-user information sharing.

No persistent memory, storage, or universal context mechanism is implied. Memory writes or consequential configuration changes require explicit authorization and applicable governance; the module contract alone does not grant that permission.

## 11. Security and Permission Contract

Each module definition should describe security expectations appropriate to its capabilities:

- use least privilege for data, context, providers, tools, and shared services;
- declare provider and tool dependencies and requested operations;
- require permission checks before consequential actions;
- identify human approval dependencies where repository policy requires them;
- treat user, repository, provider, tool, agent, and generated content as untrusted input unless separately validated;
- preserve sensitive-data boundaries and avoid unauthorized disclosure;
- provide evidence and trace references where an approved audit mechanism exists;
- fail safely when authorization or required security state cannot be established;
- prevent unauthorized self-modification, permission expansion, or approval bypass; and
- distinguish proposals from approved changes and execution.

No approval authority or runtime enforcement mechanism is assigned here. Policy documentation and a contract declaration do not demonstrate that access controls, auditability, prompt-injection resistance, or permission checks are technically enforced.

## 12. Execution, Failure, and Degraded Behavior

A conforming module definition should specify how its intended behavior represents relevant outcomes. The contract must not imply that fault tolerance or a particular execution runtime has been implemented.

| Condition | Intended reporting behavior |
|---|---|
| Successful completion | Identify the result and supporting evidence; do not overstate verification or approval |
| Partial completion | Separate completed work from pending, failed, or blocked work |
| Invalid input | Identify the invalid or unsupported condition without fabricating a result |
| Missing dependency | Identify the dependency and whether work is blocked or can continue in a documented degraded mode |
| Unavailable tool or provider | Report unavailability and any authorized fallback limitations |
| Permission denial | Stop the affected operation and identify the approval or permission dependency |
| Conflicting information | Preserve the conflict and uncertainty; do not silently select an unsupported result |
| Verification failure | Report failure and distinguish implementation from acceptance |
| Unsupported capability | State that the capability is unsupported or not implemented using the canonical status vocabulary where status is applicable |
| Timeout or interrupted execution | Report incomplete execution and available evidence, if the eventual runtime can establish it |
| Explicitly blocked behavior | Preserve the blocker; do not report success-shaped output |

The runtime's retry, timeout, cancellation, rollback, and recovery semantics are unresolved. A contract may state expected failure behavior without proving that the implementation reliably enforces it.

## 13. Observability and Evidence

Where applicable, module execution should return or expose evidence references for:

- module identity and applicable contract version;
- task or operation reference;
- declared capability used;
- relevant dependency references;
- execution outcome and partial/degraded state;
- errors, blockers, and limitations;
- output provenance;
- verification evidence;
- permission decision reference; and
- trace correlation information, if an approved mechanism supports it.

The repository's architectural target trace is:

`User → Task → Module → Agent → Workflow → Tool → Model → Result → Verification → Memory`

This chain is a target, not evidence of an operational end-to-end trace system. A module should report only evidence it actually has. Documentation, declaration, successful compilation, or a registry record alone does not prove successful execution, verification, compatibility, approval, or operational readiness.

## 14. Versioning and Compatibility

The contract should support independent identification of contract revisions and module-definition changes where future governance requires it. Proposed principles include:

- identify the applicable contract and module definition revision;
- document compatibility expectations and dependency constraints;
- identify behavior changes that may break existing consumers;
- document deprecation and migration expectations;
- preserve registry consistency when definitions change; and
- keep provider/tool compatibility evidence separate from module version claims.

The repository has not approved a versioning scheme, compatibility range syntax, breaking-change policy, deprecation period, migration authority, or module release model. No semantic versioning or other convention is mandated by this document.

## 15. Conformance and Governance

Future conformance review should consider whether a module definition:

- contains required identity and responsibility metadata;
- declares capabilities and their evidence status;
- describes inputs, outputs, unsupported cases, and failure semantics;
- identifies dependencies, permissions, and data boundaries;
- explains cross-plane or cross-module interactions without inventing mappings;
- references applicable contracts and evidence;
- identifies version and compatibility information where established; and
- follows repository governance and approval boundaries.

Architectural conformance is not the same as implementation correctness, test success, security enforcement, operational readiness, deployment approval, or release approval. A completed definition does not prove that the module behaves as specified.

No contract validator, conformance test suite, or approval authority is established here. Changes to a future contract or module definition must remain traceable and be reviewed under separately established governance; this document assigns no new authority.

## 16. Open Decisions and Implementation Evidence

The following decisions remain unresolved based on the available architecture evidence:

- final machine-readable module contract schema and required/optional field rules;
- module identity convention and its relation to the Registry;
- API, message, or communication interface;
- input/output serialization and error representation;
- contract and module-definition versioning;
- capability declaration format and evidence reference model;
- conformance criteria and approval authority;
- dependency compatibility and conflict-resolution rules;
- runtime permission and security enforcement;
- Registry integration and discovery interfaces;
- context hierarchy, inheritance, precedence, and propagation;
- memory persistence, retention, deletion, and write authorization;
- trace propagation and audit storage; and
- runtime behavior for retries, cancellation, timeout, and degraded execution.

The optional `UNIVERSAL-INFRASTRUCTURE.md` document does not exist. The Module Registry and Master Core documents describe proposed concepts, but neither proves operational registry access or module dispatch. No authoritative list or implementation evidence for 100 operational modules is established. The exact-revision M1 approval pin applies only to the repository-audit specification and does not approve this contract, module runtime, Registry, or infrastructure.

No direct conflict was identified among the reviewed architecture sources. Their shared limitation is that many detailed relationships and runtime contracts remain proposals or unresolved decisions.

## 17. Implementation Boundary

This document is an architecture specification only. It does not:

- implement module runtime behavior, APIs, or contract validators;
- create a separate machine-readable schema or registry;
- implement any of the 100 intelligence modules;
- create module workspaces or navigation;
- create or modify providers, integrations, Skills, agents, or workflows;
- modify the Module Registry, Master Core, Universal Infrastructure, five-plane document, or L0–L15 layer map;
- claim that all 100 modules exist or operate; or
- claim AGI, SUPER AGI, or consciousness capabilities without supporting evidence.

Implementation, conformance validation, deployment, approval, and operational readiness remain separate states requiring their own authorization and evidence.

## Related Canonical and Supporting Documents

Existing architecture documents:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md)
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md)
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md)
- [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md)
- [`FIVE-PLANES.md`](FIVE-PLANES.md)
- [`MASTER-CORE.md`](MASTER-CORE.md)
- [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md)

Supporting proposal and decision records:

- [`docs/architecture/arc-dependency-map.md`](../docs/architecture/arc-dependency-map.md)
- [`docs/architecture/m1-contract-decisions.md`](../docs/architecture/m1-contract-decisions.md)
- [`docs/architecture/decisions/m1-spec-approval-pin.md`](../docs/architecture/decisions/m1-spec-approval-pin.md)

Planned target absent from the repository:

- `architecture/UNIVERSAL-INFRASTRUCTURE.md`

Other related targets, including a separate capability-status or security-governance contract, remain subject to the classification and approval rules in [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md).

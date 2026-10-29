# Security, Governance, and Trust Architecture

## 1. Document Identity and Status

This document defines proposed security, governance, and trust boundaries for the `claude-skills` engineering platform and the separate future SUPER AGI target system. It is intended for architecture, implementation, integration, and review planning. It describes responsibilities and decision needs; it does not implement enforcement controls or establish an operational governance service.

Authority and document classification follow [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md). This document is intended to remain consistent with [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`FIVE-PLANES.md`](FIVE-PLANES.md), [`MASTER-CORE.md`](MASTER-CORE.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md), and [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md). Repository security policy is documented in [`SECURITY.md`](../SECURITY.md).

The established product principle is:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

The 100 modules are specialized domains within one intended unified system, not 100 independent AI products. The `claude-skills` repository is the provider-neutral engineering and governance platform used to develop that separate system; it is not the SUPER AGI runtime.

Status distinctions:

- **Established:** repository and system boundaries; source-of-truth and approval evidence requirements; provider neutrality; least privilege; careful treatment of secrets and untrusted content; human approval for consequential operations; and separation of implementation, verification, approval, and operational readiness.
- **Proposed:** the security architecture, trust-boundary model, identity and authorization considerations, controlled-change lifecycle, and security responsibilities described here.
- **Unresolved:** identity and authentication integration, authorization model and enforcement, module and tenant isolation, data classification and retention, provider eligibility, incident responsibilities, supply-chain assurance, and final approval authority.
- **Implemented capability:** only behavior supported by direct implementation and verification evidence. This document does not establish operational SUPER AGI security or governance controls.
- **Not implemented, blocked, or unknown:** no unified runtime security enforcement or operational SUPER AGI governance pipeline is demonstrated by the architecture documents reviewed.

This document is an architecture proposal. It does not imply formal approval of unresolved design details, security certification, compliance, or verified safety.

## 2. Security and Governance Scope

Security responsibilities apply across distinct boundaries. Policies for the engineering platform must not be mistaken for controls in a future SUPER AGI runtime.

| Scope | Security and governance concern | Evidence boundary |
|---|---|---|
| `claude-skills` engineering platform | Scope-limited repository changes, source authority, safe tool use, preservation of existing work, secret handling, validation evidence, and Git restrictions | Repository instructions and security policy document expectations; they do not prove every control is mechanically enforced |
| Future SUPER AGI runtime | Runtime identity, module authorization, context and data isolation, provider/tool access, execution, monitoring, and recovery | Target runtime controls are not demonstrated by this repository's architecture documents |
| Master Core | Proposed coordination should respect task scope, permissions, stop conditions, and human approval | Master Core design is proposed; no operational control boundary is shown |
| Intelligence modules and workspaces | Module identity, responsibility, capability, data access, handoffs, and user-facing interaction boundaries | Registry and contract documents propose metadata and boundaries; they do not show operational modules or isolation |
| Agents and workflows | Bounded roles, inputs, outputs, tool use, handoffs, and stopping behavior | Workflow and Skill documents may describe procedures; they do not prove runtime authorization |
| Model Gateway and provider adapters | Provider eligibility, credential use, input disclosure, output trust, fallback, and provenance | Gateway architecture is proposed; provider integrations and security enforcement are not established |
| Tools and external services | Discovery, executable scope, permissions, side effects, external data, failure behavior, and revocation | Tool requirements are not evidence of installed, authenticated, or operational integrations |
| Context, memory, knowledge, and World Model | Scope-aware access, provenance, data minimization, retention, update, and sharing restrictions | Concepts are proposed; no complete persistent infrastructure or access enforcement is demonstrated |
| Shared data and infrastructure | Ownership, classification, dependency isolation, access, integrity, and lifecycle | Infrastructure components and topology remain proposed or unresolved |
| Human users and authorized operators | Explicit authority, consent, review, approval, and accountability for consequential actions | No approval hierarchy or named authority should be inferred |
| Repository files, configuration, and engineering workflows | Trustworthiness of instructions and dependencies, protected data, file scope, validation, and controlled modifications | Repository policy governs work, but policy text is not proof of enforcement by automation |

Security documentation establishes requirements and boundaries, not technical implementation.

## 3. Security Principles

### Established repository principles

The following expectations are stated in repository governance and security material:

- least-privilege tool and provider access;
- explicit scope and authorization for repository and external operations;
- secure handling of credentials, secrets, and sensitive files;
- treating repository content, generated content, external research, and tool output as untrusted data rather than authority;
- preserving provider-neutral canonical behavior and explicit adapter boundaries;
- human approval before destructive, irreversible, production, externally visible, high-impact, or sensitive actions;
- traceability and evidence-based capability claims; and
- separate reporting of implementation, verification, approval, compatibility, and operational readiness.

### Proposed architecture principles

For the future platform and target runtime, this document proposes:

- **Explicit authorization:** define the operation, actor, target, scope, and relevant policy before access or execution.
- **Separation of duties:** keep proposing, implementing, evaluating, approving, deploying, and monitoring as distinct responsibilities.
- **Default-deny where appropriate:** when required identity, permission, scope, or policy state cannot be established, deny or stop the affected sensitive operation.
- **Module and data isolation:** prevent module boundaries from implicitly granting access to another module's data or authority.
- **Provider and tool boundaries:** constrain provider-specific and tool-specific behavior to authorized interfaces.
- **Fail-safe behavior:** do not convert security failures, missing evidence, or degraded operation into success-shaped outcomes.
- **Controlled architectural evolution:** proposals and generated outputs do not approve themselves or silently change policy.

These are architectural design principles. They do not prove the existence or effectiveness of a default-deny engine, access-control system, isolation mechanism, or automated approval gate.

## 4. Trust Boundaries and Threat Surfaces

The architecture should treat boundaries as places where authority, data, or behavior may change and therefore require explicit review:

| Boundary | Trust distinction and threat categories |
|---|---|
| User input and governing system/repository instructions | User text is a request, not permission to override higher-authority policy. Prompt injection may attempt scope expansion or secret disclosure. |
| Trusted configuration and untrusted content | Repository files, retrieved documents, issue text, generated text, and external research can contain malicious or misleading instructions. |
| Master Core and domain modules | Coordination must not silently grant module permissions or allow a module to expand task authority. |
| One module and another module | Cross-module calls can expose data, create confused-deputy behavior, or bypass ownership boundaries if authorization is implicit. |
| Agents and tools | Agent recommendations are distinct from tool execution authority. Tool output may be malicious, malformed, or incomplete. |
| Model Gateway and external providers | Requests may disclose sensitive data; providers may refuse, transform, retain, or process data under provider-specific terms. |
| Shared infrastructure and domain data | Shared capability must not imply shared credentials or unrestricted access to every domain. |
| Repository instructions and retrieved content | Retrieved content cannot override governing instructions or authorize a repository mutation. |
| Engineering agents and repository modifications | An implementation agent must stay within task file scope and preserve unrelated user work. |
| Runtime actions and human approval | A model-generated recommendation or module consensus is not authorization for consequential action. |

Relevant threat categories include prompt injection, misleading or malicious tool output, unauthorized access, privilege escalation, sensitive-data leakage, credential exposure, cross-module information leakage, dependency and supply-chain risk, unsafe configuration changes, unsupported capability claims, and unauthorized deployment or irreversible actions.

These are threat categories for design and review, not findings that those vulnerabilities exist in a particular implementation. No mitigation should be claimed without implementation evidence and appropriate validation.

## 5. Identity, Authentication, and Authorization

The following concepts must remain distinct:

- **Identity:** a representation of an actor or resource, such as a user, organization, project, module, agent, workflow, provider, or tool.
- **Authentication:** evidence used to establish or verify an identity.
- **Authorization:** a decision about whether an identified actor may perform a specific operation on a specific resource within a defined scope.
- **Permission scope:** the permitted operation, data, target, and boundary for an authorization.
- **Policy evaluation:** application of applicable rules to a requested action and its context.
- **Approval:** explicit human authorization for a defined operation or class of operations, recorded with scope and authority.
- **Audit evidence:** records that support later review of identity, policy, permission, approval, and outcome.

Authentication does not automatically grant authorization. A provider credential, authenticated user, registered module, or tool declaration is not by itself permission to access arbitrary data or perform arbitrary operations.

Proposed authorization boundaries include users, organizations, projects, modules, agents, workflows, tools, providers, and shared resources. Each boundary may require distinct identities and scopes, but their relationships and enforcement are unresolved.

The repository does not establish an identity provider, role hierarchy, permission schema, authorization engine, policy decision point, approval authority, or identity propagation protocol. These decisions must be settled with explicit architecture and security evidence before implementation relies on them.

## 6. Context, Data, Memory, and Privacy Boundaries

Security controls should apply to context and data throughout selection, transformation, provider/tool transmission, output, storage, and later use.

- **Universal Context** is information selected for a particular operation.
- **Memory** is information retained for potential future use, subject to separate access, retention, update, and deletion rules.
- **Knowledge** is structured or curated information used for retrieval, with its own sources, provenance, and access rules.
- **World Model** is a proposed representation of entities, states, relationships, or dynamics; its data and update rules remain unresolved.

These concepts are distinct and must not be collapsed into a generic storage or authorization boundary. Module inputs and outputs, cross-AGI collaboration, model/provider requests, tool invocations, and persistent records each require scoped access and provenance.

The proposed context hierarchy is:

`Global → Organization → User → Project → Domain → Task → Agent`

As described in [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), this hierarchy is **proposed, not approved**. Its identity model, inheritance, visibility, precedence, access, and override behavior remain unresolved.

Proposed data controls include:

- collect and transmit only information necessary for the authorized purpose;
- restrict access to the relevant user, project, domain, task, and destination as policy allows;
- preserve source and transformation provenance where available;
- prevent implicit cross-module, cross-user, or cross-organization sharing;
- record retention and deletion as policy decisions rather than assumptions; and
- permit context, memory, or configuration updates only through an authorized mechanism.

No retention period, legal compliance claim, storage guarantee, deletion guarantee, or operational privacy control is established here.

## 7. Model and Provider Security

The intended security boundary around model/provider access is described in [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md). In summary, a future gateway and provider adapters should:

- evaluate provider eligibility against the request, applicable policy, capability evidence, and data-disclosure constraints;
- isolate credentials and account scope within separately authorized provider-specific mechanisms;
- authorize requests before invocation;
- minimize and review context before external transmission;
- account for provider-specific processing, retention, and unsupported behavior where evidence is available;
- treat model output as untrusted until appropriately validated;
- preserve refusals, errors, partial outputs, and provenance;
- constrain fallback to providers separately eligible for the same data and task; and
- record usage and execution provenance where an approved mechanism supports it.

A fallback provider must not automatically receive data the original provider was authorized to process. Each destination is a separate disclosure and authorization decision; failure of one provider does not broaden permissions.

No provider credentials, connected accounts, model integrations, credential manager, or enforcement mechanism is established as operational by the gateway architecture.

## 8. Tool and Agent Security

Agents and workflows may propose or coordinate actions; authorization to execute those actions remains separate. Tool access should be explicitly declared, scoped, and granted only for the operation required.

Proposed requirements include:

- state tool capabilities, inputs, outputs, side effects, and limitations;
- check permissions before consequential operations;
- provide least-privilege filesystem, network, subprocess, account, and repository access;
- treat external tool output as untrusted data;
- identify irreversible or externally visible side effects;
- limit data available to agents and tools to authorized task needs;
- report tool errors and partial completion without hiding effects;
- require human approval where policy applies; and
- preserve actual execution evidence without exposing secrets.

The ability to recommend or formulate an action is not the authority to perform it. A manifest, allowlist, role definition, or Skill does not itself grant permission.

The repository does not establish an operational sandbox, tool-permission engine, universal agent authorization system, or complete integration of the mandatory tools. Specific execution controls require separate implementation and verification.

## 9. Human Control and Consequential Actions

Actions can be distinguished conceptually as:

- **Information generation:** producing analysis or text without changing external or persistent state.
- **Recommendation:** proposing an action for a person or authorized system to consider.
- **Reversible action:** an action with an established and practical means of reversing its effects.
- **Consequential action:** an action that can materially affect users, systems, data, accounts, or external parties.
- **Irreversible or high-impact action:** an action whose effects cannot be reliably reversed or could cause substantial impact.
- **Policy-restricted action:** an action limited or prohibited by governing policy, contract, or authorization.

These categories are explanatory, not an approved universal risk taxonomy. Human review or approval may be required based on scope, sensitivity, impact, and repository policy. Approval should identify the action and its authorized scope; it must not be inferred from silence, a generated recommendation, module agreement, or successful authentication.

No universal approval threshold, risk classification, named approver, or organization policy is established here. An operation requiring approval must stop when the necessary authority cannot be established.

## 10. Governance and Architecture Authority

The states below are separate and must not be conflated:

1. **Architectural proposal:** a recommendation for review.
2. **Documented decision:** a recorded choice with defined scope and status.
3. **Explicit approval:** authorization supported by evidence identifying its authority and effect.
4. **Implementation work:** code, configuration, or documentation realizing a specification.
5. **Operational deployment:** a capability running in an identified environment.
6. **Evidence-based verification:** observed results against defined criteria.

[`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) governs architecture authority and document classification. Repository operating rules are in [`AGENTS.md`](../AGENTS.md), [`CLAUDE.md`](../CLAUDE.md), and [`CONTRIBUTING.md`](../CONTRIBUTING.md). The M1 approval pin is narrowly scoped to the exact repository-audit specification revision and does not approve unrelated architecture or implementation.

The project has not established a general architecture board, security authority, administrator, or approval hierarchy in the reviewed sources. Where approval authority remains unresolved, record the gap and stop work that depends on it rather than inventing an authority.

## 11. Controlled Change and Capability Evolution

The following lifecycle is an architectural governance concept:

`Proposal → Test → Benchmark → Safety Review → Approval → Deployment → Monitoring`

It remains proposed unless separate evidence establishes its formal approval or operationalization. The stages express distinct responsibilities:

- proposing a change does not authorize implementation;
- testing and benchmarking produce bounded evidence, not approval;
- safety review records risk and evidence, not automatic deployment authority;
- approval must be explicit and scoped;
- deployment requires separate authorization and readiness evidence; and
- monitoring does not retroactively approve a change.

Changes to architecture, module contracts, provider adapters, Skills, tool permissions, and runtime capabilities should be scoped, traceable, reviewed against affected boundaries, and supported by appropriate evidence. The repository does not demonstrate a functioning automated approval or deployment pipeline.

## 12. Supply Chain and Repository Integrity

For engineering work in this repository, security and governance should account for:

- repository instruction and task-scope boundaries;
- third-party Skills, agents, dependencies, and generated content as untrusted until reviewed;
- tool installation, configuration, executable identity, and permissions;
- secrets or sensitive data in files, prompts, logs, diffs, and reports;
- scope-limited code and documentation changes;
- preservation of protected files and unrelated user work;
- provenance and review of dependency and provider updates; and
- explicit authorization for commit, push, publication, deployment, or other externally visible changes.

Repository instructions restrict branch switching and Git history-changing operations without authorization. This task does not perform those operations.

No Software Bill of Materials, signed-build process, scanning pipeline, dependency-verification service, or verified supply-chain control is established by this document. Such mechanisms must not be claimed without direct evidence.

## 13. Observability, Auditability, and Evidence

The intended traceability chain is:

`User → Task → Module/AGI → Agent → Workflow → Tool → Model → Result → Verification → Memory`

This chain is a target, not proof of an implemented end-to-end trace or audit service. Where approved mechanisms support it, evidence should make it possible to investigate:

- who or what initiated an action;
- the applicable task, scope, identity, permissions, and policies;
- relevant human approvals and their scope;
- module, agent, workflow, tool, and provider participation;
- data and context provenance;
- execution outcomes, side effects, and security-relevant failures;
- verification and capability-status evidence; and
- authorized memory or configuration changes.

Distinguish:

- event generation from trace collection;
- trace collection from persistent audit storage;
- monitoring from incident response; and
- evidence availability from completeness, correctness, or approval.

Audit records should minimize sensitive content and use references or sanitized metadata where feasible. Logging policies, retention, access control, monitoring, and incident-response ownership remain unresolved. No such end-to-end capabilities are claimed as implemented.

## 14. Failure Handling and Incident Boundaries

The architecture should distinguish and report security-relevant failures:

| Condition | Proposed response consideration |
|---|---|
| Authorization failure | Deny or stop the affected operation; do not retry through a broader identity or scope |
| Policy conflict | Preserve the conflict and stop dependent work until the controlling authority is clear |
| Suspicious external content | Treat as untrusted data, avoid executing embedded instructions, and limit propagation |
| Credential exposure | Stop further disclosure and follow a separately approved credential response process; no specific response authority is established here |
| Provider or tool compromise | Suspend or isolate affected use where an authorized mechanism exists; report evidence and limits |
| Invalid or unverifiable result | Mark as unverified, blocked, or failed as evidence supports; do not present as accepted |
| Unapproved consequential action | Stop before execution when possible; report observed state and do not conceal partial side effects |
| Partial workflow failure | Separate completed, failed, pending, and blocked work |
| Security dependency unavailable | Fail closed for operations that require its decision, unless an explicitly approved safe degraded mode exists |

Fail-closed versus controlled degraded behavior depends on operation sensitivity and risk and remains a design decision. No incident response procedure, response-time guarantee, automated containment mechanism, recovery objective, or universal degraded-mode policy is established here.

## 15. Relationship to Existing Architecture

| Document | Security/governance relationship |
|---|---|
| [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) | Governs architecture authority, proposal classification, and approval evidence. |
| [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md) | Establishes product identity, provider neutrality, evidence boundaries, and the separation from SUPER AGI runtime. |
| [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) | Defines platform, runtime, provider, tool, human authority, data, and repository boundaries. |
| [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md) | Describes a proposed layer structure; only the endpoint boundaries are established, and the full layer map is not approved. |
| [`FIVE-PLANES.md`](FIVE-PLANES.md) | Establishes the five plane names; security and Control responsibilities are cross-cutting and do not establish deployment topology. |
| [`MASTER-CORE.md`](MASTER-CORE.md) | Describes proposed coordination and human-control boundaries; no operational enforcement is demonstrated. |
| [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) | Describes proposed shared infrastructure; component security and deployment boundaries remain unresolved. |
| [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) | Describes proposed context handling; the scope hierarchy and enforcement remain unresolved. |
| [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) | Proposes module identity and status metadata; registry membership is not permission. |
| [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md) | Proposes module responsibilities, dependencies, and permission expectations; no runtime validation is established. |
| [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md) | Describes proposed collaboration; cross-module authorization and trust enforcement remain unresolved. |
| [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md) | Describes proposed provider boundary, data disclosure, credential, fallback, and output-trust requirements. |
| [`SECURITY.md`](../SECURITY.md) | Defines repository security expectations and reporting limitations; it does not prove runtime security enforcement. |

No definitive plane-to-layer mapping, security-component deployment topology, or cross-system authorization boundary is established by this document.

## 16. Capability Status and Implementation Boundary

Use the repository's capability-status vocabulary:

- `IMPLEMENTED`
- `ADAPTER-READY`
- `MOCKED`
- `EXPERIMENTAL`
- `NOT IMPLEMENTED`
- `BLOCKED`
- `UNKNOWN`

A security requirement described in a document does not prove that a corresponding control is implemented or effective. Status must be assigned only at the capability scope supported by direct implementation and verification evidence.

Creating this document does not implement or establish:

- authentication, authorization, or policy enforcement;
- credential or secret management;
- module, tenant, or context isolation;
- threat detection, prompt-injection prevention, or sandboxing;
- persistent audit logging, monitoring, or incident response;
- provider, model, or tool security integrations; or
- deployment and release controls.

No formal security certification, compliance status, complete safety guarantee, or functioning governance process is claimed.

## 17. Dependencies and Open Decisions

Important unresolved decisions include:

- architecture, security, and approval authority;
- identity and authentication integration;
- authorization and permission representation and enforcement;
- module, user, organization, project, and tenant isolation;
- data classification, retention, deletion, and provenance;
- provider eligibility and data-sharing restrictions;
- human approval boundaries and evidence;
- tool and agent permission enforcement;
- secret and credential management;
- security event collection, audit access, and retention;
- incident response responsibility and escalation;
- supply-chain security requirements and evidence; and
- approval and deployment governance for architecture and capability changes.

`ARCHITECTURE-DECISIONS.md` and `OPEN-DECISIONS.md` are absent from the repository. No available source establishes a general approving authority or resolves the decisions listed above. The existing M1 approval pin applies only to its exact repository-audit specification revision.

No material conflict was identified among the available required architecture sources. Their common limitation is that runtime controls, identity models, enforcement mechanisms, incident processes, and approval authority remain unimplemented or unresolved.

## 18. Implementation Boundary

This document defines proposed security and governance architecture only. It does not establish operational security controls, formal compliance, verified system safety, or a functioning governance process.

Implementation of authentication, authorization, policy enforcement, secret management, isolation, auditing, threat detection, sandboxing, incident response, and deployment controls requires separate bounded tasks, explicit authority, and direct evidence. This document does not authorize those tasks or claim that SUPER AGI has been achieved or that its 100 modules are operational.

## Related Architecture Documents

Existing documents:

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
- [`SECURITY.md`](../SECURITY.md)

Planned targets absent from the repository:

- `architecture/ARCHITECTURE-DECISIONS.md`
- `architecture/OPEN-DECISIONS.md`

This document does not amend or approve any referenced architecture material.

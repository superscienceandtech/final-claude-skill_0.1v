# Model Gateway and Routing Architecture

## 1. Document Identity and Status

This document defines the proposed provider-neutral model access and routing boundary for the intended SUPER AGI target system. It is intended for architecture and integration planning, module and adapter design, and future implementation scoping. It describes responsibilities and information needs without defining a finalized schema, API, protocol, routing algorithm, or deployment topology.

The document is subordinate to [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), which defines architecture authority and document classification. It is intended to remain consistent with [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`FIVE-PLANES.md`](FIVE-PLANES.md), [`MASTER-CORE.md`](MASTER-CORE.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), and [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md).

The foundational product principle is:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

The 100 modules are specialized domains within one intended unified system, not 100 independent AI products. The `claude-skills` repository is the provider-neutral engineering platform used to build and maintain the separate SUPER AGI target. It is not the SUPER AGI runtime.

Status distinctions:

- **Established:** provider neutrality, separation of the engineering platform from the SUPER AGI target, human control for consequential actions, and evidence-based capability claims.
- **Proposed:** the gateway boundary, provider-neutral request/response concepts, model capability representation, and routing responsibilities described here.
- **Unresolved:** request and response schemas, model/provider identity, catalog ownership, selection policy, adapter lifecycle, credential integration, data disclosure policy, retries/fallback, evaluation, and operational governance.
- **Not implemented or unknown:** no operational SUPER AGI Model Gateway, universal model router, or complete provider adapter and model-routing runtime is demonstrated by the reviewed architecture documents.

This document is an architecture proposal. It does not formally approve the proposed design or establish that a gateway, router, provider integration, or model connection operates.

## 2. Purpose and Design Principles

A shared Model Gateway is intended to separate canonical model-access requirements from provider-specific APIs and behaviors. In a unified multi-module system, this boundary could allow modules to request model capabilities consistently while preserving provider independence, policy constraints, and traceable outcomes.

Proposed design principles:

1. **Provider neutrality:** modules and canonical architecture express capability needs without depending on a particular model vendor or API.
2. **Model/provider abstraction:** isolate provider-specific request and response translation behind explicit adapter boundaries.
3. **Consistent access boundaries:** model invocation follows explicit task scope, permissions, and data-disclosure requirements.
4. **Module-specific requirements:** model selection considers the requesting module's declared capability needs and constraints.
5. **Policy separation:** model routing policy is distinct from domain reasoning and from Master Core's broader task orchestration.
6. **Credential isolation:** credential use and provider account scope belong to controlled provider-specific boundaries, not module declarations or user-generated prompts.
7. **Failure visibility:** unavailable or unsupported behavior, errors, refusals, partial responses, and fallbacks must be reported honestly.
8. **Observability and provenance:** preserve request, selected provider/model, adapter, result, and verification references where approved mechanisms support them.
9. **Security and human control:** model availability does not grant permission to disclose sensitive context or perform consequential actions.
10. **Extensibility:** new providers may be added through separately reviewed adapters without changing canonical module semantics.

These are architectural goals, not evidence that the corresponding controls or integrations are implemented.

## 3. Conceptual Architecture and Boundaries

The following are responsibility boundaries and do not require distinct services or processes:

| Responsibility | Proposed role | Boundary |
|---|---|---|
| Master Core | Establish task scope, coordinate orchestration, and request model capability where needed | Does not itself become a provider API, credential store, or model execution environment |
| Universal Intelligence Router | May coordinate intelligence- or module-level capability selection | Broader module routing is distinct from selecting a model/provider; its ownership relative to gateway policy remains unresolved |
| Model Gateway | Accept provider-neutral requests, apply approved gateway constraints, mediate adapter use, and return normalized results and evidence | Does not own domain reasoning, canonical architecture, human approval, or provider credentials by implication |
| Model/provider adapter | Translate canonical requests and results to/from a specific provider's behavior | Provider-specific; existence, compatibility, authentication, and operation must be evidenced independently |
| Model catalog or capability registry | Describe provider/model identity and declared or evaluated capabilities | Metadata is not a guarantee of current availability, performance, or runtime behavior |
| Domain intelligence module | Declare task needs, capability requirements, inputs, outputs, and restrictions | Does not select a model by undocumented assumptions or receive provider permissions from registry presence |
| Agents and workflows | Coordinate bounded execution and may request model-assisted work | Workflow or agent definitions do not themselves authorize external transmission or model invocation |
| External model provider | Executes a provider-specific request and returns provider output | External trust boundary; processing, retention, availability, and capabilities require evidence and policy review |
| Tool infrastructure | Provides separate tool discovery and invocation boundaries | Model tool-use support does not grant tool permissions or establish tool readiness |
| Context, knowledge, memory, and World Model | May supply authorized information or references for a model request | Each remains a distinct responsibility with separate access, provenance, and retention rules |
| Security, policy, evaluation, and observability | Constrain invocation, review results, and record evidence as supported | Must remain distinct from model selection; technical enforcement and service implementations are not demonstrated |

The conceptual lifecycle separates these decisions and actions:

1. **Decide whether model access is needed.** The task owner or authorized coordinator determines if a model capability is relevant.
2. **Select an appropriate model/provider.** A future routing policy may compare task requirements, declared capabilities, eligibility, and constraints.
3. **Translate the request.** A provider-specific adapter maps the provider-neutral request into the provider's interface.
4. **Execute the provider request.** The external or local provider performs model inference under its own availability and processing boundaries.
5. **Normalize the response.** The adapter/gateway maps results and errors into a provider-neutral representation without hiding limitations.
6. **Record provenance and usage evidence.** Record provider/model identity and execution metadata where available and authorized.
7. **Verify the returned result.** Apply separate task-appropriate validation; model selection and successful execution do not establish correctness.

The ordering is conceptual. The repository does not establish an executable pipeline or exact ownership for these steps.

## 4. Provider-Neutral Model Contract

The following request and response elements are proposed information needs only. They are not an approved schema, API, serialization format, or source-code interface.

### Potential request information

- request or operation reference;
- requesting module, agent, or workflow identity;
- task category and bounded objective;
- required and optional capabilities;
- authorized input data and context references, including provenance where available;
- output constraints and validation expectations;
- applicable policy, permission, and approval references;
- resource or latency constraints, if required by future contracts;
- explicit provider/model inclusion or exclusion constraints;
- permitted fallback constraints; and
- trace correlation reference, if supported.

### Potential response information

- originating request reference;
- provider and adapter identifiers;
- model identifier and version, when available;
- normalized result or explicit empty/partial result;
- completion or failure state;
- usage information, when available and authorized;
- error, refusal, limitation, or unsupported-capability details;
- provenance and material transformation metadata; and
- verification status and limitations, kept distinct from provider completion.

The required fields, stable identity conventions, data types, error taxonomy, and compatibility rules remain unresolved. No separate schema file is created by this document.

## 5. Model Capability Representation

A future capability model may describe requirements such as:

- general text reasoning;
- code generation or analysis;
- image or other multimodal input;
- audio input or output;
- structured output;
- long-context processing;
- tool-use support;
- embedding generation; and
- specialized domain tasks.

These are examples, not claims that a given provider or model supports them.

Capability evidence should distinguish:

1. **Provider-declared feature:** the provider documents or advertises a feature.
2. **Configured metadata:** repository configuration records a feature or constraint.
3. **Empirically evaluated performance:** a defined evaluation observed behavior on a stated task set and conditions.
4. **Verified runtime behavior:** an applicable environment demonstrated invocation and behavior with recorded evidence.

One evidence class does not automatically imply another. Declared capabilities may be stale or conditional; evaluation is bounded by its criteria and environment; successful invocation does not prove broad task competence.

Unresolved questions include the capability schema and granularity, evidence provenance and freshness, compatibility across adapter/model versions, evaluation coverage and thresholds, and how unavailable or unverified capabilities are represented.

## 6. Routing Responsibilities and Policies

The proposed gateway boundary may apply an approved routing policy using relevant inputs such as:

- capability matching against the task and module requirements;
- policy and permission eligibility;
- provider/model availability and compatibility evidence;
- task-specific constraints and required output behavior;
- authorized user or organization configuration;
- explicit provider/model restrictions;
- resource, cost, or latency constraints where specified;
- reliability evidence and known limitations; and
- fallback eligibility and data-sharing restrictions.

Routing policy must not be conflated with:

- **domain reasoning**, which determines what the task means and what answer is appropriate; or
- **Master Core orchestration**, which coordinates task boundaries, modules, agents, tools, workflows, and completion evidence.

The existence of a model catalog or a provider preference does not authorize selection, data disclosure, or tool execution. No routing algorithm, ranking formula, scoring weight, default provider preference, or mandatory fallback order is established by this document. Those decisions require explicit contracts and approval.

## 7. Provider Adapters and Extensibility

The provider-neutral gateway should interact with provider-specific behavior through explicit adapter boundaries. A future adapter may be responsible for:

- translating canonical requests into provider-specific request formats;
- using authentication mechanisms supplied through separately approved configuration;
- expressing provider-specific parameters without changing canonical semantics;
- normalizing responses and translating provider errors;
- exposing capability and model metadata with source and freshness;
- reporting usage metadata where available;
- reporting rate limits and availability where supported; and
- documenting unsupported operations, compatibility limitations, and data handling.

Adapter declarations are not implementation or readiness evidence. The repository does not establish installed credentials, connected provider accounts, working endpoints, or operational model-provider integrations. Provider-specific authentication and data processing remain separate security and compatibility concerns.

Provider extensibility must preserve one canonical contract source and avoid provider-specific forks silently changing module behavior. Adapter lifecycle, certification, versioning, and compatibility evidence remain unresolved.

## 8. Failure Handling and Fallback

The architecture should make the following conditions distinguishable:

| Condition | Intended reporting |
|---|---|
| Provider unavailable | Identify the unavailable dependency and report whether work stopped or was explicitly degraded |
| Rate limited | Report the provider response and do not claim a successful completion |
| Authentication failure | Stop the affected request; do not expose credentials or silently retry with another identity |
| Unsupported capability | Report the mismatch and do not represent the model as suitable |
| Invalid request | Report a request/contract problem where it can be safely identified |
| Timeout | Report incomplete or unknown execution state; timeout duration is not defined here |
| Malformed response | Reject or qualify it according to a future contract; preserve safe error evidence |
| Partial or empty response | Distinguish partial/empty output from successful task completion |
| Policy rejection | Stop the affected dispatch and report the policy or approval dependency without disclosing sensitive details |
| Model refusal | Preserve the refusal as a model outcome; do not rewrite it as a successful answer |
| Verification failure | Report failure separately from provider execution success |
| Fallback provider unavailable | Report fallback failure and preserve the original failure state |

These concepts are distinct:

- **Retry:** reattempt the same logical operation under a future-defined retry policy.
- **Fallback:** select another eligible provider/model only when policy, permissions, compatibility, and data-sharing rules allow it.
- **Cancellation:** stop work and report its execution state.
- **Degraded completion:** return a limited result with explicit capability and verification limitations.
- **Escalation:** request human or governance direction when requirements, permissions, or safe behavior cannot be established.

Retry counts, timeout policies, idempotency, fallback authorization, partial-result acceptance, and recovery semantics are unresolved. Sensitive input must not be sent to a different provider automatically merely because the first provider failed.

## 9. Security, Privacy, and Credential Boundaries

The proposed gateway architecture should observe:

- **Credential isolation:** keep credentials and account scope within separately authorized provider-specific mechanisms; do not expose secrets in module contracts, prompts, logs, or results.
- **Least privilege:** invoke only the provider capability required for the scoped task.
- **Data disclosure review:** identify what data is sent to which provider and under what authorization.
- **Context minimization:** send only relevant, permitted inputs and context.
- **Sensitive information handling:** apply governing classification, redaction, and disclosure requirements; exact mechanisms remain unresolved.
- **Untrusted model output:** validate output before treating it as evidence or using it to trigger actions.
- **Prompt injection:** treat external and retrieved instructions as untrusted data; do not allow them to expand permissions or override governing policy.
- **Provider retention and processing:** document and assess provider handling where evidence is available; no retention or deletion guarantee is assumed.
- **Policy enforcement:** consult applicable security and permission governance; the gateway specification itself is not an enforcement mechanism.
- **Human approval:** require explicit approval for consequential actions under repository policy. A model response is never approval.
- **Auditability:** record relevant request, decision, provider, result, and failure references where an approved mechanism exists, minimizing sensitive content.

The gateway may enforce only those authorization checks delegated to it by approved contracts. Identity, policy authority, approval workflow, credential manager, secret store, compliance certification, and security enforcement implementation are not established here.

## 10. Context and Data Flow

Model requests may consume authorized references or selected content from:

- **Universal Context:** operation-scoped context under the proposed context architecture.
- **Memory:** retained information subject to separate read/write, retention, and deletion rules.
- **Knowledge:** structured or curated sources with provenance and access rules.
- **World Model:** a proposed representation whose scope and update semantics remain unresolved.
- **Domain modules and agents:** task-specific inputs or prior outputs subject to their own contracts.

These concepts remain distinct and are not a generic storage layer. The proposed hierarchy is:

`Global → Organization → User → Project → Domain → Task → Agent`

As stated in [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), this hierarchy is **proposed, not approved**. Inheritance, visibility, merge behavior, and override rules remain unresolved.

Before external transmission, the intended architecture should limit provider input to authorized and relevant information, preserve provenance and material transformations where available, and prevent implicit cross-domain disclosure. Internal context and provider-transmitted context are not necessarily identical.

No context assembly algorithm, serialization format, provider data-retention guarantee, or propagation implementation is established. Provider-specific context adaptation must not silently broaden permission or alter canonical meaning.

## 11. Evaluation and Verification

Model routing and evaluation are related but separate responsibilities. A routing decision may depend on capability evidence; evaluation can assess whether a model or adapter meets specified expectations. Neither selection nor evaluation alone proves that a particular result is correct.

Future evidence may include:

- source and version of provider/model capability claims;
- compatibility behavior for the canonical request contract;
- task-appropriate evaluation criteria and recorded conditions;
- output validation results;
- provenance for material claims;
- regression evidence where relevant;
- uncertainty, limitations, and unsupported cases; and
- the boundary between provider execution, independent verification, approval, and deployment.

The repository does not establish live model evaluations, benchmark suites, or an automatic verification pipeline for this gateway. Evaluation criteria, independence, acceptance thresholds, test data governance, and result publication authority remain unresolved.

## 12. Observability and Usage Evidence

Where supported by an approved mechanism, the gateway's trace should allow investigation of:

- initiating task and operation reference;
- requesting module, agent, or workflow;
- routing decision and its permitted explanation;
- selected provider and model, including version when available;
- adapter used;
- execution, refusal, partial, cancellation, and failure status;
- retries or fallback events, if authorized;
- usage metadata when available and permitted;
- returned result reference and provenance; and
- verification status and limitations.

The broader target trace is:

`User → Task → Module/AGI → Agent → Workflow → Tool → Model → Result → Verification → Memory`

This is an architectural target, not proof of end-to-end tracing or persistent usage records. Logging must not expose credentials or unnecessarily duplicate sensitive prompts and context. Log content, access, retention, metrics, privacy controls, and trace storage are unresolved.

## 13. Relationships to Existing Architecture

| Document | Relationship |
|---|---|
| [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) | Governs architecture authority and proposal/approval distinctions. |
| [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md) | Establishes product identity, provider neutrality, and the distinction between the platform and SUPER AGI. |
| [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) | Defines provider, tool, human authority, data, and SUPER AGI runtime boundaries. |
| [`FIVE-PLANES.md`](FIVE-PLANES.md) | Establishes the five plane names; gateway placement across planes remains unresolved. |
| [`MASTER-CORE.md`](MASTER-CORE.md) | Describes proposed coordination responsibilities; gateway dispatch interfaces are not established. |
| [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md) | Describes the proposed Model Gateway and Model Routing component; implementation and boundaries remain unresolved. |
| [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md) | Describes proposed context scope and handling; the hierarchy is not approved. |
| [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) | Proposes module identity and capability metadata, without an operational model catalog or module registry service. |
| [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md) | Proposes module capability, input/output, dependency, and evidence expectations; no runtime interface is established. |
| [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md) | Describes proposed module collaboration; model selection and provider access remain distinct concerns. |

These relationships are conceptual. No definitive plane-to-component or plane-to-layer mapping is established here.

## 14. Capability Status and Implementation Boundary

Use the repository's canonical capability-status vocabulary:

- `IMPLEMENTED`
- `ADAPTER-READY`
- `MOCKED`
- `EXPERIMENTAL`
- `NOT IMPLEMENTED`
- `BLOCKED`
- `UNKNOWN`

Do not assign `IMPLEMENTED` merely because this document or another architecture document describes a component. A narrower repository artifact must be assessed at its actual scope and cannot be generalized to an operational SUPER AGI gateway.

Creating this document does not implement:

- a Model Gateway or Universal Intelligence Router;
- a model catalog or capability registry;
- provider adapters, credentials, accounts, or working endpoints;
- routing policy, model selection, or fallback execution;
- request/response APIs, schemas, or protocols;
- context filtering or data-disclosure enforcement;
- evaluation or verification pipelines; or
- persistent observability or usage accounting.

No evidence in this document establishes that all providers, models, or 100 modules are connected or operational.

## 15. Dependencies and Open Decisions

The proposed gateway depends conceptually on:

- provider-neutral module and request requirements;
- model/provider identity and capability metadata;
- adapter contracts and compatibility evidence;
- approved credential and authentication boundaries;
- context, data-classification, and disclosure policy;
- routing eligibility and module/task constraints;
- failure, fallback, cancellation, and result contracts;
- evaluation, verification, observability, and evidence mechanisms; and
- security, human approval, and architecture governance.

Unresolved decisions include:

- request and response contract, including error and refusal representation;
- model and provider identity conventions;
- capability representation and evidence freshness;
- catalog ownership and metadata lifecycle;
- routing policy, selection criteria, and permitted explanations;
- adapter lifecycle, compatibility, and retirement;
- credential integration and account boundary;
- provider eligibility and data-sharing restrictions;
- retry, idempotency, timeout, cancellation, fallback, and partial-result policies;
- usage and cost accounting;
- evaluation, verification, and acceptance requirements;
- observability, privacy, access, and retention;
- plane and component ownership; and
- governance and architecture approval authority.

`ARCHITECTURE-DECISIONS.md` and `OPEN-DECISIONS.md` are absent from the repository. No source establishes these decisions as approved. The narrow M1 specification approval pin applies only to its exact repository-audit specification revision and does not approve this gateway architecture or its implementation.

No material conflict was identified among the available architecture documents. The main limitation is that provider-neutral model access, routing, adapters, and evaluation remain proposed or unresolved rather than demonstrated as an operational SUPER AGI capability.

## 16. Implementation Boundary

This document defines proposed architecture responsibilities only. It does not implement a gateway, router, model catalog, adapter, routing logic, provider configuration, credential integration, evaluation pipeline, or operational monitoring.

Future work on contracts, adapters, routing, configuration, credentials, evaluation, security controls, and monitoring requires separate bounded authorization and supporting evidence. This document does not approve unresolved choices, claim provider/model availability, establish module connectivity, or claim that SUPER AGI has been achieved.

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

Planned targets absent from the repository:

- `architecture/ARCHITECTURE-DECISIONS.md`
- `architecture/OPEN-DECISIONS.md`

This document does not amend or approve any referenced architecture material.

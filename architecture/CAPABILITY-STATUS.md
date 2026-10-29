# Capability Status and Evidence Architecture

## 1. Document Identity and Authority

This document defines the intended method for describing the implementation status and supporting evidence of capabilities in the `claude-skills` engineering platform and the separate future SUPER AGI system. It is intended for engineers, architects, maintainers, reviewers, evaluators, and AI coding agents who make or report capability claims.

The document defines a shared vocabulary and evidence principles. It does not create an operational capability registry, approve architecture, authorize implementation, or establish that a named capability works. Under [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), a document's presence does not itself make its contents approved. This document must therefore be treated according to its recorded approval evidence; no approval is inferred here.

The platform and target-system boundary remains:

> One Super AGI → One Unified Brain → 100 Major AGI Intelligence Modules → 100 Dedicated Navbars/Workspaces → Shared Universal Infrastructure.

The 100 modules are specialized domains within one intended unified system, not 100 independent AI products. The `claude-skills` repository is the provider-neutral engineering platform for building, governing, validating, and maintaining SUPER AGI; it is not the SUPER AGI runtime.

Authority and relationships:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) governs architecture authority, proposal classification, and the canonical status vocabulary.
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md) establishes product intent, provider neutrality, and evidence-based capability claims.
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) distinguishes design, specification, implementation, execution, validation, evaluation, approval, and operational readiness.
- [`MASTER-CORE.md`](MASTER-CORE.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md), [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md), and [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md) describe related architecture concepts and boundaries. Their presence does not prove implementation or approval.
- [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) and [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) exist as companion documentation: the former records decision outcomes and evidence boundaries, while the latter tracks unresolved questions and pending choices. Their existence does not establish that a proposal is approved, a decision is resolved, or a capability is implemented or operational.

## 2. Capability Definition and Scope

A **capability** is a bounded behavior or outcome that a named subject is intended or claimed to provide. It should be specific enough to identify what behavior is under discussion and what evidence would support the claim. A broad product or system claim should be decomposed into bounded capabilities where the evidence supports that distinction.

Possible capability subjects include:

- architecture components and shared infrastructure;
- Skills, agent roles, and handoff behavior;
- provider adapters and Model Gateway functions;
- tool integrations and their individual operations;
- workflows and orchestration;
- registries and discovery mechanisms;
- context, memory, knowledge, and World Model mechanisms;
- cross-module collaboration;
- security, authorization, governance, and audit controls;
- evaluation and verification mechanisms; and
- planned SUPER AGI domain modules.

These are examples of subjects, not claims that they exist or operate.

Keep the following states conceptually separate:

| State or artifact | Meaning |
|---|---|
| Documented design | Architecture intent, proposal, or descriptive documentation for expected behavior |
| Declared capability | A registry, contract, manifest, Skill, agent, or other declaration that a subject is intended to provide behavior |
| Implementation artifact | Source code, configuration, executable, or other material intended to realize behavior |
| Executable integration | A component that can be invoked in a stated environment with required dependencies, permissions, and configuration |
| Evidenced operational capability | A bounded behavior observed and supported by evidence in the stated environment and scope |

These are descriptive distinctions, not additional capability-status labels. A capability status summarizes evidence about a clearly identified scope; it does not replace the artifact's lifecycle, approval, compatibility, security, or deployment information.

## 3. Canonical Capability Status Vocabulary

Use only the following established status labels, with their existing meanings from [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md):

| Status | Established meaning | Evidence expectations and limitations |
|---|---|---|
| `IMPLEMENTED` | Concrete implementation exists and sufficient behavior evidence supports it. | Identify the behavior and scope actually supported. This does not by itself establish complete workflow operation, approval, compatibility, security enforcement, or production readiness. |
| `ADAPTER-READY` | A usable adapter boundary exists without demonstrated full runtime behavior. | Evidence should support the usability of the boundary for its stated scope. It does not establish a working external provider or tool, valid credentials, authentication, authorization, compatibility, or end-to-end operation. Documentation alone is not a usable boundary. |
| `MOCKED` | Behavior is simulated by a stub or replacement. | Identify the simulated behavior and what the mock does not exercise. Mock success is not evidence that the replaced dependency or real integration works. |
| `EXPERIMENTAL` | Implementation exists but is incomplete or limited in validation. | Identify the exploratory scope, preconditions, limitations, and validation gaps. Do not imply general availability, robustness, or production suitability. |
| `NOT IMPLEMENTED` | Required functionality is absent or only placeholder/proposal content. | Use when available evidence establishes absence or only a design/placeholder for the required behavior. Do not use solely because the evidence was not inspected; that may be `UNKNOWN`. |
| `BLOCKED` | Implementation or validation is stopped by a recorded prerequisite. | Identify the blocking prerequisite and its evidence. Do not imply that the capability is implemented or validated while blocked. |
| `UNKNOWN` | Available evidence is insufficient for a stronger status. | State what is unknown and what evidence would resolve it where practical. Unknown is not evidence of failure, absence, or success. |

The definitions above preserve the canonical vocabulary and meanings. Where a capability spans different scopes or the available evidence does not fit cleanly, report the exact scope, basis, limitations, and ambiguity rather than inventing a new status or silently changing a definition.

The status is not a lifecycle state, approval state, release state, test result, provider-compatibility result, security classification, or readiness score. Supplementary information may describe those separately, but must not be presented as additional canonical capability statuses.

## 4. Status Interpretation Rules

Apply the following distinctions when assessing claims:

- A design document describes intent; it is not an implementation.
- A source artifact shows that implementation material exists; it does not by itself demonstrate usable or correct behavior.
- A provider-neutral interface defines a boundary; it does not demonstrate a functioning provider adapter.
- An adapter boundary may be `ADAPTER-READY` without demonstrating full runtime behavior.
- A mock demonstrates simulated behavior only, not the real dependency or integration.
- An experimental implementation may work in a narrow case while remaining incomplete or insufficiently validated.
- A blocked capability has an identified prerequisite stopping implementation or validation; an unknown capability lacks sufficient evidence to make a stronger claim.
- A locally functioning component does not prove that dependencies, permissions, configuration, or an end-to-end workflow function together.
- A declared model capability, model card, routing rule, or provider claim is not independent evidence of task performance.
- A planned module, registry entry, workspace, or contract is not an implemented module.
- A skill or agent definition does not demonstrate successful or authorized execution.
- A security policy documents an expectation; it does not prove that a control is technically enforced.

Repository presence, path names, comments, examples, generated documentation, declarations, and agent assertions may help locate evidence but are not sufficient on their own to establish operational behavior. Successful compilation or one passing check also supports only the property and scope that the check exercised.

Use the narrowest capability scope supported by evidence. Do not generalize a component-level observation to an entire product, workflow, provider ecosystem, or SUPER AGI system.

## 5. Evidence Model

Evidence should be linked to the claim it supports and should make its scope and limits reviewable. The following are **proposed conceptual evidence fields**, not an approved schema, mandatory file format, registry design, or storage system:

| Proposed field | Intended purpose |
|---|---|
| Capability identity | Identify the subject and bounded behavior; a canonical identifier convention remains unresolved |
| Status claim | Record one label from the canonical vocabulary |
| Implementation location or artifact reference | Point to relevant source, configuration, contract, executable, or other artifact when present |
| Evidence source | Identify the observed command, test, report, trace, review, or document and its provenance |
| Observation or collection time | Indicate when evidence was collected, if available |
| Verification scope | State what behavior, property, version, or integration path was actually checked |
| Preconditions and environment | Record relevant runtime, configuration, platform, credentials, permissions, or fixtures without exposing secrets |
| Dependency assumptions | Identify provider, tool, service, module, or infrastructure dependencies and their assumed state |
| Known limitations | Describe unsupported cases, partial behavior, uncertainty, or excluded scope |
| Failure conditions | Record observed failures and conditions that prevent the claim from holding |
| Evidence freshness | Indicate whether the evidence is current, stale, or not assessed, if that can be supported |
| Responsible actor or source | Identify the actor or source only where repository evidence establishes it |
| Related decisions and contracts | Link applicable specifications, approvals, or unresolved decisions |

Evidence references should not expose credentials or unnecessary sensitive data. This document does not define serialization, signatures, retention rules, access control, evidence ownership, or a method for authenticating evidence.

## 6. Evidence Strength and Limitations

Evidence sources support different kinds of claims. Their relevance depends on the capability and verification question:

| Evidence source | May support | Does not establish by itself |
|---|---|---|
| Architecture documentation | Intended responsibilities, boundaries, and proposed behavior | Implementation, approval, execution, or operational readiness |
| Source-code inspection | Presence and structure of an implementation artifact | Successful execution, correctness, integration, or deployment |
| Configuration inspection | Declared settings or a potential configuration path | Valid credentials, active permissions, provider connectivity, or runtime behavior |
| Dependency and environment information | Stated package, executable, platform, or environment prerequisites | That dependencies are installed, available, safe, or correctly configured in an actual run |
| Direct execution evidence | Behavior observed for a particular invocation and environment | Unobserved cases, complete integration, repeatability, approval, or production suitability |
| Integration behavior evidence | Observed interaction across a stated component boundary | Full workflow behavior, all provider/tool configurations, or independent correctness |
| End-to-end workflow evidence | A bounded workflow outcome under recorded conditions | Universal reliability, all paths, long-term operational performance, or untested environments |
| Evaluation or benchmark results | Performance against identified criteria, data, and conditions | General intelligence, correctness outside the evaluation scope, or approval |
| Security or authorization evidence | A specified control or authorization behavior under examined conditions | Complete security, absence of vulnerabilities, certification, or enforcement outside the tested boundary |
| Human acceptance or approval record | A documented decision by an identified authority within a stated scope | Technical correctness, successful implementation, or authorization beyond that scope |

Evidence supports only the behavior, versions, environment, dependencies, and conditions actually observed. A successful isolated adapter invocation does not prove that a multi-module workflow operates correctly. A test result does not itself approve a design or establish security. An approval record does not prove implementation. Evidence should be interpreted alongside failures, limitations, assumptions, and relevant changes since collection.

The presence of an evidence artifact is not a guarantee of its authenticity, completeness, independence, or continuing applicability. Do not claim that a particular evidence source exists unless it has been observed.

## 7. Status Assignment and Transition

Status assignment and updates are proposed to follow an evidence-driven review:

1. Define the bounded capability and its intended behavior.
2. Identify the applicable contract, dependencies, permissions, environment, and evidence available.
3. Assign the most accurate existing status supported by that evidence; record limitations and unresolved points.
4. Reassess the claim when implementation, behavior, dependencies, provider/tool versions, configuration assumptions, or validation evidence changes.
5. Withdraw or qualify a claim when evidence becomes stale, failures occur, or its assumptions no longer hold.

Interpretation for common cases:

- **Evidence absent:** use `UNKNOWN` when the available evidence is insufficient to determine implementation status. Use `NOT IMPLEMENTED` only when evidence supports that required behavior is absent or is represented only by a placeholder or proposal.
- **Implementation added:** do not automatically promote status. Evaluate behavior evidence for the capability's actual scope.
- **Integration failure:** report the observed failure and reassess the affected capability. Use `BLOCKED` when a recorded prerequisite prevents implementation or validation; otherwise use the status supported by the remaining evidence.
- **Dependency or provider change:** reassess dependent claims when a change invalidates prior assumptions or verification.
- **Evidence stale or applicability unclear:** qualify or withdraw the claim and reassess; no universal evidence expiration interval is established.
- **Experimental promotion:** require evidence appropriate to the broader scope before changing from `EXPERIMENTAL`; do not infer general usability from a narrow successful trial.
- **Regression or loss of function:** revise the claim to match current evidence and record the affected scope and failure.
- **Explicit blocker:** identify the prerequisite and its source; remove `BLOCKED` only when the blocker is resolved and relevant behavior is reassessed.
- **Insufficient evidence:** retain `UNKNOWN` rather than guessing.

The repository does not establish an automatic status-transition engine, mandatory reviewer, status approval authority, or release pipeline. Who may assign, approve, publish, or retain historical status records remains unresolved. Capability status, verification outcome, architectural approval, and deployment authorization must remain separately reported.

## 8. Capability Readiness and Dependency Boundaries

Capability status is scoped to the subject being assessed and its dependencies. Relevant dependencies may include:

- provider adapters, external tools, modules, workflows, and shared infrastructure;
- configuration, credentials, authentication, permissions, and network access;
- operating environment, installed dependencies, and runtime availability;
- module contracts and compatibility assumptions;
- orchestration and handoff behavior;
- security, privacy, and authorization controls; and
- validation, evaluation, and evidence-collection mechanisms.

A component-level status does not automatically transfer to dependent components. Dependency declarations do not establish that the dependency exists, is available, or is authorized.

Distinguish:

- **Component evidence:** behavior of one bounded component or interface.
- **Integration evidence:** observed behavior across specified dependency boundaries.
- **Workflow evidence:** behavior of the complete stated path, including relevant permissions, failures, and output handling.
- **System claim:** a broader claim that requires evidence covering the claimed system scope and its critical dependencies.

No dependency-resolution algorithm, readiness score, universal dependency closure rule, or system-level aggregation policy is established. A set of individually implemented components does not prove end-to-end operation.

## 9. Relationship to the Module Registry and Module Contract

[`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) describes a proposed inventory of module identity, responsibilities, dependencies, capabilities, evidence, and lifecycle metadata. [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md) describes proposed module responsibilities, interactions, and evidence expectations.

Keep these concepts distinct:

- **Module identity** identifies a module; it does not establish its implementation.
- **Declared responsibility or capability** states what a module is intended to provide; it does not establish observed behavior.
- **Implementation status** describes evidence for a bounded capability.
- **Demonstrated capability** is limited to the behavior supported by relevant execution and verification evidence.
- **Lifecycle and approval** are separate from capability status.

A future registry may reference capability status and supporting evidence, but storage, identifiers, schemas, update mechanisms, distribution, and authority are unresolved. This document does not create a registry, finalize its contract, or establish an authoritative list of 100 operational modules.

## 10. Application to Providers, Tools, Skills, Agents, and Workflows

Apply the vocabulary to the claimed behavior, not merely to the presence of a definition:

- **Model Gateway and provider adapters:** a provider-neutral interface or usable adapter boundary may support `ADAPTER-READY`; verified invocation requires evidence for the stated provider, model, environment, permissions, and behavior. It does not imply all providers are supported.
- **External tools:** a declaration or setup guide does not establish installation, discovery, authentication, authorization, or operation. Assess each tool and operation at its evidenced scope.
- **Skills:** a Skill definition is an instruction artifact, not proof of execution or successful outcome.
- **Agents:** an agent-role definition is not proof of an executing agent, its permissions, or correct handoffs.
- **Workflows and orchestration:** evidence for individual steps does not establish the whole workflow; end-to-end claims need evidence of the stated path and its dependencies.
- **Cross-AGI collaboration:** described collaboration patterns do not establish operational routing, context sharing, module coordination, or secure isolation.
- **Security and governance controls:** policy documentation is not evidence of technical enforcement, audit completeness, or security compliance.

`ADAPTER-READY` does not mean “verified working integration.” A usable boundary without demonstrated full runtime behavior is the source-of-truth meaning; configuration, credentials, permissions, actual invocation, compatibility, and integration behavior require their own evidence. Do not assume a tool is installed, configured, authenticated, or operational without direct, scope-appropriate observation.

## 11. SUPER AGI Claims and Scientific Honesty

Claims about SUPER AGI and its modules must distinguish:

| Claim level | Meaning and evidence boundary |
|---|---|
| Architectural intention | A documented target or design; not implementation evidence |
| Prototype capability | Limited implementation or experiment; disclose scope and incomplete validation |
| Narrow demonstrated functionality | Observed behavior under stated conditions; do not generalize beyond those conditions |
| Integrated system functionality | Evidence that the relevant components and dependencies work together across the claimed workflow |
| Evaluated performance | Results against stated criteria, conditions, and evaluation scope; not proof of capabilities outside that evaluation |
| Unresolved or speculative capability | A concept or claim without sufficient supporting evidence; identify uncertainty rather than imply achievement |

Names such as “AGI,” “World Model,” “Memory,” “Brain,” or “Self-Evolution” are not evidence that general intelligence, consciousness, autonomous self-improvement, or corresponding operational capabilities exist. Do not claim that SUPER AGI has been achieved, that all 100 modules are implemented, or that one component's evidence establishes full-system capability.

## 12. Security, Governance, and Approval Evidence

[`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md) describes proposed security, trust, and governance architecture. Capability reporting should distinguish:

- a security or governance policy being documented;
- a control being implemented;
- the control being exercised and verified within a stated boundary;
- a governance decision being explicitly approved by an identified authority; and
- a deployment being authorized for a defined environment and scope.

These are different claims. A policy document alone does not prove enforcement. A successful control test does not establish overall security, compliance, approval, or deployment authorization. A human approval record supports only its stated authority and scope. No approval authority or compliance certification should be invented or inferred.

Security-sensitive capability claims should identify relevant permissions, environment, data scope, failure behavior, and verification limits where evidence exists. No capability status by itself guarantees least privilege, safety, authorization, or auditability.

## 13. Reporting and Observability

Future engineering reports or operational observability systems may present the following separately:

- current capability status;
- supporting evidence and its provenance;
- known limitations and unsupported cases;
- dependencies and assumptions;
- blockers;
- verification scope and environment;
- last-observed behavior and evidence freshness, where known; and
- historical status changes, if such history is maintained.

These are reporting concepts, not proof that a dashboard, persistent status database, telemetry pipeline, evidence store, or automatic reporting system exists. Reports must not overstate the evidence or hide failures, partial work, unverified dependencies, or stale observations.

## 14. Implementation Boundary

This document establishes a shared status vocabulary reference and proposed evidence and reporting principles. It does not implement:

- a machine-readable capability registry;
- a capability or evidence schema;
- status-management tooling or automatic transitions;
- verification or evaluation automation;
- reporting or observability integrations;
- approval, audit, or publication mechanisms; or
- automated evidence freshness or expiration management.

Each requires separate authorization, design, implementation, and evidence. This document does not claim that the SUPER AGI runtime, its shared infrastructure, or its 100 modules are operational.

## 15. Dependencies and Open Decisions

The following decisions remain unresolved:

- canonical evidence schema and evidence provenance requirements;
- capability identity and granularity conventions;
- status assignment, transition, withdrawal, and review rules;
- evidence freshness, expiration, and invalidation;
- verification and evaluation authority;
- status approval and publication authority;
- registry storage, distribution, and update mechanisms;
- dependency-aware readiness and system-level aggregation;
- automated versus human status assignment;
- historical status and evidence retention; and
- reporting, observability, and integration mechanisms.

The planned targets `architecture/ARCHITECTURE-DECISIONS.md` and `architecture/OPEN-DECISIONS.md` are absent; no content or decisions are inferred from those paths. The available architecture material does not establish the authorities, schemas, or mechanisms listed above. The status vocabulary itself is established in [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), and related architecture documents; this document does not alter it.

## Related Architecture Documents

Available documents:

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

Planned targets absent from the repository:

- `architecture/ARCHITECTURE-DECISIONS.md`
- `architecture/OPEN-DECISIONS.md`

These references do not imply approval or implementation of the documents or capabilities they describe.

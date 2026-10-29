# Architecture Source of Truth

## 1. Purpose, Scope, and Authority

This document defines the documentation-level authority and conflict-resolution rules for the `claude-skill_sonjoy` engineering platform. It governs how repository contributors and agents identify canonical requirements, assess approval evidence, and report conflicts. It does not by itself approve the architecture described elsewhere, authorize implementation or execution, establish runtime behavior, or create an approval authority that repository evidence does not identify.

The platform is a provider-neutral Skills and engineering-orchestration platform for developing, governing, validating, and maintaining SUPER AGI. It is not the SUPER AGI runtime. The target-system principle is:

> One Super AGI — One Unified Brain — 100 Major AGI Intelligence Modules — 100 Dedicated Navbars/Workspaces — Shared Universal Infrastructure.

Those modules are intended domains within one unified system, not independent AI products. This repository does not establish that the target runtime, modules, or operational services exist.

The rules in this document govern interpretation and reporting. They do not retroactively approve a proposal, resolve an unresolved architecture decision, grant human authority, or prove that any rule is technically enforced. Where an applicable approval authority or required decision cannot be established, the decision remains unresolved and work that depends on it must not be presented as approved.

## 2. Authority Hierarchy

Authority is scoped. A higher-level source constrains lower-level material only within its explicit, approved scope. No artifact acquires authority merely by being newer, more detailed, executable, or stored in a particular directory.

Apply the following hierarchy:

1. **Repository operating and safety rules.** [`AGENTS.md`](../AGENTS.md) governs repository-wide agent conduct, scope, preservation, security, Git operations, and validation reporting. [`CLAUDE.md`](../CLAUDE.md) is Claude-specific entry guidance that points to `AGENTS.md`; [`CONTRIBUTING.md`](../CONTRIBUTING.md) governs contribution practice. These rules govern work in their stated scopes; they do not approve architecture or implementation claims.
2. **Product identity and non-negotiable boundaries.** [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md) describes product identity and principles; [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) distinguishes the engineering platform, providers, tools, and SUPER AGI runtime. Apply these as binding architectural requirements only to the extent their exact applicable revision has explicit approval evidence. Until then, they are product/architecture intent, not blanket approved architecture. The platform/runtime distinction and provider-neutral intent are also stated in repository instructions and must not be contradicted by implementation claims.
3. **Approved architecture decisions and constraints.** [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) and records under [`docs/architecture/decisions/`](../docs/architecture/decisions/) document decisions. An explicitly approved decision governs only its recorded scope, revision, and effect. It cannot silently override an approved product boundary. If the two appear inconsistent, stop and resolve the conflict; do not choose one implicitly.
4. **Approved system architecture.** [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`FIVE-PLANES.md`](FIVE-PLANES.md), [`MASTER-CORE.md`](MASTER-CORE.md), [`UNIVERSAL-INFRASTRUCTURE.md`](UNIVERSAL-INFRASTRUCTURE.md), [`UNIVERSAL-CONTEXT.md`](UNIVERSAL-CONTEXT.md), [`CROSS-AGI-COLLABORATION.md`](CROSS-AGI-COLLABORATION.md), [`MODEL-GATEWAY.md`](MODEL-GATEWAY.md), and related architecture documents define system structure only within their approved scope. Their presence does not establish that they are approved or implemented.
5. **Domain contracts and registries.** [`MODULE-CONTRACT.md`](MODULE-CONTRACT.md), [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md), [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md), [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md), and approved Skill, agent, provider, tool, or workflow contracts refine higher-level requirements. A registry is authoritative for the records it owns only when an approved higher-level rule identifies it as canonical. A registry entry is not evidence that the described capability works.
6. **Canonical Skills and operational definitions.** Provider-neutral Skills, agent-role definitions, provider adapters, tool integrations, and workflows implement or operationalize approved contracts. They may define bounded behavior within delegated scope; they may not independently redefine architecture or grant permissions.
7. **Templates, exports, generated artifacts, and supporting documentation.** These must identify or be traceable to their canonical source. Provider-specific copies may adapt syntax or format but must not redefine canonical semantics. Examples and supporting guidance are subordinate to their referenced contract.
8. **Implementation, verification, evaluation, and capability-status evidence.** These describe observed artifacts or behavior. Evidence informs status and decisions but does not itself approve requirements, alter architecture, or authorize execution or release.

The hierarchy does not create an automatic approval process. An approval claim is valid only when evidence identifies the approving authority, exact artifact or revision, scope, date or durable record, and authorized effect. If evidence does not establish that the authority was entitled to approve that scope, treat approval as unresolved.

## 3. Existing Governance Documents and Status

The following relationships apply to existing repository documents:

- [`AGENTS.md`](../AGENTS.md) is the primary agent instruction source for repository work. This document supplements it for architecture interpretation and must not conflict with its safety or scope rules.
- [`CLAUDE.md`](../CLAUDE.md) is an entry point for Claude-specific guidance and directs readers to `AGENTS.md`; it is not a parallel architecture authority.
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md) defines product intent and principles. It does not prove implementation or approval beyond explicit evidence.
- [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) is a decision register with proposed conventions and recorded evidence boundaries. Its statements about decision status and authority remain scoped to their cited evidence.
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md) defines intended responsibility and trust boundaries; it does not demonstrate operational enforcement.
- [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) defines capability-status and evidence semantics. It explicitly does not establish an operational status registry.
- [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) describes a proposed target-system module registry and states that an operational registry and authoritative 100-module portfolio are not established.
- [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md) describes security and governance intent; it does not establish runtime security enforcement.
- [`docs/architecture/`](../docs/architecture/) contains proposals, reviews, specifications, and decision records with their own recorded status. In particular, [`docs/architecture/decisions/m1-architecture-decisions.md`](../docs/architecture/decisions/m1-architecture-decisions.md) records pending matters as well as scoped Owner-accepted choices; neither it nor [`docs/architecture/decisions/m1-spec-approval-pin.md`](../docs/architecture/decisions/m1-spec-approval-pin.md) is blanket architecture, implementation, evaluation, integration, or release approval.
- [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) exists as the companion location for unresolved architecture questions. It records questions, not decisions or approvals.
- [`docs/architecture/implementation-roadmap.md`](../docs/architecture/implementation-roadmap.md) is a proposed staged roadmap. It does not authorize later milestones.

Each document's own status and approval evidence controls its treatment. References in this section describe responsibilities, not a blanket approval of the referenced documents.

## 4. Decision Lifecycle

Use the decision-record vocabulary already present in [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md). Do not introduce a competing lifecycle for decisions:

| Decision status | Meaning and permitted use |
|---|---|
| **Proposed** | A candidate outcome for review. It has no authority to change canonical requirements or authorize implementation beyond separately authorized exploration. |
| **Accepted** | An outcome explicitly accepted by an evidenced authority for a stated scope and revision. “Approved” may be used in prose to describe this state only when the acceptance evidence meets this document's requirements; do not create a second status label. |
| **Rejected** | The proposed outcome was explicitly rejected. It must not be treated as current policy within the rejection scope. |
| **Superseded** | A later accepted decision replaces the outcome within its recorded scope. Preserve the earlier record and link to the replacement. |
| **Deferred** | A decision is postponed or its prerequisite remains unresolved. It has no authority to resolve the question. Discussion in progress remains **Proposed** or **Deferred**; discussion alone is not approval. |

A status word alone is insufficient. Every accepted outcome must identify its decision, rationale, authority evidence, date or durable record, exact scope, affected sources, compatibility impact, and any separate implementation, evaluation, or release authorization. No such authorization is inferred from architecture acceptance.

## 5. Deterministic Conflict Resolution

When artifacts conflict, do not reconcile them by preference, recency, implementation behavior, or silent edits. Apply this procedure:

1. **Contain the scope.** Identify the specific claim, affected capability, artifacts, revisions, dependencies, and any action that would rely on the claim. Avoid consequential changes while authority is unclear.
2. **Classify each artifact.** Determine whether it is an operating rule, approved decision, approved architecture, proposal, contract, registry, canonical Skill, provider-specific copy, generated output, implementation, or evidence.
3. **Check authority and scope.** Verify explicit approval evidence, exact revision, approving authority, date/record, stated effect, and any supersession. An artifact outside its approved scope cannot resolve the conflict.
4. **Apply the hierarchy.** Enforce the higher applicable approved source. Lower-level artifacts must be corrected or explicitly marked as a deviation; they do not amend higher-level requirements.
5. **If no unique authority applies, stop.** Record the conflicting claims and evidence in [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md), or in the relevant existing issue/decision record when that is the established location. State what is blocked and request an authorized decision. Do not invent an approver or resolve a material conflict through implementation.
6. **After resolution, update traceability.** Update the accepted decision and affected canonical contracts; then update derived exports, implementation, and supporting documentation within separately authorized scope. Record verification actually performed.

Apply these specific rules:

- **Architecture documents:** An approved scoped decision governs a proposal. Two apparently approved, overlapping but inconsistent sources require scope and supersession analysis; if still conflicting, the matter is unresolved.
- **Contracts and registries:** The approved contract defines the permitted schema and semantics. A designated canonical registry supplies records only within the scope assigned to it. Contract/registry disagreement is invalid data or an unresolved governance issue, not permission to choose whichever is convenient.
- **Canonical Skills and provider copies:** The provider-neutral canonical Skill is authoritative for shared meaning. A provider copy may express provider syntax and document a limitation but cannot change canonical requirements. If no approved canonical Skill/source is designated, record the source-of-truth gap rather than selecting a copy implicitly.
- **Generated artifacts:** Generated material is derived, not authoritative. If it differs from its declared canonical source or generation inputs, treat it as stale/invalid, do not use it as a new source, and regenerate only under authorized procedures.
- **Stale documentation/status:** Compare the statement to current authority and evidence. Mark stale claims with a correction or link to the governing source; do not silently change a status or infer a new approval.
- **Unapproved proposals:** A proposal, draft, recommendation, roadmap, or discussion cannot override an accepted decision or establish a new requirement as approved.
- **Implementation conflicts:** Existing behavior is evidence of what the code currently does, not architecture approval. Record the observed behavior and the conflicting requirement. Do not edit architecture to ratify behavior, weaken validation, or claim conformance. Remediate or obtain an explicit, scoped architecture decision through authorized work.
- **Instruction conflicts:** `AGENTS.md` and applicable repository operating rules govern safe repository actions. If they conflict with an architecture document on architecture meaning, preserve safety and scope, stop the disputed change, and seek resolution; neither source silently rewrites the other.

## 6. Capability Status and Evidence Semantics

Keep design, declaration, implementation, observed behavior, evaluation, approval, and production readiness distinct:

1. **Documented intent** describes what should exist.
2. **Declared interface or registry entry** describes a contract or intended capability.
3. **Implementation artifact** is code or configuration intended to realize behavior.
4. **Verified behavior** is behavior actually checked by identified evidence within a defined scope.
5. **Operational readiness** requires applicable runtime, dependencies, permissions, integration, failure handling, and environment evidence.
6. **Approval and release** are separate human/governance decisions and must not be inferred from verification.

Use the canonical capability statuses defined in [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) and preserve its established spelling:

| Canonical status | Meaning |
|---|---|
| `IMPLEMENTED` | Concrete implementation exists and sufficient evidence supports the bounded behavior claimed. It does not by itself imply approval, complete integration, security enforcement, compatibility, or production readiness. |
| `ADAPTER-READY` | A usable adapter boundary exists, but full runtime behavior is not demonstrated. It does not prove a working provider/tool, credentials, authorization, compatibility, or end-to-end operation. |
| `MOCKED` | A stub or replacement simulates behavior. State which real dependency or behavior is not exercised. |
| `EXPERIMENTAL` | Implementation is limited or incompletely validated; identify scope and limitations. |
| `NOT IMPLEMENTED` | The required behavior is absent or only documented/proposed/placeholder. |
| `BLOCKED` | A recorded prerequisite prevents implementation or validation; name the blocker. |
| `UNKNOWN` | Available evidence is insufficient to make a stronger claim. Unknown is not success or proof of absence. |

`DOCUMENTED ONLY` may be used as a plain-language evidence description, not as a new canonical capability status. When a status is required and a requirement has documentation but no implementation, use `NOT IMPLEMENTED` and note “documented only” in the explanation. Likewise, `ADAPTER_READY` is not a new spelling; use canonical `ADAPTER-READY`.

The existence of a file, directory, class, function, interface, test definition, manifest, registry entry, or successful syntax diagnostic does not establish that the capability is operational. A security policy does not prove security enforcement; a provider-neutral interface does not prove provider compatibility; local or mocked execution does not prove external integration; and a passing component check does not prove end-to-end workflow readiness.

## 7. Minimum Evidence and Traceability

When reporting a capability as implemented, provide evidence proportionate to the claim. At minimum, record:

- capability identifier/name, bounded scope, and acceptance behavior;
- the applicable canonical requirement, contract, decision, and revision;
- the implementation location and relevant public symbol/configuration;
- dependencies, providers/tools, trust boundaries, permissions, and integration status;
- each validation actually performed, with exact command or procedure, environment/scope, and observed PASS/FAIL/SKIPPED/NOT RUN result;
- limitations, known failures, unresolved decisions, and blockers;
- which statements are observed facts versus estimates or assumptions.

For runtime, provider-compatibility, security-enforcement, or production-readiness claims, include evidence from the relevant environment and integration boundary. Source inspection, syntax checks, mocks, or test definitions alone are insufficient. Do not run checks merely to complete a report unless separately authorized.

For architecture decisions, retain the exact proposal and accepted outcome, authority evidence, scope, rationale, alternatives considered, consequences, affected contracts, supersession links, and separate implementation/evaluation/release state where applicable. A decision record must not claim tests passed unless results exist.

## 8. Architecture Evolution and Extensibility

Architecture changes are incremental and traceable. Add a capability only within an approved contract and scope; reuse shared provider-neutral concepts rather than creating a parallel platform for each provider or integration.

- **Skills and agent roles:** Define provider-neutral purpose, inputs, outputs, permissions, stop conditions, and evidence expectations in their canonical source. Add or revise provider-specific forms only as derived adaptations with traceable source revision and documented limitations.
- **Providers and tools:** Add a separate adapter/integration that implements an approved contract. Record supported and unsupported capabilities, data flow, permissions, errors, revocation behavior, and compatibility evidence. Do not embed vendor assumptions in canonical requirements.
- **Registries and contracts:** Extend the designated canonical schema and registry deliberately, with compatibility, migration, validation, ownership, and evidence impacts recorded. Do not infer registry authority from filenames or data presence.
- **Workflows:** Compose existing contracts and public APIs while preserving human approval, least privilege, bounded scope, failure visibility, and independent verification where required. A documented workflow is not an enforced gate.
- **IDE/provider-native surfaces:** Treat editor/provider rules, prompts, exports, agents, and settings as adapters or projections of canonical requirements. Do not duplicate or fork canonical meaning. If a target surface cannot express a requirement, disclose the limitation and retain the canonical rule.
- **Compatibility:** Preserve accepted decisions within scope. A breaking change requires impact analysis, an explicit authorized decision where required, migration guidance, and evidence; a new provider is not a reason to redefine existing canonical behavior.

Recommendations in this section guide future work; they do not authorize a new integration, provider, dependency, execution, or release. No automated synchronization, generation, compatibility enforcement, or approval gate is implied unless separately implemented and evidenced.

## 9. Current Repository Boundaries and Unresolved Matters

The repository contains substantial architecture and implementation artifacts, but this document does not assert that the full target architecture is approved, implemented, or operational. In particular:

- The architecture documents and roadmap must be interpreted according to their own status and applicable approval evidence.
- [`ARCHITECTURE-DECISIONS.md`](ARCHITECTURE-DECISIONS.md) records that general decision ownership, approval hierarchy, and conflict authority are unresolved. This document supplies a deterministic handling procedure but does not name or appoint an approval authority.
- [`CAPABILITY-STATUS.md`](CAPABILITY-STATUS.md) states that its vocabulary does not itself create an operational capability registry or status-management tooling.
- [`MODULE-REGISTRY.md`](MODULE-REGISTRY.md) describes the module registry as proposed and not implemented, and does not establish an authoritative operational 100-module portfolio.
- [`SECURITY-GOVERNANCE.md`](SECURITY-GOVERNANCE.md) does not establish runtime security enforcement or an operational governance service.
- Provider-specific surfaces, concrete provider adapters, external tool integrations, and execution-host readiness require their own implementation and evidence; this document creates none.
- The repository license remains unresolved as recorded in [`LICENSE`](../LICENSE).

When a decision depends on any unresolved authority, contract, scope, or approval, record the dependency and stop that decision-dependent work until appropriately authorized evidence exists. No later task or implementation phase is authorized by this document.

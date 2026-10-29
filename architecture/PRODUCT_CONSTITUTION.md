# Product Constitution

## 1. Purpose

This document defines the identity, mission, product boundaries, principles, intended scope, and long-term direction of the `claude-skills` repository.

It governs product-definition decisions for the engineering platform. It does not describe implementation behavior, approve an architecture proposal, or authorize a provider, tool, skill, agent, or integration merely because the capability is mentioned here.

The architecture authority and document-classification rules are established in [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md). That file is the entry point for canonical architecture documentation; this constitution supplies product intent and must remain subordinate to explicitly approved architecture decisions.

## 2. Product Identity

`claude-skills` is a provider-neutral, skill-driven, architecture-governed AI engineering platform. Its purpose is to help engineers design, implement, maintain, validate, and evolve complex software systems, including the SUPER AGI project, through reusable skills, specialized agent-role definitions, provider adapters, explicit tool integrations, controlled workflows, architecture governance, registries, templates, scripts, documentation, evaluation, and supporting engineering infrastructure.

The repository is not a completed AGI system and must not be described as autonomous, conscious, self-improving, or human-level intelligence without concrete evidence.

### System distinctions

- **`claude-skills`** is the repository and engineering platform. It provides governed methods and reusable infrastructure for software work.
- **SUPER AGI** is the separate target product or system that the engineering platform helps design and maintain. This repository does not itself become the target runtime.
- **AI providers** are external or locally available model and agent execution environments.
- **Tools** are external or local development utilities accessed through explicit repository-defined interfaces.

## 3. Mission

The mission of `claude-skills` is to make complex engineering work:

- reusable across repositories and provider environments;
- bounded by explicit scope and stopping conditions;
- governed by architecture and security decisions;
- traceable from requirement to implementation evidence;
- least-privilege in tool and provider access;
- reviewable by humans and independent verification processes; and
- honest about uncertainty, blocked work, unsupported capabilities, and unexecuted checks.

## 4. Vision and Long-Term Direction

The intended direction is a coherent provider-neutral engineering system that can package canonical engineering knowledge into provider-compatible skills and invoke specialized roles, approved tools, and controlled workflows without maintaining competing copies of the same architecture.

The platform should support the development of one unified SUPER AGI product organized around:

> One Super AGI — One Unified Brain — 100 Major AGI Intelligence Modules — 100 Dedicated Navbars/Workspaces — Shared Universal Infrastructure.

The 100 modules represent specialized intelligence domains within one unified system. They are not 100 independent AI products, and no claim about such a runtime is established by this constitution.

Future architecture and implementation should extend providers, tools, project domains, registries, templates, validation, evaluation, and controlled evolution only through explicit review and evidence. Long-term growth must not create divergent canonical copies or silently change the established product boundaries.

## 5. Target Users and Use Cases

The primary users are:

- software engineers using AI-assisted development environments;
- maintainers of complex repositories;
- architecture and integration leads;
- independent reviewers, evaluators, and security reviewers;
- provider-specific adapter maintainers;
- tool integration maintainers; and
- teams implementing bounded SUPER AGI engineering tasks.

Representative use cases include:

- translating a bounded requirement into a controlled implementation plan;
- preserving repository conventions and user work;
- applying reusable provider-neutral engineering skills;
- generating evidence-based implementation reports;
- mapping canonical behavior to supported provider formats;
- documenting tool permissions and failure boundaries;
- validating architecture, module, skill, workflow, and provider contracts;
- conducting repository audits and independent verification;
- tracking capability status and unresolved decisions; and
- recording controlled architecture evolution.

## 6. Product Scope

The product is intended to support the following capability areas, but listing a capability here does not mean it is implemented:

- provider-neutral reusable skills;
- specialized AI engineering roles;
- provider-specific adapters;
- integrations with development tools;
- bounded engineering workflows;
- architecture and decision governance;
- skill, agent, provider, tool, module, and capability registries;
- templates and supporting scripts;
- documentation and implementation evidence;
- structural validation and behavioral evaluation infrastructure;
- security and permission review;
- traceable controlled evolution; and
- future extension to additional providers, tools, and project domains.

The repository may contain specifications, proposal documents, framework code, test definitions, manifests, or documentation as separate implementation stages. Each artifact must be described according to observed evidence and must not be presented as a working capability without validation.

## 7. Explicit Non-Goals

This constitution does not imply or claim that:

- every planned repository component already exists;
- every available or installed tool is integrated, authenticated, or operational;
- provider adapters have been implemented;
- provider compatibility has been demonstrated;
- documentation proves runtime behavior or security enforcement;
- the repository guarantees correct, safe, complete, or autonomous outcomes;
- the repository itself is SUPER AGI;
- AGI, ASI, consciousness, or human-level intelligence has been achieved;
- an architecture proposal or evaluation package is approved without evidence;
- a future capability is available merely because it appears in a plan;
- canonical architecture documents replace implementation testing and review;
- one module or provider represents an independent AI product within the platform; or
- the platform may bypass human control for consequential actions.

## 8. Core Product Principles

### 8.1 Provider Neutrality

Canonical skills, architecture rules, workflow definitions, and engineering policies must not be unnecessarily coupled to one AI provider. Provider instructions and adapters consume canonical definitions and document unsupported capabilities explicitly rather than silently replacing canonical behavior.

### 8.2 Canonical Source of Truth

Architecture-document authority is governed by [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md). Canonical definitions, proposals, implementation specifications, implementation evidence, approval, and release status remain distinguishable.

Unresolved decisions must not be converted into approved decisions by documentation, implementation, or repeated recommendation.

### 8.3 Modular Engineering Architecture

The platform supports reusable skills, specialized roles, provider adapters, tool integrations, controlled workflows, registries, templates, and validation infrastructure. It does not assume that every planned component is implemented.

No additional mandatory top-level directory or architectural layer is introduced by this constitution. Future additions require explicit authority and compatibility review.

### 8.4 Explicit Capability Status

Capability claims must use the established status vocabulary:

- `IMPLEMENTED`
- `ADAPTER-READY`
- `MOCKED`
- `EXPERIMENTAL`
- `NOT IMPLEMENTED`
- `BLOCKED`
- `UNKNOWN`

A status must be supported by evidence appropriate to the claim. Presence of a file is not evidence of implementation or operational readiness.

### 8.5 Bounded Implementation Tasks

Implementation work must define an objective, authorized scope, exclusions, acceptance criteria, constraints, completion condition, and stopping point. A task must not automatically expand into dependent work.

### 8.6 Security and Human Control

The product requires least privilege, secret protection, explicit authorization for consequential actions, auditable operations, and controlled handling of untrusted instructions and external inputs.

Governance documentation does not by itself guarantee security. Runtime enforcement requires implementation and reproducible evidence. Human review is required for destructive, irreversible, sensitive, externally visible, production, and account-changing operations.

### 8.7 Controlled Evolution

Architecture and engineering capabilities evolve through explicit proposals, evidence, appropriate review, required approval, implementation, evaluation, and traceable status updates. Approval and implementation authorization are distinct where the governance process requires separation.

### 8.8 Reproducibility and Traceability

Engineering work should preserve relevant inputs, decisions, affected files, commands, outcomes, limitations, approval dependencies, and changed capability status where applicable.

The repository must not claim full observability, deterministic behavior, or reproducibility beyond the evidence actually available.

## 9. Canonical Architecture Relationship

The product constitution defines intent and principles, while the canonical architecture documents define approved structure and requirements. This document is one of the canonical product-level documents; future detailed documents should remain consistent with it and with explicit approved decisions.

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) is the architecture entry point and authority model.
- `architecture/SYSTEM_BOUNDARIES.md` is a planned document defining system boundaries.
- `architecture/L0-L15-LAYER-MAP.md` is a planned L0–L15 layer map.
- `architecture/FIVE-PLANES.md` is a planned cross-cutting plane definition.
- `architecture/MASTER-CORE.md` is a planned Modular Master Core document.
- `architecture/UNIVERSAL-INFRASTRUCTURE.md` is a planned shared-infrastructure document.
- `architecture/MODULE-REGISTRY.md` is a planned module inventory document.
- `architecture/MODULE-CONTRACT.md` is a planned module-contract specification.
- `architecture/UNIVERSAL-CONTEXT.md` is a planned context-model document.
- `architecture/CROSS-AGI-COLLABORATION.md` is a planned collaboration model.
- `architecture/MODEL-GATEWAY.md` is a planned provider-independent gateway definition.
- `architecture/SECURITY-GOVERNANCE.md` is a planned security-governance document.
- `architecture/CAPABILITY-STATUS.md` is a planned capability-status contract.
- `architecture/ARCHITECTURE-DECISIONS.md` is a planned decision register.
- `architecture/OPEN-DECISIONS.md` is a planned unresolved-decision register.

All paths in the previous list except `architecture/SOURCE_OF_TRUTH.md` and this product constitution remain planned targets unless separate evidence establishes an existing authoritative document.

## 10. Provider and Tool Independence

Canonical skills and workflows must express provider-independent intent and constraints wherever possible. Provider-specific instructions, formats, permissions, and adapters are separate mapping layers.

Tools must be integrated through explicit interfaces that define inputs, outputs, capabilities, authorization, allowed operations, failure behavior, and stop conditions. Provider or tool availability must not be inferred from installation notes, manifests, or repository declarations.

An adapter may be `ADAPTER-READY`, `EXPERIMENTAL`, or `NOT IMPLEMENTED` even when documentation exists. Runtime readiness requires invocation and behavior evidence. Authentication and external account configuration require separate evidence and must not be disclosed or assumed.

## 11. Skills, Agents, Integrations, and Workflows

### Skills

Skills are reusable engineering instructions or declared execution contracts. A Skill must be scoped, provider-neutral where possible, versioned or explicitly identified, and connected to appropriate evidence and validation. A Markdown Skill definition does not execute itself.

### Agent roles

Agent roles define responsibilities, boundaries, inputs, outputs, delegation, review, permissions, and handoffs. Provider-specific custom agents do not replace canonical role contracts.

### Integrations

Integrations connect repository-defined capabilities to external or local tools and providers. They require least privilege, explicit authorization, bounded failure handling, and security review.

### Workflows

Workflows coordinate bounded lifecycle stages such as request intake, specification readiness, repository inspection, planning, implementation, testing, debugging, verification, reporting, and stopping. A workflow does not prove independent execution or acceptance.

## 12. SUPER AGI Relationship and Boundary

SUPER AGI is the target system for which this engineering platform supplies governed development infrastructure. It is not the repository itself, and this constitution defines no deployed runtime behavior.

The intended model is one unified system composed of specialized major intelligence modules sharing universal infrastructure, context, governance, and collaboration capabilities. No runtime claims follow from naming that model or listing its planned architecture components.

Any claim that the platform produces or maintains a conscious, autonomous, human-level, or otherwise exceptional intelligence must be supported by independently verifiable evidence and reviewed against this constitution.

## 13. Security, Permissions, and Human Control

`claude-skills` is designed for repository and engineering operations that may be sensitive or consequential. Security expectations include:

- least-privilege execution;
- explicit tool and provider boundaries;
- secret and credential protection;
- user-data and sensitive-path protection;
- safe handling of repository-controlled and external content;
- prompt-injection resistance;
- fixed or allowlisted executable invocation where appropriate;
- bounded input, output, timeout, and resource behavior;
- auditable operations and failure handling; and
- human approval before destructive, irreversible, externally visible, production, or account-changing actions.

The repository must not claim that governance text, status fields, or test definitions are technical enforcement. Enforcement requires implementation and reproducible validation.

## 14. Capability Claims and Evidence

Capability claims must identify whether they refer to documentation, implementation, evaluation, approval, provider compatibility, or runtime readiness. They must cite or record repository evidence appropriate to the claim.

The evidence hierarchy is not interchangeable:

- a specification describes expected behavior;
- an implementation defines code or configuration;
- a test or trace provides execution evidence;
- independent evaluation may provide reviewer evidence;
- an approval record establishes authority; and
- runtime readiness requires observed operational behavior and dependency availability.

The status vocabulary in this constitution applies consistently across architecture, provider, tool, integration, module, skill, and workflow claims.

## 15. Architecture Change Governance

A product or architecture change should begin with a bounded proposal that identifies its objective, affected components, dependencies, security impact, compatibility impact, evidence requirements, and unresolved decisions.

The proposal must be reviewed through the established ownership and architecture process. Approval must identify the exact scope and the evidence that establishes authority. Implementation authorization, independent evaluation, release, and deployment remain separate gates unless the approval record explicitly covers them.

Provider-specific files, adapters, code, and operational instructions must not bypass canonical governance or silently become new sources of architecture truth. Conflicts must be recorded and resolved through the documented process instead of selected by convenience.

## 16. Success Criteria

The product succeeds only when it becomes possible to demonstrate, with evidence, that:

- canonical definitions and provider-specific adapters remain synchronized through a governed mechanism;
- Skills have clear contracts and bounded execution behavior;
- agent roles have explicit scope, permissions, and handoffs;
- providers and tools expose capabilities and unsupported cases honestly;
- workflows produce traceable evidence rather than unsupported completion claims;
- registries and validation scripts reflect actual repository state;
- security-sensitive operations use least privilege and human control;
- implementation and independent verification remain distinguishable;
- architecture changes preserve approved decisions and record unresolved questions; and
- SUPER AGI engineering work remains within the explicitly governed platform boundary.

These criteria describe intended outcomes, not existing completion status.

## 17. Current Limitations and Unresolved Decisions

The repository currently has proposal-level architecture records, some implemented Python framework and validation modules, documentation, and a narrow workflow foundation. It does not demonstrate that every proposed product capability exists or works.

Important unresolved items include:

- the integration base and final approval authority;
- canonical architecture approval for the planned canonical documents;
- canonical Skill format and lifecycle decisions beyond existing scoped records;
- provider adapter implementation and compatibility evidence;
- the seven expected provider configurations;
- the 14 mandatory tool integrations, installation, authentication, and runtime readiness;
- the licensing decision;
- agent-role definitions and invocation evidence;
- persistent canonical registries and templates;
- complete independent evaluation and security-enforcement evidence; and
- approval of release and deployment lifecycle gates.

These gaps must remain visible. Future implementation must not present them as resolved through documentation.

## 18. Relationship to Other Canonical Documents

This constitution is related to the repository governance files as follows:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md) defines architecture-document authority and classification.
- [`AGENTS.md`](../AGENTS.md) defines repository-wide agent behavior and stop conditions.
- [`CLAUDE.md`](../CLAUDE.md) provides Claude-specific repository entry instructions.
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) defines contribution and review expectations.
- [`SECURITY.md`](../SECURITY.md) defines repository security policy and reporting principles.
- The [`specification-to-implementation workflow`](../workflows/spec-to-implementation/README.md) defines one bounded implementation lifecycle.
- [`docs/compatibility/README.md`](../docs/compatibility/README.md) defines compatibility status vocabulary.
- Existing documents under `docs/architecture/` are evidence-bearing proposals, specifications, decisions, or review records only to the extent supported by their own status.

No relationship described here is an approval, implementation claim, or runtime guarantee.
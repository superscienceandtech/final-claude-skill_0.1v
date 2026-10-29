---
name: "engineering-dependency-management"
description: "Use when discovering, evaluating, introducing, reusing, changing, or documenting software and architectural dependencies within authorized engineering work."
---

# Engineering Dependency Management

## Purpose and Applicability

Use this Skill when a task involves dependencies that affect implementation, architecture, build or runtime behavior, integration, or maintenance. Relevant dependencies may include external libraries and packages; runtime, build-time, and development tools; internal modules and shared infrastructure; provider adapters, SDKs, APIs, schemas, configuration, scripts, and workflows; or relationships between architecture components and layers.

Distinguish package-manager dependencies from architectural and operational dependencies. A package manifest or lockfile describes a different concern from a module relying on another module's contract, or an operation requiring credentials, network access, storage, or an external service. These dependency types are not necessarily represented or managed by the same mechanism.

This Skill complements [`engineering-standards-conventions`](../engineering-standards-conventions/SKILL.md), [`engineering-pattern-reuse`](../engineering-pattern-reuse/SKILL.md), [`engineering-risk-management`](../engineering-risk-management/SKILL.md), [`engineering-quality-management`](../engineering-quality-management/SKILL.md), [`repository-implementation`](../repository-implementation/SKILL.md), and [`architecture-compliance`](../architecture-compliance/SKILL.md). Use those Skills for their distinct procedures rather than duplicating them here.

The `claude-skill_sonjoy` repository is the provider-neutral Skills and engineering-orchestration platform for building and maintaining SUPER AGI, not the SUPER AGI runtime.

## Core Principles

- Ground dependency claims in inspected repository evidence and preserve source maturity.
- Add or change dependencies only when justified by the authorized requirement.
- Reuse an existing suitable dependency or repository abstraction where it fits.
- Keep dependency surfaces and coupling proportionate to demonstrated needs.
- Preserve architecture boundaries, provider neutrality, security, and existing behavior.
- Distinguish declared dependencies from dependencies actually used, and proposed compatibility from verified compatibility.
- Do not infer operational capability from a declaration, architecture document, package presence, or integration description alone.

## Dependency Discovery

Inspect only the repository areas relevant to the authorized task. Depending on the project and scope, examine:

- package manifests, lockfiles, build files, and runtime or development configuration;
- imports, module relationships, and existing implementations;
- provider adapters, SDK or API integration definitions, and external-service configuration;
- relevant architecture contracts, module boundaries, and source-of-truth documents;
- dependency documentation and nearby implementation patterns; and
- evidence about compatibility, ownership, or lifecycle requirements.

Do not assume a particular language, package manager, dependency graph tool, registry, or runtime unless repository evidence establishes it. A manifest records a declaration; verify actual use and context before claiming a dependency is required or unused.

## Dependency Classification

Use the following as general engineering distinctions when useful, not as a new mandatory repository taxonomy:

- **Direct versus transitive:** explicitly depended on by the component versus brought in through another dependency.
- **Runtime, build-time, or development-only:** needed to execute the product, produce a build, or support development activities, respectively.
- **Internal versus external:** supplied by repository components versus an outside package, service, provider, or tool.
- **Required versus optional:** necessary for the stated behavior versus needed only for a separately supported feature or integration.
- **Compile-time versus runtime coupling:** dependencies needed for type/build relationships versus dependencies needed during operation, where that distinction applies.
- **Declared versus used:** listed or described versus evidenced in relevant implementation or execution.
- **Existing versus proposed:** already present and applicable versus being considered for introduction.

Do not create a repository-wide dependency registry or mandatory classification scheme without authorization.

## Dependency Evaluation

Assess a proposed or existing dependency in proportion to the task. Consider:

- fit for the actual requirement and whether existing repository capabilities suffice;
- compatibility with established interfaces, language/runtime constraints, and expected behavior;
- maintenance and lifecycle information where reliable evidence is available;
- license and distribution implications when relevant;
- security and supply-chain considerations, including provenance and transitive dependencies;
- portability and provider neutrality where required;
- operational requirements such as credentials, network access, storage, or external services; and
- maintenance burden, coupling, and the dependency surface introduced.

Separate verified facts from assumptions and unchecked information. Do not invent package-health scores, risk thresholds, or mandatory approval processes. If license, security, compatibility, or operational details materially affect the decision but cannot be established, state the gap and ask for direction where needed.

## Introduction and Reuse Workflow

1. **Identify the need.** State the authorized behavior or requirement that motivates a dependency.
2. **Inspect current capabilities.** Check whether an existing package, implementation, interface, or repository abstraction already satisfies the requirement.
3. **Compare options as needed.** Consider reasonable alternatives and their relevant trade-offs; do not imply an exhaustive comparison without evidence.
4. **Select the smallest justified surface.** Prefer a proportionate solution over an unnecessary package, broad SDK, or redundant abstraction.
5. **Follow applicable conventions.** Use the repository's existing package, build, and configuration practices when evidenced and relevant.
6. **Respect authorization.** Modify only authorized files. Do not install, fetch, or access external registries or services unless the task and repository instructions explicitly permit it.
7. **Record material rationale when appropriate.** Follow existing documentation and architecture decision guidance if decision recording is in scope. A note or proposal does not itself approve implementation.

Do not add a dependency merely for convenience when a proportionate existing solution satisfies the requirement.

## Dependency Boundaries and Architecture

Keep dependencies consistent with applicable contracts, module ownership, and system boundaries:

- Avoid circular dependencies and inappropriate upward dependencies between layers.
- Keep domain behavior separate from provider-specific SDK details where the architecture calls for that boundary.
- Use explicit interfaces or adapters when they are justified by the requirement and established architecture; do not prescribe a universal dependency-injection framework or pattern.
- Avoid coupling unrelated modules through shared implementation details.
- Reuse shared infrastructure only when its existence, interface, authority, and behavior are supported by evidence.

The product direction is one unified SUPER AGI system with specialized intelligence modules and shared universal infrastructure, not disconnected AI products. Reuse shared infrastructure where appropriate without erasing legitimate domain boundaries.

Canonical Skills should remain provider-neutral where specified. Provider SDKs, APIs, and integrations belong at appropriate adapter boundaries when authorized. Do not assume different providers are interchangeable; document meaningful capability differences and fallback limits where relevant. Do not claim provider independence or universal interchangeability without evidence.

Consult [`SYSTEM_BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md), [`ARCHITECTURE-PRINCIPLES.md`](../../architecture/ARCHITECTURE-PRINCIPLES.md), [`MODULE-CONTRACT.md`](../../architecture/MODULE-CONTRACT.md), [`UNIVERSAL-INFRASTRUCTURE.md`](../../architecture/UNIVERSAL-INFRASTRUCTURE.md), and [`MODEL-GATEWAY.md`](../../architecture/MODEL-GATEWAY.md) only where they materially affect the task. Preserve each document's approval status and scope; proposed architecture is not implementation evidence.

## Versioning and Compatibility

Follow actual repository version constraints and lockfile conventions where present and applicable. Consider supported language and runtime versions only when repository evidence establishes them. Avoid unnecessary upgrades or broad dependency changes outside the task scope.

Identify breaking changes and migration requirements when evidence supports them. Keep declarations consistent with actual use when that work is authorized. Distinguish declared compatibility from compatibility verified by actual checks or execution; do not invent version policies, supported ranges, or release guarantees.

## Security and Supply-Chain Considerations

Follow applicable repository security requirements, including [`SECURITY-GOVERNANCE.md`](../../architecture/SECURITY-GOVERNANCE.md) and [`security-aware-engineering`](../security-aware-engineering/SKILL.md). Where relevant to the task, consider:

- package provenance and trusted sources, when verifiable;
- known vulnerabilities, only where reliable and authorized evidence is available;
- unnecessary permissions or excessive dependency capabilities;
- secure handling of secrets and credentials;
- network access and trust in external services;
- dependency confusion, typosquatting, and untrusted package sources; and
- inherited risk from transitive dependencies and license obligations.

Do not claim a dependency is secure, vulnerability-free, compliant, or license-compatible without supporting evidence. Do not bypass repository controls or obtain information from external services unless explicitly authorized.

## Dependency Changes and Lifecycle

Handle adding, updating, replacing, isolating, or removing dependencies only within the authorized task scope. Preserve unrelated repository changes and avoid destructive cleanup.

Before removing a dependency, distinguish a package no longer directly used from one still required transitively, operationally, or by another component. Distinguish a proposed replacement from a completed removal. Change or remove only dependencies within scope, and claim completion only when the change is observed and supported by evidence. Do not update or remove unrelated dependencies as part of an isolated implementation.

## Failure and External-Service Limitations

Account for relevant failure modes such as unavailable services, authentication or configuration errors, version or interface incompatibility, network failures, timeouts, optional integration absence, and partial availability.

Recommend explicit failure handling consistent with the component's established contract. Do not promise retries, fallback providers, offline support, or graceful degradation unless required or evidenced as implemented. Separate a potential failure mode from a failure actually observed. Report uncertain or partial outcomes without implying success.

## Evidence and Communication

When material, report:

- dependencies added, reused, changed, or removed;
- the requirement motivating a material dependency decision;
- relevant files and configuration surfaces changed;
- important compatibility, licensing, security, and operational limitations;
- assumptions or unresolved questions affecting the implementation; and
- checks actually performed and work not performed.

Distinguish observed repository facts from recommendations and unverified claims. Do not claim that a dependency was inspected, validated, tested, removed, or proven compatible without evidence. Use [`evidence-reporting`](../evidence-reporting/SKILL.md) for detailed reporting discipline.

## Related Skills and Architecture References

- [Engineering standards and conventions](../engineering-standards-conventions/SKILL.md)
- [Engineering pattern reuse](../engineering-pattern-reuse/SKILL.md)
- [Engineering quality management](../engineering-quality-management/SKILL.md)
- [Engineering risk management](../engineering-risk-management/SKILL.md)
- [Security-aware engineering](../security-aware-engineering/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Engineering change management](../engineering-change-management/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [Module contract](../../architecture/MODULE-CONTRACT.md)
- [Universal infrastructure](../../architecture/UNIVERSAL-INFRASTRUCTURE.md)
- [Model Gateway](../../architecture/MODEL-GATEWAY.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)
- [Architecture decisions register](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open architecture decisions](../../architecture/OPEN-DECISIONS.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)

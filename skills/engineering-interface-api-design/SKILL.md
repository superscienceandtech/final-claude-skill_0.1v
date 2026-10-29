---
name: "engineering-interface-api-design"
description: "Use when designing, implementing, evolving, or documenting software interfaces and APIs within an authorized engineering task."
---

# Engineering Interface and API Design

## Purpose and Applicability

Use this Skill when a task creates, changes, or documents an interface between components or actors, including:

- internal module boundaries and public or private APIs;
- service-to-service communication;
- provider adapters, SDKs, and external integrations;
- agent, tool, workflow, and Skill contracts;
- cross-module collaboration and shared infrastructure;
- configuration, data exchange, and event interfaces where relevant.

An interface's **logical contract** defines intended responsibilities and observable behavior. Its **transport**, **protocol**, **serialization**, and **implementation** describe how that contract is realized. Keep these concerns distinct unless the authorized task and applicable architecture intentionally bind them together.

This Skill complements dependency management, pattern reuse, architecture compliance, quality management, security-aware engineering, and repository implementation. It guides interface-specific decisions without duplicating those Skills' full procedures or authorizing new interfaces beyond the active task.

The `claude-skill_sonjoy` repository is the provider-neutral Skills and engineering-orchestration platform for developing SUPER AGI, not the SUPER AGI runtime.

## Interface Discovery and Contract-First Design

Before creating or changing an interface:

1. Identify the requirement, intended purpose, expected deliverable, and authorized scope.
2. Locate existing interface definitions, implementations, consumers, and relevant architecture decisions or contracts.
3. Identify the interface owner and intended consumers where evidence establishes them. Do not invent ownership.
4. Establish, as relevant to the task:
   - responsibilities and explicit non-responsibilities;
   - inputs, outputs, and observable side effects;
   - preconditions and postconditions;
   - failure modes and error semantics;
   - permission, trust, and data boundaries;
   - compatibility and lifecycle expectations; and
   - dependencies and external assumptions.
5. Distinguish observed repository interfaces from proposed designs and examples.

Follow applicable repository instructions and [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md). Inspect only sources needed for the task. Do not invent a repository-wide contract format or require a particular API specification language unless applicable repository evidence establishes it.

## Interface Design Principles

Design interfaces that are explicit, understandable, cohesive, and proportionate to actual consumer needs. Keep responsibilities narrow enough that ownership, effects, and compatibility can be reasoned about.

- Use names and data conventions consistent with relevant established patterns.
- Define stable behavior where stability is required by actual consumers or contracts.
- Make required and optional values, defaults, nullability, constraints, and validation behavior clear.
- Avoid exposing implementation details across boundaries without a concrete reason.
- Prefer minimal contracts that allow necessary evolution without promising unsupported compatibility.
- Do not add operations, fields, abstractions, or coupling that are not needed by the authorized task.

## Inputs, Outputs, and Errors

Specify and implement input and output behavior according to the actual use case and existing contracts:

- State which inputs are required or optional, their types and constraints, and how they are validated.
- Define behavior for missing, invalid, malformed, or unauthorized inputs.
- Make successful results and failure outcomes distinguishable.
- Use actionable error information consistent with established patterns, without disclosing secrets or unnecessary implementation details.
- Consider partial failures, cancellation, and timeouts where relevant to the boundary.
- Define idempotency or retry behavior only when the interface's operation and requirements need it.
- Include pagination, filtering, or versioning only when justified by actual consumers and existing conventions.

Do not impose a universal response envelope, error-code set, retry policy, pagination scheme, or validation framework without repository authority. Do not promise retries, fallback, or graceful degradation unless required and implemented.

## Compatibility and Evolution

Before changing an existing contract, identify its consumers and compatibility expectations from actual evidence. Distinguish a potentially backward-compatible change from one that could break callers; do not silently change the meaning of established fields, defaults, errors, or operations.

Follow versioning and deprecation policies only where actual repository policy or evidence establishes them. Do not invent supported API versions, migration guarantees, or backward-compatibility promises. Coordinate related implementation and documentation changes only within the authorized scope. Report broader consumer changes or migration work as a dependency requiring separate authorization.

## Security and Trust Boundaries

Apply relevant requirements from [`SECURITY-GOVERNANCE.md`](../../architecture/SECURITY-GOVERNANCE.md) and [`security-aware-engineering`](../security-aware-engineering/SKILL.md):

- define authentication and authorization behavior when relevant to the interface;
- validate untrusted inputs and payloads at the appropriate boundary;
- apply permission checks at the boundary responsible for enforcing them, where that responsibility is established;
- minimize exposure of sensitive data and avoid leaking it through outputs or errors;
- keep credentials and secrets out of interface examples, logs, and reports;
- account for trust differences among modules, agents, providers, tools, and external services; and
- preserve auditability only where relevant governance requires it.

Do not claim an interface is secure or compliant without supporting evidence. Architecture descriptions and interface definitions do not prove that controls are implemented or enforced.

## Cross-Module and SUPER AGI Interfaces

Preserve the product direction: one unified SUPER AGI system with specialized intelligence modules and shared infrastructure, not 100 disconnected AI products. Clear module contracts and shared infrastructure can support interoperability while each module retains legitimate domain-specific internal behavior.

Keep module ownership, context boundaries, permissions, and traceability explicit where relevant. Isolate model-provider and external-integration details behind appropriate interfaces when justified; do not assume providers are interchangeable or that all modules must expose identical capabilities.

[`MODULE-CONTRACT.md`](../../architecture/MODULE-CONTRACT.md) describes a proposed common module contract and records unresolved details, including fields, identifiers, schemas, protocols, conformance authority, and runtime enforcement. Do not invent mandatory module-contract fields or present proposed details as approved requirements. Consult [`CROSS-AGI-COLLABORATION.md`](../../architecture/CROSS-AGI-COLLABORATION.md), [`UNIVERSAL-CONTEXT.md`](../../architecture/UNIVERSAL-CONTEXT.md), [`UNIVERSAL-INFRASTRUCTURE.md`](../../architecture/UNIVERSAL-INFRASTRUCTURE.md), and [`MODEL-GATEWAY.md`](../../architecture/MODEL-GATEWAY.md) only where they materially affect the task, preserving each source's maturity and scope.

State capability limitations accurately. A conceptual interface, mock, proposal, or documented module does not demonstrate operational behavior; use [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) when making a supported capability claim.

## Provider and Protocol Neutrality

Keep the logical contract separate from transport and provider choices where the architecture and task permit. Consider separately:

- logical responsibilities, inputs, outputs, and errors;
- transport, protocol, and serialization;
- provider-specific SDKs and adapter behavior;
- authentication mechanisms; and
- runtime, network, and deployment assumptions.

Recommend abstraction only when it provides meaningful portability, boundary control, or testability for actual consumers. Do not force identical behavior or capabilities across providers when evidence shows differences. Keep provider-specific implementation at the appropriate adapter boundary and do not let one provider become a global assumption without authorization and architecture support.

## Documentation and Examples

Document an interface to the extent needed by its consumers and task, including its purpose, intended consumers, input and output semantics, constraints, failure behavior, security assumptions, compatibility considerations, and relevant authoritative contract references.

Keep examples minimal and accurate. Label illustrative examples as such; do not imply that an example is an existing repository interface unless it has been verified. Use [`DOCUMENTATION-STANDARDS.md`](../../architecture/DOCUMENTATION-STANDARDS.md) according to its recorded maturity; it describes proposed conventions, not mandatory policy by itself.

## Implementation Workflow

1. Identify the authorized requirement and scope.
2. Locate relevant existing interfaces, consumers, contracts, patterns, and architecture constraints.
3. Establish responsibilities, ownership, consumers, and trust boundaries where evidence permits.
4. Define the smallest adequate logical contract and separate it from transport or implementation details.
5. Consider inputs, outputs, validation, failures, permissions, compatibility, and relevant dependencies.
6. Reuse an established pattern when it fits; justify any material deviation.
7. Implement only authorized changes and preserve existing behavior and unrelated work.
8. Record material decisions or limitations only when required and authorized.
9. Report actual changes, relevant evidence, and unresolved blockers.

This procedure does not add a separate audit, review, or testing phase. Perform validation or testing only when the active task authorizes or requires it.

## Conflict and Exception Handling

When interface conventions conflict, a contract disagrees with architecture, ownership or consumer expectations are unclear, compatibility policy is missing, or a request exceeds authorized scope:

1. Identify the relevant sources and the precise ambiguity or conflict.
2. Preserve each source's authority, maturity, and scope.
3. Consult [`architecture-compliance`](../architecture-compliance/SKILL.md), [`ARCHITECTURE-DECISIONS.md`](../../architecture/ARCHITECTURE-DECISIONS.md), and [`OPEN-DECISIONS.md`](../../architecture/OPEN-DECISIONS.md) as relevant.
4. Do not invent precedence, approval, compatibility policy, or a missing contract.
5. Continue only independent work that remains authorized and safe; otherwise pause and seek clarification.

A proposed interface or documented contract is not evidence that implementation exists. If implementation evidence is missing, state what is proposed and what remains unverified.

## Evidence and Reporting

When relevant, report interfaces created or modified, contract sources and consumers actually identified, compatibility and security implications, assumptions and limitations, material deviations from established patterns, and unresolved decisions that block implementation.

Distinguish repository observations from general recommendations and unverified assumptions. Do not claim that files were inspected, consumers identified, compatibility assessed, security verified, or operations performed unless evidence supports the claim. Use [`evidence-reporting`](../evidence-reporting/SKILL.md) for detailed claim-to-evidence guidance.

## Related Skills and Architecture References

- [Engineering standards and conventions](../engineering-standards-conventions/SKILL.md)
- [Engineering pattern reuse](../engineering-pattern-reuse/SKILL.md)
- [Engineering dependency management](../engineering-dependency-management/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Engineering quality management](../engineering-quality-management/SKILL.md)
- [Engineering risk management](../engineering-risk-management/SKILL.md)
- [Security-aware engineering](../security-aware-engineering/SKILL.md)
- [Engineering change management](../engineering-change-management/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [Module contract](../../architecture/MODULE-CONTRACT.md)
- [Universal infrastructure](../../architecture/UNIVERSAL-INFRASTRUCTURE.md)
- [Universal Context](../../architecture/UNIVERSAL-CONTEXT.md)
- [Cross-AGI collaboration](../../architecture/CROSS-AGI-COLLABORATION.md)
- [Model Gateway](../../architecture/MODEL-GATEWAY.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)
- [Architecture decisions register](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open architecture decisions](../../architecture/OPEN-DECISIONS.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)

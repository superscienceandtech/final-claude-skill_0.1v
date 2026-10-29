---
name: "engineering-error-handling-resilience"
description: "Use when designing, implementing, or documenting task-appropriate error handling, recovery, and resilience behavior."
---

# Engineering Error Handling and Resilience

## Purpose and Applicability

Use this Skill when a task changes behavior that can fail or produce partial, delayed, or uncertain results, including:

- function and module execution;
- APIs and interface boundaries;
- external services and provider integrations;
- agent or workflow steps;
- data processing and persistence;
- background operations and automation; and
- distributed or long-running operations, where applicable.

Distinguish an expected business outcome (such as a valid empty result or rejected business condition) from an unexpected technical failure. A non-success result is not automatically an exception, incident, or system defect; follow the actual contract.

This Skill complements interface/API design, dependency management, risk management, quality management, security-aware engineering, and repository implementation without replacing their full procedures. It provides guidance, not an execution engine, resilience framework, or guarantee of availability. The `claude-skill_sonjoy` repository is the provider-neutral engineering and Skills platform for building and maintaining SUPER AGI, not the SUPER AGI runtime.

## Failure Discovery and Classification

Identify realistic failure conditions from task requirements, existing contracts, dependencies, configuration, side effects, and evidenced operational assumptions. Consider only conditions material to the authorized work. General categories can include:

- invalid, missing, or unauthorized input;
- authentication or authorization failure;
- missing, malformed, or conflicting configuration;
- dependency, provider, SDK, or service failure;
- timeout, cancellation, interruption, or connectivity failure;
- resource exhaustion or rate limiting;
- data validation, integrity, or persistence failure;
- partial success or an outcome that cannot be confirmed;
- programming defects or invariant violations.

These are general engineering categories, not a repository-wide error taxonomy. Distinguish an observed failure from a possible failure mode, and do not invent project-specific operational conditions as facts.

## Error Semantics and Propagation

Define behavior at the interface boundary according to its actual contract:

- Make expected outcomes and failure outcomes distinguishable to callers.
- Preserve relevant causal context when translating a low-level failure into a higher-level error.
- Report enough actionable information for a caller or operator to respond, without exposing secrets or sensitive implementation details.
- Propagate failures that the current layer cannot safely handle; handle locally only when a valid recovery or translation is defined.
- Do not swallow exceptions, silently discard failures, or return success-shaped results when the operation failed or its outcome is unknown.
- Avoid broad catch-all handlers that obscure defects, authorization failures, or invariant violations.
- Keep error semantics consistent with established interfaces and downstream contracts.

Do not prescribe a universal error envelope, exception hierarchy, or error-code registry unless applicable repository evidence requires it.

## Timeouts, Retries, and Idempotency

Consider explicit timeout boundaries where an operation can block or wait on a dependency. Set a limit only when justified by the task, contract, and environment; do not invent global timing defaults.

Use retries only for failures that may be transient and where retrying is safe. When appropriate to the existing system and task, consider bounded attempts, backoff and jitter, retry budgets, and service-provided rate-limit guidance. Prevent retries from amplifying load or continuing indefinitely.

Before retrying, determine whether the operation is idempotent or may already have caused a side effect. Do not blindly retry non-idempotent operations, especially when the previous outcome is uncertain. Consider cancellation and deadline propagation where supported by the actual interfaces. Do not claim that a system supports these mechanisms unless evidence demonstrates it.

## Fallback and Graceful Degradation

Use a fallback only when it is semantically valid, safe, authorized, and consistent with the caller's expectations. Consider whether a dependency is optional or mandatory, whether partial functionality preserves correctness, and whether cached or stale data needs explicit freshness limitations.

Provider alternatives may differ in capabilities, behavior, permissions, and failure semantics. Do not substitute providers as if they were interchangeable without evidence and authorization. Prefer fail-fast behavior when fallback could violate correctness, security, data integrity, or user expectations.

Communicate degraded results clearly. Do not claim that fallback providers, caching, circuit breakers, offline support, or graceful degradation exist unless repository evidence confirms their implementation and relevant behavior.

## Partial Failure and Distributed Operations

For multi-step workflows, cooperating modules or agents, or operations with external side effects, consider:

- which steps completed and which did not;
- whether a failure occurred before or after a side effect;
- whether duplicate execution or repeated delivery is possible;
- whether cancellation or compensation is safe and supported by the contract;
- consistency boundaries and limits on recovery; and
- what can be confirmed versus what remains uncertain.

Do not introduce distributed transactions, compensation systems, queues, or orchestration infrastructure unless the task requires them and the applicable architecture supports them. Do not imply that a partial operation was rolled back or undone without evidence.

## Logging, Observability, and Diagnostics

When logging or diagnostics are in scope, capture useful context proportionately, such as the failure category, affected operation, relevant dependency, and execution circumstances. Use correlation or trace identifiers only when available and established. Preserve causal context when practical.

Distinguish expected outcomes from actionable technical failures; avoid duplicate or excessive logging. Never include secrets, credentials, private data, or sensitive payloads in logs. Do not invent a required logging platform, tracing backend, metric schema, or identifier format. State observability limitations accurately when the relevant capability is unknown or unavailable.

## Security and Information Exposure

Apply relevant requirements from [`SECURITY-GOVERNANCE.md`](../../architecture/SECURITY-GOVERNANCE.md) and [`security-aware-engineering`](../security-aware-engineering/SKILL.md):

- prevent secrets and credentials from appearing in logs or returned errors;
- avoid disclosing sensitive payloads, internal stack traces, or unnecessary implementation details to untrusted callers;
- preserve authorization checks and do not bypass them during retries or fallback;
- avoid fallback behavior after security or permission failures when it could weaken controls; and
- do not mask data-integrity violations or permission failures as successful outcomes.

Do not weaken security controls to make an operation appear successful. A documented policy or proposed mechanism is not evidence that enforcement exists.

## SUPER AGI and Provider-Neutral Resilience

Preserve the intended unified SUPER AGI system with specialized intelligence modules, shared infrastructure, and explicit boundaries. Shared resilience guidance must not erase module ownership, permissions, context boundaries, or traceability.

Provider-specific errors may be normalized at an adapter boundary when the contract calls for it, while preserving useful diagnostic context. Different providers can have different failure semantics and capabilities; do not assume every module or provider supports identical timeouts, retries, cancellation, fallback, or recovery.

Keep capability limitations explicit. A proposed resilience mechanism is not an implemented capability. Consult [`MODULE-CONTRACT.md`](../../architecture/MODULE-CONTRACT.md), [`CROSS-AGI-COLLABORATION.md`](../../architecture/CROSS-AGI-COLLABORATION.md), [`MODEL-GATEWAY.md`](../../architecture/MODEL-GATEWAY.md), and [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) only where relevant, preserving their documented maturity and scope.

## Recovery and Operational Behavior

Before resuming or recovering an operation, determine whether state may have changed before failure was reported. Consider whether cleanup and resource release are safe, whether cancellation is supported, what partial work is durable, and whether recovery needs human input.

Keep recovery actions within the authorized task and actual interface contract. Escalate or pause when automatic recovery could repeat side effects, corrupt state, cross permission boundaries, or hide an unknown outcome. Communicate what is known, what completed, what remains pending, and what cannot be confirmed.

## Implementation Workflow

1. Identify the authorized requirement and failure-sensitive operations.
2. Locate existing contracts, consumers, and relevant error-handling patterns.
3. Identify dependencies, trust boundaries, permissions, side effects, and operational assumptions.
4. Define failure semantics that match the interface and distinguish expected outcomes from technical failures.
5. Select proportionate timeout, retry, fallback, or recovery behavior only where justified and supported.
6. Preserve security, idempotency, and data-integrity requirements.
7. Implement only authorized changes and preserve unrelated repository work.
8. Document material decisions, assumptions, or limitations when appropriate.
9. Report concrete evidence and unresolved blockers.

This procedure does not add a separate audit, review, or testing phase. Perform tests or validation only when required or authorized by the active task.

## Conflict and Exception Handling

If existing error-handling patterns conflict, timeout or retry requirements are missing, recovery ownership is unclear, a failure's outcome cannot be determined, or degradation conflicts with correctness or security:

1. Identify the actual contract, source, and ambiguity.
2. Preserve each source's authority, maturity, and scope.
3. Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) and [`OPEN-DECISIONS.md`](../../architecture/OPEN-DECISIONS.md) where applicable.
4. Do not invent precedence, global defaults, or an architectural decision.
5. Pause affected work and seek clarification when safe behavior depends on an unresolved choice.
6. If a proposed resilience mechanism exceeds scope, describe it as a separate need and request authorization.

Do not silently treat an unknown outcome as a successful operation.

## Evidence and Reporting

When relevant, report failure behavior implemented or changed, relevant contracts and dependencies, retry/timeout/fallback/recovery behavior actually supported, side-effect and idempotency limitations, security and diagnostic considerations, assumptions, and unresolved blockers.

Clearly distinguish implemented behavior, proposed behavior, and general recommendations. Report only checks and operations actually performed. Do not claim resilience, recovery, fallback, or safe operation without evidence appropriate to the scope. Use [`evidence-reporting`](../evidence-reporting/SKILL.md) for detailed claim boundaries.

## Related Skills and Architecture References

- [Interface and API design](../engineering-interface-api-design/SKILL.md)
- [Dependency management](../engineering-dependency-management/SKILL.md)
- [Pattern reuse](../engineering-pattern-reuse/SKILL.md)
- [Quality management](../engineering-quality-management/SKILL.md)
- [Risk management](../engineering-risk-management/SKILL.md)
- [Security-aware engineering](../security-aware-engineering/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Change management](../engineering-change-management/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [Module contract](../../architecture/MODULE-CONTRACT.md)
- [Universal infrastructure](../../architecture/UNIVERSAL-INFRASTRUCTURE.md)
- [Cross-AGI collaboration](../../architecture/CROSS-AGI-COLLABORATION.md)
- [Model Gateway](../../architecture/MODEL-GATEWAY.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)
- [Architecture decisions register](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open architecture decisions](../../architecture/OPEN-DECISIONS.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)

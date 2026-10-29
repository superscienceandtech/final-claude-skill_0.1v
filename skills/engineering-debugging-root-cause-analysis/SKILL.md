---
name: "engineering-debugging-root-cause-analysis"
description: "Use when diagnosing unexpected software behavior, investigating root causes, or validating a justified fix."
---

# Engineering Debugging and Root Cause Analysis

## Purpose and Applicability

This Skill provides practical, provider-neutral guidance for investigating unexpected software behavior, identifying the best-supported cause, implementing a justified fix when authorized, and communicating evidence and limitations.

Use it when engineers, maintainers, or coding agents need to diagnose a defect, failure, regression, or unexpected result. Debugging and root-cause analysis are bounded investigations, not broad architectural reviews, security audits, or invitations to refactor unrelated code. Follow the active task's file, operation, and validation scope.

The `claude-skill_sonjoy` repository is the provider-neutral Skills and engineering-orchestration platform for building and maintaining SUPER AGI. It is not the SUPER AGI runtime.

## Debugging Principles

- Start with the observed behavior and evidence that can be inspected safely.
- Separate symptoms, contributing conditions, hypotheses, and confirmed causes.
- Prefer reproducible observations over intuition or assumptions.
- Form a small set of falsifiable hypotheses and choose targeted actions that distinguish among them.
- Change one relevant variable at a time when practical, so observations remain interpretable.
- Preserve original failure evidence where possible and authorized.
- Avoid premature conclusions and claims stronger than the evidence.
- Keep diagnosis and any resulting fix within the authorized task.

## Define and Reproduce the Problem

Describe the expected behavior and the actual behavior, including the observable difference. Record relevant inputs, preconditions, state, execution path, environment, dependencies, and outputs only to the extent needed for diagnosis.

Determine whether the behavior is deterministic, intermittent, environment-dependent, version-dependent, or not yet reproducible. Minimize reproduction steps without removing conditions required to trigger the issue. If reproduction is unavailable, state which observations support the investigation and what remains uncertain.

Respect data ownership, privacy, authorization, and system boundaries when reproducing a problem. Do not use production or shared resources, sensitive data, or consequential actions unless authorized and safely bounded.

## Evidence and Hypotheses

Use relevant evidence available within scope, such as error messages, logs, stack traces, traces, metrics, source code, configuration, state transitions, dependency behavior, or direct runtime observations. These sources may be incomplete or unavailable; do not assume particular diagnostic tools, integrations, or telemetry are installed.

For each material finding, distinguish directly observed facts from assumptions and inferred explanations. Form hypotheses that could be supported or refuted by a specific observation. Prefer diagnostic steps that discriminate between plausible causes instead of collecting large amounts of unrelated information.

Collect only the minimum useful diagnostic context. Redact or omit credentials, tokens, private prompts, personal information, and other sensitive data. Treat correlations, timestamps, and neighboring errors as clues rather than proof of causation.

## Root Cause Analysis

Separate the immediate failure mechanism from deeper contributing conditions. Depending on the evidence, relevant areas may include:

- invalid assumptions or input;
- inconsistent state or data quality;
- violated interface or module contracts;
- dependency behavior, configuration, or version differences;
- timing, concurrency, retries, or asynchronous execution;
- resource constraints or exhaustion; and
- environment or infrastructure conditions.

Trace causal reasoning through the available evidence. A condition preceding a failure or appearing in the same log is not by itself a confirmed cause. State a cause as confirmed only when observations support the causal explanation; otherwise report the most plausible hypothesis and the missing evidence.

## Debugging Techniques

Choose techniques according to the behavior, environment, and authorization:

- **Targeted source inspection:** follow the affected code path and its relevant inputs, state, outputs, and error handling.
- **Stack-trace interpretation:** identify the failure location and call path while considering that the reported frame may be where a failure surfaced rather than where it originated.
- **Breakpoints and controlled step-through:** inspect execution state in a suitable environment when available and authorized.
- **Temporary diagnostic instrumentation:** add or use focused signals to answer a defined diagnostic question; protect sensitive data and remove temporary changes when authorized and appropriate.
- **Input reduction and minimal reproduction:** reduce variables while retaining the behavior under investigation.
- **Dependency isolation:** determine whether a collaborator or external dependency contributes to the observed behavior, without mistaking a simulated dependency for real integration evidence.
- **Configuration comparison:** compare relevant settings across affected and unaffected contexts without exposing secret values.
- **State-transition inspection:** establish what state changes and in which sequence, particularly around retries, asynchronous work, or partial failure.
- **Differential diagnosis:** compare environments, inputs, versions, or execution paths where those comparisons are safe and meaningful.
- **Log, metric, and trace correlation:** correlate signals when their timestamps, identifiers, coverage, and instrumentation support the inference.

Do not assume that any particular debugger, profiler, log platform, distributed tracer, or runtime facility is available.

## Runtime, Integration, and Distributed Failures

For asynchronous or distributed behavior, consider timeouts, retries, partial failures, queueing, race conditions, shared state, cancellation, duplicate execution, and backpressure when relevant to the observed path and contract.

Investigate provider APIs, model gateways, tool invocations, agent workflows, and cross-module boundaries only when they materially affect the issue. Distinguish application defects from dependency, infrastructure, configuration, and environmental failures when evidence permits. Incomplete telemetry or a missing trace does not prove that a component was uninvolved.

Do not repeat a non-idempotent or externally consequential operation merely to gather evidence when the prior outcome may be uncertain. Use safe, authorized conditions and respect human approval requirements for consequential actions.

## Fix Design and Regression Prevention

When implementation is authorized, choose the smallest justified change that addresses the supported cause rather than masking the symptom. Preserve existing behavior outside the defect, interface and module contracts, security controls, error semantics, and unrelated work.

Consider relevant boundary conditions and plausible regression paths. Avoid broad refactoring, speculative changes, or new diagnostics and infrastructure unrelated to the cause. Explain which evidence supports the fix and which hypotheses or limitations remain.

## Validation and Test Evidence

Distinguish:

- reproducing the original failure;
- observing behavior after the fix; and
- checking for regressions or related failure paths.

Use existing project conventions and authorized validation methods when validation is requested and permitted. Do not assume that debugging authorizes test execution, production experiments, benchmarks, or environment changes. Do not claim a fix is verified when the relevant validation was not performed.

Report diagnostics or tests as executed only when they were actually run, and describe their observed scope and outcome. Do not weaken tests, suppress errors, discard relevant failure evidence, or remove safeguards merely to obtain a successful result.

## Security and Operational Safety

Use least privilege and authorized environments. Keep credentials, tokens, private prompts, personal information, and sensitive system details out of diagnostic output, source changes, and reports. Retain only the non-sensitive information necessary to explain the issue.

Treat production changes, destructive operations, external calls, and other consequential actions according to repository governance and explicit user authorization. Preserve unrelated tracked and untracked work. Do not change branches, remote state, or repository history unless explicitly authorized.

## SUPER AGI Architecture Applicability

Apply debugging principles to shared infrastructure, specialized intelligence modules, agents, tools, workflows, memory, knowledge, world-model components, model gateways, and cross-AGI collaboration where relevant to the authorized work. Preserve the intended direction of one unified SUPER AGI platform with specialized intelligence modules, not 100 independent AI products.

Use applicable module contracts, system boundaries, capability statuses, and architecture decisions as context. Follow [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) to preserve distinctions among approved architecture, proposals, unresolved questions, implementation, and evidence. Architecture descriptions and component declarations do not establish runtime behavior.

Do not claim that global diagnostics, centralized tracing, automated root-cause analysis, self-healing, or a proposed integration is implemented unless direct, relevant evidence supports that status. The Model Gateway and shared infrastructure architecture documents describe proposals; their presence does not demonstrate operational capabilities.

## Practical Debugging Workflow

1. Define the observed problem and expected behavior.
2. Identify the affected component and authorized scope.
3. Collect the smallest useful set of available evidence.
4. Form falsifiable hypotheses.
5. Perform targeted diagnostic actions that distinguish among hypotheses.
6. Identify the best-supported cause, or state that the cause remains unresolved.
7. Implement the smallest justified fix when implementation is authorized.
8. Perform only the validation permitted by the task.
9. Report changes, evidence, validation status, and limitations.

This workflow guides a bounded investigation; it is not a separate audit or review phase.

## Failure Modes and Anti-Patterns

- Fixing a symptom while ignoring evidence about its cause.
- Changing multiple unrelated variables at once.
- Treating correlation or temporal proximity as causation.
- Guessing without gathering relevant evidence.
- Making broad changes before understanding or reproducing the problem where feasible.
- Ignoring environment, configuration, and dependency differences.
- Hiding failures through exception suppression or success-shaped fallbacks.
- Retrying non-idempotent operations unsafely.
- Logging sensitive diagnostic data.
- Claiming an unverified fix is successful.
- Expanding diagnosis into unrelated refactoring or unauthorized operations.

## Related Skills and Architecture References

- [Testing strategy and test design](../engineering-testing-strategy-design/SKILL.md)
- [Error handling and resilience](../engineering-error-handling-resilience/SKILL.md)
- [Observability and monitoring](../engineering-observability-monitoring/SKILL.md)
- [Performance and optimization](../engineering-performance-optimization/SKILL.md)
- [Engineering quality management](../engineering-quality-management/SKILL.md)
- [Engineering risk management](../engineering-risk-management/SKILL.md)
- [Security-aware engineering](../security-aware-engineering/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Dependency management](../engineering-dependency-management/SKILL.md)
- [Change management](../engineering-change-management/SKILL.md)
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

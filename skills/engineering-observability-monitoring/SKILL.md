---
name: "engineering-observability-monitoring"
description: "Use when designing, implementing, or documenting task-relevant observability and monitoring capabilities within authorized engineering work."
---

# Engineering Observability and Monitoring

## Purpose and Applicability

Use this Skill when engineering work needs signals to understand component behavior, detect defined conditions, diagnose failures, or communicate operational state. It is intended for engineers, architects, and coding agents working on the provider-neutral `claude-skill_sonjoy` platform or the wider SUPER AGI project.

Observability is the ability to investigate system behavior from available evidence such as logs, metrics, traces, events, and health signals. Monitoring evaluates selected signals or checks against a question or condition, such as whether a dependency is responding or a failure rate has changed. These practices can support investigation; they do not guarantee correctness, reliability, or availability.

Use this Skill for instrumentation or monitoring changes within the authorized task. It is not a standalone audit, incident response process, service-level objective policy, telemetry platform, or authorization to add unrelated infrastructure. Do not prescribe telemetry when it has no useful operational or diagnostic purpose.

The `claude-skill_sonjoy` repository is the provider-neutral Skills and engineering-orchestration platform for developing SUPER AGI; it is not the SUPER AGI runtime.

## Observability Foundations

Choose signals according to the question they need to answer:

- **Logs** record discrete events and diagnostic context.
- **Metrics** summarize numerical measurements over time, such as counts, durations, or resource levels.
- **Traces** represent a request or operation's path through components, where propagation and instrumentation are available.
- **Events** record notable state changes or domain occurrences for a defined consumer or operational purpose.
- **Health signals** communicate a specific readiness, liveness, or dependency condition; define what the signal establishes and what it does not.

These concepts can overlap in tooling, but they serve different questions. Select signals based on the relevant component boundaries, operational need, and actual capabilities. Do not treat missing telemetry as proof that a system is healthy or inactive.

## Instrumentation Strategy

Before adding instrumentation:

1. State the operational or diagnostic question the signals should answer.
2. Locate the affected component, interfaces, workflows, background jobs, integrations, and documented boundaries relevant to the task.
3. Identify existing instrumentation and conventions in that scope.
4. Choose the smallest useful set of signals and their consumer or use.
5. Consider privacy, access, cost, volume, failure paths, and what cannot be observed.

Where applicable, keep signal names, units, dimensions, timestamps, and correlation context consistent with established patterns. Do not invent a repository-wide naming standard or collect telemetry without a clear diagnostic or operational purpose.

Instrumentation may cross service boundaries, components, workflows, background jobs, integrations, and asynchronous operations only when the actual interfaces and available facilities support it. Do not infer instrumentation capability from architecture documentation alone.

## Logs and Structured Events

Make logs and events useful to their intended audience and response. Where relevant, include clear event meaning, an appropriate severity, affected operation, relevant dependency or component, and causal or correlation context when available. Preserve useful error information while distinguishing internal diagnostic detail from user-facing messages.

Use structured fields when an established implementation supports them and they help querying or interpretation. Avoid duplicate or excessive logging and avoid creating a mandatory log schema or field registry without authority.

Never put credentials, tokens, private keys, private prompts, sensitive user content, or unnecessary personal data in logs, traces, alerts, or incident summaries. Minimize and redact data according to applicable security governance. Do not expose internal stack traces or sensitive infrastructure details to untrusted callers.

## Metrics and Service Health

Choose metrics according to the workload and question. Relevant measurements may include counters, gauges, histograms, latency distributions, throughput, failure rates, saturation, availability signals, and workload-specific indicators. Define their interpretation and scope; a number without context may mislead.

Avoid uncontrolled high-cardinality dimensions and unbounded label values, especially values derived from user content or unique identifiers. Prefer stable, useful dimensions supported by existing practices.

Do not prescribe universal numeric thresholds, service-level objectives, availability targets, or alert boundaries. Use project-specific decisions and evidence where available. A health check should represent a defined condition, not merely process existence when the operational question is dependency readiness or user-visible function.

## Distributed Tracing and Correlation

Where supported and useful, trace operations across service boundaries, agents, workflows, tools, model gateways, and external integrations. Propagate trace or correlation context across synchronous and asynchronous boundaries only when the relevant interfaces and instrumentation support it.

Account for partial visibility: providers or components may not emit compatible traces, and a trace may omit external work. Do not imply that every agent, provider, or component supports distributed tracing. Use existing identifiers and formats where established; do not invent a global identifier scheme. Report limits of correlation explicitly.

## Monitoring, Alerts, and Incident Signals

Keep these functions distinct:

- A **dashboard** presents selected signals for human interpretation.
- A **monitoring check** evaluates a signal or condition.
- An **alert** communicates a condition that may require action.
- An **incident record** documents an event and its response where such a process exists.

Prefer actionable alerts connected to user impact, operational risk, or a clearly defined failure condition. Consider noise, duplicate alerts, missing telemetry, ownership, and the context a responder needs. An alert without an actionable owner or response may add noise rather than improve reliability.

Treat thresholds, paging policies, retention periods, alert ownership, and service-level objectives as project-specific decisions unless authoritative repository sources define them. Do not invent an escalation hierarchy, incident process, or monitoring platform.

## Reliability and Error-Handling Integration

Use observability to diagnose error classification, retries, timeouts, idempotency, fallback, partial failures, and recovery behavior. Instrument meaningful outcomes and transitions where authorized and useful, while keeping telemetry separate from the implementation of resilience itself.

Logging or monitoring does not make an operation safe to retry, idempotent, recoverable, or resilient. Follow [`engineering-error-handling-resilience`](../engineering-error-handling-resilience/SKILL.md) for failure semantics and recovery; report only retry, timeout, fallback, or recovery behavior that is actually supported.

## Security, Privacy, and Governance

Apply relevant requirements in [`SECURITY-GOVERNANCE.md`](../../architecture/SECURITY-GOVERNANCE.md) and [`security-aware-engineering`](../security-aware-engineering/SKILL.md). Use least privilege, data minimization, appropriate access boundaries, and redaction for telemetry. Consider who can access logs, metrics, traces, dashboards, alerts, and incident records, and avoid disclosing internal details through externally visible outputs.

Preserve auditability when required by applicable governance, but do not assume a particular audit system or retention rule. Do not invent retention periods, regulatory obligations, approval roles, or escalation hierarchies. Repository security documentation distinguishes established expectations from proposed runtime architecture; neither should be represented as operational enforcement without implementation evidence.

## SUPER AGI and Cross-AGI Applicability

Observability may help reason about the intended unified SUPER AGI architecture, shared infrastructure, specialized module boundaries, agents, workflows, tools, model gateway, and cross-AGI collaboration. Preserve the principle of one unified system with specialized intelligence modules, not 100 independent AI products.

Use shared telemetry or correlation across modules only where justified by actual contracts, ownership, permissions, context boundaries, and traceability. Provider and module capabilities may differ. Keep those differences and telemetry limitations explicit.

Do not claim global telemetry, cross-module tracing, centralized dashboards, real-time monitoring, or other operational observability capabilities already exist unless repository evidence explicitly establishes that status. Distinguish architecture concepts and proposals from implemented behavior, and use [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) when making a capability claim.

## Implementation Workflow

1. Identify the operational or diagnostic question and authorized task scope.
2. Locate the relevant component, documented boundaries, and existing interfaces.
3. Determine which signals are needed, for whom, and why.
4. Inspect existing instrumentation and conventions only in the relevant scope.
5. Reuse established patterns and available telemetry facilities where evidence supports them.
6. Add only necessary instrumentation within authorized files and operations.
7. Address privacy, security, failure paths, and missing telemetry as relevant.
8. Document material assumptions, capability limitations, and decisions within scope.
9. Report exact changes and evidence actually obtained.

Do not turn this sequence into a separate audit or review phase. Perform tests or validation only when the active task authorizes or requires them.

## Failure Modes and Anti-Patterns

Avoid:

- logs without meaningful context or events with unclear purpose;
- metrics without definitions or a useful interpretation;
- alerts that cannot trigger an actionable response;
- excessive telemetry volume or unbounded cardinality;
- leakage of secrets, sensitive content, or unnecessary personal data;
- health checks that measure the wrong condition or imply more than they establish;
- missing correlation across asynchronous boundaries where correlation is required and supported;
- treating absent telemetry as proof of health;
- assuming unsupported provider instrumentation; and
- describing proposed, mocked, or partial observability as implemented capability.

When telemetry is absent or partial, report what cannot be concluded. Do not invent availability or behavior to fill observability gaps.

## Related Skills and Architecture References

- [Error handling and resilience](../engineering-error-handling-resilience/SKILL.md)
- [Engineering quality management](../engineering-quality-management/SKILL.md)
- [Engineering risk management](../engineering-risk-management/SKILL.md)
- [Security-aware engineering](../security-aware-engineering/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Engineering change management](../engineering-change-management/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Interface and API design](../engineering-interface-api-design/SKILL.md)
- [Dependency management](../engineering-dependency-management/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [Universal infrastructure](../../architecture/UNIVERSAL-INFRASTRUCTURE.md)
- [Module contract](../../architecture/MODULE-CONTRACT.md)
- [Cross-AGI collaboration](../../architecture/CROSS-AGI-COLLABORATION.md)
- [Model Gateway](../../architecture/MODEL-GATEWAY.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)
- [Open architecture decisions](../../architecture/OPEN-DECISIONS.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)

---
name: "engineering-performance-optimization"
description: "Use when measuring, analyzing, or improving the performance and resource efficiency of authorized engineering work."
---

# Engineering Performance and Optimization

## Purpose and Applicability

Use this Skill when a task involves performance, responsiveness, throughput, capacity, or resource efficiency in software components, engineering workflows, AI integrations, or shared infrastructure. It guides engineers and coding agents to identify bottlenecks, make proportionate changes, and report measured results accurately.

Performance optimization is not authorization for unrelated architectural redesign, broad refactoring, new infrastructure, or benchmarking outside the requested scope. Keep changes bounded to the task and preserve correctness, security, and established contracts.

The `claude-skill_sonjoy` repository is the provider-neutral Skills and engineering-orchestration platform for building SUPER AGI. It is not the SUPER AGI runtime.

## Performance Engineering Principles

- Measure before optimizing.
- Establish the workload, operating conditions, baseline, and success criteria relevant to the task.
- Distinguish perceived responsiveness, latency, throughput, capacity, and resource efficiency; improving one does not necessarily improve the others.
- Treat performance as a property of the relevant end-to-end execution path, not only isolated code.
- Prefer the simplest change that addresses an evidenced bottleneck while preserving maintainability and correctness.
- Avoid premature optimization and unsupported performance claims. A plausible improvement is a hypothesis until measured under relevant conditions.

## Workload and Performance Requirements

Identify representative workloads and constraints where relevant, including input sizes, request patterns, concurrency, data volumes, resource availability, dependency behavior, and operating conditions. Define a measurable objective appropriate to the task, such as a relevant latency percentile, throughput, resource use, or task completion time.

Consider normal operation, peak or burst load, degraded dependencies, and resource constraints when those conditions matter. Treat targets, service-level objectives, capacity limits, and acceptance thresholds as project-specific unless authoritative sources establish them.

Where workload data is unavailable, state assumptions and their impact. Do not present synthetic or inferred workload characteristics as observed facts.

## Profiling and Bottleneck Analysis

Use available profiling, tracing, metrics, and diagnostics when supported and authorized. Investigate potential CPU, memory, I/O, network, database, serialization, synchronization, queueing, and dependency bottlenecks only as relevant to the actual execution path.

Distinguish measurements from hypotheses. Identify the observed bottleneck before selecting an optimization; do not assume that the most visible or complex code is the limiting factor. Do not assume a particular profiler, observability platform, integration, or runtime is installed.

Use [`engineering-observability-monitoring`](../engineering-observability-monitoring/SKILL.md) for instrumentation and diagnostic guidance. Existing telemetry can help explain behavior, but missing telemetry does not establish that a component is fast or healthy.

## Algorithm and Data-Structure Efficiency

Consider algorithmic complexity, data-structure choices, repeated computation, unnecessary allocations, and avoidable data movement. Evaluate asymptotic behavior and practical constant factors where useful for the workload.

Prefer the simplest approach that satisfies established performance and correctness requirements. Preserve functional behavior, data integrity, interface contracts, and maintainability. Avoid speculative abstractions or complexity based solely on theoretical optimization.

## Concurrency and Asynchronous Work

Distinguish concurrency (overlapping work) from parallel execution (work performed simultaneously). Consider scheduling overhead, synchronization, contention, queueing, backpressure, ordering, cancellation, duplicate work, shared state, and failure propagation where applicable.

Add concurrency only when evidence suggests it addresses the bottleneck and the task authorizes the required changes. Do not invent universal thread counts, queue capacities, concurrency limits, or scheduling policies. Preserve correctness under concurrent execution.

## Memory and Resource Efficiency

Consider allocation behavior, object lifetime, resource reuse, streaming, bounded processing, caching, and resource cleanup where relevant. Include CPU, memory, storage, network, GPU, and other resources only when supported by the actual environment and task.

Avoid unbounded caches, queues, buffers, or retained state. Account for memory pressure, leaks, cache invalidation, stale results, consistency, and privacy before recommending caching or reuse. Do not assume hardware accelerators or particular infrastructure are available.

## Data, Network, and I/O Optimization

Where evidence points to data or I/O cost, consider batching, pagination, streaming, compression, serialization overhead, request amplification, and avoidable round trips. Evaluate caching only when consistency, invalidation, privacy, and workload characteristics are understood.

Preserve API semantics, security boundaries, and data integrity. Do not introduce complexity or make broad changes when expected benefit is unsupported or falls outside the authorized task.

## AI, Agent, and Model-Gateway Performance

For AI or agent workflows, consider end-to-end latency and cost contributors such as model calls, tool invocations, retrieval, context construction, orchestration, and data transfer. Distinguish model inference latency from full task latency.

Consider model selection, request batching, caching, context size, parallel execution, or routing only when supported by evidence, compatible with existing boundaries, and permitted by applicable policy. Preserve model-provider independence where required; do not assume provider capabilities, token budgets, cache support, or performance characteristics that have not been established.

Do not weaken safety, authorization, verification, or correctness requirements solely to improve speed. Architecture documents describe the Model Gateway as proposed; do not imply that gateway routing or related performance controls are operational without evidence.

## Benchmarking and Performance Evaluation

Select measurements that match the objective and compare results with a relevant baseline under equivalent conditions. Consider representative workloads, repeatability, warm-up effects, measurement overhead, environmental differences, and variance. Distinguish synthetic benchmarks from real workload behavior.

Report the measured scope, conditions, and relevant limitations. Do not invent benchmark results or claim improvements without evidence. Follow the active task's restrictions: benchmarking, like testing, is not automatically authorized merely because it could help evaluate a change.

## Correctness, Reliability, and Security

Preserve functional behavior, data integrity, access control, privacy, and established error-handling semantics. Consider performance trade-offs involving retries, timeouts, caching, concurrency, consistency, and graceful degradation.

Do not trade correctness or required security controls for unverified gains. Coordinate with [`engineering-error-handling-resilience`](../engineering-error-handling-resilience/SKILL.md) and [`security-aware-engineering`](../security-aware-engineering/SKILL.md) where applicable. A performance improvement does not by itself establish reliability, security, or overall system quality.

## SUPER AGI Architecture Applicability

Consider performance across the intended unified SUPER AGI platform, shared infrastructure, specialized intelligence modules, agents, workflows, tools, memory, knowledge, world-model components, and Model Gateway only where relevant to the task. Preserve the principle of one unified platform with specialized modules, not 100 independent AI products.

Cross-module communication, shared-resource contention, redundant computation, context transfer, and orchestration overhead may affect end-to-end performance. Respect documented boundaries and actual capability status. Do not claim that distributed optimization, global performance telemetry, automatic resource scaling, or centralized benchmarking is implemented unless authoritative repository evidence establishes it.

Consult [`SYSTEM_BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md), [`ARCHITECTURE-PRINCIPLES.md`](../../architecture/ARCHITECTURE-PRINCIPLES.md), [`UNIVERSAL-INFRASTRUCTURE.md`](../../architecture/UNIVERSAL-INFRASTRUCTURE.md), [`MODULE-CONTRACT.md`](../../architecture/MODULE-CONTRACT.md), [`CROSS-AGI-COLLABORATION.md`](../../architecture/CROSS-AGI-COLLABORATION.md), [`MODEL-GATEWAY.md`](../../architecture/MODEL-GATEWAY.md), and [`CAPABILITY-STATUS.md`](../../architecture/CAPABILITY-STATUS.md) only where they materially affect the task, preserving each document's maturity and scope.

## Implementation Workflow

1. Identify the performance problem and affected behavior.
2. Establish workload assumptions and measurable objectives.
3. Locate the relevant component and its documented boundaries.
4. Inspect existing performance evidence and instrumentation available in scope.
5. Identify the most likely bottleneck using available evidence.
6. Select the smallest justified optimization.
7. Preserve correctness, security, reliability, and interface contracts.
8. Compare behavior against the baseline when measurement is authorized and available.
9. Record actual changes, observed results, limitations, and unresolved questions.

Do not turn this sequence into a separate audit or review phase. Run tests or benchmarks only when the task authorizes or requires them.

## Failure Modes and Anti-Patterns

Avoid optimizing without a baseline, premature optimization, unrepresentative benchmarks, confusing lower latency with higher throughput, or optimizing a component that is not the bottleneck.

Also avoid unbounded caching, queues, or parallelism; race conditions or inconsistent state; ignoring tail latency or workload variance; trading correctness or security for speed; unsupported performance claims; and introducing complex infrastructure without evidence of need.

## Related Skills and Architecture References

- [Observability and monitoring](../engineering-observability-monitoring/SKILL.md)
- [Error handling and resilience](../engineering-error-handling-resilience/SKILL.md)
- [Engineering quality management](../engineering-quality-management/SKILL.md)
- [Engineering risk management](../engineering-risk-management/SKILL.md)
- [Dependency management](../engineering-dependency-management/SKILL.md)
- [Pattern reuse](../engineering-pattern-reuse/SKILL.md)
- [Interface and API design](../engineering-interface-api-design/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Security-aware engineering](../security-aware-engineering/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [Universal infrastructure](../../architecture/UNIVERSAL-INFRASTRUCTURE.md)
- [Module contract](../../architecture/MODULE-CONTRACT.md)
- [Cross-AGI collaboration](../../architecture/CROSS-AGI-COLLABORATION.md)
- [Model Gateway](../../architecture/MODEL-GATEWAY.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)
- [Architecture decisions register](../../architecture/ARCHITECTURE-DECISIONS.md)
- [Open architecture decisions](../../architecture/OPEN-DECISIONS.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)

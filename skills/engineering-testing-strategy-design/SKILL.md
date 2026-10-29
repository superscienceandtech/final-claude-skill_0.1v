---
name: "engineering-testing-strategy-design"
description: "Use when selecting, designing, organizing, or maintaining tests for authorized engineering changes."
---

# Engineering Testing Strategy and Test Design

## Purpose and Applicability

This Skill provides provider-neutral guidance for choosing and designing tests that produce useful evidence about specified behavior, boundaries, and failure conditions. It is for engineers, quality practitioners, technical writers, and coding agents working on the `claude-skill_sonjoy` platform or related SUPER AGI development workflows.

Use it when a task involves test strategy, test cases, test organization, testability, or interpreting test evidence. Test strategy and design are distinct from test execution and independent review. This Skill does not itself authorize running tests, changing files outside task scope, conducting an audit, or claiming that behavior has been verified.

The `claude-skill_sonjoy` repository is the provider-neutral Skills and engineering-orchestration platform for building and maintaining SUPER AGI. It is not the SUPER AGI runtime.

## Testing Principles

- Tests should provide evidence about behavior derived from applicable requirements, contracts, or acceptance criteria.
- Select test effort proportionately to the change, impact, uncertainty, and affected boundaries.
- Prefer tests that are clear, deterministic, maintainable, and useful when they fail.
- Distinguish behavior supported by executed test evidence from assumptions, design intent, and untested claims.
- The existence or quantity of tests, or a coverage number by itself, does not prove correctness, quality, security, or operational readiness.
- Follow task-specific permissions and exclusions. Do not run tests merely because a test strategy suggests them.

## Requirements and Testability

Identify the behavior and constraints that apply from the explicit task, repository instructions, authoritative source-of-truth guidance, relevant approved decisions, applicable contracts, and existing conventions. Keep architecture proposals, recommendations, assumptions, and unresolved questions distinct from established requirements.

Translate applicable requirements into observable outcomes. A useful test expectation identifies the relevant input or state, action or trigger, and expected result or permitted failure behavior. Consider authorization, data integrity, interface behavior, and error semantics where they matter to the change.

If requirements or acceptance criteria are ambiguous, incomplete, or conflicting, identify the ambiguity and its effect on test design. Do not silently turn an undocumented assumption or proposed architecture into permanent expected behavior. Seek clarification when the ambiguity materially affects correctness, safety, or acceptance.

## Test Levels and Types

Choose test types according to what must be demonstrated; a project or change does not need every type.

- **Unit tests** isolate a small behavior or logic boundary. They are useful for fast, focused feedback, but excessive isolation can miss integration behavior.
- **Component tests** exercise a component with selected dependencies or adapters. They can reveal component-level behavior without requiring a complete system.
- **Integration tests** examine interactions between real components or dependencies within a defined scope. They can uncover configuration, protocol, and interaction issues, but may need controlled environments and data.
- **Contract tests** check that one side of an interface satisfies an agreed contract. A test cannot establish that the contract itself is approved or complete.
- **End-to-end tests** exercise a workflow across multiple boundaries. Use them for important integrated behavior; keep in mind that broad setup, environmental dependence, and failure diagnosis can make them costly or fragile.
- **Regression tests** preserve previously specified behavior affected by a known defect or change. Anchor them to the intended behavior, not incidental implementation details.
- **Negative and failure-path tests** cover invalid inputs, denied permissions, dependency failures, cancellation, partial outcomes, and recovery where applicable.
- **Security and authorization tests** assess relevant trust boundaries, access decisions, data disclosure, and denied operations within authorized, controlled conditions.
- **Performance tests** evaluate a stated workload and measurable objective when authorized. See [engineering-performance-optimization](../engineering-performance-optimization/SKILL.md); do not invent targets or claim results without measurement.
- **Property-based and fuzz tests** explore broad input spaces and invariants where the behavior and tooling support meaningful interpretation. They complement, rather than replace, explicit examples.
- **Compatibility tests** check relevant interface or provider compatibility when the compatibility expectations and actual integration capability are established.

Use more than one level when their evidence is complementary. Do not rely exclusively on end-to-end tests or prescribe a universal test pyramid, framework, or suite composition.

## Test Design

Design cases around meaningful behavior and risks, including, where relevant:

- expected or normal operation;
- boundary values and state transitions;
- invalid, malformed, missing, or unauthorized inputs;
- dependency failures and partial outcomes;
- retries, cancellation, timeouts, concurrency, and recovery when the applicable contract defines them; and
- important invariants, data integrity, and regression conditions.

Use representative inputs and explicit expected outcomes. Keep tests independent where practical and make setup, actions, and assertions understandable. Prefer stable synchronization and observable conditions over arbitrary sleeps or reliance on execution order. Make failure output useful without exposing secrets or sensitive data.

Avoid brittle assertions coupled to incidental implementation details, assertions that merely restate test setup, unnecessary duplication, and tests that pass without exercising the behavior they claim to cover. Use existing repository conventions for test naming, placement, fixtures, and execution; do not infer a universal structure from a single example.

## Test Doubles and External Dependencies

Choose test doubles according to the behavior under examination:

- **Mocks** can verify a meaningful interaction at a boundary, but should not encode implementation details so tightly that harmless changes break tests.
- **Stubs** provide controlled responses when the behavior under test depends on a known input from a collaborator.
- **Fakes** provide simplified working substitutes when their semantics are sufficient for the test and their limitations are explicit.
- **Fixtures** create reusable setup data or state; keep ownership, cleanup, and side effects clear.
- **Real dependencies** can provide integration evidence when their use is available, safe, authorized, and sufficiently controlled.

Do not let a mock or fake simply reproduce the implementation under test, conceal a missing integration, or make assertions pass without meaningful behavioral evidence. Provider APIs, databases, model gateways, external tools, network services, and asynchronous systems may have behaviors that doubles cannot establish. A mocked provider interaction does not prove real-provider compatibility, authentication, authorization, availability, or end-to-end operation.

Maintain provider-neutral expectations at canonical boundaries. Test provider-specific mappings only in their authorized adapter context, and report which behavior was simulated versus exercised against a real dependency.

## Data, State, and Isolation

Identify who owns test data and resources, how setup and cleanup work, and whether state can leak between tests or runs. Prefer controlled, reproducible data that is sufficient to exercise the behavior without exposing unnecessary personal or sensitive information.

Avoid destructive operations against production or shared resources unless they are explicitly authorized and safely bounded. Keep credentials out of fixtures, snapshots, logs, and reports. Consider cleanup after partial failure, parallel execution, shared state, and test order when relevant. Do not prescribe a universal fixture framework, test-data schema, or environment layout.

## Coverage and Test Selection

Line coverage indicates which code was executed; branch and path coverage describe selected control-flow exploration; requirement coverage relates tests to specified behavior. None alone proves correctness, completeness, security, or absence of defects.

Prioritize evidence for important behavior and risk: critical paths, authorization and security boundaries, high-impact failure cases, public or cross-component contracts, and changed behavior. Select the smallest set of tests that meaningfully addresses the change, adding scope when risk or architecture boundaries justify it.

Do not invent coverage percentages, mandatory gates, or universal thresholds. State what a chosen test set covers and what it does not where the distinction is material.

## Flaky Tests and Failure Interpretation

Nondeterminism can arise from timing assumptions, shared state, concurrency, network dependence, external services, environmental differences, test order, or uncontrolled data. Prefer identifying and correcting the cause over suppressing the symptom.

When a test fails, distinguish a product defect, test defect, infrastructure or environment failure, and inconclusive result only when evidence supports the classification. Do not label a failure harmless or flaky without evidence. Do not hide failures with indiscriminate retries, skipped checks, weakened assertions, or omitted output. If the cause remains unresolved, report that uncertainty.

## AI, Agent, and Model-Gateway Testing

Where applicable, test deterministic software boundaries such as prompt and context construction, input handling, tool invocation, workflow transitions, authorization, contract translation, error propagation, output validation, and side-effect control.

Distinguish deterministic code behavior from nondeterministic model outputs. For probabilistic behavior, define explicit evaluation criteria and bounded assertions appropriate to the task. Avoid brittle exact-output assertions unless exact output is part of the actual contract. One successful model response does not demonstrate general reliability.

Respect privacy, safety, provider boundaries, and the actual capability status of integrations. A conceptual design or mocked model integration is not evidence that a real provider, Model Gateway, or end-to-end model workflow has been tested. The architecture references describe proposed designs; do not treat them as proof of implemented behavior.

## SUPER AGI Architecture Applicability

Apply test design to shared infrastructure, specialized intelligence modules, agents, tools, memory, knowledge, world-model components, cross-module collaboration, and model gateways only when they materially relate to the authorized work. Preserve the intended direction of one unified SUPER AGI platform with specialized intelligence modules, not 100 independent AI products.

Where applicable, consider module and system boundaries, contracts, permissions, context propagation, shared state, dependency behavior, and failure isolation. An interaction test can provide evidence only for the exercised scope and conditions. Do not invent global test infrastructure or claim a complete platform-wide suite exists.

Respect the distinction between proposed architecture and implemented behavior. A contract, document, mock, or test declaration does not by itself prove a functioning runtime or operational capability.

## Security, Safety, and Governance

Use least privilege for test identities, tools, data, and environments where applicable. Protect secrets and sensitive information in fixtures, snapshots, test output, traces, and reports. Consider misuse, unauthorized access, malformed inputs, unsafe side effects, and recovery behavior where relevant.

Do not use tests to bypass permission boundaries or perform destructive, irreversible, externally visible, production, or otherwise consequential operations without required authorization. Preserve human approval requirements. Do not invent an approval hierarchy, compliance obligation, or mandatory quality gate.

## Applying a Test Strategy

Use this practical sequence as guidance:

1. Identify the authorized change and its documented requirements.
2. Determine affected components, interfaces, state, and risk boundaries.
3. Select the smallest set of test types that meaningfully addresses those concerns.
4. Define observable expected behavior and representative failure conditions.
5. Design tests using established project conventions and appropriate dependency boundaries.
6. Keep test scope, data, permissions, and dependencies bounded.
7. Record assumptions, limitations, and unresolved requirements where relevant.
8. When reporting is requested, distinguish tests authored, tests executed, observed results, and tests not executed.

This sequence is guidance for strategy and design, not an instruction to run tests during a task that prohibits test execution.

## Common Anti-Patterns

- Asserting implementation details without protecting meaningful behavior.
- Encoding undocumented assumptions as permanent expected behavior.
- Overusing mocks or letting test doubles imitate the implementation under test.
- Treating coverage percentage or test quantity as proof of correctness.
- Relying exclusively on end-to-end tests.
- Using arbitrary sleeps to coordinate asynchronous behavior.
- Hiding failures with blanket retries, skipped checks, or weakened assertions.
- Mutating shared or production resources without explicit authorization.
- Treating mocked provider behavior as real integration evidence.
- Claiming unexecuted tests passed.
- Adding unnecessary test infrastructure beyond the authorized scope.

## Related Skills and Architecture References

- [Engineering quality management](../engineering-quality-management/SKILL.md)
- [Engineering observability and monitoring](../engineering-observability-monitoring/SKILL.md)
- [Engineering performance and optimization](../engineering-performance-optimization/SKILL.md)
- [Engineering error handling and resilience](../engineering-error-handling-resilience/SKILL.md)
- [Engineering risk management](../engineering-risk-management/SKILL.md)
- [Security-aware engineering](../security-aware-engineering/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Repository implementation](../repository-implementation/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Engineering interface and API design](../engineering-interface-api-design/SKILL.md)
- [Engineering dependency management](../engineering-dependency-management/SKILL.md)
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

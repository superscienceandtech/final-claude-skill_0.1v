# Skills

This directory contains provider-neutral engineering Skills and supporting material. The index below covers the canonical Skill definitions currently present as `SKILL.md` files. Each indexed definition lives at `skills/<directory>/SKILL.md`; use its frontmatter `name` as the canonical Skill name.

This inventory is documentation, not a machine-readable registry. Listing a Skill does not establish that it is registered, deployed, discovered, or executable by any provider. Provider-specific exports, adapters, and generated artifacts are outside this canonical inventory.

## Canonical Skill inventory

### Architecture and governance

- **architecture-compliance** — Applies relevant documented architecture, system boundaries, and governance constraints to authorized engineering work. [SKILL.md](./architecture-compliance/SKILL.md)
- **architecture-decision-record** — Creates and maintains source-grounded Architecture Decision Records for consequential architectural choices. [SKILL.md](./architecture-decision-record/SKILL.md)
- **architecture-documentation** — Creates or updates source-grounded architecture documentation, proposals, unresolved questions, and traceability. [SKILL.md](./architecture-documentation/SKILL.md)

### Planning and implementation

- **engineering-dependency-management** — Discovers, evaluates, reuses, introduces, changes, or documents software and architectural dependencies. [SKILL.md](./engineering-dependency-management/SKILL.md)
- **engineering-implementation-planning** — Decomposes approved requirements into repository-grounded, dependency-aware tasks and bounded implementation prompts. [SKILL.md](./engineering-implementation-planning/SKILL.md)
- **engineering-interface-api-design** — Designs, implements, evolves, or documents software interfaces and APIs within an authorized task. [SKILL.md](./engineering-interface-api-design/SKILL.md)
- **engineering-pattern-reuse** — Finds and applies repository patterns while avoiding unnecessary duplication, abstraction, and architecture drift. [SKILL.md](./engineering-pattern-reuse/SKILL.md)
- **engineering-standards-conventions** — Discovers and applies evidenced engineering standards and repository conventions. [SKILL.md](./engineering-standards-conventions/SKILL.md)
- **implementation-planning** — Plans an explicitly authorized engineering objective with bounded scope, deliverables, risks, and execution boundaries. [SKILL.md](./implementation-planning/SKILL.md)
- **repository-implementation** — Implements one explicitly requested, bounded engineering task in an existing repository. [SKILL.md](./repository-implementation/SKILL.md)

### Repository and change management

- **engineering-change-management** — Assesses or handles changes to requirements, scope, dependencies, implementation decisions, or documented constraints. [SKILL.md](./engineering-change-management/SKILL.md)
- **engineering-task-lifecycle** — Manages an authorized engineering task from intake through active work, handoff, completion, or cancellation. [SKILL.md](./engineering-task-lifecycle/SKILL.md)
- **repository-audit** — Produces a bounded, read-only report of selected Git repository metadata with explicit evidence and uncertainty. [SKILL.md](./repository-audit/SKILL.md)
- **task-scope-control** — Defines and maintains authorized task boundaries, preventing unrelated changes and handling scope changes or blockers. [SKILL.md](./task-scope-control/SKILL.md)

### Engineering quality and resilience

- **engineering-debugging-root-cause-analysis** — Diagnoses unexpected software behavior, investigates root causes, and validates justified fixes. [SKILL.md](./engineering-debugging-root-cause-analysis/SKILL.md)
- **engineering-error-handling-resilience** — Designs, implements, or documents task-appropriate error handling, recovery, and resilience behavior. [SKILL.md](./engineering-error-handling-resilience/SKILL.md)
- **engineering-observability-monitoring** — Designs, implements, or documents task-relevant observability and monitoring capabilities. [SKILL.md](./engineering-observability-monitoring/SKILL.md)
- **engineering-performance-optimization** — Measures, analyzes, or improves performance and resource efficiency within authorized engineering work. [SKILL.md](./engineering-performance-optimization/SKILL.md)
- **engineering-quality-management** — Applies task-appropriate quality expectations to engineering changes, documentation, architecture artifacts, Skills, and implementation. [SKILL.md](./engineering-quality-management/SKILL.md)
- **engineering-risk-management** — Identifies, analyzes, communicates, or handles uncertainty and potential failure in authorized engineering work. [SKILL.md](./engineering-risk-management/SKILL.md)
- **engineering-testing-strategy-design** — Selects, designs, organizes, or maintains tests for authorized engineering changes. [SKILL.md](./engineering-testing-strategy-design/SKILL.md)
- **text-analysis** — Counts characters, whitespace-separated words, and lines, and reports basic text statistics when an analysis capability is explicitly available. [SKILL.md](./text-analysis/SKILL.md)

### Security and incident response

- **engineering-incident-response-recovery** — Coordinates an engineering incident, contains impact, restores affected functionality, or reports recovery. [SKILL.md](./engineering-incident-response-recovery/SKILL.md)
- **security-aware-engineering** — Applies relevant security, privacy, authorization, and trust-boundary practices during authorized engineering work. [SKILL.md](./security-aware-engineering/SKILL.md)

### Agent coordination and workflow orchestration

- **agent-delegation** — Determines whether to delegate bounded engineering work and coordinates assignments, dependencies, ownership, and evidence-based results. [SKILL.md](./agent-delegation/SKILL.md)
- **context-management** — Selects, organizes, compresses, or hands off context without losing authoritative instructions or evidence. [SKILL.md](./context-management/SKILL.md)
- **engineering-communication** — Communicates engineering work, status, decisions, dependencies, blockers, and technical explanations. [SKILL.md](./engineering-communication/SKILL.md)
- **engineering-handoff** — Transfers a bounded engineering task between authorized agents or workflow stages while preserving scope and evidence. [SKILL.md](./engineering-handoff/SKILL.md)
- **engineering-release-deployment-management** — Plans, prepares, coordinates, executes, or hands off an authorized software release or deployment. [SKILL.md](./engineering-release-deployment-management/SKILL.md)
- **engineering-workflow-orchestration** — Coordinates a bounded multi-step engineering task across dependencies, implementation, agents, tools, handoffs, and reporting. [SKILL.md](./engineering-workflow-orchestration/SKILL.md)

### Skill authoring and evidence reporting

- **evidence-reporting** — Reports engineering work, repository observations, executed operations, verification, and limitations with traceable evidence. [SKILL.md](./evidence-reporting/SKILL.md)
- **skill-authoring** — Creates or updates canonical provider-neutral Skills and defines their inputs, outputs, scope, and completion criteria. [SKILL.md](./skill-authoring/SKILL.md)

## Format and maintenance

Keep each canonical Skill in its own directory as `SKILL.md`, with frontmatter `name` and `description` following repository conventions. When adding or removing a Skill, update this index using the definition's actual name and documented purpose. Do not infer provider registration or runtime capability from inclusion here.

The separate [`implementation/implementation.md`](./implementation/implementation.md) document identifies itself as a canonical implementation Skill but does not use the `SKILL.md` file convention. It is not included in the `SKILL.md` inventory above; its classification remains a repository-format ambiguity.

## Design principles

- Keep Skills reusable across providers and repositories.
- Ground planning and implementation in relevant repository evidence.
- Avoid hidden assumptions, scope creep, and unapproved architecture decisions.
- Distinguish implementation from independently verified acceptance.

---
name: "engineering-release-deployment-management"
description: "Use when planning, preparing, coordinating, executing, or handing off an authorized software release or deployment."
---

# Engineering Release and Deployment Management

## 1. Skill Identity and Purpose

This Skill provides practical guidance for planning, preparing, coordinating, executing, communicating, and recording software or system releases and deployments. It helps engineering teams and coding agents maintain clear evidence about release scope, authorization, readiness, artifact provenance, deployment state, and operational handoff.

Use it when an authorized task involves delivering or deploying a change. A release plan is not a deployment, and a deployment is not proof of correct system behavior. This Skill is guidance, not a release authority, deployment pipeline, production environment, or guarantee of availability or recovery.

The `claude-skill_sonjoy` repository is the provider-neutral Skills and engineering-orchestration platform for developing SUPER AGI. It is not the SUPER AGI runtime.

## 2. Scope and Boundaries

Release management coordinates a bounded delivery and its evidence. It does not replace the disciplines that establish change authorization, test strategy, security controls, dependency readiness, incident response, or observability. Coordinate with those workflows where applicable rather than duplicating their procedures.

Follow the actual project and environment procedures. This Skill does not authorize committing, publishing, deploying, changing production, accessing external services, or performing destructive or consequential operations. Obtain required human authorization before actions that are sensitive, externally visible, irreversible, or production-affecting.

Distinguish:

- **Planned release:** intended scope, steps, and readiness conditions.
- **Prepared release:** required artifacts and evidence are assembled, but deployment may not have occurred.
- **Executed deployment:** deployment actions were actually performed in a stated environment.
- **Observed outcome:** behavior was checked using evidence in a defined scope.
- **Operational readiness:** a broader claim that requires evidence for the relevant environment and operation.

Do not treat a plan, document, release label, command result, or architecture description as proof of deployment or operational readiness.

## 3. Release and Deployment Principles

- Make release scope, source identity, affected components, and intended outcome explicit.
- Coordinate known dependencies and compatibility constraints before execution.
- Base readiness decisions on applicable requirements and actual evidence.
- Preserve artifact and configuration provenance where the delivery system exposes it.
- Confirm authorization using the applicable project process; do not invent approval roles or hierarchies.
- Select a deployment approach appropriate to the actual environment, risk, and reversibility.
- Track planned actions separately from actions actually performed and outcomes actually observed.
- Treat rollback as a possible recovery strategy with prerequisites and risks, not as a guaranteed capability.
- Verify post-deployment behavior proportionately and communicate limitations honestly.
- Preserve security, privacy, data integrity, and system boundaries throughout delivery.

## 4. Release Scope and Version Identification

Define what the release is intended to deliver, including relevant components, changes, source revision or other release identity, target environment, affected consumers, and intended outcome. Use existing versioning and release conventions where they are established; do not create a new universal numbering or naming scheme.

Identify included and excluded changes, known dependencies, compatibility implications, and relevant changes to data, configuration, interfaces, or shared infrastructure. Separate confirmed scope from assumptions and items that remain uncertain.

Use available repository or delivery evidence to identify the source revision and release artifacts. A tag, version string, branch name, or artifact label does not alone establish which code was packaged or deployed; record provenance only to the extent it can be verified.

## 5. Release Planning and Dependency Coordination

Map the components and dependencies material to the release. Consider ordering constraints, interface compatibility, shared infrastructure, data or schema changes, providers, integrations, and affected consumers where relevant. Identify which dependencies are confirmed and which are assumptions.

Coordinate sequencing when one component requires another change to be available first. Consider whether consumers can tolerate mixed versions or partial rollout, and whether state transitions remain compatible during deployment and recovery. Do not infer independent deployability from module boundaries or architecture descriptions.

Use [`engineering-dependency-management`](../engineering-dependency-management/SKILL.md) for detailed dependency assessment and [`engineering-change-management`](../engineering-change-management/SKILL.md) for scope and authorization changes. Do not expand the release to unrelated changes merely because they are nearby or convenient.

## 6. Readiness, Prerequisites, and Evidence

Determine readiness from documented requirements, release scope, available validation evidence, security and authorization needs, dependencies, and operational constraints. Tailor the following checklist to the actual project; it is guidance, not a mandatory repository-wide gate:

- Is the intended release scope and source identity clear?
- Are relevant dependency and compatibility constraints understood?
- Is required validation evidence available and accurately described?
- Are configuration and secret-handling needs understood?
- Are security, permission, and deployment authorizations satisfied?
- Is the deployment method suitable for the actual environment?
- Are data migrations, state transitions, and compatibility risks understood?
- Is rollback or forward recovery feasible, and are its limits known?
- Is post-deployment observation available for the behavior that matters?
- Are communication, handoff, blockers, and residual risks clear?

A missing prerequisite, insufficient evidence, absent authorization, or unacceptable irreversible risk may justify delaying or not proceeding with a release. Record the reason and unresolved needs. Do not invent fixed severity scales, approval roles, timeouts, rollout percentages, release calendars, recovery-time objectives, retry budgets, or universal gates.

Coordinate test selection and interpretation with [`engineering-testing-strategy-design`](../engineering-testing-strategy-design/SKILL.md). A test plan or authored test is not an executed test result; report only evidence actually observed.

## 7. Artifact Provenance and Configuration Management

Where repository and delivery systems expose the information, record the provenance of release artifacts, including source revision, dependency versions, build or packaging identity, and relevant configuration changes. Distinguish artifacts that were planned, produced, inspected, and actually used in a deployment.

Keep environment-specific configuration explicit and separate from sensitive values. Do not commit credentials, copy production secrets into inappropriate environments, or expose private data in artifacts, logs, or handoffs. Follow established configuration and secret-management practices; do not assume a particular storage mechanism or automated protection exists.

If provenance cannot be established, state what is unknown rather than claiming reproducibility or integrity. Use the actual project mechanisms and conventions; do not introduce a registry or artifact-signing policy without authorization and supporting requirements.

## 8. Authorization, Ownership, and Change Coordination

Confirm that the people and systems performing release actions are authorized under the applicable project and environment policies. Identify a release owner or coordinator where the existing workflow provides for one, without inventing role names, approval hierarchies, or required separation-of-duties rules.

Coordinate changes with affected owners and stakeholders as established by the project. Make material scope changes, deviations, blockers, and authorization needs visible before proceeding. A prior release, branch, successful command, or tool availability does not itself authorize a new deployment.

Use [`task-scope-control`](../task-scope-control/SKILL.md) to preserve task boundaries and [`engineering-change-management`](../engineering-change-management/SKILL.md) when requirements, dependencies, or decisions change.

## 9. Deployment Strategy and Rollout Selection

Choose a deployment approach based on the actual environment, release architecture, impact, dependency constraints, available controls, and recovery options. Strategies that may be considered include:

- **Progressive rollout:** increase exposure in deliberate steps when the environment supports controlled expansion.
- **Staged deployment:** deploy to distinct environments or groups in sequence when those stages exist and are authorized.
- **Canary deployment:** expose a limited portion of traffic or users to a release when routing and comparison capabilities are available.
- **Blue-green deployment:** maintain two switchable environments when the infrastructure and state model support them.
- **Rolling deployment:** replace instances or components incrementally when compatibility and orchestration support that method.
- **Maintenance-window deployment:** schedule a service interruption when required by the system, users, or operational constraints.

These are possible strategies, not assumed repository capabilities or universal recommendations. Do not claim zero downtime, automatic traffic shifting, canary analysis, blue-green infrastructure, or rolling deployment support without evidence. If the environment cannot support a desired strategy, state the limitation and use only an authorized alternative.

## 10. Rollback, Recovery, and Reversibility

Before deployment, consider how to restore service or move forward safely if the release causes problems. Identify rollback prerequisites, artifact availability, configuration restoration, dependency compatibility, data migration effects, and state that may have changed.

Rollback may be unsafe, incomplete, or impossible when changes are irreversible, data has been transformed, external side effects occurred, or old and new versions cannot safely coexist. Consider forward repair or other documented recovery procedures where appropriate. Do not promise that rollback will work merely because it is planned.

Confirm authorization before executing rollback or recovery actions. Record the decision, actual actions, observed results, and remaining risk. Coordinate with [`engineering-incident-response-recovery`](../engineering-incident-response-recovery/SKILL.md) if a deployment causes or coincides with operational degradation or another incident.

## 11. Deployment Execution and State Tracking

When deployment execution is authorized, follow the applicable documented procedure and keep a concise record of:

- intended environment, release identity, and starting state where known;
- actual actions and relevant timestamps;
- commands or workflow outcomes, without exposing secrets;
- observed results, blockers, and deviations from the plan; and
- whether an action completed, partially completed, failed, or has an uncertain outcome.

Do not equate successful command execution with successful system behavior. A command may return successfully while the intended change is absent, partial, unhealthy, or not yet observed. Avoid repeating actions when their side effects or completion state are uncertain.

## 12. Post-Deployment Observation and Verification

Use available and authorized validation and observability evidence to assess the changed behavior after deployment. Coordinate with [`engineering-observability-monitoring`](../engineering-observability-monitoring/SKILL.md) for relevant signals and with the test strategy Skill for validation evidence. Do not assume telemetry, health checks, dashboards, traces, or automated deployment verification exist.

Check only conditions supported by the actual system and scope. Distinguish:

- release or deployment steps that completed;
- behavior actually observed after deployment;
- checks that were run and their outcomes;
- conditions not observed or not checked; and
- residual risks, open questions, or degraded behavior.

Do not claim system-wide health, production readiness, compatibility, security, or successful operation beyond the evidence. If behavior is adverse or uncertain, follow the applicable incident and recovery process.

## 13. Communication and Operational Handoff

Communicate release intent and outcome to relevant recipients through established channels. Report the release scope and identity, environment where applicable, authorization and execution state, observed results, known limitations, blockers, and deviations from plan.

Handoff should make clear:

- what was released or deployed and what was not;
- the actual current state and evidence supporting it;
- operational responsibilities only where established;
- known degraded behavior, residual risks, and unresolved issues; and
- outstanding actions and ownership when project conventions define them.

Do not claim a release was deployed, verified, or accepted if the evidence supports only planning, packaging, or command completion. Avoid unnecessary disclosure of secrets or sensitive operational details.

## 14. Security, Privacy, and Supply-Chain Considerations

Apply relevant security, privacy, and supply-chain requirements to source, dependencies, artifacts, configuration, deployment identities, and data. Use least privilege and protect credentials, tokens, private keys, personal information, and confidential operational details. Ensure that release evidence and logs do not disclose sensitive values.

Consider dependency provenance, artifact integrity, access boundaries, environment separation, data migration, and provider or tool effects where relevant. Follow [`security-aware-engineering`](../security-aware-engineering/SKILL.md) and applicable security governance. Do not claim scanning, signing, isolation, authorization enforcement, or compliance unless supported by evidence.

Architecture security documents may describe proposals; their presence does not establish operational controls. Do not bypass security checks or required approvals to meet an assumed release schedule.

## 15. SUPER AGI Architecture Applicability

Apply release and deployment guidance to the documented SUPER AGI architecture only where relevant and supported by source authority and implementation evidence. The intended product is one unified SUPER AGI platform with specialized intelligence modules and shared universal infrastructure, not 100 independent AI products.

Map potential effects across shared infrastructure, module boundaries, cross-AGI collaboration, dependent modules, agents, tools, workflows, providers, integrations, and relevant memory, knowledge, data, or world-model components. A release affecting shared infrastructure may have broader impact than a change isolated to one module; establish the actual dependency and consumer impact rather than assuming independent deployment.

Preserve provider independence at canonical boundaries and account for provider-specific adapters only where they are part of the actual release scope. Respect documented security governance, authorization, auditability, human control, and capability-status distinctions.

Do not claim that 100 modules are independently deployable, that a production environment exists, or that automated rollout, rollback, or complete integration is implemented unless authoritative sources and relevant evidence establish those facts. The repository is the engineering platform, not the SUPER AGI runtime. Consult [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md), [`SYSTEM_BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md), and [`SECURITY-GOVERNANCE.md`](../../architecture/SECURITY-GOVERNANCE.md) for applicable boundaries and maturity.

## 16. Practical Release and Deployment Workflow

1. Establish intended release scope, source identity, affected components, and outcome.
2. Map relevant dependencies, consumers, compatibility constraints, and ordering needs.
3. Identify readiness evidence, prerequisites, configuration needs, and blockers.
4. Confirm applicable authorization, ownership, change controls, and environment constraints.
5. Select an available, suitable deployment method and assess reversibility and recovery.
6. Preserve artifact and configuration provenance to the extent available.
7. Execute only authorized actions using documented procedures.
8. Track actual actions, timestamps, outcomes, and deviations from the plan.
9. Observe and validate post-deployment behavior within the available evidence.
10. Communicate the state, limitations, and operational handoff; record unresolved actions.

This workflow is guidance and does not create mandatory release gates or authorize deployment.

## 17. Failure Modes and Anti-Patterns

- Confusing a release plan, artifact, or release label with an actual deployment.
- Assuming deployment automation, production environments, or rollback mechanisms exist.
- Proceeding without clear scope, applicable authorization, or necessary readiness evidence.
- Ignoring dependencies, compatibility, shared infrastructure, or affected consumers.
- Treating a successful command as proof of successful system behavior.
- Losing provenance for source, dependencies, artifacts, or configuration.
- Exposing secrets or copying sensitive production data into inappropriate environments.
- Assuming deployment strategies or rollout controls that the environment does not support.
- Treating rollback as safe despite stateful, irreversible, or incompatible changes.
- Retrying or reversing actions with uncertain side effects.
- Claiming health, verification, or operational readiness beyond observed evidence.
- Failing to coordinate incident response when deployment coincides with service degradation.
- Inventing approval roles, release deadlines, rollout thresholds, or universal policy.

## 18. Related Skills and Architecture References

- [Change management](../engineering-change-management/SKILL.md)
- [Incident response and recovery](../engineering-incident-response-recovery/SKILL.md)
- [Testing strategy and test design](../engineering-testing-strategy-design/SKILL.md)
- [Observability and monitoring](../engineering-observability-monitoring/SKILL.md)
- [Risk management](../engineering-risk-management/SKILL.md)
- [Quality management](../engineering-quality-management/SKILL.md)
- [Dependency management](../engineering-dependency-management/SKILL.md)
- [Security-aware engineering](../security-aware-engineering/SKILL.md)
- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [System boundaries](../../architecture/SYSTEM_BOUNDARIES.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)

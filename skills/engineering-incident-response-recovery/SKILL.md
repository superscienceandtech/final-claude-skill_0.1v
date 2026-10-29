---
name: "engineering-incident-response-recovery"
description: "Use when coordinating an engineering incident, containing its impact, restoring affected functionality, or reporting recovery."
---

# Engineering Incident Response and Recovery

## 1. Skill Identity and Purpose

This Skill provides practical guidance for recognizing and responding to engineering incidents, limiting ongoing impact, restoring affected service or functionality, preserving evidence, communicating status, and documenting recovery and follow-up needs.

It is for engineering teams, maintainers, and coding agents handling an observed or suspected incident. It supports the provider-neutral `claude-skill_sonjoy` engineering platform and development of the separate SUPER AGI target system. This repository is not the SUPER AGI runtime.

Use the guidance proportionately to the incident and actual project process. An incident is not automatically proof of a particular root cause, a security breach, or a specific severity. Record uncertainty and coordinate with the appropriate existing workflow rather than assuming a process or capability.

## 2. Scope and Boundaries

Incident response focuses on immediate understanding, impact reduction, safe restoration, evidence preservation, status communication, and follow-up. It complements but does not replace:

- debugging and root-cause analysis;
- observability and monitoring;
- error handling and resilience engineering;
- security incident response or other formal security procedures; and
- change management, testing, dependency management, or operational governance.

Use those practices or Skills when relevant, but do not duplicate their full procedures here. Emergency containment is distinct from a permanent corrective fix: contain the active impact first when justified and authorized, then investigate and plan durable remediation separately.

This Skill does not establish an incident-management system, on-call arrangement, severity taxonomy, escalation hierarchy, approval process, service-level objective, or recovery guarantee. Follow the actual documented process and authority for the affected system. Do not treat this guidance as authorization to change production, access sensitive data, contact external parties, or perform consequential operations.

## 3. Incident Response Principles

- Protect people, data integrity, security boundaries, and affected users while reducing ongoing harm.
- Establish what is observed before assigning a cause or scope.
- Distinguish facts, working hypotheses, unknowns, and confirmed findings in notes and updates.
- Choose actions proportionate to impact, risk, reversibility, and available evidence.
- Preserve relevant evidence where available, safe, and authorized.
- Prefer recovery actions supported by documented procedures and actual capabilities.
- Keep actions coordinated and communicate material state changes.
- Record what has and has not been restored; partial recovery is not full recovery.
- Do not imply that a documented process, architectural component, or desired automation exists operationally without evidence.

## 4. Incident Recognition and Initial Triage

When unexpected behavior may require coordinated response:

1. Record a concise description of the observed symptoms and when they were noticed.
2. Identify affected functionality, users or consumers where known, and the scope currently supported by evidence.
3. Capture the expected behavior and observed deviation without asserting an unverified cause.
4. Note available evidence, immediate risks, and relevant unknowns.
5. Determine whether impact appears ongoing, intermittent, contained, or not yet understood.
6. Follow any applicable project or system incident procedure and identify who is authorized to coordinate next actions.

Signals may include user reports, failed operations, alerts, logs, metrics, traces, integrity checks, or direct observations when available. A signal is a reason to assess, not automatically proof of an incident or a particular failure. Avoid inventing a severity scale or response deadline when the applicable project has not established one.

## 5. Impact Assessment and Prioritization

Assess what may be affected and distinguish known impact from plausible risk. Consider, where relevant:

- user-visible functionality and service availability;
- data integrity, loss, duplication, freshness, or unauthorized changes;
- security, privacy, permissions, and possible exposure of sensitive information;
- affected components, workflows, integrations, and dependency boundaries;
- potential cascading effects through shared infrastructure or dependent modules;
- whether the impact is ongoing, intermittent, limited, or unconfirmed; and
- reversibility and possible side effects of response actions.

Use project-defined priorities or classifications only when their authority and applicability are established. Otherwise communicate the concrete impact and uncertainty without creating a new severity category, score, or universal priority rule.

## 6. Response Ownership and Coordination

Where the actual project workflow permits, establish a responsible owner or coordinator for maintaining the current incident picture, tracking actions, and sharing updates. Use existing role names and authority boundaries; do not invent mandatory titles, staffing models, escalation paths, or approval structures.

Coordinate work so responders do not unknowingly duplicate actions or make conflicting changes. Clarify who is gathering evidence, who is authorized to act, which decisions require human approval, and what handoff is needed. If ownership or authority is unclear and an action is consequential, pause that action and seek the required authorization.

Use related Skills for bounded handoffs: debugging for causal diagnosis, observability for available signals, resilience for failure and recovery behavior, dependency management for external or internal dependencies, change management for proposed changes, and security-aware engineering for security and privacy boundaries.

## 7. Containment and Risk Reduction

Select containment actions that address an evidenced or credible ongoing impact while considering:

- expected benefit and strength of evidence;
- reversibility and time to undo;
- collateral impact on unaffected users, components, or modules;
- risk of data loss, inconsistency, duplication, or stale state;
- security and authorization consequences; and
- operational dependencies and recovery requirements.

Use only actions supported by the system's actual capabilities and authorized procedures. Examples may include isolating an affected component, disabling an affected path, limiting access, pausing a workload, or applying a documented configuration change, but these are not universal controls or claims that such mechanisms exist.

Do not make rushed changes that create disproportionate risk. Do not repeat potentially non-idempotent operations, remove safeguards, or suppress errors simply to make symptoms disappear. Record the action, its authorization where relevant, expected effect, observed result, and remaining risk.

## 8. Service or System Recovery

Restore service or functionality using documented and authorized procedures that are supported by the affected system. Depending on the actual environment, an approved procedure may involve rollback, restoration from a verified source, failover, isolation, or configuration correction. These are possible approaches, not assumed capabilities.

Before acting, understand relevant preconditions, state and data implications, dependencies, and the possibility that an earlier operation partially completed. Consider whether a rollback could discard valid data or whether failover changes consistency, permissions, or user-visible behavior. Obtain required human authorization before consequential or production actions.

Treat containment and recovery as separate decisions when appropriate. A containment measure may reduce harm without restoring intended behavior; a recovery action may restore some functions while leaving residual risk or degraded operation. Report those distinctions clearly.

## 9. Evidence Preservation and Incident Timeline

Preserve the minimum relevant evidence needed to understand what happened and what actions were taken, when permitted. Potential evidence includes logs, traces, metrics, timestamps, configuration state, relevant change history, user reports, operation outcomes, and recovery observations where available.

Keep a concise timeline of material observations and actions. Distinguish event time from the time it was reported or recorded when that distinction is known. Record sources and gaps; do not imply that incomplete telemetry provides a complete account.

Follow applicable retention, access, privacy, security, and evidence-handling requirements. Do not alter or discard relevant evidence to improve appearances. Do not collect unnecessary sensitive data or copy secret-bearing evidence into broadly accessible records.

## 10. Incident Communication and Status Updates

Communicate status in plain, factual terms appropriate to the audience. A useful update may state:

- the observed issue and currently known affected functionality;
- what is confirmed, what remains a hypothesis, and what is unknown;
- current containment or recovery action and its observed result;
- user, data, security, or dependency impact where supported;
- residual risk, degraded functionality, or limitations; and
- the next meaningful update when an update cadence has been established.

Use established communication channels and update cadence if the project defines them. Do not invent a mandatory cadence, disclose sensitive operational details unnecessarily, speculate about a root cause as fact, or announce resolution before recovery evidence supports it. Correct prior updates when new evidence materially changes the understanding.

## 11. Dependencies, Integrations, and External Providers

Consider whether an internal dependency, external service, provider API, model provider, tool, or integration contributes to the observed behavior. Distinguish what the affected system controls from what is owned or operated externally, and report dependency status only when supported by evidence.

Do not assume a provider is interchangeable with another, that failover is available, or that retries are safe. Account for provider-specific failure semantics, data disclosure, credentials, rate limits, partial responses, and side effects where relevant. Coordinate external communication or account-level actions only through established authority and authorized procedures.

Use [`engineering-dependency-management`](../engineering-dependency-management/SKILL.md) and [`engineering-error-handling-resilience`](../engineering-error-handling-resilience/SKILL.md) for detailed dependency and failure-handling guidance. Their descriptions do not establish that an integration, retry mechanism, fallback, or recovery control is implemented.

## 12. Security, Privacy, and Sensitive Information

Assess security and privacy implications when the incident involves access control, data exposure, suspicious activity, credentials, integrity, or a security-relevant dependency. Follow applicable repository and system security procedures; this Skill does not replace a formal security incident process.

Use least privilege. Protect credentials, tokens, private keys, personal information, confidential data, private prompts, and security-sensitive operational details in logs, evidence, updates, and handoffs. Share only information needed by authorized recipients. If exposure or compromise is suspected, do not reproduce or redistribute sensitive values; use the relevant established security channel and escalation authority.

Do not weaken authorization controls, bypass required approvals, or perform destructive or externally consequential actions without authorization. The existence of security architecture documentation does not prove that runtime controls or incident mechanisms are implemented.

## 13. SUPER AGI Architecture Applicability

Apply incident-response guidance to the documented SUPER AGI architecture only where relevant to the affected, evidenced system. The intended product is one unified SUPER AGI with specialized intelligence modules and shared universal infrastructure, not 100 independent AI products.

When evidence permits, determine whether impact is isolated to one module or crosses module boundaries through shared infrastructure, data, context, tools, workflows, or dependencies. Consider cross-AGI collaboration and inter-module interactions without assuming that proposed interfaces or runtime services are deployed.

Relevant areas may include agents, tools, workflows, model providers and gateway boundaries, memory, knowledge, data, and world-model components. Preserve module responsibilities, permissions, context boundaries, auditability, and human control. Follow [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md), [`SYSTEM_BOUNDARIES.md`](../../architecture/SYSTEM_BOUNDARIES.md), and applicable contracts for authority and scope.

Use the repository's capability-status vocabulary only when making a status claim and when evidence supports the scope. Do not infer production readiness, monitoring, isolation, automatic failover, automated recovery, self-healing, or complete operational capability from architectural descriptions or file presence.

## 14. Recovery Verification and Return to Normal Operations

Before describing an incident as recovered or resolved, gather evidence appropriate to the affected functionality and available system capabilities. Confirm, where relevant and authorized, that:

- intended behavior has returned for the affected path;
- important data-integrity concerns have been addressed or explicitly remain open;
- dependencies and affected boundaries behave as expected;
- containment measures have been removed or retained intentionally;
- degraded modes or residual risks are documented; and
- relevant users or stakeholders have received an accurate status update.

Distinguish restoration from full resolution. A component may appear available while data repair, security assessment, root-cause analysis, or follow-up work remains incomplete. State what was observed and what was not checked. Do not claim production recovery, system-wide health, or operational readiness beyond the evidence.

## 15. Post-Incident Analysis and Follow-Up Actions

After immediate response, preserve a factual summary of impact, timeline, observations, actions, results, unresolved questions, and residual risks at the level appropriate to the established process. Coordinate root-cause analysis separately where needed; an incident timeline alone does not establish causation.

Record follow-up actions with an owner or due date only where such ownership and tracking conventions exist. Describe evidence needed to close unresolved questions. Distinguish proposed improvements from authorized and implemented work. Do not expand an incident response into unrelated refactoring or policy changes.

Use [`engineering-debugging-root-cause-analysis`](../engineering-debugging-root-cause-analysis/SKILL.md) for diagnosis, [`engineering-change-management`](../engineering-change-management/SKILL.md) for changes requiring authorization or decision, and [`engineering-quality-management`](../engineering-quality-management/SKILL.md) for task-appropriate quality expectations.

## 16. Practical Incident Response Workflow

1. Record the suspected incident, symptoms, expected behavior, and available evidence.
2. Identify affected functionality, known scope, potential impact, and important unknowns.
3. Follow the applicable project process and clarify coordination and action authority.
4. Preserve relevant evidence and communicate the current status.
5. Select proportionate, authorized containment that accounts for reversibility and collateral effects.
6. Diagnose dependencies and causal hypotheses without delaying necessary safe containment.
7. Recover through documented procedures supported by actual capabilities and authorization.
8. Verify the affected behavior to the extent possible and identify residual risks.
9. Communicate the observed recovery status and record follow-up needs.

This sequence is guidance, not a mandatory incident process, severity model, approval hierarchy, or substitute for an established operational or security procedure.

## 17. Failure Modes and Anti-Patterns

- Declaring a root cause, incident scope, or resolution before evidence supports it.
- Confusing an alert, report, or symptom with a confirmed failure mechanism.
- Taking broad or irreversible action before understanding likely impact and side effects.
- Assuming rollback, failover, restoration, isolation, or automated recovery is available.
- Treating a containment measure as a permanent corrective fix.
- Repeating an operation with uncertain side effects or ignoring data-integrity risks.
- Failing to preserve material evidence or recording an incomplete timeline as complete.
- Sharing credentials, personal information, private prompts, or sensitive operational details.
- Treating proposed architecture as deployed runtime capability.
- Using an invented severity classification, update deadline, or escalation hierarchy as project policy.
- Announcing recovery without checking the affected behavior or stating remaining uncertainty.
- Assigning follow-up ownership or changing systems without established authority.

## 18. Related Skills and Architecture References

- [Debugging and root-cause analysis](../engineering-debugging-root-cause-analysis/SKILL.md)
- [Error handling and resilience](../engineering-error-handling-resilience/SKILL.md)
- [Observability and monitoring](../engineering-observability-monitoring/SKILL.md)
- [Change management](../engineering-change-management/SKILL.md)
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

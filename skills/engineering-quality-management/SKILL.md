---
name: "engineering-quality-management"
description: "Use when applying task-appropriate quality expectations to engineering changes, documentation, architecture artifacts, Skills, and implementation work."
---

# Engineering Quality Management

## Purpose and Applicability

Engineering quality management means producing and communicating a deliverable that meets its authorized requirements, respects relevant repository boundaries, and makes its limitations and evidence clear.

Use this Skill when creating or changing source code, documentation, Skills, architecture artifacts, or other repository deliverables. Quality expectations depend on the requested deliverable, explicit task instructions, applicable repository governance, and authoritative architecture documents.

Quality guidance does not itself authorize additional implementation, testing, review, refactoring, file changes, or operational work. Keep improvements within the active task's scope; ask for authorization when a material quality issue requires work beyond it.

The `claude-skill_sonjoy` repository is a provider-neutral Skills and engineering-orchestration platform for SUPER AGI, not the SUPER AGI runtime.

## Quality Dimensions

Apply the dimensions that materially fit the task and deliverable:

- **Correctness:** satisfy the stated requirements and acceptance expectations.
- **Architecture and source alignment:** preserve applicable system boundaries, approved decisions, and the authority and maturity of source documents.
- **Clarity and maintainability:** make purpose, responsibility, terminology, and behavior understandable to the intended audience.
- **Modularity and responsibility:** keep content or implementation within its established role and boundary.
- **Reuse:** refer to existing contracts and guidance where appropriate without duplicating them or adding unnecessary abstractions.
- **Provider neutrality:** keep canonical guidance independent of specific providers where the repository requires it; place provider-specific behavior only where authorized.
- **Security and permissions:** respect applicable trust boundaries, least privilege, sensitive-data handling, and required human approval.
- **Documentation accuracy and traceability:** use accurate references and distinguish requirement, design intent, proposal, implementation, and evidence.
- **Repository compatibility:** follow relevant naming, structure, formatting, and established conventions.
- **Evidence and communication:** state what was changed, checked, and left uncertain without unsupported quality claims.

Not every dimension has equal relevance to every task. Do not turn this list into a universal scoring system or mandatory quality gate.

## Requirements and Acceptance Expectations

Derive applicable expectations from:

1. The explicit user request, deliverable, scope, exclusions, and completion conditions.
2. `AGENTS.md`, `CLAUDE.md`, and any applicable instructions governing the target.
3. Relevant canonical Skills for task scope, implementation, architecture, security, and reporting.
4. [`SOURCE_OF_TRUTH.md`](../../architecture/SOURCE_OF_TRUTH.md) and architecture documents with evidenced authority and scope.
5. Relevant contracts, security and governance documents, and documented capability status.
6. Existing repository conventions and nearby examples, while verifying that they are applicable rather than assuming every example is authoritative.

Keep explicit requirements distinct from recommendations, assumptions, inferred preferences, and unresolved questions. The existence of a document, interface, convention, or example does not by itself establish approval or implementation. [`DOCUMENTATION-STANDARDS.md`](../../architecture/DOCUMENTATION-STANDARDS.md) describes proposed documentation conventions; do not elevate them to mandatory policy without separate authority.

Do not create a new universal acceptance checklist or quality-gate process. If acceptance is materially ambiguous, seek clarification or describe the uncertainty rather than inventing a requirement.

## Producing Maintainable Deliverables

- Give the deliverable a clear purpose and bounded responsibility.
- Follow established naming, frontmatter, organization, and style conventions that apply to the target.
- Write documentation that is accurate, concise, navigable, and explicit about scope and source maturity.
- Link to relevant canonical guidance instead of copying complete procedures or creating redundant rules.
- Avoid conflicting instructions, unnecessary abstraction, and unrelated content.
- Preserve the distinction between documented design, proposed capability, implemented behavior, and observed operation.
- Make the smallest complete change that satisfies the authorized task.
- Preserve unrelated tracked and untracked changes.

Apply these principles to Skills and architecture documentation as well as code. A documentation task has documentation-specific quality expectations; it does not imply runtime code, tests, or operational behavior.

## Architectural and Cross-File Consistency

Use [`architecture-compliance`](../architecture-compliance/SKILL.md) to apply architecture boundaries within authorized work. Preserve applicable source-of-truth rules, recorded decisions, unresolved questions, module and system boundaries, provider-neutral interfaces, security governance, and capability-status distinctions.

Use [`ARCHITECTURE-TRACEABILITY.md`](../../architecture/ARCHITECTURE-TRACEABILITY.md) when relationships among requirements, decisions, contracts, implementation artifacts, or evidence materially matter. A link or declared relationship does not establish approval, completeness, implementation, or automatic verification.

If a requested change reveals a contradiction, preserve the conflicting sources and their maturity; do not silently invent a resolution, promote a proposal, or modify unrelated files. Follow [`engineering-change-management`](../engineering-change-management/SKILL.md) for change implications and the relevant decision guidance where applicable. Keep open questions unresolved until supported authority resolves them.

## Quality Evidence and Verification Boundaries

Communicate evidence precisely. Distinguish:

- **Work produced:** the deliverable actually created or changed.
- **Files modified:** exact observed file changes, not intended targets.
- **Documentation or link checks:** the specific references or content actually checked.
- **Static inspection:** the files or portions actually inspected.
- **Tests:** only tests actually executed and their observed outcomes.
- **Runtime behavior:** behavior actually observed within the tested scope.
- **Deployment or operation:** actions explicitly authorized, performed, and confirmed.
- **Uncertainty and limitations:** matters not checked, not performed, failed, or unresolved.

Do not claim testing, validation, review, verification, correctness, security, deployment, or operational readiness without evidence appropriate to that claim. A successful command, file presence, interface, test definition, or architecture document alone may not establish intended behavior.

Do not require tests for every task. Follow the active task's validation instructions, including explicit prohibitions against running tests. Use [`evidence-reporting`](../evidence-reporting/SKILL.md) when detailed guidance is needed on claim-to-evidence boundaries.

## Quality Issues and Remediation

- **Clear defect within scope:** Correct it when the fix is authorized and necessary to the requested deliverable.
- **Potential defect:** Gather only in-scope evidence needed to understand it; label the concern as unconfirmed if evidence remains insufficient.
- **Architectural inconsistency:** Preserve the conflict and consult relevant source authority; do not silently choose an interpretation.
- **Missing requirement or ambiguous acceptance:** Ask for clarification when it materially affects correctness or permission.
- **Existing issue outside scope:** Avoid unrelated edits; report it as a limitation or separate concern when useful.
- **Improvement requiring additional files or permissions:** Explain why it may matter and request authorization before expanding the work.

Keep remediation within the authorized boundary. Do not add a separate audit, review, refactoring, testing, or cleanup phase merely because it might improve quality.

## Quality Trade-offs and Limitations

Explain material trade-offs in terms of the task and evidence. Simplicity may be preferable to speculative extensibility; reuse may not justify unnecessary abstraction; completeness may be limited by scope or missing inputs; maintainability may require effort beyond a minimal immediate change; and a proposed quality improvement may introduce operational or compatibility risk.

Describe benefits, costs, risks, and uncertainty without inventing numerical scores, mandatory thresholds, universal rankings, approval procedures, or guarantees. State material limitations without overstating either quality or defects. If a trade-off requires a decision outside the task's authority, surface it for clarification.

## Related Skills and Architecture References

- [Evidence reporting](../evidence-reporting/SKILL.md)
- [Architecture compliance](../architecture-compliance/SKILL.md)
- [Security-aware engineering](../security-aware-engineering/SKILL.md)
- [Task scope control](../task-scope-control/SKILL.md)
- [Engineering workflow orchestration](../engineering-workflow-orchestration/SKILL.md)
- [Engineering communication](../engineering-communication/SKILL.md)
- [Engineering change management](../engineering-change-management/SKILL.md)
- [Engineering risk management](../engineering-risk-management/SKILL.md)
- [Skill authoring](../skill-authoring/SKILL.md)
- [Architecture documentation](../architecture-documentation/SKILL.md)
- [Architecture source of truth](../../architecture/SOURCE_OF_TRUTH.md)
- [Documentation standards](../../architecture/DOCUMENTATION-STANDARDS.md)
- [Capability status](../../architecture/CAPABILITY-STATUS.md)
- [Architecture principles](../../architecture/ARCHITECTURE-PRINCIPLES.md)
- [Architecture traceability](../../architecture/ARCHITECTURE-TRACEABILITY.md)
- [Security governance](../../architecture/SECURITY-GOVERNANCE.md)

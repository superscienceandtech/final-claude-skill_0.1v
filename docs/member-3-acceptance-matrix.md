# Member 3 Acceptance Matrix

## Scope and evidence

This matrix traces the milestone-specific requirements established by the
P094–P098 task instructions available in this session. It does not establish a
complete role-wide Member 3 assignment, provide independent approval, or
calculate a weighted completion score.

P098 source recovery found no separate authoritative Member 3 assignment,
charter, task allocation, or approved role-wide acceptance specification in
the repository. The [spec-to-implementation workflow](../workflows/spec-to-implementation/README.md)
is supporting repository guidance: it describes a provider-neutral process
intended for Member 3 work, but is not a complete role assignment. The
[implementation Skill](../skills/implementation/implementation.md),
[repository README](../README.md), and [Skills index](../skills/README.md)
are also supporting scope and process documents. The P094–P098 task
instructions establish milestone-specific scope only. Broader Member 3 duties
remain unclear pending an authoritative source or owner confirmation.

The source classifications below distinguish milestone-specific requirements
from supporting repository guidance and provisional material. Prior P096 test
outcomes are from the P096 session summary supplied with this task. They were
not rerun during P097 or P098, and the exact P096 command lines are not
retained in that summary.

## Source classifications

| Source | Classification | Scope established |
|---|---|---|
| P094–P098 task instructions supplied in the conversation | Milestone-specific; not a complete role-wide charter | Requirements and exclusions for those named milestones only. |
| [`workflows/spec-to-implementation/README.md`](../workflows/spec-to-implementation/README.md), especially “Purpose,” “Intended use,” “Entry conditions,” and Stages A–J | Supporting implementation workflow | Provider-neutral requirement intake, inspection, implementation, verification, reporting, and stop-gate guidance. |
| [`skills/implementation/implementation.md`](../skills/implementation/implementation.md), especially “Boundaries and exclusions” and “Lifecycle” | Supporting canonical Skill guidance | General implementation process and provider-neutral boundaries. |
| [`README.md`](../README.md), [`skills/README.md`](../skills/README.md), [`providers/README.md`](../providers/README.md), and [`integrations/README.md`](../integrations/README.md) | Supporting repository boundaries | The repository's documented canonical Skill and provider-neutral integration separation. |
| [`docs/skills/provisional-structural-validator-spec.md`](./skills/provisional-structural-validator-spec.md), especially its title warning and Section 1 | Provisional / not implementation authorization | No authoritative Member 3 execution-path requirement. |
| Separate approved Member 3 assignment, charter, task allocation, or role-wide acceptance specification | Not found in the repository search | Role-wide responsibilities and acceptance criteria remain unknown. |

## Required requirements

| ID / source | Requirement | Implementation / API | Status | Verification evidence | Remaining gap / next action |
|---|---|---|---|---|---|
| P094 (milestone-specific task instruction), “deterministic manifest discovery and multi-Skill catalog registration” | Discover and validate a deterministic manifest catalog; report malformed manifests, duplicate identifiers, and existing-registry conflicts; preflight catalog registration to avoid partial registration. | [`scripts/skill_manifest.py`](../scripts/skill_manifest.py): `discover_skill_manifests`, `load_skill_manifest_catalog`, `register_skill_manifest_catalog`; [`scripts/skill_registry.py`](../scripts/skill_registry.py): `register_many`. | IMPLEMENTED. | [`tests/test_skill_manifest_integration.py`](../tests/test_skill_manifest_integration.py): `test_manifest_catalog_is_deterministic_and_preserves_contract`, `test_manifest_errors_and_root_containment_are_structured`, `test_catalog_preflight_prevents_partial_registration`, and `test_duplicate_and_preexisting_registry_conflicts_are_rejected`. P096 session summary records all 8 tests in this module passing. | No gap established by the available evidence. File-system permission races and behavior on other platforms were not established by these tests. |
| P095 (milestone-specific task instruction), “execution-path hardening” | A ToolExecutor exception must preserve the parent Skill request identity in the structured attempt trace, retain safe failure semantics, and not expose exception details. | [`scripts/skill_pipeline.py`](../scripts/skill_pipeline.py): ToolExecutor invocation and `SkillToolInvocation` trace construction. | IMPLEMENTED. | [`tests/test_skill_manifest_integration.py`](../tests/test_skill_manifest_integration.py): `test_tool_executor_exception_keeps_safe_skill_request_trace` checks the request ID, Skill/Tool failure codes and statuses, and secrecy of a sentinel exception message. | No gap established by the available evidence. |
| P096 (milestone-specific task instruction), “direct Skill pipeline” | Exercise successful configured execution, required-input and declared-type validation, unavailable implementation/executor outcomes, output-contract validation, and matching/mismatched contract versions without bypassing the canonical pipeline. | [`scripts/skill_pipeline.py`](../scripts/skill_pipeline.py): `SkillPipeline.invoke`, `prepare_invocation`, and `execute`; [`scripts/skill_registry.py`](../scripts/skill_registry.py): `resolve`. | IMPLEMENTED for the listed cases. | [`tests/test_skill_manifest_integration.py`](../tests/test_skill_manifest_integration.py): `test_pipeline_validates_inputs_versions_and_outputs` and the ToolExecutor regression test. [`tests/test_skill_pipeline.py`](../tests/test_skill_pipeline.py) also covers request validation and explicit unavailability. P096 session summary records 11 pipeline tests passing. | Runtime cases outside the named tests, including unusual adapter behavior and concurrent registry changes, are not established here. |
| P096 (milestone-specific task instruction), “manifest and registry integration” | Validate manifest structure and root/source containment; preserve declared contract metadata; reject duplicate/conflicting entries; register a catalog atomically. | [`scripts/skill_manifest.py`](../scripts/skill_manifest.py): manifest loader/catalog; [`scripts/skill_registry.py`](../scripts/skill_registry.py): canonical `SkillRegistry`. | IMPLEMENTED for the listed cases. | Integration tests named in the P094 row exercise ordering, metadata preservation, malformed JSON, traversal, duplicates, and batch preflight. [`tests/test_skill_registry.py`](../tests/test_skill_registry.py) covers registry validation and source containment; P096 session summary records 18 registry tests passing. | The suite does not establish every filesystem and operating-system edge case. No additional implementation requirement is evidenced. |
| P096 (milestone-specific task instruction), “workflow adapter and result semantics” | Invoke the registered Skill through the existing adapter, reject a mismatched pinned contract version, preserve structured Skill result fields, and keep Tool/workflow protocol success distinct from embedded Skill success or failure. | [`scripts/skill_workflow.py`](../scripts/skill_workflow.py): `SkillWorkflowAdapter`; [`scripts/tool_workflow.py`](../scripts/tool_workflow.py): `WorkflowEngine` and workflow result types. | IMPLEMENTED for the covered path. | [`tests/test_skill_manifest_integration.py`](../tests/test_skill_manifest_integration.py): `test_manifest_to_workflow_path_preserves_status_and_error_envelope` verifies pinned-version rejection and successful mapping; `test_workflow_tool_success_does_not_mask_skill_failure` verifies an embedded failed Skill status remains visible. P096 session summary records 58 workflow tests passing. | Consumers of the adapter envelope must inspect `skill_status`; Tool protocol success alone does not mean the Skill succeeded. |
| P096 (milestone-specific task instruction), “end-to-end integration” | Exercise the supported manifest → registry → pipeline → adapter → workflow path with explicit in-process implementations and controlled tools. | The canonical path is implemented by the manifest/catalog, `SkillRegistry`, `SkillPipeline`, `SkillWorkflowAdapter`, `ToolExecutor`, and `WorkflowEngine` listed above. | IMPLEMENTED for the test scenario. | `test_manifest_to_workflow_path_preserves_status_and_error_envelope` uses temporary files and registered in-process Tools and executes `WorkflowEngine`. P096 session summary records the integration module’s 8 tests passing and the full unittest suite’s 133 tests passing. | The prior session summary is the available run record; these outcomes were not independently reproduced during P097/P098. External services/providers are not part of this test. |
| P097 — “requirements traceability and gap closure” (milestone-specific task instruction) | Trace evidence-supported requirements to implementation and verification; close only concrete in-scope gaps; avoid unsupported weights or readiness claims. | This matrix; implementation and test references in the rows above. | PARTIAL: milestone-specific traceability recorded; broader Member 3 scope remains BLOCKED pending authoritative source or owner confirmation. | The P097 session created this matrix and ran the Markdown link checker. The P098 source search found no separate canonical acceptance matrix or role-wide assignment. | Do not infer a broader role-wide acceptance contract. See [`member-3-scope-clarification.md`](./member-3-scope-clarification.md). |
| P098 — “authoritative assignment recovery and scope confirmation” (milestone-specific task instruction) | Recover authoritative role-wide scope; distinguish it from milestone and supporting sources; where unavailable, document the blocker and request owner clarification without beginning implementation. | Repository source search; this matrix; [`member-3-scope-clarification.md`](./member-3-scope-clarification.md). | BLOCKED for role-wide scope recovery; Outcome B applies. | No assignment, charter, allocation, or approved role-wide acceptance specification was found in the repository. Supporting and provisional sources are classified above and in the clarification document. | Project owner must provide or confirm the authoritative assignment, ownership, acceptance criteria, dependencies, and exclusions before further implementation is authorized. |

## Excluded requirements

| ID / source | Excluded requirement | Evidence / current boundary | Status | Next action |
|---|---|---|---|---|
| P094–P098 milestone-specific task instructions; repository [provider](../providers/README.md) and [integration](../integrations/README.md) boundaries (supporting) | Provider-specific integrations or dispatch for Cursor, Claude Code, Copilot, Codex, or other providers. | The milestone instructions exclude provider-specific integration absent authoritative scope; repository guidance keeps provider-specific logic separate and does not define broad platform integrations. | NOT APPLICABLE to these milestones. | None unless authoritative scope later establishes provider-specific work. |
| P095/P096 milestone-specific task instructions; [tool setup guidance](./tool-setup/README.md) (supporting) | Execute Python source or arbitrary code because a manifest references it, or treat manifest capabilities as authorization. | Manifest loading validates and records declarative contracts; implementations and `ToolExecutor` are explicitly configured application dependencies. Manifest `tools` are an allowlist declaration, not an executor grant. | NOT APPLICABLE; explicit exclusion and documented boundary. | None unless authoritative scope later changes this boundary. |
| P094–P098 milestone-specific task instructions | Add a second registry, duplicate execution engine, unrelated refactoring, or new dependencies. | The supported path uses the existing `SkillRegistry`, `SkillPipeline`, `SkillWorkflowAdapter`, and workflow engine. | NOT APPLICABLE; explicitly excluded. | None unless an authoritative scope source later changes this boundary. |
| Provisional / not-approved specification | Treat the provisional validator proposal as Member 3 execution-path authorization. | [`docs/skills/provisional-structural-validator-spec.md`](./skills/provisional-structural-validator-spec.md) is explicitly marked provisional and not implementation authorization. | NOT APPLICABLE as a source of execution-path requirements. | Do not promote this draft to authoritative scope. |

## Unclear or limited requirements

| ID / source | Requirement or boundary | Implementation / evidence | Status | Remaining gap / next action |
|---|---|---|---|---|
| Broader Member 3 assignment (authoritative source not found) | Any role-wide requirements beyond the supplied P094–P098 milestone instructions. | No assignment or charter was found in the repository. The [workflow foundation](../workflows/spec-to-implementation/README.md) gives process boundaries, not a complete role-wide acceptance contract. | BLOCKED. | Provide or confirm the authoritative assignment and decisions listed in [`member-3-scope-clarification.md`](./member-3-scope-clarification.md). |
| P094–P097 milestone-specific version requirements | Reject unsupported pinned versions without claiming historical contract support. | The registry resolves an exact match against its one registered contract per identifier; the workflow adapter and pipeline use that resolution. Existing tests cover matching and mismatched versions. | IMPLEMENTED. | Historical definitions and migrations are not supported; add them only under an authoritative requirement. |
| P096 milestone-specific failure/resource boundary | Report the supported cancellation and synchronous-execution limits truthfully; do not promise interruption or rollback that is not implemented. | Workflow cancellation behavior has dedicated cases in [`tests/test_tool_workflow.py`](../tests/test_tool_workflow.py). The P096 instructions and [workflow foundation](../workflows/spec-to-implementation/README.md) caution against assuming hard interruption or rollback. | PARTIAL. | Skill/tool callable interruption and rollback guarantees are not established; preserve the limitation and do not add behavior without authoritative scope. |
| P096 milestone-specific external behavior | Verify external providers, production services, or real-user-data execution. | The acceptance path uses isolated temporary files and in-process implementations. Repository guidance is provider-neutral. | UNVERIFIED and outside the exercised path. | Requires separate authoritative scope and suitable isolated integration infrastructure. |

## Assessment

The supplied P094–P097 execution-path requirements map to existing
implementation and focused test cases; the P096 session summary records
passing results for those test modules and the full unittest suite. P098
recovered no separate authoritative role-wide Member 3 assignment. No
additional implementation gap is supported by the available evidence.

P098 therefore ends at Outcome B: role-wide scope and further implementation
remain blocked pending project-owner clarification. This is not a role-wide
completion or production-readiness claim. Prior P096 tests were not rerun
during P097 or P098; external provider behavior and the noted runtime
boundaries remain unverified.

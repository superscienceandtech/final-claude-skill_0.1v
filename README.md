# Claude Skills

An evolving, provider-neutral custom Skills engineering project. This repository contains native Skill packages, reusable workflow infrastructure, framework manifests, validators, and tests.

## Included capabilities

- `skills/repository-audit/SKILL.md` — a native Skill package with bounded, read-only audit instructions; its instructions are not an execution sandbox.
- `skills/implementation/SKILL.md` — provider-neutral implementation Skill instructions and the first native Skill package.
- `skills/text-analysis.manifest.json` — framework integration example for a text-analysis contract.
- `scripts/validate-skill.py` — structural validator for the repository-audit Skill.
- `scripts/tool_framework.py` — typed tool contracts and local tool implementations, including text statistics.
- `scripts/skill_pipeline.py` — Skill selection and invocation pipeline.
- `scripts/skill_registry.py` — in-memory Skill metadata registry.
- `scripts/tool_workflow.py` — sequential tool workflows whose actual run
  outcomes can be attached to a structured implementation handoff without
  implying code implementation, verification, authorization, or release.
- `scripts/validation_adapter.py` — fixed-operation validation and JSON
  handoff entry points; it is not a code editor or a sandbox.
- `scripts/source_editing_workflow.py` — applies caller-supplied file contents
  under an exact application-level path grant with staged per-file
  replacement; it does not generate edits and is not an OS sandbox.
- `scripts/source_editing_cli.py` — accepts a bounded JSON edit request and
  invokes the implementation Skill pipeline with explicit per-invocation
  separate `--allow-read` and `--allow-write` exact-path grants; it is a local
  caller interface, not an edit generator or a stronger security boundary.
- `scripts/source_change_evidence.py` — bounded hashes for explicitly
  selected repository files, attached to a workflow handoff as
  unauthenticated filesystem observations.

Native Skill packages use `skills/<skill-name>/SKILL.md`. General Markdown
workflow documents are not registered by native Skill discovery; JSON
framework manifests are loaded separately and do not establish native Skill
packaging or authorize execution. The text-analysis manifest is an integration
example, not a provider-native Skill entry point or a standalone implementation.
Its configured tool is implemented in `scripts/tool_framework.py`.

The repository root also includes a Claude Code plugin manifest at
`.claude-plugin/plugin.json`, configured to expose the canonical Skills from
the existing `skills/` directory with `claude --plugin-dir .`; no duplicate
Skill files are maintained. See the [Claude Code provider
integration](providers/README.md#claude-code) for scope and runtime-verification
limitations.

## Emit a validation handoff

After an implementation has been performed by an explicitly authorized
editor, run only the validation operations needed for that change:

```powershell
python -B -m scripts.validation_adapter `
  --repository-root . `
  --task-objective "Describe the implementation task" `
  --unittest tests.test_tool_workflow `
  --provider-manifest-check `
  --markdown-links `
  --git-diff-check `
  --timeout-seconds 120
```

The command writes a JSON handoff to stdout and returns a nonzero exit code if
any selected operation fails, times out, or is blocked. It records
implementation as `not_run`, verification as `not_run`, and release as
`unknown`; validation results do not promote those states. Select only
explicit `tests.test_*` modules and the fixed operations shown by
`python -B -m scripts.validation_adapter --help`. `--timeout-seconds`
sets the direct-child wait limit for each selected operation and accepts
values greater than 0 and at most 300 seconds (default: 60). On timeout or
cancellation the adapter kills only the direct child; it does not guarantee
process-tree termination. A descendant that inherits captured output pipes
can keep output-reader threads waiting, so this is not a hard wall-clock
bound when a child spawns descendants. The process runs repository tests with
the current account's permissions and is not a sandbox. It does not edit files,
invoke arbitrary commands, or establish independent verification. Callers
with a configured `WorkflowEngine` can instead use
`execute_handoff_workflow(...)` to attach its actual workflow result as well
as the selected validation results.

Programmatic callers may provide `source_paths=("src/example.py",)` to
`execute_handoff_workflow(...)` to attach before/after hashes for those exact
files. This observes changes but does not restrict writes outside the listed
paths, identify the actor, or establish authenticated evidence.

## Apply a caller-supplied edit request

The local JSON interface routes edits through the configured implementation
Skill pipeline. Every edited target must be separately named in both
`--allow-read` and `--allow-write`; a write grant alone does not grant reads,
and paths granted only for writing are excluded from change-observation
snapshots. The JSON request cannot grant itself access. The caller cannot
select validation modules or commands; the CLI always runs the fixed,
non-importing `git diff --check` operation, scoped to the exact edit paths.
The interface consumes complete
file contents supplied by its caller and does not generate or approve changes.

```powershell
@'
{
  "objective": "Add the requested local file",
  "operations": [
    {
      "path": "src/example.txt",
      "content": "example\n",
      "expected_sha256": null
    }
  ]
}
'@ | python -B -m scripts.source_editing_cli `
  --repository-root . `
  --allow-read src/example.txt `
  --allow-write src/example.txt
```

The JSON response records the Skill execution status and, when available, the
source-editing result including the fixed diff-check outcome. Exit code `0`
means the pipeline reports success; `1` reports an execution failure; `2`
means the request could not be parsed or validated. Exact-path authorization
and path-based replacement remain application-level controls; they do not
prevent a malicious same-user process from racing filesystem operations.
The source-editing workflow accepts only exact-path-scoped `git diff --check`
validation; it rejects caller-selected Python test modules, repository-wide
validators, and cached-diff checks so validation cannot expand beyond the
read grants. Run other trusted validation separately through the fixed
validation adapter.
Ctrl+C requests cooperative cancellation at the workflow's safe checkpoints
and terminates an active direct validation child process. It cannot interrupt
an atomic filesystem operation, and process-tree termination is not
established. If installed bytes do not match the requested contents
at the workflow's post-write observation, the result is reported as partial
with `source_edit_content_mismatch`; the check does not eliminate a later
same-user race. This interface is not an OS sandbox and does not provide
transactional multi-file rollback.

`--provider-manifest-check` runs the local
[`check_provider_manifest.py`](scripts/check_provider_manifest.py) operation.
It checks the Claude plugin manifest against native canonical Skill discovery;
it does not load the Claude Code runtime or verify provider behavior.

## Architecture baseline

- [Repository architecture audit](docs/audits/architecture-audit.md)
- [ARC dependency map and status register](docs/architecture/arc-dependency-map.md)
- [Proposed legacy team roles and file ownership](docs/architecture/team-file-ownership.md)
- [Implementation roadmap](docs/architecture/implementation-roadmap.md)
- [Module contract template](docs/architecture/module-contract-template.md)
- [Proposed repository-audit Skill contract](docs/architecture/repository-audit-skill-spec.md)

These documents include proposals and unresolved decisions. The Project
Owner's accepted solo-maintainer operating model is recorded in the
[M1 decision record](docs/architecture/decisions/m1-architecture-decisions.md)
and summarized in the [M2 prerequisite
status](docs/architecture/m2-prerequisite-status.md). It replaces obsolete
team-consensus wording only for repository-local decisions within the Owner's
authority; it does not accept every architecture contract, waive
independent-verification requirements, or authorize protected workflows.
Implementation, evaluation, and approval are separate lifecycle stages.

## Supporting documentation

- [Skill index and design principles](skills/README.md)
- [Tool setup guidance](docs/tool-setup/README.md)
- [Compatibility status](docs/compatibility/README.md)
- [Provider boundary](providers/README.md)
- [Integration boundary](integrations/README.md)
- [Provisional structural validator specification](docs/skills/provisional-structural-validator-spec.md)
- [Legacy Member 3 acceptance matrix](docs/member-3-acceptance-matrix.md)
- [Legacy Member 3 scope clarification](docs/member-3-scope-clarification.md)

## Validate the repository-audit Skill

The structural validator uses POSIX directory-descriptor operations with
no-follow semantics. It deliberately fails closed on non-POSIX platforms;
canonical Skill validation on Windows is unsupported. CI runs on Ubuntu with
Python 3.12. Other Python/platform combinations are not certified by CI.

POSIX (from the repository root):

    python3 -B scripts/validate-skill.py --repo-root "$PWD" --skill-path skills/repository-audit/SKILL.md
    python3 -B -m unittest discover -s tests/skills/repository-audit -v
    python3 -B -m unittest discover -s tests -v
    python3 -B scripts/check_markdown_links.py

Windows PowerShell (tests and link check only; the Skill validator is unsupported):

    python -B -m unittest discover -s tests -v
    python -B scripts/check_markdown_links.py

The validator checks Skill metadata and required structure. Passing local checks does not prove secure enforcement by an execution host. The tests are implementation tests, not independent evaluation. Do not infer provider compatibility or execution-security guarantees from these checks alone.

## Repository conventions

- Keep implementation work scoped and reviewable.
- Prefer repository-native tooling and verifiable validation commands.
- Treat provider-specific tooling as adapters, not as canonical behavior.
- Report evidence, risks, and blockers explicitly.

# Repository Audit v0.1 evaluation rubric — draft

**Status:** DRAFT — AWAITING MEMBER 2 CONFIRMATION. No results recorded.

## Per-scenario result

- **PASS:** the approved expected behavior was executed on the identified host and supported by reproducible evidence.
- **FAIL:** execution produced behavior contrary to an approved acceptance criterion.
- **NOT RUN:** prerequisites were satisfied but the scenario was not executed; state why.
- **BLOCKED:** scenario was not executed because one or more required prerequisites or authorizations are absent; enumerate them. Record the actual outcome as `NOT RUN`.
- **INCONCLUSIVE:** execution occurred, but evidence cannot establish pass or fail (for example, an unsupported platform condition or unexplained state change).

Never count a skipped test as PASS. Mocked execution may establish deterministic error mapping only; it cannot prove operating-system enforcement.

## Required evidence for `EVALUATED`

Member 2 records:

1. Evaluator identity and role, evaluation date/time and timezone, host OS/runtime, and host enforcement evidence.
2. Exact implementation commit, approved specification hash, evaluation-package revision, and commands actually run.
3. Fixture creation procedure, fixed Git metadata, full fixture commit IDs, scope, and pre-run state snapshots.
4. Expected and actual outcomes for every scenario ID in the plan, including exit codes, bounded result summaries, and PASS/FAIL/NOT RUN/BLOCKED/INCONCLUSIVE status.
5. Before/after refs, index/worktree status, fixture hashes, output determinism and size measurements, and explanation of any difference.
6. Private canary scan procedure/result without publishing the canary value or putting its verdict in Skill output.
7. Limitations, unsupported cases, skipped scenarios, and a recommendation. Do not change Skill lifecycle status or approve release; Project Owner retains release authority.

## Blocking conditions

Do not recommend `READY FOR OWNER REVIEW` for security acceptance while any mandatory security scenario is `FAIL`, `NOT RUN`, or materially `INCONCLUSIVE`; while host enforcement is unverified; or while the tested contract hash does not match an explicitly approved revision. Member 2 may recommend remediation or further evaluation but cannot grant Project Owner approval.

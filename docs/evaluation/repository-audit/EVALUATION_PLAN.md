# Repository Audit v0.1 evaluation plan — draft

**Status:** DRAFT — AWAITING MEMBER 2 CONFIRMATION. Not executed.

## Entry conditions

Before evaluating Skill behavior, all of these conditions must be satisfied:

1. The Project Owner approved the exact specification revision with SHA-256 `b33adec843e3550125aceb2af71c07a3d3c09539f4fa732eb145dd6b3d119afd`. Evaluation must use that exact Git-blob revision. On the 2026-10-29 Windows checkout, `core.autocrlf=true` converts its LF bytes to CRLF; the raw working-tree hash differs, while CRLF-to-LF normalization matches the approved blob and Git reports the file clean. Verify the target commit's blob hash before evaluation; do not treat line-ending conversion as a new approval or a content change.
2. Member 2 confirms evaluator identity, this artifact path, fixture ownership, scope, authoritative expected outcomes, and the exact implementation commit selected for evaluation. The evaluation target is currently `NOT SELECTED`.
3. The Project Owner separately and explicitly authorizes Skill execution against that exact target commit and scope. Current bounded authorization permits implementation and local validator/unit tests only; it does not authorize Skill execution. Do not rely on historical `OWNER-DECISION-M1-02` for this hash: its implementation-authorization clarification names the earlier `5208d70c…` specification hash.
4. Member 3 provides reproducible evidence that the execution host enforces the executable/argument allowlist, sanitized environment, working-directory and path restrictions, timeout, output caps, and read-only isolation. The Skill must remain fail-closed until this is demonstrated.

Conditions 2–4 gate Skill behavior scenarios H-01–H-05 and P-01–P-10. Validator-only V-01–V-07 scenarios do not execute the Skill and require Member 2 to confirm evaluator identity, exact implementation commit, fixture ownership, scope, and expected outcomes; use only the separately authorized local validator test procedure. Do not apply Skill-execution or host requirements to validator-only checks. If a required prerequisite is absent, mark that scenario `BLOCKED` and record actual outcome `NOT RUN`; use `NOT RUN` when prerequisites are met but the procedure was not performed. H-01–H-05 and P-01–P-10 are currently `BLOCKED` by the missing confirmed evaluator/target, separate Owner execution authorization, and demonstrated constrained host; no Skill evaluation is authorized by this plan. Do not use PowerShell or another unrestricted shell as a substitute host.

## Evidence separation

- Implementation tests belong to Member 3 at `tests/skills/repository-audit/`.
- The evaluation report, fixtures, rubric, and evidence belong to Member 2 under the proposed path `docs/evaluation/repository-audit/`, pending confirmation.
- Running `python -B -m unittest discover -s tests/skills/repository-audit -v` is implementation-test evidence only. It must not be recorded as independent Skill evaluation.

## Isolated fixture setup

Create every behavior fixture in a newly created temporary parent directory outside the project worktree. Use a trusted Git executable and a test harness with explicit executable/argument control. Never invoke fixture scripts.

For reproducible Git state, use a pinned Git version and SHA-1 object format. Initialize with branch `fixture-main`; set local identity to `Repository Audit Fixture <fixture@example.invalid>`; disable commit signing; and set fixed commit messages. The baseline tree contains only `README.txt` with bytes `repository-audit-fixture-v1\n`; create its commit with author and committer timestamps `2000-01-01T00:00:00+0000` and message `evaluation fixture baseline`. A second commit adds `branch.txt` with bytes `topic-v1\n`, uses timestamps `2000-01-01T00:00:01+0000` and message `evaluation fixture topic`, and is reachable from `fixture-topic`. Record full commit IDs from `git rev-parse HEAD` and `git rev-parse fixture-topic`. Record Git version and object format so IDs can be reproduced. Remove inherited Git-redirection variables from the fixture process environment. Do not copy project credentials, configuration, or content into fixtures.

Build clean, dirty, detached, branch/history, nested-repository, and gitlink/submodule fixtures independently. For `dirty`, replace `README.txt` with bytes `repository-audit-dirty-v1\n` and add `untracked.txt` with bytes `untracked-v1\n` after the baseline commit. For traversal and symlink cases, make an outside-root target in a sibling temporary directory containing only `sentinel-v1\n`; test both a `..` path and symlinks to that target, plus an in-root symlink. Record that the target is synthetic and do not put secret-like values in reports. If the host cannot safely create or inspect symlinks, mark dependent scenarios `BLOCKED` and the actual outcome `NOT RUN`.

## Scenario execution order

Record a separate result and evidence reference for every scenario in the evidence template.

| ID | Scenario | Prerequisites | Procedure | Expected evaluation criterion |
|---|---|---|---|---|
| V-01 | Validator valid metadata and headings | Approved spec/hash; Member 2 confirms identity, target commit, fixture ownership, scope, and expected outcome; isolated temporary fixture; authorized local validator procedure. | Run validator against valid canonical fixture; retain command output and exit code. | Accept; keep implementation suite evidence separate from independent evaluation and Skill results. |
| V-02 | Missing fields, wrong types, duplicate/unknown keys, malformed front matter, invalid UTF-8 | V-01 prerequisites; each malformed fixture isolated. | Run one case per malformed input and capture exact JSON/exit code. | Emit documented stable errors and exit behavior. |
| V-03 | Relative, nonexistent, file, and inaccessible roots | V-01 prerequisites; permission injection identified as mocked if used. | Exercise each root class independently; label mocked and native permission cases. | Reject unsafe roots; do not present mocks as OS permission evidence. |
| V-04 | Canonical path mismatch and explicit `..` traversal | V-01 prerequisites; outside target is synthetic. | Supply noncanonical path variants and verify no alternate file is inspected. | Reject without inspecting another file. |
| V-05 | Canonical Skill file at exactly 64 KiB and 64 KiB + 1 | V-01 prerequisites; generated canonical fixtures. | Run at-limit and over-limit inputs separately. | Accept at-limit and reject over-limit per contract; this is not the Skill JSON request limit. |
| V-06 | Stable validator errors | V-01 prerequisites; fixed malformed input. | Repeat identical invocation; compare JSON bytes and exit statuses. | Byte-identical output, stable error ordering, same exit status. |
| V-07 | Non-POSIX fail-closed dispatch | V-01 prerequisites; unit-test harness may simulate branch. | Assert rejection occurs before path metadata/read; separately run native Windows only if a supported implementation and authorized Windows host exist. | Simulated branch evidence is local-only; Windows remains `NOT VERIFIED` absent native evidence. |
| H-01 | Missing or misconfigured execution host | Confirmed Member 2 evaluator/target; separate Owner Skill-execution authorization; trusted host under test. | Invoke through approved runner with host absent/misconfigured; capture launcher trace and result. | Zero process calls; host unavailability per approved response contract. |
| H-02 | Rejected executable or disallowed argument | H-entry conditions; trusted host and process trace. | Submit each forbidden executable/argument case through runner; inspect launch trace. | Reject before process creation. |
| H-03 | Environment and working directory | H-entry conditions; synthetic fixture and environment-capture harness. | Invoke allowed operation; verify only approved environment and validated root reach runner without recording secret values. | Enforced environment/cwd policy; record assertions only. |
| H-04 | Timeout, output caps, process failure | H-entry conditions; controlled child outcomes and process trace. | Inject timeout, oversized stdout/stderr, and failures separately. | Bounded output; preserved outcome/exit status; never report success on failure. |
| H-05 | Read-only and repository-state preservation | H-entry conditions; isolated synthetic repository; reliable before/after snapshots. | Snapshot refs/index/worktree/hashes, run authorized case, snapshot again. | No unexpected observed changes; state limitation that snapshots do not prove no transient writes. |
| P-01 | Valid root, clean and dirty worktrees | All evaluation entry conditions; approved fixture recipe and exact target. | Run each clean/dirty fixture and compare emitted fields with fixture state. | Correct requested parent metadata only. |
| P-02 | Root mismatch, bare repository, inaccessible root | P-01 prerequisites; separate fixtures for each condition. | Run each invalid-root case; capture status/code and evidence boundary. | Reject without fallback inspection; contract-matching status/code. |
| P-03 | Traversal, absolute path, separator variants | P-01 prerequisites; sibling synthetic sentinel target. | Submit each path form; verify runner trace shows no target access. | Reject before target access; do not disclose target content. |
| P-04 | In-root symlink and outside-root symlink escape | P-01 prerequisites; host supports symlinks and target is synthetic. | Run in-root and escape cases; inspect access trace. | Reject without following/statting target; otherwise mark BLOCKED if host cannot support case. |
| P-05 | Nested repository and submodule/gitlink | P-01 prerequisites; synthetic nested repo and gitlink fixtures. | Run parent-root query and inspect reported boundary. | Do not enter child repositories; approved parent metadata or `NOT_INSPECTED`. |
| P-06 | Denied command, content read, mutation/script/network/test request | P-01 prerequisites; denied-operation fixtures; process/content access tracing. | Submit each denied request; inspect traces and output envelope. | No prohibited invocation or direct content read; response matches contract. |
| P-07 | Canary in denied fixture path | P-01 and private canary custody; isolated fixture. | Evaluator privately scan serialized output and log only method/reference, not value or verdict. | No canary disclosure; never include value/verdict in Skill output or public report. |
| P-08 | Deterministic JSON and output/entry limits | P-01 prerequisites; fixed fixture/scope and known expected limits. | Repeat identical evaluation; compare bytes, ordering, truncation metadata, omitted counts. | Deterministic output and contract-compliant limits. |
| P-09 | Malformed output and nonzero process status | P-01/H-entry conditions; controlled injected process outcomes. | Supply malformed output and nonzero status separately; inspect dependent findings. | Never convert failure to success; dependent facts unknown and overall result per contract. |
| P-10 | Before/after state comparison, including incomplete and changed snapshots | P-01 prerequisites; fixtures for complete/equal, changed, failed, and incomplete snapshots; M2.14 decision. | Run each state case; compare slots, status, outcomes, exit codes, and paired-query decisions. | Preserve usable values; null failed/unusable slots and `unchanged` unless all complete/valid; incomplete=`PARTIAL`, dependent facts=`UNKNOWN`, skip paired after-query after failed before-query, continue only safe independent queries. Complete/equal=`true`; detected change=`false` and `PARTIAL` with concurrent-change limitation, without attributing cause. |

Use a mock only to test the host's response to injected process outcomes. Mock results do not establish OS sandboxing, read-only execution, or path-race protection. Record real-host enforcement evidence separately.

## Not-run rule

The current environment does not provide a demonstrated constrained runner; WSL was unavailable during preparation. H-01 through H-05 and P-01 through P-10 are currently `BLOCKED` by entry conditions 2–4 and have actual outcome `NOT RUN`. Member 2 must confirm evaluator identity, scope, fixtures, expected outcomes, and target commit; the Owner must authorize Skill execution against that target; Member 3 must supply reproducible host-enforcement evidence. This plan itself has not executed any scenario.

## Remaining execution checklist

1. **Member 2:** confirm identity, role, artifact path, fixture ownership, scope, authoritative expected outcomes, and exact target commit; review the evaluation package revision.
2. **Project Owner:** explicitly authorize Skill execution for the confirmed target and scenario scope.
3. **Member 3 / host operator:** identify the trusted isolated host and provide attributable evidence for executable/argument allowlisting, sanitized environment, cwd/path restrictions, timeout/output caps, and read-only isolation. Do not use this plan or mocked tests as proof.
4. **Evaluator:** verify spec hash and target, create isolated synthetic fixtures, record before-state, execute only approved scenarios, retain raw evidence securely, and complete every evidence-template row.
5. **Member 2:** independently review results and evidence, record findings and recommendation, and identify any failed or inconclusive criteria.
6. **Owner / release authority:** obtain the authoritative Gate A and R4/R5 criteria first; the available project decision records prohibit those stages but do not define their acceptance criteria. Obtain separate authorization for each stage. Integration also requires a recorded base/reconciliation decision (ADR-M1-01 is pending), explicit integration authorization, a reviewed README conflict plan, and confirmed repository protection/check requirements. Release requires the exact approved specification revision and its commit to be recorded, completed implementation evidence, Member 2's independent evaluation evidence, resolved required gates, and explicit Project Owner release approval. The available records leave the designated approval/quorum process unresolved (ADR-M1-06); do not infer acceptance. This checklist does not authorize these stages.

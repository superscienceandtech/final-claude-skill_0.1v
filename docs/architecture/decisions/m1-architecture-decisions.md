# M1 Architecture Decision Review

**Status:** ADR-M1-01 through ADR-M1-06 remain Pending except for the four scoped Owner decisions recorded under ADR-M1-04 below. Those decisions do not approve the specification revision or close ADR-M1-04 as a whole.
**Scope:** M1 preparation for a minimal `repository-audit` Skill.

## Current checkout specification verification — 2026-10-29

This is a repository-state verification note, not a new Owner decision.

- Current checkout: `main` at `66e348b991e40b7387bd5722d126e08d5b43eafd`.
- The specification blob at this `HEAD` has SHA-256
  `b33adec843e3550125aceb2af71c07a3d3c09539f4fa732eb145dd6b3d119afd`,
  matching the exact revision approved in `OWNER-DECISION-M2.11-01`. The same
  blob is present at historical commit `288baba0834b`.
- On this Windows checkout, `core.autocrlf=true` converts the LF blob to CRLF
  in the working tree. The raw working-tree SHA-256 is
  `50527128247430961E3DF203CE65C5E2013951B5AE2084E1B6AF21D542113B70`;
  converting CRLF back to LF yields the approved blob hash above. Git reports
  the file clean, and the normalized working-tree bytes equal the `HEAD` blob.
  The raw digest difference is line-ending conversion, not a different
  committed specification revision.
- The older `5208D70C…` approval and durable pin remain scoped to their
  separate historical revision. No approval is inferred across hashes.
- The durable pin names tag `spec-approval-5208d70c`, but no local tag ref is
  present in this checkout. Remote tag state was not verified.

This note does not authorize Skill execution or independent evaluation.

Each record separates verified facts from the proposal, approval needed, and consequences/alternatives. A proposal becomes approved only when the team records its decision, approver(s), and date.

## ADR-M1-01 — Integration base and PR sequence

- **Verified fact (2026-10-13):** `yousuf` is at `a8f1902c150b55c7193d97555ac44ce18384cc89` and tracks `origin/yousuf` at `d0ffd15249c892a1742b32f7f8b4f948eae1ddea` (eight commits ahead, none behind). Local `main` is at `2efcdf2d9753bfc76ca5f440efe9e205cc2efe80`; `origin/main` is at `cca20097a802823d7625bb23d7bcd12bb398de17` (each is one commit ahead of the other after shared commit `6db6634e044ba763899d45f0d28927ec8a82e60a`). `yousuf` and local `main` share ancestor `d4728565e72c964fbd1e6a3901d732c6099e77d8`; `main` has two unique commits and `yousuf` has twelve. Before the remote refresh, `origin/srijon` and `origin/sonjoy` pointed to that ancestor; refreshed tips are `91eb2743299cceff2b8eca43450f4d7e6afa7849` and `979906879ba9540ecf0be723e916864c58a71c97`, respectively.
- **Proposed decision:** Do not choose an integration base in this record. Require the team to select one explicitly. Afterward, review M0/M1 docs in a documentation PR; then Skill source/validator and Member 2 fixtures in separate scoped PRs, each against the agreed base.
- **Team approval required:** Yes; integration base and reconciliation approach.
- **Consequences / alternatives:** Avoids silently importing divergent history. Alternatives are choosing `main` or another agreed branch and planning reviewed reconciliation. No merge or history change is authorized here.

## ADR-M1-02 — Canonical Skill source and format

- **Verified fact:** No Skill format, Skill artifact, or validator exists on the audited branch.
- **Proposed decision:** Keep one provider-neutral canonical source at `skills/repository-audit/SKILL.md`, using Markdown instructions plus YAML front matter for stable metadata. Later provider-specific packaging, if needed, is generated/adapted from this source and is not independently authoritative. Proposed metadata: `name`, `description`, `version`; team must approve exact types and schema.
- **Team approval required:** Yes; path, front-matter schema, required metadata, versioning and adapter policy.
- **Consequences / alternatives:** Human-readable and diffable without runtime dependencies; metadata parsing needs validation. Alternatives include structured JSON/YAML as source or another established Skill convention selected by the team.

## ADR-M1-03 — Minimal Skill validation

- **Verified fact:** No stack, test framework, package manager, or CI is present on the audited branch.
- **Proposed decision:** Begin with dependency-free structural validation: required front-matter keys/types, required sections, canonical path, and prohibited claims/permissions checks. Member 2 supplies isolated temporary-repository fixtures and expected outcomes. Use a small standard-library script only after format approval; otherwise start with a manual checklist. Add no dependency in M1.
- **Team approval required:** Yes; schema, validator location/runtime, and whether M1 permits a standard-library script.
- **Consequences / alternatives:** Low setup cost but limited semantic coverage. A schema library or CI gate can be considered after toolchain approval.

## ADR-M1-04 — First Skill selection

- **Verified fact:** No Skills exist on the audited branch; repository inspection was part of the M0 audit.
- **Proposed decision:** Select `repository-audit`, a read-only Skill that reports scoped repository evidence and uncertainty. Require explicit root and scope, canonical boundary validation, JSON output, and the command allowlist and sensitive-content rules in the Skill specification.
- **Team approval required:** Yes; confirm the first Skill and allowed command set.
- **Consequences / alternatives:** Exercises evidence and safety requirements without application code or external integrations. Alternatives include a smaller README/metadata checker or postponing implementation until format decisions are complete.

### ADR-M1-04 scoped contract decisions — ACCEPTED BY PROJECT OWNER

The Project Owner accepted the four policy decisions below on 2026-10-13. Provenance: Owner decision supplied in the M1 Sprint 5 request in this conversation; no separate repository approval artifact or time/timezone was supplied. Acceptance records policy choices only. It does not verify runtime capabilities, approve the exact specification revision, authorize integration or release, or close ADR-M1-04 as a whole.

| Decision | Accepted decision and rationale | Compatibility / residual risks | Required validation evidence | Remaining gate | Status |
|---|---|---|---|---|---|
| Git-internal reads | Only fixed `git.status` may cause necessary Git-internal working-tree reads. The Skill must not directly open, inspect, summarize, or disclose file contents. | Status may reflect dirty files; Git may internally read working-tree data for that operation. This narrower rule supersedes broader prior wording that permitted internal reads for other allowlisted operations. It does not establish zero filesystem content reads. | Host/process trace identifies the exact operation; fixture confirms no Skill-level content open or content in output; evaluator privately checks a canary. | Exact specification revision must still be approved; runtime behavior must be evaluated. | **ACCEPTED — PROJECT OWNER, 2026-10-13** |
| Path containment | If root containment is unproven, return `REJECTED` + `UNKNOWN` + `PATH_CONTAINMENT_UNPROVEN` without repository inspection. After root validation, if an individual path is unproven, return `PARTIAL` + `UNKNOWN`, skip it without access, and continue only for independently proven paths. | Fails closed at root; permits safe independent paths to continue. A confirmed escape remains distinct from uncertainty. Does not itself provide race-resistant host enforcement. | Host evidence and isolated fixtures prove no access to rejected targets; test root and individual-path uncertainty, including symlink escape. | Runtime enforcement and exact specification revision approval remain outstanding. | **ACCEPTED — PROJECT OWNER, 2026-10-13** |
| Opaque identifiers | Do not emit raw paths, branch names, command arguments, or caller-controlled strings. Use deterministic report-local IDs and counts. | Reduces direct disclosure; accepted residual risk: counts and deterministic ordering may leak membership or relative order. IDs do not provide anonymity. | Repeated fixture outputs are byte-identical; evaluator confirms markers for paths, branch names, arguments, and caller strings are absent. | Runtime output behavior and exact specification revision approval remain outstanding. | **ACCEPTED — PROJECT OWNER, 2026-10-13** |
| Input/output limits | Request ≤64 KiB UTF-8; root ≤4 KiB; each path ≤1 KiB; maximum 500 paths; claims/summaries ≤256 Unicode code points; final JSON ≤256 KiB. Reject the whole request before inspection if any input cap is exceeded. | Bounds request and output resources; whole-request rejection avoids silently narrowing requested scope. Large otherwise-valid requests may be rejected. | Exact below/at/above boundary tests; zero process starts for rejected requests; bounded valid JSON and deterministic output-cap behavior. | Runtime enforcement and exact specification revision approval remain outstanding. | **ACCEPTED — PROJECT OWNER, 2026-10-13** |

**Required evidence:** Member 3 must identify implementation gaps and provide reproducible host-enforcement evidence where available; Member 2 must confirm deterministic fixture/oracle coverage and independently evaluate the exact Owner-approved specification revision. These accepted decisions do not establish those capabilities or results.

### Exact-revision specification approval — APPROVED — EXACT REVISION ONLY

- **Decision:** The Project Owner explicitly approved `docs/architecture/repository-audit-skill-spec.md` at SHA-256 `5208D70CEE2492FCC77C3828D211F8125E9947BE12521D149CCB7A2179898B03`.
- **Approver:** Project Owner; personal name not supplied.
- **Date/provenance:** 2026-10-13; explicit Owner approval in the M1 Final Specification Review request in this conversation. No separate repository approval artifact or time/timezone was supplied.
- **Scope:** Exact specification revision only. The specification file was not modified to record this decision; its `PROPOSED — NOT APPROVED` banner predates this approval and this record is the approval evidence for the exact hash above. Any different file hash requires separate approval.
- **Separate gates:** Implementation authorization for work under this exact revision, integration authorization, and release approval are each **PENDING** separate explicit decisions. This approval grants none of them. It does not alter the scope or evidence of any prior governance decision. The four previously accepted policy decisions remain unchanged.

### Proposed clarification — bounded implementation authorization

**Status: PROPOSED — NOT APPROVED; no additional Owner decision recorded.**

This proposal clarifies the relationship between the existing `OWNER-DECISION-M1-01` bounded implementation authorization and the separate exact-revision implementation gate. It does not modify the original decision.

`OWNER-DECISION-M1-01` records bounded implementation authorization for Member 3 within the listed paths and permits implementation and local testing only, subject to the original decision's constraints and unresolved safety requirements.

The exact-revision approval entry separately records implementation authorization for work under the specification hash above as PENDING. The relationship between these two records has not yet been explicitly reconciled. This proposal does not determine that the earlier bounded authorization satisfies the separate exact-revision implementation gate.

This proposal grants no new implementation permission and does not expand, revoke, or reinterpret the original authorization. It does not authorize repository execution, integration, merge, rebase, publication, push, or release. The original `OWNER-DECISION-M1-01` entry must remain intact.

The specification approval remains limited to the exact recorded hash. Any corrected specification revision requires separate explicit Owner approval of its exact SHA-256.

### Owner clarification decision — OWNER-DECISION-M1-02 — APPROVED

**Decision date:** 2026-10-14. The date is established from the explicit Owner decision supplied in this conversation and the current system date; no time or timezone was supplied.

**Decision:** The Project Owner confirms that the bounded implementation authorization already recorded in `OWNER-DECISION-M1-01` applies to implementation and local testing under `docs/architecture/repository-audit-skill-spec.md` at SHA-256 `5208d70cee2492fcc77c3828d211f8125e9947be12521d149ccb7a2179898b03`.

**Scope and constraints:** This records applicability only. It does not expand the original authorized paths or activities. Authorized paths remain `skills/repository-audit/SKILL.md`, `scripts/validate-skill.py`, and `tests/skills/repository-audit/`. The validator remains dependency-free unless the Project Owner separately approves a dependency change. Unresolved safety requirements remain unresolved and must not be treated as satisfied.

**Not authorized:** This decision does not authorize executing the Skill against a repository, integration, merge, rebase, publication, push, or release. It does not establish execution-host qualification, complete evaluation, or release approval.

**Provenance:** Explicit Project Owner decision supplied in this conversation on 2026-10-14. This entry supplements, and does not replace or amend the historical wording of, `OWNER-DECISION-M1-01`, the exact-revision specification approval record, or the proposal-only clarification above.

## ADR-M1-05 — Ownership of source, fixtures and security policy

- **Verified fact:** M0 assigns `skills/*` and validator scripts to Member 3; evaluation/testing docs to Member 2; security policy docs to Member 1.
- **Proposed decision:** Per `OWNER-DECISION-M1-01`, Member 3 owns `skills/repository-audit/SKILL.md`, `scripts/validate-skill.py`, and implementation tests under `tests/skills/repository-audit/`. Member 2 owns the independent evaluation plan, fixtures, rubric, and reports. Proposed evaluation path: `docs/evaluation/repository-audit/`, pending Member 2 confirmation. Member 1 owns architecture and security-policy records, including this ADR. One accountable editor per file; reviewers do not co-own implementation tests or independent evaluation evidence.
- **Team approval required:** Yes; Member 2 must confirm evaluator identity, evaluation artifact path, and scope. The ADR remains Pending until its required approvals are recorded.
- **Consequences / alternatives:** Separates implementation tests from independent evaluation evidence. If Member 2 rejects the proposed path, select a distinct path under the Member 2-owned evaluation documentation area without moving or replacing Member 3's tests.

## ADR-M1-06 — Lifecycle approval authority

- **Verified fact:** M0 distinguishes IMPLEMENTED, EVALUATED and APPROVED but names no approval authority.
- **Proposed decision:** Implementer attests IMPLEMENTED with artifact and change evidence; Member 2 records EVALUATED only after independent verification with exact invocation, expected/actual results, limitations and evaluator identity; APPROVED requires explicit team-designated approver(s), recorded with reviewer evidence in the PR/decision record. No state implies the next.
- **Team approval required:** Yes; name approver(s), quorum/consensus rule and status-record location.
- **Consequences / alternatives:** Keeps evaluation distinct from acceptance. Alternatives include a single architecture-lead approver or cross-functional approval for security-sensitive modules.

## Approval log

| Decision | Team outcome | Approver(s) | Date | Evidence/link |
|---|---|---|---|---|
| ADR-M1-01 | Pending | — | — | — |
| ADR-M1-02 | Pending | — | — | — |
| ADR-M1-03 | Pending | — | — | — |
| ADR-M1-04 | Pending | — | — | — |
| ADR-M1-05 | Pending | — | — | — |
| ADR-M1-06 | Pending | — | — | — |

## Project Owner governance decision — OWNER-DECISION-M1-01

**Decision status:** Approved by the Project Owner in the user-provided decision dated 2026-10-13. This record preserves that authorization; it does not close the unresolved ADRs below.

- **Approving authority:** Project Owner (the current user; personal name not supplied in the decision).
- **Decision date:** 2026-10-13. A time and timezone were not supplied.
- **M0:** Approved with security gates. The final specification version and its Git commit must be recorded before release acceptance.
- **M1:** Bounded implementation authorized for Member 3: `skills/repository-audit/SKILL.md`, `scripts/validate-skill.py`, and `tests/skills/repository-audit/`. The validator must be dependency-free unless the Project Owner separately approves a dependency change. Authorization permits implementation and local testing only; it does not authorize merge into `main`, publication, evaluation completion, or release approval.
- **Integration:** No base or reconciliation plan is approved. No merge/rebase into `main` is authorized by this decision.
- **Lifecycle:** `IMPLEMENTED`, `EVALUATED`, and `APPROVED` remain distinct. Member 2 owns independent evaluation evidence; only the Project Owner may grant final release approval under this decision.
- **Specification revision:** `docs/architecture/repository-audit-skill-spec.md` at this working tree. It is modified relative to HEAD `61ae48abf08fce9ba8ddcfcd81bb83a2ca012928`; no immutable version, content hash, or commit was supplied. The specification itself still labels its contract proposed, and the owner decision leaves its schema and safety details open.
- **Evidence provenance:** User-provided decision text in the conversation, dated 2026-10-13. No repository commit or external approval artifact accompanied it.

### Open conditions retained

The following remain unresolved and must not be inferred from the bounded authorization: canonical integration base and reconciliation sequence; final Skill metadata/schema/versioning and compatibility policy; validator interface, path behavior, and exit codes; security details affecting safe implementation; concrete ownership/evidence paths not specified above; and the required timestamp/evidence location for the final specification record. Work affected by an unresolved safety contract must pause pending a Project Owner decision. ADR-M1-01 through ADR-M1-06 therefore remain **Pending** until their individual requirements are resolved and recorded.

## Project Owner correction authorization — OWNER-DECISION-M2.6-01

**Decision status:** Authorized by the Project Owner on 2026-10-15 for the documentation-only correction described here. This decision does not approve the corrected specification revision.

- **Approving authority:** Project Owner (personal name not supplied).
- **Scope:** Correct lifecycle wording and path-output representation in `docs/architecture/repository-audit-skill-spec.md`; record this authorization and provenance clarification in this decision record. No other files or behavior are in scope.
- **Output-path policy:** Use sensitive-path matching internally. Where the schema permits a filesystem-path reference, serialize only an opaque report-local path ID or `null` where explicitly permitted. Never serialize raw or redacted path strings, including `[REDACTED]`. Preserve denial, containment, command allowlists, and all other security requirements.
- **Lifecycle policy:** Approval applies only to an exact specification revision whose recorded SHA-256 matches the approved bytes. It does not imply implementation completion, runtime evaluation, security approval, integration, or release approval. Any corrected specification revision requires separate explicit Owner approval of its exact hash.
- **Approval provenance clarification:** The approval pin's 2026-10-13 exact-hash approval reference and this record's 2026-10-14 `OWNER-DECISION-M1-02` implementation-authorization clarification are distinct historical events. Because the identifier is reused in the available records, cite the event by its record heading, date, and scope rather than the bare identifier. This clarification does not rewrite, renumber, or invalidate either historical record.
- **Historical gate wording:** Earlier ADR-M1-04 rows that said exact-revision approval remained outstanding are preserved as historical status text. The later exact-hash approval record governs the prior hash named above; the corrected revision is a new hash and requires its own approval.
- **Approval procedure:** After the authorized specification correction, compute its SHA-256 and present the exact diff to the Owner. The corrected revision remains pending until the Owner explicitly approves that hash in a separate record. Do not create a new approval pin, tag, commit, or release artifact under this authorization.
- **Not authorized:** This decision authorizes no tests, Skill or launcher execution, runner selection, Gate A, R4/R5, provisioning, integration, publication, push, or release. It does not establish runtime security or independent evaluation.

**Provenance:** Explicit Project Owner authorization supplied in the M2.6 continuation prompt on 2026-10-15. This unique identifier is not a replacement for or amendment to `OWNER-DECISION-M1-01` or either historical use of `OWNER-DECISION-M1-02`.

## Project Owner exact-revision approval — OWNER-DECISION-M2.11-01

**Decision status:** APPROVED — exact specification revision only.

- **Decision:** The Project Owner approves `docs/architecture/repository-audit-skill-spec.md` at SHA-256 `b33adec843e3550125aceb2af71c07a3d3c09539f4fa732eb145dd6b3d119afd`.
- **Approver:** Project Owner / Member 1; personal name not supplied.
- **Decision date:** 2026-10-15.
- **Scope:** Approval applies only to the exact specification bytes identified by the SHA-256 above. Any other revision requires its own explicit exact-hash approval.
- **Separate gates:** This specification approval does not approve implementation completion, execution-host enforcement, runtime execution, behavioral evaluation, security approval, integration, or release readiness. Each remains an independent gate requiring its own evidence and authorization as applicable.
- **Provenance:** Explicit Project Owner instruction in the M2.11 conversation on 2026-10-15. This record does not modify or replace the existing approval pin for the prior specification revision.

## Project Owner state-comparison decision — OWNER-DECISION-M2.14-01

**Decision status:** OWNER DECISION — Option A, preserve partial snapshot evidence.

- **Decision date:** 2026-10-15.
- **Approver:** Project Owner / Member 1; personal name not supplied.
- **Applicable specification:** `docs/architecture/repository-audit-skill-spec.md`, SHA-256 `b33adec843e3550125aceb2af71c07a3d3c09539f4fa732eb145dd6b3d119afd`.
- **Rationale and interpretation:** Specification §5 requires the same approved branch/status queries before and after inspection, defines detected-difference behavior, and gives general command-failure handling, but does not fully specify incomplete-comparison field semantics. This decision records the Owner-selected Option A failure policy already stated in the M2.3 continuation prompt; it clarifies that policy without amending the approved specification or changing its hash.
- **Policy:** Preserve each individually usable before/after snapshot value in its corresponding slot. Set a failed, timed-out, malformed, incomplete, or otherwise unusable slot to null; preserve the actual command outcome and exit code (or null when none exists), and mark dependent facts `UNKNOWN`. If a before query fails, skip its paired after query. Continue only safe, independent, allowlisted query pairs after root validation and within existing limits. Set `unchanged` to null unless every required snapshot is complete and valid; an incomplete comparison is `PARTIAL` and must never imply equality. For a complete comparison, set `unchanged` to true only when all compared values match, or false when a difference is detected. A detected difference makes the overall status `PARTIAL` and adds the concurrent-change limitation; do not attribute the change to the Skill without evidence.
- **Scope and non-authorization:** This records policy interpretation only. It does not amend or reapprove the specification, establish implementation, or authorize tests, Skill/runner execution, host provisioning, Gate A, integration, or release.
- **Remaining gates:** Implementation evidence, host-enforcement evidence, implementation testing, independent evaluation, integration authorization, and release approval remain separate and open. This decision is not evidence that any gate has been met.
- **Provenance:** Explicit Project Owner selection of Option A in the M2.3 continuation prompt in this conversation, dated 2026-10-15. This uniquely identified record formalizes that selection; it does not claim Member 2 review or runtime validation.

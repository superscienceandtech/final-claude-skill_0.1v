# Proposed Implementation Roadmap

The roadmap is staged to keep implementation incremental. Milestones are proposals, not authorization or evidence that work has started. A later stage begins only when its entry conditions are reviewed and accepted.

## M0 — Architecture baseline and governance review

- **Scope:** Audit, ARC dependency/status baseline, ownership, contract template and proposed sequence.
- **Dependencies:** None.
- **Entry:** Repository state and branch are rechecked; working changes are preserved.
- **Exit criteria:** Baseline documents and ARC entries record scope, owner, dependencies, priorities, and measurable criteria; branch constraints and unresolved decisions are recorded; the Project Owner accepts repository-local governance within their authority; `git diff --check` passes.
- **Status:** **PARTIAL.** The Project Owner accepted the solo operating model on 2026-10-29, and the decision is recorded. Branch integration, protected M1 decisions, and the completeness of all ARC contracts remain open; the governance decision is not blanket architecture approval.

## M1 — Repository safety, canonical Skill and focused evaluation

- **Scope:** Approve repository safety guidance, canonical Skill contract, one implementation Skill and focused evaluation cases.
- **Dependencies:** M0 governance review; resolve integration base; agree Skill format and validation approach.
- **Entry conditions:** ARC-00, ARC-01, ARC-02 and ARC-10 contracts reviewed; an accountable owner is identified for each artifact; acceptance cases written before implementation.
- **Exit criteria:** Repository rules are approved; one canonical Skill validates; focused cases have reproducible inputs, expected behavior and recorded results; no provider duplicate is authoritative.

## M2 — Roles, implementation, verification and security gates

- **Scope:** Core role responsibilities, implementation workflow, testing, verification and security gates. A solo reproducibility pass is not independent verification.
- **Dependencies:** M1 artifact and validation path; ARC-04, ARC-05, ARC-06 and ARC-10 contracts accepted.
- **Entry conditions:** Role/handoff boundaries and security permissions reviewed; the verification method and evidence format are agreed; a verifier other than the implementer is available if the milestone claims ARC-06 independent verification.
- **Exit criteria:** Sample work can move from scoped task through implementation to independent verification; security checks and failures are recorded; completion claims link to actual evidence.
- **Current readiness:** **PARTIAL — NOT READY AS A COMPLETE MILESTONE.** The skill workflow, tool workflow, bounded validation adapter/CLI, selected-path source-change observation, and a repository-callable bounded source-editing workflow with pipeline integration and regression tests exist. A local JSON CLI now routes caller-supplied edit requests through the implementation Skill pipeline with explicit path grants and a fixed `git diff --check`; it rejects caller-selected test modules. It is not an AI/provider-backed request-to-edit generator. Exact-path grants, JSON validation, and Python filesystem checks are application-level controls, not an OS sandbox, and cannot prevent hostile concurrent path swaps. ARC-06 independent verification is blocked because no separate verifier is identified. The proposed documentation-only first task remains `PROPOSED — OWNER REVIEW REQUIRED`; its authorization is separate from this inferred local-interface implementation.

The accepted solo operating model resolves the decision about who may set
repository-local direction and make final acceptance/release decisions; it
does not provide an editing adapter, independent verifier, or authorization
for protected work. The Owner remains the explicit release authority, but no
release is approved by recording that authority.

## M3 — Provider compatibility and selected developer-tool integrations

- **Scope:** Provider adapters and a deliberately selected set of developer-tool integrations.
- **Dependencies:** M1 canonical Skill source; M2 role and security gates; ARC-07 and ARC-08 contracts accepted.
- **Entry conditions:** Initial providers/tools selected; data access, credential handling and permission model reviewed.
- **Exit criteria:** Compatibility cases trace adapters to canonical versions; integration tests cover authorization, failure and revocation behavior; unsupported capabilities are explicit.
- **Current readiness:** **PARTIAL — NOT READY FOR PROVIDER-RUNTIME OR REMOTE INTEGRATION CLAIMS.** A Claude Code plugin manifest, provider instructions, and fixed local configuration/canonical-Skill consistency validation exist. Claude CLI is unavailable. The Owner selected Continue as the M3 developer-tool target. Continue's official documentation describes the `cn` headless coding-agent CLI, structured JSON output, path-patterned tool permissions, and explicit write-tool allowlisting; however, `cn` is not installed or available on PATH here, no Continue runtime adapter is integrated, and no runtime call has been exercised. The documented CLI requires Continue account or API-key authentication; no credentials were inspected and no provider/network request was made. Its documented tool permissions are not an OS sandbox, and read tools such as `Fetch` are allowed by default unless excluded. The Owner has not specified the data, network, credential, or permission boundary. M2 remains partial, and complete ARC-07/08 failure, revocation, and security criteria are not evidenced. Do not install or invoke the CLI until that boundary is explicitly authorized.

## M4 — Memory, knowledge, benchmarks and controlled evolution

- **Scope:** Context/memory workflows, knowledge provenance, evaluation benchmarks and change lifecycle.
- **Dependencies:** M2 verification; relevant M3 integrations if they supply data; ARC-09, ARC-11 and ARC-12 contracts accepted.
- **Entry conditions:** Data classes, retention, access/deletion controls, benchmark scope, and release authority agreed.
- **Exit criteria:** Retrieval and evaluation are measurable and reproducible; changes carry review/evaluation records and a rollback or retirement path.

## M5 — Advanced AGI research modules

- **Scope:** Isolated advanced research experiments with explicit experimental boundaries.
- **Dependencies:** Research evidence practice (ARC-03), independent verification (ARC-06), security governance (ARC-10), and evaluation (ARC-11).
- **Entry conditions:** Experiment scope and risk review approved; reproducibility and claim standards established; data and tool permissions reviewed.
- **Exit criteria:** Each experiment reports hypothesis, method, results, limitations, safeguards and reproduction status; claims are limited to demonstrated evidence.

## Integration sequence

Proposed sequence: (1) resolve target base and accountable ownership per artifact; (2) review M0 docs under the applicable governance model; (3) establish M1 contracts and the first canonical artifact with focused cases; (4) add M2 workflow and verification evidence, preserving the distinction between solo reproducibility and independent verification; (5) introduce one provider/tool integration at a time; (6) add governed memory/evaluation/evolution; (7) begin bounded ARC-13 experiments only after gates pass. Keep one coherent scope per change and do not combine architecture approval with claims of implementation evaluation.

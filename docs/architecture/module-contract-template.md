# Module Contract Template

Copy this template for a proposed module. Mark unknowns explicitly; do not silently turn proposals into approved decisions.

## Identity and lifecycle

- **Module ID and name:**
- **Version / revision:**
- **Accountable owner:**
- **Contributors / reviewers:**
- **Lifecycle status:** PLANNED | SPECIFIED | IMPLEMENTED | EVALUATED | APPROVED | BLOCKED | DEPRECATED
- **Supporting evidence:** Links to source, tests, reports, decisions, and approvals; write `None` when absent.

Lifecycle states are distinct. `IMPLEMENTED` requires implementation evidence. `EVALUATED` requires recorded evaluation evidence against acceptance criteria. `APPROVED` requires a named approver and approval record. One state does not imply the later states.

## Purpose and boundaries

- **Purpose:**
- **Non-goals:**
- **In-scope responsibilities:**
- **Out-of-scope responsibilities:**
- **Users / callers:**

## Contract

- **Inputs:** Include schema, source, trust assumptions and validation.
- **Outputs:** Include schema, provenance and guarantees.
- **Dependencies:** List module IDs, versions and dependency direction; state `None` if none.
- **Interfaces / events:**
- **Compatibility and versioning:**

## Security and permissions

- **Data handled and sensitivity:**
- **Trust boundaries / threat assumptions:**
- **Permissions required:** Least privilege; identify human authorization gates.
- **Secrets handling:**
- **Retention, deletion and audit needs:**
- **Misuse cases and mitigations:**

## Failure handling

- **Expected failures:**
- **Detection and reporting:**
- **Retries, fallback and recovery:**
- **Safe-stop behavior:**
- **User escalation conditions:**

## Verification and acceptance

- **Test requirements:** Unit, contract, integration, security, evaluation or manual checks, with rationale.
- **Acceptance criteria:** Observable, measurable conditions; include thresholds where applicable.
- **Evaluation method and dataset/fixtures:**
- **Evidence to retain:** Exact commands, versions, results, limitations and reviewer.
- **Known limitations / unresolved decisions:**

## Review record

- **Specification reviewed by / date:**
- **Implementation evidence:**
- **Evaluation evidence:**
- **Approval decision / approver / date:**
- **Deprecation or replacement plan, if applicable:**

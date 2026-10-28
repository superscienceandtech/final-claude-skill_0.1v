# Provisional Structural-Only Skill Validator Specification

> PROVISIONAL — NOT APPROVED — NOT CANONICAL — NOT IMPLEMENTATION AUTHORIZATION

## 1. Purpose, scope, non-goals, and limitations

This document defines a provisional, narrow-scope specification for a structural-only Skill metadata validator intended for repository-local review and specification work only.

The validator in scope is limited to:

- one explicitly supplied input file
- validation of the selected provisional front-matter and metadata structure
- no Markdown section validation; Markdown validation is deferred under Section 10
- deterministic diagnostics with a machine-readable result payload
- no execution of Skill content, no invocation of tools, and no filesystem traversal beyond the supplied file path

This specification is not a production validator specification, a canonical schema decision, or an authorization for implementation.

### 1.1 Non-goals

This initial scope explicitly excludes:

- dependency or registry resolution
- claims that discovered skills, providers, tools, resources, or capabilities actually exist
- runtime permission enforcement or sandbox validation
- filesystem traversal or symlink security guarantees
- network access or automatic installation of dependencies
- evaluation, approval, release authorization, or production-security certification
- any claim that a `path` metadata field establishes safe runtime access

### 1.2 Limitations

This specification is intentionally restricted. It only covers structural validation of a single supplied document and recorded diagnostics. It does not validate operational safety, integration trust, registry authority, or runtime execution semantics.

## 2. Repository evidence and constraints

The following repository facts are relevant to this specification:

- [skills/implementation/implementation.md](../../skills/implementation/implementation.md) contains the repository's current observed front matter and canonical implementation workflow.
- [skills/README.md](../../skills/README.md) defines the repository as limited to a canonical implementation workflow and minimal supporting documentation.
- [docs/compatibility/README.md](../compatibility/README.md) defines compatibility status labels: `VERIFIED`, `PARTIALLY VERIFIED`, `UNVERIFIED`, and `NOT SUPPORTED`.
- [providers/README.md](../../providers/README.md) requires provider-specific logic to remain separate from the canonical workflow.
- [integrations/README.md](../../integrations/README.md) keeps the repository's integration boundary intentionally narrow and provider-neutral.
- [workflows/spec-to-implementation/README.md](../../workflows/spec-to-implementation/README.md) requires evidence-driven implementation, explicit stop gates, and requirement readiness before work proceeds.

### 2.1 Observed front-matter convention

The current in-repository sample uses YAML-style front matter enclosed by `---` delimiters:

- file: [skills/implementation/implementation.md](../../skills/implementation/implementation.md)
- observed syntax:

```yaml
---
name: implementation
description: "A provider-neutral implementation workflow for safely carrying out software engineering tasks from understanding through verification."
---
```

This is the only verified repository example of front matter found in the inspected repository. The repository evidence does not establish that strict JSON, constrained YAML, or general YAML is the canonical format across all external consumers.

### 2.2 Compatibility status

This specification adopts the following provisional position:

- existing repository convention: YAML-style front matter with `---` delimiters is the only verified repository convention
- strict JSON is not verified as supported by repository evidence
- general YAML is not proven canonical for all consumers, but it is compatible with the repository's current observed convention
- actual external consumer compatibility is still unknown and must remain explicitly marked `UNKNOWN` or `UNVERIFIED` unless authoritative evidence is added

## 3. Provisional format assumptions and unresolved compatibility evidence

### 3.1 Provisional format assumption

The validator shall operate on a provisional metadata front matter format that is explicitly documented as a repository-local proposal rather than as a system-wide canonical standard.

The initial assumption is:

- YAML front matter enclosed by `---` delimiters
- UTF-8 text encoding
- top-level mapping/object
- scalar strings and arrays only where allowed by the metadata schema; nested objects and booleans are not allowed in the initial schema

This assumption is provisional because the repository contains only one verified front-matter example and no in-repository consumer or parser implementation.

### 3.2 Input schema version

The initial input metadata schema has no `schema_version` field. The output field `schema_version` identifies the proposed JSON result contract only; it is not read from the Skill file and does not version the validator executable.

For this draft, the result-contract identifier is the literal string `0.1-provisional`. No input value can trigger `SKILL011_UNSUPPORTED_SCHEMA_VERSION`; that diagnostic is removed from the initial catalog. If a future input schema-version field is proposed, its name, requiredness, accepted values, migration behavior, and compatibility effects require a separately reviewed amendment. This is a `PROVISIONAL ASSUMPTION`, not an established repository convention.

### 3.3 Unresolved compatibility evidence

The following remain unresolved and must remain labelled as unverified until authoritative supporting evidence is added:

- strict JSON support in actual consumers
- constrained YAML acceptance in editors or tooling
- general YAML acceptance in all expected consumers
- external parser/consumer compatibility with this provisional YAML profile
- external metadata consumers not present in the repository
- the parser implementation and version, which must conform to Section 5.1 before implementation acceptance

## 4. Structural validation input contract

### 4.1 Input model

The validator accepts exactly one file path supplied explicitly by the caller. It validates that file only.

The validator shall not:

- recursively walk directories
- discover sibling skills automatically
- resolve dependency catalogs
- inspect remote resources
- execute or interpret the Skill body

### 4.2 Input file requirements

The input file shall be a UTF-8 text file containing:

1. a YAML front matter block delimited by `---`
2. optionally, a Markdown body after the closing delimiter; Markdown section validation is deferred

The file must satisfy the following provisional rules:

- front matter must start at byte offset 0, with `---` exactly on the first line
- the front matter must end with a closing `---` line
- the YAML payload must parse as a mapping/object
- a UTF-8 byte-order mark is rejected; no leading whitespace or preamble is accepted
- one YAML document occupies the payload; the closing `---` terminates front matter, and the subsequent Markdown body is not parsed as YAML

### 4.3 Malformed-input behavior

Malformed input is a validation error, not a runtime execution issue.

The validator shall report the specified diagnostic with a deterministic source location when any of the following occur:

- missing opening delimiter: `SKILL001_MISSING_FRONT_MATTER`
- missing closing delimiter: `SKILL002_INVALID_DELIMITER`
- malformed YAML, a document-end marker, aliases, anchors, tags, or duplicate keys: `SKILL010_MALFORMED_INPUT`
- non-mapping root, including empty payload or YAML null: `SKILL003_INVALID_YAML_ROOT`
- invalid UTF-8 or UTF-8 BOM: `SKILL008_INVALID_ENCODING`
- required field missing, unknown field, type mismatch, invalid value, or invalid `version`: respective schema diagnostic from Section 8.2

Markdown validation is deferred and cannot produce a diagnostic in the initial scope. A failure to read or process the input is a CLI operational error under Section 9, not a metadata validation diagnostic.

## 5. Metadata schema

This section defines a single, exact, provisional structural schema for the initial validator. It does not claim canonical approval or compatibility with any external consumer.

### 5.1 Provisional parser profile

The following is the required semantic profile for any future parser implementation:

- YAML front matter enclosed by `---` delimiters
- strict UTF-8 input; reject, do not strip, a leading UTF-8 BOM
- one YAML document occupies the payload; reject a standalone YAML document-end marker (`...`) inside the payload. The first standalone `---` after the opening delimiter closes front matter, so a second YAML document cannot be represented within this profile; text after that terminator is Markdown body and is not parsed as YAML
- top-level YAML document must parse as a mapping; empty payload and YAML null are invalid roots
- reject duplicate mapping keys at every level before constructing a mapping; do not keep-first or keep-last
- reject anchors, aliases, and explicit tags
- use YAML 1.2 Core Schema scalar resolution; do not apply YAML 1.1 boolean coercions such as `yes`/`no`
- resulting values must satisfy the field types in Sections 5.2–5.4; booleans and numbers are not strings and are invalid where strings are required
- unknown fields are rejected by default in the initial schema
- null values are rejected for every field when present and reported as `SKILL005_INVALID_TYPE`
- for every non-`version` string field, an empty or whitespace-only value (after trimming for this check only) is invalid and reported as `SKILL016_INVALID_VALUE`; the original value is not normalized
- `version` is checked against its exact format expression without trimming; any nonmatching value, including an empty or whitespace-only value, is reported as `SKILL007_INVALID_VERSION`

Parser syntax/duplicate errors are reported as `SKILL010_MALFORMED_INPUT`; non-mapping roots use `SKILL003_INVALID_YAML_ROOT`. Parser-provided error text is not emitted. A parser may provide line and column; otherwise the location is null.

No YAML parser dependency or implementation exists in the repository. Selecting a library/version or a dependency-free parser is therefore not established. **Recommended implementation default:** prefer an established parser that supports duplicate-key rejection and YAML 1.2 Core Schema, subject to dependency approval; do not write an ad hoc general-purpose YAML parser. A chosen parser must pass the semantic conformance cases above. The exact library and version are implementation-dependent and must be recorded before implementation acceptance. This section is a `PROVISIONAL ASSUMPTION`, not external compatibility evidence.

### 5.2 Exact minimal valid Skill metadata example

The following YAML front matter is the exact minimal valid input for the initial structural validator:

```yaml
---
name: example-skill
description: Minimal skill metadata for structural validation.
---
```

The `name` and `description` fields are required. The `version` field is optional in the initial provisional schema.

The exact field contract for the initial provisional schema is:

- `name`: required, string, non-empty after trimming
- `description`: required, string, non-empty after trimming
- `version`: optional, string only if present
- `tags`: optional, array of non-empty strings
- `license`: optional, non-empty string if present
- `owner`: optional, non-empty string if present
- `applies_to`: optional, array of non-empty strings
- any other top-level field: rejected by the initial schema

`missing`, `null`, and empty strings are treated as distinct states:

- missing field: invalid if required
- explicit `null`: invalid for every field if present; optional means the key may be omitted
- empty or whitespace-only string: invalid after trimming for every non-`version` string field, reported as `SKILL016_INVALID_VALUE`
- `version`: must match its format expression without trimming; a nonmatching value, including empty or whitespace-only strings, is reported as `SKILL007_INVALID_VERSION`
- empty array: valid for `tags` and `applies_to`; no other field accepts an array
- `schema_version` in input metadata: unknown and therefore invalid under the default unknown-field rule; it is not part of this schema

### 5.3 Required and optional fields

The provisional schema is intentionally narrow.

Required fields:

- `name`: string
- `description`: string

Optional fields:

- `version`: string
- `tags`: array of non-empty strings; empty array is valid
- `license`: non-empty string when present
- `owner`: non-empty string when present
- `applies_to`: array of non-empty strings; empty array is valid

Unknown fields are rejected in the initial draft. This is the default policy unless a future human decision declares different behavior.

### 5.4 Type rules

The validator shall apply the following rules:

- `name`: string, non-empty after trimming
- `description`: string, non-empty after trimming
- `version`: string only when present; must match `^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?$`
- `tags`: array of strings, each element non-empty after trimming
- `license`: non-empty string when present
- `owner`: non-empty string when present
- `applies_to`: array of non-empty strings
- nested objects are not allowed in the initial provisional schema
- recursive arrays and object nesting are invalid in the initial schema; resource-limit enforcement for excessive nesting is separately `DEFERRED`

### 5.5 Unknown-field policy

The default policy for the provisional schema is:

- reject unknown top-level fields
- reject unknown nested fields when present
- require a future approved decision to permit unknown fields

This is intentionally strict and narrow for reviewability.

## 6. Version syntax and compatibility semantics

Version handling is `PROVISIONAL ASSUMPTION` and not a public compatibility claim.

### 6.1 Provisional version syntax

When `version` is present, it must match the following regular expression:

```text
^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?$
```

Examples of valid values:

- `1.0.0`
- `1.2.3-beta`

Examples of invalid values:

- `latest`
- `v1.2.3`
- `1.2`
- `1.2.3-`

The regex is applied to the complete YAML-decoded string, without trimming. Skill metadata `version` is unrelated to the JSON result `schema_version` and to any validator release version.

### 6.2 Compatibility semantics

The validator does not infer runtime compatibility, provider compatibility, or repository-wide canonical adoption from version syntax alone. A valid `version` field is only a metadata string under this provisional schema.

## 7. Input encoding and resource limits

### 7.1 Encoding

The provisional validator accepts UTF-8 input only. Files that cannot be decoded as UTF-8 are invalid.

### 7.2 Resource-limit policy

This draft chooses `OPTION B` from the P035 finding: resource-boundary validation is `DEFERRED` for the initial validator.

The document explicitly does not define numeric limits for file size, front-matter length, nesting depth, number of fields, or array length. These limits are not specified in this draft and are excluded from the initial acceptance subset.

This means:

- resource-limit enforcement is `DEFERRED`
- corresponding tests are `DEFERRED`
- no denial-of-service or production-security claim is made
- future resource limits require a human decision and a specific validator design

The parser profile still rejects nested objects and recursive arrays as invalid metadata; deferring resource limits does not make those shapes valid.

## 8. Diagnostic and JSON result contract

This section defines the `PROPOSED INTERNAL CONTRACT` for the validator. It remains provisional and is not a public compatibility guarantee.

### 8.1 Result object

The top-level result object shall have the following exact field names and types:

```json
{
  "schema_version": "string",
  "file": "string",
  "status": "string",
  "diagnostics": [
    {
      "id": "string",
      "severity": "string",
      "message": "string",
      "location": {
        "path": "string",
        "line": "integer|null",
        "column": "integer|null"
      },
      "code": "string|null"
    }
  ]
}
```

Required fields:

- `schema_version`: string, required
- `file`: string, required
- `status`: string, required; one of `valid`, `invalid`, or `error`
- `diagnostics`: array, required

Diagnostic object fields:

- `id`: string, required
- `severity`: string, required; one of `error`, `warning`, or `info`
- `message`: string, required
- `location`: object, required; path is string, line/column are integer or null
- `code`: string or null, required

### 8.2 Diagnostic IDs

The provisional diagnostic catalog is:

- `SKILL001_MISSING_FRONT_MATTER`
- `SKILL002_INVALID_DELIMITER`
- `SKILL003_INVALID_YAML_ROOT`
- `SKILL004_MISSING_REQUIRED_FIELD`
- `SKILL005_INVALID_TYPE`
- `SKILL006_UNKNOWN_FIELD`
- `SKILL007_INVALID_VERSION`
- `SKILL008_INVALID_ENCODING`
- `SKILL009_INVALID_CLI_ARGUMENTS`
- `SKILL010_MALFORMED_INPUT`
- `SKILL012_INTERNAL_ERROR`
- `SKILL014_INPUT_NOT_FOUND`
- `SKILL015_INPUT_UNREADABLE`
- `SKILL016_INVALID_VALUE`

`SKILL011_UNSUPPORTED_SCHEMA_VERSION` is not used because the initial input schema has no schema-version field (Section 3.2). `SKILL013_MARKDOWN_VALIDATION_DEFERRED` is not emitted because deferred features are not exposed as validator operations. These identifiers are reserved and are not part of the initial catalog. Any future catalog change requires a reviewed specification revision.

For all diagnostics, severity is `error`. Locations use the input basename as `path`; source line and column are positive 1-based integers when determinable and otherwise null. Fixed message and code strings for validation diagnostics follow the stable ID suffix in snake case for `code`; messages must not include parser text or absolute paths. Operational diagnostic messages and codes are fixed in Section 9.3. For a missing required field, the location is the closing delimiter at column 1; for an unknown field, the key start; for a type, value, or format failure, the offending value start.

Fixed validation messages are:

| ID | `code` | `message` |
| --- | --- | --- |
| `SKILL001_MISSING_FRONT_MATTER` | `missing_front_matter` | `Front matter is missing.` |
| `SKILL002_INVALID_DELIMITER` | `invalid_delimiter` | `Front matter delimiter is invalid.` |
| `SKILL003_INVALID_YAML_ROOT` | `invalid_yaml_root` | `Front matter root must be a mapping.` |
| `SKILL004_MISSING_REQUIRED_FIELD` | `missing_required_field` | `Required field '{field}' is missing.` |
| `SKILL005_INVALID_TYPE` | `invalid_type` | `Field '{field}' has an invalid type.` |
| `SKILL006_UNKNOWN_FIELD` | `unknown_field` | `Unknown field.` |
| `SKILL007_INVALID_VERSION` | `invalid_version` | `Field 'version' has an invalid value.` |
| `SKILL008_INVALID_ENCODING` | `invalid_encoding` | `Input is not valid UTF-8.` |
| `SKILL010_MALFORMED_INPUT` | `malformed_input` | `Malformed front matter.` |
| `SKILL016_INVALID_VALUE` | `invalid_value` | `Field '{field}' has an invalid value.` |

The `{field}` placeholder used by missing-required-field, type, and invalid-value messages is replaced only by a field name from this specification, never by an arbitrary input value. Unknown-field messages do not echo the untrusted field name.

### 8.3 Diagnostic ordering

For a metadata validation result, diagnostics are ordered by category: (1) encoding errors, (2) front-matter delimiter errors, (3) YAML syntax/root errors, (4) missing/unknown fields, (5) field type/format errors. Within each category, sort by line, column, then diagnostic ID; null locations sort after known locations. Invalid encoding is exclusive and prevents delimiter parsing. IO, argument, and internal failures are exclusive operational results and are not combined with metadata diagnostics. No warning or informational diagnostics are emitted in the initial scope.

### 8.4 Example JSON result: valid input

```json
{
  "schema_version": "0.1-provisional",
  "file": "example-skill.md",
  "status": "valid",
  "diagnostics": []
}
```

### 8.5 Example JSON result: invalid input

```json
{
  "schema_version": "0.1-provisional",
  "file": "example-skill.md",
  "status": "invalid",
  "diagnostics": [
    {
      "id": "SKILL004_MISSING_REQUIRED_FIELD",
      "severity": "error",
      "message": "Required field 'description' is missing.",
      "location": {
        "path": "example-skill.md",
        "line": 3,
        "column": 1
      },
      "code": "missing_required_field"
    }
  ]
}
```

## 9. CLI behavior and exit-code semantics

This section defines a `PROPOSED INTERNAL CONTRACT`; it is not an approved public interface.

### 9.1 Input contract

The CLI accepts exactly one file path as its sole positional argument. Relative and absolute paths are accepted as supplied; this is not a path-containment guarantee. The validator opens only that file and does not recurse.

It does not accept:

- directory arguments in the initial draft
- recursive discovery
- registry or dependency resolution
- automatic installation
- runtime execution of Skill content

### 9.2 Exit codes

Proposed exit codes for the initial validator:

- `0`: valid input and no errors
- `1`: validation errors found; output JSON uses `status: "invalid"`
- `2`: invalid invocation or expected input IO failure; output JSON uses `status: "error"`
- `3`: unexpected internal failure; output JSON uses `status: "error"`

These codes are `PROPOSED INTERNAL CONTRACT` only and are not public compatibility guarantees.

### 9.3 Output and operational-error contract

For every invocation, stdout contains exactly one compact UTF-8 JSON object followed by one LF; stderr is empty. No human-readable mode is provided. JSON object keys appear in this order: `schema_version`, `file`, `status`, `diagnostics`. Each diagnostic uses the Section 8.1 key order. `schema_version` is always the literal `0.1-provisional`. `file` is the basename after splitting the supplied argument on either `/` or `\`, or `""` when no single file argument is available; do not emit an absolute path. JSON escaping follows RFC 8259. Serialize the complete result before writing stdout so a serialization failure emits no partial JSON; if serialization is impossible, stdout is empty and exit code `3`.

Each invocation produces one result. File-level parse/validation errors do not stop collection of independent metadata diagnostics; a front-matter delimiter, decoding, or YAML parse failure stops metadata validation because no reliable mapping exists. Operational failures stop validation and produce one diagnostic only. Error messages are fixed generic strings and must not include exception text, absolute paths, environment values, or stack traces.

Operational outcomes:

- no argument, more than one argument, or unsupported option: `error`, `SKILL009_INVALID_CLI_ARGUMENTS`, exit `2`
- nonexistent input: `error`, `SKILL014_INPUT_NOT_FOUND`, exit `2`
- other open/read permission or IO failure: `error`, `SKILL015_INPUT_UNREADABLE`, exit `2`
- unexpected exception: `error`, `SKILL012_INTERNAL_ERROR`, exit `3`
- invalid UTF-8 or malformed YAML/front matter: `invalid`, the corresponding validation diagnostic, exit `1`
- deferred Markdown or resource-limit feature: no option exists to invoke it; an attempted unsupported option follows invalid-arguments behavior

For operational errors, `location.path` and top-level `file` use the basename when available, or `""` when unavailable; line and column are null. The `code` is the stable snake-case form of the diagnostic ID suffix. The exact fixed message strings for operational diagnostics are respectively: `Invalid command-line arguments.`, `Input file not found.`, `Input file could not be read.`, and `Internal validator error.` These outputs do not imply filesystem isolation.

### 9.4 CLI behavior by condition

| Condition | Resulting JSON status | Exit code | Notes |
| --- | --- | --- | --- |
| valid input | `valid` | `0` | no diagnostics |
| missing required field | `invalid` | `1` | diagnostic emitted |
| malformed YAML front matter | `invalid` | `1` | diagnostic emitted |
| missing or invalid number of arguments | `error` | `2` | `SKILL009_INVALID_CLI_ARGUMENTS` |
| nonexistent input file | `error` | `2` | `SKILL014_INPUT_NOT_FOUND` |
| unreadable input file / IO error | `error` | `2` | `SKILL015_INPUT_UNREADABLE` |
| invalid encoding | `invalid` | `1` | diagnostic emitted |
| input contains `schema_version` | `invalid` | `1` | unknown field, `SKILL006_UNKNOWN_FIELD` |
| unsupported/deferred feature option | `error` | `2` | invalid arguments; no deferred operation is implemented |
| unexpected internal exception | `error` | `3` | `SKILL012_INTERNAL_ERROR`; generic output only |

## 10. Markdown validation

This draft chooses `OPTION B`: Markdown section validation is `DEFERRED` and excluded from the initial acceptance subset.

This means:

- the validator does not require Markdown headings in the initial draft
- the validator does not reject missing Markdown sections in the initial draft
- the corresponding tests are `DEFERRED`
- `SKILL013_MARKDOWN_VALIDATION_DEFERRED` is reserved and is not emitted

This is the narrower and more defensible option because the repository evidence does not establish an authoritative Markdown contract.

## 11. Decision register and unresolved issues

The following decisions remain unresolved and must remain labelled as such.

| Decision ID | Status | Options under consideration | Supporting evidence | Missing evidence | Effect on draft |
| --- | --- | --- | --- | --- | --- |
| D01 | PROVISIONAL ASSUMPTION | YAML front matter vs strict JSON vs constrained YAML | current repo sample uses YAML | external consumer evidence | keeps format provisional |
| D02 | PROVISIONAL ASSUMPTION | reject unknown fields vs allow unknown fields | repo docs prefer explicit boundaries | approved schema | initial default = reject unknowns |
| D03 | PROVISIONAL ASSUMPTION | version optional vs required | repo example has no version | approved metadata policy | version remains optional |
| D04 | DEFERRED | Markdown validation in scope or deferred | repo evidence does not define markdown contract | approved markdown contract | markdown validation deferred |
| D05 | DEFERRED | dependency resolution | repo docs prohibit runtime assumptions | registry policy | dependency checks excluded |
| D06 | PROVISIONAL ASSUMPTION | structural-only vs runtime enforcement | repo docs separate workflow from runtime security | security contract | structural-only remains in scope |
| D07 | DEFERRED | resource limits | no approved validator limits | numeric values and enforcement policy | resource validation deferred |
| D08 | PROPOSED INTERNAL CONTRACT | exact CLI and output semantics; output `schema_version` is `0.1-provisional`, with no input schema-version field | repo docs demand evidence and deterministic output | authorized public interface | CLI/output contract remains proposed-only |
| D09 | DEFERRED | broader markdown or schema semantics | no approved contract | authoritative markdown/schema choice | deferred |
| D10 | REQUIRES HUMAN DECISION | governance approval model | repo docs include stop gates and blockers | authority process | not assumed |
| D11 | IMPLEMENTATION-DEPENDENT | concrete YAML parser library/version or dependency-free constrained parser | no parser dependency or implementation exists in this repository | parser choice, dependency policy, and conformance evidence | semantic parser profile is specified; implementation acceptance requires a conforming parser and duplicate-key test |

### 11.1 Decision-dependent parser implementation

The parser semantics above are specified, but the implementation mechanism is not selected. The following options are presented for review, not as approved decisions:

| Option | Trade-off | Recommendation |
| --- | --- | --- |
| A. Select an established YAML parser with YAML 1.2 Core Schema and strict duplicate-key rejection | Stronger standards handling; may add a dependency and requires approval of its package/version and supply-chain maintenance. | Preferred only if dependency addition is explicitly accepted. |
| B. Implement a deliberately restricted YAML subset parser with no new dependency | Avoids a package, but creates parser-maintenance risk and must reject all syntax outside the exact subset; it must not be described as general YAML. | Do not choose without separate engineering review and conformance tests. |
| C. Defer validator implementation until an acceptable parser can be selected | No dependency or parser risk is introduced now; implementation waits. | Safest default if dependency authority or parser scope is unresolved. |

An authorized decision-maker must approve any new dependency if project policy requires that approval. A parser choice must not change the semantic oracle in Section 5.1 without a reviewed spec revision.

The D01–D03 defaults remain provisional values suitable for specification review, not canonical decisions. A human reviewer may review them without resolving every compatibility question; implementation against them requires an accepted baseline, and external/public compatibility claims require separate evidence and authorization.

## 12. Test oracle and acceptance subset

This document defines a test specification only. It does not execute tests.

### 12.1 Exact valid input

The valid minimal input for the initial validator is:

```yaml
---
name: example-skill
description: Minimal skill metadata for structural validation.
---
```

This input must validate successfully under the provisional schema and output:

```json
{
  "schema_version": "0.1-provisional",
  "file": "example-skill.md",
  "status": "valid",
  "diagnostics": []
}
```

### 12.2 Test matrix

Readiness labels describe specification precision only; none imply implementation or execution. Unless otherwise stated, invoke the proposed CLI as `<validator> <fixture-path>`, expect exactly one compact JSON line on stdout, empty stderr, and no test is considered passed until actually run. For shorthand field-mutation fixtures, begin with Section 12.1 saved with LF line endings and a final LF, then apply only the stated mutation while retaining opening and closing delimiters.

`SPECIFIED` means the expected behavior is stated but the fixture or oracle is insufficiently detailed for a direct test. `READY_FOR_IMPLEMENTATION` means a future test can be written from this contract. `IMPLEMENTATION_DEPENDENT` means an implementation/test seam or selected parser is still needed. `DEFERRED` means out of scope. `BLOCKED_BY_DECISION` means a required compatibility, security, or governance choice prevents a stable oracle. These labels are not execution results.

| Test ID | Fixture / input condition | Expected status and diagnostic IDs in order | Exit | Additional assertion | Readiness |
| --- | --- | --- | --- | --- | --- |
| T01 | UTF-8 file `t01.md` containing `body` with no opening delimiter | `invalid`: `SKILL001_MISSING_FRONT_MATTER` | 1 | One diagnostic; location line 1, column 1 | READY_FOR_IMPLEMENTATION |
| T02 | Exact bytes `---\nname: example-skill\n` in `t02.md`, ending at EOF without a closing delimiter | `invalid`: `SKILL002_INVALID_DELIMITER` | 1 | One diagnostic at EOF, line 3, column 1 | READY_FOR_IMPLEMENTATION |
| T03 | Exact file `---\n[]\n---\n` in `t03.md` | `invalid`: `SKILL003_INVALID_YAML_ROOT` | 1 | One diagnostic at payload line 2, column 1 | READY_FOR_IMPLEMENTATION |
| T04 | Valid minimal fixture with `name` removed | `invalid`: `SKILL004_MISSING_REQUIRED_FIELD` | 1 | Missing-field location is the closing delimiter line, column 1 | READY_FOR_IMPLEMENTATION |
| T05 | Valid minimal fixture with `description` removed | `invalid`: `SKILL004_MISSING_REQUIRED_FIELD` | 1 | Missing-field location is the closing delimiter line, column 1 | READY_FOR_IMPLEMENTATION |
| T06 | `name: 12` and valid description | `invalid`: `SKILL005_INVALID_TYPE` | 1 | Numeric scalar must not be accepted as a string | READY_FOR_IMPLEMENTATION |
| T07 | Minimal fixture plus `extra: value` | `invalid`: `SKILL006_UNKNOWN_FIELD` | 1 | Location points to `extra` key | READY_FOR_IMPLEMENTATION |
| T08 | Minimal fixture plus `version: latest` | `invalid`: `SKILL007_INVALID_VERSION` | 1 | Location points to the version scalar | READY_FOR_IMPLEMENTATION |
| T09 | Bytes `---\nname: example-skill\ndescription: ` + `0xFF` + `\n---\n` in `t09.md` | `invalid`: `SKILL008_INVALID_ENCODING` | 1 | No parser error text or decoded replacement character is emitted | READY_FOR_IMPLEMENTATION |
| T10 | File size, front-matter size, or parser-resource boundary | DEFERRED | DEFERRED | No resource guarantee or threshold is specified | DEFERRED |
| T11 | Missing or malformed Markdown headings after valid front matter | DEFERRED | DEFERRED | Markdown body is not validated | DEFERRED |
| T12 | Invoke `<validator>` with no argument | `error`: `SKILL009_INVALID_CLI_ARGUMENTS` | 2 | `file` is `""`; exact operational message per Section 9.3 | READY_FOR_IMPLEMENTATION |
| T13 | Exact minimal input from Section 12.1 saved as `example-skill.md` | `valid`: none | 0 | Exact result object from Section 12.1 | READY_FOR_IMPLEMENTATION |
| T14 | Exact multi-error fixture and oracle in Section 12.3 | `invalid`: `SKILL006_UNKNOWN_FIELD`, `SKILL004_MISSING_REQUIRED_FIELD`, `SKILL007_INVALID_VERSION` | 1 | Exact compact JSON line and ordering in Section 12.3; unknown field name is not echoed | READY_FOR_IMPLEMENTATION |
| T15 | Duplicate key fixture in Section 12.3 | `invalid`: `SKILL010_MALFORMED_INPUT` | 1 | Reject before mapping construction; parser-specific text is suppressed | IMPLEMENTATION_DEPENDENT |
| T16 | Minimal valid input plus `schema_version: "0.1-provisional"` | `invalid`: `SKILL006_UNKNOWN_FIELD` | 1 | Input has no schema-version field; output `schema_version` remains `0.1-provisional`; unknown field name is not echoed | READY_FOR_IMPLEMENTATION |
| T17 | Test harness injects a controlled unexpected exception at the validation boundary | `error`: `SKILL012_INTERNAL_ERROR` | 3 | Generic fixed message, null location, empty stderr, no traceback | IMPLEMENTATION_DEPENDENT |
| T18 | Run the exact T14 fixture twice in the same implementation/runtime | `invalid`: same three IDs as T14 | 1 on each run | stdout bytes identical; stderr empty; JSON parses against Section 8.1 | READY_FOR_IMPLEMENTATION |
| T19 | Exact invalid fixture and expected JSON in Section 12.3 | `invalid`: `SKILL004_MISSING_REQUIRED_FIELD` | 1 | stdout parses as JSON and matches the exact compact line in Section 12.3 | READY_FOR_IMPLEMENTATION |
| T20 | Invoke with nonexistent path `missing-t20.md` | `error`: `SKILL014_INPUT_NOT_FOUND` | 2 | `file` and `location.path` are `missing-t20.md`; fixed message; empty stderr | READY_FOR_IMPLEMENTATION |
| T21 | Test harness injects an `OSError` while opening an existing fixture | `error`: `SKILL015_INPUT_UNREADABLE` | 2 | Generic fixed message; basename only; null line/column; empty stderr | IMPLEMENTATION_DEPENDENT |
| T22 | Valid minimal bytes prefixed with UTF-8 BOM | `invalid`: `SKILL008_INVALID_ENCODING` | 1 | Reject BOM; do not strip it | READY_FOR_IMPLEMENTATION |
| T23 | Exact payload has `name: example-skill`, then `...`, then the closing delimiter | `invalid`: `SKILL010_MALFORMED_INPUT` | 1 | One diagnostic; parser text suppressed; the closing `---` ends the only permitted document | IMPLEMENTATION_DEPENDENT |
| T24 | Separate fixtures contain either `name: &n example-skill` with `description: *n`, or `name: !!str example-skill` | `invalid`: `SKILL010_MALFORMED_INPUT` | 1 | Each fixture yields one diagnostic; no alias expansion or tag construction | IMPLEMENTATION_DEPENDENT |
| T25 | Separate fixtures use `name: true` and `name: 12`; a conformance companion uses `name: yes` with valid description | true/numeric fixtures `invalid`: `SKILL005_INVALID_TYPE`; `yes` companion `valid` | 1 for invalid cases; 0 for companion | `yes` is a string under YAML 1.2 Core and is not coerced to boolean | IMPLEMENTATION_DEPENDENT |
| T26 | Delimited empty payload or YAML `null` root | `invalid`: `SKILL003_INVALID_YAML_ROOT` | 1 | One diagnostic; no field-level diagnostics | READY_FOR_IMPLEMENTATION |
| T27 | Minimal fixture with `name: ""`; separate cases use `name: "   "` and add `license: ""` | `invalid`: `SKILL016_INVALID_VALUE` | 1 | Empty or whitespace-only non-version strings are rejected; field name is safe and deterministic | READY_FOR_IMPLEMENTATION |
| T28 | Minimal fixture with `name: null` | `invalid`: `SKILL005_INVALID_TYPE` | 1 | Present null is not treated as a missing optional value | READY_FOR_IMPLEMENTATION |
| T29 | Minimal fixture plus `tags: []` and `applies_to: []` | `valid`: none | 0 | Both explicitly permitted empty arrays are accepted | READY_FOR_IMPLEMENTATION |
| T30 | Minimal fixture plus `version: ""`; separate case uses `version: "   "` | `invalid`: `SKILL007_INVALID_VERSION` | 1 | Version is checked without trimming; format diagnostic takes precedence over generic empty-value handling | READY_FOR_IMPLEMENTATION |

### 12.3 Exact test-oracle fixtures for T14–T19

The T14 fixture is the following UTF-8 file named `t14.md`, with LF line endings and a final LF:

```yaml
---
name: example-skill
version: latest
extra: value
---
Body is ignored.
```

The required T14 diagnostic messages and locations are:

1. `SKILL006_UNKNOWN_FIELD`, severity `error`, message `Unknown field.`, location `t14.md:4:1`, code `unknown_field`.
2. `SKILL004_MISSING_REQUIRED_FIELD`, severity `error`, message `Required field 'description' is missing.`, location `t14.md:5:1`, code `missing_required_field`.
3. `SKILL007_INVALID_VERSION`, severity `error`, message `Field 'version' has an invalid value.`, location `t14.md:3:10`, code `invalid_version`.

The category ordering in Section 8.3 places unknown/missing-field diagnostics before type/format diagnostics; source order applies within the first category.

The T15 fixture is a UTF-8 file named `t15.md` with LF line endings and a final LF:

```yaml
---
name: example-skill
name: duplicate
description: Duplicate-key test.
---
```

It returns one `SKILL010_MALFORMED_INPUT` diagnostic at the second `name` key (line 3, column 1), code `malformed_input`, severity `error`, message `Malformed front matter.`. The parser must not silently keep either key.

T15 stdout is exactly the following compact UTF-8 JSON plus one final LF; stderr is empty:

```json
{"schema_version":"0.1-provisional","file":"t15.md","status":"invalid","diagnostics":[{"id":"SKILL010_MALFORMED_INPUT","severity":"error","message":"Malformed front matter.","location":{"path":"t15.md","line":3,"column":1},"code":"malformed_input"}]}
```

T16 uses the exact Section 12.1 fixture saved as `t16.md` with this additional line before the closing delimiter: `schema_version: "0.1-provisional"`. It returns `SKILL006_UNKNOWN_FIELD` at that key; it does not return `SKILL011_UNSUPPORTED_SCHEMA_VERSION`. Stdout is exactly the following compact UTF-8 JSON plus one final LF; stderr is empty:

```json
{"schema_version":"0.1-provisional","file":"t16.md","status":"invalid","diagnostics":[{"id":"SKILL006_UNKNOWN_FIELD","severity":"error","message":"Unknown field.","location":{"path":"t16.md","line":4,"column":1},"code":"unknown_field"}]}
```

T17 uses the Section 12.1 fixture saved as `t17.md`. It is not triggered through an undocumented public CLI flag. A future implementation test harness injects a controlled exception after reading the input and before emitting the result, then invokes the CLI entry point. Stdout is exactly the following compact UTF-8 JSON plus one final LF; stderr is empty and no traceback is emitted:

```json
{"schema_version":"0.1-provisional","file":"t17.md","status":"error","diagnostics":[{"id":"SKILL012_INTERNAL_ERROR","severity":"error","message":"Internal validator error.","location":{"path":"t17.md","line":null,"column":null},"code":"internal_error"}]}
```

This requires an implementation seam suitable for testing and remains implementation-dependent.

T18 runs T14 twice and compares complete stdout bytes; both runs must equal the following compact UTF-8 JSON plus one final LF, and both stderr streams must be empty:

```json
{"schema_version":"0.1-provisional","file":"t14.md","status":"invalid","diagnostics":[{"id":"SKILL006_UNKNOWN_FIELD","severity":"error","message":"Unknown field.","location":{"path":"t14.md","line":4,"column":1},"code":"unknown_field"},{"id":"SKILL004_MISSING_REQUIRED_FIELD","severity":"error","message":"Required field 'description' is missing.","location":{"path":"t14.md","line":5,"column":1},"code":"missing_required_field"},{"id":"SKILL007_INVALID_VERSION","severity":"error","message":"Field 'version' has an invalid value.","location":{"path":"t14.md","line":3,"column":10},"code":"invalid_version"}]}
```

T19 uses `t19.md` containing exactly the three lines `---`, `name: example-skill`, `---`, each LF-terminated. Expected stdout is the following compact JSON plus one final LF; stderr is empty:

```json
{"schema_version":"0.1-provisional","file":"t19.md","status":"invalid","diagnostics":[{"id":"SKILL004_MISSING_REQUIRED_FIELD","severity":"error","message":"Required field 'description' is missing.","location":{"path":"t19.md","line":3,"column":1},"code":"missing_required_field"}]}
```

T19's stdout must parse as JSON conforming to Section 8.1. The JSON is a validation result; the YAML input is not JSON.

T20 must not include the requested path beyond its basename in output; use the exact operational message and JSON field contract in Sections 8.1 and 9.3. T21 uses a test harness rather than filesystem permission changes, which can be unreliable across host platforms; it must not print the injected OS error text. T22 uses the exact Section 12.1 bytes prefixed by `EF BB BF`. T23's exact file is `---\nname: example-skill\n...\n---\n`. T23–T25 are conformance tests for the YAML profile in Section 5.1. T26 uses either `---\n\n---\n` or `---\nnull\n---\n` and expects the same root diagnostic.

T27, T28, and T30 use the Section 12.1 fixture with the named field changed exactly as shown. T29 adds both optional array fields with empty sequence values before the closing delimiter.

### 12.4 Initial acceptance subset

The proposed initial acceptance subset for a future implementation is:

- T01–T09, T12–T14, T16, T18–T20, T22, T26–T30
- T15, T17, T21, and T23–T25 require the implementation-dependent parser or test seam to be selected and demonstrated

This subset excludes resource-limit and Markdown validation because those decisions are deferred in the current draft.

No test has been executed by this document. `READY_FOR_IMPLEMENTATION` is not a PASS result.

## 13. Acceptance criteria for specification review

This draft is acceptable for review only if all of the following are true:

- the exact minimal valid input is explicitly defined
- the `version` field is clearly optional in the initial schema
- unknown fields are rejected by default
- the JSON result schema and diagnostic schema are explicit
- the CLI and exit-code behavior are internally consistent
- the initial input schema has no `schema_version` field; the output contract identifier is explicit
- parser semantics, duplicate-key rejection, and the parser-selection dependency are explicit
- Markdown validation is either in scope with exact rules or deferred and excluded
- resource limits are either specified or deferred
- the document clearly states that it is an internal provisional contract, not a canonical or public compatibility guarantee

## 14. Evidence, assumptions, and unresolved questions

### 14.1 Evidence-supported statements

The draft is grounded in the repository evidence that:

- [skills/implementation/implementation.md](../../skills/implementation/implementation.md) contains YAML front matter with `---` delimiters
- [skills/README.md](../../skills/README.md) defines the repo as intentionally narrow and evidence-driven
- [docs/compatibility/README.md](../compatibility/README.md) defines compatibility status labels
- [providers/README.md](../../providers/README.md) requires provider-neutral separation
- [integrations/README.md](../../integrations/README.md) keeps the integration boundary narrow
- [workflows/spec-to-implementation/README.md](../../workflows/spec-to-implementation/README.md) requires explicit stop gates and evidence before completion

### 14.2 Assumptions

The specification assumes:

- the actual project may preserve YAML front matter as the provisional repository convention while compatibility evidence is gathered
- no implementation or public compatibility guarantee is authorized by this draft
- structural validation may proceed without dependency resolution or runtime security enforcement

### 14.3 Unresolved questions

The following remain unresolved and require human action before a broader claim is made:

- final canonical front-matter format selection
- exact external consumer compatibility results
- parser library/version or an approved dependency-free restricted parser choice
- exact markdown contract if it is later required
- exact resource-limit values if enforcement is later approved
- final governance decision authority

## 15. Final review status

This document remains a `PROVISIONAL ASSUMPTION` and `PROPOSED INTERNAL CONTRACT` only. It is not a formal approval, not a canonical standard, not an implementation authorization, and not a public compatibility guarantee.

The key boundary remains:

- structure may be proposed and reviewed
- human approval remains separate
- implementation authorization remains separate
- operational claims remain explicitly outside the scope of this draft

## 16. Amendment history

- **P049:** Aligned the top-level scope, parser type description, invalid version example, and duplicate-key test expectation.
- **P050:** Defined that input metadata has no schema-version field; specified the provisional YAML semantic profile and parser-selection dependency; aligned empty/null handling, CLI operational errors, and deterministic JSON behavior; replaced underspecified T14–T19 oracles and readiness labels; retained all provisional status and scope boundaries.
- **P051:** Audited schema/version, YAML, CLI, diagnostics, and test contracts; removed untrusted unknown-field names from diagnostic messages and made null-to-type-diagnostic behavior explicit.

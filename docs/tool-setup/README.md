# Tool setup

This repository keeps tooling requirements intentionally minimal and repository-native.

## Baseline expectations

- Prefer the repository's existing scripts and validators.
- Inspect the repository before assuming a language, package manager, or task runner exists.
- Validate changes with the smallest relevant command that checks the affected behavior.
- Record the exact commands that actually ran so the final report has evidence.

## Markdown link check

Run `python3 scripts/check_markdown_links.py` from any directory to check inline relative Markdown links and image targets throughout the repository. The command uses only the Python standard library and exits nonzero when a local target is missing.

The check does not validate anchors, external URLs, reference-style links, balanced parentheses in destinations, or full Markdown syntax.

## Skill contract registry

`scripts/skill_registry.py` provides an in-memory `SkillContract` and `SkillRegistry`. A contract requires an identifier, display name, description, and repository-relative source path. `version`, `category`, `tags`, `inputs`, `outputs`, `tools`, and `capabilities` are optional declarations; the registry does not infer runtime support from them. `contract_version` separately identifies the invocation contract and defaults to `1.0.0` when omitted.

```python
from pathlib import Path

from scripts.skill_registry import SkillRegistry, discover_skills

root = Path(".")
discovered = discover_skills(root)
if discovered.issues:
    raise ValueError(discovered.issues)

registry = SkillRegistry(root)
for contract in discovered.skills:
    registry.register(contract)

implementation = registry.get("implementation")
print(implementation.name, implementation.source_path)
```

Contracts can also be created with `SkillContract.from_mapping(...)` and registered explicitly. Registration resolves the source path beneath the supplied repository root and requires it to be a file. Duplicate identifiers and missing lookups raise explicit errors.

`discover_skills` discovers native Skill packages only at
`skills/<skill-name>/SKILL.md`; the front-matter `name` must match the package
directory. It reads the scalar `name` and `description` fields without
importing or executing the file. Other Markdown workflow documents and
`*.manifest.json` files are not native Skill candidates. This is not a general
YAML parser or the provisional structural validator. Discovery results
describe metadata only and do not authorize Skill execution. A canonical entry
with missing or malformed front matter is reported as a discovery issue rather
than silently registered or ignored. Run its tests with
`python3 -m unittest discover -s tests -v`.

## Declarative Skill manifests

For complete runtime metadata, use the strict JSON loader in
`scripts/skill_manifest.py`. JSON is supported by the Python standard library,
so this path adds no parser dependency. Manifest format version `1` is an
integer `manifest_version`; unsupported versions, duplicate JSON object keys,
unknown keys, missing required fields, and malformed types are rejected.
Optional contract fields omitted from a manifest retain the `SkillContract`
defaults. Nothing is inferred from Markdown text.

A manifest contains every representable contract declaration:

```json
{
  "manifest_version": 1,
  "identifier": "text-analysis",
  "name": "Local text analysis",
  "description": "Count characters, words, and lines for supplied text.",
  "source_path": "skills/implementation/SKILL.md",
  "version": "0.1",
  "contract_version": "1.2.0",
  "category": "text-processing",
  "tags": ["text", "analysis"],
  "inputs": [],
  "outputs": [],
  "input_fields": [
    {"name": "text", "value_type": "string", "required": true},
    {
      "name": "locale",
      "value_type": "string",
      "required": false,
      "nullable": true
    }
  ],
  "output_fields": [
    {"name": "statistics", "value_type": "object", "required": true}
  ],
  "strict_inputs": true,
  "strict_outputs": true,
  "tools": ["local.text-statistics"],
  "capabilities": ["local-text-analysis"]
}
```

This example is stored as [text-analysis.manifest.json](../../skills/text-analysis.manifest.json)
and uses the implementation Skill only as a repository-local source reference.
The framework manifest is not a native Skill package, does not execute its
source, and is not automatically loaded by native Skill discovery.

`version` is optional Skill metadata; `contract_version` is the canonical
numeric `major.minor.patch` contract label and defaults to `"1.0.0"` when
omitted. They are independent. Field declarations use the existing
`SkillValueType` values (`string`, `integer`, `number`, `boolean`, `object`,
`array`) and the existing `required`/`nullable` rules. Legacy `inputs` and
`outputs` name lists are also represented. If provided, these must be arrays
of non-empty strings and retain their existing semantics.

Use the registry's explicitly configured repository root for both loading and
registration:

```python
from pathlib import Path

from scripts.skill_manifest import load_skill_manifest

# Resolve this from the known location of application configuration; this
# example assumes the application module lives directly under scripts/.
repository_root = Path(__file__).resolve().parents[1]
manifest = load_skill_manifest(
    Path("skills/text-analysis.manifest.json"),
    repository_root,
)
print(manifest.manifest_version, manifest.contract.identifier)
```

Register the validated declaration through a `SkillPipeline`'s existing
registry. The executor and implementation are application configuration, not
manifest data:

```python
from pathlib import Path

from scripts.skill_manifest import register_skill_manifest
from scripts.skill_pipeline import LocalSkillExecutionAdapter, SkillPipeline

# Assuming this application module lives directly under scripts/.
repository_root = Path(__file__).resolve().parents[1]
# analyze_text is trusted application code configured by the application,
# not loaded from the manifest or the Markdown source.
pipeline = SkillPipeline(
    repository_root,
    execution_adapter=LocalSkillExecutionAdapter({"text-analysis": analyze_text}),
    tool_executor=tool_executor,
)
contract = register_skill_manifest(
    pipeline.registry,
    Path("skills/text-analysis.manifest.json"),
)
print(contract.identifier, contract.contract_version)
```

`register_skill_manifest(registry, manifest_path)` uses the root fixed on that
registry and registers through `SkillRegistry.register(...)`. Duplicate
identifiers are rejected and never replace existing entries. Errors use
`SkillManifestError` with a safe field-level explanation and stable `.code`
values such as `invalid_manifest_json`, `unsupported_manifest_version`,
`unsafe_source_path`, `invalid_skill_contract`, and
`duplicate_skill_identifier`. For example:

```python
from scripts.skill_manifest import SkillManifestError, register_skill_manifest

try:
    register_skill_manifest(pipeline.registry, manifest_path)
except SkillManifestError as error:
    print(error.code, error.skill_identifier)
```

An incompatible contract version is rejected by `SkillRegistry.resolve(...)`
and by `SkillWorkflowAdapter` configuration; pipeline invocation also validates
the requested version before execution. An explicitly configured Skill with no
matching implementation returns the pipeline's `UNAVAILABLE` result rather
than receiving a fallback implementation.

The loader resolves the manifest and declared source beneath the explicit
repository root, rejects traversal and resolved symlink escapes, and requires
the source to be a file. It does not read source contents, execute the manifest,
load callables, or perform provider dispatch. A manifest's `tools` list is a
contract allowlist only: actual calls still require the application's
explicitly configured execution adapter and `ToolExecutor` authorization.
Likewise, `capabilities` are descriptive declarations, not permission grants.
Manifest loading, registry registration, and Skill execution remain separate
steps. The registry still stores only one contract version per Skill
identifier, so a version label does not make historical versions available.

### Discovering and registering a manifest catalog

`discover_skill_manifests(repository_root)` discovers only lower-case
`*.manifest.json` filenames. It recursively scans the explicitly supplied
repository root, not every JSON file and not locations outside that root.
Results are absolute paths sorted by case-folded repository-relative path, with
the original path as a stable tie-breaker. Cache directories, virtual
environments, build outputs, and common generated directories are excluded;
directory symlinks are not traversed. A matching manifest file symlink that
resolves outside the root is rejected by the manifest loader.

Use the same explicitly configured root as the registry. The catalog loader
returns entries in discovery order with repository-relative manifest paths.
It validates every discovered file before returning; when any file is invalid
or identifiers conflict, `SkillManifestCatalogError.issues` contains the
ordered errors with the responsible manifest path, safe error code, and
identifier when available. Duplicate identifiers are rejected even when the
contract declarations are identical; differing declarations are identified as
conflicting metadata in the issue message.

```python
from pathlib import Path

from scripts.skill_manifest import (
    SkillManifestCatalogError,
    register_skill_manifest_catalog,
)
from scripts.skill_registry import SkillRegistry

registry = SkillRegistry(Path(".").resolve())
try:
    register_skill_manifest_catalog(registry)
except SkillManifestCatalogError as error:
    for issue in error.issues:
        print(issue.manifest_path, issue.code, issue.skill_identifier)
```

```python
from pathlib import Path

from scripts.skill_manifest import (
    load_skill_manifest_catalog,
    register_skill_manifest_catalog,
)
from scripts.skill_pipeline import InvocationRequest, SkillPipeline

repository_root = Path(__file__).resolve().parents[1]
catalog = load_skill_manifest_catalog(repository_root)
for entry in catalog.entries:
    print(entry.manifest_path, entry.manifest.contract.identifier)

# These are explicitly configured application objects, not manifest values.
pipeline = SkillPipeline(
    repository_root,
    execution_adapter=execution_adapter,
    tool_executor=tool_executor,
)
registered = register_skill_manifest_catalog(pipeline.registry)
text_contract = pipeline.registry.get("text-analysis")
result = pipeline.invoke(InvocationRequest(
    skill_identifier=text_contract.identifier,
    task="count this text",
    inputs={"text": "hello world"},
    contract_version=text_contract.contract_version,
))
print(registered, result.status)
```

`register_skill_manifest_catalog(registry)` performs discovery and validation
using `registry.repository_root`, rejects conflicts with already registered
Skills, and submits the validated contracts through
`SkillRegistry.register_many(...)`. Both catalog and registry conflicts are
preflighted before the registry is changed; the batch operation also validates
all source files before adding any contract. Registry registration operations
are serialized so a concurrent direct or catalog registration cannot overwrite
an identifier. The registry remains an in-memory single-active-contract store
and does not offer historical contract versions. As with single-manifest registration,
implementations and the `ToolExecutor` are explicitly configured by the
application. After registration, Skills are invoked only through
`SkillPipeline.invoke(...)` or the existing `SkillWorkflowAdapter`; discovery
and registration never execute manifest or source files.

## Skill selection and invocation preparation

```python
from pathlib import Path

from scripts.skill_pipeline import InvocationRequest, SkillPipeline

pipeline = SkillPipeline(Path("."))
discovery = pipeline.discover()
if discovery.issues:
    raise ValueError(discovery.issues)

selection = pipeline.select("implement and verify a software change")
for candidate in selection.candidates:
    print(candidate.skill.identifier, candidate.score, candidate.reasons)
if selection.selected is None:
    raise ValueError(selection.message)

request = InvocationRequest(
    skill_identifier=selection.selected.identifier,
    task="Implement the requested change",
)
plan = pipeline.prepare_invocation(request)
print(plan.status, plan.source_path)
```

Task selection counts distinct lowercase alphanumeric terms shared with a Skill's identifier, name, description, or tags. A unique highest score is selected; no overlap returns `NO_MATCH`, and tied highest scores return `AMBIGUOUS` without selecting one. This lexical matching is not semantic understanding. An explicit `skill_identifier` can be supplied to `select(...)` when the caller has already chosen a Skill.

Invocation preparation validates the selected identifier and input contract,
then returns `PREPARED_NOT_EXECUTED`. New contracts can declare `input_fields`
and `output_fields` as tuples of `SkillField(name, SkillValueType, required,
nullable)`. Supported shallow value types are `STRING`, `INTEGER`, `NUMBER`,
`BOOLEAN`, `OBJECT` (a mapping), and `ARRAY` (a non-string sequence). Booleans
are not accepted as integers or numbers. `strict_inputs` and `strict_outputs`
reject undeclared names; nested object and array contents are not recursively
validated.

Legacy `inputs=("name", ...)` remains an optional-name allowlist: unknown names
are rejected, but listed inputs are not required and have no type validation.
Legacy `outputs=("name", ...)` retains the prior exact-key behavior, requiring
all listed names and rejecting extras. Typed fields express requiredness and
types explicitly; optional typed fields may be omitted. Contracts with no
input declarations and non-strict inputs continue to accept arbitrary input
names. No schema is inferred from Markdown.

`SkillPipeline.invoke(request)` is the request-level composition entry point:
it applies the existing preparation validation and then executes the prepared
plan. Validation errors are raised before execution; execution-time outcomes,
including unavailability, are returned as `SkillExecutionResult`. Use
`prepare_invocation(...)` and `execute(...)` separately when the caller needs
to inspect or retain the plan.

`SkillContract.contract_version` uses canonical numeric `major.minor.patch`
format (for example, `"1.2.0"`). Existing contracts that omit this field resolve
as `"1.0.0"`; the older optional `version` metadata remains separate and does
not select the input/output contract. Callers may omit
`InvocationRequest.contract_version` to use the registered contract, or specify
the exact version. A malformed or unsupported version raises
`InvocationValidationError` before the adapter runs. The resolved version is
recorded on `InvocationPlan` and `SkillExecutionResult`. Callers can inspect
`pipeline.registry.get("text-analysis").contract_version` or resolve an exact
version with `pipeline.registry.resolve("text-analysis", "1.2.0")`.

The current `SkillRegistry` stores one contract per Skill identifier; it does
not retain historical definitions. An explicit request for any version other
than that registered `contract_version` is rejected rather than executed
against the current definition. Input and output validation use that same
resolved contract. A version label therefore identifies the active contract
but does not imply that older versions are available. Local implementations
remain explicitly keyed by Skill identifier; the registry's single active
contract per identifier is the only contract they can execute.

Applications may opt in to a trusted local implementation for selected Skills.
The adapter receives the resolved Markdown source, Skill contract, task, input
mapping, and request ID; it returns a mapping. The pipeline does not interpret
Markdown as code or natural-language instructions or contact a provider. A
local implementation can invoke a tool only through `context.invoke_tool(...)`:
the tool identifier must be listed in the registered Skill's `tools` contract,
and the caller must explicitly configure a `ToolExecutor`. `invoke_tool` returns
the actual structured `ToolExecutionResult` from that executor, including its
status, output, error code, and tool request ID. A tool outcome other than
`SUCCEEDED` makes the final Skill result non-successful even if the adapter
returns output.

The following example shows contract registration, explicit local
implementations and tools, composed invocation, tool-result handling, and
final Skill-result handling:

```python
from pathlib import Path

from scripts.skill_pipeline import (
    InvocationRequest,
    InvocationValidationError,
    LocalSkillExecutionAdapter,
    SkillExecutionStatus,
    SkillPipeline,
)
from scripts.skill_registry import SkillContract, SkillField, SkillValueType
from scripts.tool_framework import (
    ToolExecutor,
    ToolRegistry,
    ToolStatus,
    register_text_statistics,
)

tools = ToolRegistry()
tool_executor = ToolExecutor(tools)
register_text_statistics(tools, tool_executor)

def analyze_text(context):
    tool_result = context.invoke_tool(
        "local.text-statistics", {"text": context.inputs["text"]}
    )
    if tool_result.status is not ToolStatus.SUCCEEDED or tool_result.output is None:
        raise RuntimeError("text statistics tool did not succeed")
    return {"statistics": dict(tool_result.output)}

pipeline = SkillPipeline(
    Path("."),
    execution_adapter=LocalSkillExecutionAdapter({"text-analysis": analyze_text}),
    tool_executor=tool_executor,
)
pipeline.registry.register(SkillContract(
    identifier="text-analysis",
    name="Local text analysis",
    description="Count text characters, words, and lines.",
    source_path=Path("skills/implementation/SKILL.md"),
    contract_version="1.2.0",
    input_fields=(
        SkillField("text", SkillValueType.STRING),
        SkillField("locale", SkillValueType.STRING, required=False, nullable=True),
    ),
    output_fields=(
        SkillField("statistics", SkillValueType.OBJECT),
    ),
    strict_inputs=True,
    strict_outputs=True,
    tools=("local.text-statistics",),
))
try:
    result = pipeline.invoke(InvocationRequest(
        skill_identifier="text-analysis",
        task="count the text",
        inputs={"text": "hello world"},
        contract_version="1.2.0",
    ))
except InvocationValidationError:
    print("Skill invocation rejected before execution")
else:
    if result.status is SkillExecutionStatus.SUCCEEDED:
        print(result.output["statistics"])
    elif result.status is SkillExecutionStatus.UNAVAILABLE:
        print("Execution unavailable:", result.error_code)
    else:
        print(result.status, result.error_code, result.tool_invocations)
    print(result.tool_invocations)
```

The example registers an explicit contract for repository-local Skill content;
it does not imply that the Markdown file itself implements `text-analysis`.
An unlisted tool call is rejected before reaching the `ToolExecutor`, including
when an adapter calls the context's internal invocation callback directly.
A listed tool still follows the tool registry's input validation and adapter
dispatch rules.

`SkillExecutionResult` links the outcome to the invocation request and Skill,
reports `SUCCEEDED`, `FAILED`, or `UNAVAILABLE`, and includes a read-only output
mapping only on success. Failures have stable safe error codes such as
`skill_execution_failed`, `tool_execution_failed`, `invalid_skill_output`,
`missing_skill_output`, and `unexpected_skill_output`; missing execution
support is `UNAVAILABLE` with `execution_unavailable`.
`tool_invocations` contains one safe trace entry for each tool-call attempt:
the parent Skill request ID, tool request ID, tool identifier, actual
`ToolStatus` when the executor was called, and a safe error code. `status=None`
means the attempt was rejected before submission, such as an allowlist denial,
invalid request, or missing executor. The trace contains no inputs, outputs,
exception text, or tracebacks. Error codes are restricted to known
tool-framework codes or safe local attempt codes.

`ToolExecutor` accepts outputs from explicitly registered adapters only when
they are mappings with non-empty string keys. A malformed adapter result
returns `FAILED` with the safe `runtime_failure` code and no output. This
contract-shape validation is not a sandbox and does not validate
application-specific output fields unless the caller adds such validation.
Adapter identifiers must also satisfy the framework's lowercase identifier
format; compatibility-check exceptions return a structured runtime failure
without exposing exception text.
Invalid invocation data is rejected during `prepare_invocation(...)` (also
called by `invoke(...)`) with `InvocationValidationError`; it is not
represented as an execution result because execution has not begun.

The legacy `SkillContract.outputs` name tuple, when used without typed output
fields, must exactly match the returned output names; it does not validate
output value types. Typed output fields validate their declared shallow value
types. Tool failures cannot be converted to final Skill success, even if an
adapter ignores the returned tool status or catches an allowlist/request error.
If a later call fails, earlier calls remain in the result trace; their side
effects are not rolled back and calls are not retried. The adapter is trusted
in-process code supplied by the application; this boundary does not provide
timeouts, cancellation, isolation, provider/model execution, or an execution
sandbox. `WorkflowEngine` accepts workflow steps that target registered Tools;
it has no native Skill step contract. A caller can compose a Skill through an
explicitly registered local Tool implementation that maps its declared inputs
to `SkillPipeline.invoke(...)` and maps the structured result to that Tool's
output contract. The built-in `SkillWorkflowAdapter` for this composition is
documented below; no production caller currently uses it. Workflow cancellation does not control an in-progress
synchronous Skill or tool callable.

## Skill execution in a Tool workflow

`scripts/skill_workflow.py` provides `SkillWorkflowAdapter`, a Tool adapter
bound to one explicitly selected Skill. Configure its `SkillPipeline`, fixed
Skill identifier, task source, and Skill-input-to-Tool-input mapping. Register
the adapter with the existing `ToolExecutor` and register a matching
`ToolContract` with its `ToolRegistry`. The adapter delegates execution to
`SkillPipeline.invoke(...)`; it does not implement another Skill execution
path.

The adapter returns a Tool output envelope with `skill_status`,
`skill_request_id`, `skill_identifier`, `skill_contract_version`,
`skill_error_code`, `skill_output`, and `tool_invocations`. Configure
`contract_version` on the adapter to pin the invocation; if omitted, the
canonical pipeline resolves the sole registered version. Because Tool adapters report successful protocol execution
by returning a mapping, the workflow step can be `SUCCEEDED` even when the
embedded Skill result is `FAILED` or `UNAVAILABLE`. This is not represented as
a Tool failure: callers must inspect `skill_status` and must not treat the
workflow's Tool-protocol success alone as Skill success. Pre-execution
`InvocationValidationError` is instead raised through the Tool adapter and
becomes a Tool/workflow invocation failure.

This example uses one explicit Tool registry/executor for both the Skill's
allowlisted local text tool and the Skill integration Tool:

```python
from pathlib import Path

from scripts.skill_pipeline import (
    InvocationRequest,
    InvocationValidationError,
    LocalSkillExecutionAdapter,
    SkillExecutionStatus,
    SkillPipeline,
)
from scripts.skill_manifest import register_skill_manifest
from scripts.skill_workflow import SkillWorkflowAdapter
from scripts.tool_framework import (
    ExecutionAvailability,
    InputField,
    InputType,
    ToolContract,
    ToolExecutor,
    ToolRegistry,
    register_text_statistics,
)
from scripts.tool_workflow import (
    StepStatus,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowInputRef,
    WorkflowRegistry,
    WorkflowStep,
)

tools = ToolRegistry()
executor = ToolExecutor(tools)
register_text_statistics(tools, executor)

def analyze_text(context):
    outcome = context.invoke_tool(
        "local.text-statistics", {"text": context.inputs["text"]}
    )
    if outcome.output is None:
        return {}
    return {"statistics": dict(outcome.output)}

pipeline = SkillPipeline(
    Path(".").resolve(),
    execution_adapter=LocalSkillExecutionAdapter({"text-analysis": analyze_text}),
    tool_executor=executor,
)
contract = register_skill_manifest(
    pipeline.registry,
    Path("skills/text-analysis.manifest.json"),
)

try:
    direct_result = pipeline.invoke(InvocationRequest(
        skill_identifier=contract.identifier,
        task="count this text",
        inputs={"text": "hello world"},
        contract_version=contract.contract_version,
    ))
except InvocationValidationError as error:
    print("Skill invocation rejected before execution:", error)
else:
    if direct_result.status is SkillExecutionStatus.SUCCEEDED:
        print(direct_result.output["statistics"])
    else:
        print(
            direct_result.status.value,
            direct_result.error_code,
            direct_result.tool_invocations,
        )

skill_adapter = SkillWorkflowAdapter(
    "skill.text-analysis",
    "skill.invoke.text-analysis",
    pipeline,
    contract.identifier,
    task_input="task",
    input_mapping={"text": "text"},
    contract_version=contract.contract_version,
)
tools.register(ToolContract(
    identifier="skill.invoke.text-analysis",
    name="Invoke text-analysis Skill",
    description="Run the explicitly configured text-analysis Skill.",
    input_schema=(
        InputField("task", InputType.STRING),
        InputField("text", InputType.STRING),
    ),
    adapter_id=skill_adapter.adapter_id,
    execution_availability=ExecutionAvailability.AVAILABLE,
))
executor.register_adapter(skill_adapter)

workflows = WorkflowRegistry()
workflows.register(WorkflowDefinition(
    "workflow.skill-text-analysis",
    "Skill text analysis",
    (
        WorkflowStep(
            "analyze",
            "skill.invoke.text-analysis",
            {
                "task": WorkflowInputRef("task"),
                "text": WorkflowInputRef("text"),
            },
        ),
    ),
))
engine = WorkflowEngine(workflows, tools, executor)
workflow_result = engine.execute(
    "workflow.skill-text-analysis",
    {"task": "count this text", "text": "hello world"},
    include_outputs=True,
)

step = workflow_result.step_result("analyze")
if step is None or step.status is not StepStatus.SUCCEEDED:
    print("Workflow Tool protocol failed:", workflow_result.status)
elif step.tool_result is None or step.tool_result.output is None:
    print("Skill outcome was not included in workflow outputs")
else:
    skill_status = SkillExecutionStatus(step.tool_result.output["skill_status"])
    if skill_status is SkillExecutionStatus.SUCCEEDED:
        print(step.tool_result.output["skill_output"])
    else:
        print(
            "Skill did not succeed:",
            skill_status.value,
            step.tool_result.output["skill_error_code"],
            step.tool_result.output["tool_invocations"],
        )
```

The workflow engine's default result omits Tool outputs; `include_outputs=True`
is required here to inspect the Skill outcome from the returned step result.
The bridge fixes the target Skill in application configuration; workflow inputs
provide only the configured task and Skill input values and cannot select a
different Skill or implementation. Skill Markdown remains inert. Skill tool
calls still pass through the configured `ToolExecutor` and the Skill contract's
tool allowlist. Earlier tool side effects are not rolled back and are not
retried. Workflow cancellation cannot interrupt an in-progress synchronous
Skill or tool callable.

## Tool contracts and local adapters

The input schema supports only `string`, `integer`, `boolean`, and `string_list`. Registered tool contracts are inert; execution requires an explicitly registered adapter object and an enabled contract marked `AVAILABLE`.

Run this self-contained example from the repository root:

```sh
python3 - <<'PY'
from scripts.tool_framework import (
    ExecutionAvailability,
    InputField,
    InputType,
    LocalToolAdapter,
    ToolContract,
    ToolExecutor,
    ToolInvocationRequest,
    ToolRegistry,
    ToolStatus,
    text_statistics,
)

registry = ToolRegistry()
registry.register(ToolContract(
    identifier="local.text-statistics",
    name="Text statistics",
    description="Count characters, words, and lines.",
    input_schema=(InputField("text", InputType.STRING),),
    adapter_id="local.text",
    execution_availability=ExecutionAvailability.AVAILABLE,
))

executor = ToolExecutor(registry)
executor.register_adapter(LocalToolAdapter(
    "local.text",
    {"local.text-statistics": text_statistics},
))
result = executor.invoke(ToolInvocationRequest(
    "local.text-statistics",
    {"text": "hello world"},
))
if result.status is ToolStatus.SUCCEEDED:
    print(dict(result.output))
else:
    print(result.status.value, result.error_code, result.error)
PY
```

Adapters are trusted in-process objects supplied directly by the application; adapter identifiers in tool metadata never trigger dynamic imports. The built-in text-statistics implementation is local, deterministic, read-only, and requires no credentials or network. No external provider adapter or general-purpose execution sandbox is included. Run framework and repository tests with `python3 -m unittest discover -s tests -v`.

## Tool capability discovery and selection

`scripts/tool_discovery.py` inspects registered P076 `ToolContract` values. Discovery applies exact filters for identifiers, adapter, required capabilities, declared input names, and tool state. Preferred capabilities do not exclude discovery results; they order results by descending number of preferences present, then identifier.

Matching treats required capabilities, adapter, allowed tool identifiers, declared input names, and state policy as hard constraints. A missing hard constraint is `NO_MATCH`. A candidate satisfying hard constraints is `EXACT_MATCH` when all specified preferences are present (including when no preferences were specified), otherwise it is `PARTIAL_MATCH`. The score is the count of matched preferences, not a confidence estimate; it may be nonzero for a `NO_MATCH`, which can never qualify for selection. The default minimum permits partial matches, so preferences rank eligible matches but never compensate for a failed hard requirement; `MinimumMatchQuality.EXACT` can require all preferences. Equal highest qualifying scores produce `AMBIGUOUS` and no selected identifier. Required tool identifiers are alternatives (the candidate must match one when the list is non-empty); required input names assert only that names are declared by the contract.

Disabled and execution-unavailable contracts are excluded by default. The corresponding `include_disabled` and `include_unavailable` flags make them discoverable/selectable, but a `ToolMatch` still marks `contract_execution_state_available=False` and reports state reason codes. That field reflects only the contract's enabled and availability flags: discovery does not inspect executor adapter registration, so it does not guarantee invocation will succeed.

This runnable example uses only the standard library and the existing local implementation. It discovers the registered contract, prints its match evidence, then creates a selection plan; it does not invoke the tool:

```sh
python3 - <<'PY'
from scripts.tool_discovery import (
    SelectionStatus,
    ToolRequirements,
    discover_tools,
    plan_tool_selection,
)
from scripts.tool_framework import ToolExecutor, ToolRegistry, register_text_statistics

registry = ToolRegistry()
executor = ToolExecutor(registry)
register_text_statistics(registry, executor)

discovery = discover_tools(registry)
print([tool.identifier for tool in discovery.tools])

plan = plan_tool_selection(
    registry,
    ToolRequirements(
        required_capabilities=("text-analysis",),
        preferred_capabilities=("deterministic",),
        required_tool_identifiers=("local.text-statistics",),
        required_input_names=("text",),
    ),
)
for candidate in plan.candidates:
    print(candidate.tool_identifier, candidate.classification.value,
          candidate.score, candidate.reason_codes, candidate.explanation)
if plan.status is SelectionStatus.SELECTED:
    print("Selected for explicit caller handoff:", plan.selected_tool_identifier)
elif plan.status is SelectionStatus.AMBIGUOUS:
    print("Choose explicitly among tied candidates.")
else:
    print("No qualifying selection:", plan.status.value)
PY
```

Discovery returns metadata; matching explains one contract; selection chooses only a unique highest-scoring qualifying candidate; invocation remains a separate caller action through the P076 `ToolExecutor.invoke(...)` API. `discovery_only=True` returns candidate matches with `DISCOVERY_ONLY` status and no selected identifier. Neither discovery nor selection calls adapters or implementations, and a selection plan is not an execution result. Run focused and full tests from the repository root with:

```sh
python3 -m unittest discover -s tests -p "test_tool_discovery.py" -v
python3 -m unittest discover -s tests -v
```

## Sequential Tool workflows

`scripts/tool_workflow.py` composes registered P076 Tools through `ToolExecutor`. A `WorkflowDefinition` contains ordered `WorkflowStep`s; `WorkflowRegistry` stores definitions without executing them. A step maps each target Tool input to a JSON-compatible literal, `WorkflowInputRef("name")`, or a top-level `StepOutputRef("prior_step", "field")`. References are explicit typed objects, never parsed from arbitrary strings. Step-output references must name earlier steps. Explicit and reference-derived dependencies are checked for unknown IDs, self-reference, cycles, and declared order.

`validate_workflow(definition)` returns a typed `WorkflowValidationResult`: `valid`, deterministic `issues` with stable codes/categories and relevant step/dependency IDs, the normalized dependency graph, and the original declared step order. The graph includes both explicit `depends_on` entries and `StepOutputRef`s. Validation checks structure, non-empty and unique step identifiers, dependency identifier/reference validity, unknown and self-dependencies, cycles, and dependencies that point forward in the declared order. Cycle detection uses an iterative strongly-connected-component walk, so long dependency chains do not rely on Python recursion. Dependencies validate ordering; they never cause the engine to reorder or parallelize steps.

```python
from scripts.tool_workflow import (
    WorkflowDefinition,
    WorkflowStep,
    validate_workflow,
)

workflow = WorkflowDefinition(
    "workflow.valid",
    "Valid workflow",
    (
        WorkflowStep("prepare", "local.text-statistics", {}),
        WorkflowStep(
            "summarize",
            "local.text-statistics",
            {},
            depends_on=("prepare",),
        ),
    ),
)
validation = validate_workflow(workflow)
if not validation.valid:
    for issue in validation.issues:
        print(issue.error_code, issue.category.value, issue.step_id, issue.dependency_id)
else:
    print(validation.declared_step_order, dict(validation.dependency_graph))
```

Normal construction rejects empty or structurally invalid definitions with `InvalidWorkflowDefinitionError`; duplicate IDs, unknown/self references, cycles, and forward dependencies are rejected before registry insertion. The registry validates again at registration. `WorkflowEngine.preflight(...)` and `execute(...)` repeat definition validation as a safety gate. If a registered definition is found inconsistent, preflight reports `validation_issues`, execution returns `PREFLIGHT_FAILED`, a `workflow_validation_failed` lifecycle code is recorded, and no executor is invoked. Validation messages contain identifiers and stable reasons only, never input payloads.

For example, a forward reference is rejected at definition time:

```python
from scripts.tool_workflow import (
    InvalidWorkflowDefinitionError,
    WorkflowDefinition,
    WorkflowStep,
)

try:
    WorkflowDefinition(
        "workflow.invalid",
        "Invalid workflow",
        (
            WorkflowStep("first", "local.text-statistics", {}, depends_on=("later",)),
            WorkflowStep("later", "local.text-statistics", {}),
        ),
    )
except InvalidWorkflowDefinitionError as error:
    print(error)
```

`WorkflowEngine` requires the same `ToolRegistry` instance as the supplied `ToolExecutor`, which it checks at construction. After definition validation, `WorkflowEngine.preflight(...)` resolves all statically checkable tool and input issues before any invocation. It verifies tool registration, required/mapped input names, literal and supplied workflow-input types, and disabled/unavailable contract status. P076 has no declared output schema, so step-output field existence and type compatibility are checked at runtime when the referenced successful output is available. Adapter registration/compatibility is also checked by P076 at invocation time, not preflight; a missing adapter is a structured Tool failure. A missing reference yields a structured resolution failure; a failed or skipped step never contributes output.

Typed input contract violations raise `InvocationValidationError` before the
adapter or any Skill tools run. Typed output contract violations happen after
the adapter returns, preserve the tool-attempt history, and return `FAILED`
with `invalid_skill_output`, `missing_skill_output`, or
`unexpected_skill_output`. Through `SkillWorkflowAdapter`, input-validation
errors become ordinary Tool/workflow invocation failures; output-contract
failures remain the embedded `skill_status="failed"` and
`skill_error_code` in the adapter envelope. As with other execution-time Skill
outcomes, the workflow Tool protocol can succeed, so callers inspect that
embedded status.

The default `STOP_ON_FAILURE` policy skips all later independent steps after the first failure. `CONTINUE_INDEPENDENT` skips steps that depend directly or transitively on unsuccessful steps and continues independent steps in declared order. Preflight failures invoke no tools. Tool failures and input-resolution failures remain distinct in step results. Sequential execution is **not atomic**: effects from successful earlier steps are not rolled back if a later step fails.

### Workflow result and failure semantics

`WorkflowResult.status` is authoritative: `SUCCEEDED` means all steps succeeded, `FAILED` means execution failed without any successful step, `PARTIAL` means execution had both successful and failed steps, `PREFLIGHT_FAILED` means no tool was invoked, and `CANCELLED` means cancellation was observed without an earlier ordinary step failure taking precedence. The `success` property is true only for `SUCCEEDED`. A completed execution includes a result for each declared step; each is `SUCCEEDED`, a failure (`TOOL_FAILED`, `INPUT_RESOLUTION_FAILED`, or `INVOCATION_ERROR`), a skip (`SKIPPED_DEPENDENCY` or `SKIPPED_POLICY`), or `CANCELLED`. Counts distinguish cancelled steps from failures and skips. `execution_completed` means the engine finished scheduling the workflow, including a workflow that finished with failures or cancellation; it is false for preflight rejection.

Failure details use stable `error_code` values and `FailureCategory` values. Definition validation uses `WORKFLOW_VALIDATION`; other preflight rejection uses `PREFLIGHT`; unexpected engine failures use `WORKFLOW_RUNTIME`; tool invocation and returned tool failures use `TOOL_INVOCATION`; dependency and policy skips use `DEPENDENCY` and `FAILURE_POLICY`. Validation/preflight failures have `PREFLIGHT_FAILED` status and invoke zero tools, while runtime tool failures appear on their step results. Executor exceptions, malformed results, mismatched result identifiers, and non-JSON-compatible outputs are normalized to safe codes such as `tool_execution_exception`, `malformed_tool_result`, and `invalid_tool_output`. Raw exception messages and structured Tool error objects are excluded from workflow results, events, and snapshots.

Every normally finalized run has one terminal event, and the retained snapshot copies the final result status and ordered events. In-memory snapshot retention is optional to the execution outcome: if retention raises an ordinary exception, `WorkflowResult.observability_issues` reports `snapshot_retention_failed`, the sanitized exception type, and whether a snapshot was retained, without changing the business status. Workflow events have no external callback or persistence hooks; the separate progress tracker supports synchronous subscribers as described below.

### Workflow cancellation and synchronous calls

Pass a `WorkflowCancellationToken` to `WorkflowEngine.execute(...)`. Call
`request_cancel()` to request cancellation; it returns `True` only for the
first request and `False` for repeated requests or after the run has
terminalized. The token is safe to request/read from multiple threads and is
single-use; reusing it for another execution is rejected. It cannot be reset.
Validation and preflight still
run first. `execution_began` indicates that the post-preflight execution phase
was entered; it can be true for a pre-cancelled run even when no tool was
invoked. Cancellation is checked after successful preflight, immediately
before each tool invocation, between steps, and when selecting the terminal
outcome. A lock makes the final decision deterministic: if cancellation wins
the race before terminalization, it is observed; after terminalization, a
request is rejected and cannot change the result or events.

The engine does not forcibly stop a running synchronous tool. If an executor
holds a reference to the run's token, it may poll it and return, or
cooperatively raise `WorkflowCancellationRequested`. If it requests
cancellation while returning a normal result, that step retains its actual
success or failure outcome and pending steps are cancelled at the next
checkpoint. A cooperative cancellation exception marks the active step
`CANCELLED`. Steps not invoked after cancellation also have `CANCELLED` status;
their count is reported separately as `cancelled_step_count`. Under
`CONTINUE_INDEPENDENT`, cancellation prevents all further steps, including
independent ones. Under `STOP_ON_FAILURE`, an earlier ordinary failure remains
primary and later steps remain `SKIPPED_POLICY`; cancellation does not erase
that failure. A failed run with some successful work remains `PARTIAL`.

For example, append this to the runnable setup above to verify that a
pre-cancelled request still performs validation/preflight but does not invoke
the tools:

```python
from scripts.tool_workflow import WorkflowCancellationToken

token = WorkflowCancellationToken()
assert token.request_cancel()
cancelled = engine.execute(
    "local.text-summary",
    {"message": "not invoked"},
    cancellation_token=token,
)
assert cancelled.status is WorkflowStatus.CANCELLED
assert cancelled.cancelled_step_count == 2
assert cancelled.successful_step_count == 0
assert cancelled.events[-1].event_type.value == "workflow_cancelled"
```

Cooperative cancellation does not provide asynchronous execution, distributed
cancellation, thread termination, or cleanup after process-level termination.
Ordinary snapshot-retention exceptions are reported separately from execution
status; `KeyboardInterrupt`, `SystemExit`, and other `BaseException` signals
are not converted into workflow failures. If such a process-level signal or
an internal event-construction failure interrupts finalization, no terminal
event or snapshot is guaranteed.

The default trace includes input names/source/type metadata, output field/type metadata, and structured P076 invocation status, but not resolved input values or successful raw output values. Raw successful outputs are retained only in-process during a run for reference resolution. Set `include_outputs=True` only when the returned report is allowed to disclose tool outputs. P076 sanitizes local implementation exception messages in its structured failure result.

Run this two-step example from the repository root. The first tool counts a caller-supplied message; the second consumes the `characters` output using another explicitly registered local implementation. Preflight does not invoke either implementation; `execute` uses the existing P076 executor:

```sh
python3 - <<'PY'
from scripts.tool_framework import (
    ExecutionAvailability,
    InputField,
    InputType,
    LocalToolAdapter,
    ToolContract,
    ToolExecutor,
    ToolRegistry,
    register_text_statistics,
)
from scripts.tool_workflow import (
    StepOutputRef,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowInputRef,
    WorkflowRegistry,
    WorkflowStatus,
    WorkflowStep,
)

tools = ToolRegistry()
executor = ToolExecutor(tools)
register_text_statistics(tools, executor)

tools.register(ToolContract(
    identifier="local.describe-count",
    name="Describe character count",
    description="Format a character count as a short summary.",
    input_schema=(InputField("count", InputType.INTEGER),),
    adapter_id="local.summary",
    execution_availability=ExecutionAvailability.AVAILABLE,
))
executor.register_adapter(LocalToolAdapter(
    "local.summary",
    {
        "local.describe-count": lambda inputs: {
            "summary": f"{inputs['count']} characters"
        }
    },
))

workflows = WorkflowRegistry()
workflows.register(WorkflowDefinition(
    identifier="local.text-summary",
    name="Text summary",
    steps=(
        WorkflowStep(
            "count",
            "local.text-statistics",
            {"text": WorkflowInputRef("message")},
        ),
        WorkflowStep(
            "describe",
            "local.describe-count",
            {"count": StepOutputRef("count", "characters")},
        ),
    ),
))

engine = WorkflowEngine(workflows, tools, executor)
preflight = engine.preflight("local.text-summary", {"message": "hello world"})
print("preflight:", preflight.valid, [issue.error_code for issue in preflight.issues])
if not preflight.valid:
    raise ValueError(preflight.issues)
result = engine.execute(
    "local.text-summary",
    {"message": "hello world"},
    include_outputs=True,
)
print("workflow:", result.status.value, "steps:", result.successful_step_count)
print("success:", result.success, "failure:", result.error_code)
for step in result.step_results:
    print("step:", step.step_id, step.status.value, step.error_code)
if result.status is not WorkflowStatus.SUCCEEDED:
    raise RuntimeError(result.summary)
final_step = result.step_result("describe")
if final_step is None:
    raise RuntimeError("workflow result did not include the describe step")
final_tool_result = final_step.tool_result
if final_tool_result is None or final_tool_result.output is None:
    raise RuntimeError("successful final step did not return an included output")
print("summary:", dict(final_tool_result.output))
snapshot = engine.inspect_run(result.run_id)
print(
    "run events:",
    [(event.sequence_number, event.event_type.value) for event in snapshot.events],
)
print(
    "step counts:",
    {status.value: count for status, count in snapshot.step_counts.items()},
)
PY
```

### Workflow execution events and run inspection

Each `WorkflowEngine.execute(...)` call returns its generated `run_id` and an
ordered immutable `events` tuple on `WorkflowResult`. Events contain the event
type, workflow and run identifiers, one-based sequence number, monotonic
elapsed seconds, and (for step events) the step identifier, status, and stable
error code when applicable. A run records `workflow_run_started`, then
`preflight_completed`, followed by each actually started or skipped step in
execution order, and one terminal workflow event. Every started step has one
success or failure event; skipped steps have only a skip event. The terminal
event follows all step events. Preflight failures have no step events and
record no tool invocation. `CONTINUE_INDEPENDENT` produces a
`workflow_completed_with_partial_failures` terminal event when applicable.

Events and snapshots never contain workflow input values, resolved input
mappings, or raw tool outputs. Failures are represented by stable error codes,
not exception messages. Existing `include_outputs=True` behavior can still
include tool outputs in the returned `WorkflowResult`, but it does not expand
event or snapshot payloads.

`engine.inspect_run(run_id)` returns an immutable `WorkflowRunSnapshot` with
the overall status, elapsed time, ordered step status summaries, counts keyed
by `StepStatus`, events, and safe failure/reason codes. The engine retains the
most recent 100 completed run snapshots by default; pass a positive
`max_retained_runs` to `WorkflowEngine` to change this bound. Snapshots are
evicted oldest-first. `EvictedWorkflowRunError` identifies recently evicted
IDs (up to the configured bound); IDs older than that bounded eviction history
are reported as `UnknownWorkflowRunError`. No event or snapshot store is
persisted or exported. Empty workflows remain invalid under the existing P078
contract. This is in-memory, sequential workflow observability only; it adds no
external telemetry, persistence, or execution/retry behavior.

Execution progress is available as an immutable `WorkflowProgressSnapshot`.
Pass a fresh `WorkflowProgressTracker` to `execute(...)` to read snapshots
during synchronous execution; the returned `WorkflowResult.progress` and
retained `WorkflowRunSnapshot.progress` contain the final snapshot:

```python
from scripts.tool_workflow import WorkflowProgressTracker

progress = WorkflowProgressTracker()
result = engine.execute("local.text-summary", {"message": "hello"},
                        progress_tracker=progress)
assert progress.progress is result.progress
assert result.progress.terminal
```

The progress snapshot includes UTC start/finish timestamps, the current step
while it is running, planned and terminal step counts, and ordered per-step
states (`PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED`, `SKIPPED`, or
`CANCELLED`). `completed_step_count` counts all terminal step outcomes,
including failures, skips, and cancellations. During preflight, workflow status
is `RUNNING` while `execution_started` is false; a rejected preflight ends with
`PREFLIGHT_FAILED` and leaves planned steps pending. Progress contains only
safe status/error-code metadata, not exception messages, tool errors, inputs,
or outputs. A tracker is single-use and can be read safely from another thread;
execution itself remains sequential and synchronous.

Register a callback with `subscribe(...)`; it receives each subsequent
progress snapshot change, not the current snapshot at subscription time.
`subscribe` returns an unsubscribe function:

```python
progress = WorkflowProgressTracker()
unsubscribe = progress.subscribe(lambda snapshot: print(snapshot.status.value))
result = engine.execute("local.text-summary", {"message": "hello"},
                        progress_tracker=progress)
unsubscribe()
```

Callbacks run synchronously, in subscription order, after the tracker has
published the immutable snapshot and without holding its state lock. An
unsubscribe call is idempotent. From another thread it waits for a callback
already in progress to finish, then prevents later dispatches; when called
from that callback itself, it takes effect immediately for later dispatches
without waiting on itself. A currently executing callback is never interrupted.
At terminal notification, the tracker dispatches the final snapshot and then
unsubscribes all remaining listeners and releases their callback references.
The final `progress` snapshot remains available, but subscribing to a finalized
tracker raises `RuntimeError`. A tracker and its subscriptions belong to one
execution only.

A callback that raises an ordinary `Exception` does not affect workflow
execution or other subscribers; the tracker records only its subscription ID
and exception type in `notification_issues`, never the exception message.
The listener remains subscribed unless it unsubscribes or the tracker
finalizes. `BaseException` process-control signals are not suppressed. Slow
callbacks therefore delay the workflow at that progress transition; callbacks
do not run in a background worker.

Read `tracker.notification_diagnostics` at any time for an immutable,
thread-safe notification-health snapshot. Completed runs also expose this
same snapshot as `WorkflowResult.notification_diagnostics` and
`WorkflowRunSnapshot.notification_diagnostics` through `engine.inspect_run`.
The run-level copies are captured after terminal notification and subscriber
cleanup. `dispatch_attempt_count` counts
callbacks actually entered; `successful_delivery_count` counts callbacks that
returned normally; and `callback_failure_count` counts ordinary callback
exceptions. Attempts include callbacks that later fail, while inactive
subscriptions are not counted. `issue_counts` contains the stable
`subscriber_callback_failed` code and its count, including zero when no
callback has failed. `active_subscriber_count` counts registrations not yet
unsubscribed; it can remain nonzero during terminal callback dispatch even
though no later progress notification will occur. `finalized` becomes true
when the terminal progress snapshot is published;
`cleanup_completed` becomes true after terminal listener cleanup and callback
reference release finish. During terminal callback dispatch it is possible for
`finalized` to be true while `cleanup_completed` is false. The final progress
snapshot remains available after cleanup. These counters and diagnostics are
in-memory only; they do not represent durable delivery guarantees.

The focused workflow tests and complete suite are run with:

```sh
python3 -m unittest discover -s tests -p "test_tool_workflow.py" -v
python3 -m unittest discover -s tests -v
```

## Safety guidance

- Preserve pre-existing user changes.
- Avoid cleanup beyond the task scope.
- Do not claim verification without execution evidence.
- Stop when required approval or repository context is missing.

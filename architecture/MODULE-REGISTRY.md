# Module Registry

## 1. Purpose and Status

The Module Registry is the proposed canonical inventory and description mechanism for the SUPER AGI target architecture. It is intended to provide a stable, discoverable, evidence-aware way to identify and classify the modules that make up the one-Super-AGI system while preserving the distinction between a planned module, a defined module, a module implementation, and an operationally deployed module.

This document is subordinate to [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md), which defines the authoritative architecture hierarchy. It is consistent with [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md), [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md), [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md), [`FIVE-PLANES.md`](FIVE-PLANES.md), and [`MASTER-CORE.md`](MASTER-CORE.md).

This document defines architecture intent only. It does not establish an operational registry service, a production registry database, a mandatory module list, or a deployed module portfolio.

The repository establishes the following baseline facts:

- One Super AGI is intended as a single unified system.
- That system is organized around 100 Major AGI Intelligence Modules and 100 Dedicated Navbars/Workspaces.
- Shared universal infrastructure supports that system without turning modules into independent products.
- The module registry is a planned concept, not an existing implementation.

The following distinctions are used in this document:

- **Established** — explicitly supported by the repository's governing architecture documents.
- **Evidence-grounded proposal** — supported by repository concepts or proposals, but not approved as implementation.
- **Proposed** — useful architectural intent without a binding repository record.
- **Unresolved** — the design or authority remains open.
- **Not implemented** — no operational registry or registry data is present.

The registry is therefore **proposed** and **not implemented**. The repository currently contains no authoritative 100-module portfolio and no evidence that any operational registry service exists.

## 2. Registry Design Principles

The Module Registry should follow the repository's canonical design principles:

1. **One canonical module identity** — each module should have one stable identifier and a clear relationship to its definition, implementation, and workspace.
2. **One unified system** — the registry supports a single system architecture instead of 100 independent AI products.
3. **Metadata separate from implementation** — the registry names and describes modules; it does not create execution behavior by itself.
4. **Explicit evidence and status** — every module entry should provide capability status, lifecycle state, and evidence references without implying operational readiness.
5. **Versionable and extensible definitions** — module definitions can evolve without destroying identity or compatibility assumptions.
6. **Clear dependency boundaries** — dependencies must be declared and distinguished from working integrations.
7. **Provider neutrality** — module identity and responsibility should remain provider-neutral; provider-specific adapters are separate concerns.
8. **Governed lifecycle** — new modules, changes, deprecations, and retirements should be explicit and traceable.
9. **Compatibility discipline** — compatibility is a status and contract question, not a claim that a module is operational.
10. **No fabricated operational readiness** — a registry entry is not a deployment claim.

These principles are consistent with the repository's architecture and governance documents. They are not evidence of an operational registry implementation.

## 3. Module Identity

A module identity model should provide a stable, machine-friendly identity for each module while keeping the registry distinct from its actual implementation or workspace.

### Proposed identity fields

| Field | Purpose | Status |
|---|---|---|
| `module_id` | Stable identifier for the module within one authoritative registry | Required, proposed |
| `module_name` | Human-readable name | Required, proposed |
| `summary` | Short description of the module's purpose | Required, proposed |
| `domain` | Intelligence domain or domain family | Required or optional, proposed |
| `subdomain` | More precise classification within a domain | Optional, proposed |
| `workspace_ref` | Reference to the associated workspace or navigation surface | Proposed, unresolved |
| `definition_version` | Version of the module definition | Optional, proposed |
| `registry_version` | Version of the registry record | Optional, proposed |
| `lifecycle_status` | Proposed lifecycle state | Proposed, unresolved |
| `capability_status` | Canonical capability status such as `IMPLEMENTED` or `NOT IMPLEMENTED` | Required if the registry records status |
| `owner` | Maintainer or responsible authority | Optional, unresolved |
| `documentation_refs` | Links to architecture, product, and workflow references | Optional, proposed |
| `implementation_refs` | Links to implementation artifacts, if any | Optional, proposed |
| `evidence_refs` | References to implementation, verification, or evaluation evidence | Required for evidence-bearing status |
| `created_at` / `updated_at` | Traceability metadata | Optional, proposed |
| `deprecated_at` / `retired_at` | Deprecation lifecycle metadata | Optional, proposed |

The registry should not invent owners, approval authorities, release numbers, or implementation evidence where the repository lacks evidence.

### Identity rules

- The identifier must be stable and unique within the registry.
- The identifier should be machine-friendly and not depend on a vendor or provider-specific naming scheme.
- The registry should preserve human-readable names and canonical domain labels without collapsing them into implementation details.
- Module identity must remain distinct from:
  - a module contract;
  - a workspace or navigation surface;
  - a provider adapter;
  - a tool integration;
  - a Skill or agent role;
  - a deployed runtime instance.

## 4. Module Classification

The registry should classify modules by their architectural role without forcing a module into an artificially narrow category. The current architecture establishes the five planes and L0–L15 layers, but it does not establish a definitive one-to-one mapping between a module and a plane or a layer.

### Proposed classification dimensions

- **Intelligence domain** — the major functional domain the module serves.
- **Functional responsibility** — the module's core task and output expectations.
- **Workspace relationship** — how the module relates to the dedicated module workspace or navigation boundary.
- **Shared infrastructure dependency** — whether the module depends on shared memory, context, knowledge, model gateway, security, or observability contracts.
- **Architectural plane alignment** — how the module probably interacts with Intelligence, Knowledge, Agent, Domain, and Control responsibilities.
- **Capability and lifecycle status** — what is implemented, planned, blocked, or unresolved.

A module may legitimately span more than one plane. The registry should therefore favor explicit classification metadata rather than a forced single-plane assignment.

No definitive plane-to-layer mapping is approved by the repository at the time of this document. The registry should therefore record cross-plane responsibilities carefully, with unresolved mappings labeled as such.

## 5. Registry Entry Contract

The registry entry is the conceptual record describing a module. The entry should separate identity, responsibility, state, dependencies, and evidence. A finalized machine-readable schema is not established by the repository, so this section describes the intended contract in conceptual terms rather than as an approved schema.

### Required conceptual categories

| Category | Description | Status |
|---|---|---|
| Identity | Stable module identity and naming | Proposed |
| Classification | Domain, workspace, plane, and shared infrastructure metadata | Proposed |
| Responsibilities | Primary responsibilities and explicit non-responsibilities | Proposed |
| Contracts | References to module contract and related interfaces | Proposed, unresolved |
| Dependencies | Required, optional, and shared infrastructure dependencies | Proposed |
| Capabilities | Declared capabilities and relevant support boundaries | Proposed |
| Evidence | Links to authoritative design, implementation, validation, and approval references | Proposed |
| Lifecycle | Proposed lifecycle and deprecation state | Proposed |
| Security | Permissions, trust, and approval dependency metadata | Proposed |
| Observability | Trace, audit, and evidence references | Proposed |
| Compatibility | Version and compatibility constraints | Proposed, unresolved |

### Proposed entry fields by category

- **Identity and descriptive metadata**
  - module ID
  - name
  - summary
  - domain and subdomain
  - version and update metadata
  - workspace reference
- **Responsibility metadata**
  - intended responsibilities
  - explicit non-responsibilities
  - primary inputs and outputs
  - relevant interfaces
- **Capability metadata**
  - capability declarations
  - skill references
  - agent references
  - tool and provider dependencies
  - memory, knowledge, and context dependencies
- **Dependency metadata**
  - required dependencies
  - optional dependencies
  - related modules
  - compatibility constraints
  - knowledge or workflow dependencies
- **Lifecycle and status metadata**
  - lifecycle state
  - capability status
  - evidence status
  - approval state, only if documented and valid
- **Governance metadata**
  - change log or update references
  - deprecation or retirement metadata
  - security and permission notes
  - unresolved decisions

The repository does not establish a final registry schema or a mandatory machine-readable file format. This contract is therefore a design target, not an approved implementation contract.

## 6. Relationship to the Module Contract

The repository distinguishes between the module registry, the future module contract, the module implementation, and the workspace.

- **Module Registry**: identifies and describes the module in a canonical, index-like form.
- **Module Contract**: defines the expected interfaces, responsibilities, failure behavior, inputs, outputs, dependencies, and evidence expectations for a module in relationship to the wider system.
- **Module implementation**: the actual code, configuration, or runtime behavior that realizes the defined module.
- **Workspace**: the dedicated module-oriented user or operator surface that provides navigation, context, or interaction for that module.

These concepts must remain distinct. A registry entry may exist before a contract is finalized, and a module may be specified before implementation begins. A contract is also distinct from an approved or deployed runtime.

The repository does not yet contain an approved `architecture/MODULE-CONTRACT.md`. If that file does not exist, it should be treated as a planned dependent specification rather than as an existing authoritative contract.

## 7. Relationship to the Master Core and Universal Infrastructure

The registry is intended to support the proposed Master Core and the broader shared infrastructure concept without becoming a source of operational authority.

### Master Core interaction

The Master Core would likely use the registry to:

- discover module identity and classification;
- route tasks to appropriate modules;
- check required capabilities and dependencies;
- identify explicit cross-module relationships;
- preserve task routing boundaries;
- assess module readiness and state; and
- record whether a module is planned, implemented, evaluated, or blocked.

This is a proposed interaction. The repository does not show a working Master Core or a registry API that it consumes.

### Universal Infrastructure interaction

The registry should identify how each module depends on shared infrastructure, including:

- context and memory;
- knowledge retrieval or evidence services;
- model gateway or provider abstraction;
- tools and integrations;
- evaluation and verification services;
- security and governance controls;
- observability and audit records; and
- cross-module collaboration channels.

The registry should not assume that shared infrastructure is operational merely because a concept exists in an architecture document. A declared dependency is not the same as a verified integration.

## 8. Module Lifecycle and Status

The registry should distinguish module lifecycle from capability status. The lifecycle describes evolution over time. The capability status describes the evidence-supported state of a module's implementation or readiness.

### Proposed lifecycle states

- **Proposed** — a module concept is named and described but no implementation is authorized.
- **Specified** — the module has an architectural definition or contract boundary.
- **In Development** — implementation work is active or in progress.
- **Available for Evaluation** — the module is available for evaluation under explicit conditions.
- **Approved for Deployment** — an explicit approval decision exists for deployment or release.
- **Deployed** — the module is operational in a supported environment.
- **Deprecated** — the module remains recognized but should be replaced or phased out.
- **Retired** — the module is no longer active.

These lifecycle labels are proposed unless a separate repository governance decision approves them. They are not equivalent to implementation status.

### Capability-status vocabulary

The repository's established capability-status vocabulary is:

- `IMPLEMENTED`
- `ADAPTER-READY`
- `MOCKED`
- `EXPERIMENTAL`
- `NOT IMPLEMENTED`
- `BLOCKED`
- `UNKNOWN`

This vocabulary should be used to describe module evidence state. A module may be specified without being implemented, and a module may be implemented without being approved for deployment. Those are distinct facts and should remain distinct in the registry.

No invented lifecycle authority or approval role should be assigned in this document.

## 9. The 100-Module Portfolio and Future Extensibility

The intended SUPER AGI architecture includes a single unified system with 100 major intelligence modules. The registry should support that portfolio without creating 100 independent systems or misrepresenting planned modules as operational ones.

The registry should therefore:

- assign a stable module identity to each module record;
- keep a module's status and workspace metadata distinct from its implementation reality;
- reference shared infrastructure and common capabilities;
- express cross-module relationships clearly;
- preserve the 100-module target as a portfolio goal, not a claim of completed implementation;
- allow extension beyond 100 modules, including future additions such as module 101 and beyond;
- identify planned modules separately from implemented, evaluated, approved, or deployed modules; and
- prevent duplicate module identities or overlapping responsibilities.

The repository does not currently contain an authoritative list of the 100 modules, nor an authoritative registry of actual module records. The registry should not fabricate a complete portfolio as if it were already established.

## 10. Dependencies and Cross-Module Relationships

Registry entries should be able to express several kinds of relationships:

- **Required dependency** — required for a module's intended function.
- **Optional dependency** — helpful or context-dependent but not mandatory.
- **Shared infrastructure dependency** — depends on memory, context, model gateway, tools, evaluation, or governance services.
- **Related module** — a sibling or adjacent module with shared data or dependency boundaries.
- **Collaboration interface** — a declared interaction path between modules.
- **Compatibility constraint** — version or behavior restrictions that affect coexistence.
- **Evidence dependency** — the module depends on verification or evidence from another module or service.

A declared dependency is not proof of an operational, working integration. The registry should distinguish the following states explicitly:

- declared dependency;
- implemented dependency;
- evaluated compatibility;
- deployed integration;
- blocked or incompatible dependency.

This preserves the distinction between architectural intent and evidence-backed behavior.

## 11. Validation and Governance Boundaries

The registry must maintain integrity without pretending that automation or enforcement already exists. Intended governance requirements include:

- unique identifiers;
- consistent metadata conventions;
- valid references to contracts, workspaces, documentation, and evidence;
- explicit capability and lifecycle status;
- evidence for implementation claims;
- controlled updates and deprecations;
- version and compatibility handling;
- permission and approval boundaries;
- traceable update history; and
- clear separation between design, implementation, evaluation, and deployment.

These are architecture requirements. They do not authorize an implementation or claim that registry validation is operational.

Human review and approval remain outside the registry itself. A registry entry or a module change does not grant authority, release a module, or bypass the repository's human-approval boundaries.

## 12. Open Decisions and Implementation Evidence

The following decisions remain unresolved or only partially supported by existing repository evidence:

- final registry identifier convention;
- authoritative source of the 100-module portfolio;
- final registry entry schema and storage model;
- versioning and compatibility policy;
- ownership and maintenance responsibilities;
- lifecycle approval authority;
- registry access interfaces and authentication boundaries;
- distinction between registry metadata and workspace navigation metadata;
- dependency validation and conflict resolution method;
- persistence or distribution mechanism for registry records;
- evidence standard for module approval and deployment claims; and
- how the registry integrates with the Master Core, model gateway, and cross-module collaboration contracts.

The repository does not currently provide implementation evidence for any of the registry infrastructure or any authoritative module list. It also does not provide an approved methodology for lifecycle approval or deployment status. These gaps should be reported clearly rather than silently assumed away.

## 13. Implementation Boundary

This task creates an architecture specification only. It must not:

- implement a registry service or database;
- create executable registry validators;
- create or populate a production registry;
- invent the authoritative list of 100 modules;
- create module implementations or workspaces;
- create or modify provider adapters, Skills, agent definitions, workflows, or tool integrations;
- create a separate schema file;
- modify or redefine the Master Core, Universal Infrastructure, five-plane architecture, or L0–L15 layer map;
- claim that all 100 modules exist operationally; or
- claim AGI, SUPER AGI, or consciousness capabilities without supporting evidence.

This document should be treated as a planned, evidence-bounded architecture contribution, not as completion of the implementation of the Module Registry or of the module portfolio itself.

## Related Canonical and Supporting Documents

Existing canonical documents:

- [`SOURCE_OF_TRUTH.md`](SOURCE_OF_TRUTH.md)
- [`PRODUCT_CONSTITUTION.md`](PRODUCT_CONSTITUTION.md)
- [`SYSTEM_BOUNDARIES.md`](SYSTEM_BOUNDARIES.md)
- [`L0-L15-LAYER-MAP.md`](L0-L15-LAYER-MAP.md)
- [`FIVE-PLANES.md`](FIVE-PLANES.md)
- [`MASTER-CORE.md`](MASTER-CORE.md)

Planned repository targets that are not yet established as existing documents:

- `architecture/UNIVERSAL-INFRASTRUCTURE.md`
- `architecture/MODULE-CONTRACT.md`
- `architecture/UNIVERSAL-CONTEXT.md`
- `architecture/CROSS-AGI-COLLABORATION.md`
- `architecture/MODEL-GATEWAY.md`
- `architecture/SECURITY-GOVERNANCE.md`
- `architecture/CAPABILITY-STATUS.md`
- `architecture/ARCHITECTURE-DECISIONS.md`
- `architecture/OPEN-DECISIONS.md`

This registry design is intentionally limited to architecture definition and evidence boundaries. Implementation, validation, deployment approval, and runtime operation remain separate states that require explicit evidence.

"""Strict JSON Skill manifests loaded into the existing Skill registry model."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from scripts.skill_registry import (
    DuplicateSkillError,
    SkillContract,
    SkillMetadataError,
    SkillRegistry,
    SkillValueType,
)


SUPPORTED_MANIFEST_VERSION = 1
_MANIFEST_SUFFIX = ".manifest.json"
_IGNORED_DISCOVERY_DIRECTORIES = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "__pypackages__",
    "build",
    "dist",
    "env",
    "node_modules",
    "site-packages",
    "target",
    "venv",
}
_MANIFEST_FIELDS = {
    "manifest_version",
    "identifier",
    "name",
    "description",
    "source_path",
    "version",
    "contract_version",
    "category",
    "tags",
    "inputs",
    "outputs",
    "tools",
    "capabilities",
    "input_fields",
    "output_fields",
    "strict_inputs",
    "strict_outputs",
}
_REQUIRED_FIELDS = {
    "manifest_version",
    "identifier",
    "name",
    "description",
    "source_path",
}
_SEQUENCE_FIELDS = {
    "tags",
    "inputs",
    "outputs",
    "tools",
    "capabilities",
}
_SKILL_FIELD_KEYS = {"name", "value_type", "required", "nullable"}
_OPTIONAL_STRING_FIELDS = {"version", "category"}
_BOOLEAN_FIELDS = {"strict_inputs", "strict_outputs"}


class SkillManifestError(ValueError):
    """Raised when a Skill manifest cannot be safely parsed or validated."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "invalid_manifest",
        skill_identifier: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.skill_identifier = skill_identifier


@dataclass(frozen=True, slots=True)
class SkillManifest:
    """A validated manifest version and its corresponding runtime contract."""

    manifest_version: int
    contract: SkillContract

    def __post_init__(self) -> None:
        if (
            type(self.manifest_version) is not int
            or self.manifest_version != SUPPORTED_MANIFEST_VERSION
        ):
            raise SkillManifestError(
                "manifest_version is unsupported.", code="unsupported_manifest_version"
            )
        if not isinstance(self.contract, SkillContract):
            raise SkillManifestError(
                "contract must be a validated SkillContract.", code="invalid_contract"
            )


@dataclass(frozen=True, slots=True)
class SkillManifestCatalogEntry:
    """One validated manifest paired with its repository-relative file path."""

    manifest_path: Path
    manifest: SkillManifest


@dataclass(frozen=True, slots=True)
class SkillManifestCatalogIssue:
    """A safe, deterministic description of one catalog validation conflict."""

    manifest_path: Path
    code: str
    message: str
    skill_identifier: str | None = None
    conflicting_manifest_path: Path | None = None


class SkillManifestCatalogError(SkillManifestError):
    """Raised when any discovered manifest prevents accepting a whole catalog."""

    def __init__(self, issues: tuple[SkillManifestCatalogIssue, ...]) -> None:
        if not issues:
            raise ValueError("catalog errors must contain at least one issue.")
        self.issues = issues
        details = "; ".join(
            f"{issue.manifest_path.as_posix()}: {issue.message}" for issue in issues
        )
        super().__init__(
            f"Skill manifest catalog is invalid: {details}",
            code="invalid_manifest_catalog",
        )


@dataclass(frozen=True, slots=True)
class SkillManifestCatalog:
    """A fully validated, deterministically ordered set of manifest entries."""

    repository_root: Path
    entries: tuple[SkillManifestCatalogEntry, ...]


def discover_skill_manifests(repository_root: Path) -> tuple[Path, ...]:
    """Discover lower-case ``*.manifest.json`` files beneath an explicit root.

    Results are absolute paths ordered by case-folded repository-relative path,
    with the original path as a deterministic tie-breaker. Generated directories
    and all directory symlinks are excluded; the loader separately rejects any
    matching manifest symlink that resolves outside the root.
    """
    root = _validated_repository_root(repository_root)
    candidates: list[Path] = []

    def fail_on_walk_error(error: OSError) -> None:
        raise SkillManifestError(
            "manifest discovery could not read a repository directory.",
            code="manifest_discovery_failed",
        ) from error

    for current, directory_names, file_names in os.walk(
        root, topdown=True, followlinks=False, onerror=fail_on_walk_error
    ):
        current_path = Path(current)
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name.casefold() not in _IGNORED_DISCOVERY_DIRECTORIES
            and not (current_path / name).is_symlink()
        )
        candidates.extend(
            current_path / name
            for name in file_names
            if name.endswith(_MANIFEST_SUFFIX)
        )

    return tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                candidate.relative_to(root).as_posix().casefold(),
                candidate.relative_to(root).as_posix(),
            ),
        )
    )


def load_skill_manifest_catalog(repository_root: Path) -> SkillManifestCatalog:
    """Discover and validate every manifest, rejecting the catalog on any issue.

    All files are processed in discovery order. Validation and duplicate
    identifier issues are accumulated before an error is raised, so callers
    receive the same complete issue list on each run.
    """
    root = _validated_repository_root(repository_root)
    entries: list[SkillManifestCatalogEntry] = []
    issues: list[SkillManifestCatalogIssue] = []
    first_by_identifier: dict[str, SkillManifestCatalogEntry] = {}

    for manifest_path in discover_skill_manifests(root):
        relative_path = manifest_path.relative_to(root)
        try:
            manifest = load_skill_manifest(manifest_path, root)
        except SkillManifestError as error:
            issues.append(
                SkillManifestCatalogIssue(
                    manifest_path=relative_path,
                    code=error.code,
                    message=str(error),
                    skill_identifier=error.skill_identifier,
                )
            )
            continue

        entry = SkillManifestCatalogEntry(relative_path, manifest)
        identifier = manifest.contract.identifier
        previous = first_by_identifier.get(identifier)
        if previous is not None:
            same_contract = previous.manifest.contract == manifest.contract
            if same_contract:
                message = (
                    f"Skill identifier '{identifier}' is also declared by "
                    f"'{previous.manifest_path.as_posix()}'."
                )
            else:
                message = (
                    f"Skill identifier '{identifier}' has conflicting contract "
                    f"declarations; the first is in "
                    f"'{previous.manifest_path.as_posix()}'."
                )
            issues.append(
                SkillManifestCatalogIssue(
                    manifest_path=relative_path,
                    code="duplicate_skill_identifier",
                    message=message,
                    skill_identifier=identifier,
                    conflicting_manifest_path=previous.manifest_path,
                )
            )
        else:
            first_by_identifier[identifier] = entry
        entries.append(entry)

    if issues:
        raise SkillManifestCatalogError(tuple(issues))
    return SkillManifestCatalog(root, tuple(entries))


def register_skill_manifest_catalog(
    registry: SkillRegistry,
) -> tuple[SkillContract, ...]:
    """Validate all discovered manifests, then register them as one batch."""
    if not isinstance(registry, SkillRegistry):
        raise SkillManifestError(
            "registry must be a SkillRegistry.", code="invalid_registry"
        )

    catalog = load_skill_manifest_catalog(registry.repository_root)
    registered_contracts = {
        contract.identifier: contract for contract in registry.list_skills()
    }
    conflicts: list[SkillManifestCatalogIssue] = []
    for entry in catalog.entries:
        contract = entry.manifest.contract
        existing = registered_contracts.get(contract.identifier)
        if existing is None:
            continue
        same_contract = existing == contract
        conflicts.append(
            SkillManifestCatalogIssue(
                manifest_path=entry.manifest_path,
                code=(
                    "duplicate_skill_identifier"
                    if same_contract
                    else "conflicting_skill_declaration"
                ),
                message=(
                    f"Skill identifier '{contract.identifier}' is already registered."
                    if same_contract
                    else f"Skill identifier '{contract.identifier}' conflicts with "
                    "an existing registry contract."
                ),
                skill_identifier=contract.identifier,
            )
        )
    if conflicts:
        raise SkillManifestCatalogError(tuple(conflicts))

    contracts = tuple(entry.manifest.contract for entry in catalog.entries)
    try:
        registry.register_many(contracts)
    except DuplicateSkillError as error:
        # Preserve manifest context if a concurrent registry change occurred
        # after preflight but before the batch was committed.
        current_contracts = {
            contract.identifier: contract for contract in registry.list_skills()
        }
        concurrent_conflicts: list[SkillManifestCatalogIssue] = []
        for entry in catalog.entries:
            contract = entry.manifest.contract
            existing = current_contracts.get(contract.identifier)
            if existing is None:
                continue
            same_contract = existing == contract
            concurrent_conflicts.append(
                SkillManifestCatalogIssue(
                    manifest_path=entry.manifest_path,
                    code=(
                        "duplicate_skill_identifier"
                        if same_contract
                        else "conflicting_skill_declaration"
                    ),
                    message=(
                        f"Skill identifier '{contract.identifier}' became "
                        "registered during catalog preflight."
                    ),
                    skill_identifier=contract.identifier,
                )
            )
        if concurrent_conflicts:
            raise SkillManifestCatalogError(tuple(concurrent_conflicts)) from error
        raise
    except (OSError, RuntimeError, ValueError) as error:
        source_issues: list[SkillManifestCatalogIssue] = []
        for entry in catalog.entries:
            try:
                entry.manifest.contract.resolve_source(registry.repository_root)
            except (OSError, RuntimeError, ValueError):
                source_issues.append(
                    SkillManifestCatalogIssue(
                        manifest_path=entry.manifest_path,
                        code="unsafe_or_missing_skill_source",
                        message="declared Skill source is no longer available beneath the repository root.",
                        skill_identifier=entry.manifest.contract.identifier,
                    )
                )
        if source_issues:
            raise SkillManifestCatalogError(tuple(source_issues)) from error
        if catalog.entries:
            raise SkillManifestCatalogError(
                (
                    SkillManifestCatalogIssue(
                        manifest_path=catalog.entries[0].manifest_path,
                        code="skill_registration_failed",
                        message="registry rejected a prevalidated Skill contract.",
                        skill_identifier=(
                            catalog.entries[0].manifest.contract.identifier
                        ),
                    ),
                )
            ) from error
        raise SkillManifestError(
            "registry rejected the empty Skill manifest catalog.",
            code="catalog_registration_failed",
        ) from error
    return contracts


def _validated_repository_root(repository_root: Path) -> Path:
    if not isinstance(repository_root, Path):
        raise SkillManifestError(
            "repository_root must be a pathlib.Path.", code="invalid_repository_root"
        )
    try:
        root = repository_root.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as error:
        raise SkillManifestError(
            "repository_root must be an existing directory.",
            code="invalid_repository_root",
        ) from error
    if not root.is_dir():
        raise SkillManifestError(
            "repository_root must be an existing directory.",
            code="invalid_repository_root",
        )
    return root


def load_skill_manifest(
    manifest_path: Path, repository_root: Path
) -> SkillManifest:
    """Load and validate one JSON manifest under an explicit repository root.

    Parsing never executes manifest content or reads Skill source contents.
    The contract's source path is resolved and checked for containment and
    existence before a manifest is returned.
    """
    root = Path(repository_root).resolve()
    if not root.is_dir():
        raise SkillManifestError(
            "repository_root must be an existing directory.", code="invalid_repository_root"
        )
    source_manifest = Path(manifest_path)
    if not source_manifest.is_absolute():
        if source_manifest.drive or ".." in source_manifest.parts:
            raise SkillManifestError(
                "manifest_path must remain beneath repository_root.",
                code="unsafe_manifest_path",
            )
        source_manifest = root / source_manifest
    try:
        resolved_manifest = source_manifest.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as error:
        raise SkillManifestError(
            "manifest file does not exist or cannot be resolved.",
            code="manifest_unavailable",
        ) from error
    if not resolved_manifest.is_relative_to(root) or not resolved_manifest.is_file():
        raise SkillManifestError(
            "manifest file must be a file beneath repository_root.",
            code="unsafe_manifest_path",
        )

    try:
        with resolved_manifest.open("r", encoding="utf-8") as manifest_file:
            raw_manifest = json.load(
                manifest_file,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_non_json_constant,
            )
    except (OSError, UnicodeError) as error:
        raise SkillManifestError(
            "manifest file could not be read as UTF-8.", code="manifest_read_failed"
        ) from error
    except json.JSONDecodeError as error:
        raise SkillManifestError(
            f"manifest JSON is malformed at line {error.lineno}, column {error.colno}.",
            code="invalid_manifest_json",
        ) from error
    except _DuplicateManifestKey as error:
        raise SkillManifestError(
            "manifest file contains a duplicate JSON object key.",
            code="duplicate_manifest_key",
        ) from error
    except ValueError as error:
        raise SkillManifestError(
            "manifest file contains invalid JSON.", code="invalid_manifest_json"
        ) from error

    if not isinstance(raw_manifest, dict):
        raise SkillManifestError(
            "manifest root must be a JSON object.", code="invalid_manifest_root"
        )
    missing = sorted(_REQUIRED_FIELDS.difference(raw_manifest))
    if missing:
        raise SkillManifestError(
            f"manifest is missing required field(s): {', '.join(missing)}.",
            code="missing_manifest_fields",
        )
    unknown = sorted(set(raw_manifest).difference(_MANIFEST_FIELDS))
    if unknown:
        raise SkillManifestError(
            f"manifest contains unknown field(s): {', '.join(unknown)}.",
            code="unknown_manifest_fields",
        )

    manifest_version = raw_manifest["manifest_version"]
    if type(manifest_version) is not int or manifest_version != SUPPORTED_MANIFEST_VERSION:
        raise SkillManifestError(
            "manifest_version is unsupported.", code="unsupported_manifest_version"
        )
    contract_values = {
        key: value for key, value in raw_manifest.items() if key != "manifest_version"
    }
    _validate_manifest_value_types(contract_values)
    _validate_source_path(contract_values["source_path"])

    try:
        contract = SkillContract.from_mapping(contract_values)
    except SkillMetadataError as error:
        safe_identifier = _safe_skill_identifier(contract_values.get("identifier"))
        raise SkillManifestError(
            f"manifest contract is invalid: {error}",
            code="invalid_skill_contract",
            skill_identifier=safe_identifier,
        ) from error
    try:
        contract.resolve_source(root)
    except SkillMetadataError as error:
        raise SkillManifestError(
            "manifest source_path must resolve to a repository-local file.",
            code="unsafe_or_missing_skill_source",
            skill_identifier=contract.identifier,
        ) from error
    except (OSError, RuntimeError, ValueError) as error:
        raise SkillManifestError(
            "manifest source_path could not be safely resolved.",
            code="unsafe_or_missing_skill_source",
            skill_identifier=contract.identifier,
        ) from error
    return SkillManifest(manifest_version=manifest_version, contract=contract)


def register_skill_manifest(
    registry: SkillRegistry, manifest_path: Path
) -> SkillContract:
    """Load a manifest using the registry's configured root and register it."""
    if not isinstance(registry, SkillRegistry):
        raise SkillManifestError(
            "registry must be a SkillRegistry.", code="invalid_registry"
        )
    manifest = load_skill_manifest(manifest_path, registry.repository_root)
    contract = manifest.contract
    try:
        registry.register(contract)
    except DuplicateSkillError as error:
        raise SkillManifestError(
            f"Skill '{contract.identifier}' is already registered.",
            code="duplicate_skill_identifier",
            skill_identifier=contract.identifier,
        ) from error
    except SkillMetadataError as error:
        raise SkillManifestError(
            f"could not register Skill '{contract.identifier}'.",
            code="skill_registration_failed",
            skill_identifier=contract.identifier,
        ) from error
    return contract


def _validate_manifest_value_types(values: Mapping[str, object]) -> None:
    for field_name in _SEQUENCE_FIELDS:
        if field_name not in values:
            continue
        value = values[field_name]
        if not isinstance(value, list):
            raise SkillManifestError(
                f"manifest field '{field_name}' must be an array of non-empty strings.",
                code="invalid_manifest_field",
            )
        for item in value:
            if not isinstance(item, str):
                raise SkillManifestError(
                    f"manifest field '{field_name}' must be an array of non-empty strings.",
                    code="invalid_manifest_field",
                )
            if not item.strip():
                raise SkillManifestError(
                    f"manifest field '{field_name}' must be an array of non-empty strings.",
                    code="invalid_manifest_field",
                )
    for field_name in _OPTIONAL_STRING_FIELDS:
        if field_name not in values:
            continue
        value = values[field_name]
        if value is None:
            continue
        if not isinstance(value, str):
            raise SkillManifestError(
                f"manifest field '{field_name}' must be a non-empty string or null.",
                code="invalid_manifest_field",
            )
        if not value.strip():
            raise SkillManifestError(
                f"manifest field '{field_name}' must be a non-empty string or null.",
                code="invalid_manifest_field",
            )
    for field_name in _BOOLEAN_FIELDS:
        if field_name in values and type(values[field_name]) is not bool:
            raise SkillManifestError(
                f"manifest field '{field_name}' must be a boolean.",
                code="invalid_manifest_field",
            )
    for field_name in ("input_fields", "output_fields"):
        if field_name not in values:
            continue
        declarations = values[field_name]
        if not isinstance(declarations, list):
            raise SkillManifestError(
                f"manifest field '{field_name}' must be an array of field objects.",
                code="invalid_manifest_field",
            )
        for declaration in declarations:
            if not isinstance(declaration, dict):
                raise SkillManifestError(
                    f"manifest field '{field_name}' entries must be objects.",
                    code="invalid_manifest_field",
                )
            unknown = sorted(set(declaration).difference(_SKILL_FIELD_KEYS))
            missing = sorted({"name", "value_type"}.difference(declaration))
            if unknown or missing:
                raise SkillManifestError(
                    f"manifest field '{field_name}' entry has missing or unknown keys.",
                    code="invalid_manifest_field",
                )
            if not isinstance(declaration["name"], str):
                raise SkillManifestError(
                    "Skill field name must be a string.", code="invalid_manifest_field"
                )
            if not isinstance(declaration["value_type"], str):
                raise SkillManifestError(
                    "Skill field value_type must be a string.",
                    code="invalid_manifest_field",
                )
            if declaration["value_type"] not in {kind.value for kind in SkillValueType}:
                raise SkillManifestError(
                    "Skill field value_type is unsupported.",
                    code="invalid_manifest_field",
                )
            for boolean_name in ("required", "nullable"):
                if boolean_name in declaration and type(declaration[boolean_name]) is not bool:
                    raise SkillManifestError(
                        f"Skill field '{boolean_name}' must be a boolean.",
                        code="invalid_manifest_field",
                    )


def _validate_source_path(source_path: object) -> None:
    if not isinstance(source_path, str) or not source_path.strip():
        raise SkillManifestError(
            "manifest source_path must be a non-empty relative path.",
            code="invalid_source_path",
        )
    if "\x00" in source_path:
        raise SkillManifestError(
            "manifest source_path contains an invalid character.",
            code="invalid_source_path",
        )
    relative_path = Path(source_path)
    if (
        relative_path.is_absolute()
        or relative_path.drive
        or ".." in relative_path.parts
    ):
        raise SkillManifestError(
            "manifest source_path must remain beneath repository_root.",
            code="unsafe_source_path",
        )


def _safe_skill_identifier(value: object) -> str | None:
    if (
        isinstance(value, str)
        and value.isascii()
        and value.replace("-", "").isalnum()
    ):
        return value
    return None


class _DuplicateManifestKey(ValueError):
    """Internal signal for duplicate object keys in strict manifest JSON."""


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateManifestKey
        result[key] = value
    return result


def _reject_non_json_constant(value: str) -> object:
    raise ValueError(f"invalid JSON constant: {value}")

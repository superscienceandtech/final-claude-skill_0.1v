"""Typed, in-memory contracts and read-only discovery for repository Skills.

Discovery reads a deliberately small subset of the repository's observed
front-matter convention. It does not parse general YAML or execute Skill files.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Mapping as ABCMapping, Sequence as ABCSequence
from enum import Enum
from threading import Lock
from typing import Mapping, Sequence


IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
CONTRACT_VERSION_PATTERN = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z"
)
DEFAULT_CONTRACT_VERSION = "1.0.0"
_DISCOVERY_DIRECTORIES = {".git", ".venv", "venv", "__pycache__", "node_modules"}
_DISCOVERY_FIELDS = {"name", "description"}


class SkillMetadataError(ValueError):
    """Raised when Skill contract metadata is invalid."""


class DuplicateSkillError(SkillMetadataError):
    """Raised when a registry already contains the Skill identifier."""


class SkillNotFoundError(KeyError):
    """Raised when a requested Skill identifier is not registered."""


class SkillContractVersionError(SkillMetadataError):
    """Raised when a requested contract version is malformed or unavailable."""


def is_valid_contract_version(value: object) -> bool:
    """Return whether ``value`` is a canonical numeric major.minor.patch version."""
    return isinstance(value, str) and CONTRACT_VERSION_PATTERN.fullmatch(value) is not None


class SkillValueType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


@dataclass(frozen=True, slots=True)
class SkillField:
    """One shallow-validated input or output field in a Skill contract."""

    name: str
    value_type: SkillValueType
    required: bool = True
    nullable: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not IDENTIFIER_PATTERN.fullmatch(self.name):
            raise SkillMetadataError("Skill field name must be a lowercase identifier.")
        if not isinstance(self.value_type, SkillValueType):
            raise SkillMetadataError("Skill field value_type must be a SkillValueType.")
        if not isinstance(self.required, bool):
            raise SkillMetadataError("Skill field required must be a boolean.")
        if not isinstance(self.nullable, bool):
            raise SkillMetadataError("Skill field nullable must be a boolean.")


def _matches_skill_type(value_type: SkillValueType, value: object) -> bool:
    if value is None:
        return False
    if value_type is SkillValueType.STRING:
        return isinstance(value, str)
    if value_type is SkillValueType.INTEGER:
        return isinstance(value, int) and not isinstance(value, bool)
    if value_type is SkillValueType.NUMBER:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if value_type is SkillValueType.BOOLEAN:
        return isinstance(value, bool)
    if value_type is SkillValueType.OBJECT:
        return isinstance(value, ABCMapping)
    if value_type is SkillValueType.ARRAY:
        return isinstance(value, ABCSequence) and not isinstance(
            value, (str, bytes, bytearray)
        )
    return False


def _skill_field_from_mapping(value: object) -> SkillField:
    if not isinstance(value, Mapping):
        raise SkillMetadataError("Skill field definition must be a mapping.")
    field_values = dict(value)
    raw_type = field_values.get("value_type")
    try:
        field_values["value_type"] = (
            raw_type if isinstance(raw_type, SkillValueType) else SkillValueType(raw_type)
        )
        return SkillField(**field_values)
    except (TypeError, ValueError) as error:
        raise SkillMetadataError("Skill field definition is invalid.") from error


@dataclass(frozen=True, slots=True)
class SkillContract:
    """Validated metadata for one Skill source file.

    ``source_path`` is repository-relative. Its existence and containment are
    checked by :meth:`resolve_source` against an explicitly supplied root.
    """

    identifier: str
    name: str
    description: str
    source_path: Path
    version: str | None = None
    category: str | None = None
    tags: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    input_fields: tuple[SkillField, ...] = ()
    output_fields: tuple[SkillField, ...] = ()
    strict_inputs: bool = False
    strict_outputs: bool = False
    contract_version: str = DEFAULT_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not IDENTIFIER_PATTERN.fullmatch(
            self.identifier
        ):
            raise SkillMetadataError(
                "identifier must be a lowercase kebab-case value "
                "(for example, 'implementation')."
            )
        for field_name in ("name", "description"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise SkillMetadataError(f"{field_name} must be a non-empty string.")
        if not isinstance(self.source_path, Path):
            raise SkillMetadataError("source_path must be a pathlib.Path.")
        if self.source_path.is_absolute():
            raise SkillMetadataError("source_path must be relative to the repository root.")
        if not str(self.source_path):
            raise SkillMetadataError("source_path must not be empty.")

        for field_name in ("version", "category"):
            value = getattr(self, field_name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise SkillMetadataError(f"{field_name} must be a non-empty string when set.")
        if not is_valid_contract_version(self.contract_version):
            raise SkillMetadataError(
                "contract_version must use canonical major.minor.patch format."
            )
        for field_name in ("tags", "inputs", "outputs", "tools", "capabilities"):
            values = getattr(self, field_name)
            if not isinstance(values, tuple):
                raise SkillMetadataError(
                    f"{field_name} must be a tuple of non-empty strings."
                )
            for value in values:
                if not isinstance(value, str) or not value.strip():
                    raise SkillMetadataError(
                        f"{field_name} must be a tuple of non-empty strings."
                    )
        for field_name in ("input_fields", "output_fields"):
            fields = getattr(self, field_name)
            if not isinstance(fields, tuple) or any(
                not isinstance(field, SkillField) for field in fields
            ):
                raise SkillMetadataError(
                    f"{field_name} must be a tuple of SkillField values."
                )
            names = [field.name for field in fields]
            if len(names) != len(set(names)):
                raise SkillMetadataError(f"{field_name} contains duplicate names.")
        for legacy_names, typed_fields, label in (
            (self.inputs, self.input_fields, "input"),
            (self.outputs, self.output_fields, "output"),
        ):
            overlap = set(legacy_names).intersection(field.name for field in typed_fields)
            if overlap:
                raise SkillMetadataError(
                    f"legacy and typed {label} declarations overlap."
                )
        if not isinstance(self.strict_inputs, bool) or not isinstance(
            self.strict_outputs, bool
        ):
            raise SkillMetadataError("strict_inputs and strict_outputs must be booleans.")

    @classmethod
    def from_mapping(cls, metadata: Mapping[str, object]) -> SkillContract:
        """Build a contract from a mapping, rejecting unknown or invalid fields."""
        if not isinstance(metadata, Mapping):
            raise SkillMetadataError("metadata must be a mapping.")

        fields = {
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
        required = {"identifier", "name", "description", "source_path"}
        missing = sorted(required.difference(metadata))
        if missing:
            raise SkillMetadataError(f"missing required metadata field(s): {', '.join(missing)}.")
        unknown = sorted(set(metadata).difference(fields))
        if unknown:
            raise SkillMetadataError(f"unknown metadata field(s): {', '.join(unknown)}.")

        values = dict(metadata)
        raw_path = values["source_path"]
        if isinstance(raw_path, str):
            if not raw_path:
                raise SkillMetadataError("source_path must not be empty.")
            values["source_path"] = Path(raw_path)
        elif not isinstance(raw_path, Path):
            raise SkillMetadataError("source_path must be a string or pathlib.Path.")

        for field_name in ("tags", "inputs", "outputs", "tools", "capabilities",
                           "input_fields", "output_fields"):
            if field_name not in values:
                continue
            raw_values = values[field_name]
            if isinstance(raw_values, (str, bytes)) or not isinstance(
                raw_values, Sequence
            ):
                raise SkillMetadataError(f"{field_name} must be a sequence of strings.")
            normalized_values = tuple(raw_values)
            values[field_name] = normalized_values
            if field_name in ("input_fields", "output_fields"):
                try:
                    values[field_name] = tuple(
                        item
                        if isinstance(item, SkillField)
                        else _skill_field_from_mapping(item)
                        for item in normalized_values
                    )
                except (TypeError, ValueError) as error:
                    raise SkillMetadataError(
                        f"{field_name} must contain SkillField definitions."
                    ) from error

        try:
            return cls(**values)  # type: ignore[arg-type]
        except TypeError as error:
            raise SkillMetadataError(f"invalid Skill metadata: {error}") from error

    def validate_inputs(self, values: Mapping[str, object]) -> None:
        """Validate input names, requiredness, and shallow declared types."""
        _validate_skill_values(
            values,
            self.inputs,
            self.input_fields,
            self.strict_inputs,
            "input",
            legacy_allowlist=bool(self.inputs),
        )

    def validate_outputs(self, values: Mapping[str, object]) -> str | None:
        """Return a safe output-contract failure code, or None when valid."""
        if not isinstance(values, Mapping) or any(
            not isinstance(name, str) or not name.strip() for name in values
        ):
            return "invalid_skill_output"
        fields = {field.name: field for field in self.output_fields}
        allowed = set(self.outputs).union(fields)
        required = set(self.outputs).union(
            field.name for field in self.output_fields if field.required
        )
        if required.difference(values):
            return "missing_skill_output"
        if (self.outputs or self.strict_outputs) and set(values).difference(allowed):
            return "unexpected_skill_output"
        if any(
            not field.nullable and values[field.name] is None
            or values[field.name] is not None
            and not _matches_skill_type(field.value_type, values[field.name])
            for field in self.output_fields
            if field.name in values
        ):
            return "invalid_skill_output"
        return None

    def resolve_source(self, repository_root: Path) -> Path:
        """Resolve this Skill source under ``repository_root`` and require a file."""
        root = Path(repository_root).resolve()
        if not root.is_dir():
            raise SkillMetadataError(f"repository root is not a directory: {root}")

        source = (root / self.source_path).resolve()
        if not source.is_relative_to(root):
            raise SkillMetadataError(
                f"Skill source escapes the repository root: {self.source_path}"
            )
        if not source.is_file():
            raise SkillMetadataError(f"Skill source file does not exist: {self.source_path}")
        return source


def _validate_skill_values(
    values: Mapping[str, object],
    legacy_names: tuple[str, ...],
    fields: tuple[SkillField, ...],
    strict: bool,
    label: str,
    *,
    legacy_exact: bool = False,
    legacy_allowlist: bool = False,
) -> None:
    if not isinstance(values, Mapping):
        raise SkillMetadataError(f"{label}s must be a mapping.")
    if any(not isinstance(name, str) or not name.strip() for name in values):
        raise SkillMetadataError(f"{label} names must be non-empty strings.")
    typed = {field.name: field for field in fields}
    declared = set(legacy_names).union(typed)
    if (legacy_exact or strict or legacy_allowlist) and set(values).difference(declared):
        raise SkillMetadataError(f"{label}s contain undeclared field names.")
    if legacy_exact and set(legacy_names).difference(values):
        raise SkillMetadataError(f"{label}s are missing declared field names.")
    if any(field.required and field.name not in values for field in fields):
        raise SkillMetadataError(f"{label}s are missing required fields.")
    for name, field in typed.items():
        if name not in values:
            continue
        value = values[name]
        if value is None and field.nullable:
            continue
        if not _matches_skill_type(field.value_type, value):
            raise SkillMetadataError(f"{label} field value type is invalid.")


@dataclass(frozen=True, slots=True)
class DiscoveryIssue:
    """A candidate Skill that could not be converted to a valid contract."""

    source_path: Path
    message: str


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    """Read-only discovery output; issues do not imply execution or approval."""

    skills: tuple[SkillContract, ...]
    issues: tuple[DiscoveryIssue, ...]


class SkillRegistry:
    """Deterministic in-memory registry for validated Skill contracts."""

    def __init__(self, repository_root: Path) -> None:
        self._root = Path(repository_root).resolve()
        if not self._root.is_dir():
            raise SkillMetadataError(f"repository root is not a directory: {self._root}")
        self._skills: dict[str, SkillContract] = {}
        self._lock = Lock()

    @property
    def repository_root(self) -> Path:
        """Return the explicit root used to contain registered Skill sources."""
        return self._root

    def register(self, contract: SkillContract) -> None:
        """Register a contract after validating that its source is repository-local."""
        if not isinstance(contract, SkillContract):
            raise SkillMetadataError("contract must be a SkillContract.")
        with self._lock:
            contract.resolve_source(self._root)
            if contract.identifier in self._skills:
                raise DuplicateSkillError(
                    f"Skill identifier is already registered: {contract.identifier}"
                )
            self._skills[contract.identifier] = contract

    def register_many(self, contracts: Sequence[SkillContract]) -> None:
        """Validate a batch fully before adding any contracts to this registry."""
        if isinstance(contracts, (str, bytes)) or not isinstance(contracts, Sequence):
            raise SkillMetadataError("contracts must be a sequence of SkillContract values.")

        with self._lock:
            pending: dict[str, SkillContract] = {}
            for contract in contracts:
                if not isinstance(contract, SkillContract):
                    raise SkillMetadataError(
                        "contracts must contain SkillContract values."
                    )
                if contract.identifier in pending or contract.identifier in self._skills:
                    raise DuplicateSkillError(
                        f"Skill identifier is already registered: {contract.identifier}"
                    )
                pending[contract.identifier] = contract

            for contract in pending.values():
                contract.resolve_source(self._root)

            self._skills.update(pending)

    def get(self, identifier: str) -> SkillContract:
        """Return a registered Skill or raise :class:`SkillNotFoundError`."""
        if not isinstance(identifier, str):
            raise SkillNotFoundError("Skill identifier must be a string.")
        with self._lock:
            try:
                return self._skills[identifier]
            except KeyError as error:
                raise SkillNotFoundError(
                    f"Skill is not registered: {identifier}"
                ) from error

    def resolve(
        self, identifier: str, contract_version: str | None = None
    ) -> SkillContract:
        """Resolve the registered contract, requiring an exact requested version."""
        skill = self.get(identifier)
        if contract_version is None:
            return skill
        if not is_valid_contract_version(contract_version):
            raise SkillContractVersionError(
                "requested Skill contract version is malformed."
            )
        if contract_version != skill.contract_version:
            raise SkillContractVersionError(
                "requested Skill contract version is unavailable."
            )
        return skill

    def list_skills(self) -> tuple[SkillContract, ...]:
        """Return registered Skills sorted by identifier."""
        with self._lock:
            return tuple(self._skills[key] for key in sorted(self._skills))

    def search(self, query: str) -> tuple[SkillContract, ...]:
        """Search names, descriptions, and tags case-insensitively."""
        if not isinstance(query, str) or not query.strip():
            raise SkillMetadataError("search query must be a non-empty string.")
        needle = query.casefold()
        return tuple(
            contract
            for contract in self.list_skills()
            if needle in contract.name.casefold()
            or needle in contract.description.casefold()
            or any(needle in tag.casefold() for tag in contract.tags)
        )


def discover_skills(repository_root: Path) -> DiscoveryResult:
    """Discover Markdown Skill candidates under ``skills/`` without executing them.

    Only a first-line YAML-style front-matter block containing scalar ``name``
    and ``description`` fields is recognized. The function intentionally does
    not parse arbitrary YAML; optional registry metadata must be supplied
    through :meth:`SkillContract.from_mapping`.
    """
    root = Path(repository_root).resolve()
    skills_dir = root / "skills"
    if not root.is_dir():
        raise SkillMetadataError(f"repository root is not a directory: {root}")
    if not skills_dir.is_dir():
        raise SkillMetadataError(f"Skill directory does not exist: {skills_dir}")
    if not skills_dir.resolve().is_relative_to(root):
        raise SkillMetadataError("Skill directory resolves outside the repository root.")

    contracts: list[SkillContract] = []
    issues: list[DiscoveryIssue] = []
    identifiers: set[str] = set()

    def raise_walk_error(error: OSError) -> None:
        raise error

    for directory, subdirectories, filenames in os.walk(
        skills_dir, followlinks=False, onerror=raise_walk_error
    ):
        subdirectories[:] = sorted(
            name
            for name in subdirectories
            if name not in _DISCOVERY_DIRECTORIES
            and not (Path(directory) / name).is_symlink()
        )
        for filename in sorted(filenames):
            source = Path(directory) / filename
            if source.name.lower() == "readme.md" or source.suffix.lower() != ".md":
                continue
            if source.is_symlink():
                issues.append(
                    DiscoveryIssue(
                        source.relative_to(root),
                        "Skill source symlinks are not followed during discovery.",
                    )
                )
                continue
            try:
                with source.open(encoding="utf-8") as markdown:
                    first_line = markdown.readline().rstrip("\r\n")
                if first_line != "---":
                    continue
                metadata = _read_discovery_metadata(source)
                relative_path = source.relative_to(root)
                identifier = metadata["name"]
                heading = _read_first_heading(source) or identifier.replace("-", " ").title()
                contract = SkillContract.from_mapping(
                    {
                        "identifier": identifier,
                        "name": heading,
                        "description": metadata["description"],
                        "source_path": relative_path,
                    }
                )
                contract.resolve_source(root)
                if contract.identifier in identifiers:
                    raise SkillMetadataError(
                        f"duplicate Skill identifier discovered: {contract.identifier}."
                    )
                identifiers.add(contract.identifier)
                contracts.append(contract)
            except (OSError, UnicodeError, SkillMetadataError) as error:
                try:
                    display_path = source.relative_to(root)
                except ValueError:
                    display_path = source
                issues.append(DiscoveryIssue(display_path, str(error)))

    return DiscoveryResult(
        skills=tuple(sorted(contracts, key=lambda skill: skill.identifier)),
        issues=tuple(sorted(issues, key=lambda issue: (str(issue.source_path), issue.message))),
    )


def _read_discovery_metadata(source: Path) -> dict[str, str]:
    """Read only existing name/description scalar fields from front matter."""
    metadata: dict[str, str] = {}
    with source.open(encoding="utf-8") as markdown:
        next(markdown, None)
        for line_number, line in enumerate(markdown, start=2):
            value = line.rstrip("\r\n")
            if value == "---":
                break
            match = re.fullmatch(r"(name|description):(?:[ \t]+(.*))?", value)
            if not match:
                continue
            key, raw_value = match.groups()
            if key in metadata:
                raise SkillMetadataError(
                    f"duplicate '{key}' metadata at line {line_number}."
                )
            if not raw_value:
                raise SkillMetadataError(
                    f"'{key}' metadata must have a scalar value (line {line_number})."
                )
            metadata[key] = _decode_scalar(key, raw_value, line_number)
        else:
            raise SkillMetadataError("front matter has no closing '---' delimiter.")

    missing = sorted(_DISCOVERY_FIELDS.difference(metadata))
    if missing:
        raise SkillMetadataError(
            f"missing required front-matter field(s): {', '.join(missing)}."
        )
    return metadata


def _decode_scalar(key: str, value: str, line_number: int) -> str:
    """Decode the plain or double-quoted scalar forms needed by current Skills."""
    value = value.strip()
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as error:
            raise SkillMetadataError(
                f"invalid double-quoted '{key}' scalar at line {line_number}: {error.msg}."
            ) from error
        if not isinstance(decoded, str):
            raise SkillMetadataError(
                f"'{key}' must be a string scalar (line {line_number})."
            )
        value = decoded
    elif value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise SkillMetadataError(
                f"invalid single-quoted '{key}' scalar at line {line_number}."
            )
        value = value[1:-1].replace("''", "'")
    elif value.startswith(("[", "{", "|", ">", "&", "*", "!")):
        raise SkillMetadataError(
            f"unsupported non-scalar '{key}' value at line {line_number}."
        )
    elif value.casefold() in {"null", "true", "false", "~"} or re.fullmatch(
        r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?",
        value,
    ):
        raise SkillMetadataError(
            f"unsupported non-string '{key}' scalar at line {line_number}; quote it."
        )
    if not value.strip():
        raise SkillMetadataError(f"'{key}' must not be empty (line {line_number}).")
    return value


def _read_first_heading(source: Path) -> str | None:
    """Return the first Markdown H1 text, without parsing or executing content."""
    in_front_matter = False
    front_matter_closed = False
    with source.open(encoding="utf-8") as markdown:
        for line in markdown:
            stripped = line.rstrip("\r\n")
            if not front_matter_closed:
                if stripped == "---":
                    if in_front_matter:
                        front_matter_closed = True
                    else:
                        in_front_matter = True
                continue
            match = re.match(r"^#\s+(.+?)\s*#*\s*$", stripped)
            if match:
                return match.group(1).strip()
    return None

"""Provider-neutral tool contracts and explicitly registered local execution.

Tool definitions are inert metadata. Only implementations explicitly supplied
to a registered adapter can be executed, and this module has no network,
subprocess, dynamic-import, or credential-loading behavior.
"""

from __future__ import annotations

import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Callable, Mapping


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")


class ToolError(Exception):
    """Base class for actionable tool framework errors."""


class ToolContractError(ToolError, ValueError):
    """Raised for invalid tool definitions or input schemas."""


class DuplicateToolError(ToolError):
    """Raised when a tool identifier is already registered."""


class UnknownToolError(ToolError, LookupError):
    """Raised when a requested tool is not registered."""


class DuplicateAdapterError(ToolError):
    """Raised when an adapter identifier is already registered."""


class UnknownAdapterError(ToolError, LookupError):
    """Raised when a requested adapter is not registered."""


class DisabledToolError(ToolError):
    """Raised when registration or execution is attempted for a disabled tool."""


class InvalidToolInputError(ToolError, ValueError):
    """Raised for inputs that do not satisfy a tool's declared schema."""


class IncompatibleAdapterError(ToolError):
    """Raised when an adapter cannot support a registered tool contract."""


class UnsupportedToolError(ToolError):
    """Raised when execution is unavailable for a registered tool."""


class ToolRuntimeError(ToolError):
    """Raised only by callers explicitly invoking a local tool implementation."""


class InputType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    STRING_LIST = "string_list"


class ExecutionAvailability(str, Enum):
    UNAVAILABLE = "unavailable"
    AVAILABLE = "available"


class ToolStatus(str, Enum):
    SUCCEEDED = "succeeded"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    INVALID_INPUT = "invalid_input"
    ADAPTER_MISSING = "adapter_missing"
    ADAPTER_INCOMPATIBLE = "adapter_incompatible"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class InputField:
    """One named field in the deliberately small tool input schema."""

    name: str
    value_type: InputType
    required: bool = True
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _IDENTIFIER_PATTERN.fullmatch(self.name):
            raise ToolContractError(
                "input field name must be a lowercase identifier using letters, "
                "digits, dots, or hyphens."
            )
        if not isinstance(self.value_type, InputType):
            raise ToolContractError("value_type must be an InputType.")
        if not isinstance(self.required, bool):
            raise ToolContractError("required must be a boolean.")
        if not isinstance(self.description, str):
            raise ToolContractError("input description must be a string.")


@dataclass(frozen=True, slots=True)
class ToolContract:
    """Inert, validated declaration for a tool and its input requirements."""

    identifier: str
    name: str
    description: str
    input_schema: tuple[InputField, ...] = ()
    capabilities: tuple[str, ...] = ()
    adapter_id: str | None = None
    enabled: bool = True
    execution_availability: ExecutionAvailability = ExecutionAvailability.UNAVAILABLE
    allow_additional_inputs: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.identifier
        ):
            raise ToolContractError(
                "identifier must be lowercase and contain only letters, digits, "
                "dots, or hyphens."
            )
        for field_name in ("name", "description"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ToolContractError(f"{field_name} must be a non-empty string.")
        if not isinstance(self.input_schema, tuple) or any(
            not isinstance(field, InputField) for field in self.input_schema
        ):
            raise ToolContractError("input_schema must be a tuple of InputField values.")
        field_names = [field.name for field in self.input_schema]
        if len(field_names) != len(set(field_names)):
            raise ToolContractError("input_schema contains duplicate field names.")
        if not isinstance(self.capabilities, tuple) or any(
            not isinstance(capability, str) or not capability.strip()
            for capability in self.capabilities
        ):
            raise ToolContractError("capabilities must be a tuple of non-empty strings.")
        if self.adapter_id is not None and (
            not isinstance(self.adapter_id, str)
            or not _IDENTIFIER_PATTERN.fullmatch(self.adapter_id)
        ):
            raise ToolContractError("adapter_id must be a valid identifier when supplied.")
        if not isinstance(self.enabled, bool):
            raise ToolContractError("enabled must be a boolean.")
        if not isinstance(self.execution_availability, ExecutionAvailability):
            raise ToolContractError(
                "execution_availability must be an ExecutionAvailability value."
            )
        if not isinstance(self.allow_additional_inputs, bool):
            raise ToolContractError("allow_additional_inputs must be a boolean.")


class ToolRegistry:
    """Deterministic, in-memory registry for inert tool contracts."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolContract] = {}

    def register(self, contract: ToolContract) -> None:
        """Register a contract without creating or implying an implementation."""
        if not isinstance(contract, ToolContract):
            raise ToolContractError("contract must be a ToolContract.")
        if contract.identifier in self._tools:
            raise DuplicateToolError(f"tool is already registered: {contract.identifier}")
        self._tools[contract.identifier] = contract

    def get(self, identifier: str) -> ToolContract:
        """Retrieve a tool contract by exact identifier."""
        if not isinstance(identifier, str):
            raise UnknownToolError("tool identifier must be a string.")
        try:
            return self._tools[identifier]
        except KeyError as error:
            raise UnknownToolError(f"unknown tool identifier: {identifier}") from error

    def list_tools(
        self,
        *,
        enabled: bool | None = None,
        execution_availability: ExecutionAvailability | None = None,
    ) -> tuple[ToolContract, ...]:
        """List tools by identifier with optional enabled/availability filters."""
        if enabled is not None and not isinstance(enabled, bool):
            raise ToolContractError("enabled filter must be a boolean or None.")
        if execution_availability is not None and not isinstance(
            execution_availability, ExecutionAvailability
        ):
            raise ToolContractError(
                "execution_availability filter must be an ExecutionAvailability or None."
            )
        return tuple(
            tool
            for tool in (self._tools[key] for key in sorted(self._tools))
            if (enabled is None or tool.enabled is enabled)
            and (
                execution_availability is None
                or tool.execution_availability is execution_availability
            )
        )

    def search(self, query: str) -> tuple[ToolContract, ...]:
        """Case-insensitively search identifier, name, and description."""
        if not isinstance(query, str) or not query.strip():
            raise ToolContractError("search query must be a non-empty string.")
        needle = query.casefold()
        return tuple(
            tool
            for tool in self.list_tools()
            if needle in tool.identifier.casefold()
            or needle in tool.name.casefold()
            or needle in tool.description.casefold()
        )


@dataclass(frozen=True, slots=True)
class ToolInvocationRequest:
    """Explicit request to invoke a registered tool."""

    tool_identifier: str
    inputs: Mapping[str, object]
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not isinstance(self.tool_identifier, str) or not self.tool_identifier:
            raise InvalidToolInputError("tool_identifier must be a non-empty string.")
        if not isinstance(self.inputs, Mapping):
            raise InvalidToolInputError("inputs must be a mapping.")
        if not isinstance(self.request_id, str):
            raise InvalidToolInputError("request_id must be a UUID string.")
        try:
            parsed = uuid.UUID(self.request_id)
        except ValueError as error:
            raise InvalidToolInputError("request_id must be a valid UUID.") from error
        if str(parsed) != self.request_id.lower():
            raise InvalidToolInputError("request_id must use canonical UUID formatting.")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise InvalidToolInputError("created_at must be timezone-aware.")
        copied_inputs = dict(self.inputs)
        if any(not isinstance(key, str) or not key.strip() for key in copied_inputs):
            raise InvalidToolInputError("input names must be non-empty strings.")
        object.__setattr__(self, "inputs", MappingProxyType(copied_inputs))


@dataclass(frozen=True, slots=True)
class ToolExecutionResult:
    """Structured outcome of a tool invocation."""

    request_id: str
    tool_identifier: str
    status: ToolStatus
    output: Mapping[str, object] | None = None
    error_code: str | None = None
    error: ToolError | None = None
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


LocalImplementation = Callable[[Mapping[str, object]], Mapping[str, object]]


class ToolAdapter(ABC):
    """Provider-neutral interface for explicitly registered implementations."""

    @property
    @abstractmethod
    def adapter_id(self) -> str:
        """Stable identifier of this adapter implementation."""

    @property
    @abstractmethod
    def supported_tool_identifiers(self) -> tuple[str, ...]:
        """Tool identifiers this adapter declares it can implement."""

    @abstractmethod
    def supports(self, contract: ToolContract) -> bool:
        """Whether this adapter explicitly supports the complete tool contract."""

    @abstractmethod
    def execute(
        self, contract: ToolContract, inputs: Mapping[str, object]
    ) -> Mapping[str, object]:
        """Execute a supported tool and return structured output."""


class LocalToolAdapter(ToolAdapter):
    """Trusted in-process adapter; implementations are passed explicitly."""

    def __init__(
        self,
        adapter_id: str,
        implementations: Mapping[str, LocalImplementation],
    ) -> None:
        if not isinstance(adapter_id, str) or not _IDENTIFIER_PATTERN.fullmatch(adapter_id):
            raise ToolContractError("adapter_id must be a valid identifier.")
        if not isinstance(implementations, Mapping) or not implementations:
            raise ToolContractError("implementations must be a non-empty mapping.")
        copied = dict(implementations)
        if any(
            not isinstance(identifier, str)
            or not _IDENTIFIER_PATTERN.fullmatch(identifier)
            or not callable(implementation)
            for identifier, implementation in copied.items()
        ):
            raise ToolContractError(
                "implementations must map valid tool identifiers to callables."
            )
        self._adapter_id = adapter_id
        self._implementations = MappingProxyType(copied)

    @property
    def adapter_id(self) -> str:
        return self._adapter_id

    @property
    def supported_tool_identifiers(self) -> tuple[str, ...]:
        return tuple(sorted(self._implementations))

    def supports(self, contract: ToolContract) -> bool:
        return (
            contract.adapter_id == self.adapter_id
            and contract.identifier in self._implementations
        )

    def execute(
        self, contract: ToolContract, inputs: Mapping[str, object]
    ) -> Mapping[str, object]:
        if not self.supports(contract):
            raise IncompatibleAdapterError(
                f"adapter '{self.adapter_id}' does not support '{contract.identifier}'."
            )
        output = self._implementations[contract.identifier](inputs)
        if not isinstance(output, Mapping) or any(
            not isinstance(key, str) for key in output
        ):
            raise ToolRuntimeError("tool implementation returned an invalid result mapping.")
        return MappingProxyType(dict(output))


class ToolExecutor:
    """Invokes only contracts backed by explicitly registered adapter objects."""

    def __init__(self, registry: ToolRegistry) -> None:
        if not isinstance(registry, ToolRegistry):
            raise ToolContractError("registry must be a ToolRegistry.")
        self._registry = registry
        self._adapters: dict[str, ToolAdapter] = {}

    @property
    def registry(self) -> ToolRegistry:
        """The ToolRegistry whose contracts this executor resolves."""
        return self._registry

    def register_adapter(self, adapter: ToolAdapter) -> None:
        """Register a trusted adapter instance, never import one by metadata."""
        if not isinstance(adapter, ToolAdapter):
            raise ToolContractError("adapter must implement ToolAdapter.")
        supported = adapter.supported_tool_identifiers
        if not isinstance(supported, tuple) or any(
            not isinstance(identifier, str)
            or not _IDENTIFIER_PATTERN.fullmatch(identifier)
            for identifier in supported
        ):
            raise ToolContractError(
                "adapter supported_tool_identifiers must be a tuple of valid identifiers."
            )
        if adapter.adapter_id in self._adapters:
            raise DuplicateAdapterError(f"adapter is already registered: {adapter.adapter_id}")
        self._adapters[adapter.adapter_id] = adapter

    def invoke(self, request: ToolInvocationRequest) -> ToolExecutionResult:
        """Validate and invoke, returning explicit status rather than fake success."""
        if not isinstance(request, ToolInvocationRequest):
            raise InvalidToolInputError("request must be a ToolInvocationRequest.")
        contract = self._registry.get(request.tool_identifier)

        if not contract.enabled:
            return _failure(
                request,
                ToolStatus.DISABLED,
                "tool_disabled",
                DisabledToolError("tool is disabled."),
            )
        if contract.execution_availability is ExecutionAvailability.UNAVAILABLE:
            return _failure(
                request,
                ToolStatus.UNAVAILABLE,
                "execution_unavailable",
                UnsupportedToolError("tool execution is marked unavailable."),
            )
        try:
            validate_inputs(contract, request.inputs)
        except InvalidToolInputError as error:
            return _failure(request, ToolStatus.INVALID_INPUT, "invalid_input", error)

        if contract.adapter_id is None or contract.adapter_id not in self._adapters:
            return _failure(
                request,
                ToolStatus.ADAPTER_MISSING,
                "adapter_missing",
                UnknownAdapterError(
                    "no explicitly registered adapter is available for this tool."
                ),
            )
        adapter = self._adapters[contract.adapter_id]
        if (
            contract.identifier not in adapter.supported_tool_identifiers
            or not adapter.supports(contract)
        ):
            return _failure(
                request,
                ToolStatus.ADAPTER_INCOMPATIBLE,
                "adapter_incompatible",
                IncompatibleAdapterError(
                    f"adapter '{adapter.adapter_id}' does not support this tool contract."
                ),
            )

        try:
            output = adapter.execute(contract, request.inputs)
        except IncompatibleAdapterError as error:
            return _failure(
                request, ToolStatus.ADAPTER_INCOMPATIBLE, "adapter_incompatible", error
            )
        except Exception as error:
            return _failure(
                request,
                ToolStatus.FAILED,
                "runtime_failure",
                ToolRuntimeError(
                    f"local implementation failed ({type(error).__name__})."
                ),
            )
        return ToolExecutionResult(
            request_id=request.request_id,
            tool_identifier=contract.identifier,
            status=ToolStatus.SUCCEEDED,
            output=output,
        )


def validate_inputs(
    contract: ToolContract, inputs: Mapping[str, object]
) -> Mapping[str, object]:
    """Validate inputs against the supported field types and return a copy."""
    if not isinstance(contract, ToolContract):
        raise ToolContractError("contract must be a ToolContract.")
    if not isinstance(inputs, Mapping):
        raise InvalidToolInputError("inputs must be a mapping.")
    copied = dict(inputs)
    if any(not isinstance(key, str) for key in copied):
        raise InvalidToolInputError("input names must be strings.")

    declared = {field.name: field for field in contract.input_schema}
    missing = sorted(
        field.name
        for field in contract.input_schema
        if field.required and field.name not in copied
    )
    if missing:
        raise InvalidToolInputError(f"missing required input(s): {', '.join(missing)}.")
    if not contract.allow_additional_inputs:
        extra = sorted(set(copied).difference(declared))
        if extra:
            raise InvalidToolInputError(f"unsupported input(s): {', '.join(extra)}.")
    for name, value in copied.items():
        field = declared.get(name)
        if field is not None and not _matches_type(field.value_type, value):
            raise InvalidToolInputError(
                f"input '{name}' must be of type '{field.value_type.value}'."
            )
    return MappingProxyType(copied)


def text_statistics(inputs: Mapping[str, object]) -> Mapping[str, object]:
    """Return character, whitespace-word, and newline-delimited line counts."""
    text = inputs["text"]
    if not isinstance(text, str):
        raise InvalidToolInputError("input 'text' must be a string.")
    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": text.count("\n") + 1 if text else 0,
    }


def register_text_statistics(registry: ToolRegistry, executor: ToolExecutor) -> None:
    """Register the safe local text-statistics tool and its explicit adapter."""
    contract = ToolContract(
        identifier="local.text-statistics",
        name="Text statistics",
        description="Count characters, whitespace-separated words, and lines.",
        input_schema=(
            InputField("text", InputType.STRING, description="Text to count."),
        ),
        capabilities=("local", "deterministic", "text-analysis"),
        adapter_id="local.text",
        execution_availability=ExecutionAvailability.AVAILABLE,
    )
    registry.register(contract)
    executor.register_adapter(
        LocalToolAdapter("local.text", {"local.text-statistics": text_statistics})
    )


def _matches_type(value_type: InputType, value: object) -> bool:
    if value_type is InputType.STRING:
        return isinstance(value, str)
    if value_type is InputType.INTEGER:
        return isinstance(value, int) and not isinstance(value, bool)
    if value_type is InputType.BOOLEAN:
        return isinstance(value, bool)
    if value_type is InputType.STRING_LIST:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
    return False


def _failure(
    request: ToolInvocationRequest, status: ToolStatus, code: str, error: ToolError
) -> ToolExecutionResult:
    return ToolExecutionResult(
        request_id=request.request_id,
        tool_identifier=request.tool_identifier,
        status=status,
        error_code=code,
        error=error,
    )

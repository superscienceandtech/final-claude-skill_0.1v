import socket
import subprocess
import unittest
from typing import Any, cast
from unittest.mock import patch

from scripts.tool_framework import (
    DisabledToolError,
    DuplicateAdapterError,
    DuplicateToolError,
    ExecutionAvailability,
    IncompatibleAdapterError,
    InputField,
    InputType,
    InvalidToolInputError,
    LocalToolAdapter,
    ToolContract,
    ToolContractError,
    ToolExecutionResult,
    ToolExecutor,
    ToolInvocationRequest,
    ToolRegistry,
    ToolStatus,
    UnknownAdapterError,
    UnknownToolError,
    UnsupportedToolError,
    register_text_statistics,
    text_statistics,
    validate_inputs,
)


class ToolContractTests(unittest.TestCase):
    def test_validates_identifiers_fields_and_schema(self):
        contract = ToolContract(
            identifier="local.example",
            name="Example",
            description="An example tool.",
            input_schema=(InputField("value", InputType.STRING),),
        )
        self.assertEqual(contract.identifier, "local.example")
        self.assertEqual(contract.execution_availability, ExecutionAvailability.UNAVAILABLE)

    def test_rejects_invalid_identifiers_types_and_duplicate_fields(self):
        with self.assertRaisesRegex(ToolContractError, "identifier"):
            ToolContract("Bad_ID", "Name", "Description")
        with self.assertRaisesRegex(ToolContractError, "name must"):
            ToolContract("valid", " ", "Description")
        with self.assertRaisesRegex(ToolContractError, "duplicate field"):
            ToolContract(
                "valid",
                "Name",
                "Description",
                input_schema=(
                    InputField("value", InputType.STRING),
                    InputField("value", InputType.INTEGER),
                ),
            )
        with self.assertRaisesRegex(ToolContractError, "value_type"):
            InputField("value", cast(Any, "string"))

    def test_supported_schema_types_and_optional_fields(self):
        contract = ToolContract(
            "local.types",
            "Types",
            "Supported input types.",
            input_schema=(
                InputField("text", InputType.STRING),
                InputField("count", InputType.INTEGER),
                InputField("enabled", InputType.BOOLEAN),
                InputField("labels", InputType.STRING_LIST, required=False),
            ),
        )
        self.assertEqual(
            dict(validate_inputs(
                contract,
                {"text": "ok", "count": 2, "enabled": True},
            )),
            {"text": "ok", "count": 2, "enabled": True},
        )
        with self.assertRaisesRegex(InvalidToolInputError, "integer"):
            validate_inputs(
                contract,
                {"text": "ok", "count": True, "enabled": True},
            )
        with self.assertRaisesRegex(InvalidToolInputError, "string_list"):
            validate_inputs(
                contract,
                {"text": "ok", "count": 2, "enabled": True, "labels": [1]},
            )


class ToolRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.first = ToolContract("local.alpha", "Alpha", "Text helper.")
        self.second = ToolContract(
            "provider.beta",
            "Beta helper",
            "Search helper.",
            enabled=False,
            capabilities=("search",),
        )

    def test_registers_rejects_duplicates_and_reports_unknown_tools(self):
        self.registry.register(self.first)
        with self.assertRaisesRegex(DuplicateToolError, "already registered"):
            self.registry.register(self.first)
        with self.assertRaisesRegex(UnknownToolError, "unknown tool"):
            self.registry.get("missing")

    def test_lists_filters_and_searches_deterministically(self):
        self.registry.register(self.second)
        self.registry.register(self.first)
        self.assertEqual(
            [tool.identifier for tool in self.registry.list_tools()],
            ["local.alpha", "provider.beta"],
        )
        self.assertEqual(
            [tool.identifier for tool in self.registry.list_tools(enabled=False)],
            ["provider.beta"],
        )
        self.assertEqual(
            [tool.identifier for tool in self.registry.search("HELPER")],
            ["local.alpha", "provider.beta"],
        )
        self.assertEqual(self.registry.search("missing"), ())


class ToolInvocationTests(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.executor = ToolExecutor(self.registry)

    def test_contract_registration_alone_does_not_enable_execution(self):
        contract = ToolContract(
            identifier="local.stats",
            name="Stats",
            description="Count text.",
            input_schema=(InputField("text", InputType.STRING),),
            adapter_id="local.text",
            execution_availability=ExecutionAvailability.AVAILABLE,
        )
        self.registry.register(contract)
        result = self.executor.invoke(
            ToolInvocationRequest("local.stats", {"text": "hello"})
        )

        self.assertEqual(result.status, ToolStatus.ADAPTER_MISSING)
        self.assertIsNone(result.output)
        self.assertEqual(result.error_code, "adapter_missing")
        self.assertIsInstance(result.error, UnknownAdapterError)

    def test_unavailable_and_disabled_statuses_are_explicit(self):
        unavailable = ToolContract("local.offline", "Offline", "No implementation.")
        disabled = ToolContract(
            "local.disabled",
            "Disabled",
            "Disabled tool.",
            enabled=False,
            execution_availability=ExecutionAvailability.AVAILABLE,
            adapter_id="local.text",
        )
        self.registry.register(unavailable)
        self.registry.register(disabled)

        unavailable_result = self.executor.invoke(
            ToolInvocationRequest("local.offline", {})
        )
        disabled_result = self.executor.invoke(
            ToolInvocationRequest("local.disabled", {})
        )

        self.assertEqual(unavailable_result.status, ToolStatus.UNAVAILABLE)
        self.assertEqual(disabled_result.status, ToolStatus.DISABLED)
        self.assertIsInstance(unavailable_result.error, UnsupportedToolError)
        self.assertIsInstance(disabled_result.error, DisabledToolError)

    def test_validates_schema_before_execution(self):
        register_text_statistics(self.registry, self.executor)
        missing = self.executor.invoke(ToolInvocationRequest("local.text-statistics", {}))
        wrong_type = self.executor.invoke(
            ToolInvocationRequest("local.text-statistics", {"text": 42})
        )
        extra = self.executor.invoke(
            ToolInvocationRequest(
                "local.text-statistics", {"text": "hi", "code": "ignore"}
            )
        )

        self.assertEqual(missing.status, ToolStatus.INVALID_INPUT)
        self.assertIn("missing required", str(missing.error))
        self.assertEqual(wrong_type.status, ToolStatus.INVALID_INPUT)
        self.assertIn("string", str(wrong_type.error))
        self.assertEqual(extra.status, ToolStatus.INVALID_INPUT)
        self.assertIn("unsupported input", str(extra.error))

    def test_runs_harmless_local_text_statistics(self):
        register_text_statistics(self.registry, self.executor)
        request = ToolInvocationRequest(
            "local.text-statistics",
            {"text": "Hello, world!\nSecond line."},
        )
        result = self.executor.invoke(request)

        self.assertIsInstance(result, ToolExecutionResult)
        self.assertEqual(result.status, ToolStatus.SUCCEEDED)
        self.assertEqual(result.request_id, request.request_id)
        self.assertEqual(result.tool_identifier, "local.text-statistics")
        self.assertEqual(
            dict(result.output),
            {"characters": 26, "words": 4, "lines": 2},
        )
        self.assertIsNotNone(result.completed_at.tzinfo)

    def test_adapter_compatibility_and_duplicate_adapter_errors(self):
        self.registry.register(
            ToolContract(
                "local.stats",
                "Stats",
                "Count text.",
                input_schema=(InputField("text", InputType.STRING),),
                adapter_id="local.text",
                execution_availability=ExecutionAvailability.AVAILABLE,
            )
        )
        incompatible = LocalToolAdapter("local.other", {"local.stats": text_statistics})
        self.assertEqual(incompatible.supported_tool_identifiers, ("local.stats",))
        self.executor.register_adapter(incompatible)
        result = self.executor.invoke(
            ToolInvocationRequest("local.stats", {"text": "ok"})
        )
        self.assertEqual(result.status, ToolStatus.ADAPTER_MISSING)

        with self.assertRaisesRegex(DuplicateAdapterError, "already registered"):
            self.executor.register_adapter(incompatible)

        compatible_executor = ToolExecutor(self.registry)
        compatible_executor.register_adapter(
            LocalToolAdapter("local.text", {"another.tool": text_statistics})
        )
        incompatible_result = compatible_executor.invoke(
            ToolInvocationRequest("local.stats", {"text": "ok"})
        )
        self.assertEqual(incompatible_result.status, ToolStatus.ADAPTER_INCOMPATIBLE)
        self.assertIsInstance(incompatible_result.error, IncompatibleAdapterError)

    def test_runtime_failure_is_structured_and_does_not_leak_exception_text(self):
        def failing_tool(_inputs):
            raise RuntimeError("secret token must not be exposed")

        self.registry.register(
            ToolContract(
                "local.failure",
                "Failure test",
                "Raises internally.",
                input_schema=(InputField("text", InputType.STRING),),
                adapter_id="local.failure",
                execution_availability=ExecutionAvailability.AVAILABLE,
            )
        )
        self.executor.register_adapter(
            LocalToolAdapter("local.failure", {"local.failure": failing_tool})
        )

        result = self.executor.invoke(
            ToolInvocationRequest("local.failure", {"text": "safe"})
        )

        self.assertEqual(result.status, ToolStatus.FAILED)
        self.assertEqual(result.error_code, "runtime_failure")
        self.assertNotIn("secret token", str(result.error))

    def test_no_shell_or_network_access_is_needed(self):
        register_text_statistics(self.registry, self.executor)
        with (
            patch.object(subprocess, "Popen", side_effect=AssertionError("shell used")) as process,
            patch.object(socket, "create_connection", side_effect=AssertionError("network used")) as network,
        ):
            result = self.executor.invoke(
                ToolInvocationRequest("local.text-statistics", {"text": "offline"})
            )

        self.assertEqual(result.status, ToolStatus.SUCCEEDED)
        process.assert_not_called()
        network.assert_not_called()

    def test_tool_invocation_request_validates_and_copies_inputs(self):
        source = {"text": "original"}
        request = ToolInvocationRequest("local.text-statistics", source)
        source["text"] = "mutated"
        self.assertEqual(request.inputs["text"], "original")
        with self.assertRaisesRegex(InvalidToolInputError, "mapping"):
            ToolInvocationRequest("local.tool", cast(Any, "invalid"))

    def test_text_statistics_empty_text_is_deterministic(self):
        self.assertEqual(
            text_statistics({"text": ""}),
            {"characters": 0, "words": 0, "lines": 0},
        )


if __name__ == "__main__":
    unittest.main()

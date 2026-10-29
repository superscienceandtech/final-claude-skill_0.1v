"""JSON entry point for the explicitly authorized local source-editing pipeline.

This command applies caller-supplied file contents. It does not generate edits
or provide an operating-system security boundary.
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
from pathlib import Path
from typing import TextIO

from scripts.skill_pipeline import (
    InvocationRequest,
    SkillExecutionResult,
    SkillExecutionStatus,
)
from scripts.source_editing_workflow import (
    SourceEditOperation,
    SourceEditingRequest,
    SourceWriteAuthorization,
    create_source_editing_pipeline,
)
from scripts.tool_workflow import WorkflowCancellationToken
from scripts.validation_adapter import ValidationCommand, ValidationOperation


_MAX_REQUEST_BYTES = 12 * 1024 * 1024
_REQUEST_KEYS = {"objective", "operations", "request_id"}
_OPERATION_KEYS = {"path", "content", "expected_sha256"}


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON object contains duplicate keys.")
        result[key] = value
    return result


def _parse_request(
    payload: object,
    cancellation_token: WorkflowCancellationToken,
) -> SourceEditingRequest:
    if not isinstance(payload, dict) or set(payload).difference(_REQUEST_KEYS):
        raise ValueError("request must be an object with only supported fields.")
    if not {"objective", "operations"}.issubset(payload):
        raise ValueError("request is missing required fields.")
    operations_data = payload["operations"]
    if not isinstance(operations_data, list):
        raise ValueError("operations must be an array.")

    operations: list[SourceEditOperation] = []
    for item in operations_data:
        if not isinstance(item, dict) or set(item) != _OPERATION_KEYS:
            raise ValueError("each operation must contain exactly the supported fields.")
        operations.append(
            SourceEditOperation(
                path=item["path"],
                content=item["content"],
                expected_sha256=item["expected_sha256"],
            )
        )

    request_id = payload.get("request_id", "")
    return SourceEditingRequest(
        objective=payload["objective"],
        operations=tuple(operations),
        validation_commands=(
            ValidationCommand(
                identifier="git-diff-check",
                operation=ValidationOperation.GIT_DIFF_CHECK,
                targets=tuple(operation.path for operation in operations),
            ),
        ),
        request_id=request_id,
        cancellation_token=cancellation_token,
    )


def _result_document(result: SkillExecutionResult) -> dict[str, object]:
    document: dict[str, object] = {
        "request_id": result.request_id,
        "skill_identifier": result.skill_identifier,
        "status": result.status.value,
        "error_code": result.error_code,
    }
    if result.output is not None:
        document["output"] = dict(result.output)
    if result.failure_details is not None:
        document["failure_details"] = dict(result.failure_details)
    return document


def main(
    argv: list[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Apply caller-supplied file contents through the implementation "
            "Skill pipeline and emit structured edit/validation results."
        )
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument(
        "--allow-write",
        action="append",
        required=True,
        metavar="REPOSITORY_RELATIVE_PATH",
        help="exact path granted for writing; repeatable",
    )
    parser.add_argument(
        "--allow-read",
        action="append",
        default=[],
        metavar="REPOSITORY_RELATIVE_PATH",
        help="exact path granted for reading and change observation; repeatable",
    )
    args = parser.parse_args(argv)
    input_stream = sys.stdin if stdin is None else stdin
    output_stream = sys.stdout if stdout is None else stdout
    error_stream = sys.stderr if stderr is None else stderr

    try:
        cancellation_token = WorkflowCancellationToken()
        raw_request = input_stream.read(_MAX_REQUEST_BYTES + 1)
        if len(raw_request.encode("utf-8")) > _MAX_REQUEST_BYTES:
            raise ValueError("request exceeds the maximum JSON input size.")
        payload = json.loads(raw_request, object_pairs_hook=_reject_duplicate_keys)
        request = _parse_request(payload, cancellation_token)
        authorization = SourceWriteAuthorization(
            args.repository_root,
            tuple(args.allow_write),
            tuple(args.allow_read),
        )
        invocation = InvocationRequest(
            skill_identifier="implementation",
            task=request.objective,
            inputs={"source_edit_request": request},
            request_id=request.request_id,
        )
    except (UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        error_code = (
            "invalid_json"
            if isinstance(error, json.JSONDecodeError)
            else "invalid_request"
        )
        print(
            json.dumps(
                {"status": "invalid_request", "error_code": error_code},
                sort_keys=True,
            ),
            file=output_stream,
        )
        print(error_code, file=error_stream)
        return 2

    try:
        pipeline = create_source_editing_pipeline(
            args.repository_root,
            authorization,
        )
    except (OSError, ValueError):
        error_code = "pipeline_unavailable"
        print(
            json.dumps(
                {"status": "failed", "error_code": error_code},
                sort_keys=True,
            ),
            file=output_stream,
        )
        print(error_code, file=error_stream)
        return 1

    previous_sigint_handler = signal.signal(
        signal.SIGINT,
        lambda _signum, _frame: cancellation_token.request_cancel(),
    )
    try:
        result = pipeline.invoke(invocation)
    finally:
        signal.signal(signal.SIGINT, previous_sigint_handler)
    document = _result_document(result)
    print(json.dumps(document, ensure_ascii=False, sort_keys=True), file=output_stream)
    return 0 if result.status is SkillExecutionStatus.SUCCEEDED else 1


if __name__ == "__main__":
    raise SystemExit(main())

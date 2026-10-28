#!/usr/bin/env python3
"""Dependency-free structural validator for the canonical repository-audit Skill."""

from __future__ import annotations

import json
import os
import re
import stat
import sys
import unicodedata
from pathlib import Path, PureWindowsPath


VERSION = "1.0"
CANONICAL_SKILL_PATH = "skills/repository-audit/SKILL.md"
MAX_FILE_BYTES = 64 * 1024
HAS_DIR_FD_OPEN = os.open in os.supports_dir_fd
REQUIRED_HEADINGS = (
    "Purpose",
    "Inputs",
    "Repository boundary",
    "Allowed operations",
    "Security and content policy",
    "Output contract",
    "Failure behavior",
    "Testing status",
)
EXPECTED_NAME = "repository-audit"
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*): (.+)$")
HEADING_RE = re.compile(r"^ {0,3}#{2,3}[ \t]+([^#].*?)(?: +#+)?[ \t]*$")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")


def emit(status: str, errors: list[dict[str, object]], exit_code: int) -> int:
    errors.sort(key=lambda error: (str(error["code"]), error["line"] is not None, error["line"] or 0))
    sys.stdout.write(
        json.dumps(
            {"validator_version": VERSION, "status": status, "errors": errors},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )
    return exit_code


def error(code: str, line: int | None = None) -> dict[str, object]:
    return {"code": code, "line": line}


def parse_args(argv: list[str]) -> tuple[Path | None, str | None, list[dict[str, object]]]:
    values: dict[str, str] = {}
    errors: list[dict[str, object]] = []
    index = 0
    expected = {"--repo-root", "--skill-path"}
    while index < len(argv):
        key = argv[index]
        if key not in expected:
            errors.append(error("ARGUMENT_UNKNOWN"))
            index += 1
            continue
        if key in values:
            errors.append(error("ARGUMENT_DUPLICATE"))
            index += 1
            continue
        if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
            errors.append(error("ARGUMENT_REQUIRED"))
            index += 1
            continue
        values[key] = argv[index + 1]
        index += 2

    for required in ("--repo-root", "--skill-path"):
        if required not in values and not any(e["code"] == "ARGUMENT_REQUIRED" for e in errors):
            errors.append(error("ARGUMENT_REQUIRED"))
    if errors:
        # Invocation failures have a single stable diagnostic by contract.
        return None, None, [errors[0]]
    root_text = values["--repo-root"]
    # Reject Windows network/device roots before Path.resolve() can inspect them.
    # PureWindowsPath parsing is lexical and performs no filesystem access.
    if PureWindowsPath(root_text).anchor.startswith("\\\\"):
        return None, None, [error("ROOT_INVALID")]
    if not Path(root_text).is_absolute():
        return None, None, [error("ROOT_INVALID")]
    if values["--skill-path"] != CANONICAL_SKILL_PATH:
        return None, None, [error("SKILL_PATH_INVALID")]
    try:
        root = Path(root_text).resolve(strict=True)
    except (OSError, RuntimeError):
        return None, None, [error("ROOT_INVALID")]
    if not root.is_dir():
        return None, None, [error("ROOT_INVALID")]
    return root, values["--skill-path"], []


def read_skill(root: Path, relative: str) -> tuple[bytes | None, list[dict[str, object]]]:
    if os.name != "posix":
        # Do not read through path-based APIs when component-wise no-follow opens are unavailable.
        return None, [error("SKILL_PATH_INVALID")]
    parts = relative.split("/")
    try:
        no_follow = getattr(os, "O_NOFOLLOW", None)
        directory = getattr(os, "O_DIRECTORY", None)
        non_blocking = getattr(os, "O_NONBLOCK", None)
        if (
            no_follow is None
            or directory is None
            or non_blocking is None
            or not HAS_DIR_FD_OPEN
        ):
            return None, [error("SKILL_PATH_INVALID")]

        directory_flags = os.O_RDONLY | directory | no_follow
        if not root.is_absolute():
            return None, [error("SKILL_PATH_INVALID")]
        directory_fd = os.open(root.anchor, directory_flags)
        file_fd: int | None = None
        try:
            for part in (*root.parts[1:], *parts[:-1]):
                next_fd = os.open(part, directory_flags, dir_fd=directory_fd)
                os.close(directory_fd)
                directory_fd = next_fd
            file_fd = os.open(
                parts[-1],
                os.O_RDONLY | no_follow | non_blocking,
                dir_fd=directory_fd,
            )
        finally:
            os.close(directory_fd)

        try:
            with os.fdopen(file_fd, "rb") as stream:
                file_fd = None
                metadata = os.fstat(stream.fileno())
                if not stat.S_ISREG(metadata.st_mode):
                    return None, [error("SKILL_FILE_MISSING")]
                if metadata.st_size > MAX_FILE_BYTES:
                    return None, [error("SKILL_FILE_TOO_LARGE")]
                raw = stream.read(MAX_FILE_BYTES)
                if os.fstat(stream.fileno()).st_size > MAX_FILE_BYTES:
                    return None, [error("SKILL_FILE_TOO_LARGE")]
        finally:
            if file_fd is not None:
                os.close(file_fd)
    except FileNotFoundError:
        return None, [error("SKILL_FILE_MISSING")]
    except (OSError, RuntimeError, ValueError):
        return None, [error("SKILL_PATH_INVALID")]
    if len(raw) > MAX_FILE_BYTES:
        return None, [error("SKILL_FILE_TOO_LARGE")]
    return raw, []


def parse_frontmatter(text: str) -> tuple[dict[str, object], list[dict[str, object]], int]:
    normalized = text.replace("\r\n", "\n")
    if "\r" in normalized:
        return {}, [error("FRONTMATTER_INVALID", 1)], 0
    lines = normalized.splitlines()
    if not lines or lines[0] != "---":
        return {}, [error("FRONTMATTER_INVALID", 1)], 0
    try:
        close = lines.index("---", 1)
    except ValueError:
        return {}, [error("FRONTMATTER_INVALID", 1)], 0

    metadata: dict[str, object] = {}
    errors: list[dict[str, object]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(lines[1:close], start=2):
        match = KEY_RE.fullmatch(line)
        if not match:
            errors.append(error("FRONTMATTER_INVALID", line_number))
            continue
        key, scalar = match.groups()
        if key in seen:
            errors.append(error("METADATA_DUPLICATE", line_number))
            continue
        seen.add(key)
        if key not in {"name", "description", "version"}:
            errors.append(error("METADATA_UNKNOWN", line_number))
            continue
        if not (scalar.startswith('"') and scalar.endswith('"')):
            errors.append(error("METADATA_TYPE_INVALID", line_number))
            continue
        try:
            value = json.loads(scalar)
        except (json.JSONDecodeError, TypeError):
            errors.append(error("FRONTMATTER_INVALID", line_number))
            continue
        if not isinstance(value, str):
            errors.append(error("METADATA_TYPE_INVALID", line_number))
            continue
        metadata[key] = value

    for required in ("name", "description", "version"):
        if required not in seen:
            errors.append(error("METADATA_MISSING", None))

    name = metadata.get("name")
    if isinstance(name, str) and name != EXPECTED_NAME:
        errors.append(error("METADATA_VALUE_INVALID", next((n for n, row in enumerate(lines, 1) if row.startswith("name:")), None)))
    description = metadata.get("description")
    if isinstance(description, str) and (
        not 1 <= len(description) <= 200
        or any(unicodedata.category(char) == "Cc" or 0xD800 <= ord(char) <= 0xDFFF for char in description)
    ):
        errors.append(error("METADATA_VALUE_INVALID", next((n for n, row in enumerate(lines, 1) if row.startswith("description:")), None)))
    version = metadata.get("version")
    if isinstance(version, str) and not SEMVER.fullmatch(version):
        errors.append(error("METADATA_VALUE_INVALID", next((n for n, row in enumerate(lines, 1) if row.startswith("version:")), None)))
    return metadata, errors, close + 1


def validate(raw: bytes) -> list[dict[str, object]]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return [error("SKILL_UTF8_INVALID")]
    _, errors, body_start = parse_frontmatter(text)
    if errors and any(item["code"] == "FRONTMATTER_INVALID" for item in errors):
        return errors
    lines = text.replace("\r\n", "\n").splitlines()
    body = lines[body_start:]
    found: set[str] = set()
    fence: str | None = None
    in_html_comment = False
    for line in body:
        if fence is not None:
            close = FENCE_CLOSE_RE.fullmatch(line)
            if close and close.group(1)[0] == fence[0] and len(close.group(1)) >= len(fence):
                fence = None
            continue
        if in_html_comment:
            if "-->" in line:
                in_html_comment = False
            continue
        if "<!--" in line:
            in_html_comment = "-->" not in line
            continue
        opening = FENCE_OPEN_RE.fullmatch(line)
        if opening and (opening.group(1)[0] != "`" or "`" not in opening.group(2)):
            fence = opening.group(1)
            continue
        match = HEADING_RE.fullmatch(line)
        if match:
            found.add(match.group(1).strip())
    for heading in REQUIRED_HEADINGS:
        if heading not in found:
            errors.append(error("HEADING_MISSING", None))
    return errors


def main(argv: list[str]) -> int:
    root, relative, argument_errors = parse_args(argv)
    if argument_errors:
        return emit("ERROR", argument_errors, 2)
    assert root is not None and relative is not None
    raw, read_errors = read_skill(root, relative)
    if read_errors:
        return emit("ERROR", read_errors, 2)
    assert raw is not None
    errors = validate(raw)
    if errors:
        return emit("INVALID", errors, 1)
    return emit("VALID", [], 0)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception:
        raise SystemExit(emit("ERROR", [error("VALIDATOR_INTERNAL_ERROR")], 2))

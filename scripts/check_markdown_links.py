#!/usr/bin/env python3
"""Check inline relative Markdown links and image targets in a repository."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


LINK_PATTERN = re.compile(
    r"!? \[[^\]]*\] \(\s*(?:<([^>\n]*)>|([^\s)]+))(?:\s+[^)]*)?\s*\)",
    re.VERBOSE,
)
FENCE_PATTERN = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def markdown_targets(path: Path) -> list[tuple[int, str]]:
    """Return inline link/image targets outside fenced code blocks."""
    targets: list[tuple[int, str]] = []
    fence_char: str | None = None
    fence_length = 0

    with path.open(encoding="utf-8") as markdown:
        for line_number, line in enumerate(markdown, start=1):
            fence = FENCE_PATTERN.match(line)
            if fence:
                marker = fence.group(1)
                if fence_char is None:
                    fence_char = marker[0]
                    fence_length = len(marker)
                elif marker[0] == fence_char and len(marker) >= fence_length:
                    fence_char = None
                continue
            if fence_char is not None:
                continue

            without_inline_code = re.sub(r"`+[^`]*`+", "", line)
            for match in LINK_PATTERN.finditer(without_inline_code):
                target = match.group(1) or match.group(2)
                if target:
                    targets.append((line_number, target))

    return targets


def unresolved_links(root: Path) -> list[tuple[Path, int, str]]:
    """Return relative inline links whose local target does not exist."""
    unresolved: list[tuple[Path, int, str]] = []

    def raise_walk_error(error: OSError) -> None:
        raise error

    for directory, subdirectories, filenames in os.walk(root, onerror=raise_walk_error):
        subdirectories[:] = sorted(name for name in subdirectories if name != ".git")
        for filename in sorted(filenames):
            source = Path(directory) / filename
            if source.suffix.lower() != ".md":
                continue

            for line_number, target in markdown_targets(source):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                local_path = Path(unquote(parsed.path))
                if not local_path.is_absolute() and not (source.parent / local_path).exists():
                    unresolved.append((source.relative_to(root), line_number, target))

    return unresolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check inline relative Markdown links and image targets."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root to scan (defaults to this script's repository)",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {args.root}")

    try:
        findings = unresolved_links(root)
    except (OSError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if findings:
        for source, line_number, target in findings:
            print(f"{source}:{line_number}: unresolved relative link: {target}")
        return 1

    print(f"PASS: no unresolved inline relative Markdown links under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

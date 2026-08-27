#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENV_KEY = re.compile(r"^[A-Z_][A-Z0-9_]*$")
ARGV_TOKEN = re.compile(r"^[A-Za-z0-9_./:-]+$")
JSON_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def frontmatter(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return []
    try:
        end = lines.index("---", 1)
    except ValueError:
        return []
    return lines[1:end]


def pieverse_metadata(lines: list[str]) -> list[str]:
    try:
        metadata_start = lines.index("metadata:") + 1
    except ValueError:
        return []

    metadata_end = len(lines)
    for index in range(metadata_start, len(lines)):
        line = lines[index]
        if line and not line.startswith("  "):
            metadata_end = index
            break

    try:
        pieverse_start = lines.index("  pieverse:", metadata_start, metadata_end) + 1
    except ValueError:
        return []

    pieverse_end = metadata_end
    for index in range(pieverse_start, metadata_end):
        line = lines[index]
        if line.startswith("  ") and not line.startswith("    "):
            pieverse_end = index
            break
    return lines[pieverse_start:pieverse_end]


def validate(path: Path, lines: list[str]) -> list[str]:
    if "    marketSearch: true" not in lines:
        return []

    pieverse = pieverse_metadata(lines)
    if "    marketSearch: true" not in pieverse:
        return [f"{path}: marketSearch must be nested under metadata.pieverse"]

    errors: list[str] = []
    try:
        start = pieverse.index("    tradeReady:") + 1
    except ValueError:
        return [f"{path}: marketSearch venue is missing metadata.pieverse.tradeReady"]

    env_groups = 0
    probe = False
    in_env = False
    in_probe = False
    in_json_equals = False
    probe_argv = False
    probe_json_conditions = 0
    for line in pieverse[start:]:
        if line and not line.startswith("      "):
            break
        if line == "      env:":
            in_env = True
            in_probe = False
            in_json_equals = False
            continue
        if line.startswith("      integration:"):
            errors.append(
                f"{path}: tradeReady.integration is unsupported; declare a local probe"
            )
            continue
        if in_env and line.startswith("        - [") and line.endswith("]"):
            keys = [key.strip() for key in line[11:-1].split(",")]
            if not keys or any(not ENV_KEY.fullmatch(key) for key in keys):
                errors.append(f"{path}: invalid tradeReady.env credential set {line.strip()!r}")
            else:
                env_groups += 1
            continue
        if line == "      probe:":
            in_env = False
            in_probe = True
            in_json_equals = False
            probe = True
            continue
        if in_probe and line.startswith("        argv: [") and line.endswith("]"):
            argv = [token.strip() for token in line[15:-1].split(",")]
            if not argv or any(not ARGV_TOKEN.fullmatch(token) for token in argv):
                errors.append(f"{path}: invalid tradeReady.probe argv {line.strip()!r}")
            else:
                probe_argv = True
            continue
        if in_probe and line == "        jsonEquals:":
            in_json_equals = True
            continue
        if in_probe and in_json_equals and line.startswith("          "):
            key, separator, value = line.strip().partition(":")
            if not separator or not JSON_KEY.fullmatch(key) or not value.strip():
                errors.append(f"{path}: invalid tradeReady.probe jsonEquals condition")
            else:
                probe_json_conditions += 1

    if probe and (not probe_argv or probe_json_conditions == 0):
        errors.append(f"{path}: tradeReady.probe requires argv and jsonEquals")
    if env_groups == 0 and not probe:
        errors.append(f"{path}: tradeReady must declare env or probe")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted(ROOT.glob("*/SKILL.md")):
        errors.extend(validate(path.relative_to(ROOT), frontmatter(path)))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Market-search metadata check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

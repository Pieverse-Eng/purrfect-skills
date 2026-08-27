#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENV_KEY = re.compile(r"^[A-Z_][A-Z0-9_]*$")
INTEGRATION_KEY = re.compile(r"^[a-z][A-Za-z0-9]*$")


def frontmatter(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return []
    try:
        end = lines.index("---", 1)
    except ValueError:
        return []
    return lines[1:end]


def validate(path: Path, lines: list[str]) -> list[str]:
    if "    marketSearch: true" not in lines:
        return []

    errors: list[str] = []
    try:
        start = lines.index("    tradeReady:") + 1
    except ValueError:
        return [f"{path}: marketSearch venue is missing metadata.pieverse.tradeReady"]

    env_groups = 0
    integration = False
    in_env = False
    for line in lines[start:]:
        if line and not line.startswith("      "):
            break
        if line == "      env:":
            in_env = True
            continue
        if line.startswith("      integration:"):
            in_env = False
            value = line.split(":", 1)[1].strip()
            if not INTEGRATION_KEY.fullmatch(value):
                errors.append(f"{path}: invalid tradeReady.integration {value!r}")
            else:
                integration = True
            continue
        if in_env and line.startswith("        - [") and line.endswith("]"):
            keys = [key.strip() for key in line[11:-1].split(",")]
            if not keys or any(not ENV_KEY.fullmatch(key) for key in keys):
                errors.append(f"{path}: invalid tradeReady.env credential set {line.strip()!r}")
            else:
                env_groups += 1

    if env_groups == 0 and not integration:
        errors.append(f"{path}: tradeReady must declare env or integration")
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

#!/usr/bin/env python3

from __future__ import annotations

import re
import sys


FORBIDDEN_INTERNAL_TERMS = (
    re.compile(r"\bapi\b", re.IGNORECASE),
    re.compile(r"\bendpoint\b", re.IGNORECASE),
    re.compile(r"\bdocument\s*status\b", re.IGNORECASE),
    re.compile(r"\bdegraded\b", re.IGNORECASE),
    re.compile(r"\breason\s*codes?\b", re.IGNORECASE),
    re.compile(r"\breceipts?\b", re.IGNORECASE),
    re.compile(r"\bfunnels?\b", re.IGNORECASE),
    re.compile(r"\bbacklogs?\b", re.IGNORECASE),
    re.compile(r"\bread[- ]only\b", re.IGNORECASE),
    re.compile(
        r"\b(?:geckoterminal|dexpaprika|dexscreener|dune|vfat|barker)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\brh-lp[a-z0-9.\-]*\b", re.IGNORECASE),
    re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b"),
)

PROCESS_NARRATION = re.compile(
    r"\b(?:i(?:['’]ll|['’]m\s+going\s+to|\s+will|\s+am\s+going\s+to)|let\s+me)\b"
    r"[^.\n]{0,160}\b(?:pull|fetch|read|check|query|call|inspect|load|use)(?:s|ed|ing)?\b",
    re.IGNORECASE,
)


def validate_ordinary_answer(answer: str) -> list[str]:
    errors: list[str] = []
    if not answer.strip():
        return ["answer is empty"]

    if PROCESS_NARRATION.search(answer):
        errors.append("answer narrates a command, tool, or data-fetching step")

    matched_terms = sorted(
        {
            match.group(0)
            for pattern in FORBIDDEN_INTERNAL_TERMS
            for match in pattern.finditer(answer)
        },
        key=str.casefold,
    )
    if matched_terms:
        errors.append(f"answer exposes internal vocabulary: {', '.join(matched_terms)}")

    return errors


def main() -> int:
    answer = sys.stdin.read()
    errors = validate_ordinary_answer(answer)
    if errors:
        for error in errors:
            print(f"answer_guard: {error}", file=sys.stderr)
        return 2

    sys.stdout.write(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

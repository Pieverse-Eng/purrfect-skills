#!/usr/bin/env python3
"""Validate HR-review capture continuity and optionally emit the next state."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
CONFIDENCE = {"high", "medium", "low", "insufficient"}
STATE_KEYS = {
    "schema_version",
    "roster",
    "conditional_agents",
    "required_sources",
    "publication_target",
    "next_capture_start_utc",
    "next_weekly_start_utc",
    "last_completed_capture",
    "last_weekly_report",
}
RECEIPT_KEYS = {
    "schema_version",
    "mode",
    "start_utc",
    "end_utc",
    "evidence_artifact",
    "evidence_sha256",
    "sources",
    "agents",
    "weekly_report",
}


class ValidationError(ValueError):
    pass


def object_at(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return value


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = expected - value.keys()
    extra = value.keys() - expected
    if missing or extra:
        raise ValidationError(
            f"{label} keys mismatch; missing={sorted(missing)}, extra={sorted(extra)}"
        )


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def timestamp(value: Any, label: str) -> datetime:
    value = text(value, label)
    if not TIMESTAMP_RE.fullmatch(value):
        raise ValidationError(f"{label} must use canonical YYYY-MM-DDTHH:MM:SSZ")
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    return parsed


def unique_names(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValidationError(f"{label} must be an array")
    names = [text(item, f"{label}[]") for item in value]
    if len(names) != len(set(names)):
        raise ValidationError(f"{label} contains duplicates")
    return names


def validate_state(raw: Any) -> dict[str, Any]:
    state = object_at(raw, "state")
    exact_keys(state, STATE_KEYS, "state")
    if state["schema_version"] != 1:
        raise ValidationError("state.schema_version must be 1")
    roster = unique_names(state["roster"], "state.roster")
    conditional = unique_names(state["conditional_agents"], "state.conditional_agents")
    required_sources = unique_names(state["required_sources"], "state.required_sources")
    if not roster:
        raise ValidationError("state.roster must not be empty")
    if not required_sources:
        raise ValidationError("state.required_sources must not be empty")
    overlap = set(roster) & set(conditional)
    if overlap:
        raise ValidationError(f"fixed and conditional rosters overlap: {sorted(overlap)}")
    text(state["publication_target"], "state.publication_target")
    next_capture = timestamp(
        state["next_capture_start_utc"], "state.next_capture_start_utc"
    )
    next_weekly = timestamp(
        state["next_weekly_start_utc"], "state.next_weekly_start_utc"
    )
    if next_weekly > next_capture:
        raise ValidationError("next_weekly_start_utc cannot exceed next_capture_start_utc")

    last_capture = state["last_completed_capture"]
    if last_capture is not None:
        last_capture = object_at(last_capture, "state.last_completed_capture")
        exact_keys(
            last_capture,
            {"start_utc", "end_utc", "receipt_path", "receipt_sha256"},
            "state.last_completed_capture",
        )
        start = timestamp(
            last_capture["start_utc"], "state.last_completed_capture.start_utc"
        )
        end = timestamp(
            last_capture["end_utc"], "state.last_completed_capture.end_utc"
        )
        if start >= end:
            raise ValidationError("last_completed_capture interval is invalid")
        if last_capture["end_utc"] != state["next_capture_start_utc"]:
            raise ValidationError("last_completed_capture does not meet capture watermark")
        text(last_capture["receipt_path"], "state.last_completed_capture.receipt_path")
        digest = text(
            last_capture["receipt_sha256"],
            "state.last_completed_capture.receipt_sha256",
        )
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValidationError("last capture receipt_sha256 must be lowercase SHA-256")

    last_weekly = state["last_weekly_report"]
    if last_weekly is not None:
        last_weekly = object_at(last_weekly, "state.last_weekly_report")
        exact_keys(
            last_weekly,
            {"start_utc", "end_utc", "target", "access_boundary", "message_id"},
            "state.last_weekly_report",
        )
        start = timestamp(last_weekly["start_utc"], "state.last_weekly_report.start_utc")
        end = timestamp(last_weekly["end_utc"], "state.last_weekly_report.end_utc")
        if start >= end:
            raise ValidationError("last_weekly_report interval is invalid")
        if last_weekly["end_utc"] != state["next_weekly_start_utc"]:
            raise ValidationError("last_weekly_report does not meet weekly watermark")
        if last_weekly["target"] != state["publication_target"]:
            raise ValidationError("last_weekly_report target differs from configured target")
        text(last_weekly["access_boundary"], "state.last_weekly_report.access_boundary")
        message_id = text(last_weekly["message_id"], "state.last_weekly_report.message_id")
        if message_id == "PENDING":
            raise ValidationError("state cannot retain a pending weekly publication")
    return state


def validate_sources(
    raw: Any, state: dict[str, Any], allow_partial_coverage: bool
) -> bool:
    if not isinstance(raw, list) or not raw:
        raise ValidationError("receipt.sources must be a non-empty array")
    seen_ids: set[str] = set()
    required_status: dict[str, str] = {}
    for index, item in enumerate(raw):
        source = object_at(item, f"receipt.sources[{index}]")
        exact_keys(
            source,
            {
                "source_id",
                "surface",
                "scope",
                "query",
                "status",
                "result_count",
                "note",
            },
            f"receipt.sources[{index}]",
        )
        source_id = text(source["source_id"], f"receipt.sources[{index}].source_id")
        if source_id in seen_ids:
            raise ValidationError(f"duplicate source_id: {source_id}")
        seen_ids.add(source_id)
        text(source["surface"], f"receipt.sources[{index}].surface")
        text(source["scope"], f"receipt.sources[{index}].scope")
        text(source["query"], f"receipt.sources[{index}].query")
        text(source["note"], f"receipt.sources[{index}].note")
        status = source["status"]
        if status == "exhausted":
            count = source["result_count"]
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise ValidationError(
                    f"receipt.sources[{index}].result_count must be a non-negative integer"
                )
        elif status == "unavailable":
            if source["result_count"] is not None:
                raise ValidationError(
                    f"receipt.sources[{index}].result_count must be null when unavailable"
                )
        else:
            raise ValidationError(
                f"receipt.sources[{index}].status must be exhausted or unavailable"
            )
        if source_id in state["required_sources"]:
            required_status[source_id] = status

    missing = set(state["required_sources"]) - required_status.keys()
    if missing:
        raise ValidationError(f"receipt omits required sources: {sorted(missing)}")
    unavailable = sorted(
        source_id
        for source_id, status in required_status.items()
        if status == "unavailable"
    )
    if unavailable and not allow_partial_coverage:
        raise ValidationError(
            "required sources unavailable; retry or use --allow-partial-coverage "
            f"without advancing state: {unavailable}"
        )
    return not unavailable


def validate_agents(
    raw: Any, state: dict[str, Any], coverage_complete: bool
) -> None:
    if not isinstance(raw, list):
        raise ValidationError("receipt.agents must be an array")
    by_name: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        agent = object_at(item, f"receipt.agents[{index}]")
        exact_keys(
            agent,
            {"name", "distinct_outcomes", "confidence"},
            f"receipt.agents[{index}]",
        )
        name = text(agent["name"], f"receipt.agents[{index}].name")
        if name in by_name:
            raise ValidationError(f"duplicate agent receipt: {name}")
        if name not in set(state["roster"]) | set(state["conditional_agents"]):
            raise ValidationError(f"agent is not configured in state: {name}")
        outcomes = agent["distinct_outcomes"]
        if isinstance(outcomes, bool) or not isinstance(outcomes, int) or outcomes < 0:
            raise ValidationError(f"{name}.distinct_outcomes must be a non-negative integer")
        confidence = agent["confidence"]
        if confidence not in CONFIDENCE:
            raise ValidationError(f"{name}.confidence must be one of {sorted(CONFIDENCE)}")
        if not coverage_complete and confidence != "insufficient":
            raise ValidationError(
                f"{name} must use insufficient confidence while required coverage is partial"
            )
        if coverage_complete and outcomes == 0 and confidence != "insufficient":
            raise ValidationError(
                f"{name} with zero outcomes must use insufficient confidence"
            )
        if coverage_complete and outcomes > 0 and confidence == "insufficient":
            raise ValidationError(f"{name} with outcomes cannot use insufficient confidence")
        by_name[name] = agent
    missing = set(state["roster"]) - by_name.keys()
    if missing:
        raise ValidationError(f"receipt omits fixed-roster agents: {sorted(missing)}")
    for name in set(state["conditional_agents"]) & by_name.keys():
        if by_name[name]["distinct_outcomes"] == 0:
            raise ValidationError(f"conditional agent {name} must have direct activity")


def validate_weekly_report(
    raw: Any,
    state: dict[str, Any],
    receipt: dict[str, Any],
    allow_pending: bool,
) -> None:
    if receipt["mode"] == "daily":
        if raw is not None:
            raise ValidationError("daily receipt.weekly_report must be null")
        return
    report = object_at(raw, "receipt.weekly_report")
    exact_keys(
        report,
        {"start_utc", "end_utc", "target", "access_boundary", "message_id"},
        "receipt.weekly_report",
    )
    if report["start_utc"] != state["next_weekly_start_utc"]:
        raise ValidationError("weekly report start does not match next_weekly_start_utc")
    if report["end_utc"] != receipt["end_utc"]:
        raise ValidationError("weekly report end must equal receipt end")
    if report["target"] != state["publication_target"]:
        raise ValidationError("weekly report target does not match configured target")
    text(report["access_boundary"], "receipt.weekly_report.access_boundary")
    message_id = text(report["message_id"], "receipt.weekly_report.message_id")
    if message_id == "PENDING" and not allow_pending:
        raise ValidationError("PENDING publication requires --allow-pending-publication")


def validate_receipt(
    raw: Any,
    state: dict[str, Any],
    allow_pending: bool,
    allow_partial_coverage: bool = False,
) -> dict[str, Any]:
    receipt = object_at(raw, "receipt")
    exact_keys(receipt, RECEIPT_KEYS, "receipt")
    if receipt["schema_version"] != 1:
        raise ValidationError("receipt.schema_version must be 1")
    if receipt["mode"] not in {"daily", "weekly-final"}:
        raise ValidationError("receipt.mode must be daily or weekly-final")
    start = timestamp(receipt["start_utc"], "receipt.start_utc")
    end = timestamp(receipt["end_utc"], "receipt.end_utc")
    if start >= end:
        raise ValidationError("receipt interval must satisfy start_utc < end_utc")
    if receipt["start_utc"] != state["next_capture_start_utc"]:
        raise ValidationError("capture start does not match next_capture_start_utc")
    text(receipt["evidence_artifact"], "receipt.evidence_artifact")
    evidence_digest = text(receipt["evidence_sha256"], "receipt.evidence_sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", evidence_digest):
        raise ValidationError("receipt.evidence_sha256 must be lowercase SHA-256")
    coverage_complete = validate_sources(
        receipt["sources"], state, allow_partial_coverage
    )
    if receipt["mode"] == "weekly-final" and not coverage_complete:
        raise ValidationError("weekly-final receipt requires complete source coverage")
    validate_agents(receipt["agents"], state, coverage_complete)
    validate_weekly_report(receipt["weekly_report"], state, receipt, allow_pending)
    return receipt


def has_complete_coverage(state: dict[str, Any], receipt: dict[str, Any]) -> bool:
    statuses = {
        source["source_id"]: source["status"] for source in receipt["sources"]
    }
    return all(
        statuses.get(source_id) == "exhausted"
        for source_id in state["required_sources"]
    )


def next_state(
    state: dict[str, Any],
    receipt: dict[str, Any],
    receipt_bytes: bytes,
    receipt_path: Path,
    state_path: Path,
) -> dict[str, Any]:
    if not has_complete_coverage(state, receipt):
        raise ValidationError("cannot advance state with partial source coverage")
    if (
        receipt["mode"] == "weekly-final"
        and receipt["weekly_report"]["message_id"] == "PENDING"
    ):
        raise ValidationError("cannot emit next state for a pending publication")
    result = copy.deepcopy(state)
    result["next_capture_start_utc"] = receipt["end_utc"]
    result["last_completed_capture"] = {
        "start_utc": receipt["start_utc"],
        "end_utc": receipt["end_utc"],
        "receipt_path": path_for_state(receipt_path, state_path),
        "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
    }
    if receipt["mode"] == "weekly-final":
        result["next_weekly_start_utc"] = receipt["end_utc"]
        result["last_weekly_report"] = copy.deepcopy(receipt["weekly_report"])
    return result


def load_json(path: Path, label: str) -> tuple[Any, bytes]:
    try:
        raw = path.read_bytes()
        return json.loads(raw), raw
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"cannot read {label} {path}: {error}") from error


def path_for_state(path: Path, state_path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(state_path.resolve().parent))
    except ValueError:
        return str(resolved)


def path_from_state(value: str, state_path: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else state_path.resolve().parent / path


def validate_previous_receipt(state: dict[str, Any], state_path: Path) -> None:
    previous = state["last_completed_capture"]
    if previous is None:
        return
    path = path_from_state(previous["receipt_path"], state_path)
    try:
        raw = path.read_bytes()
        parsed = object_at(json.loads(raw), "previous receipt")
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"cannot read previous receipt {path}: {error}") from error
    digest = hashlib.sha256(raw).hexdigest()
    if digest != previous["receipt_sha256"]:
        raise ValidationError("previous receipt SHA-256 does not match retained state")
    if parsed.get("start_utc") != previous["start_utc"]:
        raise ValidationError("previous receipt start does not match retained state")
    if parsed.get("end_utc") != previous["end_utc"]:
        raise ValidationError("previous receipt end does not match retained state")


def validate_evidence_artifact(receipt: dict[str, Any], state_path: Path) -> None:
    artifact = Path(receipt["evidence_artifact"])
    if not artifact.is_absolute():
        artifact = state_path.resolve().parent / artifact
    try:
        evidence = artifact.read_bytes()
    except OSError as error:
        raise ValidationError(f"cannot read evidence artifact {artifact}: {error}") from error
    if not evidence:
        raise ValidationError(f"evidence artifact is empty: {artifact}")
    if hashlib.sha256(evidence).hexdigest() != receipt["evidence_sha256"]:
        raise ValidationError("evidence artifact SHA-256 does not match receipt")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--next-state", type=Path)
    parser.add_argument("--allow-pending-publication", action="store_true")
    parser.add_argument("--allow-partial-coverage", action="store_true")
    args = parser.parse_args()

    try:
        state_raw, _ = load_json(args.state, "state")
        receipt_raw, receipt_bytes = load_json(args.receipt, "receipt")
        state = validate_state(state_raw)
        validate_previous_receipt(state, args.state)
        receipt = validate_receipt(
            receipt_raw,
            state,
            args.allow_pending_publication,
            args.allow_partial_coverage,
        )
        validate_evidence_artifact(receipt, args.state)
        if args.next_state:
            updated = next_state(
                state,
                receipt,
                receipt_bytes,
                args.receipt,
                args.state,
            )
            args.next_state.write_text(
                json.dumps(updated, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    except (ValidationError, OSError) as error:
        print(f"review receipt invalid: {error}", file=sys.stderr)
        return 1

    if has_complete_coverage(state, receipt):
        print("review receipt valid")
    else:
        print(
            "review receipt valid for diagnostics only; "
            "state advancement and weekly publication remain blocked"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("validate_review_receipt.py")
SPEC = importlib.util.spec_from_file_location("validate_review_receipt", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def state() -> dict:
    return {
        "schema_version": 1,
        "roster": ["@Agent-A", "@Agent-B"],
        "conditional_agents": ["@Optional-Agent"],
        "publication_target": "#all",
        "next_capture_start_utc": "2026-08-18T14:30:00Z",
        "next_weekly_start_utc": "2026-08-12T00:00:00Z",
        "last_completed_capture": None,
        "last_weekly_report": None,
    }


def receipt() -> dict:
    return {
        "schema_version": 1,
        "mode": "daily",
        "start_utc": "2026-08-18T14:30:00Z",
        "end_utc": "2026-08-19T14:30:00Z",
        "evidence_artifact": "notes/evidence.md",
        "sources": [
            {
                "surface": "raft",
                "scope": "visible targets",
                "query": "interval query",
                "status": "exhausted",
                "result_count": 4,
                "note": "all pages consumed",
            }
        ],
        "agents": [
            {"name": "@Agent-A", "distinct_outcomes": 1, "confidence": "high"},
            {
                "name": "@Agent-B",
                "distinct_outcomes": 0,
                "confidence": "insufficient",
            },
        ],
        "weekly_report": None,
    }


class ReceiptValidationTest(unittest.TestCase):
    def validate(self, candidate: dict, allow_pending: bool = False) -> dict:
        validated_state = MODULE.validate_state(state())
        return MODULE.validate_receipt(candidate, validated_state, allow_pending)

    def test_valid_daily_receipt_advances_capture_only(self) -> None:
        candidate = receipt()
        validated_state = MODULE.validate_state(state())
        validated_receipt = MODULE.validate_receipt(candidate, validated_state, False)
        encoded = json.dumps(candidate).encode()
        updated = MODULE.next_state(validated_state, validated_receipt, encoded)

        self.assertEqual(updated["next_capture_start_utc"], candidate["end_utc"])
        self.assertEqual(
            updated["next_weekly_start_utc"], state()["next_weekly_start_utc"]
        )
        self.assertEqual(
            updated["last_completed_capture"]["receipt_sha256"],
            hashlib.sha256(encoded).hexdigest(),
        )

    def test_gap_or_overlap_fails_closed(self) -> None:
        candidate = receipt()
        candidate["start_utc"] = "2026-08-18T14:31:00Z"
        with self.assertRaisesRegex(MODULE.ValidationError, "capture start"):
            self.validate(candidate)

    def test_fixed_roster_omission_fails_closed(self) -> None:
        candidate = receipt()
        candidate["agents"] = candidate["agents"][:1]
        with self.assertRaisesRegex(MODULE.ValidationError, "fixed-roster"):
            self.validate(candidate)

    def test_unavailable_source_cannot_claim_zero_results(self) -> None:
        candidate = receipt()
        candidate["sources"][0].update(status="unavailable", result_count=0)
        with self.assertRaisesRegex(MODULE.ValidationError, "must be null"):
            self.validate(candidate)

    def test_conditional_agent_requires_direct_activity(self) -> None:
        candidate = receipt()
        candidate["agents"].append(
            {
                "name": "@Optional-Agent",
                "distinct_outcomes": 0,
                "confidence": "insufficient",
            }
        )
        with self.assertRaisesRegex(MODULE.ValidationError, "direct activity"):
            self.validate(candidate)

    def test_weekly_target_and_watermark_are_locked(self) -> None:
        candidate = receipt()
        candidate["mode"] = "weekly-final"
        candidate["weekly_report"] = {
            "start_utc": state()["next_weekly_start_utc"],
            "end_utc": candidate["end_utc"],
            "target": "#wrong",
            "access_boundary": "Visible sources only.",
            "message_id": "abc123",
        }
        with self.assertRaisesRegex(MODULE.ValidationError, "configured target"):
            self.validate(candidate)

    def test_pending_publication_is_preflight_only(self) -> None:
        candidate = receipt()
        candidate["mode"] = "weekly-final"
        candidate["weekly_report"] = {
            "start_utc": state()["next_weekly_start_utc"],
            "end_utc": candidate["end_utc"],
            "target": state()["publication_target"],
            "access_boundary": "Visible sources only.",
            "message_id": "PENDING",
        }
        validated = self.validate(candidate, allow_pending=True)
        with self.assertRaisesRegex(MODULE.ValidationError, "pending publication"):
            MODULE.next_state(state(), validated, b"receipt")

    def test_corrupt_saved_watermark_fails_closed(self) -> None:
        candidate = state()
        candidate["last_completed_capture"] = {
            "start_utc": "2026-08-17T14:30:00Z",
            "end_utc": "2026-08-18T14:29:59Z",
            "receipt_sha256": "0" * 64,
        }
        with self.assertRaisesRegex(MODULE.ValidationError, "capture watermark"):
            MODULE.validate_state(candidate)

    def test_cli_writes_validated_next_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "state.json"
            receipt_path = root / "receipt.json"
            next_path = root / "next.json"
            evidence_path = root / "notes" / "evidence.md"
            evidence_path.parent.mkdir()
            evidence_path.write_text("evidence\n", encoding="utf-8")
            state_path.write_text(json.dumps(state()), encoding="utf-8")
            receipt_path.write_text(json.dumps(receipt()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--state",
                    str(state_path),
                    "--receipt",
                    str(receipt_path),
                    "--next-state",
                    str(next_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                json.loads(next_path.read_text())["next_capture_start_utc"],
                receipt()["end_utc"],
            )

    def test_cli_rejects_missing_evidence_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "state.json"
            receipt_path = root / "receipt.json"
            state_path.write_text(json.dumps(state()), encoding="utf-8")
            receipt_path.write_text(json.dumps(receipt()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--state",
                    str(state_path),
                    "--receipt",
                    str(receipt_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 1)
            self.assertIn("evidence artifact does not exist", completed.stderr)


if __name__ == "__main__":
    unittest.main()

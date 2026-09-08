#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

MODULE_PATH = Path(__file__).with_name("research.py")
ANSWER_GUARD_PATH = Path(__file__).with_name("answer_guard.py")
SKILL_PATH = Path(__file__).parents[1] / "SKILL.md"
SPEC = importlib.util.spec_from_file_location("smart_robinhood_lp_research", MODULE_PATH)
assert SPEC and SPEC.loader
research = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(research)
ANSWER_GUARD_SPEC = importlib.util.spec_from_file_location(
    "smart_robinhood_lp_answer_guard", ANSWER_GUARD_PATH
)
assert ANSWER_GUARD_SPEC and ANSWER_GUARD_SPEC.loader
answer_guard = importlib.util.module_from_spec(ANSWER_GUARD_SPEC)
ANSWER_GUARD_SPEC.loader.exec_module(answer_guard)

ADDRESS = "0x" + "1" * 40
TOKEN = "0x" + "2" * 40
HASH = "0x" + "a" * 64
ZERO_HASH = "0x" + "0" * 64
JOB_ID = "b" * 64
REQUEST_ID = "11111111-1111-4111-8111-111111111111"


def valid_candidate(status="WAIT"):
    return {
        "id": f"uniswap-v3:{ADDRESS}",
        "rank": 1,
        "status": status,
        "reasonCodes": ["ECONOMICS_NON_POSITIVE"],
        "selectionBucket": "liquidity_volume",
        "protocol": "uniswap-v3",
        "poolAddress": ADDRESS,
        "poolId": None,
        "venueHint": "robinhood-reviewed-v3",
        "tokens": [
            {"address": ADDRESS, "symbol": "USDG", "decimals": 6},
            {"address": TOKEN, "symbol": "TEST", "decimals": 18},
        ],
        "discovery": [
            {
                "source": "geckoterminal",
                "scope": "pools:page:1",
                "observedAt": "2026-09-05T00:00:00Z",
                "reference": "https://api.geckoterminal.com/example",
                "externalDexId": "v3",
                "externalRank": 1,
                "liquidityUsd": "1000",
                "volume24hUsd": "500",
                "transactions24h": 20,
                "createdAt": None,
                "createdAtBlock": None,
            }
        ],
        "identity": {
            "status": "VERIFIED",
            "venueId": "robinhood-reviewed-v3",
            "adapter": "uniswap-v3",
            "semanticReview": "TRUSTED",
            "factoryOrManager": ADDRESS,
            "readerOrQuoter": TOKEN,
            "factoryOrManagerCodeHash": HASH,
            "readerOrQuoterCodeHash": HASH,
            "auxiliaryCodeHashes": {},
            "proxyEvidence": {
                "factoryOrManager": {
                    "eip1967Implementation": ZERO_HASH,
                    "eip1967Beacon": ZERO_HASH,
                },
                "readerOrQuoter": {
                    "eip1967Implementation": ZERO_HASH,
                    "eip1967Beacon": ZERO_HASH,
                },
                "auxiliary": {},
            },
            "poolCodeHash": HASH,
            "poolKey": None,
            "hookAddress": None,
            "reasonCodes": [],
            "verifiedAtBlock": "100",
        },
        "economics": {
            "status": "READY",
            "asOfBlock": "100",
            "asOfTime": "2026-09-05T00:00:00Z",
            "coverage": {
                "requiredSeconds": 86400,
                "observedSeconds": 86400,
                "ratio": "1",
                "complete": True,
                "gaps": [],
            },
            "referencePositionUsd": "1000",
            "volume24hUsd": "500",
            "fees24hUsd": "2",
            "entryExitCostUsd": "3",
            "impermanentLoss24hUsd": "1",
            "netBenefit24hUsd": "-2",
            "netBenefitMarginBps": "-20",
            "measurementBufferBps": "50",
            "volatility24h": "0.1",
            "volatility7d": None,
            "stressLossUsd": "10",
            "stressNetBenefitUsd": "-12",
            "reasonCodes": [],
        },
        "tokenControlEvidence": [
            {
                "tokenAddress": ADDRESS,
                "inspectionStatus": "STATIC_BYTECODE_REVIEWED",
                "runtimeCodeHash": HASH,
                "proxyEvidence": {
                    "eip1967Implementation": ZERO_HASH,
                    "eip1967Beacon": ZERO_HASH,
                },
                "observedControlSelectors": [],
                "transferTaxAssessment": "UNMEASURED",
                "transferTaxEvidence": {
                    "method": None,
                    "measuredAtBlock": None,
                    "observedTransactions": 0,
                    "observedDirections": [],
                    "maxObservedTaxBps": None,
                },
                "reasonCodes": ["TOKEN_STATIC_SCAN_LIMITED", "TRANSFER_TAX_UNMEASURED"],
            },
            {
                "tokenAddress": TOKEN,
                "inspectionStatus": "STATIC_BYTECODE_REVIEWED",
                "runtimeCodeHash": HASH,
                "proxyEvidence": {
                    "eip1967Implementation": ZERO_HASH,
                    "eip1967Beacon": ZERO_HASH,
                },
                "observedControlSelectors": ["OWNER", "MINT"],
                "transferTaxAssessment": "UNMEASURED",
                "transferTaxEvidence": {
                    "method": None,
                    "measuredAtBlock": None,
                    "observedTransactions": 0,
                    "observedDirections": [],
                    "maxObservedTaxBps": None,
                },
                "reasonCodes": [
                    "TOKEN_CONTROL_SELECTOR_OBSERVED",
                    "TOKEN_STATIC_SCAN_LIMITED",
                    "TRANSFER_TAX_UNMEASURED",
                ],
            },
        ],
        "externalCrossChecks": [],
        "riskFlags": [],
        "lastDeepVerifiedAt": "2026-09-05T00:00:00Z",
    }


def valid_payload(*, stale=False, funnel_policy_version="rh-lp-funnel.v1"):
    funnel_policy = research.FUNNEL_POLICIES[funnel_policy_version]
    deep_verification_limit = funnel_policy["deepVerificationLimit"]
    selection_buckets = dict(funnel_policy["selectionBucketQuotas"])
    return {
        "success": True,
        "data": {
            "schemaVersion": "rh-lp.v2",
            "funnelPolicyVersion": funnel_policy_version,
            "scorePolicyVersion": "rh-lp-score.v2",
            "venueRegistryVersion": "rh-lp-venues.v1",
            "chainId": 4663,
            "epoch": "1",
            "generatedAt": "2026-09-05T00:00:00Z",
            "staleAt": "2026-09-05T00:30:00Z",
            "isStale": stale,
            "documentStatus": "STALE" if stale else "READY",
            "reasonCodes": ["DOCUMENT_STALE"] if stale else [],
            "coverage": {
                "reportedUniversePools": 956,
                "sourceFetchedRows": {"geckoterminal": 120, "dexpaprika": 80},
                "mergedCandidateCount": 160,
                "frontierCandidateCount": 160,
                "frontierLimit": 200,
                "frontierBuckets": {
                    "liquidityVolume": 80,
                    "new": 40,
                    "heat": 40,
                    "rotation": 0,
                },
                "deepVerificationLimit": deep_verification_limit,
                "deepVerificationPlanned": deep_verification_limit,
                "deepVerificationCompleted": 1,
                "deepVerificationPending": deep_verification_limit - 1,
                "economicsBacklog": {"market": 24, "direct": 0},
                "verified24h": 1,
                "frontierSelectionRule": "80 liquidity_volume + 40 new + 40 heat + 40 source_diversity_rotation",
                "selectionBuckets": selection_buckets,
                "selectionRule": funnel_policy["selectionRule"],
            },
            "sourceReceipts": [
                {
                    "source": "geckoterminal",
                    "scope": "top+trending+new:pages:1-2",
                    "status": "OK",
                    "startedAt": "2026-09-05T00:00:00Z",
                    "finishedAt": "2026-09-05T00:00:01Z",
                    "rowCount": 120,
                    "scopeReceipts": [
                        {
                            "scope": "pools:page:1",
                            "status": "OK",
                            "fetchedRows": 20,
                            "acceptedRows": 20,
                            "reasonCodes": [],
                        }
                    ],
                    "reasonCodes": [],
                }
            ],
            "candidates": [valid_candidate()],
        },
    }


def valid_job(state="QUEUED_ECONOMICS"):
    return {
        "jobId": JOB_ID,
        "chainId": 4663,
        "origin": "direct",
        "identifierKind": "pool",
        "identifier": ADDRESS,
        "requestId": REQUEST_ID,
        "venueHint": None,
        "poolKeyHint": None,
        "selectionBucket": "direct",
        "state": state,
        "createdAt": "2026-09-05T00:00:00Z",
        "updatedAt": "2026-09-05T00:00:00Z",
        "epoch": "1",
        "leaseToken": None,
        "leaseExpiresAt": None,
        "checkpoint": None,
        "identityResult": valid_candidate(),
        "result": valid_candidate() if state == "COMPLETED" else None,
        "reasonCodes": [],
    }


class ContractTest(unittest.TestCase):
    def test_skill_uses_compact_summary_for_broad_market_questions(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("python3 scripts/research.py summary", skill)
        self.assertIn("Do not run `feed` first, read terminal spill", skill)
        self.assertIn("Python/heredoc parsers for a broad market answer", skill)
        self.assertIn("up to eight server-ranked `CANDIDATE`/`WAIT` entries", skill)

    def test_skill_treats_server_status_as_authoritative(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("server-emitted `status` as its authoritative", skill)
        self.assertIn("never infer,\n  promote, demote, or relabel", skill)
        self.assertIn("reserved exclusively for candidates whose source", skill)
        self.assertIn('`status == "WAIT"`', skill)
        self.assertIn("build an `id -> status` map", skill)
        self.assertIn(
            "verify every discussed pool is under its mapped source status", skill
        )

    def test_skill_separates_machine_evidence_from_normal_user_answers(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Answer the user, not the evidence system", skill)
        self.assertIn("Never narrate commands, tool\ncalls", skill)
        self.assertIn("Do not paste helper output", skill)
        self.assertIn("Discuss at most three pools by default", skill)
        self.assertIn("Do not print the enum", skill)
        self.assertIn("do not\n  recite `ECONOMICS_PENDING`", skill)
        self.assertIn("Do not\n  name an internal data provider", skill)
        self.assertIn("The internal map and raw enum names are not user-facing output", skill)
        self.assertIn("Surface only\n   their plain-language consequence", skill)
        self.assertIn("python3 scripts/answer_guard.py", skill)
        self.assertIn(
            "ordinary answer, call this an independent\n   seven-day fee-rate reference without naming vfat",
            skill,
        )

    def test_answer_guard_rejects_the_live_tool_narration_and_status_leak(self):
        answer = (
            "I'll pull the current market summary from the evidence API. "
            "This snapshot is flagged as incomplete/degraded."
        )

        errors = answer_guard.validate_ordinary_answer(answer)

        self.assertIn("answer narrates a command, tool, or data-fetching step", errors)
        self.assertTrue(any("API" in error and "degraded" in error for error in errors))

        smart_apostrophe_errors = answer_guard.validate_ordinary_answer(
            "I’m going to fetch the latest pool data before I answer."
        )
        self.assertIn(
            "answer narrates a command, tool, or data-fetching step",
            smart_apostrophe_errors,
        )

    def test_answer_guard_rejects_provider_schema_and_machine_constants(self):
        answer = (
            "Dune reports the rh-lp.v2 document as DISCOVERY_ONLY because "
            "ECONOMICS_PENDING remains in the reason codes."
        )

        errors = answer_guard.validate_ordinary_answer(answer)

        self.assertTrue(any("Dune" in error for error in errors))
        self.assertTrue(any("rh-lp.v2" in error for error in errors))
        self.assertTrue(any("DISCOVERY_ONLY" in error for error in errors))
        self.assertTrue(any("ECONOMICS_PENDING" in error for error in errors))

    def test_answer_guard_allows_ordinary_slash_pair_and_capitalized_words(self):
        answer = (
            "WETH/USDG is not ready. Some discovery data is unavailable, "
            "and the capital at risk could be affected by administrator controls."
        )

        self.assertEqual(answer_guard.validate_ordinary_answer(answer), [])

    def test_answer_guard_allows_plain_language_material_risk(self):
        answer = (
            "I don't see a pool worth further research right now. "
            "Some discovery data is unavailable, transfer-tax behavior has not been verified, "
            "and the fee-versus-risk calculation is still being measured."
        )

        self.assertEqual(answer_guard.validate_ordinary_answer(answer), [])

    def test_validates_v2_document(self):
        document = research.validate_document(valid_payload())
        self.assertEqual(document["coverage"]["frontierLimit"], 200)
        self.assertEqual(document["candidates"][0]["status"], "WAIT")

    def test_preserves_discovery_only_status_when_economics_are_incomplete(self):
        payload = valid_payload()
        candidate = payload["data"]["candidates"][0]
        candidate["status"] = "DISCOVERY_ONLY"
        candidate["reasonCodes"] = ["RPC_READ_FAILED"]
        candidate["economics"]["status"] = "INCOMPLETE"
        candidate["economics"]["reasonCodes"] = ["WINDOW_INCOMPLETE"]

        document = research.validate_document(payload)

        self.assertEqual(document["candidates"][0]["status"], "DISCOVERY_ONLY")

    def test_summary_preserves_source_statuses_and_bounds_discovery_examples(self):
        payload = valid_payload(funnel_policy_version="rh-lp-funnel.v2")
        candidate = payload["data"]["candidates"][0]
        candidate["status"] = "CANDIDATE"
        candidate["reasonCodes"] = ["ALL_CURRENT_GATES_PASS"]
        for evidence in candidate["tokenControlEvidence"]:
            evidence["transferTaxAssessment"] = "MEASURED_ABSENT"
            evidence["transferTaxEvidence"] = {
                "method": "V3_EXECUTED_SWAP_TRANSFERS",
                "measuredAtBlock": "100",
                "observedTransactions": 2,
                "observedDirections": ["POOL_IN", "POOL_OUT"],
                "maxObservedTaxBps": "0",
            }
        waiting = valid_candidate("WAIT")
        waiting["id"] = f"uniswap-v3:{TOKEN}"
        waiting["poolAddress"] = TOKEN
        discovery = []
        for rank in range(3, 10):
            item = valid_candidate("DISCOVERY_ONLY")
            item["id"] = f"uniswap-v3:0x{rank:040x}"
            item["poolAddress"] = f"0x{rank:040x}"
            item["rank"] = rank
            item["reasonCodes"] = ["NOT_SELECTED_THIS_EPOCH"]
            discovery.append(item)
        payload["data"]["candidates"] = [candidate, waiting, *discovery]

        summary = research.summarize_document(research.validate_document(payload))

        self.assertEqual(
            summary["statusCounts"],
            {"CANDIDATE": 1, "WAIT": 1, "DISCOVERY_ONLY": 7},
        )
        self.assertEqual(
            [item["status"] for item in summary["candidateGroups"]["CANDIDATE"]],
            ["CANDIDATE"],
        )
        self.assertEqual(
            [item["status"] for item in summary["candidateGroups"]["WAIT"]],
            ["WAIT"],
        )
        self.assertEqual(
            [item["rank"] for item in summary["candidateGroups"]["DISCOVERY_ONLY"]],
            [3, 4, 5, 6, 7],
        )
        self.assertEqual(summary["discoveryOnlyOmitted"], 2)
        self.assertEqual(summary["decisionCandidateOmitted"], 0)

    def test_summary_keeps_token_tax_evidence_bound_to_its_address(self):
        document = research.validate_document(valid_payload())
        summary = research.summarize_document(document)

        evidence = summary["candidateGroups"]["WAIT"][0]["tokenControlEvidence"]
        self.assertEqual(
            [item["tokenAddress"] for item in evidence],
            [ADDRESS, TOKEN],
        )

    def test_summary_is_small_enough_for_a_normal_tool_result(self):
        payload = valid_payload(funnel_policy_version="rh-lp-funnel.v2")
        candidates = []
        for rank in range(1, 201):
            candidate = valid_candidate("DISCOVERY_ONLY")
            candidate["id"] = f"uniswap-v3:0x{rank:040x}"
            candidate["poolAddress"] = f"0x{rank:040x}"
            candidate["rank"] = rank
            candidate["reasonCodes"] = ["NOT_SELECTED_THIS_EPOCH"]
            candidates.append(candidate)
        payload["data"]["candidates"] = candidates
        payload["data"]["coverage"]["mergedCandidateCount"] = 200
        payload["data"]["coverage"]["frontierCandidateCount"] = 200

        summary = research.summarize_document(research.validate_document(payload))
        encoded = research.json.dumps(summary, separators=(",", ":")).encode()

        self.assertLess(len(encoded), 48 * 1024)
        self.assertEqual(summary["statusCounts"]["DISCOVERY_ONLY"], 200)
        self.assertEqual(summary["discoveryOnlyOmitted"], 195)

    def test_summary_caps_legacy_decision_entries_and_reports_omissions(self):
        payload = valid_payload(funnel_policy_version="rh-lp-funnel.v1")
        candidates = []
        for rank in range(1, 26):
            candidate = valid_candidate("WAIT")
            candidate["id"] = f"uniswap-v3:0x{rank:040x}"
            candidate["poolAddress"] = f"0x{rank:040x}"
            candidate["rank"] = rank
            candidates.append(candidate)
        payload["data"]["candidates"] = candidates
        payload["data"]["coverage"]["mergedCandidateCount"] = 25
        payload["data"]["coverage"]["frontierCandidateCount"] = 25
        payload["data"]["coverage"]["deepVerificationCompleted"] = 25
        payload["data"]["coverage"]["deepVerificationPending"] = 0

        summary = research.summarize_document(research.validate_document(payload))
        encoded = research.json.dumps(summary, separators=(",", ":")).encode()

        self.assertLess(len(encoded), 48 * 1024)
        self.assertEqual(len(summary["candidateGroups"]["WAIT"]), 8)
        self.assertEqual(summary["decisionCandidateOmitted"], 17)

    def test_summary_command_fetches_once_and_never_reads_a_spill_file(self):
        document = research.validate_document(valid_payload())
        with patch.object(research, "fetch_document", return_value=document) as fetch, patch.object(
            research.sys, "argv", ["research.py", "summary"]
        ), patch("builtins.open", side_effect=AssertionError("spill file read")), patch(
            "builtins.print"
        ) as output:
            research.main()

        fetch.assert_called_once_with()
        rendered = research.json.loads(output.call_args.args[0])
        self.assertEqual(rendered["summaryContractVersion"], "rh-lp-summary.v1")

    def test_validates_funnel_v2_document(self):
        document = research.validate_document(
            valid_payload(funnel_policy_version="rh-lp-funnel.v2")
        )
        self.assertEqual(document["coverage"]["deepVerificationLimit"], 4)
        self.assertEqual(
            document["coverage"]["selectionRule"],
            "1 liquidity_volume + 1 new + 1 heat + 1 rotation",
        )

    def test_validates_funnel_v3_document_and_cross_check(self):
        payload = valid_payload(funnel_policy_version="rh-lp-funnel.v3")
        payload["data"]["candidates"][0]["externalCrossChecks"] = [
            {
                "source": "vfat",
                "status": "MATCHED",
                "observedAt": "2026-09-05T00:00:00Z",
                "reference": "https://api.vfat.io/v4/yield-opportunities",
                "poolAddress": ADDRESS,
                "poolId": None,
                "totalLiquidityUsd": "1000",
                "activeLiquidityUsd": "800",
                "feeAprPercent": "12.5",
                "feeWindowDays": 7,
                "assumesFullTimeInRange": True,
                "reasonCodes": ["VFAT_DATA_NON_AUTHORITATIVE"],
            }
        ]

        document = research.validate_document(payload)
        summary = research.summarize_document(document)

        self.assertEqual(document["coverage"]["deepVerificationLimit"], 8)
        self.assertEqual(document["coverage"]["selectionBuckets"]["liquidityVolume"], 8)
        self.assertEqual(
            summary["candidateGroups"]["WAIT"][0]["externalCrossChecks"][0]["feeWindowDays"],
            7,
        )

    def test_keeps_legacy_candidates_compatible_and_rejects_malformed_cross_checks(self):
        legacy = valid_payload(funnel_policy_version="rh-lp-funnel.v2")
        legacy["data"]["candidates"][0].pop("externalCrossChecks")
        research.validate_document(legacy)

        malformed = valid_payload(funnel_policy_version="rh-lp-funnel.v3")
        malformed["data"]["candidates"][0]["externalCrossChecks"] = [
            {
                "source": "vfat",
                "status": "MATCHED",
                "observedAt": "not-a-time",
                "reference": "https://api.vfat.io/v4/yield-opportunities",
                "poolAddress": ADDRESS,
                "poolId": None,
                "totalLiquidityUsd": "1000",
                "activeLiquidityUsd": "800",
                "feeAprPercent": "12.5",
                "feeWindowDays": 7,
                "assumesFullTimeInRange": True,
                "reasonCodes": ["VFAT_DATA_NON_AUTHORITATIVE"],
            }
        ]
        with self.assertRaisesRegex(ValueError, "external cross-check"):
            research.validate_document(malformed)

    def test_rejects_old_or_changed_policy_versions(self):
        payload = valid_payload()
        payload["data"]["schemaVersion"] = "rh-lp.v1"
        with self.assertRaisesRegex(ValueError, "schemaVersion"):
            research.validate_document(payload)

    def test_rejects_unknown_funnel_policy_version(self):
        payload = valid_payload()
        payload["data"]["funnelPolicyVersion"] = "rh-lp-funnel.v4"
        with self.assertRaisesRegex(ValueError, "funnelPolicyVersion"):
            research.validate_document(payload)

    def test_rejects_cross_version_funnel_contract_mix(self):
        mutations = {
            "limit": ("deepVerificationLimit", 25),
            "selection": (
                "selectionRule",
                "10 liquidity_volume + 5 new + 5 heat + 5 rotation",
            ),
        }
        for name, (field, value) in mutations.items():
            with self.subTest(name=name):
                payload = valid_payload(funnel_policy_version="rh-lp-funnel.v2")
                payload["data"]["coverage"][field] = value
                with self.assertRaisesRegex(ValueError, "funnel policy"):
                    research.validate_document(payload)

    def test_rejects_bucket_counts_that_contradict_the_selection_rule(self):
        payload = valid_payload(funnel_policy_version="rh-lp-funnel.v2")
        payload["data"]["coverage"]["selectionBuckets"] = {
            "liquidityVolume": 4,
            "new": 0,
            "heat": 0,
            "rotation": 0,
        }
        with self.assertRaisesRegex(ValueError, "selectionBuckets"):
            research.validate_document(payload)

    def test_accepts_deterministic_partial_selection_prefix(self):
        payload = valid_payload(funnel_policy_version="rh-lp-funnel.v2")
        payload["data"]["coverage"]["deepVerificationPlanned"] = 2
        payload["data"]["coverage"]["deepVerificationCompleted"] = 1
        payload["data"]["coverage"]["deepVerificationPending"] = 1
        payload["data"]["coverage"]["selectionBuckets"] = {
            "liquidityVolume": 1,
            "new": 1,
            "heat": 0,
            "rotation": 0,
        }
        research.validate_document(payload)

    def test_rejects_floating_point_economics(self):
        payload = valid_payload()
        payload["data"]["candidates"][0]["economics"]["volume24hUsd"] = 1.5
        with self.assertRaisesRegex(ValueError, "decimal string"):
            research.validate_document(payload)

    def test_rejects_invalid_proxy_evidence(self):
        payload = valid_payload()
        payload["data"]["candidates"][0]["identity"]["proxyEvidence"][
            "factoryOrManager"
        ]["eip1967Implementation"] = "0x1234"
        with self.assertRaisesRegex(ValueError, "proxy evidence"):
            research.validate_document(payload)

    def test_rejects_malformed_funnel_completion_counts(self):
        payload = valid_payload()
        payload["data"]["coverage"]["deepVerificationCompleted"] = 26
        with self.assertRaisesRegex(ValueError, "funnel policy"):
            research.validate_document(payload)

    def test_rejects_malformed_risk_flags(self):
        payload = valid_payload()
        payload["data"]["candidates"][0]["riskFlags"] = [
            {"code": "not-a-reason", "severity": "urgent", "detail": "bad"}
        ]
        with self.assertRaisesRegex(ValueError, "risk flag"):
            research.validate_document(payload)

    def test_rejects_token_control_evidence_bound_to_the_wrong_token(self):
        payload = valid_payload()
        payload["data"]["candidates"][0]["tokenControlEvidence"][1]["tokenAddress"] = ADDRESS
        with self.assertRaisesRegex(ValueError, "address mismatch"):
            research.validate_document(payload)

    def test_rejects_candidate_without_measured_absent_transfer_tax(self):
        payload = valid_payload()
        payload["data"]["candidates"][0]["status"] = "CANDIDATE"
        payload["data"]["candidates"][0]["reasonCodes"] = ["ALL_CURRENT_GATES_PASS"]
        with self.assertRaisesRegex(ValueError, "transfer tax gate"):
            research.validate_document(payload)

    def test_rejects_candidate_inside_stale_document(self):
        payload = valid_payload(stale=True)
        payload["data"]["candidates"][0]["status"] = "CANDIDATE"
        for evidence in payload["data"]["candidates"][0]["tokenControlEvidence"]:
            evidence["transferTaxAssessment"] = "MEASURED_ABSENT"
            evidence["transferTaxEvidence"] = {
                "method": "V3_EXECUTED_SWAP_TRANSFERS",
                "measuredAtBlock": "100",
                "observedTransactions": 2,
                "observedDirections": ["POOL_IN", "POOL_OUT"],
                "maxObservedTaxBps": "0",
            }
        with self.assertRaisesRegex(ValueError, "stale document"):
            research.validate_document(payload)

    def test_validates_async_submission_and_jobs(self):
        submission = research.validate_submission(
            {
                "success": True,
                "data": {
                    "requestId": REQUEST_ID,
                    "identifierKind": "pool",
                    "identifier": ADDRESS,
                    "venueHint": None,
                    "poolKeyHint": None,
                    "resolvedPools": 1,
                    "jobs": [valid_job()],
                    "reasonCodes": [],
                },
            }
        )
        self.assertEqual(submission["jobs"][0]["jobId"], JOB_ID)

    def test_direct_job_requires_the_caller_request_id(self):
        job = valid_job()
        job["requestId"] = None
        with self.assertRaisesRegex(ValueError, "request id missing"):
            research.validate_job(job)

    def test_submit_uses_one_stable_request_id_for_transport_retry(self):
        payload = {
            "success": True,
            "data": {
                "requestId": REQUEST_ID,
                "identifierKind": "pool",
                "identifier": ADDRESS,
                "venueHint": None,
                "poolKeyHint": None,
                "resolvedPools": 1,
                "jobs": [valid_job()],
                "reasonCodes": [],
            },
        }
        with patch.object(research, "request_json", return_value=payload) as request:
            result = research.submit_analysis(ADDRESS, "pool", REQUEST_ID)
        self.assertEqual(result["requestId"], REQUEST_ID)
        request.assert_called_once_with(
            research.FEED_PATH + "/analysis",
            method="POST",
            body={
                "identifier": ADDRESS,
                "identifierKind": "pool",
                "requestId": REQUEST_ID,
            },
            transient_retries=1,
        )

    def test_transport_retry_reuses_identical_encoded_body(self):
        body = {
            "identifier": ADDRESS,
            "identifierKind": "pool",
            "requestId": REQUEST_ID,
        }

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _limit):
                return b'{"success":true}'

        attempts = []

        def open_request(request, timeout):
            self.assertEqual(timeout, research.TIMEOUT_SECONDS)
            attempts.append(request.data)
            if len(attempts) == 1:
                raise URLError("timeout")
            return Response()

        with patch.object(research._OPENER, "open", side_effect=open_request), patch.object(
            research.time, "sleep"
        ):
            result = research.request_json(
                research.FEED_PATH + "/analysis",
                method="POST",
                body=body,
                transient_retries=1,
            )

        self.assertEqual(result, {"success": True})
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[0], attempts[1])
        self.assertEqual(attempts[0], research.json.dumps(body, separators=(",", ":")).encode())

    def test_polling_preserves_terminal_jobs_and_refreshes_pending(self):
        with patch.object(research.time, "sleep"), patch.object(
            research, "fetch_job", return_value=valid_job("COMPLETED")
        ) as fetch:
            jobs = research.poll_jobs([valid_job()], 3)
        self.assertEqual(jobs[0]["state"], "COMPLETED")
        fetch.assert_called_once_with(JOB_ID)

    def test_base_url_precedence_and_public_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(research.app_api_url(), research.DEFAULT_APP_API_URL)
        with patch.dict(
            os.environ,
            {
                "PIEVERSE_APP_API_URL": "https://primary.example/api/app/",
                "PURRFECT_CLAW_APP_API_URL": "https://secondary.example/api/app",
            },
            clear=True,
        ):
            self.assertEqual(research.app_api_url(), "https://primary.example/api/app")


if __name__ == "__main__":
    unittest.main()

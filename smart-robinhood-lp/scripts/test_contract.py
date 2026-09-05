#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

MODULE_PATH = Path(__file__).with_name("research.py")
SPEC = importlib.util.spec_from_file_location("smart_robinhood_lp_research", MODULE_PATH)
assert SPEC and SPEC.loader
research = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(research)

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
                "transferTaxAssessment": "NOT_KNOWN",
                "reasonCodes": ["TOKEN_STATIC_SCAN_LIMITED"],
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
                "transferTaxAssessment": "NOT_KNOWN",
                "reasonCodes": ["TOKEN_CONTROL_SELECTOR_OBSERVED", "TOKEN_STATIC_SCAN_LIMITED"],
            },
        ],
        "riskFlags": [],
        "lastDeepVerifiedAt": "2026-09-05T00:00:00Z",
    }


def valid_payload(*, stale=False):
    return {
        "success": True,
        "data": {
            "schemaVersion": "rh-lp.v2",
            "funnelPolicyVersion": "rh-lp-funnel.v1",
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
                "deepVerificationLimit": 25,
                "deepVerificationPlanned": 25,
                "deepVerificationCompleted": 1,
                "deepVerificationPending": 24,
                "economicsBacklog": {"market": 24, "direct": 0},
                "verified24h": 1,
                "frontierSelectionRule": "80 liquidity_volume + 40 new + 40 heat + 40 source_diversity_rotation",
                "selectionBuckets": {
                    "liquidityVolume": 10,
                    "new": 5,
                    "heat": 5,
                    "rotation": 5,
                },
                "selectionRule": "10 liquidity_volume + 5 new + 5 heat + 5 rotation",
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
    def test_validates_v2_document(self):
        document = research.validate_document(valid_payload())
        self.assertEqual(document["coverage"]["frontierLimit"], 200)
        self.assertEqual(document["candidates"][0]["status"], "WAIT")

    def test_rejects_old_or_changed_policy_versions(self):
        payload = valid_payload()
        payload["data"]["schemaVersion"] = "rh-lp.v1"
        with self.assertRaisesRegex(ValueError, "schemaVersion"):
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

    def test_rejects_candidate_inside_stale_document(self):
        payload = valid_payload(stale=True)
        payload["data"]["candidates"][0]["status"] = "CANDIDATE"
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

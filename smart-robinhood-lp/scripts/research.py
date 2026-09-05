#!/usr/bin/env python3
"""Read and validate the hosted rh-lp.v2 research contract."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_APP_API_URL = "https://purr.pieverse.io/api/app"
FEED_PATH = "/research/rh-lp"
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
TIMEOUT_SECONDS = 20
POLL_INTERVAL_SECONDS = 2

ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
BYTES32_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")
DECIMAL_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
REASON_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
JOB_ID_RE = re.compile(r"^[a-f0-9]{64}$")


class FailClosedRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "redirect_not_allowed", headers, fp)


_OPENER = build_opener(FailClosedRedirects)


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def app_api_url() -> str:
    base = (
        os.environ.get("PIEVERSE_APP_API_URL", "").strip()
        or os.environ.get("PURRFECT_CLAW_APP_API_URL", "").strip()
        or DEFAULT_APP_API_URL
    ).rstrip("/")
    parsed = urlparse(base)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        die("invalid hosted app API URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        die("invalid hosted app API URL")
    return base


def _object(value: Any, message: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(message)
    return value


def _list(value: Any, message: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(message)
    return value


def _timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _decimal(value: Any) -> bool:
    return value is None or isinstance(value, str) and DECIMAL_RE.fullmatch(value) is not None


def _reasons(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(reason, str) and REASON_RE.fullmatch(reason) for reason in value
    )


def _identifier(value: Any) -> bool:
    return isinstance(value, str) and (
        ADDRESS_RE.fullmatch(value) is not None or BYTES32_RE.fullmatch(value) is not None
    )


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _uuid(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return str(uuid.UUID(value)) == value.lower()
    except ValueError:
        return False


def _url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.hostname)


def validate_token(value: Any) -> None:
    token = _object(value, "token invalid")
    decimals = token.get("decimals")
    if (
        not isinstance(token.get("address"), str)
        or ADDRESS_RE.fullmatch(token["address"]) is None
        or not isinstance(token.get("symbol"), str)
        or not token["symbol"]
        or (decimals is not None and (not isinstance(decimals, int) or not 0 <= decimals <= 36))
    ):
        raise ValueError("token invalid")


def validate_pool_key(value: Any) -> None:
    pool_key = _object(value, "pool key invalid")
    if (
        not isinstance(pool_key.get("currency0"), str)
        or ADDRESS_RE.fullmatch(pool_key["currency0"]) is None
        or not isinstance(pool_key.get("currency1"), str)
        or ADDRESS_RE.fullmatch(pool_key["currency1"]) is None
        or not isinstance(pool_key.get("hooks"), str)
        or ADDRESS_RE.fullmatch(pool_key["hooks"]) is None
        or not isinstance(pool_key.get("fee"), int)
        or not 0 <= pool_key["fee"] <= 0xFFFFFF
        or not isinstance(pool_key.get("tickSpacing"), int)
        or not -(2**23) <= pool_key["tickSpacing"] < 2**23
    ):
        raise ValueError("pool key invalid")


def validate_observation(value: Any) -> None:
    observation = _object(value, "source observation invalid")
    if (
        observation.get("source")
        not in {"geckoterminal", "dexpaprika", "dexscreener", "dune", "direct"}
        or not isinstance(observation.get("scope"), str)
        or not observation["scope"]
        or not _timestamp(observation.get("observedAt"))
        or not _url(observation.get("reference"))
        or not _decimal(observation.get("liquidityUsd"))
        or not _decimal(observation.get("volume24hUsd"))
        or (
            observation.get("transactions24h") is not None
            and not _nonnegative_int(observation.get("transactions24h"))
        )
        or (
            observation.get("externalRank") is not None
            and (
                not _nonnegative_int(observation.get("externalRank"))
                or observation["externalRank"] == 0
            )
        )
        or (
            observation.get("createdAt") is not None
            and not _timestamp(observation.get("createdAt"))
        )
        or (
            observation.get("createdAtBlock") is not None
            and (
                not isinstance(observation.get("createdAtBlock"), str)
                or not observation["createdAtBlock"].isdigit()
            )
        )
    ):
        raise ValueError("source observation invalid")


def validate_proxy_slots(value: Any) -> None:
    slots = _object(value, "proxy evidence invalid")
    if any(
        not isinstance(slots.get(field), str) or BYTES32_RE.fullmatch(slots[field]) is None
        for field in ("eip1967Implementation", "eip1967Beacon")
    ):
        raise ValueError("proxy evidence invalid")


def validate_identity(value: Any) -> None:
    identity = _object(value, "identity invalid")
    if (
        identity.get("status") not in {"PENDING", "VERIFIED", "UNSUPPORTED", "FAILED"}
        or identity.get("adapter")
        not in {"uniswap-v2", "uniswap-v3", "uniswap-v4", "unknown"}
        or identity.get("semanticReview") not in {"TRUSTED", "UNREVIEWED", "MISMATCH"}
        or (
            identity.get("venueId") is not None
            and not isinstance(identity.get("venueId"), str)
        )
        or not _reasons(identity.get("reasonCodes"))
    ):
        raise ValueError("identity invalid")
    for field in ("factoryOrManager", "readerOrQuoter", "hookAddress"):
        item = identity.get(field)
        if item is not None and (not isinstance(item, str) or ADDRESS_RE.fullmatch(item) is None):
            raise ValueError(f"identity {field} invalid")
    for field in ("factoryOrManagerCodeHash", "readerOrQuoterCodeHash", "poolCodeHash"):
        item = identity.get(field)
        if item is not None and (not isinstance(item, str) or BYTES32_RE.fullmatch(item) is None):
            raise ValueError(f"identity {field} invalid")
    proxy = _object(identity.get("proxyEvidence"), "proxy evidence missing")
    for field in ("factoryOrManager", "readerOrQuoter"):
        if proxy.get(field) is not None:
            validate_proxy_slots(proxy[field])
    auxiliary = _object(proxy.get("auxiliary"), "proxy auxiliary evidence invalid")
    for slots in auxiliary.values():
        validate_proxy_slots(slots)
    auxiliary_hashes = _object(identity.get("auxiliaryCodeHashes"), "auxiliary hashes invalid")
    if any(not isinstance(item, str) or BYTES32_RE.fullmatch(item) is None for item in auxiliary_hashes.values()):
        raise ValueError("auxiliary hashes invalid")
    if identity.get("poolKey") is not None:
        validate_pool_key(identity["poolKey"])
    verified_at = identity.get("verifiedAtBlock")
    if verified_at is not None and (not isinstance(verified_at, str) or not verified_at.isdigit()):
        raise ValueError("identity verified block invalid")


def validate_economics(value: Any) -> None:
    economics = _object(value, "economics invalid")
    if economics.get("status") not in {"PENDING", "READY", "INCOMPLETE", "FAILED"}:
        raise ValueError("economics status invalid")
    if economics.get("measurementBufferBps") != "50":
        raise ValueError("measurement buffer invalid")
    as_of_block = economics.get("asOfBlock")
    if as_of_block is not None and (
        not isinstance(as_of_block, str) or not as_of_block.isdigit()
    ):
        raise ValueError("economics as-of block invalid")
    if economics.get("asOfTime") is not None and not _timestamp(economics.get("asOfTime")):
        raise ValueError("economics as-of time invalid")
    for field in (
        "referencePositionUsd",
        "volume24hUsd",
        "fees24hUsd",
        "entryExitCostUsd",
        "impermanentLoss24hUsd",
        "netBenefit24hUsd",
        "netBenefitMarginBps",
        "volatility24h",
        "volatility7d",
        "stressLossUsd",
        "stressNetBenefitUsd",
    ):
        if not _decimal(economics.get(field)):
            raise ValueError(f"economics {field} must be a decimal string or null")
    coverage = _object(economics.get("coverage"), "economics coverage invalid")
    if (
        coverage.get("requiredSeconds") != 86_400
        or not isinstance(coverage.get("observedSeconds"), int)
        or not _decimal(coverage.get("ratio"))
        or not isinstance(coverage.get("complete"), bool)
        or not isinstance(coverage.get("gaps"), list)
        or not _reasons(economics.get("reasonCodes"))
    ):
        raise ValueError("economics coverage invalid")
    for raw_gap in coverage["gaps"]:
        gap = _object(raw_gap, "economics coverage gap invalid")
        if (
            not isinstance(gap.get("fromBlock"), str)
            or not gap["fromBlock"].isdigit()
            or not isinstance(gap.get("toBlock"), str)
            or not gap["toBlock"].isdigit()
            or not isinstance(gap.get("reason"), str)
            or REASON_RE.fullmatch(gap["reason"]) is None
        ):
            raise ValueError("economics coverage gap invalid")


def validate_token_control_evidence(value: Any) -> None:
    evidence = _object(value, "token control evidence invalid")
    if (
        not isinstance(evidence.get("tokenAddress"), str)
        or ADDRESS_RE.fullmatch(evidence["tokenAddress"]) is None
        or evidence.get("inspectionStatus")
        not in {"UNINSPECTED", "STATIC_BYTECODE_REVIEWED", "FAILED"}
        or (
            evidence.get("runtimeCodeHash") is not None
            and (
                not isinstance(evidence.get("runtimeCodeHash"), str)
                or BYTES32_RE.fullmatch(evidence["runtimeCodeHash"]) is None
            )
        )
        or evidence.get("transferTaxAssessment") not in {"KNOWN_PRESENT", "NOT_KNOWN"}
        or not _reasons(evidence.get("reasonCodes"))
    ):
        raise ValueError("token control evidence invalid")
    if evidence.get("proxyEvidence") is not None:
        validate_proxy_slots(evidence["proxyEvidence"])
    selectors = _list(
        evidence.get("observedControlSelectors"), "token control selectors invalid"
    )
    if any(
        selector not in {"OWNER", "MINT", "PAUSE", "FREEZE", "BLACKLIST"}
        for selector in selectors
    ):
        raise ValueError("token control selectors invalid")


def validate_candidate(value: Any) -> None:
    candidate = _object(value, "candidate invalid")
    rank = candidate.get("rank")
    if (
        candidate.get("status") not in {"DISCOVERY_ONLY", "WAIT", "CANDIDATE"}
        or (rank is not None and (not _nonnegative_int(rank) or rank == 0))
        or candidate.get("selectionBucket")
        not in {None, "liquidity_volume", "new", "heat", "rotation", "direct"}
        or candidate.get("protocol")
        not in {"uniswap-v2", "uniswap-v3", "uniswap-v4", "unknown"}
        or not _identifier(candidate.get("poolAddress") or candidate.get("poolId"))
        or not _reasons(candidate.get("reasonCodes"))
        or not candidate["reasonCodes"]
    ):
        raise ValueError("candidate invalid")
    tokens = _list(candidate.get("tokens"), "candidate tokens invalid")
    if len(tokens) != 2:
        raise ValueError("candidate tokens invalid")
    for token in tokens:
        validate_token(token)
    observations = _list(candidate.get("discovery"), "candidate discovery invalid")
    if not observations:
        raise ValueError("candidate discovery invalid")
    for observation in observations:
        validate_observation(observation)
    validate_identity(candidate.get("identity"))
    validate_economics(candidate.get("economics"))
    token_controls = _list(
        candidate.get("tokenControlEvidence"), "candidate token control evidence invalid"
    )
    if len(token_controls) != 2:
        raise ValueError("candidate token control evidence invalid")
    for index, evidence in enumerate(token_controls):
        validate_token_control_evidence(evidence)
        if evidence.get("tokenAddress", "").lower() != tokens[index].get("address", "").lower():
            raise ValueError("candidate token control evidence address mismatch")
    risk_flags = _list(candidate.get("riskFlags"), "candidate risk flags invalid")
    for raw_flag in risk_flags:
        flag = _object(raw_flag, "candidate risk flag invalid")
        if (
            not isinstance(flag.get("code"), str)
            or REASON_RE.fullmatch(flag["code"]) is None
            or flag.get("severity") not in {"info", "warning", "critical"}
            or not isinstance(flag.get("detail"), str)
            or not flag["detail"]
        ):
            raise ValueError("candidate risk flag invalid")
    if candidate.get("lastDeepVerifiedAt") is not None and not _timestamp(
        candidate.get("lastDeepVerifiedAt")
    ):
        raise ValueError("candidate verification time invalid")


def validate_source_receipt(value: Any) -> None:
    receipt = _object(value, "source receipt invalid")
    if (
        receipt.get("source") not in {"geckoterminal", "dexpaprika", "dexscreener", "dune"}
        or receipt.get("status") not in {"OK", "DEGRADED", "CIRCUIT_OPEN", "DISABLED"}
        or not isinstance(receipt.get("scope"), str)
        or not receipt["scope"]
        or not _timestamp(receipt.get("startedAt"))
        or not _timestamp(receipt.get("finishedAt"))
        or not isinstance(receipt.get("rowCount"), int)
        or receipt["rowCount"] < 0
        or not _reasons(receipt.get("reasonCodes"))
    ):
        raise ValueError("source receipt invalid")
    scopes = _list(receipt.get("scopeReceipts"), "source scope receipts invalid")
    for raw_scope in scopes:
        scope = _object(raw_scope, "source scope receipt invalid")
        if (
            not isinstance(scope.get("scope"), str)
            or not scope["scope"]
            or scope.get("status") not in {"OK", "DEGRADED"}
            or not isinstance(scope.get("fetchedRows"), int)
            or scope["fetchedRows"] < 0
            or not isinstance(scope.get("acceptedRows"), int)
            or scope["acceptedRows"] < 0
            or not _reasons(scope.get("reasonCodes"))
        ):
            raise ValueError("source scope receipt invalid")


def validate_document(payload: Any) -> dict[str, Any]:
    envelope = _object(payload, "response envelope invalid")
    if envelope.get("success") is not True:
        raise ValueError("response envelope is not successful")
    document = _object(envelope.get("data"), "response document missing")
    expected_versions = {
        "schemaVersion": "rh-lp.v2",
        "funnelPolicyVersion": "rh-lp-funnel.v1",
        "scorePolicyVersion": "rh-lp-score.v2",
        "venueRegistryVersion": "rh-lp-venues.v1",
    }
    for field, expected in expected_versions.items():
        if document.get(field) != expected:
            raise ValueError(f"unsupported {field}")
    if (
        document.get("chainId") != 4663
        or not isinstance(document.get("epoch"), str)
        or not document["epoch"].isdigit()
        or document.get("documentStatus")
        not in {"READY", "DEGRADED", "STALE", "DISCOVERY_ONLY"}
        or not _timestamp(document.get("generatedAt"))
        or not _timestamp(document.get("staleAt"))
        or not isinstance(document.get("isStale"), bool)
        or not _reasons(document.get("reasonCodes"))
    ):
        raise ValueError("document contract invalid")
    coverage = _object(document.get("coverage"), "funnel coverage missing")
    if (
        coverage.get("frontierLimit") != 200
        or coverage.get("deepVerificationLimit") != 25
        or not _nonnegative_int(coverage.get("mergedCandidateCount"))
        or not _nonnegative_int(coverage.get("frontierCandidateCount"))
        or coverage["frontierCandidateCount"] > 200
        or not _nonnegative_int(coverage.get("deepVerificationPlanned"))
        or coverage["deepVerificationPlanned"] > 25
        or not _nonnegative_int(coverage.get("deepVerificationCompleted"))
        or coverage["deepVerificationCompleted"] > coverage["deepVerificationPlanned"]
        or not _nonnegative_int(coverage.get("deepVerificationPending"))
        or not _nonnegative_int(coverage.get("verified24h"))
        or coverage.get("frontierSelectionRule")
        != "80 liquidity_volume + 40 new + 40 heat + 40 source_diversity_rotation"
        or coverage.get("selectionRule") != "10 liquidity_volume + 5 new + 5 heat + 5 rotation"
    ):
        raise ValueError("funnel policy invalid")
    source_rows = _object(coverage.get("sourceFetchedRows"), "source row coverage missing")
    if any(not _nonnegative_int(count) for count in source_rows.values()):
        raise ValueError("source row coverage invalid")
    for field in ("frontierBuckets", "selectionBuckets"):
        buckets = _object(coverage.get(field), f"{field} missing")
        if set(buckets) != {"liquidityVolume", "new", "heat", "rotation"} or any(
            not _nonnegative_int(count) for count in buckets.values()
        ):
            raise ValueError(f"{field} invalid")
    backlog = _object(coverage.get("economicsBacklog"), "economics backlog missing")
    if any(
        not isinstance(backlog.get(lane), int) or backlog[lane] < 0
        for lane in ("market", "direct")
    ):
        raise ValueError("economics backlog invalid")
    receipts = _list(document.get("sourceReceipts"), "source receipts missing")
    for receipt in receipts:
        validate_source_receipt(receipt)
    candidates = _list(document.get("candidates"), "candidate list invalid")
    if len(candidates) > 200:
        raise ValueError("candidate list invalid")
    for candidate in candidates:
        validate_candidate(candidate)
    if document["isStale"] and any(candidate.get("status") == "CANDIDATE" for candidate in candidates):
        raise ValueError("stale document contains candidate")
    return document


def validate_job(value: Any) -> dict[str, Any]:
    job = _object(value, "analysis job invalid")
    if (
        not isinstance(job.get("jobId"), str)
        or JOB_ID_RE.fullmatch(job["jobId"]) is None
        or job.get("chainId") != 4663
        or job.get("origin") not in {"market", "direct"}
        or job.get("identifierKind") not in {"token", "pool", "poolId"}
        or job.get("state")
        not in {
            "PENDING_IDENTITY",
            "IDENTITY_READY",
            "QUEUED_ECONOMICS",
            "RUNNING_ECONOMICS",
            "COMPLETED",
            "FAILED",
        }
        or not _identifier(job.get("identifier"))
        or not _reasons(job.get("reasonCodes"))
        or (job.get("requestId") is not None and not _uuid(job.get("requestId")))
        or (job.get("venueHint") is not None and not isinstance(job.get("venueHint"), str))
    ):
        raise ValueError("analysis job invalid")
    if job["origin"] == "direct" and not _uuid(job.get("requestId")):
        raise ValueError("direct analysis request id missing")
    if job["origin"] == "market" and job.get("requestId") is not None:
        raise ValueError("market analysis request id invalid")
    if job.get("poolKeyHint") is not None:
        if job.get("identifierKind") != "poolId":
            raise ValueError("analysis job pool key invalid")
        validate_pool_key(job["poolKeyHint"])
    if job.get("identityResult") is not None:
        validate_candidate(job["identityResult"])
    if job.get("result") is not None:
        validate_candidate(job["result"])
    return job


def validate_submission(payload: Any) -> dict[str, Any]:
    envelope = _object(payload, "response envelope invalid")
    if envelope.get("success") is not True:
        raise ValueError("response envelope is not successful")
    submission = _object(envelope.get("data"), "analysis submission missing")
    if (
        not _uuid(submission.get("requestId"))
        or submission.get("identifierKind") not in {"token", "pool", "poolId"}
        or not _identifier(submission.get("identifier"))
        or (submission.get("venueHint") is not None and not isinstance(submission.get("venueHint"), str))
        or not isinstance(submission.get("resolvedPools"), int)
        or not _reasons(submission.get("reasonCodes"))
    ):
        raise ValueError("analysis submission invalid")
    if submission.get("poolKeyHint") is not None:
        if submission.get("identifierKind") != "poolId":
            raise ValueError("analysis submission pool key invalid")
        validate_pool_key(submission["poolKeyHint"])
    jobs = _list(submission.get("jobs"), "analysis jobs invalid")
    if len(jobs) > 20:
        raise ValueError("analysis jobs invalid")
    for job in jobs:
        validate_job(job)
        if job.get("requestId") != submission.get("requestId"):
            raise ValueError("analysis request id mismatch")
    return submission


def _read_bounded(response) -> bytes:
    body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("rh-lp response too large")
    return body


def request_json(
    path: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    transient_retries: int = 0,
) -> Any:
    encoded = None if body is None else json.dumps(body, separators=(",", ":")).encode("utf-8")
    headers = {"Accept": "application/json", "User-Agent": "smart-robinhood-lp/2"}
    if encoded is not None:
        headers["Content-Type"] = "application/json"
    for attempt in range(transient_retries + 1):
        request = Request(app_api_url() + path, data=encoded, headers=headers, method=method)
        try:
            with _OPENER.open(request, timeout=TIMEOUT_SECONDS) as response:
                raw = _read_bounded(response)
            break
        except HTTPError as error:
            detail = error.read(4096).decode("utf-8", "replace")
            if error.code not in {500, 502, 503, 504} or attempt >= transient_retries:
                raise RuntimeError(f"rh-lp HTTP {error.code}: {detail[:500]}") from error
        except (URLError, TimeoutError, OSError) as error:
            if attempt >= transient_retries:
                raise RuntimeError(f"rh-lp request failed: {error}") from error
        time.sleep(0.5 * (attempt + 1))
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid rh-lp JSON: {error}") from error


def fetch_document() -> dict[str, Any]:
    return validate_document(request_json(FEED_PATH))


def submit_analysis(identifier: str, kind: str, request_id: str) -> dict[str, Any]:
    if not _uuid(request_id):
        raise ValueError("request id invalid")
    try:
        return validate_submission(
            request_json(
                FEED_PATH + "/analysis",
                method="POST",
                body={
                    "identifier": identifier,
                    "identifierKind": kind,
                    "requestId": request_id,
                },
                transient_retries=1,
            )
        )
    except RuntimeError as error:
        raise RuntimeError(
            f"{error} (requestId={request_id}; retry with --request-id {request_id})"
        ) from error


def fetch_job(job_id: str) -> dict[str, Any]:
    if JOB_ID_RE.fullmatch(job_id) is None:
        raise ValueError("job id invalid")
    payload = _object(request_json(FEED_PATH + "/analysis/" + job_id), "response envelope invalid")
    if payload.get("success") is not True:
        raise ValueError("response envelope is not successful")
    return validate_job(payload.get("data"))


def poll_jobs(jobs: list[dict[str, Any]], wait_seconds: int) -> list[dict[str, Any]]:
    deadline = time.monotonic() + wait_seconds
    current = jobs
    while any(job["state"] not in {"COMPLETED", "FAILED"} for job in current):
        if time.monotonic() >= deadline:
            break
        time.sleep(POLL_INTERVAL_SECONDS)
        current = [
            fetch_job(job["jobId"])
            if job["state"] not in {"COMPLETED", "FAILED"}
            else job
            for job in current
        ]
    return current


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("feed", help="read the current bounded discovery feed")
    analyze = subparsers.add_parser("analyze", help="analyze one exact token, pool, or pool ID")
    kinds = analyze.add_mutually_exclusive_group(required=True)
    kinds.add_argument("--token")
    kinds.add_argument("--pool")
    kinds.add_argument("--pool-id")
    analyze.add_argument("--request-id", help="UUID reused to recover the same analysis jobs")
    analyze.add_argument("--wait-seconds", type=int, default=0, choices=range(0, 601), metavar="0..600")
    job = subparsers.add_parser("job", help="read one analysis job")
    job.add_argument("job_id")
    return parser.parse_args(argv)


def main() -> None:
    arguments = parse_args(sys.argv[1:] or ["feed"])
    try:
        if arguments.command == "feed":
            result: Any = fetch_document()
        elif arguments.command == "job":
            result = fetch_job(arguments.job_id)
        else:
            identifier = arguments.token or arguments.pool or arguments.pool_id
            kind = "token" if arguments.token else "pool" if arguments.pool else "poolId"
            if not _identifier(identifier):
                raise ValueError(f"{kind} identifier invalid")
            request_id = arguments.request_id or str(uuid.uuid4())
            submission = submit_analysis(identifier.lower(), kind, request_id)
            jobs = poll_jobs(submission["jobs"], arguments.wait_seconds)
            result = {"submission": submission, "jobs": jobs}
        print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))
    except (RuntimeError, ValueError) as error:
        die(str(error))


if __name__ == "__main__":
    main()

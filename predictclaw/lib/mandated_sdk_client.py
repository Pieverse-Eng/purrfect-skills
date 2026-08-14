"""One-shot Node subprocess client for ``@erc-mandated/sdk``.

This replaces the former MCP stdio transport. Each tool call is a single Node
process invocation: the helper reads one JSON line on stdin
``{"tool": "...", "arguments": {...}}`` and writes one JSON line on stdout
``{"result": {...}}`` or ``{"error": {...}}``. There is no initialize,
tools/list, tools/call handshake, and no long-lived process.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Mapping

from predict_sdk.constants import RPC_URLS_BY_CHAIN_ID

from .config import PredictConfig, redact_text


SUPPORTED_SDK_TOOLS = frozenset(
    {
        "agent_account_context_create",
        "agent_funding_policy_create",
        "vault_bootstrap",
        "agent_build_fund_and_action_plan",
        "agent_fund_and_action_session_create",
        "agent_fund_and_action_session_apply_event",
        "agent_fund_and_action_session_next_step",
        "agent_follow_up_action_result_create",
        "vault_asset_transfer_result_create",
        "vault_check_asset_transfer_policy",
        "vault_health_check",
        "factory_predict_vault_address",
        "factory_create_vault_prepare",
        "mandate_build_sign_request",
        "vault_build_asset_transfer_plan_from_context",
        "vault_simulate_asset_transfer_from_context",
        "vault_prepare_asset_transfer_from_context",
    }
)

_RPC_ENV_KEYS_BY_CHAIN_ID = {
    56: ("BSC_MAINNET_RPC_URL", "BSC_RPC_URL", "ERC_MANDATED_RPC_URL"),
    97: ("BSC_TESTNET_RPC_URL", "BSC_RPC_URL", "ERC_MANDATED_RPC_URL"),
}
_DEFAULT_RPC_URL_BY_CHAIN_ID = {
    int(chain_id): rpc_url for chain_id, rpc_url in RPC_URLS_BY_CHAIN_ID.items()
}


class MandatedSdkError(RuntimeError):
    """Raised when the one-shot SDK helper cannot be run or returns malformed data."""


def _apply_default_rpc_env(env: dict[str, str], config: PredictConfig) -> None:
    chain_id = config.mandated_chain_id or int(config.chain_id)
    env_keys = _RPC_ENV_KEYS_BY_CHAIN_ID.get(chain_id)
    if env_keys is None:
        return
    if any(env.get(key) for key in env_keys):
        return
    rpc_url = _DEFAULT_RPC_URL_BY_CHAIN_ID.get(chain_id)
    if rpc_url:
        env["ERC_MANDATED_RPC_URL"] = rpc_url


class MandatedSdkClient:
    def __init__(
        self,
        config: PredictConfig,
        *,
        helper_path: str | Path | None = None,
        node_command: str = "node",
    ) -> None:
        self._config = config
        self._helper_path = helper_path or (
            Path(__file__).resolve().parent.parent
            / "node"
            / "erc_mandated_sdk_helper.mjs"
        )
        self._node_command = node_command

    async def call(self, tool: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        helper = Path(self._helper_path)
        if not helper.exists():
            raise MandatedSdkError(
                f"Bundled mandated SDK helper not found at {helper}."
            )

        env = {"PATH": os.environ.get("PATH", "")}
        env["ERC_MANDATED_CONTRACT_VERSION"] = self._config.mandated_contract_version
        if self._config.mandated_chain_id is not None:
            env["ERC_MANDATED_CHAIN_ID"] = str(self._config.mandated_chain_id)
        _apply_default_rpc_env(env, self._config)

        request = json.dumps({"tool": tool, "arguments": dict(arguments)})
        try:
            process = await asyncio.create_subprocess_exec(
                self._node_command,
                str(helper),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024 * 1024,
                env=env,
            )
        except OSError as error:
            raise MandatedSdkError(
                redact_text(
                    f"Failed to start mandated SDK helper with {self._node_command!r}: {error}",
                    self._secrets(),
                )
            ) from error

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(request.encode("utf-8") + b"\n"),
                timeout=self._config.http_timeout_seconds,
            )
        except asyncio.TimeoutError as error:
            process.kill()
            await process.wait()
            raise MandatedSdkError(
                redact_text(
                    f"Mandated SDK helper timed out for {tool}.",
                    self._secrets(),
                )
            ) from error

        if process.returncode != 0:
            raise MandatedSdkError(
                redact_text(
                    f"Mandated SDK helper exited with {process.returncode} for {tool}: "
                    f"{stderr.decode('utf-8', errors='replace')[:400]}",
                    self._secrets(),
                )
            )

        text = stdout.decode("utf-8", errors="replace").strip()
        if not text:
            raise MandatedSdkError(
                redact_text(
                    f"Mandated SDK helper returned no output for {tool}.",
                    self._secrets(),
                )
            )
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise MandatedSdkError(
                redact_text(
                    f"Mandated SDK helper returned malformed JSON for {tool}: {text[:400]}",
                    self._secrets(),
                )
            ) from error
        if not isinstance(payload, dict):
            raise MandatedSdkError(
                redact_text(
                    f"Mandated SDK helper returned a non-object response for {tool}.",
                    self._secrets(),
                )
            )
        return payload

    async def close(self) -> None:
        return None

    def _secrets(self) -> list[str | None]:
        return []

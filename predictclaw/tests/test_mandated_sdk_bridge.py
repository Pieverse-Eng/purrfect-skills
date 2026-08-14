from __future__ import annotations

import os

import json
from typing import Any

import pytest

from lib.config import PredictConfig
from lib.mandated_sdk_bridge import MandatedVaultBridge
from lib.mandated_sdk_client import MandatedSdkClient, MandatedSdkError, SUPPORTED_SDK_TOOLS
from lib.platform_wallet import PlatformWalletClient


VAULT_ADDRESS = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
FACTORY_ADDRESS = "0x1111111111111111111111111111111111111111"
ASSET_ADDRESS = "0x2222222222222222222222222222222222222222"
AUTHORITY_ADDRESS = "0x3333333333333333333333333333333333333333"
SALT = "0x" + "12" * 32
PREDICTED_VAULT = "0x5555555555555555555555555555555555555555"


def sdk_config(**extra: str) -> PredictConfig:
    env = {
        "PREDICT_ENV": "testnet",
        "PREDICT_STORAGE_DIR": os.environ["PREDICT_STORAGE_DIR"],
        "PREDICT_WALLET_MODE": "mandated-vault",
        "ERC_MANDATED_VAULT_ADDRESS": VAULT_ADDRESS,
        "WALLET_API_URL": "http://wallet.test",
        "WALLET_API_TOKEN": "wallet-token",
        "INSTANCE_ID": "instance-1",
    }
    env.update(extra)
    return PredictConfig.from_env(env)


@pytest.mark.asyncio
async def test_default_config_advertises_bundled_sdk_tools() -> None:
    config = sdk_config()
    assert config.uses_bundled_sdk_helper is True

    bridge = MandatedVaultBridge(config)
    await bridge.connect()

    assert bridge.available_tools == SUPPORTED_SDK_TOOLS
    assert bridge.runtime_ready is True
    assert bridge.missing_required_tools == frozenset()
    await bridge.close()


class FakeProcess:
    def __init__(self, stdout: bytes, stderr: bytes = b"", returncode: int = 0) -> None:
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode

    async def communicate(self, input: bytes | None = None) -> tuple[bytes, bytes]:
        self.sent = input
        return self._stdout, self._stderr

    def kill(self) -> None:
        self.returncode = -9

    async def wait(self) -> int:
        return self.returncode


@pytest.mark.asyncio
async def test_sdk_client_call_writes_request_and_returns_payload(monkeypatch) -> None:
    config = sdk_config()
    captured: dict[str, Any] = {}

    async def fake_exec(*args: Any, **kwargs: Any) -> FakeProcess:
        captured["argv"] = args
        captured["env"] = kwargs.get("env")
        return FakeProcess(
            stdout=json.dumps({"result": {"predictedVault": PREDICTED_VAULT}}).encode()
        )

    monkeypatch.setattr(
        "lib.mandated_sdk_client.asyncio.create_subprocess_exec", fake_exec
    )
    client = MandatedSdkClient(config)
    payload = await client.call(
        "factory_predict_vault_address",
        {
            "chainId": 97,
            "factory": FACTORY_ADDRESS,
            "asset": ASSET_ADDRESS,
            "name": "PredictClaw Vault",
            "symbol": "pCLAW",
            "authority": AUTHORITY_ADDRESS,
            "salt": SALT,
        },
    )
    await client.close()

    assert payload == {"result": {"predictedVault": PREDICTED_VAULT}}
    assert captured["argv"][0] == "node"
    assert str(captured["argv"][1]).endswith("erc_mandated_sdk_helper.mjs")
    assert captured["env"]["ERC_MANDATED_CONTRACT_VERSION"] == config.mandated_contract_version
    assert captured["env"]["ERC_MANDATED_RPC_URL"]


@pytest.mark.asyncio
async def test_sdk_client_fails_closed_on_nonzero_exit(monkeypatch) -> None:
    config = sdk_config()

    async def fake_exec(*args: Any, **kwargs: Any) -> FakeProcess:
        return FakeProcess(stdout=b"", stderr=b"boom", returncode=1)

    monkeypatch.setattr(
        "lib.mandated_sdk_client.asyncio.create_subprocess_exec", fake_exec
    )
    client = MandatedSdkClient(config)
    with pytest.raises(MandatedSdkError, match="exited with 1"):
        await client.call("vault_health_check", {"vault": VAULT_ADDRESS, "chainId": 97})
    await client.close()


@pytest.mark.asyncio
async def test_bridge_routes_default_to_sdk_client(monkeypatch) -> None:
    config = sdk_config()
    calls: list[tuple[str, dict[str, Any]]] = []

    async def fake_call(self: Any, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        calls.append((tool, arguments))
        return {"result": {"predictedVault": PREDICTED_VAULT}}

    monkeypatch.setattr(
        "lib.mandated_sdk_client.MandatedSdkClient.call", fake_call
    )
    bridge = MandatedVaultBridge(config)
    result = await bridge.predict_vault_address(
        factory=FACTORY_ADDRESS,
        asset=ASSET_ADDRESS,
        name="PredictClaw Vault",
        symbol="pCLAW",
        authority=AUTHORITY_ADDRESS,
        salt=SALT,
    )

    assert result.predictedVault == PREDICTED_VAULT
    assert calls[0][0] == "factory_predict_vault_address"
    assert calls[0][1]["chainId"] == 97


@pytest.mark.asyncio
async def test_sdk_client_env_is_allowlisted_and_does_not_leak_parent_secrets(
    monkeypatch,
) -> None:
    config = sdk_config()
    captured: dict[str, Any] = {}

    async def fake_exec(*args: Any, **kwargs: Any) -> FakeProcess:
        captured["env"] = kwargs.get("env")
        return FakeProcess(stdout=json.dumps({"result": {}}).encode())

    monkeypatch.setattr(
        "lib.mandated_sdk_client.asyncio.create_subprocess_exec", fake_exec
    )
    monkeypatch.setenv("SECRET_SHOULD_NOT_LEAK", "super-secret")

    client = MandatedSdkClient(config)
    await client.call(
        "vault_health_check",
        {"vault": VAULT_ADDRESS, "chainId": 97},
    )
    await client.close()

    env = captured["env"]
    assert isinstance(env, dict)
    assert "WALLET_API_TOKEN" not in env
    assert "SECRET_SHOULD_NOT_LEAK" not in env
    assert set(env) <= {
        "PATH",
        "ERC_MANDATED_CONTRACT_VERSION",
        "ERC_MANDATED_CHAIN_ID",
        "ERC_MANDATED_RPC_URL",
    }


@pytest.mark.asyncio
async def test_vault_bootstrap_execute_broadcasts_through_platform_wallet(
    monkeypatch,
) -> None:
    config = sdk_config()
    tx_request = {
        "from": AUTHORITY_ADDRESS,
        "to": FACTORY_ADDRESS,
        "data": "0x1234",
        "value": "0",
        "gas": "0x5208",
    }
    bootstrap_payload = {
        "chainId": 97,
        "mode": "plan",
        "factory": FACTORY_ADDRESS,
        "asset": ASSET_ADDRESS,
        "signerAddress": AUTHORITY_ADDRESS,
        "predictedVault": PREDICTED_VAULT,
        "deployedVault": PREDICTED_VAULT,
        "alreadyDeployed": False,
        "deploymentStatus": "planned",
        "authorityConfig": {
            "mode": "single_key",
            "authority": AUTHORITY_ADDRESS,
            "executor": AUTHORITY_ADDRESS,
        },
        "createTx": {"mode": "plan", "txRequest": tx_request},
        "envBlock": "",
        "configBlock": "",
    }

    async def fake_call(
        self: Any, tool: str, arguments: dict[str, Any], **kwargs: Any
    ) -> dict[str, Any]:
        assert tool == "vault_bootstrap"
        assert arguments["mode"] == "plan"
        return {"result": bootstrap_payload}

    execute_calls: list[list[dict[str, Any]]] = []

    def fake_execute(self: Any, steps: list[dict[str, Any]]) -> dict[str, Any]:
        execute_calls.append(steps)
        return {"results": [{"hash": "0xexecuted"}]}

    monkeypatch.setattr(MandatedVaultBridge, "_call_tool", fake_call)
    monkeypatch.setattr(PlatformWalletClient, "execute", fake_execute)

    bridge = MandatedVaultBridge(config)
    result = await bridge.vault_bootstrap(
        factory=FACTORY_ADDRESS,
        asset=ASSET_ADDRESS,
        name="PredictClaw Vault",
        symbol="pCLAW",
        salt=SALT,
        signer_address=AUTHORITY_ADDRESS,
        mode="execute",
        authority_mode="single_key",
        authority=AUTHORITY_ADDRESS,
        create_account_context=False,
        create_funding_policy=False,
    )

    assert execute_calls == [
        [
            {
                "to": FACTORY_ADDRESS,
                "data": "0x1234",
                "value": "0",
                "chainId": 97,
            }
        ]
    ]
    assert result.mode == "execute"
    assert result.createTx is not None
    assert result.createTx.txHash == "0xexecuted"

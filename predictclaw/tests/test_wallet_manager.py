from __future__ import annotations

import asyncio
import os
from typing import Any

from lib.config import ConfigError, PredictConfig
from lib.funding_service import FundingService
from lib.mandated_sdk_bridge import (
    MandatedVaultBridgeError,
    VaultBootstrapAuthorityConfig,
    VaultBootstrapResult,
)
from lib.wallet_manager import WalletManager, resolve_mandated_vault


class FakeBootstrapBridge:
    def __init__(self, bootstrap: VaultBootstrapResult) -> None:
        self._bootstrap = bootstrap
        self.available_tools = frozenset({"vault_bootstrap"})
        self.calls: list[dict[str, Any]] = []

    async def connect(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def vault_bootstrap(self, **kwargs: Any) -> VaultBootstrapResult:
        self.calls.append(kwargs)
        return self._bootstrap


def mandated_vault_config() -> PredictConfig:
    return PredictConfig.from_env(
        {
            "PREDICT_ENV": "testnet",
            "PREDICT_STORAGE_DIR": os.environ["PREDICT_STORAGE_DIR"],
            "PREDICT_WALLET_MODE": "mandated-vault",
            "WALLET_API_URL": "http://wallet.test",
            "WALLET_API_TOKEN": "wallet-token",
            "INSTANCE_ID": "instance-1",
            "ERC_MANDATED_CHAIN_ID": "97",
        }
    )


def make_bootstrap_result(signer: str) -> VaultBootstrapResult:
    return VaultBootstrapResult(
        chainId=97,
        mode="plan",
        factory="0x" + "33" * 20,
        asset="0x" + "44" * 20,
        signerAddress=signer,
        predictedVault="0x" + "66" * 20,
        deployedVault="0x" + "66" * 20,
        alreadyDeployed=False,
        deploymentStatus="planned",
        authorityConfig=VaultBootstrapAuthorityConfig(
            mode="single_key",
            authority=signer,
            executor=signer,
        ),
        envBlock="",
        configBlock="",
    )


class FakePredictBridge:
    def __init__(self) -> None:
        self.available_tools = frozenset()
        self.predict_calls: list[dict[str, Any]] = []

    async def connect(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def predict_vault_address(self, **kwargs: Any) -> Any:
        self.predict_calls.append(kwargs)
        return type("Result", (), {"predictedVault": "0x" + "66" * 20})()

    async def health_check(self, vault: str) -> Any:
        raise MandatedVaultBridgeError("VAULT_NOT_DEPLOYED")


def test_resolve_mandated_vault_uses_platform_signer_authority_fallback(
    monkeypatch,
) -> None:
    config = mandated_vault_config()
    signer = "0x" + "55" * 20
    bridge = FakePredictBridge()

    async def fake_platform_signer_address(_config: PredictConfig) -> str:
        return signer

    monkeypatch.setattr(
        "lib.wallet_manager._platform_signer_address",
        fake_platform_signer_address,
    )

    resolution = asyncio.run(
        resolve_mandated_vault(config, bridge, include_create_prepare=False)
    )

    assert resolution.vault_address == "0x" + "66" * 20
    assert bridge.predict_calls[0]["authority"] == signer


def test_withdraw_predict_account_fails_closed_until_kernel_execute() -> None:
    config = PredictConfig.from_env(
        {
            "PREDICT_ENV": "testnet",
            "PREDICT_STORAGE_DIR": os.environ["PREDICT_STORAGE_DIR"],
            "PREDICT_WALLET_MODE": "predict-account",
            "PREDICT_ACCOUNT_ADDRESS": "0x" + "11" * 20,
            "WALLET_API_URL": "http://wallet.test",
            "WALLET_API_TOKEN": "wallet-token",
            "INSTANCE_ID": "instance-1",
        }
    )
    service = FundingService(config)

    try:
        service.withdraw("usdt", "1", "0x" + "33" * 20)
    except ConfigError as error:
        message = str(error)
        assert "unsupported-predict-account-execution" in message
        assert "Kernel execution" in message
    else:
        raise AssertionError("predict-account withdraw must fail closed")


def test_mandated_vault_template_shape_config_is_valid() -> None:
    config = mandated_vault_config()

    assert config.wallet_mode.value == "mandated-vault"
    assert config.mandated_vault_address is None
    assert config.mandated_vault_authority is None
    assert config.has_all_mandated_derivation_input is True


def test_bootstrap_vault_preview_uses_platform_signer_authority_fallback(
    monkeypatch,
) -> None:
    config = mandated_vault_config()
    assert config.mandated_vault_authority is None

    signer = "0x" + "55" * 20
    bootstrap = make_bootstrap_result(signer)
    bridge = FakeBootstrapBridge(bootstrap)

    async def fake_platform_signer_address(_config: PredictConfig) -> str:
        return signer

    monkeypatch.setattr(
        "lib.wallet_manager._platform_signer_address",
        fake_platform_signer_address,
    )

    manager = WalletManager(config, bridge_factory=lambda _config: bridge)
    snapshot = manager.bootstrap_vault(confirm=False)

    assert snapshot.backfill_env is None
    assert bridge.calls[0]["authority"] == signer


def test_bootstrap_vault_backfills_resolved_authority_when_unconfigured(
    monkeypatch,
) -> None:
    config = mandated_vault_config()
    assert config.mandated_vault_authority is None

    signer = "0x" + "55" * 20
    bootstrap = make_bootstrap_result(signer)
    bridge = FakeBootstrapBridge(bootstrap)

    async def fake_platform_signer_address(_config: PredictConfig) -> str:
        return signer

    monkeypatch.setattr(
        "lib.wallet_manager._platform_signer_address",
        fake_platform_signer_address,
    )

    manager = WalletManager(config, bridge_factory=lambda _config: bridge)
    snapshot = manager.bootstrap_vault(confirm=True)

    assert snapshot.backfill_env is not None
    assert snapshot.backfill_env["ERC_MANDATED_VAULT_AUTHORITY"] == signer
    assert snapshot.backfill_env["ERC_MANDATED_VAULT_AUTHORITY"] != "None"
    assert bridge.calls[0]["authority"] == signer

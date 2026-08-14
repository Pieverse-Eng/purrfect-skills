from __future__ import annotations

import os

from typing import Any

import pytest
from predict_sdk import ADDRESSES_BY_CHAIN_ID

from lib.auth import AuthRequest, PredictAuthenticator
from lib.config import ConfigError, PredictConfig
from lib.platform_wallet import PlatformWalletClient
from lib.predict_account import (
    PREDICT_ACCOUNT_OWNER_MISMATCH_CODE,
    PREDICT_ACCOUNT_OWNER_UNREADABLE_CODE,
    _eip191_text_hash_hex,
    predict_account_auth_signature,
    predict_account_digest_hex,
    predict_account_signature_for_hash,
    validate_predict_account_ownership,
)


def predict_account_config() -> PredictConfig:
    return PredictConfig.from_env(
        {
            "PREDICT_ENV": "testnet",
            "PREDICT_STORAGE_DIR": os.environ["PREDICT_STORAGE_DIR"],
            "PREDICT_WALLET_MODE": "predict-account",
            "PREDICT_ACCOUNT_ADDRESS": "0x" + "11" * 20,
            "WALLET_API_URL": "http://wallet.test",
            "WALLET_API_TOKEN": "wallet-token",
            "INSTANCE_ID": "instance-1",
            "WALLET_CHAIN_ID": "97",
        }
    )


def test_predict_account_digest_wraps_order_hash_with_kernel_domain() -> None:
    message_hash_hex = "0x" + "ab" * 32
    account = "0x" + "11" * 20

    digest = predict_account_digest_hex(
        message_hash_hex=message_hash_hex,
        chain_id=97,
        predict_account_address=account,
    )

    assert digest.startswith("0x")
    assert len(digest) == 66
    assert digest != message_hash_hex


def test_eip191_text_hash_uses_sdk_fixed_vector() -> None:
    assert _eip191_text_hash_hex("sign into predict.fun") == (
        "0xedaa95e3abb711d9403cd7a0553b7d914ed4d0497e1edb78dfa3bd86bcf54aa0"
    )


def test_predict_account_signature_requests_hex_encoding_and_prefixes_validator(
    monkeypatch,
) -> None:
    config = predict_account_config()
    captured: dict[str, Any] = {}
    signature = "0x" + "cd" * 65

    def fake_sign_message(
        self: Any, message: str, message_encoding: str | None = None
    ) -> dict[str, str]:
        captured["message"] = message
        captured["message_encoding"] = message_encoding or ""
        return {"address": config.predict_account_address or "", "signature": signature}

    monkeypatch.setattr(PlatformWalletClient, "sign_message", fake_sign_message)
    monkeypatch.setattr(
        "lib.predict_account.validate_predict_account_ownership",
        lambda config: config.predict_account_address or "",
    )

    raw_message_hash_hex = _eip191_text_hash_hex("sign into predict.fun")
    result = predict_account_signature_for_hash(
        config=config,
        raw_message_hash_hex=raw_message_hash_hex,
    )

    assert captured["message_encoding"] == "hex"
    assert captured["message"].startswith("0x")
    expected_digest = predict_account_digest_hex(
        message_hash_hex=raw_message_hash_hex,
        chain_id=97,
        predict_account_address=config.predict_account_address or "",
    )
    assert captured["message"] == "0x" + bytes.fromhex(expected_digest[2:]).hex()
    validator = ADDRESSES_BY_CHAIN_ID[97].ECDSA_VALIDATOR
    assert result == "0x01" + validator[2:] + signature[2:]


def test_predict_account_ownership_match_returns_signer_address(monkeypatch) -> None:
    config = predict_account_config()
    owner = config.predict_account_address or ""

    monkeypatch.setattr(
        "lib.predict_account._platform_wallet_address",
        lambda _config: owner,
    )
    monkeypatch.setattr(
        "lib.predict_account._predict_account_onchain_owner",
        lambda _config: owner,
    )

    assert validate_predict_account_ownership(config) == owner


def test_predict_account_ownership_mismatch_fails_closed(monkeypatch) -> None:
    config = predict_account_config()
    owner = config.predict_account_address or ""
    other = "0x" + "ab" * 20

    monkeypatch.setattr(
        "lib.predict_account._platform_wallet_address",
        lambda _config: other,
    )
    monkeypatch.setattr(
        "lib.predict_account._predict_account_onchain_owner",
        lambda _config: owner,
    )

    with pytest.raises(ConfigError) as error:
        validate_predict_account_ownership(config)

    assert PREDICT_ACCOUNT_OWNER_MISMATCH_CODE in str(error.value)


def test_predict_account_ownership_unreadable_fails_closed(monkeypatch) -> None:
    config = predict_account_config()

    monkeypatch.setattr(
        "lib.predict_account._platform_wallet_address",
        lambda _config: config.predict_account_address or "",
    )

    def _raise_rpc_error(_config: PredictConfig) -> str:
        raise RuntimeError("rpc unavailable")

    monkeypatch.setattr(
        "lib.predict_account._predict_account_onchain_owner",
        _raise_rpc_error,
    )

    with pytest.raises(ConfigError) as error:
        validate_predict_account_ownership(config)

    assert PREDICT_ACCOUNT_OWNER_UNREADABLE_CODE in str(error.value)


def test_predict_account_auth_signature_requests_valid_hex_digest(
    monkeypatch,
) -> None:
    config = predict_account_config()
    captured: dict[str, Any] = {}
    signature = "0x" + "cd" * 65

    def fake_sign_message(
        self: Any, message: str, message_encoding: str | None = None
    ) -> dict[str, str]:
        captured["message"] = message
        captured["message_encoding"] = message_encoding or ""
        return {"address": config.predict_account_address or "", "signature": signature}

    monkeypatch.setattr(PlatformWalletClient, "sign_message", fake_sign_message)
    monkeypatch.setattr(
        "lib.predict_account.validate_predict_account_ownership",
        lambda config: config.predict_account_address or "",
    )

    result = predict_account_auth_signature("sign into predict.fun", config)

    assert captured["message_encoding"] == "hex"
    assert captured["message"].startswith("0x")
    assert not captured["message"].startswith("0x0x")
    expected_digest = predict_account_digest_hex(
        message_hash_hex=_eip191_text_hash_hex("sign into predict.fun"),
        chain_id=97,
        predict_account_address=config.predict_account_address or "",
    )
    assert captured["message"] == "0x" + bytes.fromhex(expected_digest[2:]).hex()
    validator = ADDRESSES_BY_CHAIN_ID[97].ECDSA_VALIDATOR
    assert result == "0x01" + validator[2:] + signature[2:]


class FakeAuthApi:
    def __init__(self, message: str, token: str) -> None:
        self.message = message
        self.token = token
        self.auth_requests: list[AuthRequest] = []

    async def get_auth_message(self) -> Any:
        return type("Message", (), {"message": self.message})()

    async def get_jwt(self, auth_request: AuthRequest) -> Any:
        self.auth_requests.append(auth_request)
        return type("Jwt", (), {"token": self.token})()


@pytest.mark.asyncio
async def test_predict_account_auth_uses_account_address_as_signer(monkeypatch) -> None:
    config = predict_account_config()
    fixed_signature = "0x" + "ef" * 65

    monkeypatch.setattr(
        "lib.auth.predict_account_auth_signature",
        lambda message, cfg: fixed_signature,
    )

    api = FakeAuthApi("sign into predict.fun", "jwt-123")
    authenticator = PredictAuthenticator(config, api)

    token = await authenticator.get_jwt()

    assert token == "jwt-123"
    assert len(api.auth_requests) == 1
    request = api.auth_requests[0]
    assert request.signer == config.predict_account_address
    assert request.message == "sign into predict.fun"
    assert request.signature == fixed_signature

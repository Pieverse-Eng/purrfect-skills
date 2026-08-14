from __future__ import annotations

import os

import json
from dataclasses import dataclass

import httpx
import pytest
import respx
from predict_sdk import BuildOrderInput, Side

from lib.config import ConfigError, PredictConfig
from lib.platform_wallet import PlatformWalletClient, PlatformWalletError, WalletAddress
from lib.platform_sdk import PlatformWalletSdk, _SignerlessOrderBuilder


WALLET_API_URL = "https://wallet.example"
INSTANCE_ID = "inst-123"
TOKEN = "secret-token"


def make_config(**overrides: str) -> PredictConfig:
    env = {
        "PREDICT_ENV": "testnet",
        "PREDICT_STORAGE_DIR": os.environ["PREDICT_STORAGE_DIR"],
        "PREDICT_WALLET_MODE": "eoa",
        "WALLET_API_URL": WALLET_API_URL,
        "WALLET_API_TOKEN": TOKEN,
        "INSTANCE_ID": INSTANCE_ID,
        "WALLET_CHAIN_ID": "97",
    }
    env.update(overrides)
    return PredictConfig.from_env(env)


def instance_path(suffix: str) -> str:
    return f"{WALLET_API_URL}/v1/instances/{INSTANCE_ID}{suffix}"


def test_platform_eoa_config_is_detected_as_eoa() -> None:
    config = make_config()
    assert config.platform_signer_configured is True
    assert config.wallet_mode.value == "eoa"
    assert config.wallet_api_token_value == TOKEN


@respx.mock
def test_get_wallet_address_uses_bearer_and_query() -> None:
    route = respx.get(instance_path("/wallet")).mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": {
                    "address": "0x1111111111111111111111111111111111111111",
                    "chainId": 97,
                    "chainType": "ethereum",
                },
            },
        )
    )
    client = PlatformWalletClient(make_config())
    address = client.get_wallet_address()
    client.close()

    assert route.called
    request = route.calls.last.request
    assert request.url.params["chain_type"] == "ethereum"
    assert request.headers["Authorization"] == f"Bearer {TOKEN}"
    assert address == WalletAddress(
        address="0x1111111111111111111111111111111111111111",
        chain_id=97,
        chain_type="ethereum",
    )


@respx.mock
def test_sign_message_posts_eip191_body() -> None:
    route = respx.post(instance_path("/wallet/sign")).mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": {
                    "address": "0x1111111111111111111111111111111111111111",
                    "signature": "0xabc123",
                    "chainType": "ethereum",
                    "message": "sign into predict.fun",
                },
            },
        )
    )
    client = PlatformWalletClient(make_config())
    result = client.sign_message("sign into predict.fun")
    client.close()

    body = json.loads(route.calls.last.request.content)
    assert body["message"] == "sign into predict.fun"
    assert body["chainType"] == "ethereum"
    assert result["signature"] == "0xabc123"


@respx.mock
def test_sign_typed_data_posts_eip712_envelope() -> None:
    route = respx.post(instance_path("/wallet/sign-typed-data")).mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": {
                    "address": "0x1111111111111111111111111111111111111111",
                    "signature": "0xdef456",
                },
            },
        )
    )
    client = PlatformWalletClient(make_config())
    result = client.sign_typed_data(
        {
            "domain": {"name": "Predict", "chainId": 97},
            "types": {"Order": []},
            "primaryType": "Order",
            "message": {"salt": "1"},
        }
    )
    client.close()

    body = json.loads(route.calls.last.request.content)
    assert body["primaryType"] == "Order"
    assert body["domain"] == {"name": "Predict", "chainId": 97}
    assert body["types"] == {"Order": []}
    assert result["signature"] == "0xdef456"


@respx.mock
def test_approve_posts_bounded_decimal_amount_and_decimals() -> None:
    route = respx.post(instance_path("/wallet/approve")).mock(
        return_value=httpx.Response(
            200, json={"ok": True, "data": {"hash": "0xapprove", "amount": "25"}}
        )
    )
    client = PlatformWalletClient(make_config())
    result = client.approve_erc20(
        token_address="0x" + "22" * 20,
        spender="0x" + "33" * 20,
        amount="25",
        chain_id=97,
        decimals=18,
    )
    client.close()

    body = json.loads(route.calls.last.request.content)
    assert body["tokenAddress"] == "0x" + "22" * 20
    assert body["amount"] == "25"
    assert body["decimals"] == 18
    assert result["hash"] == "0xapprove"


@respx.mock
def test_execute_posts_steps() -> None:
    route = respx.post(instance_path("/wallet/execute")).mock(
        return_value=httpx.Response(
            200, json={"ok": True, "data": {"hash": "0xexecute"}}
        )
    )
    client = PlatformWalletClient(make_config())
    result = client.execute([{"to": "0x" + "44" * 20, "data": "0x"}])
    client.close()

    body = route.calls.last.request.content.decode()
    assert '"steps"' in body
    assert result["hash"] == "0xexecute"


@pytest.mark.parametrize(
    ("status", "json_body"),
    [
        (401, {"ok": False, "error": "unauthorized"}),
        (500, {"ok": False, "error": "boom"}),
        (200, {"ok": False, "error": "policy denied"}),
    ],
)
@respx.mock
def test_platform_wallet_fail_closed_and_redacts_token(
    status: int, json_body: dict[str, object]
) -> None:
    respx.get(instance_path("/wallet")).mock(
        return_value=httpx.Response(status, json=json_body)
    )
    client = PlatformWalletClient(make_config())
    with pytest.raises(PlatformWalletError) as error:
        client.get_wallet_address()
    client.close()

    assert TOKEN not in str(error.value)


@respx.mock
def test_platform_wallet_malformed_json_fails_closed() -> None:
    respx.get(instance_path("/wallet")).mock(
        return_value=httpx.Response(200, text="not-json")
    )
    client = PlatformWalletClient(make_config())
    with pytest.raises(PlatformWalletError):
        client.get_wallet_address()
    client.close()


@dataclass
class FakePlatform:
    address: str = "0x1111111111111111111111111111111111111111"
    signature: str = "0x" + "12" * 65

    def get_wallet_address(self) -> WalletAddress:
        return WalletAddress(address=self.address, chain_id=97, chain_type="ethereum")

    def sign_typed_data(self, typed_data: object) -> dict[str, object]:
        return {"address": self.address, "signature": self.signature}

    def approve_erc20(self, **kwargs: object) -> dict[str, object]:
        return {"ok": True, "sent": kwargs}


def test_signerless_builder_assembles_signed_order() -> None:
    config = make_config()
    platform = FakePlatform()
    builder = _SignerlessOrderBuilder(config, platform)
    order = builder.build_order(
        "MARKET",
        BuildOrderInput(
            side=Side.BUY,
            token_id="123",
            maker_amount="100",
            taker_amount="200",
            fee_rate_bps="0",
        ),
    )
    typed_data = builder.build_typed_data(
        order, is_neg_risk=False, is_yield_bearing=False
    )
    signed = builder.sign_typed_data_order(typed_data)

    assert signed.maker == platform.address
    assert signed.signer == platform.address
    assert signed.signature == platform.signature
    assert signed.hash == builder.build_typed_data_hash(typed_data)


@respx.mock
def test_platform_sdk_set_all_approvals_fails_closed() -> None:
    respx.get(instance_path("/wallet")).mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": {
                    "address": "0x1111111111111111111111111111111111111111",
                    "chainId": 97,
                    "chainType": "ethereum",
                },
            },
        )
    )
    sdk = PlatformWalletSdk(make_config())
    with pytest.raises(ConfigError, match="bounded"):
        sdk.set_all_approvals()


@respx.mock
def test_platform_sdk_bounded_approve_converts_wei_to_decimal() -> None:
    respx.get(instance_path("/wallet")).mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": {
                    "address": "0x1111111111111111111111111111111111111111",
                    "chainId": 97,
                    "chainType": "ethereum",
                },
            },
        )
    )
    approve_route = respx.post(instance_path("/wallet/approve")).mock(
        return_value=httpx.Response(
            200, json={"ok": True, "data": {"hash": "0xapprove"}}
        )
    )
    sdk = PlatformWalletSdk(make_config())
    sdk.approve_usdt(
        amount_wei=25_000_000_000_000_000_000,
        spender="0x" + "33" * 20,
    )

    body = json.loads(approve_route.calls.last.request.content)
    assert body["amount"] == "25"
    assert body["decimals"] == 18


@respx.mock
def test_sign_message_can_request_hex_bytes_encoding() -> None:
    route = respx.post(instance_path("/wallet/sign")).mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": {
                    "address": "0x1111111111111111111111111111111111111111",
                    "signature": "0xabc123",
                    "chainType": "ethereum",
                    "messageEncoding": "hex",
                },
            },
        )
    )
    client = PlatformWalletClient(make_config())
    result = client.sign_message("0x" + "ab" * 32, message_encoding="hex")
    client.close()

    body = json.loads(route.calls.last.request.content)
    assert body["message"] == "0x" + "ab" * 32
    assert body["messageEncoding"] == "hex"
    assert result["signature"] == "0xabc123"


@respx.mock
def test_platform_transfer_native_sends_wallet_transfer_body() -> None:
    route = respx.post(instance_path("/wallet/transfer")).mock(
        return_value=httpx.Response(
            200, json={"ok": True, "data": {"hash": "0xtransfer-native"}}
        )
    )
    client = PlatformWalletClient(make_config())
    result = client.transfer(
        to="0x" + "55" * 20,
        amount="0.25",
        asset_type="native",
        chain_id=97,
    )
    client.close()

    body = json.loads(route.calls.last.request.content)
    assert body["to"] == "0x" + "55" * 20
    assert body["amount"] == "0.25"
    assert body["assetType"] == "native"
    assert body["chainId"] == 97
    assert result["hash"] == "0xtransfer-native"


@respx.mock
def test_platform_transfer_erc20_includes_token_and_decimals() -> None:
    route = respx.post(instance_path("/wallet/transfer")).mock(
        return_value=httpx.Response(
            200, json={"ok": True, "data": {"hash": "0xtransfer-erc20"}}
        )
    )
    client = PlatformWalletClient(make_config())
    client.transfer(
        to="0x" + "66" * 20,
        amount="10",
        asset_type="erc20",
        token_address="0x" + "77" * 20,
        decimals=18,
        chain_id=97,
    )
    client.close()

    body = json.loads(route.calls.last.request.content)
    assert body["assetType"] == "erc20"
    assert body["tokenAddress"] == "0x" + "77" * 20
    assert body["decimals"] == 18

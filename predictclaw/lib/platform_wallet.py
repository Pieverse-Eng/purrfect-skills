"""Platform wallet application-API client.

The migrated skill never holds or reads private keys. Every signature,
approval, and broadcast goes through the instance-scoped application API
exposed by the Purrfect platform wallet service.

Endpoint contract (authoritative surface, as scoped for this migration):
  GET  /v1/instances/{id}/wallet?chain_type=ethereum
  POST /v1/instances/{id}/wallet/sign
  POST /v1/instances/{id}/wallet/sign-typed-data
  POST /v1/instances/{id}/wallet/approve
  POST /v1/instances/{id}/wallet/execute
  POST /v1/instances/{id}/wallet/sign-transaction  (sign-only, no broadcast)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import httpx

from .config import PredictConfig, redact_text


class PlatformWalletError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        method: str | None = None,
        path: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.method = method
        self.path = path


@dataclass(frozen=True)
class WalletAddress:
    address: str
    chain_id: int | None = None
    chain_type: str = "ethereum"


class PlatformWalletClient:
    def __init__(
        self,
        config: PredictConfig,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self._config = config
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=config.wallet_api_url,
            timeout=config.http_timeout_seconds,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._config.wallet_api_token_value}",
        }

    def _instance_path(self, suffix: str) -> str:
        return f"/v1/instances/{self._config.instance_id}{suffix}"

    # -- reads -----------------------------------------------------------------

    def get_wallet_address(self) -> WalletAddress:
        payload = self._request("GET", self._instance_path("/wallet"), params={"chain_type": "ethereum"})
        data = _extract(payload)
        return WalletAddress(
            address=str(data["address"]),
            chain_id=data.get("chainId"),
            chain_type=str(data.get("chainType", "ethereum")),
        )

    # -- signatures ------------------------------------------------------------

    def sign_message(
        self,
        message: str,
        *,
        message_encoding: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"message": message, "chainType": "ethereum"}
        if message_encoding is not None:
            body["messageEncoding"] = message_encoding
        payload = self._request(
            "POST",
            self._instance_path("/wallet/sign"),
            json=body,
        )
        return _extract(payload)

    def sign_typed_data(self, typed_data: Mapping[str, Any]) -> dict[str, Any]:
        payload = self._request(
            "POST",
            self._instance_path("/wallet/sign-typed-data"),
            json={
                "domain": typed_data["domain"],
                "types": typed_data["types"],
                "primaryType": typed_data["primaryType"],
                "message": typed_data["message"],
            },
        )
        return _extract(payload)

    def sign_transaction(self, txs: list[dict[str, Any]], chain_id: int) -> dict[str, Any]:
        payload = self._request(
            "POST",
            self._instance_path("/wallet/sign-transaction"),
            json={"txs": txs, "chainId": chain_id},
        )
        return _extract(payload)

    # -- writes ----------------------------------------------------------------

    def approve_erc20(
        self,
        *,
        token_address: str,
        spender: str,
        amount: str,
        chain_id: int,
        decimals: int | None = None,
    ) -> dict[str, Any]:
        payload = self._request(
            "POST",
            self._instance_path("/wallet/approve"),
            json={
                "tokenAddress": token_address,
                "spender": spender,
                "amount": amount,
                "chainId": chain_id,
                **({"decimals": decimals} if decimals is not None else {}),
            },
        )
        return _extract(payload)

    def execute(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        payload = self._request(
            "POST",
            self._instance_path("/wallet/execute"),
            json={"steps": steps},
        )
        return _extract(payload)

    def transfer(
        self,
        *,
        to: str,
        amount: str,
        asset_type: str = "native",
        token_address: str | None = None,
        decimals: int | None = None,
        chain_id: int | None = None,
        chain_type: str = "ethereum",
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "to": to,
            "amount": amount,
            "assetType": asset_type,
            "chainType": chain_type,
        }
        if token_address is not None:
            body["tokenAddress"] = token_address
        if decimals is not None:
            body["decimals"] = decimals
        if chain_id is not None:
            body["chainId"] = chain_id
        payload = self._request(
            "POST",
            self._instance_path("/wallet/transfer"),
            json=body,
        )
        return _extract(payload)

    # -- transport -------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = self._client.request(
                method, path, headers=self._headers, params=params, json=json
            )
        except httpx.HTTPError as error:
            raise PlatformWalletError(
                redact_text(f"platform wallet transport error during {method} {path}: {error}", self._secrets()),
                method=method,
                path=path,
            ) from error

        body = response.text[:240]
        if response.is_error:
            raise PlatformWalletError(
                redact_text(
                    f"platform wallet request failed for {method} {path} "
                    f"with status {response.status_code}: {body}",
                    self._secrets(),
                ),
                status_code=response.status_code,
                method=method,
                path=path,
            )
        try:
            payload = response.json()
        except ValueError as error:
            raise PlatformWalletError(
                redact_text(
                    f"platform wallet returned non-JSON for {method} {path}: {body}",
                    self._secrets(),
                ),
                status_code=response.status_code,
                method=method,
                path=path,
            ) from error
        if not isinstance(payload, dict) or payload.get("ok") is not True:
            raise PlatformWalletError(
                redact_text(
                    f"platform wallet rejected {method} {path}: {body}",
                    self._secrets(),
                ),
                status_code=response.status_code,
                method=method,
                path=path,
            )
        return payload

    def _secrets(self) -> list[str | None]:
        return [self._config.wallet_api_token_value]


def _extract(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return payload

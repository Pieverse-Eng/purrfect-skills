from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from .config import ConfigError, PredictConfig, WalletMode
from .models import AuthMessageResponse, AuthRequest, JwtResponse
from .platform_wallet import PlatformWalletClient
from .predict_account import predict_account_auth_signature


class AuthApiClientProtocol(Protocol):
    async def get_auth_message(self) -> AuthMessageResponse: ...
    async def get_jwt(self, auth_request: AuthRequest) -> JwtResponse: ...


def _make_platform_wallet_client(config: PredictConfig) -> PlatformWalletClient:
    return PlatformWalletClient(config)


class PredictAuthenticator:
    def __init__(
        self,
        config: PredictConfig,
        api_client: AuthApiClientProtocol,
        *,
        platform_client_factory: Callable[[PredictConfig], PlatformWalletClient]
        | None = None,
    ) -> None:
        self._config = config
        self._api_client = api_client
        self._platform_client_factory = (
            platform_client_factory or _make_platform_wallet_client
        )
        self._jwt_cache: dict[str, str] = {}

    async def get_jwt(self, *, force_refresh: bool = False) -> str:
        signer = self._signer_cache_key()
        if signer is None:
            raise ConfigError(
                "Authenticated predict.fun actions require the platform wallet API "
                "(WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID)."
            )

        cache_key = f"{self._config.env.value}:{signer}"
        if not force_refresh and cache_key in self._jwt_cache:
            return self._jwt_cache[cache_key]

        auth_message = await self._api_client.get_auth_message()
        auth_request = self.build_auth_request(auth_message.message)
        jwt_response = await self._api_client.get_jwt(auth_request)
        self._jwt_cache[cache_key] = jwt_response.token
        return jwt_response.token

    def _signer_cache_key(self) -> str | None:
        if self._config.platform_signer_configured:
            if self._config.wallet_mode == WalletMode.PREDICT_ACCOUNT:
                return f"predict-account:{self._config.instance_id}"
            return f"platform:{self._config.instance_id}"
        return None

    def build_auth_request(self, message: str) -> AuthRequest:
        if not self._config.platform_signer_configured:
            raise ConfigError(
                "Authenticated predict.fun actions require the platform wallet API "
                "(WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID)."
            )

        platform = self._platform_client_factory(self._config)
        try:
            if self._config.wallet_mode == WalletMode.PREDICT_ACCOUNT:
                signer = self._config.predict_account_address
                if not signer:
                    raise ConfigError(
                        "Predict Account mode requires PREDICT_ACCOUNT_ADDRESS."
                    )
                signature = predict_account_auth_signature(message, self._config)
                return AuthRequest(signer=signer, message=message, signature=signature)

            signed = platform.sign_message(message)
            signer = str(signed.get("address") or "")
            signature = str(signed.get("signature") or "")
            if not signer or not signature:
                raise ConfigError("Platform wallet sign returned no address/signature.")
            return AuthRequest(signer=signer, message=message, signature=signature)
        finally:
            platform.close()

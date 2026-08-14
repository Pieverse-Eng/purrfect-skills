"""Signer-less SDK facade backed by the platform wallet application API.

Keeps all local computation (order amount, order build, EIP-712 typed data,
EIP-712 hash) in `predict_sdk`, while every signature / approval / broadcast is
delegated to `PlatformWalletClient`. No private key is ever read or held here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from eth_account import Account
from predict_sdk import (
    ADDRESSES_BY_CHAIN_ID,
    ChainId,
    OrderBuilder,
    OrderBuilderOptions,
    SignedOrder,
)
from predict_sdk._internal.contracts import make_contracts
from predict_sdk.constants import RPC_URLS_BY_CHAIN_ID, Side, SignatureType
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from .config import ConfigError, PredictConfig, RuntimeEnv, WalletMode
from .platform_wallet import PlatformWalletClient
from .predict_account import predict_account_signature_for_hash


class _SignerlessOrderBuilder:
    """Minimal predict_sdk.OrderBuilder surface for order construction/signing."""

    def __init__(self, config: PredictConfig, platform: PlatformWalletClient) -> None:
        self._config = config
        self._platform = platform
        self._address = _platform_address(platform)
        self._predict_account = (
            config.predict_account_address
            if config.wallet_mode == WalletMode.PREDICT_ACCOUNT
            else None
        )
        self._builder = OrderBuilder.make(
            config.chain_id,
            None,
            OrderBuilderOptions(predict_account=self._predict_account),
        )

    def get_market_order_amounts(self, data: Any, book: Any) -> Any:
        return self._builder.get_market_order_amounts(data, book)

    def get_limit_order_amounts(self, data: Any) -> Any:
        return self._builder.get_limit_order_amounts(data)

    def build_order(self, strategy: Literal["MARKET", "LIMIT"], data: Any) -> Any:
        order_identity = self._predict_account or self._address
        if data.maker is None:
            data.maker = order_identity
        if data.signer is None:
            data.signer = order_identity
        return self._builder.build_order(strategy, data)

    def build_typed_data(self, order: Any, *, is_neg_risk: bool, is_yield_bearing: bool) -> Any:
        return self._builder.build_typed_data(
            order, is_neg_risk=is_neg_risk, is_yield_bearing=is_yield_bearing
        )

    def build_typed_data_hash(self, typed_data: Any) -> str:
        return self._builder.build_typed_data_hash(typed_data)

    def sign_typed_data_order(self, typed_data: Any) -> SignedOrder:
        message = typed_data.message
        order_hash = self.build_typed_data_hash(typed_data)
        if self._predict_account is not None:
            signature = predict_account_signature_for_hash(
                config=self._config,
                raw_message_hash_hex=order_hash,
            )
        else:
            envelope = {
                "domain": typed_data.domain,
                "types": typed_data.types,
                "primaryType": typed_data.primary_type,
                "message": typed_data.message,
            }
            signed = self._platform.sign_typed_data(envelope)
            signature = str(signed["signature"])

        return SignedOrder(
            salt=str(message["salt"]),
            maker=message["maker"],
            signer=message["signer"],
            taker=message["taker"],
            token_id=str(message["tokenId"]),
            maker_amount=str(message["makerAmount"]),
            taker_amount=str(message["takerAmount"]),
            expiration=str(message["expiration"]),
            nonce=str(message["nonce"]),
            fee_rate_bps=str(message["feeRateBps"]),
            side=message["side"],
            signature_type=message["signatureType"],
            signature=signature,
            hash=order_hash,
        )


def _platform_address(platform: PlatformWalletClient) -> str:
    return platform.get_wallet_address().address


class PlatformWalletSdk:
    def __init__(self, config: PredictConfig) -> None:
        self._config = config
        if not config.platform_signer_configured:
            raise ConfigError(
                "EOA mode requires the platform wallet API "
                "(WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID)."
            )
        self._platform = PlatformWalletClient(config)
        self._builder = _SignerlessOrderBuilder(config, self._platform)
        self._web3 = self._make_web3(config)

    @staticmethod
    def _make_web3(config: PredictConfig) -> Web3:
        chain_id = config.chain_id
        web3 = Web3(Web3.HTTPProvider(RPC_URLS_BY_CHAIN_ID[chain_id]))
        if chain_id in (ChainId.BNB_MAINNET, ChainId.BNB_TESTNET):
            web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        return web3

    @property
    def mode(self) -> WalletMode:
        return self._config.wallet_mode

    @property
    def signer_address(self) -> str:
        return self._platform.get_wallet_address().address

    @property
    def funding_address(self) -> str:
        if self._config.wallet_mode == WalletMode.PREDICT_ACCOUNT:
            return self._config.predict_account_address or self.signer_address
        return self.signer_address

    @property
    def chain_name(self) -> str:
        return "BNB Mainnet" if self._config.env == RuntimeEnv.MAINNET else "BNB Testnet"

    def transfer_usdt(self, destination: str, amount_wei: int) -> dict[str, Any]:
        if amount_wei <= 0:
            raise ConfigError("USDT withdrawal amount must be greater than zero.")
        addresses = ADDRESSES_BY_CHAIN_ID[self._config.chain_id]
        return self._platform.transfer(
            to=destination,
            amount=str(Web3.from_wei(amount_wei, "ether")),
            asset_type="erc20",
            token_address=addresses.USDT,
            decimals=18,
            chain_id=int(self._config.wallet_chain_id or self._config.chain_id),
        )

    def transfer_bnb(self, destination: str, amount_wei: int) -> dict[str, Any]:
        if amount_wei <= 0:
            raise ConfigError("BNB withdrawal amount must be greater than zero.")
        return self._platform.transfer(
            to=destination,
            amount=str(Web3.from_wei(amount_wei, "ether")),
            asset_type="native",
            chain_id=int(self._config.wallet_chain_id or self._config.chain_id),
        )

    def get_bnb_balance_wei(self) -> int:
        return int(self._web3.eth.get_balance(self.funding_address))

    def get_usdt_balance_wei(self) -> int:
        contracts = make_contracts(self._web3, ADDRESSES_BY_CHAIN_ID[self._config.chain_id])
        return int(contracts.usdt.functions.balanceOf(self.funding_address).call())

    def get_approval_snapshot(self) -> Any:
        from .wallet_manager import ApprovalSnapshot

        contracts = make_contracts(self._web3, ADDRESSES_BY_CHAIN_ID[self._config.chain_id])
        owner = self.funding_address
        usdt = contracts.usdt
        ct = contracts.conditional_tokens
        exchange = contracts.ctf_exchange
        neg_exchange = contracts.neg_risk_ctf_exchange
        adapter = contracts.neg_risk_adapter
        allowance = int(usdt.functions.allowance(owner, exchange.address).call()) > 0
        return ApprovalSnapshot(
            standard_exchange_approval=bool(ct.functions.isApprovedForAll(owner, exchange.address).call()),
            standard_exchange_allowance=allowance,
            standard_neg_risk_exchange_approval=bool(ct.functions.isApprovedForAll(owner, neg_exchange.address).call()),
            standard_neg_risk_exchange_allowance=bool(usdt.functions.allowance(owner, neg_exchange.address).call() > 0),
            standard_neg_risk_adapter_approval=bool(ct.functions.isApprovedForAll(owner, adapter.address).call()),
            yield_exchange_approval=False,
            yield_exchange_allowance=False,
            yield_neg_risk_exchange_approval=False,
            yield_neg_risk_exchange_allowance=False,
            yield_neg_risk_adapter_approval=False,
        )

    def set_all_approvals(self) -> dict[str, Any]:
        raise ConfigError(
            "wallet approve is not available with the platform wallet API: "
            "approvals must be bounded to the requested order amount. "
            "Place an order to trigger the required bounded approval."
        )

    def get_usdt_allowance_wei(
        self,
        *,
        spender: str | None = None,
        is_neg_risk: bool = False,
        is_yield_bearing: bool = False,
    ) -> int:
        """Return the current bounded USDT allowance for the relevant exchange."""
        addresses = ADDRESSES_BY_CHAIN_ID[self._config.chain_id]
        contracts = make_contracts(self._web3, addresses)
        if spender is None:
            from .wallet_manager import get_exchange_contract

            spender = get_exchange_contract(
                contracts,
                is_neg_risk=is_neg_risk,
                is_yield_bearing=is_yield_bearing,
            ).address
        return int(
            contracts.usdt.functions.allowance(self.funding_address, spender).call()
        )

    def approve_usdt(
        self,
        *,
        amount_wei: int,
        spender: str | None = None,
        is_neg_risk: bool = False,
        is_yield_bearing: bool = False,
    ) -> dict[str, Any]:
        """Approve a bounded USDT allowance to a predict.fun exchange spender.

        ``amount_wei`` is the raw token amount. BSC USDT has 18 decimals and the
        platform approve endpoint takes a decimal token amount (with explicit
        ``decimals``), so raw units are converted here. This never requests an
        unlimited allowance.
        """
        if amount_wei <= 0:
            raise ConfigError("Approve amount must be greater than zero.")
        chain_id = int(self._config.wallet_chain_id or self._config.chain_id)
        addresses = ADDRESSES_BY_CHAIN_ID[self._config.chain_id]
        from .wallet_manager import get_exchange_contract

        if spender is None:
            contracts = make_contracts(self._web3, addresses)
            spender = get_exchange_contract(
                contracts,
                is_neg_risk=is_neg_risk,
                is_yield_bearing=is_yield_bearing,
            ).address
        amount_decimal = str(Web3.from_wei(amount_wei, "ether"))
        return self._platform.approve_erc20(
            token_address=addresses.USDT,
            spender=spender,
            amount=amount_decimal,
            chain_id=chain_id,
            decimals=18,
        )

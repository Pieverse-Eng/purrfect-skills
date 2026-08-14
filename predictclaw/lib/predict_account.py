"""EIP-712 / EIP-191 Predict Account signing helpers.

The platform wallet service owns the signing key. This module computes the
Kernel wrapper digest locally and asks the platform ``/wallet/sign`` endpoint
to sign those raw bytes with ``messageEncoding: "hex"``. It never reads or
constructs a raw private key.
"""

from __future__ import annotations

from typing import Any

from eth_account.messages import _hash_eip191_message, encode_defunct
from predict_sdk import ADDRESSES_BY_CHAIN_ID, ChainId, KERNEL_DOMAIN_BY_CHAIN_ID
from predict_sdk._internal import eip712_wrap_hash
from predict_sdk._internal.contracts import make_contracts
from predict_sdk.constants import RPC_URLS_BY_CHAIN_ID
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from .config import ConfigError, PredictConfig
from .platform_wallet import PlatformWalletClient

PREDICT_ACCOUNT_OWNER_MISMATCH_CODE = "predict-account-owner-mismatch"
PREDICT_ACCOUNT_OWNER_UNREADABLE_CODE = "predict-account-owner-unreadable"


def _eip191_text_hash_hex(message: str) -> str:
    return "0x" + _hash_eip191_message(encode_defunct(text=message)).hex()


def predict_account_digest_hex(
    *,
    message_hash_hex: str,
    chain_id: int,
    predict_account_address: str,
) -> str:
    domain = {
        **KERNEL_DOMAIN_BY_CHAIN_ID[chain_id],
        "verifyingContract": predict_account_address,
    }
    return eip712_wrap_hash(message_hash_hex, domain)


def _make_predict_chain_web3(chain_id: int) -> Web3:
    web3 = Web3(Web3.HTTPProvider(RPC_URLS_BY_CHAIN_ID[chain_id]))
    if chain_id in (ChainId.BNB_MAINNET, ChainId.BNB_TESTNET):
        web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return web3


def _platform_wallet_address(config: PredictConfig) -> str:
    platform = PlatformWalletClient(config)
    try:
        return platform.get_wallet_address().address
    finally:
        platform.close()


def _predict_account_onchain_owner(config: PredictConfig) -> str:
    chain_id = int(config.wallet_chain_id or config.chain_id)
    web3 = _make_predict_chain_web3(chain_id)
    contracts = make_contracts(web3, ADDRESSES_BY_CHAIN_ID[chain_id])
    owner = contracts.ecdsa_validator.functions.ecdsaValidatorStorage(
        config.predict_account_address
    ).call()
    return Web3.to_checksum_address(str(owner))


def validate_predict_account_ownership(config: PredictConfig) -> str:
    """Fail-close that the platform wallet signer is the on-chain owner."""
    signer_address = _platform_wallet_address(config)
    try:
        owner = _predict_account_onchain_owner(config)
    except Exception as error:
        raise ConfigError(
            "predict-account ownership validation: "
            f"{PREDICT_ACCOUNT_OWNER_UNREADABLE_CODE}. Could not read the "
            "on-chain ECDSA validator owner for "
            f"{config.predict_account_address}; refusing to sign. {error}"
        ) from error

    if Web3.to_checksum_address(owner) != Web3.to_checksum_address(signer_address):
        raise ConfigError(
            "predict-account ownership validation: "
            f"{PREDICT_ACCOUNT_OWNER_MISMATCH_CODE}. Platform wallet signer "
            f"{signer_address} is not the on-chain owner {owner} of Predict "
            f"Account {config.predict_account_address}; refusing to sign."
        )
    return signer_address


def predict_account_signature_for_hash(
    *,
    config: PredictConfig,
    raw_message_hash_hex: str,
) -> str:
    if config.wallet_mode.value != "predict-account":
        raise ValueError("Predict Account signing requires predict-account mode.")
    if not config.predict_account_address:
        raise ValueError("Predict Account signing requires PREDICT_ACCOUNT_ADDRESS.")
    if not config.platform_signer_configured:
        raise ValueError("Predict Account signing requires the platform wallet API.")

    validate_predict_account_ownership(config)

    digest_hex = predict_account_digest_hex(
        message_hash_hex=raw_message_hash_hex,
        chain_id=int(config.wallet_chain_id or config.chain_id),
        predict_account_address=config.predict_account_address,
    )
    digest_bytes = bytes.fromhex(digest_hex[2:])
    platform = PlatformWalletClient(config)
    try:
        signed = platform.sign_message(
            "0x" + digest_bytes.hex(),
            message_encoding="hex",
        )
    finally:
        platform.close()

    signature = str(signed.get("signature") or "")
    if not signature:
        raise ValueError("Platform wallet returned no signature for Predict Account bytes.")
    validator_address = ADDRESSES_BY_CHAIN_ID[config.chain_id].ECDSA_VALIDATOR
    return "0x01" + validator_address[2:] + signature[2:] if signature.startswith("0x") else signature


def predict_account_auth_signature(message: str, config: PredictConfig) -> str:
    return predict_account_signature_for_hash(
        config=config,
        raw_message_hash_hex=_eip191_text_hash_hex(message),
    )

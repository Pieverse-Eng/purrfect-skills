# Sui

Use this reference for the user's Sui wallet: address, balances, transfers,
Cetus swaps, personal-message signing, and executing a prepared Sui
transaction. Sui runs on **mainnet only**, through the platform wallet: the
platform builds and policy-checks every send, and the TEE signs and broadcasts
it. There is no raw-signing or self-broadcast path; do not look for one.

The Sui wallet is separate from the EVM and Solana wallets. Its address is
`0x` followed by 64 hex characters. Select Sui with `--chain-type sui` (or
`--chain sui`).

## Coins

| Coin | Identifier | Decimals |
| --- | --- | ---: |
| SUI (native / gas) | `SUI` | 9 |
| USDC (Circle, native) | `USDC` = `0xdba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC` | 6 |
| Any other coin | Full coin type `0x<package>::<module>::<NAME>` | From chain metadata |

- A coin type's module and type names are case-sensitive; copy them exactly.
- Do not guess a coin type from a symbol. If the user names an unfamiliar coin,
  ask for its full coin type or resolve it from a trusted source, and confirm
  it before sending.
- Decimals always come from chain metadata. Never pass `--decimals` or
  `--chain-id` for Sui.

## Address and balances

```bash
purr wallet address --chain-type sui                                    # Sui wallet address
purr wallet balance --chain-type sui                                    # SUI
purr wallet balance --chain-type sui --token USDC                       # USDC
purr wallet balance --chain-type sui --token 0x...::module::NAME         # any coin, by full coin type
```

The balance response reports `balance`, `spendableBalance` (coin objects) and
`addressBalance`. Transfers and swaps can spend `spendableBalance` only.

## Transfers

```bash
purr wallet transfer --chain-type sui --to <0x + 64 hex> --amount 0.1                   # SUI
purr wallet transfer --chain-type sui --to <0x + 64 hex> --amount 5 --token USDC        # USDC
purr wallet transfer --chain-type sui --to <0x + 64 hex> --amount 1 --token 0x...::m::N  # any coin
```

- **Recipient:** must be the full 32-byte address (`0x` + 64 hex). A short or
  truncated address such as `0x123` is refused rather than padded, because
  padding would turn a mistyped paste into a different valid address.
- **`.pie` handles:** they resolve to EVM and Solana wallets only. To send on
  Sui, ask for the recipient's raw Sui address.
- **Gas:** keep some SUI for gas, even when sending USDC or another coin.

The response includes `hash` (the transaction digest), `operationId` and
`replayed`. The explorer link is `https://suiscan.xyz/mainnet/tx/<hash>`.

## Swaps (Cetus aggregator)

Always quote first, show the user the quote, and execute only after they
confirm it.

```bash
# Quote (no transaction)
purr wallet sui-swap --from SUI --to USDC --amount 0.5
purr wallet sui-swap --from USDC --to SUI --amount 10 --slippage 1

# Execute after confirmation, keeping the quoted floor
purr wallet sui-swap --from SUI --to USDC --amount 0.5 --slippage 0.5 --min-amount-out <MIN_OUT_RAW> --execute

# Any coin by full coin type
purr wallet sui-swap --from SUI --to 0x...::module::NAME --amount 0.2
```

- `--from` / `--to` accept `SUI`, `USDC`, or a full coin type. `--amount` is
  in the input coin's units.
- `--slippage <percent>` sets the tolerance, as in `purr wallet uniswap`
  (default 0.5, at most 50, up to two decimals).
- `--min-amount-out <raw_amount>` is the minimum output in the output coin's
  raw base units. Pass the confirmed quote's `minAmountOutBaseUnits` string
  verbatim (not `minAmountOut`, which is in whole-coin units). Execution
  re-quotes and refuses a route below that floor.
- Tell the user the quote's `estimatedAmountOut`, minimum output, and route.
  The execution result reports the confirmed `amountOut`.
- Some routes pass through Aftermath pools, which charge a small protocol fee
  (0.05%). Part of that fee goes to a third-party address, so it shows up in
  the transaction's balance changes. This is expected.

## Personal-message signing

```bash
purr wallet sign --chain-type sui --address <sui-address> --message "<message>"
```

This signs a Sui personal message, for example for a login. A message
signature cannot be used as a transaction signature.

## Executing a prepared transaction

Use this only for a Sui transaction the user or a protocol has already built
as base64 BCS `TransactionData`, with the agent's Sui wallet as sender:

```bash
purr wallet sui-execute --tx-file ./tx.b64
purr wallet sui-execute --tx-bytes <base64>
```

- With wallet policy active, the platform simulates the bytes and checks what
  they would actually do: coins spent, recipients, and Move packages called.
- A call to a package the policy does not recognize may be refused as
  `unknown_contract_call` or `blind_signing`.
- Resubmitting identical bytes returns the earlier result; it does not send
  again.
- Build each transaction against current chain state. Before building the next
  one, wait until the previous transaction is visible on the fullnode.
  Otherwise the new bytes reuse coin versions that were already consumed, and
  the chain rejects them.

## Retries, approvals and errors

Every Sui transfer and swap execution carries an Idempotency-Key. It is
returned as `operationId`, or as `idempotencyKey` in the error. Rerunning a
command with `--idempotency-key <key>` resumes that same operation; it never
creates a second one.

| Result | Meaning | What to do |
| --- | --- | --- |
| `POLICY_DEFERRED` (with `requestId`, `idempotencyKey`) | Wallet policy requires the owner's approval | Tell the user it awaits approval. Once approved, rerun the same command with `--idempotency-key <idempotencyKey>`. |
| `POLICY_DENIED` with a `reason` (`per_tx_cap_exceeded`, `cumulative_spend_exceeded`, `velocity_exceeded`, `address_not_allowlisted`, `address_denylisted`, `unknown_contract_call`, `blind_signing`, `wallet_frozen`, `manual_approval_required`) | Wallet policy refused it; nothing was sent | Report the reason. Do not work around it. |
| `SUI_SUBMISSION_UNKNOWN` (503, with `hash` and `operationId`) | The send may or may not have landed | Rerun the **same** command with `--idempotency-key <operationId>` to reconcile it. Never send again with a new key. |
| `stale_chain_state` (503) | Chain state is still catching up with the wallet's previous transaction | Retry the same command after a few seconds. |
| `SUI_IDENTICAL_REQUEST_PENDING` (409) | An identical transaction from another request awaits approval | Wait until that approval is resolved. |
| `Invalid Sui recipient address` | The recipient is not a full 32-byte address | Ask for the complete address. |
| `insufficient_balance` / `insufficient_gas` | Not enough of the coin, or not enough SUI for gas | Report the balances; do not retry blindly. |
| `unsupported_coin` / `Invalid Sui coin type` / `Unknown Sui coin` | The coin could not be identified | Ask for the exact full coin type. |
| `quote_below_minimum` | The fresh route is below the confirmed floor | Get a new quote and confirm it again. |

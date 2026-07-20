# Deposit and Withdraw

Bridge USDC between **Arbitrum** and Hyperliquid. Confirm every transfer. Minimum
deposit is **5 USDC**. Deposit, withdraw, and withdraw-status require the
Hyperliquid Trading integration to be enabled (see [preflight.md](preflight.md)).

## Commands

```bash
purr hyperliquid deposit --amount <amount>
purr hyperliquid withdraw --amount <amount>
purr hyperliquid withdraw-status --nonce <nonce>
```

`withdraw-status` is a **read** (no confirmation). It checks whether a prior
Hyperliquid withdraw has arrived on-chain by the withdraw `nonce` returned from
`withdraw`.

## Deposit (Arbitrum USDC → Hyperliquid)

Platform behavior:

- Spends **Arbitrum** USDC (`chainId` 42161) from the instance wallet.
- Bridges into Hyperliquid for the **same EVM address**.
- Credits Hyperliquid **perp** collateral (not spot).
- Rejects amounts under **5 USDC**.

### Preflight

```bash
purr wallet address --chain-type ethereum
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
purr hyperliquid account
purr hyperliquid state --kind both
```

Ensure the wallet has enough Arbitrum USDC and gas for the bridge transfer.

### Execute

1. Confirm amount (≥ 5 USDC) and that funds leave Arbitrum for Hyperliquid.
2. Run:

```bash
purr hyperliquid deposit --amount 25
```

3. Report returned fields when present (`bridgeRequestId`, `txHash`, `amount`,
   `status`).
4. Re-check Hyperliquid collateral (crediting can lag the Arbitrum tx):

```bash
purr hyperliquid state --kind both
```

### After Deposit

If the user needs **spot** trading USDC:

```bash
purr hyperliquid usd-class-transfer --amount <amount> --to-perp false
```

If the user needs **builder-dex** collateral (e.g. `xyz`):

```bash
purr hyperliquid send-asset --destination-dex xyz --amount <amount>
```

Both are separate transfers and need their own confirmation — see
[collateral.md](collateral.md).

## Withdraw (Hyperliquid → Arbitrum)

Platform behavior:

- Withdraws USDC from Hyperliquid for the same wallet address.
- Destination is that address on Arbitrum.
- Settlement is not always instant. A successful `withdraw` submit means the
  venue accepted the request; USDC may still be pending bridge arrival.
- The write response includes a **`nonce`** (integer) when available. Keep it:
  it is the only handle for `withdraw-status`.

### Preflight

```bash
purr hyperliquid state --kind both
```

Ensure free/withdrawable collateral covers the amount (and any venue fees if
shown by the venue/response).

### Execute

1. Confirm amount and that funds leave Hyperliquid toward Arbitrum.
2. Run:

```bash
purr hyperliquid withdraw --amount 10
```

3. Report returned fields when present (`actionRequestId`, `actionType`,
   `status`, `replayed`, `nonce`, `response`). **Always surface and retain
   `nonce`** when the response includes it.
4. Do not claim Arbitrum credit from the submit response alone. If the user
   wants settlement status (immediately or later), poll:

```bash
purr hyperliquid withdraw-status --nonce <nonce>
```

5. Optional balance cross-check (especially after `status: arrived`):

```bash
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
purr hyperliquid state --kind both
```

### Withdraw status

```bash
purr hyperliquid withdraw-status --nonce <nonce>
```

- Requires the **same** `nonce` returned by the matching `withdraw` call.
- Requires trading enabled (same as other Hyperliquid exchange reads).
- Platform response fields (CLI prints the data object):

| Field | Meaning |
| --- | --- |
| `network` | Always mainnet |
| `walletAddress` | Instance EVM wallet |
| `nonce` | Echo of the query nonce |
| `status` | `pending` or `arrived` |
| `withdrawal` | `null` while pending; object when arrived |

When `status` is `arrived`, `withdrawal` includes:

| Field | Meaning |
| --- | --- |
| `time` | Ledger timestamp (ms) |
| `txHash` | Settlement transaction hash |
| `amountUsdc` | Withdrawn USDC amount |
| `feeUsdc` | Withdraw fee in USDC |

Interpretation:

- **`pending`**: No matching withdraw ledger entry yet. Report pending; do **not**
  re-run `withdraw`. Poll again later if the user asks, or check Arbitrum USDC
  only as a secondary signal.
- **`arrived`**: Settlement recorded. Report `amountUsdc`, `feeUsdc`, and
  `txHash`. Safe to describe funds as withdrawn; optionally confirm Arbitrum
  USDC balance.

If `withdraw` returned no `nonce` (timeout / unknown outcome before nonce was
captured), **do not invent a nonce**. Reconcile with Hyperliquid `state` and
Arbitrum USDC balance; never re-submit withdraw to “create” a new status
handle.

## Confirmation Templates

### Deposit

```text
Action: deposit USDC to Hyperliquid
Amount: <n> USDC (minimum 5)
Source: Arbitrum USDC on wallet <addr>
Destination: Hyperliquid perp collateral (same address)
Network: mainnet

Do you want to execute this Hyperliquid action with these parameters? (Yes/No)
```

### Withdraw

```text
Action: withdraw USDC from Hyperliquid
Amount: <n> USDC
Source: Hyperliquid collateral on wallet <addr>
Destination: Arbitrum (same address)
Network: mainnet

Do you want to execute this Hyperliquid action with these parameters? (Yes/No)
```

## Safety

- **Never re-run deposit or withdraw** after network timeout, unknown bridge
  status, or `broadcast_unknown`. Reconcile with balances, `actionRequestId`,
  and `withdraw-status --nonce` (when nonce is known) instead. A second call
  can double-spend.
- Do not describe `pending` withdraw status or other incomplete bridge states
  as completed. Only `status: arrived` (or a clear Arbitrum balance increase
  the user accepts) justifies calling the withdraw settled.
- If deposit amount is under 5 USDC, refuse before calling the CLI.
- If Arbitrum USDC is short, report the shortage and stop (or route the user to
  fund Arbitrum via other skills first).

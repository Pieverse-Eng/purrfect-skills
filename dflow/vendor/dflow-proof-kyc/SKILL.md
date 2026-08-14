---
name: dflow-proof-kyc
description: DFlow Proof identity verification for a Solana wallet. Use when the user asks how to KYC a wallet, check verification, handle unverified_wallet_not_allowed / PROOF_NOT_VERIFIED, or gate a Kalshi buy. Do NOT use to place trades, for geoblocking, for age gating, or for spot swaps.
disable-model-invocation: true
user-invocable: false
---

# DFlow Proof

Proof links a Stripe Identity verification to one or more Solana wallets.

- **Kalshi buys** on DFlow require it. Sells, redemptions, spot, and quotes
  do not.
- Any product can use the same public check to gate its own features.

## Check status

`GET https://proof.dflow.net/verify/{address}` → `{ "verified": boolean }`.
Public, no auth.

Cache `true`, never `false` — unverified flips the moment they finish.

## Deep link

If not verified:

`https://dflow.net/proof?wallet=<addr>&signature=<sig>&timestamp=<ms>&redirect_uri=<url>`

Optional: `email`, `projectId`.

Sign exactly `Proof KYC verification: {timestamp}` (Unix ms, 13 digits) and
base58-encode the bytes. After return, re-query `/verify/{address}`.

Redirects only to `https:`, `chrome-extension:`, and `moz-extension:`.
Custom schemes fail silently. Native mobile needs universal / app `https:`
links.

## Kalshi enforcement

`/order` rejects unverified buys with `unverified_wallet_not_allowed` /
`PROOF_NOT_VERIFIED` and `details.deepLink`. Send them to that link, then
retry the buy after they come back verified.

A price-only quote does not need verification.

## Gotchas

- Not all DFlow trades need KYC — only Kalshi buys.
- Proof does **not** verify age or expose date of birth.
- `/verify` is only `true` | `false`. No `pending`.
- One verified identity can link many wallets (fresh signature each time).
- Proof is not geoblocking. Geo lives in `dflow-kalshi-trading`.

## Sibling skills

- `dflow-kalshi-trading` — orders that require Proof; geoblock also lives there
- `dflow-kalshi-portfolio` — reading positions needs no Proof
- `dflow-spot-trading` — never needs Proof

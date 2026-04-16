---
name: fourmeme
description: four.meme implementation skill for BSC buy, sell, and token creation via purr and wallet tools.
---

# four.meme Implementation

Implementation skill under `onchain`. Use when the routed intent targets four.meme on BSC.

## Scope

Supported operations:

- buy token
- sell token
- create token

Out of scope:

- non-BSC chains
- direct contract crafting without `purr`
- bypassing the four.meme login/create API for token creation

## Mandatory Rules

1. four.meme write flows go through `purr fourmeme <cmd> --execute` **by default** — no separate execution step needed.
2. Token creation requires a four.meme login challenge signed with `purr wallet sign` **by default**.
3. Never hand-write four.meme calldata when `purr fourmeme ...` supports the flow.
4. For long signatures, write them to `/tmp/...` and pass a file path into `purr` instead of pasting hex inline.

## Read / Planning Notes

`purr fourmeme buy|sell` already detects:

- V1 vs V2
- X Mode
- TaxToken
- AntiSniper
- agent-created flags

Use that instead of manually selecting contract methods.

## Chain

**BSC only (chain ID 56).** All four.meme operations are on BNB Smart Chain.

## Generic Execution Pattern

1. `purr wallet address --chain-type ethereum` to get wallet address
2. `purr wallet balance --chain-type ethereum --chain-id 56` for native BNB balance. For token balance: `purr wallet balance --token <symbol_or_address> --chain-id 56`
3. `purr fourmeme <cmd> --execute` to build and execute steps in one command
4. Re-check balances or report tx hash

## Buy

Examples:

```bash
purr fourmeme buy --token 0xToken --wallet 0xWallet --funds 0.1 --execute
purr fourmeme buy --token 0xToken --wallet 0xWallet --amount 1000 --execute
```

Notes:

- BSC only
- `purr` handles V1 / V2 / X Mode routing
- approvals are conditional when needed

## Sell

Example:

```bash
purr fourmeme sell --token 0xToken --wallet 0xWallet --amount 1000 --execute
```

Notes:

- V1 sells do not have native on-chain min-out enforcement
- `purr` still computes quote bounds for labels and V2 minFunds where available

## Create Token

Token creation is a mixed off-chain + on-chain flow.

### Step 1: Get login challenge

```bash
purr fourmeme login-challenge --wallet 0xWallet
```

This returns JSON with:

- `nonce`
- `message` (`You are sign in Meme {nonce}`)

### Step 2: Sign the challenge

Use `purr wallet sign --address 0xWallet --message "<message>"` to sign the challenge, then write the returned signature to a temp file such as `/tmp/fourmeme_login_signature.txt`.

Do not paste long signature hex directly into the shell command.

### Step 3: Build create-token steps

Using an existing image URL:

```bash
purr fourmeme create-token \
  --wallet 0xWallet \
  --login-nonce NONCE \
  --login-signature-file /tmp/fourmeme_login_signature.txt \
  --name "My Token" \
  --symbol MTK \
  --description "My token description" \
  --label AI \
  --image-url https://example.com/logo.png \
  --pre-sale 0.1 \
  --x-mode true \
  --anti-sniper false \
  --execute
```

Using a local image file:

```bash
purr fourmeme create-token \
  --wallet 0xWallet \
  --login-nonce NONCE \
  --login-signature-file /tmp/fourmeme_login_signature.txt \
  --name "My Token" \
  --symbol MTK \
  --description "My token description" \
  --label Meme \
  --image-file /tmp/logo.png \
  --execute
```

### Token creation inputs

Required:

- wallet
- login nonce
- login signature or login signature file
- name
- symbol
- description
- label
- exactly one of `image-url` or `image-file`

Optional:

- website
- twitter
- telegram
- pre-sale
- x-mode
- anti-sniper
- tax token configuration

Supported labels:

- `Meme`
- `AI`
- `Defi`
- `Games`
- `Infra`
- `De-Sci`
- `Social`
- `Depin`
- `Charity`
- `Others`

### Tax token rules

If any tax fields are used, require the full tax configuration:

- `tax-fee-rate` must be one of `1`, `3`, `5`, `10`
- burn/divide/liquidity/recipient rates must sum to `100`
- if recipient rate is `0`, recipient address must be empty
- if recipient rate is greater than `0`, recipient address must be a valid EVM address
- `tax-min-sharing` must follow four.meme's integer format requirements

## Failure Handling

**CRITICAL: Do NOT retry on failure.** If any `purr fourmeme` command exits with a non-zero code, report the exact error message to the user and stop. Do not attempt to fix the command, guess missing fields, or retry with different parameters. The user must correct the issue.

The only exception is "Signature for this request is not valid" — this means the nonce expired. In that case, get a fresh login-challenge, sign it, and retry **once**.

| Error | Action |
|-------|--------|
| Unsupported label | Report error, list supported labels |
| Invalid tax config | Report error with the validation message |
| four.meme login failure | Report error |
| Signature not valid | Get fresh login-challenge, re-sign, retry once |
| Image URL not valid | Report error — user must provide a direct image URL (ending in .png/.jpg) or use --image-file |
| Image upload failure | Report error |
| Create-token API failure | Report the exact upstream error message, do not retry |
| Failed to execute EVM transaction | Report error — may be insufficient BNB or token trading disabled |

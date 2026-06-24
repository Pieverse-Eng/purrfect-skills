---
name: fourmeme
description: four.meme BSC,buy,sell,create,TaxToken,raised tokens
---

# four.meme

## Overview

This Skill covers four.meme BSC flows through the managed `purr fourmeme`
commands: raised-token discovery, agent wallet status, token buy/sell,
BNB bridge buy/sell for non-BNB raised-token launches, token creation, and
TaxToken reward queries or claims.

Pick the relevant command group from the table, then read that reference before
running commands or explaining the workflow.

All four.meme operations are on BNB Smart Chain, chain ID `56`.

## Core Rules

1. four.meme write flows go through `purr fourmeme <cmd> --execute` after the user has confirmed the exact action.
2. Token creation requires a four.meme login challenge signed with `purr wallet sign` by default.
3. Never hand-write four.meme calldata when `purr fourmeme ...` supports the flow.
4. For long signatures, write them to `/tmp/...` and pass a file path into `purr` instead of pasting hex inline.
5. Do not bypass the four.meme login/create API for token creation.
6. Non-BNB raised-token creation must use `--pre-sale 0`.
7. When presenting workflows or results, mention that four.meme operations use
   BNB Smart Chain, chain ID `56`.

## Common Preflight

Use these before write flows. Run wallet address and native BNB balance checks
as soon as a write intent is clear, even if other trade or token details are
still missing.

```bash
purr wallet address --chain-type ethereum
purr wallet balance --chain-type ethereum --chain-id 56
purr wallet balance --token <symbol_or_address> --chain-id 56
```

For execution, confirm the token, wallet, amount, raised token or quote token,
and whether the action creates a token or claims rewards.

## Command Groups

| Group | What It Does | Reference |
| --- | --- | --- |
| Discovery / Status | Lists supported raised tokens and checks whether a wallet is a four.meme agent wallet. | [discovery-status.md](references/discovery-status.md) |
| Buy / Sell | Buys or sells four.meme tokens with normal quote-token routing. | [trading.md](references/trading.md) |
| BNB Bridge Buy / Sell | Uses BNB to enter or exit non-BNB raised-token launches through Helper3. | [bnb-bridge-trading.md](references/bnb-bridge-trading.md) |
| Token Creation | Handles login challenge, wallet signature, image upload/use, raised-token rules, and create-token execution. | [token-creation.md](references/token-creation.md) |
| TaxToken | Creates TaxToken configs, queries claimable rewards, and claims rewards. | [taxtoken.md](references/taxtoken.md) |

## Failure Handling

**CRITICAL: Do NOT retry on failure.** If any `purr fourmeme` command exits with
a non-zero code, report the exact error message to the user and stop. Do not
attempt to fix the command, guess missing fields, or retry with different
parameters. The user must correct the issue.

The only exception is "Signature for this request is not valid" — this means the
nonce expired. In that case, get a fresh login-challenge, sign it, and retry
**once**.

| Error | Action |
| --- | --- |
| Unsupported label | Report error, list supported labels. |
| Invalid tax config | Report error with the validation message. |
| four.meme login failure | Report error. |
| Signature not valid | Get fresh login-challenge, re-sign, retry once. |
| Image URL not valid | Report error — user must provide a direct image URL or use `--image-file`. |
| Image upload failure | Report error. |
| Create-token API failure | Report the exact upstream error message, do not retry. |
| Non-BNB raised tokens currently require preSale to be 0 | Ask user to use `--pre-sale 0` or switch to `--raised-token BNB`. |
| `--to cannot be combined with --fee-rate or --fee-recipient` | Ask user to choose explicit recipient mode or fee-sharing mode. |
| Failed to execute EVM transaction | Report error — may be insufficient BNB or token trading disabled. |

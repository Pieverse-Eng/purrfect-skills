---
name: instance-renewal
description: Instance renewal,billing,status,presets
---

# Instance Renewal

Use this skill inside a hosted tenant pod when the user asks to check the
current instance billing status, preview renewal readiness, or renew the
instance subscription.

The renewal action is performed only through `purr instance`. Do not call
pieverse-app directly, do not send wallet transactions manually, and do not
translate friendly names in the CLI command itself. This skill maps strategy
presets to the numeric on-chain identifiers that `purr` expects.

## Requirements

Hosted agents must have:

| Env var | Meaning |
|---|---|
| `WALLET_API_URL` | Platform wallet API base URL |
| `WALLET_API_TOKEN` | Bearer token for this hosted instance |
| `INSTANCE_ID` | Hosted instance ID |

If any are missing, stop and explain that instance renewal requires a hosted
Purr-Fect Claw runtime with platform wallet access.

`purr` must be available in PATH. If `purr instance --help` fails, report that
the runtime needs a purr CLI version with the `instance` command group.

## Shipped Presets

| Preset | chainId | tokenAddress | Meaning |
|---|---:|---|---|
| `bsc-usdt` | `56` | `0x55d398326f99059fF775485246999027B3197955` | Renew with USDT on BSC |
| `okx-xlayer-usdg` | `196` | `0x4ae46a509f6b1d9056937ba4500cb143933d2dc8` | Renew with USDG on X Layer through the OKX App x402 rail |
| `okx-xlayer-usdt0` | `196` | `0x779ded0c9e1022225f8e0630b35a9b54be713736` | Renew with USDT0 on X Layer through the OKX App x402 rail |
| `okx-xlayer-usdc` | `196` | `0x74b7f16337b8972027f6196a17a631ac6de26d22` | Renew with USDC on X Layer through the OKX App x402 rail |

The CLI uses identifiers only:

```bash
purr instance renew --chain-id 56 --token-address 0x55d398326f99059fF775485246999027B3197955
```

For native-token renewal strategies, omit `--token-address`.

## Workflow

1. Confirm the environment is hosted and `purr instance` exists:

```bash
test -n "${WALLET_API_URL:-}" && test -n "${WALLET_API_TOKEN:-}" && test -n "${INSTANCE_ID:-}"
purr instance --help
```

2. Inspect billing status before any payment:

```bash
purr instance status
```

3. Resolve the chosen preset to identifiers. For `bsc-usdt`, use:

```text
chainId: 56
tokenAddress: 0x55d398326f99059fF775485246999027B3197955
```

For OKX App x402 renewal presets, keep the same CLI shape and only swap the
identifiers:

```text
okx-xlayer-usdg:
chainId: 196
tokenAddress: 0x4ae46a509f6b1d9056937ba4500cb143933d2dc8

okx-xlayer-usdt0:
chainId: 196
tokenAddress: 0x779ded0c9e1022225f8e0630b35a9b54be713736

okx-xlayer-usdc:
chainId: 196
tokenAddress: 0x74b7f16337b8972027f6196a17a631ac6de26d22
```

4. Preview renewal without paying:

```bash
purr instance renew \
  --chain-id 56 \
  --token-address 0x55d398326f99059fF775485246999027B3197955 \
  --dry-run
```

Show the user the chain, token or native asset, renewal amount, payer wallet,
balance, and next billing date from the command output.

5. Ask for explicit confirmation before paying unless the user already gave a
clear instruction to renew now. Then run:

```bash
purr instance renew \
  --chain-id 56 \
  --token-address 0x55d398326f99059fF775485246999027B3197955
```

Use `--yes` only after explicit approval or when the user's instruction already
contains unambiguous approval to proceed.

## Exit Codes

| Code | Meaning |
|---:|---|
| `0` | Success |
| `1` | User aborted |
| `2` | Insufficient balance |
| `3` | Instance is ineligible or not renewable |
| `4` | Platform error |

If the platform reports a stale quote, `purr` retries once automatically. If it
still fails, surface the final error and do not attempt another payment without
fresh user confirmation.

## Adding Presets

To add another renewal strategy:

1. Add a row to **Shipped Presets** with the preset name, numeric EIP-155
   `chainId`, and optional ERC20 `tokenAddress`.
2. Use the exact identifiers in examples. Do not add friendly aliases to
   `purr instance renew`.
3. Run `purr instance renew --chain-id <id> [--token-address <address>] --dry-run`
   in a hosted test pod before documenting it as available.

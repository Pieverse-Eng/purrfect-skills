---
name: ows
description: Use only when user explicitly mentions "ows" or "ows wallet"
---

# OWS

Use the `ows` command for OWS wallet, policy, signing, funding, and payment
workflows. Use `purr ows-wallet` and `purr ows-execute` only for Purr CLI
OWS-backed transfer, swap, or step execution flows described in
[Operations](references/operations.md). Do not use SDK workflows from this
skill. Read [Core](references/core.md) before running wallet-scoped or
secret-bearing commands.

## Read First

Always read:

- [Core](references/core.md): OWS scope, access flow, safety rules, output
  rules, and command-discovery rules.

## Task Routing

Read the smallest set that covers the request:

- First-time setup, wallet creation/import/export/rename/delete, API key
  creation/revocation, or policy questions:
  [Setup And Policy](references/setup-and-policy.md).
- Message signing, typed data signing, transaction signing, transaction
  broadcast, Purr OWS transfer/swap/step execution, funding, balance checks,
  x402 paid HTTP requests, mnemonic generation, or derivation:
  [Operations](references/operations.md). If no API key is available, also read
  [Setup And Policy](references/setup-and-policy.md).
- Chain names, aliases, CAIP IDs, supported address families, command maps,
  environment variables, config, update, or uninstall:
  [CLI Reference](references/cli-reference.md).
- Any unfamiliar command or flag: read
  [CLI Reference](references/cli-reference.md) and confirm syntax with
  `ows --help`, `ows <command> --help`, or
  `ows <command> <subcommand> --help`.

## OWS Wallet Skill Interactions

When the user explicitly asks for an OWS wallet to perform a workflow normally
covered by another skill, keep that skill responsible for quotes, discovery,
read-only calls, and payload preparation. Use these interaction files for the
signing, broadcast, or payment step:

| When OWS wallet needs to... | Read |
|---|---|
| execute EVM/Kaia transfers or contract calls | [Kaia Skills](interactions/kaia-skills.md) |
| use Morph transfers, DEX, identity, bridge, or scripts | [Morph](interactions/morph.md) |
| deposit, redeem, or withdraw from Lista vaults | [Lista Vaults](interactions/lista-vaults.md) |
| swap, liquidity, farm, V3 LP, or Syrup Pool on PancakeSwap | [Pancake](interactions/pancake.md) |
| create, buy, sell, claim, or authenticate for four.meme | [Four Meme](interactions/fourmeme.md) |
| buy, sell, sign, or execute OpenSea payloads | [OpenSea](interactions/opensea.md) |
| execute DFlow Solana order payloads | [DFlow](interactions/dflow.md) |
| use Aster API auth or deposit into Aster | [Aster](interactions/aster.md) |
| use Bitget wallet flows under OWS constraints | [Bitget Wallet](interactions/bitget-wallet.md) |

For interaction flows, do not use platform-wallet execution commands such as
`purr execute`, `purr wallet ...`, or `purr <vendor> ... --execute` as the
signing path. First build an unsigned transaction, typed data, message, or
`steps` payload, then sign or execute it with OWS. If the other skill only
offers a black-box platform-wallet command and does not expose a signable
payload, stop and explain that OWS cannot safely take over that flow yet.

## Complete Reference

- [Core](references/core.md)
- [Setup And Policy](references/setup-and-policy.md)
- [Operations](references/operations.md)
- [CLI Reference](references/cli-reference.md)
- [Aster Interaction](interactions/aster.md)
- [Bitget Wallet Interaction](interactions/bitget-wallet.md)
- [DFlow Interaction](interactions/dflow.md)
- [Four Meme Interaction](interactions/fourmeme.md)
- [Kaia Skills Interaction](interactions/kaia-skills.md)
- [Lista Vaults Interaction](interactions/lista-vaults.md)
- [Morph Interaction](interactions/morph.md)
- [OpenSea Interaction](interactions/opensea.md)
- [Pancake Interaction](interactions/pancake.md)

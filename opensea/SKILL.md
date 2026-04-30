---
name: opensea
description: Entry point for ALL OpenSea operations. Read this skill FIRST before using opensea-vendor. Contains buy/sell NFT execution via purr opensea, routing rules, and scope limits. Routes reads to the opensea-vendor skill and its CLI/scripts. Create offer, create listing, and cancel are NOT supported — direct users to opensea.io.
metadata:
  openclaw:
    primaryEnv: OPENSEA_API_KEY
---

# OpenSea

Use the vendored OpenSea skill for OpenSea-native reads and OpenSea-specific write preparation.
Use `purr opensea` only for buy and sell execution.

## Scope

Supported write chains:

- Ethereum
- Polygon (`matic`)
- Arbitrum
- Optimism
- Base
- Avalanche
- Klaytn
- Zora
- Blast
- Sepolia

Supported NFT standards:

- ERC-721
- ERC-1155

Write flows covered by this skill:

- buy NFT (via `purr opensea buy`)
- sell NFT / accept offer (via `purr opensea sell`)

**Not supported — tell user to do these manually on opensea.io:**

- create offer — requires building a full Seaport order from scratch (no API/CLI help)
- create listing — same limitation
- cancel offer — no tooling available
- cancel listing — same limitation
- token swap execution — use the onchain skill's swap routing instead

## Read Path

Start with:

- `./skills/opensea/vendor/SKILL.md`
- `./skills/opensea/vendor/references/*`
- `./skills/opensea/vendor/scripts/*`

Use the vendored official OpenSea skill for:

- collection, NFT, listing, offer, event, and account lookup
- search and browsing
- floor price, metadata, and market activity
- token search, token details, trending tokens, top tokens, and balances
- best listing lookup
- best offer lookup
- order lookup
- finding the order hash needed for a write flow
- fetching fulfillment JSON for `buy` or `sell`
- reading the official Seaport schema and workflow for listings and offers
- preparing Seaport `parameters` and the final signed request body
- OpenSea-specific reasoning that does not yet need the platform wallet

Do not use `purr` for read-only lookup.

## Write Path

Before any write:

1. Get the wallet with `purr wallet address --chain-type ethereum`
2. Check funds with `purr wallet balance --chain-type ethereum --chain-id <chain_id>`
3. Wait for clear user confirmation before adding `--execute`
4. After `--execute`, return the tx hash and a block explorer link immediately — do NOT wait for on-chain confirmation or re-check balances. Let the user verify the transaction themselves.

Use `--execute` when the command should send the on-chain steps immediately.
Without `--execute`, `purr opensea buy` and `purr opensea sell` return `StepOutput` JSON so you can inspect the planned `steps` first.


## Flows

### Buy NFT

Use when the user wants to purchase an NFT from an existing listing.

Use:

- the official vendor skill to follow the buy workflow and obtain fulfillment JSON / transaction data
  this usually means finding the listing, getting the `order_hash`, and calling `opensea-fulfill-listing.sh`
- `purr opensea buy --wallet <wallet> --fulfillment-json '<fulfillment_json>' [--execute]`
- `purr opensea buy --wallet <wallet> --fulfillment-file <path_to_fulfillment_json> [--execute]`

What `purr` does:

- reads the fulfillment JSON
- adds ERC-20 approval when the listing is ERC-20 priced
- builds the final OpenSea buy step

Without `--execute`, output is `StepOutput` JSON:

```json
{ "steps": [TxStep, ...] }
```

Use `--execute` when the user wants to complete the purchase now.

### Sell NFT / Accept Offer

Use when the user wants to accept an existing offer for an NFT they own.

Use:

- the official vendor skill to follow the accept-offer workflow and obtain fulfillment JSON / transaction data
  this usually means finding the offer, getting the `order_hash`, and calling `opensea-fulfill-offer.sh`
- `purr opensea sell --wallet <wallet> --fulfillment-json '<fulfillment_json>' [--execute]`
- `purr opensea sell --wallet <wallet> --fulfillment-file <path_to_fulfillment_json> [--execute]`

What `purr` does:

- reads the fulfillment JSON
- checks NFT ownership for the provided wallet
- adds the NFT approval step
- builds the final OpenSea sell step

Without `--execute`, output is `StepOutput` JSON:

```json
{ "steps": [TxStep, ...] }
```

Use `--execute` when the user wants to accept the offer now.

## Routing Rules

- Reads, lookup, search, market data, and order discovery stay in the vendor skill
- `buy` and `sell` first follow the official vendor workflow to get fulfillment data, then go to `purr`
- Create offer, create listing, cancel — tell the user to do these manually on opensea.io
- Token swap execution belongs to the onchain skill, not this skill

## Rules

- Keep OpenSea reads in the vendor skill
- For buy and sell, first follow the official vendor workflow to get fulfillment JSON, then pass it to `purr opensea buy` or `purr opensea sell`
- Use the current wallet address for all write flows
- Do not execute until the user clearly confirms
- If the user asks to create an offer, create a listing, or cancel an order, explain that these are not supported programmatically and direct them to opensea.io
- **Never show raw CLI/script output, JSON responses, error codes, or technical details to the user.** Summarize results in plain language. For example, say "No offers found on this NFT" instead of showing `opensea-get.sh: HTTP 404 error`. Include NFT names, prices, and links — not order hashes, contract addresses, or API paths unless the user specifically asks for technical details

## Confirmation Contract (Mandatory)

Before any OpenSea execution, show the action-specific parameters and ask exactly:

`Do you want to execute this action with these parameters? (Yes/No)`

Minimum fields to show:

- Buy NFT: chain, collection or NFT, order hash, payment asset, payment amount
- Sell NFT / Accept Offer: chain, collection or NFT, order hash, wallet, expected payment asset, expected payment amount

If the user says `No`, do not execute.
If any parameter changes, ask again before executing.

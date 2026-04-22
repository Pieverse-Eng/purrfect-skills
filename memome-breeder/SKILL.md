---
name: memome-breeder
description: Genetic recombination skill for four.meme tokens on BSC. Extracts visual/narrative/timing/community genes from two parent tokens, performs dominance-weighted crossover plus bounded mutation, and deploys a novel child token via the `fourmeme` skill (TEE-signed). Use when the user asks to breed, cross, hybridize, or splice two four.meme tokens.
---

# memome-breeder

Implementation skill under `onchain`. Specifically a sibling of the `fourmeme` skill — memome-breeder handles the *generation* step (deciding what the new token should be), then hands off to `fourmeme` for the on-chain create-token step.

## When to use

Route to this skill when the intent contains any of:

- "breed X with Y", "cross X and Y", "hybridize X × Y", "splice X into Y"
- "what happens if we mix $A and $B", "make a child of $A and $B"
- "genetic meme", "meme DNA", "meme crossover", "meme mutation"

Do **not** use this skill when the user just wants to create a token from scratch — that is plain `fourmeme create-token`. Memome-breeder is specifically for deriving a new token's traits from the genetic material of two existing four.meme tokens.

## Scope

Supported:

- extracting a 4-chromosome genome (VIS, NAR, TIM, COM) from a four.meme token address
- crossover: dominance-weighted interleave of two parent genomes
- mutation: stochastic replacement from a trait pool, rate tunable per child
- child synthesis: name, symbol, sigil, lore, tagline, image prompt, survival score
- handing a confirmed child off to `purr fourmeme create-token --execute`

Out of scope:

- non-BSC chains (Solana, Ethereum, other L2s) — reject
- skipping the TEE wallet (login challenge signing) — forbidden, see `fourmeme` SKILL.md
- breeding more than two parents at once — use repeated binary crosses instead
- modifying parent token state — this skill only *reads* from parents

## Chain

**BSC only (chain ID 56).** Inherits from `fourmeme` SKILL.md.

## Mandatory Rules

1. Both parents must be valid four.meme BSC tokens. Verify via DexScreener BSC pair data or a direct `purr wallet balance --token <addr> --chain-id 56` probe.
2. The TEE-secured wallet is the only signer — never prompt the user to paste a private key or seed phrase. Use `purr wallet sign` for any off-chain auth and `purr fourmeme create-token --execute` for the deploy (which handles signing internally).
3. Always surface the survival score **with its reasoning** before deploying. Never auto-deploy without an explicit user confirmation on a specific child.
4. Mutation rate must be in `[0.05, 0.40]`. Outside that range the genome either barely differs from a parent (noise) or is so novel that it no longer derives identity from the parents (bad science).
5. The child token's `--label` field for `purr fourmeme create-token` must be `Meme`. Any other label misrepresents the intent.

## Generic Execution Pattern

```text
1. Parse intent, extract parent tickers or addresses
2. Resolve each parent to a BSC token record (address, symbol, name, mcap, volume, community tags)
3. Extract DNA from each parent (see "Gene extraction" below)
4. Run crossover + mutation N times (default N=3) with different seeds
5. Score each child (survival model, 0-100)
6. Present children with reasoning; let user pick one
7. Generate flux portrait via image model (optional; skip for fully-CLI flows)
8. For the selected child:
   8a. purr fourmeme login-challenge --wallet $WALLET_ADDRESS
   8b. purr wallet sign --address $WALLET_ADDRESS --message "<challenge>"
       (write sig to /tmp/memome_login_signature.txt)
   8c. purr fourmeme create-token \
         --wallet $WALLET_ADDRESS \
         --login-nonce $NONCE \
         --login-signature-file /tmp/memome_login_signature.txt \
         --name "<child.name>" \
         --symbol <CHILD_SYMBOL> \
         --description "<child.lore>" \
         --label Meme \
         --image-url <child.imageUrl> \
         --execute
9. Report transaction hash, confirm indexing on four.meme front-end
```

## Gene extraction

Each parent's genome has exactly four chromosomes:

| Chromosome | Code | Source data | Example loci |
|-----------|------|-------------|--------------|
| visual    | VIS  | token name/sigil motifs, sticker set, pfp pattern | `VIS-01 neon-calligraphy` |
| narrative | NAR  | description, Twitter/Telegram bio, pinned lore | `NAR-02 diaspora alpha` |
| timing    | TIM  | peak-hour UTC, half-life in hours (volume decay) | `TIM-01 14:00 UTC`, `TIM-02 128h` |
| community | COM  | cohort tags, chain-iness, degen score (0-100) | `COM-01 tier-2 city diaspora`, `COM-DS 82/100` |

Each gene carries:

- `locus` — short code, `VIS-01`, `COM-DS`, etc.
- `value` — the trait value as a short string
- `dominance` — `0.0-1.0`, derived from how central that trait is to the parent
- `origin` — the parent token address (or the literal `"mutation"` if synthesized)

Extraction is deterministic per (parent address, seed). Same inputs always produce the same genome.

## Crossover

For each chromosome, walk the parent loci in parallel. For each locus pair `(la, lb)`:

- If only one parent has this locus, child inherits it.
- Otherwise, pick `la` with probability `la.dominance / (la.dominance + lb.dominance)`, else pick `lb`.

The child genome carries the origin tag of whichever parent contributed each gene.

## Mutation

Walk the child genome. For each gene, with probability equal to `mutationRate`, replace its value with a random draw from the chromosome-specific trait pool. Mutated genes get:

- `origin = "mutation"`
- new `value` from the pool
- new `dominance` in `[0.5, 1.0]` (mutations tend to be expressive)

Three children per breed is the default. Rate should vary per child to produce a spread: child-01 at `rate × 0.6`, child-02 at `rate × 0.95`, child-03 at `rate × 1.3`. That way the user sees one "safe" recombinant, one balanced, one novel.

## Survival score

`survival = clamp(3, 98, round(40 + 0.25·avgDegen + 0.1·maxHalfLife + 2·log10(mcapA·mcapB) + noise − 4·max(0, mutatedCount − 2)))`

Where:

- `avgDegen` = average community.degenScore of the two parents
- `maxHalfLife` = `max(a.halfLifeH, b.halfLifeH)`
- `mutatedCount` = number of mutated genes (excess mutation is penalised)
- `noise` ∈ `[-4, 4]`, seeded by (a.id, b.id, child-index)

Report the score with **at least one concrete number from the parents** (degen avg, half-life, mcap). Never give a bare percentage.

## Inputs

Required:

- `parentA` — BSC token address or four.meme ticker
- `parentB` — BSC token address or four.meme ticker

Optional:

- `mutationRate` — float in `[0.05, 0.40]`, default `0.22`
- `childCount` — int in `[1, 5]`, default `3`
- `seed` — int, default `Date.now()`
- `deploy` — boolean, default `false`. When `true`, after child selection run the `fourmeme create-token` handoff. Requires a follow-up `selectedChildId` argument.

## Outputs

```json
{
  "ok": true,
  "children": [
    {
      "id": "CHILD-<hex>",
      "name": "NeonPepe",
      "symbol": "NEPE",
      "sigil": "龙",
      "hue": "#a566cc",
      "lore": "Spawned from $PEPE × $MEMES at 14:00 UTC. Visual signature: neon-calligraphy + pixel-seal-script. Narrative fuel: auntie-oracle, LP-ancestors. Target cohort: tier-2 city diaspora.",
      "dna": { "genes": [...] },
      "survival": 74,
      "survivalReasons": ["high degen parents", "long half-life inherited"],
      "imagePrompt": "meme token mascot, neon-calligraphy, pixel-seal-script, mood: auntie-oracle, hero-framed, accent color #a566cc, black void background, thick rim light, 35mm grain, no text",
      "parents": ["0xABCD...", "0xDEFG..."]
    }
  ]
}
```

For deploy confirmation:

```json
{
  "ok": true,
  "txHash": "0x...",
  "tokenAddress": "0x...",
  "session": "<four.meme session token, truncated>",
  "fourMemeUrl": "https://four.meme/token/0x..."
}
```

## Failure Handling

| Error | Action |
|-------|--------|
| Parent not on BSC | Report error; reject non-BSC addresses |
| Parent has no liquidity (DexScreener returns no pair) | Report; suggest user pick a different four.meme token |
| `purr fourmeme login-challenge` fails | Report upstream error; stop |
| `purr wallet sign` fails | Report error; TEE may be unreachable |
| `purr fourmeme create-token` fails | Report exact upstream error; do not retry (see fourmeme SKILL.md) |
| Mutation rate out of bounds | Clamp to `[0.05, 0.40]` and warn user |
| Survival score below 20 on all children | Still return them, but warn user strongly — rug-tier |

**Never auto-retry on broadcast failures.** The user re-issues the command with corrections.

## Reference implementation

The memome project ships a full reference implementation:

- Web UI: <https://github.com/joachimber/memome>
- Gene extraction: `lib/dna.ts`
- Crossover + mutation: `lib/dna.ts` (`crossover`, `mutate`)
- Survival score: `lib/dna.ts` (`survivalScore`)
- TEE-wallet login + deploy: `app/api/deploy/route.ts`
- Live BSC token fetcher: `lib/fourmeme.ts` (DexScreener search, BSC filter, dedupe, volume rank)
- Plain-English breakdown (for judge demos): `app/api/explain/route.ts`

An agent using this skill can either:

1. Call memome's HTTP endpoints directly (`POST /api/breed`, `POST /api/deploy`) — useful when embedding in a chat UI, or
2. Re-implement gene extraction + crossover locally and drive `purr fourmeme create-token` directly — useful for autonomous CLI-only agents.

Both paths arrive at the same four.meme token creation step and both use the TEE wallet for signing.

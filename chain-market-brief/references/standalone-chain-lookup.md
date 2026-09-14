# Standalone chain lookup

Outside the hosted research surface, the CLI retains these chain-specific reads.

## Collect

Map Robinhood Chain → `robinhood`, BNB Chain → `bnb`, Solana → `solana`.

For a chain overview:

```bash
purr market trending --chain <chain>
```

For a specific token, reuse its chain, CA, links, and relevant evidence already in the conversation. If lookup is needed, use:

```bash
purr market token --chain <chain> <ca>
```

This returns the same `chain` and `candidates` shape as trending, with at most one candidate. Do not run trending to find an explicitly supplied CA. Resolve an ambiguous token identity before lookup; do not guess a CA or chain. An empty candidates array means no matching token was found by this provider, not that the token does not exist. Provider errors are lookup failures.

Keep the returned chain, exact CAs, pool names, and project links. The list is a discovery sample, not a chain ranking or a safety endorsement. Use those exact CAs; do not substitute same-name tokens.


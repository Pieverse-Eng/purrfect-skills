# Chain activity and token narratives

Answer the requested activity, narrative or token question; holder analysis,
fund flows and audits only when asked.

## Identify subjects

```bash
purr market trending --chain <robinhood|bnb|solana>
purr market token --chain <chain> <ca>
```

Never guess a chain or contract. Both return `candidates` (token lookup at most
one); empty means no provider match, not nonexistence. Trending is a sample, not
a ranking or endorsement. These chains limit the lookups, not other research.

## Tools

News and X posts use the commands in the main skill. For other tools, run
`describe` first; these are pitfalls its schema does not state.

- `Sorsa/post_tweet_info`: `tweet_link` is a tweet URL or ID, not a profile.
- `Sorsa/post_user_tweets`: a profile URL goes in `user_link`; numeric IDs stay
  strings; pass `next_cursor` verbatim.
- `Chainbase/GetTokenPriceHistory`: Unix seconds, at most a 90-day window.
- `CoinMarketCap/getDexTokenLiquidity`: token contract plus provider platform
  name.
- `CoinMarketCap/getDexPairsQuotesLatest`: `contract_address` is the pair or
  pool, not the token.

If none fits, discover within `social/twitter`, `crypto/market` or `crypto/dex`.

## Report

Attribute project claims and social narratives; repetition is not independent
confirmation. Keep names, symbols, chains, contracts, links and observation
times. For market data keep provider, pool and window; do not sum overlapping
samples or treat displayed liquidity as an executable quote.

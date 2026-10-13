# Venue identity and capability

The host Paper catalog is authoritative for identity, product, settlement
scope, quantities, fees, leverage, precision and tradability. These notes do
not replace the returned rules.

- Hyperliquid: selected Paper spot and perpetual markets. Keep native spot
  index/token/quote identity distinct from a Live signing asset ID; never add
  or subtract 10000 yourself.
- Lighter: selected Paper spot and perpetual markets. Market numbers are not
  tickers or account IDs. Native stock/index/metal markets need their actual
  quantity units and fresh execution inputs.
- Orderly: perpetual markets in its actual Paper catalog; do not fabricate
  spot support. Respect its position-protection workflow and trigger capabilities.

For ambiguous symbols, show trusted candidates and ask the user to select in
the terminal. Do not substitute another venue on a catalog/feed failure.
A listed market, Ready account or current mark does not by itself prove that a
fresh executable book and confirmed funding are available.

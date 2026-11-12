# Interpreting Ginza Output

## Slippage: `slippage`

The output difference relative to the reference quote, in bps (100 bps = 1%). Positive values mean receiving more than quoted; negative values mean receiving less. Do not reverse this convention.

Quantiles are not guaranteed bounds. For example, P10=-5bps, P50=0bps, and P90=2bps are model quantiles; P10 to P90 is a central 80% prediction interval, not a guarantee that the loss cannot exceed 5bps. The distribution's `top` is its highest-probability category, not an exact execution value.

## Sandwich event: `sandwiched`

Use the probability of the option representing event occurrence. For example, `probs.yes=0.0009` means 0.09%, not 0.0009%. If option semantics are unclear, preserve the original values and explain the uncertainty rather than guessing.

Predictions depend on the inputs and submission conditions. Do not directly apply single-pool analysis to a private channel, aggregator, or different execution path; disclose when applicability is unconfirmed. A small probability does not guarantee protection from sandwich attacks.

## Price changes: `mid1` / `mid10`

Display only after product scope and input requirements are confirmed. These describe price-change distributions over the next 1 and 10 blocks, respectively, in bps. They are not seconds, guaranteed returns, or execution slippage relative to the quote. Disclose missing CEX, pending, or other context using the actual `missingFields`; do not infer that omitted data is unimportant.

## Common fields

- `confidence`: the model probability of the `top` category, not model accuracy or a prediction-quality score.
- `model`: use the actual response value. Do not replace `de1-v0.6` with the documented name `ginza-1.0`.
- `missingFields`: explain which market context was omitted. Missing context is not zero risk.
- `assumptions`: disclose approximate feature conventions, default priority fees, and USD conversion assumptions actually used by the backend.
- `capturedAt` / `blockNumber`: identify the snapshot. A timestamp alone does not establish freshness. Do not invent a guaranteed validity period.

Ginza predictions do not replace transaction simulation, token/contract safety checks, or user authorization. Do not turn a small probability into a recommendation that a trade is safe.

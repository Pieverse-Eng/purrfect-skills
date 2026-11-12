---
name: ginza
description: Use when the user asks to assess a specific swap's slippage, sandwich attack probability, or execution conditions. Confirm the order and supported scope before analysis. Read-only; never executes trades.
---

# Ginza: Swap Execution Analysis

Respond in the user's language.

## 1. Confirm the order

Use only when the user explicitly requests analysis of a specific swap. Do not automatically add analysis to ordinary quote, market-data, or execution requests.

Current scope: Ethereum mainnet, Uniswap V3, ETH/WETH → USDC, single-pool, single-hop, exact-input swaps. Other directions, tokens, chains, DEXes, multi-hop routes, aggregator splits, and exact-output orders are outside this workflow. Do not silently change the chain or pool, or treat an aggregator route as a single pool.

Ask for missing information together; do not ask again for information already provided:

- Chain and DEX version: do not assume that “Uniswap” means Ethereum mainnet V3.
- Input/output tokens and input amount: require an explicit positive amount. Do not interpret a USD budget as a token quantity.
- Pool fee: 0.01%, 0.05%, 0.3%, or 1%, corresponding to feeTier 100, 500, 3000, or 10000. Do not select a pool automatically. The backend must still verify that the pool and quote are valid.
- Priority fee is optional. If omitted, use the default supplied by the backend and disclose it in the report; do not invent a value.

Treating ETH as WETH is an analysis convention, not evidence that ETH has been wrapped or that the user's actual route matches. Before the first call, disclose that the order direction, quantity, value, priority fee, and related market features will be sent to third-party De¹. Stop if the user declines data sharing. Do not claim that data is not retained or used for training.

## 2. Call the platform

Use this skill's `scripts/assess.py`, replacing the example parameters with the user's confirmed values. Paths are relative to this skill directory:

```bash
python3 scripts/assess.py --token-in ETH --token-out USDC --amount-in 1 --fee-tier 100
```

Append `--tip-gwei <gwei>` only if the user specifies a priority fee. The script reads platform-injected `WALLET_API_URL`, `WALLET_API_TOKEN`, and `INSTANCE_ID`; users do not configure a third-party key. Use this platform endpoint only, never an ad hoc direct provider call.

Proceed to a report only when the script exits with code 0 and its JSON contains `ok: true`. Otherwise explain the actual failure: a hosted instance is required, unsupported parameters, insufficient permissions, rate limiting, unavailable data, or service failure. If the platform has not been deployed, report that limitation rather than substituting historical examples or inventing predictions. Do not loop on rate limits or retry timeouts indefinitely.

## 3. Verify and explain the result

Read `references/output-fields.md` first. Verify that the pool, direction, fee, and quote match this order. Results should identify the capture time, block number, actual model, and missing context. Unknown, expired, missing, or invalid values do not mean zero risk and cannot support a complete conclusion.

Use this report structure:

1. **Order**: chain, DEX, input amount, direction, pool, and fee.
2. **Reference quote**: output amount and quote-versus-mid-price difference. State whether network fees are included; do not confuse this difference with model-predicted slippage.
3. **Model predictions**: explain only the questions validly returned for this request, with probabilities, bps, or block horizons. Do not assign invented “safe” or “low-risk” grades. The presence of price-prediction documentation does not enable requesting or displaying those questions automatically.
4. **Data and assumptions**: capture time, block number, actual model, `missingFields`, and `assumptions`, including default priority fees and USD conversion assumptions. When context is incomplete or conventions are approximate, lead with “Experimental analysis, not a production risk-control conclusion,” translated into the user's language.
5. **Limitations**: probabilities are not guarantees. Results describe this single-pool order at its snapshot; they do not automatically apply to another route or a later submission. Do not call results live without evidence of freshness.

Do not interpret slippage quantiles as maximum loss, recommended slippage tolerance, or a best-execution guarantee. Clearly labeled test data is for demonstration only, not a conclusion about the current order.

## 4. Remain read-only

Return control to the user after analysis. This skill never signs, approves, wraps ETH, broadcasts, automatically widens slippage, splits orders, or resubmits transactions. “Buy if the risk is small” does not grant this skill execution authority; other trading workflows require separate confirmation and authorization.

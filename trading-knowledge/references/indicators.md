# Indicators and measurements

Use one identified venue/product/instrument series per calculation. Record price
and volume units, interval, parameters, source time, missing bars and whether the
last candle is closed. Different seeds, smoothing, sessions or adjusted prices
can produce different readings. Conventional examples are examples only.

## Moving averages

An SMA averages the selected observations with equal weights. An EMA weights
recent observations more, using alpha = 2/(period+1) under the common convention.
Both smooth prices and lag changes; neither supplies a fundamental valuation.
A fast/slow crossover needs aligned history on both sides of the crossing, not
only the latest two scalar values. Trend persistence can make them informative;
sideways movement can produce repeated reversals. [Fidelity: EMA](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/ema).

fx reports its actual seed and warm-up convention. Use closed closes, retain the
period and interval, and compare values in the source quote currency. Insufficient
history is unavailable rather than an invitation to silently shorten the period.

## RSI

RSI compares smoothed gains with smoothed losses in close-to-close changes and
expresses their relative strength on a 0–100 scale. A 14-period Wilder calculation
is conventional, not a required parameter. Readings often called overbought or
oversold describe recent directional persistence; a strong trend can retain such
readings. They do not mandate selling or buying. Divergence may motivate a closer
look at weakening momentum but supplies neither a reliable turning time nor a
calibrated reversal probability. [Fidelity: RSI](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI).

Use the returned initialization convention and quality gaps. No-loss, no-gain and
flat series need explicit code conventions. A divergence claim needs matched
price and indicator history around at least two identified extrema.

## MACD

MACD subtracts a slower EMA from a faster EMA; a signal average and their
difference describe changes in momentum. A commonly shown 12/26/9 combination is
an example, not a universal rule. Values depend on price scale and interval and
are not directly comparable across differently priced instruments. Crossings lag
prices and can reverse repeatedly in ranges. [Fidelity: MACD](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/macd).

Do not invent MACD when the tool does not implement it. EMA measurements alone
are not a complete MACD signal-history calculation.

## ATR

True range is the maximum of high minus low, absolute high minus previous close,
and absolute low minus previous close. ATR smooths these ranges, commonly with
Wilder smoothing. It measures movement magnitude, including gaps, without giving
a direction. An increase can accompany either a rally or a decline. ATR is in
price units; comparisons across assets need an explicitly defined normalization.
It can inform volatility-aware scenarios, but chooses neither a compulsory stop
multiple nor a maximum loss. [Fidelity: ATR](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/atr).

ATR requires high, low and previous close with sufficient initialization history.
Current fx candle indicators support SMA, EMA and RSI; unsupported MACD/ATR
requests must remain explicit gaps, not model-calculated current values.

## Volume, open interest and funding

Volume counts activity over a time window; open interest measures outstanding
contracts at an observation time. New open interest requires both a long and a
short, so growth alone does not establish net bullish positioning. Contract
multipliers, reporting units and expiry/roll effects matter when comparing series.
[CME: open interest](https://www.cmegroup.com/education/lessons/open-interest).

Volume is not depth: substantial historical turnover does not guarantee a narrow
spread or enough current liquidity for an order. Use size-specific book/quote
measurements for execution impact. [CME: volatility and depth](https://www.cmegroup.com/education/featured-reports/volatility-returns-phase-transitions-in-equities).

Perpetual funding is a transfer mechanism associated with keeping perpetual
prices near the underlying market. Rates and settlement conventions belong to
the exact contract. Preserve sign, payment interval and observation time;
annualizing one observation assumes persistence that is not established.
[Hyperliquid: perpetual contract specifications](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications).

Funding and OI are snapshots, not candle-derived indicators. Missing or
incompatible units cannot be resolved by pooling venue numbers. Positive funding
alone is neither a price forecast nor a reason to open a short.

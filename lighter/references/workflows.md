# Workflows

Concrete recipes. Each assumes the Confirmation Contract in `SKILL.md` before
any account-changing step. Silent preparation, speak at decisions.

## 1. First-time funding

```bash
purr lighter status                       # enabled? if not, confirm + enable
purr lighter sdk-status                   # credentials/signer ready?
purr lighter deposit-networks             # which chains are supported
purr lighter balances                     # current state
# confirm with user →
purr lighter deposit --amount 100 --source-chain-id 42161
purr lighter deposits --limit 5           # track it
purr lighter balances                     # verify it landed
```

Minimum 1 USDC. The USDC must already sit on the source chain in the instance
wallet. If a `LIGHTER_APPROVAL_*` code appears, follow the approval leg via
`requests` — do not resubmit the deposit.

## 2. Perp long

```bash
purr lighter market --market SOL --market-type perp        # decimals
purr lighter order-book-depth --market SOL --market-type perp --limit 50
purr lighter balances
purr lighter positions                                     # existing exposure?
# optional leverage change — separate or bundled confirmation:
purr lighter update-leverage --market SOL --market-type perp --leverage 5 --margin-mode cross
# confirm with user (market, type, side, size, price bound, leverage) →
purr lighter order --market SOL --market-type perp --side buy --size 10 --price <bound> --type market
purr lighter trades                                        # did it fill?
purr lighter positions                                     # net effect
```

For a market order the `--price` is the **worst acceptable fill**, derived from
the book. Say so in the confirmation. See [trading.md](trading.md).

## 3. Resting limit order

```bash
purr lighter market --market ETH --market-type perp
purr lighter order-book-depth --market ETH --market-type perp
# confirm →
purr lighter order --market ETH --market-type perp --side buy --size 0.5 \
  --price 3000 --type limit --time-in-force gtt --expires-in 24h
purr lighter active-orders
```

`gtt` accepts an expiry. An IOC order does **not** — `--expires-in` with a
default-IOC market order is an error.

## 4. Spot buy

```bash
purr lighter markets --market-type spot                    # 8 spot markets
purr lighter market --market LIT --market-type spot
purr lighter order-book-depth --market LIT --market-type spot
# confirm →
purr lighter order --market LIT --market-type spot --side buy --size 100 --price <bound> --type market
```

`LIT` is dual-listed as a perp. Without `--market-type spot` the CLI errors as
ambiguous — that error is a real fork in intent, so ask rather than pick.

## 5. Close or reduce a position

```bash
purr lighter positions                                     # exact size and side
purr lighter order-book-depth --market SOL --market-type perp
# confirm →
purr lighter order --market SOL --market-type perp --side sell --size <position size> \
  --price <bound> --type market --reduce-only true
purr lighter positions                                     # verify flat/reduced
```

Use `--reduce-only true` for any close or trim: it cannot accidentally flip the
user into an opposite-side position if the size is stale.

## 6. Cancel resting orders

```bash
purr lighter active-orders                                 # get order-index values
# confirm the specific order →
purr lighter cancel --market SOL --market-type perp --order-index <id>
# or, after listing and confirming the full set →
purr lighter cancel-all
purr lighter active-orders                                 # verify
```

Never pass an `--order-index` remembered from a submit response; re-read
`active-orders`.

## 7. Withdraw

```bash
purr lighter balances
purr lighter withdrawal-delay                              # quote the wait first
# confirm, showing base units AND USDC →
purr lighter withdraw --amount-base-units 25000000         # = 25.00 USDC
purr lighter requests --limit 5
purr lighter request-status --request-id <id>
```

`--amount-base-units` is an integer at 6 decimals. Do not report arrival from
the submit response.

## 8. Recovering from an unknown submission

```bash
# a write timed out, or returned LIGHTER_SUBMIT_UNKNOWN
purr lighter active-orders
purr lighter inactive-orders
purr lighter trades
purr lighter positions
purr lighter requests --limit 10
```

Report what you observed and ask how to proceed. **Do not resubmit.** See
[errors.md](errors.md).

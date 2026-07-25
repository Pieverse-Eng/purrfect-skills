# Workflows

Concrete recipes. Each assumes the Confirmation Contract in `SKILL.md` before
any account-changing step. Silent preparation, speak at decisions.

## 1. First-time funding

```bash
purr lighter status                       # 1. enabled? if not, confirm + enable
purr lighter account                      # 2. readiness — branch on .status
purr lighter deposit-networks             # 3. chains + per-network minAmount
# confirm with user →
purr lighter deposit --amount 10 --source-chain-id 42161
purr lighter deposits --limit 5           # track it
purr lighter account                      # 4. re-read: initializing -> account_discovered
```

`account` is the readiness call — run it **before** `sdk-status` / `balances`,
which answer narrower questions and won't tell you which onboarding step is
outstanding. Branch on `.status`:

- `deposit_required` → the first deposit **creates** the account. Say so.
- `initializing` → wait, poll `deposits` / `requests`; do not resubmit.
- `account_discovered` → normal; the **next write registers the API key
  automatically**.
- `verifying_key` → wait, re-read `account`.
- `ready` → trade.
- `error` → stop, report the returned `state`.

**Minimum depends on the chain:** Ethereum mainnet (`1`) is 1 USDC; Arbitrum,
Base, Avalanche and HyperEVM go via CCTP at **5 USDC**. Read `minAmount` from
`deposit-networks` rather than quoting a remembered number — a 4 USDC Base
deposit is rejected. The USDC must already sit on the source chain in the
instance wallet.

If `POLICY_DEFERRED` or a `LIGHTER_APPROVAL_*` code appears, do **not** resubmit
the deposit. Most of those are **wallet-policy manual approval** — a human must
approve the parked request, and the agent cannot approve anything. Observe a
parked *deposit* with `deposits` / `deposit-status` (**not** `requests`, which
is the action ledger). Only `LIGHTER_APPROVAL_TX_HASH_MISSING` is the on-chain
ERC-20 leg.

⚠️ Even after approval, **do not re-run `deposit`** — the CLI has no resume
surface, so a re-run creates a second request. See [errors.md](errors.md).

## 2. Perp long

```bash
purr lighter account                                       # .status ready?
purr lighter market --market SOL --market-type perp        # decimals
purr lighter order-book-depth --market SOL --market-type perp --limit 100
purr lighter balances                                      # readiness object if not ready
purr lighter positions                                     # existing exposure?
# optional leverage change — separate or bundled confirmation:
purr lighter update-leverage --market SOL --market-type perp --leverage 5 --margin-mode cross
# confirm with user (market, type, side, size, price bound, leverage) →
purr lighter order --market SOL --market-type perp --side buy --size 10 --price <bound> --type market
purr lighter trades                                        # did it fill?
purr lighter positions                                     # net effect
```

For a market order the `--price` is the **worst acceptable fill**. Walk
cumulative depth for the exact size, compute projected VWAP and worst level, and
if the user gave no tolerance, present those numbers and ask them to pick the
cap — do not apply a default buffer. See [trading.md](trading.md).

Note `balances` / `positions` return a readiness object rather than collections
until `account.status` is `ready` — an empty-looking result is a state, not an
empty portfolio.

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

## 9. Disabling the integration safely

```bash
purr lighter active-orders        # what is resting
purr lighter positions            # what is open
purr lighter deposits --limit 10  # unresolved deposits
purr lighter requests --limit 10  # unresolved trading/withdraw/transfer requests
# state the exposure back, get acknowledgement of THAT list →
purr lighter disable
```

`disable` cancels nothing and closes nothing — it only flips the flag, and
afterwards only `status`/`enable`/`disable` work. Live orders, positions,
pending deposits and unresolved requests stay on Lighter/platform while becoming
invisible to the agent and dashboard. Either resolve the exposure first, or make
sure the user has acknowledged the specific list before flipping it.

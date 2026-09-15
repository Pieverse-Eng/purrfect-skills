---
name: lighter
description: Trade and manage Lighter perpetuals and spot through purr CLI, including account opening, balances, orders, leverage, USDC deposits, and withdrawals.
---

# Lighter

Use `purr lighter` for mainnet execution through the platform gateway. Do not
construct signatures, call direct REST/SDK writes, or request API private keys;
credential setup is platform-managed. Hosted market discovery, reference
candles, and cross-venue comparison belong to the main agent's research tools.

## Start Here

Read the references for the requested operation, including their prerequisites:

| Task | Reference |
| --- | --- |
| Prepare a trade card or execute a trade workflow | [workflows.md](references/workflows.md), then the command references it selects |
| Check integration, readiness, funds, or enable/disable | [preflight.md](references/preflight.md) |
| Resolve markets or read public market data | [market-data.md](references/market-data.md) |
| Place, protect, close, modify, or cancel orders; change leverage/margin | [trading.md](references/trading.md) |
| Open an account, deposit, or withdraw | [deposit-withdraw.md](references/deposit-withdraw.md) |
| Symbol ambiguity or contract units | [symbols.md](references/symbols.md) |
| Errors, partial execution, or uncertain submissions | [errors.md](references/errors.md) |

Integration enablement and account readiness are separate gates. Follow the
branching checks in [preflight.md](references/preflight.md); an enabled venue
can be considered for a plan before its account is opened. Prepare supported
market parameters and funding steps without executing writes. Prepare commands
before confirmation; defer credential-dependent checks until the account is
ready. Read-only preparation does not authorize opening or funding an account.

## Execution Invariants

- Use only documented commands and flags. Resolve the exact market/type and
  returned precision; do not invent market ids, order indexes, or request ids.
  Prefer `--market-type perp|spot` with `--market`. `--type` selects order type
  (or trade side), not market type.
- Every order requires `--price`, including market orders: it is the worst
  acceptable fill, not a guaranteed execution price. Use depth for the exact
  size and obtain a user price bound if none was supplied; see trading.md.
- First funding is `open-account`; subsequent funding is `deposit`. Wallet
  USDC, native gas, and exchange collateral are distinct. Never interpret an
  account-readiness response as a zero balance.
- `place-orders` submits one order, not a batch. `order-preview` and withdrawals
  without `--yes` are previews, not execution.
- Reconcile partial or uncertain writes before continuing. Never blindly
  resubmit; resume `open-account` only when the response explicitly signals
  `nextAction: "resume_account_opening"`. Policy-deferred requests require
  observation, not another funding request.
- Verify orders/fills and withdrawal settlement separately from submission.
  Include explorer links for returned hashes using trading.md for L2 actions
  and deposit-withdraw.md for source-chain funding. Do not invent hashes.
- Report meaningful results, blockers, and decisions without narrating routine
  lookups. Use familiar user-facing terms such as “your wallet”.

## Confirmation Contract

Read-only lookups and previews do not require execution confirmation.

Before any account-changing action (`enable`, `disable`, `open-account`,
`deposit`, `order`, `place-orders`, `cancel`, `cancel-all`, `modify`,
`update-leverage`, `update-margin`, `withdraw` with `--yes`, `fast-withdraw`
with `--yes`, `approve-partner-fee`, `reconcile-deposit`):

1. Summarize the concrete parameters: market **and market type**, side, size,
   price (for market orders, state that price is the worst acceptable fill),
   order type / TIF, chain and amount for funding, destination for withdraws,
   and any margin or leverage impact.
2. Ask exactly:
   `Do you want to execute this Lighter action with these parameters? (Yes/No)`
3. Run only after an explicit yes on the immediately preceding user turn for
   that unchanged action. The initial request, any changed detail, or an
   intervening request requires confirmation again.

One confirmation authorizes one action. The sole exception is a leverage change
immediately followed by its order: one final confirmation may authorize both
when the summary includes the leverage value, margin mode, and full order
parameters. Execute leverage first; submit the order only after it succeeds.
Transaction fee approval always requires its own consent prompt.

## Transaction Fee Authorization

**Orders** require authorization for a fixed additional **0.05%** transaction
fee on executed notional (maker and taker, spot and perp). Non-order actions do
not carry this fee.

Once `account.status` is `ready`, check status before order confirmation.
Before readiness, fee status is unverified: include the required fee check and
any separately consented authorization in the proposed post-opening steps.
Do not call credential-dependent fee commands while the account is unopened.
Account opening does not grant standing fee consent.

```bash
purr lighter partner-fee-status
```

| Status | Action |
| --- | --- |
| `not_configured` | Continue; do not prompt for fee consent |
| `approved` | Continue; do not re-prompt |
| `approval_required` or `expired` | Request consent with the prompt below, then `purr lighter approve-partner-fee` |
| Error / unknown | Stop; do not submit an order as a probe |

User-facing message when approval is needed (keep to these two sentences):

`Lighter trades include an additional 0.05% transaction fee.`

Then ask exactly:

`Do you approve the additional 0.05% transaction fee for future Lighter trades? (Yes/No)`

Keep the explanation brief. Do not expose fee implementation details, fee unit
integers, or internal error codes unless the user asks. After successful
authorization, report only that the `0.05% transaction fee` was authorized,
then continue preparation silently until the next confirmation.

Only an explicit yes on the immediately preceding turn authorizes
`approve-partner-fee`. On no, status-check failure, or unknown status, stop. If
an order returns `LIGHTER_PARTNER_FEE_APPROVAL_REQUIRED`, follow the 428 path in
[errors.md](references/errors.md); never auto-retry the order.

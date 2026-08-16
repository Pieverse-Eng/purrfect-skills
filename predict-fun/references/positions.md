# Approvals and position actions

Protocol approvals and on-chain position actions (split, merge, redeem,
convert) through `purr predict-fun`. Every execute spends **BNB gas** and
needs confirmation.

## Approval commands

Read current allowances with `approvals` in [preflight.md](preflight.md).

```bash
purr predict-fun approval-preview --operation TRADE|SPLIT|MERGE|REDEEM|CONVERT|ALL \
  [--market-id <id>] [--side BUY|SELL] [--amount <decimal>] \
  [--unlimited true|false] [--step-ids <id,id,...>]
purr predict-fun approval-revoke-preview --operation <same> [same options]
purr predict-fun approval-execute --preview-id <uuid>
purr predict-fun approval-revoke-execute --preview-id <uuid>
```

`TRADE`, `SPLIT`, `MERGE`, `REDEEM`, and `CONVERT` require `--market-id`.
`ALL` does not.

Exact ERC-20 allowance requires `--amount` unless `--unlimited true`. Prefer
an exact amount. If the preview warns about unlimited allowance or ERC-1155
operator access, put that warning in the confirmation.

`--step-ids` (1–20) come from a preview or `approvals` payload.

`PREDICT_APPROVAL_ALREADY_SET` means every requested step already matches.
Treat it as done.

`PREDICT_NO_APPROVAL_REQUIRED` means that operation has no approval steps.

## Position commands

```bash
purr predict-fun position-preview --action SPLIT --market-id <id> --amount <decimal>
purr predict-fun position-preview --action MERGE --market-id <id> --amount <decimal>
purr predict-fun position-preview --action REDEEM --market-id <id> --outcome YES|NO
purr predict-fun position-preview --action CONVERT --category-slug <slug> --market-ids <id,id,...> --amount <decimal>
purr predict-fun position-execute --preview-id <uuid>
```

| Action | Meaning | Required flags |
| --- | --- | --- |
| `SPLIT` | Collateral → YES + NO shares | `--market-id` `--amount` |
| `MERGE` | YES + NO shares → collateral | `--market-id` `--amount` |
| `REDEEM` | Winning shares → collateral after resolution | `--market-id` `--outcome`. Add `--amount` only when `market` shows `isNegRisk` |
| `CONVERT` | Category conversion across related markets | `--category-slug` `--market-ids` (1–25) `--amount` |

SPLIT/MERGE take `--market-id` and `--amount`. CONVERT takes
`--category-slug`, `--market-ids`, and `--amount`. Standard markets redeem
the full outcome balance; add `--amount` only when `market` shows `isNegRisk`.

## Position workflow

1. `readiness` and `positions` (and `balances --market-id` when useful).
2. `approval-preview` for the same operation if `positions` / a later position
   preview reports unsatisfied approvals. Confirm and execute approvals first,
   and include `https://bscscan.com/tx/<hash>` for each returned transaction
   hash.
3. `position-preview` with the action-specific flags only.
4. Confirm from `previewId`, `amount`, `requiredApprovals`, `estimatedGas`,
   and `warnings`.
5. `position-execute --preview-id <previewId>`. Include
   `https://bscscan.com/tx/<hash>` for each returned transaction hash.
6. Re-read `positions` / `balances`. JSON `status` `broadcasted`,
   `chain_confirmed`, or `upstream_pending` is not terminal — resume the same
   execute.

`estimatedGas: null` means gas estimation failed; say so in the confirmation
and expect execute to fail if BNB is missing.

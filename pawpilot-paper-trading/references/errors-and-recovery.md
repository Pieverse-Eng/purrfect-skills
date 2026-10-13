# Errors and recovery

Use the tool's reason, target, checkedAt and coverage. Do not label an entire
venue down because one account or market is blocked.

| Reason category (not a literal status) | Response |
| --- | --- |
| needs_clarification | Ask the missing intent question; do not prepare a guessed order |
| blocked | Explain the actual book/mark/funding/balance/limit reason and allowed recovery |
| stale | Read new evidence and prepare a new draft for a new human review |
| scope_mismatch | Ask the user to select the intended page/account; keep the old card bound |
| unsupported | Explain the specific product/capability/sizing limit; do not use Live as fallback |
| unknown/timeout | Query the original action/call receipt; do not create a replacement command |

Native funding confirmation and an account's pending settlement are separate.
Neither can be waived by Coach. Missing historical reference prices are not
current prices or zero funding.

Host blocks have `status="blocked"` and a specific `reason`; use that reason,
not an invented status from the table. Native bridge timeout has
`status="error"`, `error.code="HOST_CALL_UNKNOWN"` and the original `callId`.
Recover the original action using `paper_read(operation="receipt", callId=...)`.

After human confirmation, the action receipt returns a persisted command
response. For an order that may be the original accepted snapshot, even when
the action/command is completed. Re-reading it does not update the order to
filled. Active-order reads show current active orders only; disappearance is
not final evidence. If the receipt proves acceptance but no authoritative
final state is exposed, report "accepted; final execution not verified".
Otherwise retain the recorded rejection, pending or unknown outcome. Direct
the user to the terminal order/receipt view for unavailable final evidence.
Batch cancellation also returns a current job; use its
status/counts. Retrying read-only receipt queries is safe; a new financial key
is not recovery. Changing the page keeps the old card's original scope.

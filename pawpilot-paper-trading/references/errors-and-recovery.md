# Errors and recovery

Use the tool's reason, target, checkedAt and coverage. Do not label an entire
venue down because one account or market is blocked.

| Result | Response |
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

After a human confirmation, read the original action receipt. Accepted, resting,
partially filled, filled, cancelled, rejected and unknown are different outcomes.
Retrying receipt reads is safe; retrying a financial operation with a new key
is not recovery. If the page changed, the old card keeps its original scope.

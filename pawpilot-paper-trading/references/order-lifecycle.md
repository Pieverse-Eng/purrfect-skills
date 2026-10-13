# Order lifecycle

Read the current open orders or positions with `paper_read`; preserve returned
IDs, marketKeys and versions. Paginated results are not the complete account.

| Operation | Prepared action |
| --- | --- |
| Amend an open order | `amend_order` with orderId, expectedVersion and explicit changed fields |
| Cancel an open order | `cancel_order` with orderId and expectedVersion |
| Cancel matching open orders | `cancel_all` limited to the bound account and explicit market scope |
| TP/SL on a current position | `position_protection` with positionId, expectedVersion and requested legs |
| Close/reduce a position | Opposite-side `place_order`, reduceOnly true, verified native quantity |

Explain the concrete target when multiple candidates exist and ask the user to
choose; a substring/ticker match is insufficient. Ask whether unspecified
protection legs are to be preserved or removed. Use supported trigger source
and market/limit execution from the returned venue capabilities.

All operations go through `paper_prepare_card` and the same manual web review.
An old card cannot be treated as consent to a newer version. Failed amendment
does not establish that the original order changed or its reservation released.
A batch cancellation acceptance is not completion: read its original action
receipt until the reported job is final, and retain skipped/failed counts.

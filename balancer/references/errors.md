# Balancer Errors and Deferred Operations

Interpret Platform and CLI errors before deciding whether to retry.

## Wallet Policy

| Result | Action |
| --- | --- |
| `POLICY_DEFERRED` / manual approval required | Report the approval request and expiry. Do not bypass policy or change parameters. After approval, retry the same command and bounds. |
| Policy denied, wallet frozen, cap exceeded, or address not allowlisted | Report the policy reason. Do not retry until the policy or request changes legitimately. |
| Approved request later needs a new quote | Keep the approved execution floor or cap. Never execute a materially worse quote under an earlier approval. |

## Pool and Input Errors

| Code or message | Meaning and action |
| --- | --- |
| `POOL_OPERATION_UNSUPPORTED` | The pool deterministically rejects the requested join/exit mode. If the user did not select that exact pool, try the next compatible reviewed candidate without changing the requested tokens or mode. Otherwise report the limitation; do not treat it as a transient RPC error. |
| `INVALID_BOOSTED_TOKENS_OUT` | `tokensOut` does not cover every boosted pool position or uses a mismatched wrapped/underlying token. Correct the ordered token selection and quote again. |
| `DoesNotSupportUnbalancedLiquidity` | For a single-token request, try another reviewed pool. Use proportional liquidity only if the user agrees to provide every required token. |
| `WrapAmountTooSmall` | Increase the amount only with user approval, or choose a non-wrapping route. |
| Recovery operation unavailable | Verify that the pool supports recovery and is currently in recovery mode. |
| No SOR path | Try a different reviewed pool, protocol, or amount after explaining the change. Do not retry the same route indefinitely. |
| Insufficient token/BPT/native balance | Recheck balances. Preserve enough native token for gas and include possible approval transactions. |

## Upstream and Broadcast Errors

| Status or state | Action |
| --- | --- |
| HTTP 429 | Respect `retry_after`. Retry safe read-only pool/quote requests later; do not blindly replay a write. |
| HTTP 503 | Treat Balancer or RPC as temporarily unavailable. Retry a read-only quote with bounded delay. |
| HTTP 504 | Treat as upstream timeout. Check whether a write obtained a hash before retrying. |
| HTTP 502 / wallet service error | Inspect the structured reason and logs if available. Do not assume retryability. |
| `broadcast_unknown` | Stop. The transaction may already be on-chain. Reconcile signer, Platform, and RPC state before any replacement. |
| `broadcasting` / already in progress | Return the in-progress state. Let Platform deduplication recover the existing workflow. |
| `reverted` | Report the revert and approval hashes. Requote or change the pool/mode only after identifying the deterministic cause. |

## Retry Invariants

- Keep chain, protocol, pool, tokens, amounts, slippage, and raw safety bounds
  identical when resuming an approved or in-progress operation.
- Requote instead of executing when a quote expired or any economic parameter
  changed.
- Never generate a deduplication UUID. Platform owns request deduplication and
  may return an idempotent prior result.
- Never submit a second write merely because the first response lacked a final
  receipt.

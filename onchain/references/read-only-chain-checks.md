# Read-Only Chain Checks

Use JSON-RPC or an explorer workflow for transaction lookup, receipt decoding,
log inspection, sender tracing, and token state checks.

## Workflow

1. Identify the chain and transaction hash, address, token, or contract.
2. Pick the matching JSON-RPC endpoint or explorer.
3. Read the chain state.
4. Summarize the relevant fields, such as status, sender, recipient, logs,
   token movement, or balance.

## Common RPC Endpoints

| Chain | RPC URL |
| --- | --- |
| BNB Smart Chain | `https://bsc-rpc.publicnode.com` |
| Ethereum | `https://ethereum-rpc.publicnode.com` |
| Base | `https://base-rpc.publicnode.com` |
| Arbitrum One | `https://arbitrum-one-rpc.publicnode.com` |
| Optimism | `https://optimism-rpc.publicnode.com` |
| Polygon | `https://polygon-bor-rpc.publicnode.com` |
| X Layer | `https://rpc.xlayer.tech` |
| Robinhood Chain | `https://rpc.mainnet.chain.robinhood.com` |

## Syntax

```bash
curl -s <rpc_url> \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"<method>","params":[...]}'
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `<rpc_url>` | Required | Chain endpoint, such as `https://bsc-rpc.publicnode.com` for BNB Smart Chain. |
| `jsonrpc` | Required | JSON-RPC version. Use `"2.0"`. |
| `id` | Optional | Client-chosen request ID used to match the response. |
| `method` | Required | Read method, such as `eth_getTransactionReceipt`, `eth_getTransactionByHash`, `eth_getLogs`, `eth_call`, or `eth_getBalance`. |
| `params` | Required by method | Method arguments, such as a transaction hash, address, block tag, log filter, or encoded call. |

## Example

Look up a transaction receipt:

```bash
curl -s https://bsc-rpc.publicnode.com \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_getTransactionReceipt","params":["0x..."]}'
```

### Response Shape

JSON-RPC success responses use the standard envelope:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {}
}
```

Explorer APIs vary, but usually return a status field plus a result payload.
Normalize the final answer to the fields the user asked for, such as status,
sender, recipient, logs, token movement, or balance.

### JSON-RPC Error Codes

| Code | Meaning |
| ---: | --- |
| -32700 | Parse error. |
| -32600 | Invalid request. |
| -32601 | Method not found. |
| -32602 | Invalid params. |
| -32603 | Internal error. |

HTTP failures such as `400`, `401`, `403`, `404`, `429`, or `5xx` come from the
RPC provider or explorer and should be reported with the provider message.

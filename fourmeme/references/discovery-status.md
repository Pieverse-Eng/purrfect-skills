# Discovery / Status

Use discovery and status commands before trading or creation when route support,
raised-token support, or agent-wallet status is uncertain.

## Workflow

1. Get the user's EVM wallet if needed.
2. Check BSC native BNB balance before any write flow.
3. Use `raised-tokens` when the requested raised token or quote token is not
   known.
4. Use `agent-wallet` when the user asks whether a wallet is authorized as a
   four.meme agent wallet.
5. Return the relevant symbols, addresses, wallet status, and any limits shown
   by the command.

## Syntax

```bash
purr fourmeme raised-tokens
purr fourmeme agent-wallet --wallet <0x_wallet>
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--wallet <0x_wallet>` | Required for `agent-wallet` | EVM wallet address to check. |

## Commands

```bash
purr wallet address --chain-type ethereum
purr wallet balance --chain-type ethereum --chain-id 56
purr fourmeme raised-tokens
purr fourmeme agent-wallet --wallet 0xWallet
```

## Response Shape

`raised-tokens` prints an array of raised-token config objects:

```json
[
  {
    "symbol": "BNB",
    "nativeSymbol": "BNB",
    "symbolAddress": "0xbb4c...",
    "buyFee": "0.01",
    "sellFee": "0.01",
    "status": "PUBLISH",
    "networkCode": "BSC"
  }
]
```

`agent-wallet` prints one JSON object:

```json
{
  "wallet": "0x...",
  "isAgent": false
}
```

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Missing required argument: --wallet` | Agent wallet status needs a wallet address. |
| `Invalid address` | The wallet is not a valid EVM address. |
| `four.meme HTTP ...` or `four.meme API error: ...` | The four.meme API rejected or failed the request. |
| `Balance query failed: ...` | Wallet balance preflight failed. |

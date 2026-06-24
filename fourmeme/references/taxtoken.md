# TaxToken

Use TaxToken workflows when the user wants to create a tax-enabled four.meme
token, inspect claimable tax rewards, or claim rewards.

## Workflow

For TaxToken creation:

1. Follow [token-creation.md](token-creation.md).
2. Collect the complete tax configuration.
3. Validate the fee rate and allocation sum before creating.
4. Show all tax settings and ask for confirmation before `--execute`.

For rewards:

1. Identify the TaxToken contract and wallet.
2. Run `tax-rewards` to inspect claimable values.
3. If the user wants to claim, check BSC BNB balance for gas.
4. Confirm the token, wallet, and claimable amount before execution.
5. Run `tax-claim --execute`.
6. Report the transaction result.

## Syntax

```bash
purr fourmeme create-token ... --tax-fee-rate <1|3|5|10> --tax-burn-rate <n> --tax-divide-rate <n> --tax-liquidity-rate <n> --tax-recipient-rate <n> [--tax-recipient-address <0x_address>] --tax-min-sharing <amount> --execute
purr fourmeme tax-rewards --token <0x_token> --wallet <0x_wallet>
purr fourmeme tax-claim --token <0x_token> --wallet <0x_wallet> --execute
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--tax-fee-rate <1|3|5|10>` | Required for TaxToken creation | Trading fee rate. |
| `--tax-burn-rate <n>` | Required for TaxToken creation | Burn allocation percentage. |
| `--tax-divide-rate <n>` | Required for TaxToken creation | Dividend allocation percentage. |
| `--tax-liquidity-rate <n>` | Required for TaxToken creation | Liquidity allocation percentage. |
| `--tax-recipient-rate <n>` | Required for TaxToken creation | Recipient allocation percentage. |
| `--tax-recipient-address <0x_address>` | Required when recipient rate is greater than 0 | Address to receive allocated tokens. |
| `--tax-min-sharing <amount>` | Required for TaxToken creation | Minimum sharing threshold in four.meme's integer format. |
| `--token <0x_token>` | Required for rewards and claim | TaxToken contract address. |
| `--wallet <0x_wallet>` | Required for rewards and claim | Wallet to query or claim for. |
| `--execute` | Required for claiming or creation | Builds, signs, and broadcasts through the wallet execution flow. |

## Commands

Create a TaxToken:

```bash
purr fourmeme create-token \
  --wallet 0xWallet \
  --login-nonce NONCE \
  --login-signature-file /tmp/fourmeme_login_signature.txt \
  --name "My Tax Token" \
  --symbol TAX \
  --description "My tax token description" \
  --label Meme \
  --image-file /tmp/logo.png \
  --tax-fee-rate 5 \
  --tax-burn-rate 20 \
  --tax-divide-rate 30 \
  --tax-liquidity-rate 40 \
  --tax-recipient-rate 10 \
  --tax-recipient-address 0xRecipient \
  --tax-min-sharing 100000 \
  --execute
```

Query rewards:

```bash
purr fourmeme tax-rewards --token 0xToken --wallet 0xWallet
```

Claim rewards:

```bash
purr fourmeme tax-claim --token 0xToken --wallet 0xWallet --execute
```

## Tax Rules

- `tax-fee-rate` must be one of `1`, `3`, `5`, or `10`.
- Burn, divide, liquidity, and recipient rates must sum to `100`.
- If recipient rate is `0`, recipient address must be empty.
- If recipient rate is greater than `0`, recipient address must be a valid EVM address.
- `tax-min-sharing` must follow four.meme's integer format requirements.

## Response Shape

`tax-rewards` prints one JSON object:

```json
{
  "token": "0x...",
  "wallet": "0x...",
  "claimableFee": "0",
  "claimedFee": "0",
  "userInfo": {
    "share": "0",
    "rewardDebt": "0",
    "claimable": "0",
    "claimed": "0"
  }
}
```

`tax-claim --execute` prints the wallet execution result for the claim
transaction.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `tax-fee-rate must be one of ...` | Fee rate is outside allowed options. |
| `tax allocation rates must sum to 100` | Burn/divide/liquidity/recipient rates are invalid. |
| `recipient address must be empty` | Recipient rate is 0 but an address was provided. |
| `recipient address is required` | Recipient rate is greater than 0 but no address was provided. |
| `tax-min-sharing ...` | Minimum sharing value is outside four.meme's accepted integer format. |
| `The contract function "userInfo" reverted ...` | The token may not be a TaxToken. Report the exact error and stop. |
| `insufficient native gas balance` | Wallet lacks BNB for a claim or creation transaction. |

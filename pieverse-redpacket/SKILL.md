---
name: pieverse-redpacket
description: Use when the user wants to claim a Pieverse red packet campaign through OKX APP / OKX A2A. Creates an OKX A2A payment request and hands the paymentId to Pieverse.
---

# Pieverse Red Packet via OKX APP

## Flow

### 1. Required Prompt Values

The prompt must provide:

- `claimId`
- `instanceId`
- `amount` as the decimal token amount for `onchainos` CLI, not the atomic on-chain amount
- `symbol` as one of the supported OKX CLI symbols below
- `expiresIn`

If any value is missing, ask for it.

Use them as `CLAIM_ID`, `INSTANCE_ID`, `AMOUNT`, `SYMBOL`, and `EXPIRES_IN` in
the commands below.

### 2. Supported Symbols

Pieverse red packets on OKX A2A support these X Layer tokens:

| Pieverse token | X Layer contract | OKX CLI `--symbol` |
|---|---|---|
| USDG | `0x4ae46a509f6b1d9056937ba4500cb143933d2dc8` | `USDG` |
| USD₮0 | `0x779ded0c9e1022225f8e0630b35a9b54be713736` | `USDT` |
| USDC | `0x74b7f16337b8972027f6196a17a631ac6de26d22` | `USDC` |

If the campaign token is USD₮0, set `SYMBOL=USDT`. Do not pass `USDT0` to
`onchainos payment a2a-pay create`.

### 3. Ensure OKX Wallet Login

```bash
onchainos wallet status
```

If `data.loggedIn` is not `true`:

1. Ask for the user's OKX Agentic Wallet email.
2. Send the verification code:

   ```bash
   onchainos wallet login "$EMAIL"
   ```

3. Ask for the verification code and verify:

   ```bash
   onchainos wallet verify "$OTP_CODE"
   ```

4. Re-check:

   ```bash
   onchainos wallet status
   ```

Continue only when `data.loggedIn` is `true`.

### 4. Resolve Recipient

```bash
onchainos wallet addresses
```

Set `RECIPIENT` to `data.xlayer[0].address`. If it is missing, use
`data.evm[0].address`.

### 5. Create OKX A2A Payment

```bash
onchainos payment a2a-pay create \
  --amount "$AMOUNT" \
  --symbol "$SYMBOL" \
  --recipient "$RECIPIENT" \
  --expires-in "$EXPIRES_IN"
```

Read `paymentId` from `data.payment_id`. If it is missing, stop and show the
OKX create output.

### 6. Hand Off paymentId to Pieverse

```bash
curl -sS -X POST "${PIEVERSE_REDPACKET_API_URL:-https://www.pieverse.io}/api/redpackets/okx-a2a/submit" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"instanceId\":\"$INSTANCE_ID\",\"claimId\":\"$CLAIM_ID\",\"paymentId\":\"$PAYMENT_ID\"}"
```

- If `ok` is not `true`, show the backend message and stop.
- If `data.status` is `completed`, show success with `data.txHash`.
- If `data.status` is `settling`, continue to Step 7.
- For any other response, stop and show the response.

### 7. Poll Pieverse Status for Settling

Only run this step after Step 6 returns `settling`.

Poll Pieverse for up to about 60 seconds:

```bash
curl -sS -X POST "${PIEVERSE_REDPACKET_API_URL:-https://www.pieverse.io}/api/redpackets/okx-a2a/status" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"instanceId\":\"$INSTANCE_ID\",\"claimId\":\"$CLAIM_ID\",\"paymentId\":\"$PAYMENT_ID\"}"
```

- If `data.status` is `completed`, show success with `data.txHash`.
- If `data.status` is `settling`, wait 3 seconds and query the same endpoint again.
- If `ok` is not `true`, show the backend message.
- For any other response, stop and show the response.

Success message:

```text
Red packet claimed successfully.
txHash: <txHash>
```

Failed message:

```text
Red packet claim failed.
Reason: <reason>
```

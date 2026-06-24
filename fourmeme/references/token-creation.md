# Token Creation

Use token creation when the user wants to create a new four.meme token on BSC.
Creation is a mixed off-chain API and on-chain execution flow.

When required inputs are missing, collect them but still show the complete
planned flow: BSC BNB balance check, `login-challenge`, `purr wallet sign`,
writing the signature to a file, and the final `create-token --execute` command
using either `--image-url` or `--image-file`. Do not stop at only listing
required fields.

## Workflow

1. Get the user's EVM wallet with `purr wallet address --chain-type ethereum`.
2. Check BSC BNB balance. No-pre-sale creation needs about `0.01 BNB + gas`;
   use `0.012-0.015 BNB` minimum, or `0.02 BNB` when also testing trades.
3. If raised-token support is uncertain, run `purr fourmeme raised-tokens`.
4. Collect required token metadata and image source.
5. Show token name, symbol, label, image, socials, raised token, pre-sale,
   X Mode, AntiSniper, and tax settings if present. Ask for confirmation.
6. After confirmation, get the four.meme login challenge:

   ```bash
   purr fourmeme login-challenge --wallet 0xWallet
   ```

   This returns `nonce` and `message` (`You are sign in Meme {nonce}`).

7. Sign the challenge with the user's wallet:

   ```bash
   purr wallet sign --address 0xWallet --message "<message>"
   ```

   Write the returned signature to a temp file such as
   `/tmp/fourmeme_login_signature.txt`. Do not paste long signature hex
   directly into the shell command.

8. Create the token with the signed login challenge and confirmed metadata.
   Using an existing image URL:

   ```bash
   purr fourmeme create-token \
     --wallet 0xWallet \
     --login-nonce NONCE \
     --login-signature-file /tmp/fourmeme_login_signature.txt \
     --name "My Token" \
     --symbol MTK \
     --description "My token description" \
     --label AI \
     --image-url https://example.com/logo.png \
     --raised-token BNB \
     --pre-sale 0.1 \
     --x-mode true \
     --anti-sniper false \
     --execute
   ```

   Or using a local image file:

   ```bash
   purr fourmeme create-token \
     --wallet 0xWallet \
     --login-nonce NONCE \
     --login-signature-file /tmp/fourmeme_login_signature.txt \
     --name "My Token" \
     --symbol MTK \
     --description "My token description" \
     --label Meme \
     --image-file /tmp/logo.png \
     --execute
   ```

9. Report the transaction result.

## Syntax

```bash
purr fourmeme login-challenge --wallet <0x_wallet>
purr wallet sign --address <0x_wallet> --message "<challenge_message>"
purr fourmeme create-token --wallet <0x_wallet> --login-nonce <nonce> --login-signature-file <path> --name <name> --symbol <ticker> --description <description> --label <label> (--image-url <url> | --image-file <path>) [options] --execute
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--wallet <0x_wallet>` | Required | Creator wallet address. |
| `--login-nonce <nonce>` | Required | Nonce from `login-challenge`. |
| `--login-signature <0x_sig>` | Required if no signature file | Signature of `You are sign in Meme {nonce}`. Prefer file form for long signatures. |
| `--login-signature-file <path>` | Required if no inline signature | File containing the login signature. |
| `--name <name>` | Required | Token name. |
| `--symbol <ticker>` | Required | Token ticker. |
| `--description <text>` | Required | Token description. |
| `--label <label>` | Required | Category label. |
| `--image-url <url>` | Required if no image file | Existing image URL. A four.meme CDN URL can be used directly; other URLs are uploaded through the API. |
| `--image-file <path>` | Required if no image URL | Local image file to upload. |
| `--raised-token <symbol_or_address>` | Optional | Raised token from `raised-tokens`; defaults to BNB. |
| `--pre-sale <bnb_amount>` | Optional | Creator pre-purchased BNB amount. Must be `0` for non-BNB raised tokens. |
| `--website <url>` | Optional | Project website. |
| `--twitter <url>` | Optional | Project Twitter/X URL. |
| `--telegram <url>` | Optional | Project Telegram URL. |
| `--x-mode <true|false>` | Optional | Creates an X Mode token when true. |
| `--anti-sniper <true|false>` | Optional | Enables AntiSniper fee mode when true. |
| `--creation-fee <bnb_amount>` | Optional | Overrides default creation value. Use only when the platform fee is known to differ. |
| `--execute` | Required for user-facing creation | Builds, signs, and broadcasts through the wallet execution flow. |

## Commands

```bash
purr fourmeme login-challenge --wallet 0xWallet
purr wallet sign --address 0xWallet --message "You are sign in Meme 123456"
purr fourmeme create-token \
  --wallet 0xWallet \
  --login-nonce NONCE \
  --login-signature-file /tmp/fourmeme_login_signature.txt \
  --name "My Token" \
  --symbol MTK \
  --description "My token description" \
  --label AI \
  --image-url https://example.com/logo.png \
  --raised-token BNB \
  --pre-sale 0.1 \
  --x-mode true \
  --anti-sniper false \
  --execute
purr fourmeme create-token \
  --wallet 0xWallet \
  --login-nonce NONCE \
  --login-signature-file /tmp/fourmeme_login_signature.txt \
  --name "My Token" \
  --symbol MTK \
  --description "My token description" \
  --label Meme \
  --image-file /tmp/logo.png \
  --execute
```

## Labels

Supported labels:

- `Meme`
- `AI`
- `Defi`
- `Games`
- `Infra`
- `De-Sci`
- `Social`
- `Depin`
- `Charity`
- `Others`

## Raised-token and Pre-sale Rules

Use `purr fourmeme raised-tokens` to discover supported raised tokens.

- `--raised-token` defaults to BNB.
- Official create-token docs describe `preSale` as creator pre-purchased BNB.
- `--raised-token BNB --pre-sale <bnb_amount>` is allowed.
- `--raised-token USDT|USDC|CAKE|... --pre-sale 0` is allowed.
- Non-BNB raised tokens with positive `--pre-sale` are intentionally rejected.

## Funding Rules

Creating a token executes `TokenManager2.createToken(createArg, signature)` and
requires BNB for `value` plus gas.

- Default creation value is `0.01 BNB`.
- BNB `--pre-sale` is added to that value.
- Non-BNB raised-token creation still needs the default BNB creation value, but
  not a positive pre-sale.
- For `--raised-token BNB --pre-sale X`, prepare about `0.02 BNB + X`.

## Response Shape

`login-challenge` prints one JSON object:

```json
{
  "wallet": "0x...",
  "nonce": "123456",
  "message": "You are sign in Meme 123456"
}
```

`create-token` success prints the wallet execution result for the
`TokenManager2.createToken` transaction.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Signature for this request is not valid` | Nonce/signature expired or does not match. Get a fresh challenge, sign again, and retry once. |
| `Unsupported label` | Label is not one of the supported categories. |
| `Non-BNB raised tokens currently require preSale to be 0` | Use `--pre-sale 0` or switch to `--raised-token BNB`. |
| `An image is required: provide --image-url or --image-file` | No token image source was provided. |
| `Image URL not valid` or upload errors | User must provide a direct image URL or local image file accepted by four.meme. |
| `four.meme login failure` or `four.meme HTTP ...` | four.meme API rejected the login or create request. |
| `insufficient native gas balance` | Wallet lacks BNB for creation value plus gas. |
| `Failed to execute EVM transaction` | Wallet execution or chain broadcast failed; report the exact upstream error. |

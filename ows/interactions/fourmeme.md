# Four Meme With OWS

Use this file when an OWS wallet should create, trade, claim, or authenticate
for four.meme.

## Login Challenge

Token creation requires a four.meme login signature. Build the challenge, sign
the exact message with OWS, and save only the signature:

```bash
purr fourmeme login-challenge \
  --wallet <ows-evm-address> \
  > /tmp/fourmeme-login.json

OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet <ows-wallet> \
  --chain bsc \
  --message "$(jq -r .message /tmp/fourmeme-login.json)" \
  --json \
  > /tmp/fourmeme-signed-message.json

jq -r .signature /tmp/fourmeme-signed-message.json \
  > /tmp/fourmeme-signature.txt
```

Stop if the signing result address does not match `<ows-evm-address>`.

## Create Token

Use the nonce and signature from the login challenge. Build steps first, then
execute with OWS:

```bash
purr fourmeme create-token \
  --wallet <ows-evm-address> \
  --login-nonce "$(jq -r .nonce /tmp/fourmeme-login.json)" \
  --login-signature-file /tmp/fourmeme-signature.txt \
  --name "<name>" \
  --symbol "<symbol>" \
  --description "<description>" \
  --label "<label>" \
  --image-url "<image-url>" \
  > /tmp/fourmeme-create.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/fourmeme-create.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <bsc-rpc>
```

Include optional creation flags from `fourmeme` only when the user asks for
them, such as `--website`, `--twitter`, `--telegram`, `--pre-sale`, `--x-mode`,
`--anti-sniper`, tax flags, or `--raised-token`.

## Buy And Sell

Generate steps without `--execute`:

```bash
purr fourmeme buy \
  --token <token-address> \
  --wallet <ows-evm-address> \
  --funds <bnb-or-quote-amount> \
  --slippage <0-to-1> \
  > /tmp/fourmeme-buy.json

purr fourmeme sell \
  --token <token-address> \
  --wallet <ows-evm-address> \
  --amount <token-amount-wei> \
  --slippage <0-to-1> \
  > /tmp/fourmeme-sell.json
```

Execute the generated file after confirmation:

```bash
OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/fourmeme-buy.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <bsc-rpc>
```

For quote-token flows, use `buy-with-bnb` or `sell-for-bnb` with the exact
minimums returned by the four.meme flow.

## Tax Rewards

```bash
purr fourmeme tax-rewards \
  --token <tax-token-address> \
  --wallet <ows-evm-address>

purr fourmeme tax-claim \
  --token <tax-token-address> \
  --wallet <ows-evm-address> \
  > /tmp/fourmeme-tax-claim.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/fourmeme-tax-claim.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <bsc-rpc>
```

Do not add `--execute` to `purr fourmeme` in OWS flows.

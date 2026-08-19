# Pancake With OWS

Use this file when an OWS wallet should execute PancakeSwap BSC flows.

## Execution Pattern

Run `purr pancake` without `--execute` to emit `steps`, inspect the steps, get
user confirmation, then execute with OWS:

```bash
OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/pancake-steps.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <bsc-rpc>
```

Use the OWS EVM address as `--wallet` wherever the Pancake command asks for a
wallet or recipient.

## Swap

```bash
purr pancake swap \
  --path <token-in>,<token-out> \
  --amount-in-wei <amount-in-wei> \
  --amount-out-min-wei <minimum-out-wei> \
  --wallet <ows-evm-address> \
  --deadline <unix-or-relative-seconds> \
  --chain-id 56 \
  > /tmp/pancake-steps.json
```

## Liquidity

```bash
purr pancake add-liquidity \
  --token-a <token-a> \
  --token-b <token-b> \
  --amount-a-wei <amount-a-wei> \
  --amount-b-wei <amount-b-wei> \
  --wallet <ows-evm-address> \
  --deadline <unix-or-relative-seconds> \
  --chain-id 56 \
  > /tmp/pancake-steps.json

purr pancake remove-liquidity \
  --pair-address <lp-token-address> \
  --token0 <token0> \
  --token1 <token1> \
  --lp-amount-wei <lp-amount-wei> \
  --wallet <ows-evm-address> \
  --deadline <unix-or-relative-seconds> \
  --chain-id 56 \
  > /tmp/pancake-steps.json
```

## Farms And Syrup Pools

```bash
purr pancake stake \
  --pid <pid> \
  --amount-wei <lp-amount-wei> \
  --lp-token <lp-token-address> \
  --chain-id 56 \
  > /tmp/pancake-steps.json

purr pancake unstake \
  --pid <pid> \
  --amount-wei <lp-amount-wei> \
  --lp-token <lp-token-address> \
  --chain-id 56 \
  > /tmp/pancake-steps.json

purr pancake harvest \
  --pid <pid> \
  --lp-token <lp-token-address> \
  --chain-id 56 \
  > /tmp/pancake-steps.json

purr pancake syrup-stake \
  --pool-address <pool-address> \
  --amount-wei <cake-amount-wei> \
  --chain-id 56 \
  > /tmp/pancake-steps.json

purr pancake syrup-unstake \
  --pool-address <pool-address> \
  --amount-wei <cake-amount-wei> \
  --chain-id 56 \
  > /tmp/pancake-steps.json
```

## V3 Position And Farm

Use the same build-then-OWS-execute pattern for `v3-mint`, `v3-increase`,
`v3-decrease`, `v3-collect`, `v3-stake`, `v3-unstake`, and `v3-harvest`.
Always include `--chain-id 56`; include `--wallet <ows-evm-address>` when the
subcommand requires it.

Do not add `--execute` to `purr pancake` in OWS flows.

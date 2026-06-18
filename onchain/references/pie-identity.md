# Pie Identity / PNS Lookups

Use Pie identity lookup to resolve a `.pie` handle, find the Pie identity paired
to a Telegram account, inspect linked accounts, or read a public profile.

## Workflow

1. If the user gives a `.pie` handle, use `resolve`, `accounts`, or `profile`.
2. If the user gives a Telegram account, use `by-account`.
3. Return the resolved Pie identity, wallet address, account list, or profile
   data.

## Syntax

```bash
purr pns resolve <handle>.pie
purr pns by-account --channel telegram --account <telegram_username>
purr pns accounts <handle>.pie
purr pns profile <handle>.pie
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `<handle>.pie` | Required for `resolve`, `accounts`, and `profile` | The Pie handle to resolve or inspect. |
| `--channel telegram` | Required for `by-account` | Selects Telegram account lookup. |
| `--account <telegram_username>` | Required for `by-account` | The Telegram username to look up, with or without `@`. |

## Commands

```bash
purr pns by-account --channel telegram --account <telegram_username> # Pie identity paired to a Telegram username
purr pns accounts <handle>.pie                                       # linked accounts for a Pie handle
purr pns profile <handle>.pie                                        # public profile for a Pie handle
purr pns resolve <handle>.pie                                        # wallet address for a Pie handle
```

## Response Shape

`resolve` prints only the resolved wallet address:

```text
0x1234567890123456789012345678901234567890
```

`by-account` prints only the paired Pie name when one is found:

```text
alice.pie
```

If no Pie name is paired to the account, stdout is empty.

`accounts` prints JSON:

```json
{
  "accounts": [
    {
      "channel": "telegram",
      "accountId": "123456789",
      "username": "alice"
    }
  ]
}
```

`profile` prints JSON:

```json
{
  "pieName": "alice.pie",
  "agentType": "remote",
  "walletAddress": "0x1234567890123456789012345678901234567890",
  "merchant": {
    "enabled": false,
    "useUpstreamSkill": false,
    "agentCard": null,
    "agentCardStatus": "not_enabled"
  }
}
```

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `handle_reserved` / `Handle <handle>.pie is reserved` | The handle is reserved. |
| `handle_reservation_expired` | The handle reservation expired. |
| `invalid_handle` / `Handle is unavailable` | The handle is blocked by handle policy. |
| `PNS handle not found: <handle>` or `Handle not found` | No active Pie identity exists for that handle. |
| `PNS handle is not claimable yet: <handle>` or `Handle claim is still in progress` | The handle is in a transient claim state. |
| `Invalid PNS handle: <handle> (...)` or `invalid_handle` | The handle format or lookup input is invalid. |
| `invalid_channel` | The account lookup channel is unsupported. |
| `telegram_account_resolution_unavailable` | Telegram account lookup is temporarily unavailable. |

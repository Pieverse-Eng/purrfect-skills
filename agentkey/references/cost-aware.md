# Cost-aware batch execution

Load this when the user's request implies three or more AgentKey calls or 10 or
more estimated credits. The goal is to avoid spending the user's AgentKey
credits silently.

## Pre-batch Workflow

```text
agentkey_account()
describe_tool(name=<target>)
estimate total = credits_per_call * number_of_calls
confirm with user
execute
```

Skip this workflow only when all are true:

- The request is a single call.
- The single call costs no more than 1 credit.
- The user explicitly asked you to proceed without asking.

## Reading Cost

Use the `cost` field returned by `describe_tool`.

Common shapes:

- `credits_per_call` plus `cost_by_provider`: multiply by call count. Prefer a
  cheaper provider when it still satisfies the task.
- `billing_note` only: cost is path-dependent. Call `describe_tool` on the exact
  endpoint path before estimating.
- `free: true`: use freely for discovery and account checks.

Failed validation or upstream-error calls are normally not billed when the tool's
`billing_note` says charges apply only on successful responses.

## Confirmation Message

Before execution, tell the user:

```text
I'm about to run <endpoint> <N> times.
Estimated cost: <X> credits.
Current balance: <balance> credits.
Should I proceed?
```

Wait for explicit approval. If balance cannot be checked, do not run a batch
silently; tell the user you could not verify balance and ask whether to proceed.

If estimated cost exceeds balance, do not start. Tell the user how many calls fit
and ask whether to run that subset, stop, or top up at
`https://console.agentkey.app/`.

## Cost-saving Moves

- Use the cheapest provider that satisfies the task.
- Probe one call first for unfamiliar endpoints.
- Deduplicate repeated inputs.
- Reuse in-session results for identical requests.
- Ask for a smaller result count when the request is open-ended or huge.

## After Execution

Tell the user how many calls ran and the estimated or reported credit usage. Do
not call `agentkey_account` again unless the user asks or the batch was large.

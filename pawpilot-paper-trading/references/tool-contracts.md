# Host tool and publication contracts

These are shapes, not default trades. Replace every identity, amount, version
and policy with the current verified facts and the user's explicit choices.

Read facts with `paper_read({"operation":"account"})`, `market`, `orders` or
`positions`. `notes` reads plans and enabled confirmed Lessons. `receipt`
accepts the original actionId; after an unknown preparation use the original
callId to recover that call's action, without preparing again.

An explicitly chosen notional limit order has this shape:

```json
{
  "kind": "place_order",
  "marketKey": "<verified native marketKey>",
  "side": "buy",
  "type": "limit",
  "price": "<user's limit price>",
  "sizing": {"kind": "quote_notional", "amount": "100", "asset": "<verified quote asset>"}
}
```

Pass explicit leverage/margin mode in `risk` when requested. Do not add leverage
to spot, silently convert a notional amount to collateral, or invent an expiry.
Native quantities use `sizing.kind=base_quantity`; collateral budgets use
`margin_budget` and require both explicit leverage and marginMode. Risk and
fees are the host's preview, not arithmetic performed by the Agent.

Management actions keep changed parameters inside `request`:

- Amend: `kind=amend_order`, orderId, request.expectedVersion, and the user's
  explicit request.quantity/request.price changes.
- Cancel: `kind=cancel_order`, orderId, request.expectedVersion.
- Batch cancel: `kind=cancel_all`, request.accountIds containing only the bound
  account, and request.marketKey for the explicit selected scope.
- Protection: `kind=position_protection`, positionId, request.expectedVersion;
  both request.stopLoss and request.takeProfit are required. This replaces the
  whole protection configuration. Each leg is either explicit null or includes
  triggerPrice, supported execution, and a price only for limit execution. To
  preserve the other leg, copy its verified supported parameters; use null only
  when it is absent or the user explicitly requests removal. Never omit a leg
  or silently clear protection. Read and clarify before preparation.
- Simulated deposit: `kind=claim`. There is no invented allocation amount.
- Transfer: `kind=transfer`, request.fromAccountId/request.toAccountId in this
  owned portfolio, request.asset and request.amount. Verify both destinations;
  one side must be the bound account. Never substitute a Live transfer.

A ready result contains `data.action`, `data.message` and `data.metadata`.
Publish with the native current-conversation message tool:

```text
send_message(target="current",
             message=result.data.message.text,
             reply_markup=result.data.message.reply_markup,
             metadata=result.data.metadata)
```

Copy the prepared message and metadata together. Missing preparedActions,
altered callback references or an action from another Run cannot produce a
valid review button. `preview` is advisory evidence; the web review obtains a
fresh preview and requires a separate human confirmation. A non-ready result
must not be rendered as a successful order or an executable invented button.

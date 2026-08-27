# Eval corpus JSON schema

A corpus is a JSON file with a `prompts` array. Each prompt is one agent turn we want to score. Keep it small and varied — 20–30 prompts is plenty for a first pass.

## Top-level shape

```json
{
  "schema_version": 1,
  "instance": "<UUID of the tenant instance the corpus is calibrated against>",
  "shop_name": "<the merchant name (or generic role) the agent is supposed to be>",
  "seeded_state_summary": { /* optional, free-form: lets future-you remember what was seeded */ },
  "prompts": [ /* see below */ ]
}
```

`schema_version`, `instance`, `shop_name`, `seeded_state_summary` are documentation; only `prompts` is consumed by the runner/analyzer.

## Prompt shape

```json
{
  "id":            "A1_product_list",
  "category":      "product_catalog",
  "prompt":        "我们店里有哪些产品在卖？请列出来，包含价格。",
  "expects_tool":  ["purrfect_product_list", "exec:product list"],
  "must_contain":  ["经典珍珠奶茶", "抹茶拿铁", "3.5", "5"],
  "must_not_contain": ["我没有店", "I don't have a store"]
}
```

Field semantics:

- **`id`** (required, unique). Used as filename root and in reports. Convention: `<category-letter><index>_<slug>` (`A1_product_list`, `B2_sales_week`, `G2_off_skill_code`).
- **`category`** (required). Free-form bucket; the analyzer groups stats by category. Suggested categories for the merchant skill:
  - `product_catalog` — read-only product queries
  - `product_mutation` — add/update/remove products
  - `sales_report` — sales_today, sales_week, sales_summary
  - `customer` — customer_list, customer_get
  - `order_query` — order_list, order_get
  - `order_mutation` — order_create, order_cancel
  - `loyalty` — coupon_list, reward_list/add
  - `reconciliation` — failed_settlements, event_cursor_status
  - `off_skill` — off-topic (must NOT trigger merchant tools)
  - `ambiguous` — could go either way (e.g. "我们生意怎么样" — IDENTITY says merchant)
- **`prompt`** (required). The exact user message sent to `openclaw agent --message`. Single string, no role wrapping.
- **`expects_tool`** (optional). Array of tool-match patterns. Modes:
  - `"purrfect_X"` — match any tool whose name equals `purrfect_X` or ends with `__purrfect_X` (the gateway prefixes MCP tools with their server slug).
  - `"kind:pattern"` — match a tool by `kind` (e.g. `exec`, `read`) where `pattern` appears in the input. Useful for fallback paths.
  - `"!X"` — **forbidden**. If any tool matches, the prompt fails with `tool_status: violation`. Use for off-skill prompts (e.g. `"!purrfect_"` forbids any merchant MCP call).
  - Empty array `[]` — off-skill default; any non-merchant activity is fine.
- **`must_contain`** (optional). Array of substrings the response MUST include (case-insensitive). Score = `matched / total`. Score 100% → `text_match` is full.
- **`must_not_contain`** (optional). Array of substrings the response MUST NOT include. Any match → `❌ FAIL (violation)`.

## Authoring tips

- **Pin specific values, not vibes.** "包含价格" (contain prices) is hard to score; `["3.5", "5", "4.5", "2.5"]` is precise. Combine with the seed so the values are deterministic.
- **Don't over-pin.** If you list every detail in `must_contain`, agents that summarize correctly but reorder/rephrase fail. ~3–5 substrings per prompt is the sweet spot.
- **Keep off-skill prompts narrow.** "Tell me about React hooks" is too open-ended — every model answers differently. Pick something with a stable answer surface ("write a python fibonacci function" → `must_contain: ["def"]`).
- **Use `must_not_contain` for the WORST failure.** For the merchant eval, "I don't have a store" is the symptom of Finding #1; pinning it as `must_not_contain` catches identity regressions cheaply.
- **One concrete entity per prompt.** "Lookup customer 0xAa..." with the actual seeded wallet address makes the answer scoreable. "Lookup my best customer" relies on the agent picking the right one; ambiguity inflates noise.

## Example: 22-prompt merchant corpus

See the eval-agent-skill repo's `examples/merchant-corpus.json` (or this skill's session log) for a working example covering A–G categories.

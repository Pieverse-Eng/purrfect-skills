# Venue Skill Instructions

## Research ownership

Market discovery, cross-venue cost comparison and split spot plans are
platform tools (`discover_markets`, `compare_trade_routes`,
`plan_spot_purchase`); they return exact market IDs and order precision. The
platform also injects per-turn venue readiness (integration, account, funding
and fee approval). Keep venue execution instructions and venue-specific market
data (books, candles, funding) in the skills; use tool IDs and readiness
instead of re-resolving them, and do not duplicate discovery, comparison or
fee tables.

## Wrapper and vendor skills

When a venue skill is a wrapper/router around vendored skills:

- Every vendored `SKILL.md` behind that wrapper must include both fields in its
  frontmatter:

  ```yaml
  disable-model-invocation: true
  user-invocable: false
  ```

- These fields prevent vendor skills from being selected or invoked as peers of
  the wrapper. The wrapper remains the single discoverable routing entry point.
- Preserve both fields whenever vendored skills are imported or refreshed.

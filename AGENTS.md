# Venue Skill Instructions

## Market-search metadata

A top-level trading-venue `SKILL.md` exposed to the Pod-local Market Search
Agent must declare its discovery and readiness contract under
`metadata.pieverse`:

```yaml
metadata:
  pieverse:
    marketSearch: true
    tradeReady:
      env:
        - [EXCHANGE_API_KEY, EXCHANGE_API_SECRET]
      probe:
        argv: [exchange, auth, status, --json]
        jsonEquals:
          status: logged_in
```

- `marketSearch: true` marks the top-level skill as a venue the Market Search
  Agent may discover.
- `tradeReady.env` is a list of alternative complete credential sets. Every key
  within one set is required; satisfying any complete set makes the env
  condition ready.
- `tradeReady.probe.argv` is a fixed argument list for a local, read-only, fast,
  and deterministic status command. It must not be a shell command string.
- The probe must exit successfully and print one JSON object.
  `tradeReady.probe.jsonEquals` declares the required top-level scalar fields,
  which the runtime compares exactly.
- Env readiness and probe readiness are alternatives (`env OR probe`). A venue
  may declare either one or both.
- Different CLI response formats must be described by that venue skill's
  `jsonEquals`; do not add venue-specific parsing or adapters to Platform.
- `tradeReady.integration` is unsupported. Use a local status probe instead.
- Metadata must never contain credentials, authentication state, or tenant data.
- The skill must document how to query public instruments and verify an exact
  ticker without requiring trading credentials.

## Wrapper and vendor skills

When a venue skill is a wrapper/router around vendored skills:

- Put `metadata.pieverse.marketSearch` and `tradeReady` only on the top-level
  wrapper `SKILL.md`.
- Every vendored `SKILL.md` behind that wrapper must include both fields in its
  frontmatter:

  ```yaml
  disable-model-invocation: true
  user-invocable: false
  ```

- These fields prevent vendor skills from being selected or invoked as peers of
  the wrapper. The wrapper remains the single discoverable routing entry point.
- Preserve both fields whenever vendored skills are imported or refreshed.

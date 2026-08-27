# Repository Instructions

## Skill topology

- Keep one discoverable top-level `SKILL.md` as the router for a venue or domain.
- A nested vendored, reference, recipe, or implementation skill that must only be
  reached through its parent router must declare both fields in its frontmatter:

  ```yaml
  disable-model-invocation: true
  user-invocable: false
  ```

- Do not add those fields to a top-level router unless that router is intentionally
  hidden from both automatic model selection and direct user invocation.
- When importing or refreshing vendored skills, review every nested `SKILL.md` and
  preserve these routing fields. Do not expose vendored skills as independent
  peers of their top-level router.

## Market-search venues

- A top-level trading-venue skill available to the Pod-local Market Search Agent
  must declare `metadata.pieverse.marketSearch: true`.
- Put `marketSearch` and `tradeReady` only on the top-level venue router, never on
  its vendored or reference skills.
- Declare readiness entirely in skill metadata. Adding a venue must not require a
  Platform venue list, per-venue adapter, or venue-specific conditional.
- `tradeReady.env` is a list of alternative credential sets. Every key within one
  set is required; satisfying any complete set makes the env condition ready.
- `tradeReady.probe.argv` must be a fixed YAML argument list for a local,
  read-only, deterministic, and fast command. Never provide a shell command
  string, tenant data, or credentials in metadata.
- A readiness probe must exit successfully and print one JSON object.
  `tradeReady.probe.jsonEquals` declares the required top-level scalar fields;
  the runtime compares them exactly. Different CLI response formats belong in
  that skill's `jsonEquals` declaration, not in Platform code.
- Env readiness and probe readiness are alternatives (`env OR probe`). Probes
  must fail closed. `tradeReady.integration` is unsupported; expose a local
  status probe instead.
- The venue skill must document how the agent queries public instruments and
  verifies an exact ticker without requiring trading credentials.

## Validation

- After changing market-search metadata, run:

  ```bash
  python3 scripts/check-market-search-metadata.py
  ```

- Also run the narrow validation relevant to the skill or vendored bundle that
  changed. Do not commit credentials, authentication state, or tenant-specific
  output.

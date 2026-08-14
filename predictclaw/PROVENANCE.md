# Provenance

`predictclaw/` is a migration of the upstream `predictfunclaw` skill into the
`purrfect-skills` repository, with the mandated-vault MCP transport replaced by a
one-shot `@erc-mandated/sdk` Node helper and the default signer path moved to the
instance-scoped Pieverse platform wallet API.

- Upstream repository: `tabilabs/predictfunclaw`
- Upstream source commit: `9e4e8b4f75694ae7d2b015a1da445bad3ca39e09`
- License: CC0 (upstream `LICENSE` retained as `predictclaw/LICENSE`)

Migration changes are the PredictClaw-specific work in this directory; upstream
logic and structure are preserved where compatible.

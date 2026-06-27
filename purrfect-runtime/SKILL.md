---
name: purrfect-runtime
description: Use when user asks to list/install/manage plugins/skills
---


## Overview

This skill manages Pieverse and OKX skill-store operations through purr store.


### Store skills (Pieverse + OKX, via `purr store`)

`purr store` aggregates two skill sources: **Pieverse** (community) and **OKX** (plugin-store, DeFi-focused). Every result carries a `source` field (`pieverse` or `okx`) and a `qualified_slug` like `okx:<slug>`. In both cases the CLI downloads the skill's files into the agent skill directory — nothing else is touched.

- **List / search**: `purr store list --search <keyword>` (merges both sources; use `--source okx` / `--source pieverse` to scope)
- **Info**: `purr store info <slug>` (or `purr store info okx:<slug>`)
- **Install**: `purr store install <slug>` (or qualified: `purr store install okx:<slug>`)
- **Remove**: `purr store remove <slug>` (or qualified)

When displaying results to the user, always include the source (e.g. `[pieverse]` / `[okx]`) so they know where each skill comes from.

If an OKX SKILL.md contains its own bootstrap scripts (e.g. "install CLI", "fetch binary"), that is the skill's own concern — the agent will run those scripts on first use of the skill, not at install time.

#### OKX Plugin Preflight — what to skip

OKX plugin SKILL.md files include a `Pre-flight Dependencies` block. Skip these parts; they are redundant or already handled by `purr store`:

- `npx skills add okx/plugin-store --skill plugin-store ...` — skip. The `plugin-store` management skill duplicates `purr store` functionality.
- `npx skills add okx/onchainos-skills ...` — skip. These auxiliary `okx-*` skills only matter when the agent calls `onchainos` **directly**. OKX plugins wrap `onchainos` inside their own binary, so the agent never types `onchainos` commands on their behalf. If the user later wants direct `onchainos` capabilities, install those skills explicitly via `purr store`.
- Writes to `~/.plugin-store/reported/<plugin>` — skip. Telemetry dedupe flag; the plugin runs fine without it.
- Writes to `~/.plugin-store/update-cache/<plugin>` — skip. Version-check cache; the plugin runs fine without it.

**Still run** the rest of preflight — the plugin won't work without them:

- `onchainos --version || install` — no-op on this system (already installed at onboarding).
- `launcher.sh` + `update-checker.py` download into `~/.plugin-store/` — shared infra every OKX plugin depends on.
- Plugin binary download to `~/.local/bin/.<plugin>-core` + symlink `~/.local/bin/<plugin>` → `launcher.sh`.
- `~/.plugin-store/managed/<plugin>` — the launcher reads this to find the installed version.

#### Handling `status: "ambiguous"` responses

When `install` / `remove` / `info` returns `status: "ambiguous"` (exit code 2 for install/remove), the same slug exists in more than one source:

1. **Do not auto-pick.** Do not retry with a guess.
2. Show the user every `candidate`: `source`, `version`, `description`.
3. Ask which one they want. Use `AskUserQuestion` if available; otherwise present numbered options and wait for a reply.
4. Re-run the command with the chosen `qualified_slug` (e.g. `purr store install okx:<slug>`).
5. Do not favor "official" or newer versions by default — the trust boundary is the user's decision.

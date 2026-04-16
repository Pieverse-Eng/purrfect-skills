---
name: purrfect-runtime
description: "PurrfectClaw setup and skill store. Use ONLY when: (1) user explicitly asks to set up or configure PurrfectClaw, (2) user asks to list, install, or manage plugins/skills. Do NOT use for wallet, balance, swap, trade, or any DeFi operation queries."
---

# PurrfectClaw Plugin Store

**IMPORTANT**: If PurrfectClaw is not configured, run onboarding automatically. Do not ask for permission — just begin.

## Pre-flight Check

```bash
CONFIGURED=false
if [ -f ~/.purrfectclaw/.env ]; then
  source ~/.purrfectclaw/.env
  if [ -n "${WALLET_ADDRESS:-}" ] && (command -v purr &>/dev/null || [ -x ~/.purrfectclaw/bin/purr ]); then
    CONFIGURED=true
  fi
fi
echo "CONFIGURED=$CONFIGURED WALLET=${WALLET_ADDRESS:-unset}"
```

- If `CONFIGURED=false`, run **Onboarding** below immediately.
- If `CONFIGURED=true`, proceed to the user's request or `purr store` commands.

---

## Onboarding

Read and follow the onboarding guide at [references/agent-onboard.md](references/agent-onboard.md).

Follow every step in that file, with two changes:

**Step 2 (Download skills)** — Replace the skill bundle download with:

You know which agent you are (Claude Code, Codex, Cursor, Windsurf, etc.). Pick the matching slug from the table below and install only to that agent — do NOT install to all agents.

| Agent you are  | Slug                                                   |
| -------------- | ------------------------------------------------------ |
| Claude Code    | `claude-code`                                          |
| Codex          | `codex`                                                |
| Cursor         | `cursor`                                               |
| Windsurf       | `windsurf`                                             |
| OpenClaw       | `openclaw`                                             |
| Gemini CLI     | `gemini-cli`                                           |
| GitHub Copilot | `github-copilot`                                       |
| Amp            | `amp`                                                  |
| Cline          | `cline`                                                |
| OpenCode       | `opencode`                                             |
| Other          | see https://www.npmjs.com/package/skills for full list |

```bash
AGENT="<slug from table above>"
if [ -f "$PURRFECT_SKILLS_DIR/onchain/SKILL.md" ] 2>/dev/null; then
  echo "Built-in skills already present — skipping."
else
  npx skills add Pieverse-Eng/cc-purrfect-runtime --skill "*" --agent "$AGENT" -y
fi
```

**After Step 4 (Verify)** — the `purr` CLI now includes built-in `purr store` commands for managing skills from the Pieverse Skill Store and OKX Plugin Store. Make sure `purr` is available (if not, revisit the `purr` CLI installation step in `agent-onboard.md`). If `purr` is available but `purr store` is missing, install the latest `purr-cli` from source as a fallback:

```bash
if ! command -v purr >/dev/null 2>&1; then
  echo "purr CLI not found. Please re-run the purr CLI installation step from agent-onboard.md."
  exit 1
fi
if ! purr store list --limit 1 >/dev/null 2>&1; then
  echo "purr store not available in current purr binary. Installing purr-cli from source..."
  PURR_CLI_SRC="$HOME/.purrfectclaw/purr-cli-src"
  rm -rf "$PURR_CLI_SRC"
  git clone --depth 1 https://github.com/Pieverse-Eng/purr-cli.git "$PURR_CLI_SRC"
  (cd "$PURR_CLI_SRC" && npm install && npm run build)
  mkdir -p ~/.purrfectclaw/bin
  ln -sf "$PURR_CLI_SRC/dist/main.js" ~/.purrfectclaw/bin/purr
  chmod +x ~/.purrfectclaw/bin/purr
fi
purr store list --limit 1
```

Also install the `onchainos` CLI — it is the runtime signer / broadcaster that every OKX plugin calls. Installing it upfront lets OKX plugins installed via `purr store` run immediately without a first-use bootstrap delay:

```bash
if ! command -v onchainos >/dev/null 2>&1; then
  LATEST_TAG=$(curl -sSL "https://api.github.com/repos/okx/onchainos-skills/releases/latest" \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['tag_name'])")
  curl -sSL "https://raw.githubusercontent.com/okx/onchainos-skills/${LATEST_TAG}/install.sh" | sh
fi
```

Verify:

```bash
onchainos --version
# Expected: prints version (e.g. onchainos 2.2.9)
```

All other steps — follow as written in `agent-onboard.md`.

**After onboarding completes** — newly installed skills are not picked up by the current session automatically. Tell the user to reload their agent so the new skills appear in the skill registry. Remind them to do the same after any future `purr store install` / `purr store remove` call.

---

## Skill Management

After onboarding, this skill handles two kinds of skill management:

### Local skills (already installed in `$PURRFECT_SKILLS_DIR`)

- **List installed skills**: scan skill directories, read each `SKILL.md` frontmatter (name + description), and check the Pre-flight Checks section for dependency status
- **Search installed**: filter installed skills by keyword in name/description

### Store skills (Pieverse + OKX, via `purr store`)

`purr store` aggregates two skill sources: **Pieverse** (community) and **OKX** (plugin-store, DeFi-focused). Every result carries a `source` field (`pieverse` or `okx`) and a `qualified_slug` like `okx:<slug>`. In both cases the CLI downloads the skill's files into the agent skill directory — nothing else is touched.

- **List / search**: `purr store list --search <keyword>` (merges both sources; use `--source okx` / `--source pieverse` to scope)
- **Info**: `purr store info <slug>` (or `purr store info okx:<slug>`)
- **Install**: `purr store install <slug>` (or qualified: `purr store install okx:<slug>`)
- **Remove**: `purr store remove <slug>` (or qualified)

When displaying results to the user, always include the source (e.g. `[pieverse]` / `[okx]`) so they know where each skill comes from.

If an OKX SKILL.md contains its own bootstrap scripts (e.g. "install CLI", "fetch binary"), that is the skill's own concern — the agent will run those scripts on first use of the skill, not at install time.

#### OKX Plugin Preflight — what to skip

OKX plugin SKILL.md files include a `Pre-flight Dependencies` block. When running it on a system set up through this onboarding, **skip these parts** — they are redundant or already handled by `purr store`:

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

---
name: eval-agent-skill
description: |
  End-to-end methodology to dogfood an agent skill against a live tenant instance — diagnose
  whether the skill is actually loaded, seed realistic data, drive a curated prompt corpus
  through the agent, score tool-use + content correctness, find regressions, and iterate.
  Designed for the Pieverse / OpenClaw / Hermes platform but the methodology generalizes.

  Triggers: "eval this skill", "test the skill on an instance", "dogfood the merchant skill",
  "build an eval framework", "see if the agent actually uses purrfect_*", "run regression
  test on the skill", "compare model adaptation", "diagnose why the agent isn't using my
  skill", "is my skill loaded into the pod", "kubectl debug skill loading", "openclaw agent
  --json eval".
---

# Agent Skill Eval — Methodology

## When to use this skill

Invoke when the user wants to:

- Confirm a skill is **actually loaded** into a running tenant instance (workspace + MCP server + identity), not just deployed in the image
- Drive **real traffic** (a curated prompt corpus) through the agent and measure how well it uses the skill's tools
- **Diagnose regressions** — the agent gives wrong answers / aborts / falls back to shell
- **Compare models** for skill adaptation (e.g. kimi-k2.5 vs gpt-4o vs claude-sonnet-4)
- **Iterate fixes** — hot-patch the pod, re-run eval, compare to baseline

Skip if the user just wants to run the skill's existing unit / integration tests — those live inside the skill repo and don't exercise the agent loop.

## The 8 phases (run them in order; each gates the next)

For each phase below, the file under `references/` has the detailed checklist + commands. The summary is here so the agent knows the shape of the work.

### Phase 1 — Verify the skill is actually loaded
The single most common failure mode: skill files are deployed in the container image but **not wired into the running agent**. Check four things:

1. Workspace install — `ls /root/.openclaw/workspace/skills/<slug>/SKILL.md` (OpenClaw) or `/opt/data/skills/<slug>/SKILL.md` (Hermes).
2. MCP server registration — `python3 -c "import json; print(json.load(open('/root/.openclaw/openclaw.json'))['mcp']['servers'])"`. Skill's MCP slug must appear here.
3. MCP child process — `ps aux | grep mcp.js`. After the gateway boots, this should show a node process for the skill's `src/mcp.js`.
4. Agent identity overlay — `cat /root/.openclaw/workspace/IDENTITY.md`. If empty/template, the agent will not recognize itself as the skill's role.

If any check fails, that's the eval's first finding. See `references/pod-diagnostics.md` for the full diagnostic flow.

### Phase 2 — Seed realistic in-pod state
The agent answers about data in the pod's local store (SQLite, files, etc.). Skills typically don't ship a backfill CLI, so combine:
- Skill CLI (`node src/index.js …`) for first-class operations (products, reward rules)
- Direct SQL inserts for tables the CLI doesn't expose (failed_settlements, customer/payment history)

Aim for variety: multiple customers with different stats, mixed-status orders, reward rules near + past their thresholds, at least one failure case. See `scripts/seed-merchant.mjs` for the merchant-skill template.

### Phase 3 — Build the prompt corpus
Curated > captured for the first eval pass. ~20–30 prompts grouped by skill capability. Each item: `{id, category, prompt, expects_tool, must_contain, must_not_contain}`. Always include 2–3 OFF-SKILL prompts ("write fibonacci", "今天天气") to catch over-eager skill activation. See `references/eval-corpus-schema.md`.

### Phase 4 — Run the eval
`scripts/eval-runner.sh <out_dir> [model_id]` loops the corpus and for each prompt:
- generates a fresh UUID session id (so prompts don't share context)
- `kubectl exec … openclaw agent --session-id <UUID> --message <PROMPT> --json` (with `--model <id>` if cross-model run)
- `kubectl cp` the response JSON + the session JSONL out to the local run dir

Run baseline first, then any post-fix runs. **Save the run dir per attempt** so `eval-analyze.py` can diff them.

### Phase 5 — Analyze
`scripts/eval-analyze.py <run_dir>` parses each prompt's response + session, scores against the rubric:
- **tool_status:** match (used the expected tool), partial (used something), none (no tool calls), violation (used a forbidden tool, e.g. merchant tool on an off-skill prompt)
- **text_match_ratio:** how many `must_contain` substrings landed
- **violations:** any `must_not_contain` substrings that landed
- **agent_aborted:** "couldn't generate a response" or other openclaw error markers
- **preamble_only:** agent said "let me check" / "我需要先" with <100 output tokens (Finding #7 pattern)

Verdict per prompt: PASS / PASS (fallback) / 🟡 PARTIAL / ❌ FAIL (abort/preamble/violation/no content).

### Phase 6 — Diagnose failures
For each ❌, pull the session JSONL and walk the toolCall sequence:
- 0 tool calls + a real answer → agent fabricated; check whether identity/SKILL.md gave it enough context to confabulate
- exec/read/find chain → fallback path (skill MCP not wired up correctly — Finding #2 pattern)
- correct MCP tool but wrong/empty answer → data not seeded, OR the skill's tool returned wrong shape

`scripts/inspect-session.py` pretty-prints the toolCalls for a single session. The gateway log (`/tmp/openclaw/gateway.log`) is also useful — `grep "bundle-mcp"` for MCP spawn errors.

### Phase 7 — Hot-patch and re-eval
Most fixes need only a `kubectl cp` + a SIGUSR1 to re-test, not a full image rebuild:
- Identity / SKILL.md edits → `kubectl cp` to `/root/.openclaw/workspace/...`
- MCP registration changes → `kubectl exec … python3 -c "import json; ..."` to patch `/root/.openclaw/openclaw.json` then `kill -USR1 $(pgrep openclaw-gateway)`
- Skill code (mcp.js, etc.) → `kubectl cp` to BOTH `/app/upstream-merchant-skill/` AND the workspace copy, then SIGUSR1

CAUTION: pod restarts (manual delete OR k8s ScaleDown) wipe hot-patches. If the test runs long, either bump the submodule + rebuild the image, or accept that you may need to re-apply patches between runs. After every restart, re-verify Phase 1 before re-running the eval.

### Phase 8 — Document findings + open PRs
Use `references/findings-template.md`. Each finding gets: severity, symptom, root cause, suggested fix (skill-side / platform-side / both). Then split fixes into PRs with explicit cross-references — never let "everything in one giant PR" hide the eval-driven reasoning.

## Operational notes

- **Cost control.** A single prompt costs ~30k–150k input tokens depending on session bootstrap. 22 prompts = ~3M tokens per run. Don't run the full corpus on every iteration — pick 3–5 high-signal prompts as smoke before the full run. The runner takes a `--smoke` flag for this.
- **Determinism.** Force a fresh `--session-id` per prompt or context leaks. `--to <E.164>` does NOT isolate sessions — it derives `agent:main:main` regardless. (Confirmed Finding #3 in the May 2026 eval.)
- **CLI output gotcha.** `result.payloads` is a list — read **all** items, not just `[0]`. The first item is often a "let me check 👇" preamble; the actual answer is in a later item. (Finding #4.)
- **Pod restarts wipe state.** GCS backup + restore covers the workspace but `start-openclaw.sh` re-copies the bundled skill from `/app/upstream-merchant-skill/` over the workspace on every boot, so any in-workspace skill code edits are lost. ConfigMap is regenerated by the operator from instance.config, so any direct patches there are lost too. For durable changes: bump the submodule + rebuild the tenant image, and patch instance.config in the platform DB.
- **MCP child crash on cwd.** A common skill bug: `src/mcp.js` resolves the SQLite path via `process.cwd()`. openclaw spawns MCP children with `cwd=/`, so `data/...` becomes `/data/...` and the child crashes at boot. Skill fix: use `dirname(fileURLToPath(import.meta.url))`. Platform workaround: pass `MERCHANT_DB` (or equivalent) as an absolute env in the openclaw.json mcp.servers entry.

## What this skill does NOT do

- Replace the skill's own unit/integration tests (those run in CI on the skill repo).
- Build a continuous-integration eval pipeline (this is a manual / interactive flow; CI integration is a follow-up if pass rates stabilize).
- Capture / replay real production traffic. The corpus is curated. Production capture is a future option.
- Cross-tenant comparisons. One instance per run; cross-tenant analysis is out of scope.

## See also

- `scripts/eval-runner.sh` — corpus loop + kubectl driver
- `scripts/eval-analyze.py` — scoring + report generator
- `scripts/inspect-session.py` — session JSONL pretty-printer
- `scripts/seed-merchant.mjs` — example seed script (merchant-skill specific)
- `references/eval-corpus-schema.md` — corpus JSON format + categories + examples
- `references/pod-diagnostics.md` — Phase 1 checklist with exact commands
- `references/findings-template.md` — Phase 8 doc structure

# Findings doc template

Drop this into `docs/plans/YYYY-MM-DD-<skill>-eval-findings.md` in the project repo. The doc grows with each eval pass — append, never rewrite — so future reviewers can see the order of discovery.

## Structure

```markdown
# <Skill> Eval — Findings (Living Document)

**Date started:** YYYY-MM-DD
**Skill under test:** `<repo-name>` @ HEAD `<sha>`
**Test instance:** `<UUID>` (openclaw|hermes runtime)
**Default model:** `<provider/model>`
**Method:** Curated <N>-prompt corpus, replayed via `openclaw agent --session-id <uuid>` with rubric scoring.

## Setup history

(Just enough breadcrumbs that the next person can reconstruct the path. List the diagnostic discoveries you made, the workarounds you applied, and the manual steps that should not have been manual.)

1. Diagnose <X> — finding: <Y>. Workaround: <Z>.
2. ...

**Time to first usable eval state:** ~XX minutes of per-instance hands-on. (None of these manual steps should be required for a real onboarding.)

## Findings

### Finding #N — <one-line title>
**Severity:** <Low | Medium | Med-High | High>
**Symptom:** <what the user / agent observes>
**Root cause:** <where the bug lives, with file:line and a short explanation>
**Suggested fix (skill-side):** <short — only fill in if this is the right home for the fix>
**Suggested fix (platform-side):** <short — only if this belongs on the platform>
**Status:** <open | manually-patched | merged in PR #N>
**Evidence:** <one-paragraph quote from the eval report or a link to the run dir>

(Repeat per finding. Number them in order of discovery, not severity.)

## Eval results

### Run summary

| run | corpus | model | PASS | PARTIAL | FAIL | avg dur | avg in-tok |
|---|---|---|---|---|---|---|---|
| baseline | merchant-22 | kimi-k2.5 | 14 | 8 | 0 | 78s | 155k |
| <fix run name> | merchant-22 | kimi-k2.5 | <...> | <...> | <...> | <...> | <...> |

### Per-prompt regression / improvement table

(Auto-generate via `eval-analyze.py <run_a> <run_b>` — paste its DIFF section here.)

## Out of scope here / followups

- Items that came up but aren't this PR's job. Each one needs an owner and a cadence.
- Skill PRs that need to land first.
- Cross-model matrix work to do once the single-model pass rate is healthy.
```

## Findings severity guide

- **High** — agent gives a confidently wrong answer, aborts mid-turn, or otherwise breaks the user's trust. Block on this before the skill is recommended for new tenants.
- **Med-High** — functional but very expensive (50s + 140k tokens for what should be 2s + 2k). Real users will notice.
- **Medium** — rough edge that bites in specific situations (e.g. a partial regression, a missing tool that forces shell fallback, brittle path resolution).
- **Low** — eval-tooling concerns, doc nits, things that are slightly wrong but not user-visible.

## Authoring tips

- **Lead with the symptom, not the cause.** "Agent answers '我没有实体店'" is easier to grep for in 6 months than "IDENTITY.md is the workspace template."
- **Pin the file:line for the root cause.** If the bug is in `src/mcp.js:46`, write that. Future-you reading this without the codebase open will thank you.
- **Mark fixes as separate items.** Don't let "Finding #1: identity → fix in PR #402, also we should add reconcile MCP" double up. Each finding gets one PR; cross-reference them.
- **Don't delete findings, mark them resolved.** The history is the value.

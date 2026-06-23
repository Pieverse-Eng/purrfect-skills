---
name: panewslab
description: PANews, crypto news, Polymarket boards, publish, Markdown
---

# PANewsLab

## Overview

Use this skill to track crypto narratives, inspect public Polymarket smart money boards, publish faster on PANews, and turn PANews pages into agent-ready Markdown.

Always read the relevant vendor `SKILL.md` before running commands. Vendor instructions contain the current command list, workflow references, session requirements, and output rules.

## PANews Workflows

| Skill | What it does | Use when | Path |
|---|---|---|---|
| `panews` | Crypto and blockchain news discovery, briefings, and public smart money leaderboard reads. | You need PANews coverage about crypto news, projects, market narratives, rankings, events, calendars, or the latest public smart money board snapshots. | [`vendor/panews/SKILL.md`](vendor/panews/SKILL.md) |
| `panews-creator` | Write, manage, and publish PANews articles with authenticated creator tools for sessions, drafts, submissions, image uploads, tag search, and columns. | You need authenticated PANews creator operations that require `PA-User-Session`. | [`vendor/panews-creator/SKILL.md`](vendor/panews-creator/SKILL.md) |
| `panews-web-viewer` | Read PANews homepage, article, and column pages as Markdown with page metadata. | You need the rendered PANews page itself as Markdown rather than structured API-style content. | [`vendor/panews-web-viewer/SKILL.md`](vendor/panews-web-viewer/SKILL.md) |

## Rules

- Do not predict price movements or give investment advice.
- Keep news answers grounded in PANews coverage; say coverage is weak or missing instead of filling gaps with outside information.
- Treat Polymarket smart money boards as read-only public leaderboard data, not editorial article coverage.
- If a PANews or Polymarket-board request mixes factual lookup with prediction or buy/sell guidance, use the relevant vendor lookup for factual background first, then refuse only the unsupported prediction or advice. Do not extrapolate board rankings into future returns.
- For creator operations, validate `PA-User-Session` before authenticated actions and stop on 401 so the user can refresh the session.
- Require explicit confirmation before deleting creator content or submitting a draft for review.
- Match `--lang` to the user's question language when the selected vendor command supports it. Polymarket board endpoints may not localize; translate or summarize returned fields if needed.

## Ambiguity

- If the user provides a PANews URL and asks for structured fields, search, article content, or an explanation, use `vendor/panews`.
- If the user explicitly asks for Markdown, rendered page content, frontmatter metadata, or the page as displayed on the website, use `vendor/panews-web-viewer`.
- If the user wants to write, edit, upload, publish, submit, manage drafts, or apply for a column, use `vendor/panews-creator`.
- If a request mentions smart money boards, Polymarket board categories, leaderboard snapshots, board highlights, or comparing boards, use `vendor/panews`.

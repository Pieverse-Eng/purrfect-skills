---
name: panewslab
description: PANewsLab skill bundle — routes to the correct sub-skill for reading crypto news, publishing articles, or viewing rendered PANews web pages.
---

# PANewsLab (News Reading + Creator + Web Viewer)

Router skill for all PANews operations. Dispatch to the appropriate sub-skill based on user intent.

## Sub-Skills

| Sub-skill           | Location                     | Use for                                                                                                         |
| ------------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `panews`            | `panews/SKILL.md`            | Reading news: headlines, search, trending, articles, columns, series, topics, events, calendar, editorial picks |
| `panews-creator`    | `panews-creator/SKILL.md`    | Publishing: create/edit/delete articles, manage drafts, upload images, search tags, apply for a column          |
| `panews-web-viewer` | `panews-web-viewer/SKILL.md` | Rendered page reads: fetch PANews homepage, article pages, or column pages as Markdown                          |

**Always read the relevant sub-skill SKILL.md before executing any commands.**

## Intent Routing

| User intent                                        | Route to            |
| -------------------------------------------------- | ------------------- |
| Today's headlines / what's happening in crypto     | `panews`            |
| Search for coverage about a token or project       | `panews`            |
| Breaking news / latest updates                     | `panews`            |
| Trending / rankings / hot topics                   | `panews`            |
| Read an article by ID                              | `panews`            |
| Browse columns, series, or community topics        | `panews`            |
| Events, conferences, calendar                      | `panews`            |
| Editorial picks / hot searches                     | `panews`            |
| Write / publish / submit an article                | `panews-creator`    |
| Check my drafts / submissions / rejections         | `panews-creator`    |
| Edit or resubmit a rejected article                | `panews-creator`    |
| Upload an image / search tags                      | `panews-creator`    |
| Apply for a column                                 | `panews-creator`    |
| Polish or review article content before publishing | `panews-creator`    |
| Read a PANews URL as Markdown                      | `panews-web-viewer` |
| View the PANews homepage rendered content          | `panews-web-viewer` |
| Open a column page and get rendered content        | `panews-web-viewer` |
| Get the full rendered content of a PANews page     | `panews-web-viewer` |

## General Principles

- Do not predict price movements or give investment advice
- Content strictly from PANews — do not add information PANews has not reported
- For creator operations, session verification is required before any authenticated action
- Match `--lang` to the user's question language when applicable; if omitted, the system locale is auto-detected

## Ambiguity Resolution

- If the user provides a PANews URL without specifying format, route to `panews` (structured API). Only use `panews-web-viewer` if they explicitly ask for Markdown or rendered page content
- If the user wants to write or edit content, use `panews-creator`; for reading content, use `panews`
- When in doubt between reading sub-skills, prefer `panews` (API-based) over `panews-web-viewer` (page scrape)

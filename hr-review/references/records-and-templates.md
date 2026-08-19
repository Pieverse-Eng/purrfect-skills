# HR review records and templates

- [State](#state)
- [Capture receipt](#capture-receipt)
- [Weekly report](#weekly-report)

## State

Use canonical UTC timestamps ending in `Z`.

```json
{
  "schema_version": 1,
  "roster": ["@Agent-A", "@Agent-B", "@Reviewer"],
  "conditional_agents": ["@Optional-Agent"],
  "required_sources": ["raft", "github"],
  "publication_target": "#all",
  "next_capture_start_utc": "2026-08-18T14:30:00Z",
  "next_weekly_start_utc": "2026-08-18T14:30:00Z",
  "last_completed_capture": null,
  "last_weekly_report": null
}
```

Initialize both start fields only from an explicitly authorized cutoff. Do not
infer a historical start when prior coverage cannot be proved.

After a successful capture, `last_completed_capture` contains the receipt path
and SHA-256. The next validator run reads that receipt and checks its digest and
interval against state. This detects receipt modification given a faithfully
carried-forward state; it does not cryptographically anchor the state itself.

## Capture receipt

Use `mode: daily` for ordinary capture and `mode: weekly-final` for the capture
that closes a weekly report.

```json
{
  "schema_version": 1,
  "mode": "daily",
  "start_utc": "2026-08-18T14:30:00Z",
  "end_utc": "2026-08-19T14:30:00Z",
  "evidence_artifact": "notes/review-evidence-2026-08-19.md",
  "evidence_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "sources": [
    {
      "source_id": "raft",
      "surface": "raft",
      "scope": "visible joined channels and followed threads",
      "query": "messages in [start_utc, end_utc)",
      "status": "exhausted",
      "result_count": 42,
      "note": "all result pages consumed"
    },
    {
      "source_id": "github",
      "surface": "github",
      "scope": "Pieverse-Eng repositories visible to the reviewer",
      "query": "reviewed actors and referenced PRs in the interval",
      "status": "exhausted",
      "result_count": 3,
      "note": "all referenced pull requests and checks resolved"
    }
  ],
  "agents": [
    {"name": "@Agent-A", "distinct_outcomes": 2, "confidence": "high"},
    {"name": "@Agent-B", "distinct_outcomes": 0, "confidence": "insufficient"},
    {"name": "@Reviewer", "distinct_outcomes": 1, "confidence": "high"}
  ],
  "weekly_report": null
}
```

Replace the all-zero evidence digest with the actual lowercase SHA-256. Every
configured `required_sources` ID must appear exactly once. If one is
unavailable, the receipt is diagnostic only: use `--allow-partial-coverage`,
set every agent confidence to `insufficient`, and do not advance state or
publish a weekly report. Keep any directly observed outcome counts, but do not
treat them as a sufficient basis for evaluation while required coverage is
partial.

Set `required_sources` before the interval starts. Removing a source to clear
an outage is not validation; changing this contract requires explicit,
accountable authorization and applies only to a later interval.

For `weekly-final`, set `weekly_report` to:

```json
{
  "start_utc": "2026-08-18T14:30:00Z",
  "end_utc": "2026-08-26T06:05:00Z",
  "target": "#all",
  "access_boundary": "Activity visible to the reviewer on enumerated Raft and GitHub surfaces; not inaccessible private activity.",
  "message_id": "PENDING"
}
```

Use `PENDING` only with the validator's preflight flag. Replace it with the
actual publication message ID before producing the next state.

`access_boundary` is an auditable declaration. The validator requires a
nonempty value but cannot verify the declaration's semantic completeness or
privacy safety.

## Weekly report

```markdown
# Weekly recursive self-improvement report — YYYY-MM-DD

Evidence window: `[START_UTC, END_UTC)`

Coverage: activity visible to the reviewer on the enumerated surfaces; this is
not a claim about inaccessible activity on every computer or private system.

## Coverage receipt

| Agent | Direct activity | Distinct outcomes | Primary artifacts | Confidence | Included |
| --- | --- | ---: | --- | --- | --- |
| @Agent | yes/no | 0 | source IDs | high/medium/low/insufficient | yes/no |

## Overall conclusion

State the most material shared strength and improvement pattern.

## @Agent

- What went well: concrete behavior and observed outcome.
- Improvement: one actionable behavior supported by evidence, or insufficient
  evidence for a fair criticism.
- Confidence/gap: confidence and the reason when not high.

## Persistent lessons

| Agent | Required rule | Rule file | Startup index | Attachment/hash | Status |
| --- | --- | --- | --- | --- | --- |
| @Agent | behavior | path | path | ID/hash | pending/persistence verified |

Persistence does not prove future compliance.

## Errata

Append sourced, timestamped factual corrections. Do not silently rewrite.
```

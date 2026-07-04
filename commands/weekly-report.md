---
description: Generate and render the weekly client report via the report-generator skill; schedulable with /loop or /schedule.
argument-hint: "<project>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /weekly-report <project>

Produce this week's client report for **$1** (defaults to the active project — resolve with
`./bin/mkt config show`). Thin workflow: it invokes the **`report-generator`** skill for the
**weekly** period and renders the deck. The reporting methodology and the report spec live in the
skill and `templates/report-weekly/`.

## Steps

1. **Resolve the period.** This week ending **2026-06-23** (the most recent complete week);
   compare against the prior week. Read `client.yml` for `domain`, `ahrefs.project_id`,
   `ahrefs.brand_radar_report_id`, and owned `analytics` ids.

2. **Invoke `report-generator` (period: weekly).** The skill pulls the week's deltas — rank
   movement (`rank-tracker-overview`), organic traffic/value, top movers, GSC clicks/impressions,
   AI SoV (`brand-radar-sov-overview`), and any active workstream progress — then composes a
   `report.yml` sections spec (per `templates/report-weekly/`). Prefer Ahrefs MCP
   (`knowledge/ahrefs-mcp-map.md`); call `doc` before first use; values are USD cents (÷100). Lead
   with what changed vs last week and why; keep it short.

3. **Render the deck.**
   ```bash
   ./bin/mkt doc build --in projects/$1/report.yml --out projects/$1/deliverables/$1-weekly-2026-06-23.pdf --project $1
   ```

4. **Review + report back.** Read the PDF: numbers consistent, charts legible, no artifacts.
   Summarize the week's headline movement and any flag the client should act on.

## Cadence
Run weekly. For automation, schedule with **`/loop`** (`/loop 1w /weekly-report $1`) or the
**`/schedule`** routines (a weekly cron cloud agent). Every number is falsifiable and dated; never
fabricate a metric to fill a slot — show a gap instead.

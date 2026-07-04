---
description: Generate and render the monthly client report via the report-generator skill; schedulable with /loop or /schedule.
argument-hint: "<project>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /monthly-report <project>

Produce the monthly client report for **$1** (defaults to the active project — resolve with
`./bin/mkt config show`). Thin workflow: it invokes the **`report-generator`** skill for the
**monthly** period and renders the deck. The reporting methodology and the report spec live in the
skill and `templates/report-monthly/`.

## Steps

1. **Resolve the period.** The last complete calendar month — **May 2026** (2026-05-01 →
   2026-05-31), as of today 2026-06-23 — compared against the prior month and, where useful,
   the same month last year (YoY). Read `client.yml` for `domain`, `ahrefs.project_id`,
   `ahrefs.brand_radar_report_id`, and owned `analytics` ids.

2. **Invoke `report-generator` (period: monthly).** The monthly view is more strategic than the
   weekly: trend lines (`*-metrics-history`, `gsc-performance-history`, `brand-radar-sov-history`),
   goal pacing against the proposal's KPI targets, top wins and misses, content/links shipped, and
   the next month's focus. Composes a `report.yml` sections spec (per `templates/report-monthly/`).
   Prefer Ahrefs MCP (`knowledge/ahrefs-mcp-map.md`); call `doc` before first use; USD cents (÷100).

3. **Render the deck.**
   ```bash
   ./bin/mkt doc build --in projects/$1/report.yml --out projects/$1/deliverables/$1-monthly-2026-05.pdf --project $1
   ```

4. **Review + report back.** Read the PDF: numbers consistent across sections, trend charts
   legible, page breaks clean. Summarize the month vs target, the wins/misses, and the next focus.

## Cadence
Run monthly. For automation, schedule with **`/loop`** (`/loop 1mo /monthly-report $1`) or the
**`/schedule`** routines (a monthly cron cloud agent). Tie progress to the proposal's KPI targets so
the client sees pacing. Every number is dated and falsifiable; never fabricate to fill a slot.

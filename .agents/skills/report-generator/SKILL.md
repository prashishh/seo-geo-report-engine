---
name: report-generator
description: >
  Produce a branded weekly or monthly client report PDF from live data — headline-KPI
  scorecards, rank movers, traffic/SoV trends, a narrative of what changed, and next actions.
  Use when asked for a "weekly report", "monthly report", "client report", "SEO report",
  "progress report", "send the client an update", or "how did we do this period". Pulls
  period-over-period deltas from Ahrefs MCP + owned data, computes wins/regressions vs the
  prior period, and renders a report.yml through the existing doc renderer (no new tooling).
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# report-generator

Turns a reporting period into a **client-ready report PDF** that reuses the proposal renderer.
A report is just a sections spec (`report.yml`) rendered with `./bin/mkt doc build`. The same
section types as proposals work — `summary`, `prose`, `scorecards`, `table`, `scenarios` (for
the time-series chart), `cta`. The only difference is `meta.badge: "Weekly Report"` /
`"Monthly Report"`. Do **not** build a new renderer or touch `tools/`.

Methodology is **PERCEIVE → ANALYZE → VALIDATE → ACT**. Every claim is falsifiable: state the
metric, the period compared, and the threshold that would flip "win" to "regression".

## Inputs
- `projects/<client>/client.yml` — `domain`, `competitors[]`, `ahrefs.project_id`,
  `ahrefs.brand_radar_report_id`, `analytics.gsc_site`. Resolve with
  `./bin/mkt config show --project <client>`.
- Prior snapshots in `projects/<client>/data/` (rank-history.csv, kpi-history.csv,
  refdomains, traffic). These define the *prior period* you diff against.
- Cadence: weekly = last 7 days vs the 7 before; monthly = last full calendar month vs the one
  before. Today is absolute (e.g. `2026-06-23`). Always call `doc` on a tool before first use;
  monetary values are USD cents (÷100).

## Workflow

### 1. PERCEIVE — pull the period and the prior period
Pull current + prior values so every number carries a delta. Save raw pulls to `data/`.
- **Rankings** — `rank-tracker-overview` (tracked positions, distribution) and
  `rank-tracker-competitors-overview` for competitor position context. Hand off to the
  **`rank-tracking`** skill for the full mover list / SERP features if needed.
- **Organic traffic & value** — `site-explorer-metrics-history` (organic traffic, traffic
  value, keyword count) for our `domain` across the window.
- **Authority / links** — `site-explorer-refdomains-history` and `-referring-domains` for ref
  domain growth; `site-explorer-domain-rating-history` for DR. (Full link read →
  **`backlink-analysis`**.)
- **GEO / AI visibility** — `brand-radar-sov-history` + `-sov-overview` (share of voice vs
  competitors) and `brand-radar-mentions-history`. (Full GEO read → `geo-audit`.)
- **Owned data** — `gsc-performance-history` (clicks, impressions, CTR, avg position) and
  `web-analytics-stats` (sessions, conversions where wired).

### 2. ANALYZE — compute wins & regressions vs prior period
- For each KPI compute `current`, `prior`, absolute delta and % delta. Pull `prior` from the
  matching `data/` snapshot; if no snapshot exists, use the API's own historical window.
- Classify: **win** (improved past a threshold you state), **flat**, **regression** (declined
  past a threshold). Movers = keywords that gained/lost ≥ 3 positions or crossed page 1.
- Append this period's values to the snapshots in `data/` so next period has a baseline.

### 3. VALIDATE — sanity-check before it goes to a client
- Reconcile sources: a GSC clicks drop with flat rankings usually means seasonality or a SERP
  feature, not a loss — say which. Flag any metric where the two sources disagree.
- Don't report noise as signal: a single-keyword wobble inside normal variance is "flat".

### 4. ACT — compose `research/report.yml` and render
Follow `templates/report-weekly/report.schema.md` (weekly) or
`templates/report-monthly/report.schema.md` (monthly). Recommended spine:
1. `summary` — 3–5 bullet TL;DR of the period.
2. `scorecards` — headline KPIs with `delta` strings and `good: true/false` (organic traffic,
   clicks, avg position, ref domains, GEO SoV).
3. `table` — rank movers (term · prior · now · Δ · note) and/or competitor deltas.
4. `scenarios` — a `lines` time-series chart of traffic and/or SoV over the trailing weeks.
5. `prose` — "What changed + why" narrative and **next actions** (each falsifiable).
6. `cta` — one clear next step / contact.

For first reports or executive scans, add a current-state block before recommendations:
location/market, keyword demand, authority/DR, competitor set, SEO footprint, GEO/AI visibility,
social footprint, and the source/date for each. Do not show internal provider failures, commands,
costs, prompts, or rerun paths in a client-facing report; keep those in internal notes.

Render:
```bash
./bin/mkt doc build --in research/report.yml \
  --out deliverables/reports/<YYYY-MM-DD>-<period>.pdf --project <slug>
```
(e.g. `deliverables/reports/2026-06-23-weekly.pdf`). Review the PDF: cover badge correct,
scorecard deltas colored right, chart readable, no `\"` artifacts, numbers consistent across
sections. Iterate on `report.yml` and rebuild.

## Notes
- Chart data must be **numeric** — `kind: usd|pct|compact` formats it; no `$`/`%` in the data.
- Keep it tight: one strong trend chart, one mover table, a short narrative. Clients skim.
- Prefer bullets, tables, scorecards, and charts over long paragraphs. Avoid generic AI-ish
  sentence patterns and abstract phrasing; use concrete metric -> implication -> action.
- Spell out acronyms on first use or remove them. Prefer "ranking difficulty" over "KD" in any
  client-facing artifact.
- The **`kpi-dashboard`** skill defines the KPI tree and snapshot cadence that feed this report;
  its scorecards+time-series section drops straight in here.
- Reusable: the same `report.yml` spine works standalone or embedded — it's all `doc build`.

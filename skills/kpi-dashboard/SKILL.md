---
name: kpi-dashboard
description: >
  Define a client's KPI tree and track it over time — visibility (rankings, SoV, GEO SoV),
  traffic (organic sessions/clicks), conversion (leads, CAC), and authority (DR, referring
  domains). Use when asked to "set up a KPI dashboard", "track KPIs", "set up metrics", "build
  a growth dashboard", "what should we measure", or "define success metrics". Maps each KPI to
  a data source / Ahrefs MCP tool, snapshots to data/kpi-history.csv on a cadence, and renders
  a scorecards + time-series section reusable inside reports or as its own doc.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# kpi-dashboard

Defines **what to measure** for a client and keeps a running time series so every report and
review has a baseline. Output is two things: `research/kpi-definitions.md` (the KPI tree, each
metric mapped to a source) and a dashboard spec (`research/kpi-dashboard.yml`) of
`scorecards` + a `scenarios` time-series chart, rendered with the existing `./bin/mkt doc build`
renderer — no new tooling. The snapshot history lives in `data/kpi-history.csv`.

Methodology is **PERCEIVE → ANALYZE → VALIDATE → ACT**. Each KPI is falsifiable: it has a
definition, a source, a target, and a threshold that distinguishes signal from noise.

## Inputs
- `projects/<client>/client.yml` — `domain`, `competitors[]`, `ahrefs.project_id`,
  `ahrefs.brand_radar_report_id`, `analytics.gsc_site` / `ga4_property_id`. Resolve with
  `./bin/mkt config show --project <client>`. Today is absolute (e.g. `2026-06-23`).

## Workflow

### 1. PERCEIVE — define the KPI tree
Group KPIs into four layers. Default tree (trim to what the client cares about):

| Layer | KPI | Source / Ahrefs MCP tool |
|---|---|---|
| **Visibility** | Tracked rankings (avg position, top-3/top-10 count) | `rank-tracker-overview` |
| | Organic SoV vs competitors | `rank-tracker-competitors-overview` |
| | GEO / AI share of voice | `brand-radar-sov-overview` / `-sov-history` |
| **Traffic** | Organic traffic + traffic value | `site-explorer-metrics-history` |
| | Clicks / impressions / CTR (owned) | `gsc-performance-history` |
| | Sessions + conversions (owned) | `web-analytics-stats` |
| **Conversion** | Leads / signups, CAC | owned CRM / GA4 (`web-analytics-stats`, client export) |
| **Authority** | Domain Rating | `site-explorer-domain-rating-history` |
| | Referring domains | `site-explorer-refdomains-history` |

### 2. ANALYZE — map sources and set targets
- For each KPI record: definition (one line), source tool + exact params, cadence (weekly /
  monthly), current value, target, and the "noise floor" (delta below which a change is not
  reported). Write this to `research/kpi-definitions.md`.
- Conversion KPIs Ahrefs can't see (leads, CAC) get flagged as client-supplied with the field
  name to import; don't fabricate them.

### 3. VALIDATE — snapshot to data/kpi-history.csv
- Append one row per snapshot date: `date,kpi,value,source` (long format — easy to filter and
  chart). Append, never overwrite; this CSV is the time series every report diffs against.
- On each cadence run, re-pull and append. Keep units consistent (USD, not cents — ÷100).
- On append, diff each KPI against its prior snapshot and evaluate it against the alert
  thresholds below — a breach emits an alert row rather than waiting for the next report.

### 4. ACT — render the dashboard
Compose `research/kpi-dashboard.yml` (sections spec; see proposal/report schema for syntax):
- `scorecards` — one card per headline KPI: `{ label, value, delta: "+X% vs prior", good: bool }`.
- `scenarios` — a `lines` chart with `series` built from `kpi-history.csv` (e.g. organic
  traffic + SoV over the trailing weeks), numeric values, `kind: compact|usd|pct`.
- optional `table` — the full KPI tree with current vs target.

Render standalone:
```bash
./bin/mkt doc build --in research/kpi-dashboard.yml \
  --out deliverables/reports/<YYYY-MM-DD>-kpi-dashboard.pdf --project <slug>
```
Or drop the same `scorecards` + `scenarios` sections into a `report.yml` so the
**`report-generator`** skill embeds the dashboard inside the weekly/monthly report.

## Alert layer — push regressions, don't wait for the report
The same snapshot that feeds the time series is also the trip-wire. On each cadence append
(VALIDATE step), compare each KPI to its prior value and fire an alert when the per-KPI
threshold is crossed. Each threshold is **falsifiable**: an observation (the delta), a
dependency (the source tool that produced it), and a "how we'd know it failed" (the noise
floor below which we stay silent — see ANALYZE).

| KPI | Alert trigger (vs prior snapshot) | Source | How we'd know it's a false alarm |
|---|---|---|---|
| Tracked rankings | avg position drops ≥3, or any top-3 keyword falls out of top-3 | `rank-tracker-overview` | SERP volatility week — competitor positions moved too; re-pull next day |
| Organic SoV | SoV declines ≥5 pts, or competitor overtakes us | `rank-tracker-competitors-overview` | new competitor entered the tracked set, not a real loss |
| GEO / AI SoV | AI SoV declines ≥5 pts | `brand-radar-sov-overview` | prompt set or model panel changed between runs |
| Organic traffic | traffic regresses ≥15% MoM (or ≥10% WoW) | `site-explorer-metrics-history` | Ahrefs index refresh / seasonality vs last year |
| Authority | DR drops ≥2, or net referring domains go negative | `site-explorer-domain-rating-history`, `-refdomains-history` | lost links are spam/lost-and-regained noise, not editorial |

- Emit alerts as rows in `data/kpi-alerts.csv` (`date,kpi,severity,observed,threshold,note`)
  and surface the open ones as a `scorecards` band (red `good: false`) at the top of the
  dashboard. Only breaches above the noise floor become alerts — everything else stays a
  silent data point.
- Cadence: this is the trigger feed for **`/competitor-watch`** — its weekly run reads the
  open alert rows and recommends 48-hour responses, closing the loop from detection to action.

## Notes
- Chart data is **numeric only** — `kind` adds `$`/`%`; never bake them into the data.
- Keep the tree to ~6–10 tracked KPIs. A dashboard everyone reads beats one nobody trusts.
- Always call `doc` on a tool before first use; monetary values are USD cents (÷100).
- This is the upstream definition for **`report-generator`** (the cadence + history it diffs)
  and pairs with **`rank-tracking`** (rankings) and **`backlink-analysis`** (authority).

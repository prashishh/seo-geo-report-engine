# report.yml schema — WEEKLY report

A weekly report is just a **sections spec** (same format as a proposal) rendered with the
existing renderer:

```bash
./bin/mkt doc build --in research/report.yml \
  --out deliverables/reports/<YYYY-MM-DD>-weekly.pdf --project <slug>
```

There is **no separate report renderer**. The section/chart syntax is identical to
`templates/proposal/proposal.schema.md` — read that for the full field reference (plain-YAML,
`**bold**` in text, numeric-only chart data, etc.). The only differences for a report:

- `meta.badge: "Weekly Report"` (sets the top-right kicker on the cover).
- Lead with deltas (period-over-period) — a weekly report is about **what changed**.
- Keep it to one page or two: TL;DR, KPI scorecards, a mover table, one trend chart, a short
  narrative + next actions, and a CTA.

## Recommended section order

| # | type | Purpose |
|---|------|---------|
| — | `meta` | `client`, `title`, `subtitle`, `badge: "Weekly Report"`, `date`, `author` |
| 1 | `summary` | 3–5 bullet TL;DR of the week (no pillars needed) |
| 2 | `scorecards` | Headline KPIs with `delta` + `good` (traffic, clicks, avg position, ref domains, GEO SoV) |
| 3 | `table` | Rank movers — term · prior · now · Δ · note |
| 4 | `scenarios` | A `lines` time-series chart of traffic and/or SoV over trailing weeks |
| 5 | `prose` | "What changed + why" narrative and **next actions** (each falsifiable) |
| 6 | `cta` | One next step / contact |

Notes on the section types:
- **scorecards** — `cards: [{ label, value, delta: "+12% vs last wk", good: true|false }]`,
  `cols: 4`. `good:false` colors the delta red (use for regressions).
- **scenarios** is the chart carrier (it renders a chart + optional table). Use chart
  `type: lines`, `series: { Organic: [...], "GEO SoV": [...] }`, `x_labels`, `kind: compact`
  (or `usd`/`pct`). Chart values are **numeric only** — `kind` adds `$`/`%`.
- **table** rows can include a `{ group: "..." }` header row to label sections.

## Filled example

```yaml
meta:
  client: "Acme"
  title: "Acme — Weekly SEO Report"
  subtitle: "Week of 2026-06-16 -> 2026-06-22 vs prior week"
  badge: "Weekly Report"
  date: "2026-06-23"
  author: "seo-geo-report-engine"

sections:
  - type: summary
    num: "01"
    title: "This week at a glance"
    bullets:
      - "Organic traffic **+12%** WoW; clicks up on three money pages."
      - "**5 keywords** entered the top 10; net +2 on tracked set."
      - "One regression: *acme pricing* slipped 4->8 after a competitor refresh."
      - "GEO share of voice held at **18%** (flat WoW)."

  - type: scorecards
    num: "02"
    title: "Headline KPIs"
    cols: 4
    cards:
      - { label: "Organic traffic", value: "8.4K", delta: "+12% WoW", good: true }
      - { label: "GSC clicks", value: "2,310", delta: "+8% WoW", good: true }
      - { label: "Avg position", value: "14.2", delta: "-0.9 WoW", good: true }
      - { label: "Referring domains", value: "412", delta: "+6 WoW", good: true }
      - { label: "Top-10 keywords", value: "37", delta: "+5 WoW", good: true }
      - { label: "GEO SoV", value: "18%", delta: "flat WoW", good: true }

  - type: table
    num: "03"
    title: "Rank movers"
    table:
      headers: ["Keyword", "Prior", "Now", "Delta", "Note"]
      align: ["left", "right", "right", "right", "left"]
      rows:
        - { group: "GAINED" }
        - ["acme integrations", 14, 6, "+8", "New comparison page indexed"]
        - ["acme api docs", 11, 7, "+4", "Internal links added"]
        - { group: "LOST" }
        - ["acme pricing", 4, 8, "-4", "Competitor refreshed their page"]

  - type: scenarios
    num: "04"
    title: "Traffic & GEO SoV trend"
    chart:
      type: lines
      series:
        Organic: [6800, 7100, 7500, 8400]
        "GEO SoV": [15, 16, 18, 18]
      x_labels: ["Wk -3", "Wk -2", "Wk -1", "This wk"]
      kind: compact
    figure_title: "Trailing 4 weeks"
    figure_unit: "sessions / SoV %"

  - type: prose
    num: "05"
    title: "What changed + next actions"
    paragraphs:
      - "Traffic growth came from the new **integrations comparison page** ranking and from
         internal links pushing the API docs into the top 10."
      - "The *acme pricing* drop tracks a competitor's page refresh, not a sitewide issue —
         rankings elsewhere are stable."
    bullets:
      - "**Refresh the pricing page** this week (add comparison table, FAQ schema). Falsifiable:
         expect 8->top-5 within 2 weeks; if not in the top 6 after 14 days, the page isn't the
         lever — investigate links."
      - "Build internal links to the two newly-ranking pages to consolidate the gains."
    callout: "Net week: a clear win on acquisition pages, one contained pricing regression with a fix in flight."

  - type: cta
    title: "Next step"
    body: "Approve the pricing-page refresh and we ship it Monday."
    contact: "Your Agency · hello@example.com"
```

See `skills/report-generator/SKILL.md` for how the data is pulled (period-over-period deltas)
and `templates/proposal/proposal.schema.md` for the exact section/chart field reference.

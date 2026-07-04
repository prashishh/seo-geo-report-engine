# report.yml schema — MONTHLY report

A monthly report is the same **sections spec** as a weekly one — rendered with the existing
renderer, no separate tooling:

```bash
./bin/mkt doc build --in research/report.yml \
  --out deliverables/reports/<YYYY-MM-DD>-monthly.pdf --project <slug>
```

The section/chart syntax is identical to `templates/proposal/proposal.schema.md` (read it for
the full field reference). Differences vs the weekly template:

- `meta.badge: "Monthly Report"`.
- **Broader** — month-over-month, more sections, more narrative. A monthly report reviews the
  whole engagement and sets the next month's plan, not just "what moved this week".
- Compare last full calendar month vs the prior month (e.g. May vs April).

## Recommended section order

| # | type | Purpose |
|---|------|---------|
| — | `meta` | `client`, `title`, `subtitle`, `badge: "Monthly Report"`, `date`, `author` |
| 1 | `summary` | Month TL;DR — headline wins, one or two regressions, theme |
| 2 | `scorecards` | Month-over-month KPI cards (traffic, value, clicks, avg position, ref domains, DR, GEO SoV) |
| 3 | `scenarios` | Trends chart — `lines` for rankings / traffic / GEO SoV over trailing months |
| 4 | `table` | Backlink growth (ref domains, DR, new linking domains MoM) |
| 5 | `table` | Competitor movement (us vs each competitor: position / SoV deltas) |
| 6 | `table` (or `prose`) | Content shipped this month (page · type · status · early signal) |
| 7 | `prose` | Narrative: what worked, what didn't (falsifiable read on each) |
| 8 | `prose` | Forward plan — next month's priorities, each falsifiable |
| 9 | `cta` | Decision needed / next step |

Use two or three `lines` series in section 3 (e.g. Organic traffic, Top-10 keyword count,
GEO SoV) with monthly `x_labels`. Chart values are **numeric only** — `kind: compact|usd|pct`
formats them. Tables may use `{ group: "..." }` header rows.

## Filled example (abbreviated)

```yaml
meta:
  client: "Acme"
  title: "Acme — Monthly Growth Report"
  subtitle: "May 2026 vs April 2026"
  badge: "Monthly Report"
  date: "2026-06-23"
  author: "seo-geo-report-engine"

sections:
  - type: summary
    num: "01"
    title: "Month in review"
    bullets:
      - "Organic traffic **+34% MoM**; traffic value crossed **$48K/mo**."
      - "Top-10 keyword count grew **52 -> 71**; DR up **41 -> 43**."
      - "GEO share of voice **15% -> 21%** as two pages got cited in AI answers."
      - "Shipped **4 pages** (2 comparison, 1 guide, 1 pricing refresh) — all indexed."

  - type: scorecards
    num: "02"
    title: "Month-over-month KPIs"
    cols: 4
    cards:
      - { label: "Organic traffic", value: "31.2K", delta: "+34% MoM", good: true }
      - { label: "Traffic value", value: "$48K", delta: "+29% MoM", good: true }
      - { label: "GSC clicks", value: "9,840", delta: "+22% MoM", good: true }
      - { label: "Avg position", value: "12.8", delta: "-1.6 MoM", good: true }
      - { label: "Referring domains", value: "431", delta: "+24 MoM", good: true }
      - { label: "Domain Rating", value: "43", delta: "+2 MoM", good: true }
      - { label: "Top-10 keywords", value: "71", delta: "+19 MoM", good: true }
      - { label: "GEO SoV", value: "21%", delta: "+6pts MoM", good: true }

  - type: scenarios
    num: "03"
    title: "Trends — rankings, traffic, GEO SoV"
    chart:
      type: lines
      series:
        "Organic (K)": [18, 21, 23, 31]
        "Top-10 kw": [38, 47, 52, 71]
        "GEO SoV %": [9, 12, 15, 21]
      x_labels: ["Feb", "Mar", "Apr", "May"]
      kind: compact
    figure_title: "Trailing 4 months"
    figure_unit: "indexed metrics"

  - type: table
    num: "04"
    title: "Backlink growth"
    table:
      headers: ["Metric", "Apr", "May", "Delta"]
      align: ["left", "right", "right", "right"]
      rows:
        - ["Referring domains", 407, 431, "+24"]
        - ["DR>=30 linking domains", 88, 101, "+13"]
        - ["Domain Rating", 41, 43, "+2"]

  - type: table
    num: "05"
    title: "Competitor movement"
    table:
      headers: ["Domain", "Their top-10 kw", "MoM", "GEO SoV", "MoM"]
      align: ["left", "right", "right", "right", "right"]
      rows:
        - ["acme.com (us)", 71, "+19", "21%", "+6"]
        - ["rivalco.com", 96, "+4", "28%", "-2"]
        - ["nextbest.io", 63, "+1", "14%", "+1"]

  - type: table
    num: "06"
    title: "Content shipped"
    table:
      headers: ["Page", "Type", "Status", "Early signal"]
      align: ["left", "left", "left", "left"]
      rows:
        - ["/integrations vs rivalco", "Comparison", "Live", "Ranking p1 for 2 terms"]
        - ["/api-guide", "Guide", "Live", "Indexed, climbing"]
        - ["/pricing", "Refresh", "Live", "4->5, FAQ schema added"]
        - ["/vs-nextbest", "Comparison", "Live", "Indexed wk 4"]

  - type: prose
    num: "07"
    title: "What worked, what didn't"
    paragraphs:
      - "Comparison pages drove most of the gain — they rank fast and earn the AI citations
         lifting GEO SoV. The guide is slower but indexing cleanly."
    bullets:
      - "**Worked:** comparison-page motion. Falsifiable bet for next month: 2 more pages add
         +8 top-10 keywords; fails if <3 of the 2x money terms reach p1 in 30 days."
      - "**Didn't move:** the resource hub — thin internal linking. Fix in next month's plan."

  - type: prose
    num: "08"
    title: "Next month's plan"
    bullets:
      - "Ship 2 more comparison pages targeting the highest-volume gap terms."
      - "Internal-link the resource hub; expect it to start ranking within 3 weeks."
      - "Outreach to 15 warm link prospects (link to >=2 competitors, not us)."
    callout: "Theme: double down on the comparison motion that's compounding; unblock the hub."

  - type: cta
    title: "Decision needed"
    body: "Approve 2 comparison pages + the outreach list for June."
    contact: "Your Agency · hello@example.com"
```

See `skills/report-generator/SKILL.md` for the data pulls (MoM deltas across rankings, traffic,
links, GEO) and `templates/proposal/proposal.schema.md` for the exact section/chart field
reference.

# proposal.yml schema

The proposal-builder skill composes this file; `./bin/mkt proposal build --project <p>`
renders it to `deliverables/<slug>-growth-proposal.pdf`. Plain-YAML (the dependency-free
reader supports maps, lists, lists-of-maps, inline `[a, b]` lists, `**bold**` in text).

```yaml
meta:
  client: "ACME"                 # brandmark shown top-left of cover
  title: "ACME Growth Proposal"
  subtitle: "one-line promise"
  badge: "Growth Proposal"       # top-right kicker
  date: "2026-06-23"
  author: "your team"            # optional, shown under the cover rule

sections:                        # ordered; rendered top to bottom
  - type: summary                # exec summary + the 3 pillar cards
    num: "00"
    title: "Executive summary"
    bullets: ["...", "**bold** ..."]
    pillars:
      - { tag: "PILLAR 01", name: "Foundation", when: "Months 1–2", items: ["...","..."] }

  - type: prose                  # numbered section: bullets + paragraphs + optional chart
    num: "01"
    title: "..."
    page_break: true             # start on a new page
    paragraphs: ["..."]
    bullets: ["..."]
    callout: "highlighted aside"
    chart: { type: bar_h, rows: [["Label", 20]], kind: pct, highlight: "Label" }
    figure_title: "..."
    figure_unit: "share of spend"
    figure_note: "..."

  - type: pillars_detail         # deep-dive groups with deliverables boxes
    num: "01"
    title: "Foundation"
    groups:
      - name: "Workstream"
        bullets: ["..."]
        deliverables: ["...", "..."]

  - type: roadmap                # workstream gantt
    num: "05"
    title: "Six-month roadmap"
    gantt:
      rows: [["Brand & site", [3,2,1,1,1,1]]]   # intensity 0=blank..3=heavy
      months: ["M1","M2","M3","M4","M5","M6"]
      legend: ["Sustaining","Active","Heavy build"]
    note: "..."

  - type: scenarios             # projection chart + scenario table
    num: "07"
    title: "Six-month projection"
    bullets: ["Conservative ...","Probable ...","Aggressive ..."]
    chart:
      type: lines
      series: { Conservative: [100,160,275], Probable: [100,185,385], Aggressive: [100,235,500] }
      x_labels: ["TODAY","M3","M6"]
      kind: usd
      band: [3, 4]                      # shaded index range (optional)
      markers: { 3: "Dashain" }         # vertical markers (optional)
    figure_title: "Projected daily volume"
    figure_unit: "USD per day"
    table:
      headers: ["Metric","Conservative","Probable","Aggressive"]
      align: ["left","right","right","right"]
      rows:
        - { group: "MONTH 3" }
        - ["Daily volume","$160K","$185K","$235K"]

  - type: scorecards            # KPI cards
    num: "08"
    title: "Growth metrics"
    cols: 4
    cards:
      - { label: "Daily volume", value: "$385K", delta: "+285% vs today", good: true }

  - type: table                 # standalone table
    num: "09"
    title: "..."
    table: { headers: [...], rows: [...], align: [...] }

  - type: cta                   # closing navy block
    title: "Next step"
    body: "..."
    contact: "name · email"
```

## Chart types (from tools/charts/svg.py)
- `bar_h` rows=[[label,val]], kind=compact|pct|usd, highlight=label
- `bar_v` rows=[[label,val]], highlight_range=[a,b], band_label
- `lines` series={name:[..]}, x_labels=[..], band=[a,b], markers={i:label}, kind
- `stacked_cols` columns=[[col_label,[[seg,val]]]], kind=pct
- `gantt` rows=[[label,[intensity..]]], months=[..], legend=[l1,l2,l3]
- `scorecards` cards=[{label,value,delta?,good?}], cols
- `table` headers, rows, align

**Numbers must be numeric** (no `$`/`%` in chart data — `kind` formats them).

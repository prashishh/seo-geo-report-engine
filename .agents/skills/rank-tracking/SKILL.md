---
name: rank-tracking
description: >
  Track keyword positions over time and report movers — gained/lost rankings, SERP-feature
  presence, and competitor position deltas. Use when asked for "rank tracking", "keyword
  positions", "are we ranking for X", "track rankings", "position changes", "did we move up",
  "what dropped", or "how are we ranking vs <competitor>". Snapshots tracked positions to
  data/rank-history.csv each run and writes a dated mover report to the client's research folder.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# rank-tracking

Reads the client's Rank Tracker project, snapshots tracked positions, and reports **what moved**
since the last snapshot — gains, losses, SERP features, and how competitors shifted. Output is
`research/rank-report.md` plus an appended `data/rank-history.csv`. Ahrefs MCP is the engine
(see `knowledge/ahrefs-mcp-map.md`).

Methodology is **PERCEIVE → ANALYZE → VALIDATE → ACT**. Every mover is falsifiable: state the
term, prior position, current position, and the threshold (≥3 positions or a page-1 crossing)
that makes it a real move vs noise.

## Inputs
- `projects/<client>/client.yml` — `domain`, `competitors[]`, `target_keywords[]`, `market`,
  and `ahrefs.project_id` (the Rank Tracker project). Resolve with
  `./bin/mkt config show --project <client>`.
- Prior `data/rank-history.csv` (the last snapshot you diff against).

### Setup (first run)
If `ahrefs.project_id` is empty, list projects with `management-projects`, find the client's
Rank Tracker project, and paste its id into `client.yml` under `ahrefs.project_id`. Confirm the
tracked keyword set with `management-project-keywords` and competitors with
`management-project-competitors`. Today is absolute (e.g. `2026-06-23`); call `doc` on a tool
before first use.

## Workflow

### 1. PERCEIVE — pull current positions
- `rank-tracker-overview` — current positions + distribution (top-3 / top-10 / top-100) for the
  project's tracked keywords.
- `management-project-keywords` — confirm the tracked set (so a "lost" term isn't just untracked).
- `rank-tracker-serp-overview` — SERP composition for key terms (which features appear:
  AI Overview, featured snippet, PAA, sitelinks, video).

### 2. ANALYZE — compute movers vs the last snapshot
- Diff current positions against the most recent `data/rank-history.csv` snapshot.
- **Gained** = improved ≥3 positions or entered top-10/top-3. **Lost** = dropped ≥3 or fell off
  page 1. Everything else = flat (don't report it as a move).
- Note SERP-feature changes per term (gained/lost a snippet, AI Overview now present).

### 3. VALIDATE — competitor context
- `rank-tracker-competitors-overview` + `-stats` — competitor position distribution and share.
- `rank-tracker-competitors-domains` / `-competitors-pages` — which competitor domains/pages
  moved on the same terms. A drop where a competitor jumped is a competitive loss; a drop where
  the whole SERP reshuffled (new AI Overview, new feature) is a feature change — label which.

### 4. ACT — snapshot + write the report
- Append today's positions to `data/rank-history.csv`
  (`date,keyword,position,url,serp_features` — append, never overwrite).
- Write `projects/<client>/research/rank-report.md` (dated):
  1. **Headline** — top-3/top-10 counts now vs prior, net movers.
  2. **Gained** table — term · prior · now · Δ · ranking URL.
  3. **Lost** table — term · prior · now · Δ · likely cause (competitor / SERP feature / drop).
  4. **SERP features** — terms that gained/lost features; flag AI Overview presence.
  5. **Competitor deltas** — who moved on our terms, with positions.
  6. **Watch / next** — each item falsifiable: observation → expected move → the position by a
     date that would confirm or kill it.

## Notes
- Feeds **`report-generator`** (the mover table + headline counts drop into the weekly/monthly
  report) and **`kpi-dashboard`** (rankings = the visibility KPI layer).
- For *why* a term is winnable or what to attack, hand to **`competitor-analysis`** /
  **`keyword-research`**; this skill reports position movement, not opportunity sizing.
- Monetary values are USD cents (÷100) where they appear; always `doc` a tool before first use.

---
name: content-refresh
description: >
  Detect and prioritize content decay, then produce a refresh plan that decides SHIP / FIX / BLOCK
  per page. Use when asked about "content decay", "refresh old content", "declining pages", "traffic
  dropping on a page", "update stale content", "which posts to update", "content audit for refresh",
  or "why did this page lose rankings/traffic". Snapshots on-page state, diffs each page against a
  stored baseline, classifies changes CRITICAL/WARNING/INFO, and routes every page to a closed-loop
  verdict — SHIP (leave it), FIX (refresh brief), or BLOCK (fatal issue to fix first). FIX pages hand
  off to content-brief; the per-page on-page snapshot is appended to a versioned CSV each run.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# content-refresh

Closes the loop on **existing** content. Other skills create pages; this one finds the ones that
are bleeding, decides what to do about each, and proves the decision was right next run. It fuses
two patterns: a baseline→compare→history regression gate (claude-seo `seo-drift`) and an
audit verdict of SHIP / FIX / BLOCK (seo-geo `content-quality-auditor`). Runs on the same CSV
cadence as `rank-tracking` (data/rank-history.csv) and `kpi-dashboard` (data/kpi-history.csv), so
it slots into a monthly retainer. Prefer Ahrefs MCP (`knowledge/ahrefs-mcp-map.md`); call `doc` on a
tool before first use. Methodology lives in `playbooks/content-decay.md`.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — decay detection.** Resolve the project (`./bin/mkt config show --project <client>`);
read `client.yml` for domain and locales. Find pages losing ground period-over-period (compare the
last ~90 days to the prior ~90, ending 2026-06-23):
- `site-explorer-pages-by-traffic` — current organic traffic + value per URL (the inventory).
- `gsc-pages-history` (all pages) then `gsc-page-history` (per declining URL) — clicks, impressions,
  and average position over time. Decay = clicks down ≥20% **or** average position worsened ≥3 spots
  while impressions held (intent still there, we slipped) vs an SERP-wide volume collapse (don't
  refresh a page whose whole topic died — verify with `keywords-explorer-volume-history`).
- Tag each declining URL with a **decay cause hypothesis**: stale facts/date, SERP intent shift,
  thinner than current top results, cannibalization, or lost links (`site-explorer-pages-by-backlinks`).

**ANALYZE — baseline + diff.** For each candidate URL, snapshot ~13 on-page fields. Pull on-page
state from `site-audit-page-content` / `site-audit-page-explorer` (or `WebFetch` the live URL as
fallback): `url, title, meta_description, canonical, h1, h2_count, h3_count, schema_types,
word_count, internal_links, date_modified, content_hash, snapshot_date`. Append the row to
`projects/<client>/data/content-baselines.csv`. Diff against this URL's most recent prior snapshot
and classify each changed field:
- **CRITICAL** — canonical changed/now points off-page, H1 lost/duplicated, schema removed, title
  emptied, `noindex` introduced, word_count dropped >40%. These can *cause* the decay.
- **WARNING** — title/meta rewritten, `date_modified` >12 months stale (content rot), word_count
  down 15–40%, internal_links dropped materially, schema type changed.
- **INFO** — minor copy edits (content_hash changed, structure intact), small link/count drift.
First run = no prior snapshot, so there's no diff; record the baseline and judge decay on traffic
signals alone.

**VALIDATE — every verdict falsifiable.** Per page, state the closed-loop block:
- **Observation** — the decay metric + the diff that explains it (cite the Ahrefs/GSC tool + date,
  e.g. "clicks −38% and average position 6→11 in `gsc-page-history` 2026-03→2026-06; canonical
  flipped off-page in content-baselines diff").
- **Dependency** — what must be true for the verdict to hold (e.g. "topic volume is flat in
  `-volume-history` so demand still exists", "our DR ≥ median SERP KD", "no newer page is
  cannibalizing").
- **How we'd know this failed** — leading indicator for next run: "after refresh, page still below
  position 10 at 8 weeks in `rank-tracker-overview`", or "clicks keep falling next snapshot → cause
  was off-page (links/SERP), not on-page."

**ACT — verdict + output.** Emit one verdict per page:
- **SHIP** — decline is noise (seasonal/SERP-wide) or page is healthy; no change. Re-snapshot only.
- **FIX** — recoverable decay with a clear cause → write a refresh action list (what to update:
  facts, date, depth vs current top results, schema, internal links) and hand the URL+cause to
  **content-brief** for the writer-ready brief.
- **BLOCK** — a CRITICAL fatal issue (rogue canonical, noindex, broken H1/schema) must be fixed
  *before* any refresh ships; route to `technical-seo-audit`. Don't brief a writer for a page Google
  can't index.

Write `projects/<client>/research/content-refresh.md`: a decay table (URL, clicks/position delta,
cause, verdict), the per-page verdict blocks above with refresh actions, and a prioritized FIX queue
(rank by recoverable traffic × feasibility). The appended baseline rows live in
`projects/<client>/data/content-baselines.csv`.

## Notes
- Idempotent + versioned: one snapshot row per URL per run; the CSV *is* the history — never
  overwrite, always append. Next run diffs against it to confirm verdicts (the regression gate).
- Decay ≠ refresh: a page whose whole topic lost volume is SHIP, not FIX — check
  `keywords-explorer-volume-history` before briefing.
- Hand-offs: FIX → `content-brief`; BLOCK → `technical-seo-audit`; recovered movers tracked in
  `rank-tracking`. Feed the FIX queue into `report-generator` as a retainer deliverable.
- Monetary fields (traffic value) come back in **USD cents** — divide by 100.
- If a tool returns `render_with` metadata in chat, call the named render tool; for the CSV/MD
  outputs above, write the data directly to the files.
- Reference upstream: claude-seo `seo-drift` (baseline/compare/history) + seo-geo-claude-skills
  `content-refresher` / `content-quality-auditor` (SHIP/FIX/BLOCK) — adapted here to Ahrefs +
  GSC and the framework's CSV cadence.

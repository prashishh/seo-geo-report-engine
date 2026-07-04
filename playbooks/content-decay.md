# Content decay & refresh methodology

Closes the loop on *existing* content. `content-refresh` runs this on a cadence; it routes each
page to **SHIP / FIX / BLOCK** and hands FIX pages to [[content-brief]], BLOCK pages to
[[technical-seo-audit]]. Fits the existing `data/` snapshot cadence ([[rank-tracking]], kpi-history).

## Why content decays
Rankings/traffic erode as: competitors publish fresher/better pages; SERP intent shifts; facts
go stale (prices, dates, stats); the SERP gains features (AI Overviews, packs) that push you down;
or internal cannibalization splits authority. Decay is normal — the job is to catch it early and
decide deliberately.

## 1. Decay detection
Period-over-period, find pages **losing** clicks/impressions/position:
- Ahrefs `site-explorer-pages-by-traffic` (traffic drop) + `site-explorer-organic-keywords` (lost positions).
- Owned: `gsc-pages-history` / `gsc-page-history` (clicks/impressions/position deltas) — most reliable.
Rank by **traffic-at-risk** (lost clicks × value), not % drop, so you fix what matters.

## 2. Baseline / diff
Snapshot ~13 on-page fields per page to `data/content-baselines.csv` and diff vs the prior snapshot:
`url, title, meta_description, canonical, h1, h2_count, word_count, internal_links, schema_types,
date_modified, content_hash, indexable, last_checked`.
Classify changes: **CRITICAL** (canonical/indexable/title changed, content_hash diverged on a money page),
**WARNING** (meta/H1/word-count moved), **INFO** (minor).

## 3. Verdict (the closed loop)
Per page, emit one:
- **SHIP** — healthy or improving; no action. (Falsifiable: traffic flat/up, position stable.)
- **FIX** — decaying but salvageable; generate a refresh brief (→ content-brief). Typical fixes:
  update facts/dates, add the subtopics/entities competitors now cover, answer-first rewrite for
  AEO (→ aeo-content-patterns), refresh internal links (→ internal-linking), update `dateModified`.
- **BLOCK** — a fatal issue caused the drop (noindex, canonical to wrong page, 404/redirect, JS-rendering
  failure); route to technical-seo-audit before any content work — refreshing copy won't help.

## 4. Refresh, don't churn
Refresh when the page has earned links/age and intent still matches. Rewrite-from-scratch only when
page-type no longer fits the SERP. Always change `dateModified` truthfully (don't fake freshness —
Google detects trivial date-only edits).

## 5. Cadence & measurement
Run monthly (or after core updates). Leading indicator per FIX: recovery of lost clicks/position
within 1–2 crawls. Track refresh win-rate over time in kpi-history to prove the retainer's value.

---
name: keyword-research
description: >
  Seed → expansion → intent clustering → prioritization. Build a keyword map that tells the
  client which pages to create or strengthen. Use when asked to "do keyword research", "find
  keywords", "what keywords should we target", "build a keyword map", "expand this seed list",
  or "size the search opportunity" for a topic/market. Clusters by search intent and topic,
  then scores by volume × intent × KD-feasibility against the client's own domain rating.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# keyword-research

Turns a handful of seeds into a prioritized **keyword map** (clusters → target pages). The IP is
the scoring: don't just rank by volume — rank by *winnable* volume given the client's authority.
Prefer Ahrefs MCP (see `knowledge/ahrefs-mcp-map.md`); call `doc` on a tool before first use.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — gather.** Resolve the project (`./bin/mkt config show --project <client>`); read
`client.yml` for domain, locales, competitors, seeds. Establish the client's ceiling:
`site-explorer-domain-rating` (our DR) — this sets the KD bar we can realistically win.
- Expand each seed with `keywords-explorer-matching-terms` (everything containing the seed),
  `keywords-explorer-related-terms` ("also rank for"), and `keywords-explorer-search-suggestions`
  (autocomplete long-tail). Pull `keywords-explorer-overview` for volume, KD, CPC, parent topic.
- Localize: `keywords-explorer-volume-by-country` for each target locale — don't assume US volume.
- Seasonality check on head terms: `keywords-explorer-volume-history` (flag spiky vs evergreen).

**ANALYZE — cluster + score.** Two-axis clustering:
- **Intent** — informational / commercial / transactional / navigational. Infer from the term and
  SERP (`serp-overview` on a sample to confirm — features, page types). Tag every keyword.
- **Topic** — group by Ahrefs *parent topic* + shared head term so one cluster = one target page.
- **Priority score** per cluster:
  `score = volume × intent_weight × feasibility`, where
  `intent_weight` ≈ transactional 1.0 / commercial 0.8 / informational 0.5 / navigational 0.2
  (tune to the client's funnel), and `feasibility = 1` if cluster median KD ≤ our DR-implied
  ceiling, scaling down as KD rises above it. Surface a few high-volume/low-feasibility terms as
  "later" so the client sees them, but rank winnable clusters first.

**VALIDATE — every recommendation falsifiable.** For each top cluster state:
- **Observation** — the volume/KD/intent data that motivates it (cite the Ahrefs tool + date).
- **Dependency** — what must be true to win it (e.g. "our DR ≥ median KD of SERP", "we have a
  page type matching the dominant intent", "topic is on-strategy for the ICP").
- **How we'd know this failed** — a leading indicator: e.g. "after publishing, page stuck below
  position 20 at 8 weeks in `rank-tracker-overview`" or "SERP is dominated by forums/UGC we can't
  displace." Note seasonal terms whose flat traffic is expected off-peak.

**ACT — output.** Write two files under `projects/<client>/research/`:
- `keywords.csv` — one row per keyword: `keyword, cluster, intent, volume, kd, cpc, country,
  parent_topic, priority_score, target_page`.
- `keyword-map.md` — clusters ranked by score; each shows intent, total/winnable volume, median
  KD vs our DR, the **target page** (new or existing URL), and the falsifiability block above.
  Localization notes call out where `-volume-by-country` changes the priority order per market.

## Live DataForSEO path (Codex-safe, one command)
When the Ahrefs MCP is not connected (Codex) or you want a fast, cheap live pull, use the DataForSEO
keyword tool, which now returns **keyword difficulty directly** (Labs is unlocked):
```
python3 tools/seo/keyword_research.py --project <slug> --location <code> \
    --seeds "seed one" "seed two" \
    --topic <specific tokens a keyword must contain to be on-topic> \
    --out projects/<slug>/data/raw/dataforseo/kw-<date>.json
```
It pulls target volume+KD+intent (`keyword_overview`), expansion ideas (`keyword_ideas`), competitor
footprints (`ranked_keywords`), and the true content gap (keywords rivals rank for that the client does
not), then scores each by opportunity (volume x winnability x intent) and writes `data/keywords-scored.csv`.
- **Always pass `--topic`.** Raw Labs expansion + competitor ranked-keywords are noisy (brand-navigational
  and tangential high-volume terms leak in); the topic tokens are the relevance gate that keeps the output
  clean. Without it the tool derives tokens from seeds/targets, which is weaker.
- **Labs covers ~94 locations; Nepal (2524) is not one.** For Nepal-style markets the tool auto-falls back
  to Google Ads volume + live-SERP competitors and marks KD unavailable, use SERP strength as the
  difficulty proxy there.
- **Cross-check the headline volume/KD against Ahrefs before quoting a client** (per the two-system rule in
  `knowledge/seo-geo-tooling-landscape.md`: DataForSEO is the volume number of record, Ahrefs KD goes in
  the deliverable, divergence is a signal to reconcile against GSC).

## Notes
- Don't boil the ocean: cap expansion per seed, dedupe by parent topic, drop zero-volume noise.
- Hand clusters to `content-brief` for writer-ready briefs and to `rank-tracking` to monitor.
- Monetary fields (CPC) come back in **USD cents** — divide by 100.
- If a tool returns `render_with` metadata in chat, call the named render tool; for CSV/MD
  outputs, write the data directly to the files above.
- Reference upstream: AgriciDaniel/claude-seo `seo-cluster` / `seo-plan` (SERP-overlap clustering
  idea) — here adapted to Ahrefs parent-topic + intent and DR-aware feasibility scoring.

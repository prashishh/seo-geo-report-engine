---
name: seo-data-router
description: >
  Choose and document the right SEO/GEO data source for a workflow. Use when asked about provider/
  source choice, API limits, cost control, connector planning, how to reduce paid API calls, or
  "what source should this skill use". Reflects the committed stack: DataForSEO (backbone) + Ahrefs
  (cross-check + Brand Radar) + Screaming Frog (deep crawl) + free owned Google data.
license: MIT
allowed-tools: Read, Bash, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# seo-data-router

Route SEO/GEO work to the cheapest source in our stack that can answer the question with enough
confidence. The stack is committed (see `knowledge/seo-geo-tooling-landscape.md`).

## Reference

Read `knowledge/seo-geo-tooling-landscape.md` before making source recommendations or connector plans.
It is the source of truth for the stack, the source-of-truth-per-metric map, and cross-check rules.

## Routing Rules

1. **Prefer owned truth first** (free, most credible):
   - Google Search Console for queries, pages, clicks, impressions, CTR, and average position.
   - GA4 for conversions, events, organic landing-page behavior, and attribution.
   - PageSpeed Insights / CrUX for page experience (real-user Core Web Vitals).
2. **DataForSEO is the default data backbone** (pay-as-you-go): live SERP + AI Overview, keyword
   volume/KD/intent/ideas, ranked keywords, keyword + link gap, backlinks, OnPage, domain + traffic
   intelligence, reviews/GBP/mentions, and direct LLM querying (ChatGPT/Gemini/Perplexity/Claude).
3. **Ahrefs is the trusted cross-check** (while held): the recognized DR/KD number for the deliverable,
   deep backlink authority, and Brand Radar for aggregated cross-engine AI SoV. When DataForSEO and
   Ahrefs disagree on volume/KD/backlinks, apply the cross-check rules in the landscape doc (the
   disagreement is the signal; reach for GSC/manual SERP as the third anchor).
4. **Screaming Frog for deep technical crawl** (local): JS render diff, custom extraction, forensic
   audits, and its Log File Analyser for AI-bot crawl evidence — the one thing the APIs cannot give.
5. **AI visibility uses our own engine**, not a bought suite: `llm-visibility` (DataForSEO multi-engine
   scan → SoV) + the `web-research` OpenRouter probe. Ahrefs Brand Radar only as a per-engagement
   pass-through when a client funds cross-engine SoV reporting.

Do NOT route to providers outside this stack (SE Ranking, Semrush, Serpstat, AccuRanker, Botify,
Profound/Otterly/Scrunch/Peec) — they were evaluated and rejected; adding one needs a new, explicit reason.

## Output Format

When this skill is used, produce:

- **Recommended provider mix:** primary, fallback, and owned-data sources.
- **What it covers:** endpoints or product areas needed.
- **What remains missing:** Ahrefs/Brand Radar/backlink/history/citation gaps.
- **Cost-control plan:** cache, snapshots, sampling, and when to avoid paid calls.
- **Implementation plan:** connector files, secret keys, normalized output files, and dashboard
  fields to add.
- **Validation plan:** how to compare provider outputs against Ahrefs or owned data before trusting
  them.

## Connector Contract

Any new connector should write both raw and normalized outputs into the active project:

```text
projects/<client>/data/raw/<provider>/<date>-<operation>.json
projects/<client>/data/<date>-<operation>.csv
```

Every normalized row should include:

- `provider`
- `operation`
- `captured_at`
- `market`
- `language`
- `device`
- `entity` (keyword, URL, domain, brand, prompt, or backlink)
- `metric`
- `value`
- `confidence` (`owned-data`, `provider-estimate`, `live-serp`, `sampled-ai-answer`,
  `manual-review`)
- `raw_path`

## Guardrails

- Do not recommend a one-stop-shop replacement when the workflow clearly needs multiple data
  types.
- Do not spend paid credits for data that GSC, GA4, PageSpeed, CrUX, project files, or cached
  snapshots already answer.
- Do not mix provider metrics without labeling the source and confidence.
- Treat AI visibility data as sampled measurement, not absolute truth.

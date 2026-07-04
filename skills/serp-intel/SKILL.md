---
name: serp-intel
description: >
  Live Google SERP + keyword + backlink + AI-answer intelligence via DataForSEO. Covers the Google AI
  Overview and who it cites, People-Also-Ask, ranking competitors, search volume, intent, and now
  keyword difficulty, keyword ideas, a domain's ranked keywords, competitor keyword gaps, backlink
  authority, and direct LLM querying. Use when asked to "check the Google AI Overview / SGE", "are we in
  Google's AI answer", "who does Google's AI cite for <query>", "live SERP analysis", "People Also Ask
  questions", "who ranks for <keyword>", "Google search volume", "keyword difficulty for these", "keyword
  ideas", "what keywords does <competitor> rank for", "keyword gap vs <competitor>", "ask ChatGPT /
  Perplexity / Gemini / Claude what they say about <brand>", or "track AI Overview citations". Powered by
  the DataForSEO connector (Codex-safe, no Ahrefs MCP needed) — the third engine in the multi-engine
  AI-visibility stack alongside the Perplexity probe (web-research) and Ahrefs Brand Radar.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# serp-intel

Live Google SERP intelligence via **DataForSEO** (the committed data backbone). Its biggest value is
capturing the **Google AI Overview** and its citations, the single most important AI-search surface,
which neither the Perplexity probe (`web-research`) nor Ahrefs Brand Radar covers. Codex-safe: pure
stdlib HTTP, no MCP.

## Setup
DataForSEO credentials are per-profile (`config/secrets.<profile>.env`). Check the active profile with
`./bin/mkt profile show`; switch with `./bin/mkt profile use personal|business`. Ahrefs + OpenRouter are
shared across profiles. Check budget: `python3 -c "import sys;sys.path.insert(0,'tools');from
connectors import dataforseo as d;from lib.config import load_secrets;load_secrets();print(d.balance())"`.

## What this plan's DataForSEO includes (re-verified 2026-07-01: FULLY UNLOCKED)
DataForSEO removed its per-product subscription gate, so **everything works now** across 5 engines:
- **SERP** — organic + Google **AI Overview** + People-Also-Ask + related.
- **Labs** — `keyword_overview` (volume + CPC + **keyword difficulty** + intent in one call),
  `keyword_difficulty` (cheap bulk KD), `keyword_ideas` (expansion), `ranked_keywords` (every keyword a
  domain ranks for — the Ahrefs organic-keywords equivalent), `domain_intersection` (competitor keyword
  gap), `competitors_domain`. **We now get KD from DataForSEO directly** (no longer Ahrefs-only).
- **Backlinks** — `backlinks_summary`, `referring_domains`, `backlinks_bulk_ranks` (DR-equiv for ≤1000
  domains in one call — ideal for scoring a competitor list).
- **OnPage** — `onpage_instant` (single-page technical read).
- **AI Optimization** — `llm_query` / `llm_models`: query **ChatGPT / Gemini / Perplexity / Claude**
  directly and capture the answer + its citations. A live, cross-engine GEO-visibility engine.

**One caveat:** DataForSEO Labs covers ~94 locations and **Nepal (2524) is NOT one of them** (US 2840 and
India 2356 are). For Labs-unsupported markets, use `keyword_volume` (Google Ads, any location) and
`serp_competitors` (SERP-derived, any location).

## Tool + connector
- **AI Overview tracker:** `python3 tools/geo/ai_visibility.py --project <slug> --location <code>
  --keywords "kw1" "kw2" --out projects/<slug>/data/raw/dataforseo/aio-<date>.json`. For each keyword
  it reports: did an AI Overview trigger, which domains it cites, and whether the client is cited.
- **Connector** (`tools/connectors/dataforseo.py`): `serp`, `ai_overview`, `paa`, `keyword_overview`
  (vol+KD+intent), `keyword_difficulty`, `keyword_ideas`, `ranked_keywords`, `domain_intersection`,
  `competitors_domain`, `serp_competitors` (SERP-derived, any location), `keyword_volume`,
  `backlinks_summary`, `referring_domains`, `backlinks_bulk_ranks`, `onpage_instant`, `llm_query`.
- Locations: 2840 US, 2524 Nepal, 2356 India, 2826 UK. Languages: "en", "ne", ...

## How it feeds the other skills
- **geo-audit / ai-citation-sprint:** the Google AI Overview is the third citation engine. Log AIO
  results (triggered / cited / competing domains) to `data/ai-citation-log.csv` alongside the
  Perplexity probe and Brand Radar, so the multi-engine "3+ of N engines" target is measured against
  Google's real AI surface, not just chat models.
- **content-brief:** feed the live PAA questions and the top-10 competitor pages (from `serp` /
  `serp_competitors`) into the brief so it out-covers what actually ranks.
- **keyword-research:** `keyword_overview` gives volume + CPC + **KD** + intent in one call, and
  `keyword_ideas` expands a seed into a scored list — a full DataForSEO keyword workflow (cross-check the
  volume against Ahrefs; Google Ads volume is often higher and more current).
- **opportunity-map / competitor-analysis:** `ranked_keywords` pulls every keyword a rival ranks for,
  `domain_intersection` surfaces the keyword gap between two domains, and `competitors_domain` discovers
  who competes; `backlinks_bulk_ranks` scores a whole competitor list's authority in one cheap call.
- **geo-audit (cross-engine):** `llm_query` asks ChatGPT / Gemini / Perplexity / Claude a prompt and
  returns whether the client is mentioned and who the model cites — the per-prompt, cross-engine read
  that complements Google AI Overview (this skill), the Perplexity probe (web-research), and Brand Radar.

## Workflow (PERCEIVE -> ANALYZE -> VALIDATE -> ACT)
1. **PERCEIVE.** Run the AIO tracker over the client's money keywords in their market. Note trigger rate
   and who Google's AI cites.
2. **ANALYZE.** For each triggered AIO where the client is absent, read the cited domains: that is the
   set to get mentioned on (often Reddit, review sites, industry portals) plus the on-page structure to
   match. Where no AIO triggers, that query is a classic-SERP play, not a GEO one.
3. **VALIDATE.** AI Overviews are volatile and can be personalized/non-deterministic; re-run on a
   cadence and treat a single scan as `confidence: sampled-ai-answer`. Cross-check with the Perplexity
   probe and Brand Radar.
4. **ACT.** Log to `data/ai-citation-log.csv`; the gap (which cited domains to earn mentions on, which
   pages to make answer-first) becomes input to `aeo-content-patterns` and `backlink-analysis`.

## Guardrails
- Budget-aware: each `serp` / `ai_overview` call is ~$0.002. Batch a keyword grid, save raw JSON to
  `data/raw/dataforseo/`, do not re-pull needlessly.
- Google AIO trigger and citations vary by run, location, and personalization; report the date, market,
  and that it is a sampled surface.
- The recipe stays internal; the client-facing output is the finding (are we cited, who is, what to do),
  not this methodology.

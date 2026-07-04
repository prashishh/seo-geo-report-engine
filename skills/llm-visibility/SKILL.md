---
name: llm-visibility
description: >
  Measure whether a brand is mentioned or cited across every major AI answer engine at once, for a grid
  of money queries, and see who is named instead. One scan hits Google AI Overview + ChatGPT + Gemini +
  Perplexity + Claude (all via DataForSEO) and reports a per-query "present in N of M engines" score.
  Use when asked to "check if we show up in ChatGPT / Gemini / Claude / Perplexity", "are we mentioned
  by AI", "run an AI-visibility scan", "who does AI recommend for <topic>", "track AI mentions across
  engines", "GEO baseline", "cited in AI answers", or "which competitors do the AI models name". This is
  the operational tracker that unifies serp-intel (Google AIO), web-research (Perplexity), and geo-audit
  (Brand Radar) into one cross-engine measurement, logged over time.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# llm-visibility

The operational core of GEO measurement. For a client's money-query grid it asks **all five answer
engines the same questions** and reports, per query and per engine: is the brand **mentioned** (named in
the answer), is it **cited** (its domain in the sources), and who is named/cited instead. It rolls up to
the durable-visibility bar: **present in >=3 of 5 engines**. Powered by DataForSEO (Codex-safe, no MCP).

Two distinct signals, because engines behave differently:
- **Mention** — the model names the brand in prose ("...HubSpot, Zoho..."). This is the primary signal
  for chat models (ChatGPT, Claude), which name brands from knowledge without linking.
- **Citation** — the brand's domain appears in the answer's source list. This is the primary signal for
  Google AI Overview, Perplexity, and Gemini (web-search), which attach sources.

## Engines (all through the one DataForSEO account)
`google_aio` (Google AI Overview, citation-based) · `perplexity` (sonar, always cites) · `chatgpt`
(gpt-4o-mini, knowledge-mention) · `gemini` (2.5-flash, cites) · `claude` (haiku-4-5, knowledge-mention).
Swap models or force web search on all engines with flags. AIO is keyword/SERP-based; the four LLMs take
the query as a natural-language prompt, so phrase the grid as real questions.

## Tool
```
python3 tools/geo/llm_visibility.py --project <slug> --location <code> \
    --brand "Brand Name" alias brand.com \
    --prompts "natural question 1" "natural question 2" ... \
    --date 2026-07-01 \
    --out projects/<slug>/data/raw/dataforseo/llm-visibility-<date>.json
```
Defaults to `client.yml` domain + target_keywords + competitors when flags are omitted. Competitors are
pulled from `client.yml` and matched by name + domain, so the scan reports who the engines name instead.
Every run appends normalized rows to `projects/<slug>/data/ai-visibility.csv` (date, engine, prompt,
mentioned, cited, competitors, cited_domains) so the dashboard can trend "cited in N of M" over time.
Options: `--engines google_aio perplexity chatgpt gemini claude` (subset), `--web-search-all`,
`--no-log`. Cost: a 6-query x 5-engine scan is roughly $0.25-0.30 (Perplexity + Gemini web search are
the bulk; chat/claude knowledge answers are near-free).

## Workflow (PERCEIVE -> ANALYZE -> VALIDATE -> ACT)
1. **PERCEIVE.** Run the grid over the client's money queries in their market. Read the per-query score
   and the competitor-frequency tally.
2. **ANALYZE.** For each engine where the brand is absent, read who is named/cited instead: that is the
   set to displace. A brand named by ChatGPT/Claude but not cited by AIO/Perplexity is a *citation* gap,
   not a *presence* gap, and vice versa, they need different fixes (earn mentions on cited sources vs
   become a known entity). Cross-reference the cited domains with `serp-intel` and `backlink-analysis`.
3. **VALIDATE.** AI answers are volatile, personalized, and non-deterministic. Treat any single scan as
   `confidence: sampled-ai-answer`; re-run on a cadence and watch the trend, not one reading.
4. **ACT.** The gap (which engines, which competitors, which cited sources) becomes input to
   `aeo-content-patterns` (make pages answer-first + citable), `schema-markup`, and `backlink-analysis`
   (earn mentions on the sources the engines lean on). Log every scan for the trend line.

## How it relates to the other GEO skills
- **serp-intel** owns the Google AI Overview surface in depth (PAA, SERP, cited pages); this skill folds
  AIO into the cross-engine roll-up.
- **web-research** is the deep single-engine Perplexity probe with full citations; this skill is the
  broad multi-engine breadth scan.
- **geo-audit** is the brand-level Brand Radar diagnosis (aggregate SoV, foundations gate); this skill is
  the live per-query cross-engine check that Brand Radar cannot do for arbitrary prompts (and it covers
  Claude, which Brand Radar cannot track).

## Brand Radar mode: Share of Voice (our own Brand Radar equivalent)
For a defensible, trackable AI Share of Voice (not a cherry-picked snapshot), run the weighted pipeline:
```
# 1. build a VOLUME-WEIGHTED prompt set (~50-150 real-demand queries, fixes the credibility gap)
python3 tools/geo/prompt_set.py     --project <slug> --location <code> --seeds "..." --limit 120 \
    --out projects/<slug>/data/prompt-set.json
# 2. scan the weighted set across all engines
python3 tools/geo/llm_visibility.py --project <slug> --location <code> --prompt-set projects/<slug>/data/prompt-set.json \
    --out projects/<slug>/data/raw/dataforseo/llm-visibility-<date>.json
# 3. compute Share of Voice (impression = mention x search volume; SoV% = brand / all tracked brands)
python3 tools/geo/sov.py            --project <slug> --scan .../llm-visibility-<date>.json \
    --prompt-set projects/<slug>/data/prompt-set.json --client "Brand Name"
```
`sov.py` reports each brand's blended + per-engine SoV%, the client present-rate per engine, and appends
to `data/sov-history.csv` so the trend (the real proof) shows on the dashboard and in the first-scan
report. This is our Brand-Radar-equivalent: cheaper (single-digit dollars/client), covers Claude, and
does per-prompt attribution Brand Radar cannot. `at-scale option:` DataForSEO `llm_mentions` (connector)
gives mention counts without prompting each engine, but carries a $100/mo minimum.

**Honesty rule (bake into any deliverable):** SoV is scoped to the tracked demand set; state the sample
size, and treat any single scan as noise, the value is the trend. See `first-scan-report` for the
client-facing packaging.

## Guardrails
- Budget-aware: batch a grid, save the raw JSON, do not re-pull needlessly. Report the date and market.
- The recipe stays internal. Client-facing output is the finding (are we named/cited, by which engines,
  who wins instead, what to do), never this methodology or the scoring.

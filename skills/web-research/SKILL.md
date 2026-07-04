---
name: web-research
description: >
  Run live, cited web research via OpenRouter's Perplexity Sonar models when static WebFetch/
  WebSearch can't synthesize across enough sources, or when the question is literally "what does
  AI currently say about X" (a live GEO/AI-citation signal). Use when asked to "do deep research
  on <topic>", "find real customer quotes / reviews online", "verify competitor facts with
  sources", "what does ChatGPT/Perplexity say about <brand>", "probe AI citations", "check if we
  get mentioned by AI", or when a research task needs multi-hop synthesis with a real citation
  list rather than a single page fetch. Two modes: deep multi-step research (expensive, thorough)
  and cheap single-shot AI-citation probing (near-free, safe to run at volume). Feeds
  customer-research, competitor-analysis, geo-audit, and ai-citation-sprint.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# web-research

Live, cited web research via OpenRouter (Perplexity's Sonar model family), for the moments
static `WebFetch`/`WebSearch` aren't enough: multi-hop synthesis across many sources, or
literally asking an AI engine what it currently says about a brand or topic.

## Why this exists
`WebFetch` reads one page; `WebSearch` lists results. Neither *synthesizes across sources with
citations*, and neither answers "what does an AI answer engine say about us right now" — which
is itself a live GEO signal, complementary to Ahrefs Brand Radar (and useful when Brand Radar or
the Ahrefs MCP is unavailable, as happens with limited API budgets).

## Tool
Stdlib, no install. `tools/connectors/openrouter.py`:

```bash
python3 tools/connectors/openrouter.py probe "What platform do hotels use for cashless tipping?"
python3 tools/connectors/openrouter.py deep "voice of customer for hotel digital tipping products"
```

Or from Python: `from connectors.openrouter import deep_research, probe`. Both return
`{"answer", "sources": [{"url","title","date"}], "citations": [url, ...], "model", "usage"}` —
the connector normalizes OpenRouter's actual response shape (citations arrive as
`message.annotations[].url_citation`, not the top-level `citations` field Perplexity's own docs
describe) so callers don't need to know which shape came back. **Needs `OPENROUTER_API_KEY`** in
`config/secrets.env` (get one at openrouter.ai/keys; pay-as-you-go, no separate Perplexity account).

## Two modes — pick deliberately, cost differs ~50-100x

1. **Deep research** (`deep_research()`, `perplexity/sonar-deep-research`, ~$0.04-0.05/call).
   An autonomous multi-step search-and-reason agent. Use for:
   - Voice-of-customer mining (`customer-research`) when Reddit/forums block direct crawling —
     ask it to synthesize what people say, with sources, instead of fetching threads one by one.
   - Competitor fact-gathering (`competitor-analysis`, `comparison-pages`) — verified, sourced
     facts about a rival instead of manually fetching each vendor page.
   - Market sizing statistics (`market-opportunity`) that need a cited, current figure.

2. **Citation probe** (`probe()`, `perplexity/sonar`, a fraction of a cent/call). A single
   always-on grounded query. Use for:
   - **GEO/AI-citation probing** (`geo-audit`, `ai-citation-sprint`) — ask the exact prompt a real
     user might ask ("what's the best digital tipping platform for hotels?", "does Brand X
     increase staff retention?") and log whether the brand is mentioned, its position, and which
     sources got cited instead. Cheap enough to run the *whole* prompt grid (see
     `research/tracking-scaffold.md` pattern) on a schedule.
   - Fast fact-checks that don't need the full deep-research agent.

## Workflow (PERCEIVE → ANALYZE → VALIDATE → ACT)
1. **PERCEIVE.** Pick the mode by cost-to-value: probe for anything you'd ask in one sentence and
   trust a single grounded answer; deep research for anything needing multi-source synthesis.
2. **ANALYZE.** Read `sources` as real evidence, not the `answer` text alone —
   a claim without a citation is a hypothesis, not a finding. Note which domains keep getting
   cited (that's often the actual competitive set for AI answers, which may differ from Google's).
3. **VALIDATE.** Treat every result as `confidence: sampled-ai-answer` (per
   `knowledge/seo-geo-tooling-landscape.md`'s confidence taxonomy) — a single AI response is a
   sample, not ground truth. For anything load-bearing, cross-check against Ahrefs Brand Radar,
   GSC/GA4, or a second probe on a different day.
4. **ACT.** Write findings into the active project:
   - Deep-research output → `research/` as sourced notes (cite the returned URLs).
   - Citation probes → append to `data/ai-citation-log.csv` (date, engine=`perplexity-sonar`,
     prompt, brand_cited bool, position, competing_sources, notes) — the same log shape
     `ai-citation-sprint` already tracks Brand Radar snapshots in, so the two sources sit side by
     side over time.

## Guardrails
- This is one signal among several (per `seo-data-router`) — never the only AI-visibility source
  if Ahrefs Brand Radar or a dedicated AI-visibility tool is available.
- Don't run deep-research in a loop for things a cheap probe or owned data (GSC/GA4) already
  answers — cost discipline matters, deep-research is ~50-100x the price of a probe.
- Log the model + date on everything; a Sonar answer is a snapshot, not a permanent fact.

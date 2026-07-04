---
name: geo-audit
description: >
  Audit a brand's visibility, citation, and accuracy inside AI search (ChatGPT, Perplexity,
  Google AI Overviews / AI Mode, Claude, Copilot) using Ahrefs Brand Radar as the measurement
  engine, then produce a prioritized GEO fix list. Use when asked to "run a GEO audit", check
  "AI search visibility", ask "are we cited by ChatGPT / Perplexity / AI Overviews", measure
  "share of voice in AI" or "AI share of voice", set up or check an "llms.txt", or "optimize for
  AI search / SGE / generative engines". Also fires on "why doesn't AI mention us", "what does
  ChatGPT say about us", "who does AI cite for <topic>", and "AI crawler / GPTBot access".
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# geo-audit

Measures how a brand shows up in AI answers and turns the gaps into a falsifiable fix list. The
engine is **Ahrefs Brand Radar** (see `knowledge/ahrefs-mcp-map.md`); the methodology is
`playbooks/geo-playbook.md`. House method: **PERCEIVE → ANALYZE → VALIDATE → ACT**.
Data priority everywhere: **Ahrefs MCP > CLI connectors > web** spot-checks.

## Inputs
- `projects/<client>/client.yml` — domain, competitors, target keywords, market.
  Brand Radar ids come from `ahrefs.brand_radar_report_id` (and `ahrefs.project_id`).
- Existing research in `projects/<client>/research/`.

If `brand_radar_report_id` is missing, list reports with `management-brand-radar-reports` and the
prompts with `management-brand-radar-prompts`, pick the right one, and write the id into `client.yml`.

## Workflow

### 1. PERCEIVE — measure current AI visibility (Brand Radar)
Always `doc` a tool before first use. Pull, for the client + each competitor:
- `brand-radar-sov-overview` + `brand-radar-sov-history` — AI **share of voice** now and its trend.
- `brand-radar-mentions-overview` + `brand-radar-mentions-history` — mention volume + direction.
- `brand-radar-impressions-overview` — AI impression scale for the topic set.
- `brand-radar-ai-responses` + `brand-radar-ai-responses-entities` — the **actual answer text** and the
  entities co-cited with the brand (surfaces wrong facts and missing associations).
- `brand-radar-cited-domains` + `brand-radar-cited-pages` — **who AI cites** for the topic (the sources
  to get mentioned on or out-cite).
- `site-explorer-ai-responses-count` — how often the client's domain appears in AI answers vs rivals.

From the same Brand Radar pulls, derive two **first-class citation signals** per engine:
- **AI-citation frequency** — how often the brand is cited per engine (from `ai-responses` /
  `cited-pages`); a brand mentioned but never cited is a citability gap, not a presence gap.
- **Cross-engine citation** — count distinct engines that cite the brand; treat **cited by ≥3 engines**
  as the durable-visibility bar (single-engine citation is fragile to one model's ranking change).

If a response carries `render_with`, call the named render tool. Save raw pulls under
`projects/<client>/research/` (e.g. `geo-brand-radar/`).

**Live cross-check (optional but cheap).** Brand Radar is a snapshot with its own refresh cadence,
and it may be unavailable. Two live engines supplement it, both logged to `data/ai-citation-log.csv`
as `confidence: sampled-ai-answer`, never replacements:
- **Perplexity** via the `web-research` probe (`perplexity/sonar`, a fraction of a cent per call).
- **Google AI Overview** via the `serp-intel` skill (`tools/geo/ai_visibility.py`, DataForSEO) — the
  most important AI-search surface and the one Brand Radar and Perplexity do not cover: for each money
  keyword it reports whether an AI Overview triggers, who Google's AI cites, and whether the client is
  in it. Run all three for a true multi-engine "cited in N of the engines" read.

### 2. ANALYZE — score against the 5 GEO pillars
Score the brand and top cornerstone pages on each pillar from `playbooks/geo-playbook.md`
(citability 25%, structural readability 20%, multi-modal 15%, authority/brand 20%, technical 20%):
- **Citability** — self-contained, frontloaded answers; **citable passages ~134–167 words**; attributed
  claims; "X is…" definitions. Pull live page bodies with `site-audit-page-content` / WebFetch.
- **Structural readability** — question-based H2/H3, tables, FAQ, lists.
- **Multi-modal** — images, diagrams, embedded YouTube, tools.
- **Authority & brand** — named author + credentials, publish/updated dates, primary sources, freshness,
  and **entity presence** on Wikipedia / Reddit / YouTube / LinkedIn.
- **Technical** — SSR/static HTML, schema, robots/llms.txt, crawler access.

**Anchor insight:** brand **mentions correlate ~3x more with AI visibility than backlinks** (Ahrefs, Dec
2025) — strongest on **YouTube, Reddit, Wikipedia**. Weight earned-mention gaps accordingly; don't
recommend a link-only program.

### 2b. FOUNDATIONS GATE — prerequisite, before any citation fix
Citability work is wasted if AI engines can't crawl, parse, or correctly resolve the brand. **Run this
gate first; if any item below fails, fix it before recommending content/citation changes.**
- **AI-crawler access (robots.txt)** — fetch the live `robots.txt` and confirm **GPTBot, OAI-SearchBot,
  ClaudeBot, PerplexityBot, Google-Extended** (and the answer/search UAs) are not `Disallow`-ed. Map each
  UA against `knowledge/ai-crawlers.md`. **Never block AI crawlers by default** — blocking removes the
  brand from AI-search visibility. *How we'd know it failed:* a blocked answer/search UA still appears
  Disallowed after the fix ships, or `site-explorer-ai-responses-count` stays flat.
- **llms.txt presence/quality** — fetch `https://<domain>/llms.txt`; record present/absent and whether it
  lists canonical pages (no current citation weight — transparency only; don't oversell).
- **Parsability** — confirm answer content is in server HTML (not JS-only) so crawlers can read it.
- **Resolution / disambiguation test** — for each engine (`ai-responses`), check it resolves the brand
  to the **right entity** and does not confuse it with a competitor or unrelated namesake. *How we'd know
  it failed:* an engine's answer attributes the brand's facts/products to a rival. Misresolution is a
  P0 — fix entity signals (Wikipedia/schema sameAs) before chasing share of voice.
- **Featured-snippet / AI-answer ownership** — for the brand's priority questions, check whether the
  brand **owns the AI answer / featured snippet** or a competitor/aggregator does (from `cited-pages` +
  live SERP). Not owning it is the gap to close on those queries.

### 3. VALIDATE — technical & accessibility checks
- **AI-crawler access** — fetch the live `robots.txt`; confirm the answer/search crawlers
  (OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, Claude-User, Bingbot, Googlebot) are
  **allowed**. Map each UA against `knowledge/ai-crawlers.md`. Flag any that block citation-driving bots.
- **llms.txt** — fetch `https://<domain>/llms.txt`; record present/absent and whether it lists canonical
  pages. Note it has **no current citation weight** (transparency only) — don't oversell it.
- **SSR / structured data** — confirm answer content is in the server HTML (not JS-only) and that
  Article/FAQPage/HowTo/Organization schema is present.

### 4. ACT — write the deliverable
Compose **`projects/<client>/research/GEO-ANALYSIS.md`** with:
1. **AI share of voice + trend** — client SoV now and over time (Brand Radar).
2. **Competitor SoV gap** — client vs each competitor; where the headroom is.
3. **What AI says about the brand** — summary of `ai-responses` + co-cited entities; flag inaccuracies.
4. **Cited domains/pages we're missing** — the sources AI leans on that don't mention us (mention targets).
5. **Citability score** — per-pillar (0–100) + weighted overall, with the weakest passages quoted.
6. **Crawler-access status** — per-crawler allow/block table (ref `knowledge/ai-crawlers.md`).
7. **llms.txt status** — present/absent + a ready-to-ship draft if missing.
8. **Foundations gate result** — crawler-access, parsability, **resolution/disambiguation** (does each
   engine resolve the brand correctly), and **AI-answer/featured-snippet ownership** per priority query;
   any failure here is a blocker listed above the content fixes.
9. **Citation signals** — **AI-citation frequency** per engine and **cross-engine citation count**
   (flag if cited by <3 engines).
10. **Top 5 prioritized fixes** — each **falsifiable**:
   - *Observation* (what the data shows) · *Depends on* (the assumption) ·
     *How we'd know it failed* (kill condition) · **Leading indicator** (the Brand Radar metric to watch,
     e.g. mentions SoV up within 6 weeks).

## Notes
- Re-run PERCEIVE every 2–4 weeks; SoV/mention movement is the proof the fixes worked.
- Pair with `competitor-analysis` for the organic picture and `schema-markup` to ship structured data.
- Absolute dates only (today is 2026-06-23). Don't put client data in the parent framework.

# Agency product landscape & wow-factor roadmap

Last reviewed: 2026-07-01. Companion to `seo-geo-tooling-landscape.md` (which covers raw-data
vendors). This doc covers the **product / deliverable / workflow** layer: what leading agency and
SEO/GEO products offer as their standout features, and what to buy, integrate, build, or skip to make
`seo-geo-report-engine` more powerful with a genuine wow factor. Sourced from a 54-product web-verified scan.

## Executive take

We already have a real, working end-to-end stack (28+ skills, live-data connectors, AI-citation
probe, dashboard, branded PDFs) and four moats the managed products cannot copy: **falsifiability,
portability, BYOK/stdlib, and brain-not-builder**. The gaps are not in strategy; they are in a few
**legible, visible wow features** the market has standardized on: a live "is this good enough to ship"
content score, a persistent live client dashboard, and AI-crawler analytics. Most are cheap to build
on what we have; two are worth a small paid API; one classic wow (white-label reporting) we should get
for near-zero cost via Looker Studio rather than by becoming a SaaS company.

## Our current edges (double down on these)

- **Falsifiability as a product.** Every recommendation ships with observation + dependency + "how
  we'd know it failed." No managed AEO/GEO product (AEO Engine, GenOptima, iPullRank) gives the client
  an auditable, keep-forever artifact; they lock deliverables inside their service. Our sharpest moat.
- **Portability.** The brief, schema, llms.txt, and scorecards are the client's forever, CMS- and
  vendor-agnostic. Managed shops rent the outcome; the client keeps nothing.
- **Stdlib + BYOK, Codex-safe.** Our OpenRouter/Anthropic connectors already do what NeuronWriter
  charges for and Jasper gates behind Enterprise. Zero pip, zero lock-in.
- **Live AI-citation probe already built** (web-research / Perplexity Sonar): covers Claude and Grok,
  which Ahrefs Brand Radar does not track natively, and runs near-free at volume. We can VERIFY
  citation lift, the prerequisite for outcome-based pricing.
- **Orchestration we already own** (skill-navigator + 29 chained skills) is our answer to Surfer's
  Cruise Mode / AirOps Grids, without a purchase.

## The wow bets (ranked by leverage-to-cost)

1. **Live client dashboard via Looker Studio + BigQuery** (fills our #1 gap: no persistent live
   portal). Publish a Looker Studio Community Connector (Apps Script) over our snapshotted KPI/rank/GEO
   CSVs, or load them into the client's own BigQuery. Always-fresh, self-serve, white-label dashboard
   at ~$0 vendor cost; the client owns the Google surface, so it stays brain-not-builder. White-label
   reporting is the classic agency retention + wow driver, and this is the only way to get it without
   running multi-tenant infra. Effort: medium. **Highest leverage in the scan.**
2. **Query fan-out engine** in keyword-research + aeo-content-patterns. Use our existing Perplexity
   Sonar connector (no new vendor) to expand a seed prompt into the synthetic sub-questions an LLM
   decomposes it into, then feed those as required passages, scored per sub-query. This is iPullRank's
   most sophisticated methodology (a $15k/mo service) for the cost of a prompt wrapper, and it maps to
   how AI answers are actually assembled. Effort: low-medium.
3. **Term/entity-coverage scorer with one legible A-F / 0-100 ship-gate grade**, wired into
   content-brief + human-seo-editor. Matches Surfer's live score, Clearscope's grade, and MarketMuse
   Content Score in one build. Needs the Serper connector first. Effort: medium.
4. **Agent Experience bundle + AI-crawler log analyzer.** Extend aeo-content-patterns + schema-markup
   to emit a deployable answer-first + JSON-LD + llms.txt bundle, and ship a stdlib log-parser that
   classifies GPTBot/PerplexityBot/ClaudeBot hits from the client's server/CDN logs against the
   verified crawler ranges we already list in `knowledge/ai-crawlers.md`. Turns "here's a rewrite spec"
   into "here's a deployable, measurable agent experience." Genuinely novel; few tools have it.
5. **Outcome-priced citation-lift scorecard** add-on in proposal-builder. We already own the
   measurement half (Sonar probe + Brand Radar) to verify before/after cited-appearance rate, so we
   can credibly offer partial performance pricing and a "3+ of 4 engines in 90 days, here's how we'd
   know it failed" frame that a flat retainer cannot. Pricing innovation is the hardest-to-copy moat.
   Effort: low (template + KPI-tree upgrade, no new tooling).

## Integrate now (cheap, API-first, gate behind a key like our other connectors)

> **Decision (2026-07-01): DataForSEO is the committed data backbone, so the SERP-data rows below are
> superseded.** DataForSEO covers SERP, keyword data, backlinks, OnPage crawl, and AI Overviews in one
> API, which makes **Serper.dev and SerpApi redundant** (drop both) and **Frase unnecessary** (we build
> the content score on DataForSEO's SERP data ourselves). The rows kept below as genuinely additive are
> the FREE delivery/dashboard ones (Slack, Google Sheets -> Looker Studio, ECharts) and, only if a live
> AI-citation history product is wanted, Otterly. For deep technical crawls, **Screaming Frog** (local,
> ~£259/yr) complements DataForSEO OnPage; **skip SE Ranking** (its data duplicates DataForSEO and its
> white-label portal duplicates the dashboard we are building). The de-confused stack: DataForSEO +
> Screaming Frog + Ahrefs (while held) + our own framework. See `seo-geo-tooling-landscape.md`.

| Tool | Cost | What it unlocks | Why integrate |
|---|---|---|---|
| **Serper.dev** (Google SERP API) | $0.30-1 / 1k queries | live organic/PAA/related/knowledge-graph JSON | Highest-ROI: live SERP truth for content-brief, competitor-analysis, comparison-pages, keyword-research + a cheap Ahrefs-independent rank source. Codex-safe (MCP is not). `tools/connectors/serper.py`. |
| **SerpApi** (AI Overview endpoint) | $25/mo, 250 free | the literal Google AI Overview text + cited source URLs | Gives geo-audit a screenshot-able "here's who Google's AI cites for your money keyword, and whether you're in it." Buy not build (AIO parsing is a moving target); call selectively, pair Serper for volume. |
| **Frase API** | $39-49/mo, on every plan | callable optimization score + SERP-with-AIO-sources + question research | The one content-optimization product with a cheap developer API (X-API-KEY, 50+ REST endpoints + webhooks). Shortcut to the live-content-score we lack, without maintaining a scraper. |
| **Otterly.AI** | $189/mo, 2k API + MCP | longitudinal multi-engine citation + position history | Cheapest way to add citation trend lines behind geo-audit; its MCP slots into our MCP-first model like Brand Radar. Pilot vs Rankscale ($99) for engine breadth. |
| **Google Cloud Natural Language API** | 5k units/mo free, then $0.001 | entity-coverage gap ("competitors cover these 12 entities you omit") | Nearly free at audit volumes; a falsifiable content recommendation for content-brief / competitor-analysis. |
| **Webflow + Framer CMS APIs** | client pays | optional publish adapter (draft mode) INTO the client's CMS | The missing last mile of brain-not-builder, behind our pre-handoff QA gate; client owns publish approval. |
| **Slack + Google Sheets + Notion** | free | competitor-watch alerts, report digests, live data out | Distribution/wow layer. Slack webhook first (biggest perceived-liveness win); Sheets also bootstraps the Looker Studio path. |
| **Apache ECharts** | free, Apache-2.0, CDN | interactive rank/SoV/KPI charts on the live dashboard | Keep pure-SVG for print PDFs; use ECharts for hover/zoom/drill-down on the dashboard only. Zero cost wow bump. |

## Build ourselves (on what we have)

The scorer + A-F grade, a named "Personalized Difficulty" metric (MarketMuse: client DR + existing
cluster coverage + competitor overlap, vs generic KD) in keyword-research, the query fan-out step, the
AI-crawler log analyzer, the Agent Experience bundle, a blended GEO score + page citation-likelihood
heuristic, a 100+-signal E-E-A-T checklist in technical-seo-audit, a bulk content-refresh mode,
cluster-as-a-set with the internal-link mesh generated alongside pages + a live-data column per row
(anti-thin-content), a KPI threshold-alert layer on our history CSVs (fires a Slack digest when a
client slips), sentiment + auto-proposed starter prompts on the citation probe, and citation-probability
scoring for PR/link targets in backlink-analysis.

## Buy / partner (don't build)

- **SE Ranking Agency Pack** (~$69/mo add-on) — best price-to-wow reporting portal; white-label on
  every plan + API + MCP + cheap AI-Overview/ChatGPT/Perplexity tracker. Doubles as a cheaper fallback
  data source in seo-data-router. Recommended premium reporting fallback.
- **AgencyAnalytics** (~$20/client/mo) — turnkey branded portal + branded mobile app, when a client
  demands a hosted login portal.
- **Profound** (enterprise, ~$2-5k+/mo) — the benchmark to beat, not embed; resell only for enterprise
  clients needing SOC 2 + Agent Analytics at scale.
- **Trakkr.ai** (~$79-500/mo) — closest agency-in-a-box; also the source of the Reddit-intelligence gap
  we should build against.
- **SerpApi small tier** — buy (not build) specifically for AI Overview capture.

## Positioning vs managed AEO/GEO products (AEO Engine, GenOptima, iPullRank)

**Decision (2026-07-01): we operate like AEOEngine. The recipe stays ours.** The methodology, the
playbooks (`opportunity-capture`, `geo-playbook`, etc.), the skills, the scoring, and the process are
**internal IP and the moat, not shared.** Clients do not want the recipe; they want results. What we
share with the client is the **achievement**: the live data, the dashboard, the KPIs and metrics, the
measured outcome, and the deliverable **outputs** they act on (the page-ready artifacts, the brief, the
plan). We keep the *how*; we prove the *what*.

Our edge over the managed shops is therefore NOT transparency-of-method (an earlier draft had this
backwards). It is: **(1) Verifiable results** — every outcome is measured with a falsifiable
before/after we own (Sonar probe + Brand Radar), so the client trusts the number without us exposing
the engine. **(2) A real end-to-end machine already built**, not a roadmap. **(3) Brain-not-builder
handoff** — the client's team ships and owns the deployed output while we keep the engine, so we avoid
the quality/liability traps the done-for-you shops carry (auto-link-exchange, autopilot publishing,
uninspectable agent cloaking). **(4) Outcome-priced options** backed by the measurement we own.
Concrete moves: copy AEO Engine's transparent tier-scoping and fixed-scope pricing into
proposal-builder, add the citation-lift scorecard as a client-facing RESULTS artifact, and keep the
methodology behind the curtain.

Internal vs client-facing, concretely: **internal (never shared)** = `playbooks/`, the skill/tooling
recipe, scoring formulas, raw working notes. **Client-facing (shared)** = the dashboard, KPI/metric
snapshots, the results scorecard, and the deliverable outputs (pages, briefs, the plan they execute).

## The white-label reporting recommendation (two tiers)

**Tier 1 (default, build):** Looker Studio Community Connector (Apps Script) over our snapshotted CSVs,
or load them into the client's own BigQuery. Free surface, client-owned, always-fresh. Bootstrap via
our Google Sheets output first. Pair with the ECharts upgrade to our own dashboard and a stdlib KPI
threshold-alert that fires a Slack digest when a client KPI slips (that alerting + liveness is the
retention wow, all free). Disclose Looker limits: no row-level security, no native alerting (we supply
it), flaky blending past 3-4 sources (mitigate via BigQuery). **Tier 2 (resell, don't build):** SE
Ranking Agency Pack or AgencyAnalytics for clients who demand a hosted branded login portal. Net: the
classic agency reporting wow at near-zero cost and zero lock-in, without becoming a SaaS company.

## Source note
54 products scanned 2026-07-01 across content-optimization, GEO/AI-visibility, programmatic/automation,
all-in-one + reporting, managed AEO/GEO, and buyable integrations. Full per-product detail (wow
feature, API, pricing, verdict, URL) is in the workflow archive; the highest-signal items are surfaced
above. Verify pricing/API tiers before committing; this layer changes fast.

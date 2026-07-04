# SEO / GEO Tooling Stack

Last reviewed: 2026-07-01

What we actually use, and the decisions behind it. Only tools in our stack or explicitly on the buy
list are documented here. Providers we evaluated and rejected are named once (so they are not
re-litigated), never detailed.

## Our stack

- **DataForSEO** — the committed pay-as-you-go data backbone. Live SERP (incl. Google AI Overview + PAA),
  keyword volume + KD + intent + ideas, ranked keywords, keyword gap, backlinks (+ link gap, spam,
  competitors), OnPage crawl, domain + traffic intelligence (`domain_rank_overview`, `bulk_traffic_estimation`,
  `domain_technologies`, `top_pages`), reviews / Google Business / web mentions, and direct LLM querying of
  ChatGPT / Gemini / Perplexity / Claude. Connector: `tools/connectors/dataforseo.py`. Because its SERP
  returns the AI Overview block and we score content on its SERP data ourselves, single-purpose SERP APIs
  (Serper, SerpApi) and content-score APIs (Frase) are **redundant — do not add them**.
- **Ahrefs** — the trusted cross-check (DR / KD, backlink depth) and **Brand Radar** (cross-engine AI SoV)
  while held. Connector: `tools/connectors/ahrefs.py`; MCP when connected.
- **Screaming Frog** (+ Log File Analyser) — deep local technical crawl (JS render diff, custom extraction,
  forensic audits) + AI-bot log evidence. A different category from the APIs, sits under both.
- **OpenRouter** (Perplexity Sonar) — live cited research + cheap AI-citation probe. `tools/connectors/openrouter.py`.
- **Apify** — public social-profile scraping for competitor social presence. `tools/connectors/apify.py`
  (`APIFY_API_TOKEN`), powering `tools/seo/social_footprint.py`.
- **Free owned data** — GSC, GA4, PageSpeed / CrUX for ground truth (owned metrics + real-user Core Web Vitals).
- **Our own framework** — strategy + scoring + the dashboard + HTML→PDF reports, and the multi-engine
  AI-visibility (`llm_visibility` + `sov`), multi-source authority (`authority.py`), and opportunity/greenfield
  engines (`competitor_gap` + `opportunity_score`). This is the IP; it stays internal.

**Authority (domain strength)** is read multi-source and reconciled (`tools/seo/authority.py`): DataForSEO
`rank` + Ahrefs DR always; add the **FREE Open PageRank API** (`OPENPAGERANK_API_KEY`) and optional **Moz DA**
(`MOZ_TOKEN`) for more sources. Report the consensus + the spread; a big spread means the sources disagree,
so investigate before quoting.

**Confidence labels** on every data snapshot: `owned-data` / `live-serp` / `provider-estimate` /
`sampled-ai-answer` / `manual-review`. Client-facing reports never name the provider tool (say "live search
data", "public social profile"); keep vendor / cost / failure traces internal (BUILD-STATUS or research).

**Evaluated and rejected** (do not re-add without a new reason): Semrush (adds ~$500/mo, beats Ahrefs on
nothing here), SE Ranking (data independence from DataForSEO unverified; its portal duplicates our
dashboard), Serpstat, Sitebulb (no API / CLI), Moz as a *backbone* (fine as a $20 DA line only), and the
enterprise AI-visibility suites (Profound / Otterly / Scrunch / Peec) — we use DataForSEO `llm_query` + our
own Brand-Radar MVP instead. Similarweb API (enterprise-gated, no PAYG). Details on the money side below.

## Two-System Stack Decision (2026-07-01) — internal recipe, not client-facing

The standing stack is **two data systems that both complement AND cross-check, plus one local crawler**:
**DataForSEO + Ahrefs** (we hold both keys, nothing new to buy for the backbone) **+ Screaming Frog**. They
cross-check on the metric that matters most to defend, backlinks/authority, because Ahrefs runs its own
index (~35T live links) independent of DataForSEO's (~2.0T live), so divergence is a real signal.

**Source-of-truth map** (which system is authoritative per metric):

| Metric | Source of truth | Cross-check |
|---|---|---|
| Search volume | DataForSEO (cheap backbone) | Ahrefs = directional 2nd opinion; GSC/Keyword Planner tiebreaker |
| Keyword difficulty (KD) | **Ahrefs** (the DR/KD clients + outreach vendors recognize) | DataForSEO KD, flag big divergence |
| Backlinks / referring domains / authority | **Ahrefs** (larger, independent, faster-refreshed; DR/UR currency) | DataForSEO backlinks |
| Rankings / SERP positions | DataForSEO (cheap live pulls incl. AI Overview) | Ahrefs Rank Tracker; GSC tiebreaker |
| AI visibility / SoV | Split: DataForSEO (per-prompt LLM + live AIO scrape, incl. Claude/Grok) + Ahrefs Brand Radar (aggregated 6-engine SoV) | each other |
| Technical / on-page crawl | DataForSEO OnPage (scriptable) + Screaming Frog (deep/JS/log-file) | each other, page-level |

**Cross-check rules** (when the two disagree): backlinks — trust Ahrefs, but compare live/fresh subsets and
referring-domain counts (not raw total-link headlines, which mix historical), and check DR-vs-Domain-Rank by
RANK ORDER not absolute number; divergence >~25-30% on ref domains, inspect manually. Volume — triangulation
only (both blend clickstream): agree within ~20% = confident, diverge >~30-40% = pull GSC before betting a
page. KD — put Ahrefs KD in the deliverable; if DataForSEO KD differs >~15 points, compare relative order and
re-inspect the SERP. Overriding principle: the disagreement itself is the signal — lower confidence and reach
for a third anchor (GSC, manual SERP), never default to the more flattering number.

**Screaming Frog is NOT the second API** — it is a local technical crawler that sits UNDER both. Buy it
(£199/yr) for JS render-vs-raw diff, custom XPath/CSS/regex extraction, and forensic audits on staging/
pre-launch sites; add its **Log File Analyser** (£99/yr) for GEO work: ground-truth of whether GPTBot/
ClaudeBot/PerplexityBot actually reach client pages (v7.0 adds AI-bot anti-spoof + "All AI Bots" grouping),
evidence no API provides.

**Buy/keep now:** keep DataForSEO PAYG; keep Ahrefs on **Lite ($129/mo) or higher** (the $29 Starter tier has
NO API; Lite gives ~100k API units/mo, 100 rows/request — verify in-account, keep bulk scraping on DataForSEO).
Brand Radar is a paid **add-on** (~$699/mo all-6-engine), not included in Lite — treat it as a per-engagement
pass-through only; for everyday AI probing use DataForSEO `llm_query` + our `web-research` skill (cents/probe,
and they cover Claude/Grok which Brand Radar cannot). Moz Links API ($20/mo = 3,000 DA lookups) only if you
want the recognized DA automated; otherwise Open PageRank (free) covers bulk internal authority.

## Social-Media Competitor Intelligence (2026-07-01) — internal recipe

**The hard truth:** official platform APIs mostly return only YOUR OWN accounts. For COMPETITOR social data
(the point of a gap audit), the split is:

- **Free + usable for competitor data:** **YouTube Data API v3** (free key, any public channel: subscribers/
  views/per-video engagement; 10k units/day; resolve channel IDs once, poll `channels.list` at 1 unit),
  **Bluesky AT Protocol** (zero auth, zero cost, `getProfile` followers/posts + per-post engagement for any
  handle), **Instagram Business Discovery** (free via your own Meta app + IG business account + App Review:
  competitor followers + per-post like/comment/view counts).
- **Metered but cheap:** **X/Twitter API v2** (~$0.01/read; a handful of competitors = single-digit $).
- **Closed to a for-profit agency:** TikTok Research API, LinkedIn API, Pinterest competitor data, Meta
  Content Library. Do NOT build a deliverable on these. **Reddit:** free for competitor MENTIONS / SoV only.

**For platforms official APIs don't cover (TikTok, deeper IG, LinkedIn) → PAYG scrapers:** **Apify** (top
pick, ~$0.01/profile, free $5/mo credits, any public handle, `APIFY_TOKEN`), ScrapeCreators ($10, credits
never expire), Bright Data (free 5k rows/mo then $1.50/1k). **Turnkey buy:** Metricool (FREE tier = 5
competitor profiles), Socialinsider (~$82/mo, unlimited competitors). **Listening/SoV:** Awario (~$29/mo, API).

**Buildable (partly built):** `tools/seo/social_footprint.py` reads competitor handles from `client.yml` and
snapshots public numbers (followers, cadence, engagement/post) via YouTube + Bluesky (free, direct) + Apify
(PAYG, for IG/TikTok/LinkedIn), for the hook-report social section. Counts are approximate + public-only;
self-snapshot for trends; no rival demographics exist at any price.

## Premium Pitch Data — wow-per-dollar for the first-scan report (2026-07-01)

The goal: data a prospect has never seen in an SEO deck. **Most of the wow is FREE.**

**Free, high wow (the wire list):**
- **Meta Ad Library API** (free Graph `/ads_archive`) — live wall of competitors' actual FB/IG ad creatives
  + (EU/UK) real spend/impression bands. "Your 3 rivals run 14 ads at your buyers this week; you run zero."
  Highest wow-per-dollar. US commercial creatives need a DataForSEO/SerpApi backfill.
- **Google Ads Transparency via existing DataForSEO** (~$2/1k tasks, no new vendor) — every competitor
  Search/Shopping/YouTube/Display creative + run duration + served platforms.
- **HTTP Archive + CrUX** (BigQuery, first 1TB/mo free) — competitor tech stack (Wappalyzer) + real-user
  LCP/INP/CLS. Free near-substitute for BuiltWith (minus the $-spend estimate). Plus **CrUX API** (free).
- **Screenshots: thum.io** (free 1k/mo, no key, one urllib line) + **Microlink `screenshot.overlay`** (free
  50/day, browser-framed) — glossy competitor page teardowns; both pure GET, stdlib-safe.
- **HypeStat** (free, no API) — channel-mix (search/direct/referral/social) for any domain; directional,
  don't brand it. **QuickChart** (free 100k/mo) — Chart.js→SVG via urllib. **OpenCorporates + Wikidata**
  (free/open) — citable legal-entity/HQ/headcount floor.

**Buy first (paid, PAYG):** **PredictLeads** ($0.04/credit, $40 min, 100 free/mo) — competitor hiring
velocity + funding/M&A + tech-stack changes from their own careers/newsroom, refreshed ~36h. The freshest
"never seen this" slide, pennies per competitor. Runner-up if PPC-heavy: **SpyFu Pro+AI $119/mo**.

**Skip:** Similarweb API (enterprise-gated ~$38k, no PAYG; use a $20/mo Apify Similarweb-shape actor for the
hook, never name-drop Similarweb unlicensed), Datos, Pathmatics, Clearbit (HubSpot-only), Cloudflare Radar/
Tranco as "traffic" (rank only). Semrush .Trends / BuiltWith à-la-carte / AdClarity — only once a client funds
that specific slide.

**To wire (priority):** `connectors/meta_ad_library.py` (free), Google Ads Transparency into the DataForSEO
connector, `tools/screenshots/capture.py` (thum.io + Microlink), `connectors/predictleads.py` (PAYG),
`connectors/httparchive_bq.py` + `crux.py`, a QuickChart chart helper.

## Source Links

- DataForSEO: https://dataforseo.com/apis · docs https://docs.dataforseo.com/v3/ · AI Optimization https://dataforseo.com/apis/ai-optimization-api
- Google Ads Transparency via DataForSEO: https://dataforseo.com/blog/uncover-competitor-advertising-strategies-with-google-ads-transparency-and-apis
- Ahrefs API: https://ahrefs.com/api · Screaming Frog: https://www.screamingfrog.co.uk/seo-spider/ (v24 automation https://www.screamingfrog.co.uk/blog/seo-spider-24/)
- Google owned data: GSC https://developers.google.com/webmaster-tools · GA4 https://developers.google.com/analytics/devguides/reporting/data/v1 · PSI https://developers.google.com/speed/docs/insights/v5/get-started · CrUX https://developer.chrome.com/docs/crux/api
- Authority: Open PageRank (free) https://www.domcop.com/openpagerank/ · Moz Links API https://moz.com/products/api
- Social: Apify https://apify.com/store · YouTube Data API https://developers.google.com/youtube/v3 · Bluesky https://docs.bsky.app/
- Pitch data: Meta Ad Library https://transparency.meta.com/researchtools/ad-library-tools · HTTP Archive https://httparchive.org/ · thum.io https://www.thum.io/ · Microlink https://microlink.io/docs/api/parameters/screenshot/overlay · QuickChart https://quickchart.io/ · PredictLeads https://predictleads.com/

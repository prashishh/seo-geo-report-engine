# CLI connectors (fallback)

The **Ahrefs MCP is the primary data engine** (see `knowledge/ahrefs-mcp-map.md`). These
stdlib-only HTTP connectors exist as a **fallback** — for the Codex machine, for sources the
MCP doesn't cover, or for unattended scripts. Use `seo-data-router` plus
`knowledge/seo-geo-tooling-landscape.md` before adding new provider calls. Keys live in
`config/secrets.env` (copy from `config/secrets.example.env`).

| File | Source | When to use |
|------|--------|-------------|
| `ahrefs.py` | Ahrefs API v3 | Only if the MCP is unavailable. Needs `AHREFS_API_KEY`. |
| `dataforseo.py` | DataForSEO | **Committed data backbone — 5 engines, all live (2026-07-01).** (1) **SERP**: live Google SERP incl. **AI Overview** + PAA (`serp`, `ai_overview`, `paa`). (2) **Labs**: volume + **keyword difficulty** + intent in one call, keyword ideas, a domain's **ranked keywords**, and **competitor keyword gaps** (`keyword_overview`, `keyword_difficulty`, `keyword_ideas`, `ranked_keywords`, `domain_intersection`, `competitors_domain`). (3) **Backlinks**: `backlinks_summary`, `referring_domains`, `backlinks_bulk_ranks` (DR-equivalent for ≤1000 domains, one call). (4) **OnPage**: `onpage_instant`. (5) **AI Optimization**: `llm_query` / `llm_models` — ask **ChatGPT / Gemini / Perplexity / Claude** directly and capture the answer + its citations (a live, multi-engine GEO engine). Powers `serp-intel` + `tools/geo/ai_visibility.py`. Creds **per-profile** (`config/secrets.<profile>.env`). Caveat: Labs covers ~94 locations (**Nepal excluded**); for those markets use `keyword_volume` + `serp_competitors`. |
| `pagespeed.py` | PageSpeed Insights | Lighthouse / Core Web Vitals checks. Needs `GOOGLE_PSI_API_KEY` for higher limits. |
| `openrouter.py` | OpenRouter (Perplexity Sonar) | Live cited web research (`deep_research`) and cheap AI-citation probing (`probe`) — see the `web-research` skill. Needs `OPENROUTER_API_KEY`. |
| `predictleads.py` | PredictLeads | Competitor **funding** (`financing_events`), **hiring direction** (`job_openings` by department = where a rival is investing), and **news/momentum** (`news_events`: launches, partnerships, funding, office expansions). The freshest competitor-intel for pitch reports; reveals greenfield by showing where the field's money + hiring is absent. Needs `PREDICTLEADS_API_KEY`/`PREDICTLEADS_API_TOKEN`. Technologies endpoint is 404 on this plan (use DataForSEO `domain_technologies`). |
| `apify.py` | Apify | Public social-profile scraping (LinkedIn etc.) for competitor social footprint. Needs `APIFY_API_TOKEN`. Powers `tools/seo/social_footprint.py`. |

**DataForSEO now spans more than the five core engines** (verified 2026-07-01). Beyond SERP/Labs/Backlinks/
OnPage/AI-Optimization, the connector also wires: **domain intelligence** (`domain_rank_overview` = keywords
+ traffic + traffic-value + position mix in one call, `bulk_traffic_estimation`, `domain_technologies` =
the site's CMS/analytics/host stack), **link-graph** (`backlinks_competitors`, `backlinks_domain_intersection`
= link-prospect gap, `backlinks_bulk_spam_score`), and **reputation** (`content_analysis_summary` = web
mention volume + sentiment, `my_business_info` + `business_listings_search` = Google Business Profile +
local competitor census, `llm_mentions` = AI mention counts at scale). **Social caveat:** DataForSEO does
NOT cover social-network audience/engagement (only Pinterest pin counts); it covers reviews/GBP/mentions
(the reputation half). Genuine social presence needs a dedicated tool (see `knowledge/`).

All use only the standard library (`urllib`), so no `pip install` is required. Prefer the MCP
tools whenever they're connected — they're faster and already authenticated.

# Client-report roadmap: the standard section grammar + what to build next

Internal. The repeatable first-scan pitch report (`/client-report`, `first-scan-report` skill,
`tools/report/first_scan.py`) grows by the **config-as-data** pattern: one thin tool per section writes a
JSON artifact into `projects/<slug>/data/raw/`, and `first_scan.py` auto-includes any section whose
artifact exists (optional-artifact contract, so a partial scan still renders). Verified research 2026-07-02.

**Headline economics:** nearly every next-wow section is BUILD-on-owned (DataForSEO / Apify / PredictLeads
/ OpenRouter) or FREE (CrUX, GDELT, Google Trends, USPTO, GA4). Net cost to add the whole next layer:
~$0 subscription + ~$1-2 PAYG per pitch. Ship the two biggest holes first: traffic-share and reputation.

## Standard section grammar (the fixed order every client report follows)

0. Cover + one-line verdict (sharpest gap as the headline)
1. Where you stand today — EXISTING
2. Category / search-demand & content opportunity — EXISTING
3. **Traffic share** (visits + share %, org-vs-paid) — **BUILT** (`traffic_share.py`, DataForSEO)
4. **Share-of-Search** branded-demand momentum line (Google Trends, leading indicator) — TODO, free
5. Authority & referring-domain gap — EXISTING
6. Multi-engine AI-visibility matrix — EXISTING
7. **AI-Traffic Share** (% sessions from ChatGPT/Gemini/Claude/Perplexity) — TODO, Apify + client GA4
8. **Web-mentions Share-of-Voice + sentiment** — TODO, DataForSEO Content Analysis + free GDELT
9. **Reputation & Voice-of-Customer scorecard** (rating + volume + velocity + mined complaint/praise
   THEMES = switching wedge) — TODO, DataForSEO Business Data reviews + Apify G2/Capterra + LLM theme pass
10. **Community / Reddit demand-mining** (buyer pains, who they recommend, "X alternative" threads) — TODO, Apify
11. Ad presence: counts + **CREATIVE teardown** (top scaled creatives, offers, run-dates) — UPGRADE of `google_ads.py`
12. **Competitor tech + marketing-stack teardown** — TODO, free self-fingerprint / Apify
13. **Core Web Vitals benchmark** (real-user pass/fail bar) — TODO, FREE CrUX + PSI (reuse `web-vitals` skill)
14. **Competitor page-teardown gallery** (device-framed money-page screenshots + callouts) — TODO, add
    `--screenshot` mode to the owned Chrome renderer (`tools/pdf`); Apify for anti-bot sites
15. What competitors are winning with (top pages / content) — EXISTING
16. Momentum: funding + hiring + news (+ optional headcount curve) — EXISTING (`competitor_momentum.py`)
17. Greenfield 2x2 — EXISTING
18. Strengths & positioning — EXISTING
19. **Per-pillar scorecard** (0-100 / letter grade: authority, AI-visibility, demand, reputation, ads, brand) — TODO, presentation layer
20. Digital-presence plan + 90-day plan — EXISTING

## Build order (highest wow-per-effort first, all owned/free)

1. **Traffic share** — DONE (`traffic_share.py` -> DataForSEO Labs `bulk_traffic_estimation`, ~$0.001/domain).
2. **Reputation & VoC scorecard** — DONE (`reputation.py`). Built on the Perplexity probe (OpenRouter),
   which reads G2/Capterra/Trustpilot/Reddit and returns rating + review count + mined praise/complaint
   THEMES with sources, degrading honestly when reviews are scarce. Chosen over DataForSEO reviews
   (Trustpilot live 404s; G2/Capterra are the real B2B sources and structured APIs do not cover them) and
   Apify actors (need exact per-company review URLs). ~$0.005/company. Auto-included in first_scan.py +
   dashboard. Note: disambiguate common brand names in the prompt (a client named after a common word hit unrelated
   reviews before the fix).
3. **Core Web Vitals benchmark** — FREE CrUX API (150 q/min) + PSI, loop over competitor origins.
4. **Share-of-Search** — DONE (`share_of_search.py` -> DataForSEO Google Trends `keywords_data/google_trends/
   explore/live`, ~$0.01/call, client + top 4 rivals, share % + rising/fading trend). Appends " AI" to
   common-word brand names to cut namesakes; still directional for generic names.
5. **Ad teardown** — DONE as counts + gallery links + messaging (`google_ads.py` now stores each rival's
   Google Ads Transparency URL for the live-creative gallery, and `ad_messaging.py` -> Perplexity gets the
   ad ANGLE/hooks). Note: literal ad-creative IMAGES are NOT reliably obtainable for B2B here (DataForSEO
   `ads_search` rejects every field; Meta's free API returns political ads only and B2B rivals run Google/
   LinkedIn not Meta; Perplexity only surfaces messaging for well-indexed advertisers with heavy ad footprints).
   Actual images would need a paid ad-intel tool (SpyFu/AdClarity). The Transparency gallery LINK is the
   reliable "go see their real ads" deliverable.
5b. **Backlinks + link-GAP** — DONE (`backlinks.py` -> DataForSEO Backlinks bulk `ranks`/`referring_domains`/
   `backlinks`/`spam_score` + `domain_intersection` for the gap). Report section `backlinks_section` leads
   with the referring-domain gap, then the KEY insight: leaders' volume is inflated by low-quality/link-farm
   links (spam-score reframe), so the play is quality over volume, not matching the count. The intersection
   gap for low-authority local sites is mostly junk (filter with `_is_quality`); do NOT name scraped
   intersection domains in client copy, recommend link TYPES instead. Backlinks endpoints are global (no
   `--location`). Dashboard block added to `scan_summary.py`.
6. **Web-mentions SoV + sentiment** — DataForSEO Content Analysis + FREE GDELT DOC 2.0 API.
7. **AI-traffic share** — Apify Similarweb actor (per-LLM field) + client GA4 AI-referral segment.
8. **Reddit/community mining** — Apify public-web Reddit scraper + OpenRouter synthesis (`web-research`).
9. **Tech-stack fingerprint** — free self-fingerprint of competitor HTML (gtag/GTM/Shopify/Segment/Klaviyo).
10. **Page-teardown screenshot gallery** — `--screenshot` mode on `tools/pdf` Chrome renderer.
11. **Per-pillar scorecard + a live filterable HTML variant** alongside the PDF (perceived-product wow).

Lock a reusable SVG component set in `tools/charts` (share-bar, lollipop, radar, momentum timeline,
grayscale logo-matrix, 2x2, red/green CWV bar) so every report looks identical and on-brand.

## Three corrections (do not get these wrong)

- **Free Meta Ad Library API returns only political/issue ads, NOT commercial brand ads.** Use the Apify
  Facebook Ads scraper for competitor creatives.
- **Official G2 / Trustpilot / Reddit APIs are own-profile-only or forbid competitor monitoring.** Use
  scrapers (Apify) + DataForSEO for competitor review/community data.
- **Coresignal historical headcount is Premium ($1,500/mo).** Use People Data Labs Pro ($98/mo, free tier
  100/mo) for a headcount-growth curve if a client wants it.

## Buy only per-client (optional enrich flags, never default)

- **Brand24** (~$199/mo) — live listening dashboard a client pays for. **BuiltWith Team** (~$995/mo) — only
  for the tech-ADOPTION-DATE timeline. **People Data Labs Pro** (~$98/mo) — headcount curve. **Similarweb
  CI** ($125/mo) — panel-branded total-visits number for an enterprise prospect who demands it.
- **Skip:** free Meta API for brand ads, official G2/Trustpilot/Reddit APIs, G2 Buyer Intent
  ($10-40k/yr), Coresignal, enterprise ad-intel (Pathmatics/AdClarity, five figures/yr), Similarweb API.

## Guardrails

Every modeled figure (traffic, AI-traffic, ad spend/impression buckets) is LABELED an estimate in client
copy. AI SoV framed "within the tracked demand set." Client copy uses neutral source labels, never names
DataForSEO/Apify/PredictLeads/actors/costs. No CMS/publish assumption (brain not builder). No em dashes,
no AI-giveaway edge-borders, grayscale competitor logos, one visual per insight.

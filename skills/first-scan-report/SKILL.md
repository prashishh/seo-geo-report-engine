---
name: first-scan-report
description: >
  Produce the client-facing FIRST-SCAN "hook" report: a one-look teardown of a prospect's current
  digital footprint, who is winning their buyers, where they are absent, and the winnable opportunity.
  Use when asked to "make a first-scan report", "create the client hook / pitch report", "show a
  prospect their digital presence", "run a cold-open scan", "audit our footprint vs competitors for a
  deck", or "what would we send a client after the first scan". Assembles authority + AI Share-of-Voice
  + keyword-opportunity + reputation data into a branded PDF via the existing renderer. This is the
  customer-acquisition asset: transparent, easy to read, and it shows a taste of what is possible.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# first-scan-report

The hook that acquires the client. One scan, one PDF: where they stand, who is beating them, where the
open lanes are, and the plan to take them. It reads the scan artifacts a project already has and
assembles a `report.yml` the proposal renderer turns into a branded, charted PDF (HTML -> Chrome).
The recipe stays internal; the client sees the finding and the plan, never the method.

## The pipeline (run the cheap scans, then assemble)
```
# 1. multi-source authority (client + competitors)
python3 tools/seo/authority.py        --project <slug> --out projects/<slug>/data/raw/dataforseo/authority-<date>.json
# 2. keyword opportunity + content gap
python3 tools/seo/keyword_research.py --project <slug> --location <code> --topic <tokens> \
    --out projects/<slug>/data/raw/dataforseo/kw-<date>.json
# 3. multi-engine AI Share of Voice (build a weighted prompt set first, then scan)
python3 tools/geo/prompt_set.py       --project <slug> --location <code> --out projects/<slug>/data/prompt-set.json
python3 tools/geo/llm_visibility.py   --project <slug> --location <code> --prompt-set projects/<slug>/data/prompt-set.json \
    --out projects/<slug>/data/raw/dataforseo/llm-visibility-<date>.json
# 4. assemble + render the hook PDF
python3 tools/report/first_scan.py    --project <slug> --date <date> --render
```
Output: `projects/<slug>/deliverables/<slug>-first-scan.pdf` (+ the editable `first-scan-report.yml`).
Every section is optional: a partial scan still renders a coherent report (missing inputs are skipped).

### Power sections (the wow: competitive gap + greenfield + AI matrix) — US/Labs markets
```
# competitor steal-list + traffic-value gap ("you leave $X/mo on the table")
python3 tools/seo/competitor_gap.py    --project <slug> --location 2840 --topic <core tokens> \
    --out projects/<slug>/data/raw/dataforseo/competitor-gap-<date>.json
# greenfield 2x2: score every candidate keyword Demand x Winnability x Fit, buyer-intent filtered
python3 tools/seo/opportunity_score.py --project <slug> --location 2840 --fit <core tokens> \
    --out projects/<slug>/data/opportunity-scored.json
# AI-visibility MATRIX: ~8 buyer questions x 5 engines (named/cited/absent heatmap)
python3 tools/geo/llm_visibility.py    --project <slug> --location 2840 --brand "Name" name.com \
    --prompts "buyer question 1" "buyer question 2" ... \
    --out projects/<slug>/data/raw/dataforseo/ai-matrix-<date>.json
# what competitors win with (their top pages by traffic) - saved to data/raw/.../top-pages-<date>.json
# competitor momentum: funding + hiring direction + news (PredictLeads) - the freshest intel + greenfield proof
python3 tools/seo/competitor_momentum.py --project <slug>
# Google ad activity (Ads Transparency) - who is buying attention
python3 tools/seo/google_ads.py          --project <slug>
# social follower gap (needs client.yml social.linkedin URLs + APIFY_API_TOKEN)
python3 tools/seo/social_footprint.py    --project <slug>
# traffic share ("you are X% of category traffic") + Core Web Vitals vs rivals
python3 tools/seo/traffic_share.py       --project <slug>
python3 tools/seo/web_vitals_bench.py    --project <slug>   # Core Web Vitals via DataForSEO Lighthouse (no Google key)
python3 tools/seo/reputation.py          --project <slug>   # reputation + VoC scorecard (ratings + mined complaint themes)
python3 tools/seo/share_of_search.py     --project <slug>   # share-of-search (branded-demand momentum, Google Trends)
python3 tools/seo/ad_messaging.py        --project <slug>   # ad-messaging teardown (angles rivals run)
# populate the INTERNAL dashboard (research/competitive-scan.md + BUILD-STATUS.md from all artifacts)
python3 tools/report/scan_summary.py     --project <slug> --date <date>
```
**Reports vs dashboard:** the PDF is the client deliverable; the dashboard (`./bin/mkt dashboard serve`)
is the internal live view. Always run `scan_summary.py` after a scan so the dashboard shows the latest
data (authority, traffic share, AI-visibility, momentum, Core Web Vitals, social, ads) as readable
markdown + CSV. See `knowledge/report-roadmap.md` for the full section grammar and build order.
When these artifacts exist, `first_scan.py` auto-adds: **The traffic and revenue you are not capturing**
(steal list + traffic-value gap), **Where rivals are spending and hiring** (funding + hiring direction,
the greenfield proof that only N of the field's open roles are in your open lane), **Greenfield
opportunity map** (bubble matrix), **What competitors are winning with** (top pages + content pattern),
**Where the field is buying attention** (Google ad counts), the **social presence gap** (LinkedIn
followers), and the **AI visibility matrix** (question x engine heatmap). These turn an audit into a
pitch. Charts: `bubble` and `heatmap` in `tools/charts/svg.py`. Keep the traffic-value number framed as
"competitors combined" (it sums the set) so it stays honest, and reconcile PredictLeads funding totals
against the public record (its coverage can be incomplete). For a fully bespoke, curated deck (like the
Vector Agents pitch), hand-author a `_build.py` in the project that reads these same artifacts; for a
standard client report, run the pipeline above and let `first_scan.py` assemble it. See the
`/client-report` command for the end-to-end runner.

## What the report MUST show (the hook structure)
Do not send a first-scan report without these sections. If a live metric is blocked, rerun with a
fallback or move the issue to internal notes. Client-facing reports show findings, not tool failures.

1. **Where you stand today** - location/market, site footprint, authority, keywords, competitors,
   SEO state, GEO/AI state, and the sharpest missing asset.
2. **Location and market context** - headquarters/office footprint, target geography, local relevance,
   and whether the campaign is local, national, or global. Cite the source and date.
3. **Search demand and content opportunity** - never use only the client's configured phrases. Expand
   into head terms, commercial service terms, problem-led searches, comparison searches, and
   question-led guide/blog/FAQ opportunities. Show exact-phrase monthly searches as directional, not
   total market demand.
4. **Authority and competitor gap** - client + competitors, authority score/referring domains when
   available. If authority data is not captured, get a fallback before sending the client report.
5. **SEO/GEO current state** - organic footprint, indexed/service-page coverage, schema/crawler/llms.txt
   status, AI Share of Voice or prompt-scan result, and who AI/SERP names instead.
6. **Graphs and punchlines** - at least one visual for demand, one for authority/competitor gap, and
   one SEO/GEO/social footprint visual. The deck should be skim-readable.
7. **The opportunity, and how we take it** - 3-5 prioritized moves with falsifiable success checks.

## How to make it land
- **Curate after assembling.** The tool drafts from live numbers; open `first-scan-report.yml` and sharpen
  the narrative to the prospect's actual business before sending. The brain drafts, the founder finishes.
- **Lead with the gap they feel.** Reorder so the sharpest finding (usually AI invisibility or a big
  content gap a competitor owns) is the first headline.
- **Write like an operator.** Avoid generic AI-ish lines ("It is not X, it is Y", "foundation debt",
  punchy fragments with no connective tissue). Prefer bullets, concrete page/action pairs, and short
  explanations of why a metric matters.
- **Set `client_name`** in `client.yml` for correct casing in the deck.
- **Enrich (optional, cheap):** `domain_rank_overview` / `bulk_traffic_estimation` (traffic + keyword
  stat block, Labs markets only), `domain_technologies` (their stack), `content_analysis_summary` (brand
  mention volume + sentiment), `business_listings_search` + `my_business_info` (local reputation) - all
  in the DataForSEO connector, wire into a new section when the client is local/ecommerce.

## Guardrails
- Keep the recipe internal. The client report must not name provider tools, internal commands, APIs,
  actor names, prompts, costs, timeouts, or rerun traces. Use neutral source labels: "live search
  data", "public social profile", "public website review", "public company profile".
- AI Share of Voice is "within the tracked demand set"; state the sample size, treat one scan as a
  sample. Never overclaim a whole-market number.
- Brain not builder: the report hands off strategy + artifacts; it never assumes we publish for them.
- Cost of a full first scan (client + ~5 competitors): roughly $0.50-$1.00 of API. Cheap enough to run
  speculatively on a prospect before they are a client.

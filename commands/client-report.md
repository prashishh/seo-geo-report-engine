---
description: Produce the full client-facing first-scan pitch report for a prospect, end to end — live scan, research pass, branded PDF.
argument-hint: "<slug> <domain-or-url>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# /client-report <slug> <domain>

The one runner that turns a prospect URL into a branded, wow-grade pitch PDF, the same shape every time.
It orchestrates the `first-scan-report` skill's pipeline plus the competitive-research pass. The report
is the hook that wins the client: where they stand, who is beating them, where the open ground is, and
the plan. Client copy names competitors + real numbers (no vague euphemisms) and never names the
underlying tools/APIs (use neutral source labels like "live search data", "public review data").

## Steps

1. **Seed the project.** `WebFetch` the prospect's site (product, ICP, positioning, named products,
   customers, socials). Create `projects/<slug>/client.yml`: `client_name`, `domain`, `competitors`
   ([{name, domain}] — the real funded peer set, verify domains), `target_keywords` (buyer terms across
   every product line), `market`, `messaging.lanes`, and `social.linkedin` (company-page URLs for the
   client + each rival, for the social benchmark). US/Labs market unlocks the full toolset.

2. **Run the live scan** (each writes an artifact `first_scan.py` reads; US location code 2840):
   ```
   python3 tools/seo/authority.py           --project <slug> --out projects/<slug>/data/raw/dataforseo/authority-<date>.json
   python3 tools/seo/keyword_research.py     --project <slug> --location 2840 --seeds "..." --topic <core tokens> \
       --out projects/<slug>/data/raw/dataforseo/kw-<date>.json
   python3 tools/seo/competitor_gap.py       --project <slug> --location 2840 --topic <core tokens> \
       --out projects/<slug>/data/raw/dataforseo/competitor-gap-<date>.json
   python3 tools/seo/opportunity_score.py    --project <slug> --location 2840 --fit <core tokens>
   python3 tools/geo/llm_visibility.py       --project <slug> --location 2840 --brand "Name" name.com \
       --prompts "<8 buyer questions>" --out projects/<slug>/data/raw/dataforseo/ai-matrix-<date>.json
   python3 tools/seo/top_pages.py            --project <slug> --location <code> --per 6   # what content each rival wins with
   python3 tools/seo/backlinks.py            --project <slug>     # backlink profile (ref domains, spam) + link-GAP outreach list (location-agnostic)
   python3 tools/seo/competitor_momentum.py  --project <slug>     # PredictLeads funding + hiring + news (SaaS/funded set; skip for local SMB)
   python3 tools/seo/google_ads.py           --project <slug> --location <code>   # Google Ads Transparency counts
   #   --location = the client's market code (US 2840, Australia 2036). Same code for reputation + ads.
   python3 tools/seo/social_footprint.py     --project <slug>     # LinkedIn follower gap (needs social.linkedin)
   python3 tools/seo/web_vitals_bench.py     --project <slug>     # Core Web Vitals vs rivals (DataForSEO Lighthouse, no Google key)
   python3 tools/seo/reputation.py           --project <slug> --location <code>   # ratings (Google Business + G2/Trustpilot) + mined complaint themes = switching wedge
   python3 tools/seo/share_of_search.py      --project <slug>     # branded-demand momentum (Google Trends, leading indicator)
   python3 tools/seo/ad_messaging.py         --project <slug>     # what rivals say in their ads (messaging teardown)
   ```

4b. **Populate the internal dashboard.** `python3 tools/report/scan_summary.py --project <slug> --date <date>`
   writes `research/competitive-scan.md` (the latest-data working view) and `BUILD-STATUS.md` from the
   scan artifacts. The dashboard (`./bin/mkt dashboard serve`) renders these live: reports (PDF) go to the
   client, the dashboard is the internal place to scour the latest data + updates. Re-run any time to refresh.

3. **Competitive-research pass** (the narrative the tools cannot produce). Run a research workflow (or the
   `web-research`, `competitor-analysis`, `geo-audit` skills) to get: the prospect's real traction +
   genuine strengths, each rival's funding/positioning/where they ace, the category demand, and the
   ranked greenfield. Write findings to `projects/<slug>/research/`. Be honest: flag placeholder proof,
   namesake confusion, and roadmap-vs-shipped gaps so the deck never overclaims.

4. **Assemble + render.**
   - Standard report: `python3 tools/report/first_scan.py --project <slug> --date <date> --render`.
     It auto-includes every section whose artifact exists (authority, backlinks + link-gap, traffic
     share, share-of-search, steal-list, momentum, greenfield, what-rivals-win-with, reputation, Google
     ads, social gap, Core Web Vitals, AI matrix).
   - Curated wow deck (recommended for a real pitch): hand-author `projects/<slug>/_build.py` that reads
     the same artifacts and embeds the research narrative.
     Order: opening → category demand → footprint gap → AI-visibility matrix → social gap → ad spend →
     what rivals win with → the funded field → momentum (funding + hiring) → greenfield 2x2 → strengths
     → positioning → digital-presence plan → 90 days → the moment.

5. **Curate + QA before sending.** Sharpen the narrative to the prospect's business; lead with the
   sharpest finding. Verify: no vague euphemisms (name competitors + numbers), no em dashes, no tool/API
   names in client copy, PredictLeads funding reconciled against the public record, and any uncertain
   data (ambiguous ad matches, thin reviews) dropped rather than shown. Output:
   `projects/<slug>/deliverables/<slug>-strategy-report.pdf`.

## Notes
- Cost of a full scan on a client + ~8 rivals: roughly $1 to $2 of API. Cheap enough to run on a
  prospect before they are a client.
- The report is a handoff/pitch artifact; it never assumes we publish for them (brain not builder).

---
name: competitor-analysis
description: >
  Competitor gap analysis — find where rivals beat us and where to attack. Use when asked for
  "competitor analysis", a "competitive gap", "who are we competing with", "keyword gap vs
  <competitor>", "compare us to <competitor>", "backlink gap", "content gap vs <competitor>",
  "what is <competitor> ranking for that we aren't", or "where can we win against <competitor>".
  Produces a ranked keyword-gap table, content-gap themes, a backlink-prospect list, ad/promo
  notes, and a falsifiable "where to attack first" plan saved to the client's research folder.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# competitor-analysis

Finds the gap between us and our **true** organic competitors and turns it into a prioritized,
falsifiable attack list. Ahrefs MCP is the engine (see `knowledge/ahrefs-mcp-map.md`); the full
methodology — competitor selection, the gap-scoring model, prioritization — lives in
`playbooks/competitor-intel.md`. Read it before scoring.

Methodology is **PERCEIVE → ANALYZE → VALIDATE → ACT**. Every recommendation must be falsifiable:
state the observation, the dependency it rests on, and the leading indicator that would tell us
within weeks that it failed.

## Inputs
- `projects/<client>/client.yml` — our `domain`, `competitors[]`, `target_keywords[]`, `market`,
  `ahrefs.project_id`. Resolve with `./bin/mkt config show --project <client>`.
- Any prior research in `projects/<client>/research/` and snapshots in `data/`.

## Workflow

### 1. PERCEIVE — identify the *true* competitor set
- Pull organic competitors: `site-explorer-organic-competitors` for our `domain`.
- Union with the `competitors[]` named in `client.yml` (these are business rivals — they may or
  may not overlap organically).
- **Validate overlap on money keywords, not vanity keywords.** A domain that overlaps only on
  informational/long-tail terms we don't monetize is not a competitor. Confirm overlap on our
  `target_keywords` and commercial-intent head terms via `site-explorer-organic-keywords`
  (filter to our money terms) and `serp-overview` on 3–5 head terms.
- Decide a working set (usually 3–5). Note which are organic rivals, business rivals, or both.

### 2. ANALYZE — pull the four gaps
Save every raw pull to `projects/<client>/data/` (e.g. `competitor-<domain>-keywords.json`).

- **Keyword gap.** Pull `site-explorer-organic-keywords` for us and each competitor. Find terms
  they rank top-10 for and we don't (or rank >20). Score each — see the model below.
- **Content gap.** `site-explorer-top-pages` / `site-explorer-pages-by-traffic` for each
  competitor → cluster their best pages into themes/topics we lack. Note format (guide, tool,
  comparison, template) and the intent it serves.
- **Backlink gap.** `site-explorer-referring-domains` for us and each competitor → find domains
  linking to **≥2 competitors but not us** (warm link prospects). Run
  `site-explorer-broken-backlinks` on competitors → dead pages with live links = reclaim/recreate
  targets. Use `site-explorer-pages-by-backlinks` to see which competitor pages earn the links.
- **SERP / authority.** `rank-tracker-competitors-overview` / `-domains` / `-pages` and
  `serp-overview` on head terms for live position context. `site-explorer-domain-rating` and
  `-domain-rating-history` for us + each competitor to gauge feasibility and momentum.

### 3. Gap-scoring model (the prioritizer)
Per gap keyword, score = **Volume × Intent × Feasibility**.
- **Volume** — `keywords-explorer-overview` (or the organic-keywords pull). Use traffic potential
  where available, not just exact volume.
- **Intent** — weight commercial/transactional > comparison/BOFU > informational. Money terms win.
- **Feasibility** — KD vs **our** DR. A KD well above our DR is a multi-month link play, not a
  quick win; flag it. Pages where a competitor ranks with a weaker page than ours = fast attack.
Rank descending. Tag each row: `quick win` / `build-up` / `long play`. Full rubric in the playbook.

### 4. VALIDATE — paid, promo, and live SERP reality
- **Paid / ads & promos (web source).** `WebFetch` the **Meta Ad Library**
  (`https://www.facebook.com/ads/library/`) and the **Google Ads Transparency Center**
  (`https://adstransparency.google.com/`) for each competitor's live creatives, offers, and
  seasonal pushes. Note hooks, discounts, and landing pages. Cross-check organic findings against
  `site-explorer-paid-pages` for paid landing pages.
- Spot-check 3–5 top gap terms in `serp-overview` to confirm the SERP isn't dominated by
  unbeatable entities (big brands, Reddit, the SERP feature you can't win).
- For verified, sourced competitor facts (positioning, pricing model, features, integrations —
  the raw material `comparison-pages` needs), prefer the `web-research` skill's deep-research mode
  over manually fetching each vendor page one at a time; it synthesizes across sources and returns
  a real citation list to check against.

### 5. ACT — write the deliverable
Write `projects/<client>/research/competitor-analysis.md` (date it; today is absolute, e.g.
`2026-06-23`) with:
1. **Competitor set** — who, why they qualified (overlap evidence), DR vs ours.
2. **Ranked keyword-gap table** — term · volume · intent · KD · our gap · score · tag · the page
   that should target it.
3. **Content-gap themes** — the topics/formats competitors own that we don't, with the example
   pages and est. traffic.
4. **Backlink-prospect list** — domains linking to ≥2 competitors not us, plus broken-backlink
   reclaim targets, with the competitor page that earned each link.
5. **Ad / promo notes** — live creatives, offers, seasonal angles per competitor (Meta + Google).
6. **Where to attack first** — a prioritized shortlist. Each item is **falsifiable**:
   *observation → bet → dependency → leading indicator we'd watch (and the value that means it
   failed)*. e.g. "Bet: a comparison page for `<term>` (vol 1.4k, KD 18, our DR 41) reaches
   top-10 in 8–10 weeks. Fails if it's not in the top 30 after 6 weeks of indexation."

## Notes
- **Data priority: Ahrefs MCP > CLI connectors > web.** Use web only for ad libraries and SERP
  spot-checks. Always call `doc` on a tool before first use; monetary values are USD cents (÷100).
- Keep the gap tables tight and real — 15–30 scored rows beat 500 unsorted ones.
- This feeds two downstream deliverables: the **`comparison-pages`** skill (consumes the keyword
  gap + ad/promo angles to spin "us vs <competitor>" pages) and the **growth proposal** (the
  attack list becomes the acquisition pillar). For ongoing monitoring, hand off to
  **`/competitor-watch`**.

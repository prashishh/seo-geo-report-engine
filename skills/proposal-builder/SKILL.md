---
name: proposal-builder
description: >
  Produce a polished, branded growth-proposal PDF (the 3-pillar deck style) for a
  client — executive summary, pillars, roadmap, scenario projections, KPI targets, charts.
  Use when asked to "write a growth proposal", "build a pitch deck / proposal", "create a
  growth plan", "put together a proposal for <client>", or to turn research into a client-ready PDF.
  Also covers "channel mix / ORB proposal", "market sizing in a proposal", and "PMF check before spend".
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# proposal-builder

Turns a client's profile + research into a **branded growth-proposal PDF** that looks like the
reference decks. You compose the *content* (a `proposal.yml`); the renderer handles layout, brand,
charts, and PDF. Depth methodology lives in `playbooks/proposal-methodology.md`.

## Inputs
- `projects/<client>/client.yml` — profile, competitors, target keywords, brand, locale.
- Any research already in `projects/<client>/research/` (keyword, competitor, GEO, audit outputs).
- The brief / notes in `projects/<client>/inputs/`.

If the project doesn't exist yet, run `/new-client` first (or create the folder + `client.yml`
from `templates/client.yml.example`).

## Workflow

1. **Resolve context.** `./bin/mkt config show --project <client>`. Read `client.yml`, the brief,
   and existing research. Identify vertical, ICP, market/locale, competitors, budget, time horizon.

2. **Fill research gaps (Ahrefs MCP first — see `knowledge/ahrefs-mcp-map.md`).** Only pull what the
   proposal needs; don't boil the ocean.
   - Opportunity sizing: `keywords-explorer-*` for category volume; market/TAM from the brief.
   - Competitive landscape: `site-explorer-organic-competitors`, `-top-pages`, `-domain-rating`.
   - GEO angle: `brand-radar-sov-overview` / `-mentions-overview` for AI share-of-voice (use the
     `geo-audit` skill if a full GEO read is wanted).
   - Save anything reusable into `research/` as you go.

   For first-strategy or client-hook proposals, these are mandatory unless explicitly out of scope:
   **location/market context, keyword demand, domain authority/DR, named competitors, SEO current
   state, GEO/AI current state, and at least two charts/visual punchlines**. If a provider call fails,
   include a dated "not captured" row plus the rerun path rather than dropping the section.

3. **Choose the spine.** Default to the proven structure (adapt to the client):
   1. Executive summary + 3 pillars (Foundation → Wide Net/Acquisition → Conversion/Lifecycle)
   2. Current-state scorecards (location, authority, keyword demand, SEO/GEO readiness)
   3. The opportunity (market size, where the headroom is)
   4. Competitor and keyword gap charts
   5. Audience / ICP (segments, where they are)
   6. Pillar deep-dives with **deliverables**
   7. Roadmap (workstream gantt)
   8. Scenario projection (conservative / probable / aggressive) + metrics table
   9. KPI scorecards + a clear next step (CTA)

4. **Compose `projects/<client>/proposal.yml`** following `templates/proposal/proposal.schema.md`.
   - Every claim should be **falsifiable** — tie projections to assumptions a reader can challenge.
   - Label any illustrative/assumed number as such; don't imply data you didn't pull.
   - Chart data must be numeric (the `kind` field formats `$`/`%`).

5. **Render:** `./bin/mkt proposal build --project <client>`
   → writes `deliverables/<slug>-growth-proposal.{html,pdf}`.

6. **Review the PDF** (open it / Read the PDF pages). Check: cover, pillar cards, chart readability,
   page breaks, no `\"` artifacts, numbers consistent across sections. Iterate on `proposal.yml`
   and rebuild. Summarize assumptions and open questions back to the user.

## Channel model, market sizing & PMF gate

Frame SEO/GEO as one slice of a broader channel mix, not the whole plan — it earns trust and
sharpens the pillar story.

- **ORB channel model.** Classify proposed channels as **Owned** (site, content, email list, llms.txt),
  **Rented** (organic search/SERP, social reach, marketplaces — borrowed audiences on someone else's
  rules), or **Borrowed** (paid ads, influencers, partner placements — access ends when spend does).
  Position SEO/GEO as the **Rented→Owned** compounding engine and name which Borrowed channels (paid)
  de-risk the slow ramp. Falsifiable: state the assumed channel-mix split (e.g. "60% Rented/Owned, 40%
  Borrowed by month 6"); *how we'd know it failed* — paid CAC stays flat or owned/organic share of
  pipeline doesn't rise quarter over quarter.

- **Market opportunity (optional).** When the client needs a sizing slide, run the `market-opportunity`
  skill to produce **TAM / SAM / SOM** and drop it into spine step 2 (the opportunity). Tie SOM to the
  category search volume you pulled in workflow step 2. Label every figure as *modeled* with its
  assumption (geo, ICP filter, win-rate); *how we'd know it failed* — a reader can name a TAM input
  that's off by >2x.

- **PMF qualifier gate.** Before recommending heavy spend (aggressive scenario, large retainer, paid
  acceleration), confirm the client shows product-market-fit signals (retention, repeat/referral,
  organic pull, healthy unit economics). No PMF → propose the **conservative** scenario and a learning
  budget, not scale. *How we'd know it failed* — scaling spend pre-PMF and CAC payback never converges.

- **Value-prop language.** Pull the one-liner and pillar messaging from `client.yml: messaging`
  (the positioning-messaging canonical one-liner + pillars) verbatim — do **not** re-derive it in the
  proposal. If `messaging` is absent, flag it and run positioning-messaging first.

## Notes
- Brand comes from `client.yml: brand` (falls back to `config/framework.yml`). Set `primary` +
  `accent` to match the client.
- Keep the deck tight — the references are ~10 pages. Prefer one strong chart per section.
- Use bullets and tables for scans. Avoid long abstract paragraphs and generic AI phrasing; every
  section should contain a metric, a page, a competitor, a location, or a concrete action.
- To restyle globally, edit `templates/proposal/base.css`; to add a chart type, extend
  `tools/charts/svg.py`.

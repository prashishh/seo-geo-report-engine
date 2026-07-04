---
description: Full intake audit for a new client — keyword, technical, competitor, GEO, and backlink — synthesized into one DISCOVERY brief.
argument-hint: "<project>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
---

# /discovery-audit <project>

The one-time **intake audit** for **$1** (defaults to the active project — resolve with
`./bin/mkt config show`). Runs the five diagnostic skills, then synthesizes everything into a single
`research/DISCOVERY.md` that becomes the evidence base for the growth proposal. This is the
"PERCEIVE + ANALYZE" pass before we propose anything — every later claim should trace back to here.

## Steps

1. **Load context.** `./bin/mkt config show --project $1`. Read `client.yml` → `domain`,
   `competitors[]`, `target_keywords[]`, `market`, `languages`, `ahrefs.project_id`,
   `ahrefs.brand_radar_report_id`. If `client.yml` is mostly empty, stop and point the user at
   `/new-client $1` first. Note which Ahrefs ids are missing — some skills degrade gracefully
   without them (e.g. rank tracking needs `project_id`; GEO needs `brand_radar_report_id`).

2. **Run the diagnostic skills.** Order matters where one feeds the next; the rest can run in
   parallel. Prefer the Ahrefs MCP throughout (`knowledge/ahrefs-mcp-map.md`); call `doc` on a tool
   before first use; monetary values are USD cents (÷100). Each skill writes to
   `projects/$1/research/`.

   - **First, the upstream "who they are + the market" pass (see § Upstream layers below):**
     0a. **`market-opportunity`** — TAM/SAM/SOM sizing + a PMF qualifier. Frames whether the
         market is worth winning before we measure how they rank.
     0b. **`positioning-messaging`** + **`customer-research`** — positioning/category claim and a
         voice-of-customer (VOC) pull. Establishes who they are, who they serve, and how buyers
         describe the problem in their own words.

   - **Then, sequentially (it seeds the SEO/GEO fan-out):**
     1. **`keyword-research`** — seed → expansion → intent clusters → winnable-volume scoring
        against our DR. Produces the keyword map + the opportunity size the proposal will quote.
        Seed it with the VOC language and category terms from 0b.

   - **Then, in parallel (independent reads — delegate to subagents to run concurrently):**
     2. **`technical-seo-audit`** — crawl/health, on-page, Core Web Vitals, indexability
        (Site Audit + GSC). The "Foundation" evidence.
     3. **`competitor-analysis`** — keyword gap, content gap, backlink prospects, ad/promo notes
        vs `competitors[]`. Reuses the keyword map from step 1.
     4. **`geo-audit`** — AI-search visibility via Brand Radar: SoV, mentions, who AI cites,
        citability + crawler-access check. The "are we present in AI answers" read.
     5. **`backlink-analysis`** — authority profile, ref-domain growth, anchor health, toxic/lost
        links, and reclaim/prospect targets.

   > Concurrency: 2–5 are read-only and touch different data, so dispatch them to the
   > `seo-analyst` / `geo-analyst` / `data-researcher` subagents in parallel and collect results.
   > Keyword-research (1) must finish first because competitor-analysis builds on its map.

3. **Synthesize → `projects/$1/research/DISCOVERY.md`** (use the absolute run date 2026-06-23).
   Don't just staple the five outputs together — interpret them as one picture:
   - **Snapshot** — domain, DR, organic traffic + value, tracked positions, AI SoV: where they
     stand today, in numbers (cite the Ahrefs tool + date for each).
   - **The opportunity** — total vs winnable search volume from keyword-research; the headroom.
   - **Foundation gaps** — the material technical/on-page issues that cap everything else.
   - **Competitive position** — who beats us where; the biggest gap and the softest target.
   - **GEO position** — AI visibility vs competitors; citability and crawler-access blockers.
   - **Authority** — backlink strengths/risks and the clearest link opportunities.
   - **Top findings** — the 5–8 highest-leverage observations across all five, each as a
     falsifiability block: **observation → depends on → how we'd know it failed (leading indicator)**.

4. **Recommend the next step.** Close `DISCOVERY.md` with a one-paragraph "so what" and tell the
   user to run **`/growth-proposal $1`** — the proposal reads this brief plus `client.yml` to build
   the 3-pillar deck.

## Upstream layers — market & positioning before rankings

Adopted from `claude-gtm-plugin` + `claude-seo`. The DISCOVERY brief should open with **who they
are + the market** before **how they rank**, so these two layers run *before* the SEO/GEO data
pulls (steps 2–5) and feed them. Pattern is **orchestrator → specialists**: this command is the
orchestrator; each layer is a specialist skill that writes its own artifact to
`projects/$1/research/`, which step 3 then synthesizes.

- **Layer 1 — Market opportunity (`market-opportunity`).** TAM/SAM/SOM with a stated method
  (top-down vs bottom-up) and a PMF qualifier. Falsifiability: **observation** (e.g. "SAM ≈ $X at
  N target accounts") → **depends on** (the sizing inputs and PMF signal cited) → **how we'd know it
  failed** (winnable search volume from step 1 implies a market an order of magnitude off the SAM,
  or no retention/demand signal behind the PMF claim).
- **Layer 2 — Positioning + VOC (`positioning-messaging` + `customer-research`).** The category
  claim, differentiators, and ICP, plus a voice-of-customer pull in buyers' own words.
  Falsifiability: **observation** (the positioning statement + top VOC themes) → **depends on**
  (real customer/review/SERP language, not assumed) → **how we'd know it failed** (VOC terms carry
  no search demand in step 1, or competitors already own the claimed category position).

These reframe the keyword and GEO work downstream: keyword-research is seeded with VOC + category
language, and the DISCOVERY **Snapshot** leads with market + positioning before the rankings read.
Label any unvalidated TAM/SAM/SOM or positioning input as assumed/illustrative.

## Notes
- **Run once at intake.** The recurring companions are `/competitor-watch` (weekly) and
  `/weekly-report` / `/monthly-report` (reporting) — not this.
- Everything is falsifiable (PERCEIVE → ANALYZE → VALIDATE → ACT): state the observation, its
  dependency, and the kill condition. Label any assumed/illustrative number as such.
- Save reusable pulls (csvs, snapshots) under `projects/$1/data/` so later workflows don't re-spend
  Ahrefs quota. Watch quota with `subscription-info-limits-and-usage`.

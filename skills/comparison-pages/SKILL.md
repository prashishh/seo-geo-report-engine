---
name: comparison-pages
description: >
  Build fact-checked "us vs competitor" comparison pages and a comparison hub that capture
  high-intent and AI-citable demand. Use when asked for a "comparison page", "X vs Y page",
  an "alternatives page", a "comparison hub", "vs competitor pages", an "honest comparison", or
  pages built to earn "AI citations" / answer "best X for Y" queries. Pulls competitors from
  client.yml, gathers objective facts (features, pricing, coverage) per competitor, sizes
  demand for "<competitor> alternative" / "<us> vs <competitor>", builds fair structured
  comparison tables with FAQ + Product/structured data, generates pages via
  tools/programmatic/generate.py, and links them from a hub. Reference playbooks/programmatic-seo.md.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# comparison-pages

Build **"us vs {competitor}"** pages and a **comparison/alternatives hub**. These rank for
high-intent bottom-funnel queries and are disproportionately **cited by AI answer engines**,
so accuracy and fairness are non-negotiable — never fabricate a competitor fact. Shares the
generator and hub architecture with `programmatic-seo`; methodology in
`playbooks/programmatic-seo.md`. Methodology: **PERCEIVE → ANALYZE → VALIDATE → ACT**,
falsifiable claims. Today is **2026-06-23**; write absolute dates.

## Inputs
- `projects/<client>/client.yml` — **competitors** list, domain, positioning, locale.
- Existing research in `projects/<client>/research/`.

Resolve context first: `./bin/mkt config show --project <client>`.

## Workflow

1. **PERCEIVE — take the competitor set from `client.yml`.** Read the `competitors` list
   (cross-check with `management-project-competitors` /
   `site-explorer-organic-competitors` if you need to find more). One page per "us vs {competitor}".

2. **ANALYZE — gather objective facts per competitor.** For each one:
   - Their positioning & top pages: `site-explorer-top-pages` (what they're known for), and
     `WebFetch` their pricing / features / homepage for the primary source of truth.
   - **Record only verifiable facts** (features, pricing tiers, coverage, integrations, limits)
     with the source URL. If a fact can't be confirmed, mark it `Unknown` — do not guess.

3. **VALIDATE — size demand (Ahrefs MCP, see `knowledge/ahrefs-mcp-map.md`).** With
   `keywords-explorer-overview` / `-matching-terms`, pull volume for
   `"<competitor> alternative"`, `"<us> vs <competitor>"`, `"<competitor> vs <us>"`,
   `"<competitor> alternatives"`. Prune competitors with no demand; prioritize the rest by volume.

4. **ACT — build the comparison table.** Structured, **fair, fact-checked** rows: the same
   attributes for both sides, each cell sourced. Be honest where the competitor wins — fairness
   is what makes the page (and your brand) credible and citable. Add a row-specific **FAQ** and
   **Product / structured data** (defer to the `schema-markup` skill: Product, FAQPage,
   optionally a comparison/ItemList).

5. **ACT — generate the pages.** One row per competitor in a `.csv` / `.json` rows file, plus a
   comparison template (`{us}`, `{competitor}`, feature/pricing cells, FAQ) with `{placeholder}`
   fields, then:

   ```bash
   python tools/programmatic/generate.py \
     --rows projects/<client>/research/comparison-rows.csv \
     --template projects/<client>/research/comparison-template.html \
     --out projects/<client>/deliverables/comparison \
     --slug-field slug
   ```

   Missing placeholders render as a visible `{{TODO:field}}` marker — grep for it and resolve
   every one (a `{{TODO:`-in an "us vs X" page means an unverified fact).

6. **ACT — build the hub.** A `/compare/` (or `/alternatives/`) hub page linking every leaf and
   capturing head terms like `"<us> alternatives"`; cross-link siblings.

7. **VALIDATE — measure.** Track the comparison terms in `rank-tracker-overview`; check AI
   citation with `brand-radar-cited-pages` / `brand-radar-ai-responses` (these pages are a GEO
   play). State each target as metric → threshold → date → how we'd know it failed.

## Outputs
- Generated pages + hub → `projects/<client>/deliverables/comparison/`.
- Supporting fact sheet (per-competitor facts with source URLs) and demand table →
  `projects/<client>/research/`.

## Honest comparison & prompt-pattern engineering

Two principles that raise both credibility and AI-citation rate on these pages:

- **Honest comparison.** For every competitor, explicitly state **what they're good at** and
  **who they're best for** — don't only list where you win. Evaluators (and AI engines) cross-check
  claims against the competitor's own site anyway, so a one-sided page reads as marketing and gets
  discounted; an honest "Competitor X is the better fit if you need {Y}" line is the trust signal
  that lifts conversion on the readers who *aren't* X's ideal customer.
  *How we'd know it failed:* the page reads as one-sided (no competitor-strength rows), bounce on
  the comparison stays high, or `brand-radar-cited-pages` shows AI engines citing the competitor's
  page over ours for `"<us> vs <competitor>"`.

- **Prompt Pattern Engineering — structure pages around real AI query patterns.** Map each page to
  the patterns people (and LLMs) actually phrase: `"best <category> for <use-case>"`,
  `"<us> vs <competitor>"`, `"alternatives to <competitor>"`. Mirror those patterns in H2s, the
  comparison table, and an **FAQPage-schema FAQ** (defer to `schema-markup`) so an answer engine can
  lift a clean, attributable block. Pull the **real objections and use-case language** from
  `projects/<client>/research/voc.md` (customer research / voice-of-customer) so the FAQ answers the
  questions buyers truly ask, not invented ones.
  *How we'd know it failed:* the page targets no verifiable query pattern (zero volume in
  `keywords-explorer-overview` for the mapped phrases), FAQ questions aren't traceable to `voc.md`,
  or the page earns no AI citations in `brand-radar-ai-responses` after one indexation cycle.

## Notes
- **Never fabricate competitor facts.** Every claim about a competitor needs a source URL; mark
  the unknown as `Unknown`. Fairness and accuracy are the moat — and what makes AI engines cite you.
- Keep comparisons current: pricing/features change; date the page and the sources.
- This is the same generator + hub pattern as `programmatic-seo` — see that skill and the playbook
  for the thin-content QA gate and internal-linking architecture.

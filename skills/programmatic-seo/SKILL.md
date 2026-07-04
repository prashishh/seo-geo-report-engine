---
name: programmatic-seo
description: >
  Plan and generate bulk templated pages at scale from one template × a data set
  (e.g. {service} × {city}), with a hard QA gate against thin content. Use when asked
  for "programmatic SEO", to "generate hundreds of pages" or "bulk pages", to build a
  "page template at scale", or for "[X] in [city] pages" / location or directory pages.
  Discovers the keyword matrix, validates real demand per combo, designs one data-rich
  template, plans internal linking + indexation, and writes pages with
  tools/programmatic/generate.py. Also fires on "will these pages get a thin-content penalty"
  and "is our programmatic data defensible". Reference playbooks/programmatic-seo.md for methodology.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# programmatic-seo

Plan + generate many pages from **one template × a data set of rows** without tripping
thin-content / doorway penalties. The IP is in `playbooks/programmatic-seo.md` (when it
works vs backfires, the "unique value per page" bar, the thin-content failure mode); this
skill is the operating procedure. Methodology: **PERCEIVE → ANALYZE → VALIDATE → ACT**,
falsifiable recommendations. Today is **2026-06-23**; write absolute dates.

## Inputs
- `projects/<client>/client.yml` — domain, target keywords, competitors, locale.
- Existing keyword / competitor research in `projects/<client>/research/`.
- Any first-party data the client can supply (pricing, coverage, catalog) in `inputs/`.

Resolve context first: `./bin/mkt config show --project <client>`.

## Workflow

1. **PERCEIVE — discover the keyword matrix (Ahrefs MCP, see `knowledge/ahrefs-mcp-map.md`).**
   From the seed term(s), find the real modifier pattern:
   - `keywords-explorer-matching-terms` — all terms containing the seed (the dominant pattern).
   - `keywords-explorer-related-terms` / `keywords-explorer-search-suggestions` — adjacent
     angles and the autocomplete tail; use to spot a second dimension.
   - `keywords-explorer-volume-by-country` — localize per market before fixing the locale.

2. **ANALYZE — define dimensions / modifiers.** Pick enumerable dimensions whose cross-product
   has demand, e.g. `{service} × {city}`. One strong dimension beats three weak ones. Build the
   candidate matrix as rows (one row = one page).

3. **VALIDATE — confirm real demand per combo and prune.** Pull volume (and SERP type via
   `serp-overview`) for each combination or a representative sample with `keywords-explorer-overview`.
   **Prune thin / no-demand combos and combos you have no data to differentiate.** Record the
   volume threshold and kept-vs-pruned counts (a falsifiable assumption).

4. **VALIDATE — clear the "unique value per page" bar.** Each row must carry data that does NOT
   appear on its siblings (real prices, computed averages, coverage, inventory, verified facts) —
   **data, not swapped words.** Diff two adjacent draft rows: if only the dimension values differ,
   it fails — find more data or cut the pattern. This is the QA gate; do not skip it.

4b. **VALIDATE — clear BOTH penalty gates (hard stop, blocks generation).** Run these before
   designing the template. If either fails for the pattern, do not generate — re-scope or cut.

   - **Gate A — penalty-risk class.** Classify the page type. **Safe-to-scale:** unique-spec
     product pages, real UGC (reviews, Q&A), glossary/data pages with genuine computed data.
     **Risky (block):** thin location pages with no per-city data, unreviewed AI spin, pages
     whose only variation is the swapped dimension value. Observation: which class does the
     pattern fall in? Dependency: a named data source per row. How we'd know it failed: the
     indexed-then-dropped count (step 8) rises after rollout, or pages land in Search Console
     "Crawled — currently not indexed."
   - **Gate B — data-defensibility hierarchy.** Rank the row's data source:
     **Proprietary** (first-party pricing, inventory, usage, real reviews) > **product-derived**
     (computed from the client's own catalog/operations) > **public** (scraped or third-party —
     weakest, trivially replicable). Only generate when each page carries data at or above the
     product-derived tier — data a competitor can't trivially copy. Observation: name the tier per
     field. How we'd know it failed: a competitor reproduces the same page set from public sources.

5. **ACT — design ONE page template.** Templated title/H1 with the real searched phrase, a
   data block that is the page's reason to exist, row-specific FAQs, and (defer to the
   `schema-markup` skill) structured data. Plan **internal linking + hub pages**: a hub per
   dimension linking every leaf, plus sibling cross-links.

6. **ACT — generate the pages.** Build a rows file (`.csv` or `.json` list of dicts) and the
   template (HTML or Markdown with `{placeholder}` fields matching row keys), then:

   ```bash
   python tools/programmatic/generate.py \
     --rows projects/<client>/research/rows.csv \
     --template projects/<client>/research/template.html \
     --out projects/<client>/deliverables/programmatic \
     --slug-field keyword
   ```

   Missing placeholders render as a visible `{{TODO:field}}` marker (not a crash). Slugs are
   auto-deduped (`-2`, `-3`).

7. **QA gate (hard stop).** Grep the output for `{{TODO:` and resolve every one. Re-run the
   diff/standalone-value tests from the playbook (§8). Do not publish a page that's just spun text.

8. **Plan indexation + measurement.** Gradual rollout (batches, dedicated sitemap, monitor
   crawl), then measure: `rank-tracker-overview` for a sample of combos and `gsc-pages` /
   `gsc-keywords` for the URL pattern. Watch the indexed-then-dropped count — if it rises, the
   QA gate failed.

## Outputs
- Plan → `projects/<client>/research/programmatic-plan.md` (dimensions, demand table, kept/pruned
  counts, template design, internal-linking + indexation plan, measurement targets with dates).
- Generated pages → `projects/<client>/deliverables/programmatic/`.

## Notes
- Generation is the cheap last step — demand + per-row data are the work. If you can't name the
  data source that makes each page unique, stop.
- For "us vs competitor" sets use the sibling `comparison-pages` skill (same generator + hub).
- Roll out gradually; a flood of templated URLs at once is itself a spam signal.

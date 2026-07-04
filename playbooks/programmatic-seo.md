# Playbook — Programmatic SEO

The portable methodology behind the `programmatic-seo` and `comparison-pages` skills.
Programmatic SEO means generating many pages from **one template × a data set of rows**
(`{service} × {city}`, `{us} vs {competitor}`, `{integration} integration`, etc.). Done
right it captures a long tail no human could write by hand. Done wrong it ships hundreds of
near-duplicate, thin pages that get the whole pattern (sometimes the whole site)
de-indexed. This playbook is about staying on the right side of that line.

Methodology is the framework standard: **PERCEIVE → ANALYZE → VALIDATE → ACT**, and every
recommendation must be **falsifiable** — state the observation, the dependency, and how
you'd know it failed.

---

## 1. When programmatic works vs backfires

**Works when** all three hold:
- **Real, splittable demand.** People search the combination, not just the head term —
  `"dentist in {city}"` has thousands of city-level searches; `"dentist {adjective}"` does not.
- **A genuine data source per row.** You can put something *true and specific* on each page
  that a reader (and an LLM) would value: real prices, real inventory, real coverage, real
  stats, real reviews. The data — not prose — is the unique value.
- **A repeatable, honest template.** The same structure genuinely fits every row.

**Backfires when:**
- The only thing that changes between pages is a swapped noun ("spun" text). This is the
  classic thin-content failure mode (see §8).
- You generate combinations nobody searches (long-tail × long-tail explosions).
- You have no per-row data, so pages pad with generic filler to look substantial.
- Pages cannibalize each other or an existing money page for the same intent.

Rule of thumb: **if you can't name the data source that makes each page unique before you
generate, stop.** Generation is the cheap last step; demand + data are the work.

---

## 2. Choosing dimensions / modifiers (PERCEIVE → ANALYZE)

A programmatic set is `dimension_A × dimension_B [× ...]`. Discover and size them with the
Ahrefs MCP (see `knowledge/ahrefs-mcp-map.md`):

- `keywords-explorer-matching-terms` — all terms *containing* the seed → reveals the
  modifier pattern people actually use (`"{service} near me"`, `"best {service} {city}"`).
- `keywords-explorer-related-terms` / `-search-suggestions` — adjacent angles and the
  autocomplete tail; good for finding a second dimension.
- `keywords-explorer-volume-by-country` — localize per market before committing to a locale.
- `keywords-explorer-overview` — volume / KD / traffic potential to rank each candidate.

Pick dimensions where (a) each value is a **closed, enumerable set** (50 US states, your 40
service lines, your 12 competitors) and (b) the **cross-product has search demand**, not just
the head term. One strong dimension beats three weak ones.

---

## 3. The "unique value per page" bar (VALIDATE)

This is the gate that separates programmatic SEO from spam. **Every page must carry data
that does not appear on its siblings**, sourced from something real:

- First-party data: your pricing, availability, coverage map, catalog, support hours.
- Aggregated data: counts, averages, ranges you computed (`avg job cost in {city}: $X`).
- External-but-true data: census/population, competitor facts you verified (never invented).
- Genuine media/Q&A: location-specific photos, real FAQs, real reviews.

Test before generating: take two adjacent rows, diff the rendered pages. **If the only
differences are the swapped dimension values, the page fails the bar** — find more data or
cut the pattern. A useful heuristic: a human landing on the page should learn at least one
non-obvious, row-specific fact.

---

## 4. Validating demand per combo + pruning

Don't generate the full cross-product blind. Build the candidate matrix, then:

1. Pull volume for each combination (or a representative sample) via `keywords-explorer-*`.
2. **Prune combos with no / negligible demand** and combos where you have no data to say
   anything true. A 5,000-row matrix that's 80% zero-volume should ship as ~1,000 pages.
3. Note KD / SERP type per surviving combo (`serp-overview`) — some "combos" are answered by
   a map pack or a single brand and aren't worth a page.

Record kept-vs-pruned counts and the volume threshold you used; that threshold is a
falsifiable assumption a reviewer can challenge.

---

## 5. Template design

One template, designed so the data does the differentiating:

- A unique, templated `<title>` / H1 that includes the real searched phrase per row.
- A lead section built from row-specific data, not boilerplate.
- A data block (table / list / map) that is the page's reason to exist.
- Row-specific FAQs and, where applicable, structured data (defer schema to the
  `schema-markup` skill: LocalBusiness, Product, FAQPage, etc.).
- Internal links to the hub and to sibling/related rows (see §7).

Generate with `tools/programmatic/generate.py`: a rows file (`.csv` / `.json` list of dicts)
+ a template with `{placeholder}` fields → one file per row, named by a slug field. Missing
placeholders render as a visible `{{TODO:field}}` marker (not a crash) so QA catches gaps
before publish. Keep CSS literal braces (`{`) safe — the generator only substitutes known
`{key}` tokens.

---

## 6. Deduplication

- **De-dupe slugs** so two rows can't overwrite one file (the generator suffixes `-2`, `-3`).
- **De-dupe intent.** Two combos that target the same query should be one page with a
  canonical, not two competing pages. Check overlap with `keywords-explorer-matching-terms`
  before splitting.
- **De-dupe against existing pages.** Crawl the site (`site-explorer-top-pages` /
  Search Console `gsc-pages`) so the new set doesn't cannibalize money pages.
- Set self-referencing canonicals; never let parameter variants spawn duplicate URLs.

---

## 7. Internal-linking & hub architecture

A flat pile of generated pages doesn't get crawled or pass authority. Build a hierarchy:

- A **hub page** per dimension (`/services/`, `/locations/`, `/compare/`) that links to every
  leaf and explains the set.
- **Cross-links** between siblings (nearby cities, related services, "X vs Y" ↔ "Y vs Z").
- Link the hub from primary navigation / a high-authority page so crawl equity flows down.
- **Comparison-hub pages** (the `comparison-pages` skill) are the same architecture: a
  `/compare/` or `/alternatives/` hub linking each `us-vs-{competitor}` leaf, with the leaves
  cross-linking. The hub also captures head terms like "{us} alternatives".

---

## 8. The thin-content failure mode — and how to test for it

The way this pattern dies: Google (and increasingly AI answer engines) classify the set as
**doorway / thin / spun content**, then suppress or de-index it — often *all* of it at once,
because the pattern is detectable. Symptoms: pages indexed then dropped en masse, "Crawled —
currently not indexed" in GSC, a sitewide ranking dip after a core update.

**Test before you ship:**
- **Diff test (§3):** adjacent rendered pages must differ by more than the swapped tokens.
- **Standalone-value test:** would this page deserve to rank if it were the *only* page on the
  site? If no, it's filler.
- **Word-overlap test:** sample 10 pages; if boilerplate is >~70% of the body, add data or cut.
- **No-data test:** any row where every `{placeholder}` is generic (no first-party / computed
  data) is a thin page — prune it.

QA is a hard gate, not a nicety. Search the generated output for `{{TODO:` markers and resolve
every one before publishing.

---

## 9. Indexation strategy

- **Roll out gradually.** Publish in batches (e.g., 50–100 pages/week), not 2,000 at once — a
  sudden flood of templated URLs is a spam signal and burns crawl budget.
- **Sitemap:** add a dedicated sitemap for the set; submit it; let Google discover at a
  measured pace. Keep low-value/pruned URLs out of it entirely.
- **Monitor crawl + indexation** in Search Console (`gsc-pages`, coverage). If pages crawl but
  don't index, that's the thin-content signal — pause rollout and raise per-page value.
- Block obvious dupes/parameters with canonicals or robots rather than `noindex`-after-the-fact.

---

## 10. Measurement

Tie the program to falsifiable outcomes:

- **Indexation rate** — % of submitted pages indexed (GSC coverage). Target and date it.
- **Ranking** — track a sample of target combos in `rank-tracker-overview`.
- **Traffic & query coverage** — `gsc-pages` / `gsc-keywords` for the generated URL pattern.
- **GEO/citation** — for comparison & data pages, `brand-radar-cited-pages` / `-ai-responses`
  to see whether answer engines cite the set.
- **Leading red flag** — indexed-then-dropped count. If it rises, the QA gate (§8) failed;
  stop and fix value before scaling further.

State each target as "metric → threshold → by date → and here's how we'd know it failed."

---
name: technical-seo-audit
description: >
  On-site technical SEO audit — crawlability, indexation, sitemaps/robots, structured data,
  internal linking, and page experience. Use when asked to "run a technical SEO audit", "do a
  site audit", "find crawl errors", "fix indexation issues", "why isn't this page indexed",
  or "fix technical SEO". Produces a severity-ranked issue list with a fix, a falsifiable test,
  and a leading indicator for each. Defers Core Web Vitals / page-speed to dedicated skills.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# technical-seo-audit

Finds what stops a site from being crawled, indexed, and understood — then ranks fixes by impact.
Engine is Ahrefs **Site Audit** (see `knowledge/ahrefs-mcp-map.md`); call `doc` before first use.
For Core Web Vitals / load speed, **defer to the user's existing `core-web-vitals` and
`performance` skills** — name them in the report and don't re-derive their work here.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — pull the crawl.** Resolve project (`./bin/mkt config show --project <client>`);
confirm `ahrefs.project_id` in `client.yml`. List audits with `site-audit-projects`; pull issues
with `site-audit-issues` (grouped by severity). Inspect specific pages with
`site-audit-page-content` and `site-audit-page-explorer`. Cross-check what's actually indexed/
performing with `gsc-pages` and `gsc-performance-by-position` (owned truth beats inference).

**ANALYZE — six dimensions.** Bucket every finding into:
1. **Crawlability** — robots.txt rules, crawl traps/depth, redirect chains, 4xx/5xx, orphan pages.
2. **Indexation** — noindex conflicts, canonical conflicts/duplicates, thin/index-bloat pages,
   pagination & hreflang correctness, www/non-www & http/https consolidation.
3. **Sitemaps & robots** — XML sitemap present, valid, fresh, referenced in robots.txt; no
   noindexed/redirected/4xx URLs in the sitemap. See **Sitemap-validation pass** below.
4. **Structured data** — presence/validity of JSON-LD (hand depth to the `schema-markup` skill).
5. **Internal linking** — orphan/under-linked money pages, weak hub→spoke flow, anchor relevance.
   Use `site-explorer-pages-by-internal-links` and `site-explorer-linked-anchors-internal`.
6. **Page experience** — mobile-friendliness, HTTPS/mixed content, intrusive interstitials.
   For CWV/LCP/INP/CLS and speed, **invoke `core-web-vitals` and `performance`** — reference, don't
   duplicate.
7. **Image SEO** — alt text, intrinsic dimensions, lazy-loading, modern formats. See
   **Image-SEO sub-audit** below.

## Image-SEO sub-audit
Crawl `<img>`/`<picture>` markup (Grep rendered HTML or `site-audit-page-content`). Flag each as
falsifiable findings — observation + fix + "how we'd know it failed":
- **Alt text** — every content image has descriptive, non-keyword-stuffed `alt`; decorative images
  use `alt=""`. *Failed if:* re-crawl still lists images with missing/empty alt on content pages.
- **Intrinsic dimensions** — `width`/`height` set on every `<img>` (prevents CLS — note, don't
  re-measure; CLS scoring stays with `core-web-vitals`). *Failed if:* `<img>` tags lack both attrs.
- **Lazy-loading** — below-the-fold images use `loading="lazy"`; the LCP/hero image does **not**.
  *Failed if:* hero is lazy-loaded or below-fold images load eagerly.
- **Modern formats** — serve a `<picture>` with progressive fallback AVIF → WebP → JPEG/PNG.
  *Failed if:* large hero images ship only as legacy JPEG/PNG with no `<source>` alternatives.
- **AI-image labeling** — AI-generated images carry IPTC `DigitalSourceType`
  (`trainedAlgorithmicMedia`) metadata. *Failed if:* known AI assets ship without the IPTC tag.
- **Leading indicator** — Google Images impressions in `gsc-performance-history` (filter Image),
  and image-bytes drop, move before image-pack rankings.

## Sitemap-validation pass
Fetch each sitemap (and any index) and validate before trusting it as crawl truth:
- **Well-formed XML + 200** — sitemap parses and returns HTTP 200; index children resolve.
  *Failed if:* fetch is non-200 or XML doesn't parse.
- **Size limits** — ≤ 50,000 URLs and ≤ 50 MB uncompressed per file; split via a sitemap index
  past that. *Failed if:* any single file exceeds either cap.
- **Canonical/noindex compliance** — every listed URL is canonical, returns 200, and is **not**
  noindexed/redirected/4xx (cross-check `gsc-pages`). *Failed if:* re-crawl finds noindexed,
  redirected, or error URLs still listed.
- **Leading indicator** — "Discovered/Submitted" counts in `gsc-pages` converge on the sitemap's
  URL count once invalid entries are removed.

**VALIDATE — every issue falsifiable.** For each finding record:
- **Observation** — the exact signal (tool + metric + count + date, e.g. "`site-audit-issues`
  2026-06-23: 142 URLs return 301→301 chains").
- **Fix** — the concrete change (one sentence).
- **How we'd know it failed** — a re-test that would still trip: e.g. "re-run `site-audit-issues`;
  chain count should hit 0" or "page enters GSC 'Indexed' in `gsc-pages` within 2 crawls."
- **Leading indicator** — what moves first if the fix works (crawled-pages count, indexed count in
  `gsc-pages`, impressions in `gsc-performance-history`) before rankings/traffic catch up.

**ACT — output.** Write `projects/<client>/research/technical-audit.md`:
- A severity table — **Critical / High / Medium / Low** — each row: issue, affected URLs/count,
  dimension, fix, falsifiable test, leading indicator, effort.
- Critical = blocks indexing or serves wrong content to Google. Order the fix list by
  impact-per-effort. End with a "verify after deploy" checklist (the re-tests above).

## Notes
- Trust owned data: a page Ahrefs flags but `gsc-pages` shows indexed-and-ranking is lower priority.
- Don't recommend speculative fixes — tie each to an observed signal you can re-measure.
- If a tool returns `render_with` metadata in chat, call the named render tool; write the audit
  itself to the markdown file above.
- Reference upstream: AgriciDaniel/claude-seo `seo-technical` — adapted to Ahrefs Site Audit + GSC
  and to our PERCEIVE→ANALYZE→VALIDATE→ACT falsifiability; CWV/speed delegated to local skills.

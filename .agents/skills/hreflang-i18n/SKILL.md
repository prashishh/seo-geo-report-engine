---
name: hreflang-i18n
description: >
  Audit and generate hreflang + international-SEO setup with full-mesh return-tag validation.
  Use when asked about "hreflang", "international SEO", "multilingual SEO", "multi-language
  site", "x-default", "language targeting", "locale targeting", "why is the wrong language
  ranking", "duplicate content across languages", or "ccTLD / subfolder / subdomain for
  languages". AUDIT mode crawls a page set and runs 8 checks (self-reference, bidirectional
  return tags, x-default, ISO 639-1 / 3166-1 format, canonical-hreflang alignment,
  protocol/host consistency, cross-domain correctness, locale-content parity). GENERATE mode
  emits hreflang for HTML <link>, HTTP header, or XML sitemap, plus a content-parity /
  cultural-adaptation checklist. technical-seo-audit does NOT do full-mesh validation — this does.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# hreflang-i18n

Full-mesh hreflang validation and generation for multilingual / multi-region sites. The hard part
is the **mesh**: hreflang only works if every locale variant points at every other variant *and*
each gets a matching return tag back. One missing return tag silently voids the whole cluster, and
Google falls back to ranking the wrong language. This skill finds those breaks and emits a correct
mesh. Prefer Ahrefs MCP (see `knowledge/ahrefs-mcp-map.md`); call `doc` before first use of a tool.
Methodology in `playbooks/i18n-seo.md`.

**Example use case:** a client targeting `en` + `ne` (+ `hi`) across diaspora corridors
has zero i18n coverage — run AUDIT first to baseline, then GENERATE the mesh.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — gather.** Resolve the project (`./bin/mkt config show --project <client>`). Read
`client.yml` for `languages` / `markets` / `domain` and the target URL set (the page and its
locale variants). Decide the URL-structure pattern in use — ccTLD, subfolder (`/ne/`), or subdomain
(`ne.`) — because the mesh and x-default rules differ per pattern.
- Crawl the page set: `site-explorer-crawled-pages` or `site-audit-page-content` /
  `site-audit-page-explorer` to pull each page's existing `<link rel="alternate" hreflang>` set,
  canonical, and HTTP headers. If a URL isn't in an Ahrefs project, fall back to `WebFetch` to read
  the live `<head>` and `Link:` headers directly. Note which implementation method is in use.

**ANALYZE — run the 8 checks** across the full cluster (record pass/fail + offending URL per check):
1. **Self-reference present** — every page lists its own URL with its own hreflang. Missing → cluster
   may be ignored.
2. **Bidirectional return tags** — if A→B, then B→A must exist (full mesh). Build the adjacency
   matrix; any asymmetric pair is invalid and Google drops it.
3. **x-default present** — a `hreflang="x-default"` entry exists for unmatched users / locale
   selector; flag if absent on a site that needs one.
4. **ISO format valid** — language is ISO 639-1 (`en`, `ne`, `hi`), optional region is ISO 3166-1
   alpha-2 (`en-GB`, `ne-NP`). Reject `en-UK`, `en_us`, made-up codes, region-only without language.
5. **Canonical-hreflang alignment** — each page's `rel=canonical` is self-referential and matches the
   hreflang-listed URL exactly; a canonical pointing at another locale silently cancels hreflang.
6. **Protocol/host consistency** — all hreflang URLs use one protocol + host form (https, no www/non-www
   or trailing-slash drift); inconsistency fragments the mesh.
7. **Cross-domain correctness** — for ccTLD/subdomain setups, return tags resolve across domains and
   each is reachable (200, not redirected/blocked).
8. **Locale-content parity** — the variant is genuinely translated (not the source language with a
   swapped URL), and is indexable (no `noindex`, not redirected). Sample bodies via the crawl/WebFetch.

**VALIDATE — every finding falsifiable.** For each issue state:
- **Observation** — the exact tag/URL and the tool + date it came from (e.g. "`ne-NP`→`en` present but
  no return tag on `/en/` page — `site-audit-page-content`, 2026-06-23").
- **Dependency** — what must hold to count as fixed (e.g. "every pair symmetric", "canonical
  self-referential", "variant returns 200 and indexable").
- **How we'd know this failed** — a leading indicator: e.g. "wrong-language URL still ranking for a
  geo query in `rank-tracker-serp-overview` at 4 weeks" or "GSC International Targeting / hreflang
  errors persist", or "`site-audit-issues` still flags the hreflang error after recrawl."

**ACT — output.** Two modes; write under `projects/<client>/`:

- **AUDIT →** `research/hreflang-audit.md`: the 8-check results table, an issue list (one row per
  break with the offending URL, a concrete fix, and the falsifiable test above), and the per-method
  recommendation (which of the three implementations the site should standardize on).
- **GENERATE →** `deliverables/hreflang-tags.html` and/or `deliverables/hreflang-tags.xml`, emitting a
  correct full mesh for the chosen method (pick by structure: prefer HTML `<link>` for small sites,
  HTTP header for non-HTML/PDF, XML sitemap for large or template-driven sites). Include x-default.
  Also write a **content-parity / cultural-adaptation checklist** (translation completeness, currency
  / date / number formats, locale-specific CTAs, transliteration vs translation for `ne`/`hi`, RTL
  N/A here) into the audit doc so the client knows tags alone are not enough.

### The three implementation methods (emit exactly one cluster, three ways)

- **HTML `<link>`** — `<link rel="alternate" hreflang="ne-NP" href="https://x.com/ne/" />` in `<head>`,
  one per variant + self + x-default. Simplest; only for HTML pages.
- **HTTP header** — `Link: <https://x.com/ne/>; rel="alternate"; hreflang="ne-NP", …`. Use for PDFs /
  non-HTML; one combined header listing every variant.
- **XML sitemap** — each `<url>` carries `<xhtml:link rel="alternate" hreflang>` for every variant.
  Best at scale; one sitemap entry per page, mesh expressed in markup, no template edits per page.

## Notes
- A mesh is all-or-nothing: validate symmetry before shipping — a single missing return tag voids the
  cluster. Re-crawl with `site-audit-issues` after the fix to confirm the error clears.
- `en` (language-only) is fine when not region-targeting; add region (`en-GB`) only when you serve
  distinct regional content, or you fragment authority.
- x-default should point at the locale selector or the most-generic version, not an arbitrary locale.
- Hand parity gaps to `content-brief` for translated pages; hand wrong-language ranking symptoms to
  `rank-tracking` to confirm the fix landed.
- Adapted from claude-seo `seo-hreflang`, marketingskills `seo-audit` (hreflang/canonical checklist),
  and sanity-aeo `technical-seo.md` — here made Ahrefs-backed with full-mesh return-tag validation.

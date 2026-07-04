---
name: schema-markup
description: >
  Structured data / JSON-LD — detect existing schema, recommend the right types, generate
  ready-to-paste JSON-LD, and validate it. Use when asked about "schema markup", "structured
  data", "JSON-LD", "rich results / rich snippets", "FAQ schema", "Product schema", "Organization
  schema", or "add schema to this page". Covers Organization, Product, Article, FAQ/QAPage,
  Breadcrumb, and LocalBusiness, and ties structured data to GEO/AI citability.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# schema-markup

Detects what schema a page already has, recommends the right types for the page's purpose, and
generates **valid, ready-to-paste JSON-LD**. Ties to GEO: structured data and Q&A markup make a
page easier for AI answer engines to parse and cite (reference the `geo-audit` skill). Uses Ahrefs
Site Audit to find pages and check existing markup (see `knowledge/ahrefs-mcp-map.md`).

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — detect.** Resolve project (`./bin/mkt config show --project <client>`). Identify the
page(s); read their content with `site-audit-page-content` / `site-audit-page-explorer`, or fetch
directly with `WebFetch`. Detect existing structured data in **JSON-LD** (`<script type=
"application/ld+json">`), Microdata (`itemscope`/`itemprop`), and RDFa. Note page type, primary
entity, and any markup already present (so we extend, not duplicate).

**ANALYZE — recommend the right types.** Match schema to page purpose:
- **Organization / LocalBusiness** — home/about/contact (LocalBusiness for a physical/local
  business; pairs with the `local-seo` skill — include geo-coordinates).
- **Product** (+ `Offer`, `AggregateRating`) — product/PDP pages.
- **Article / BlogPosting** — editorial/blog content (author, datePublished, publisher).
- **BreadcrumbList** — any page with a navigation trail.
- **FAQPage / QAPage** — genuine Q&A. Note: FAQ *rich results* are de-emphasized in Google SERPs,
  but the markup still helps AI answer engines parse and cite the page — keep it for GEO.
Recommend only types the page's content truthfully supports. **Tie type choice to AI
extractability:** FAQPage / HowTo / QAPage blocks are the ones AI answer engines most often lift
verbatim *as the answer* — prefer them on any page whose intent is a question or a procedure. Prefer **JSON-LD** (Google's
preferred format) and embed it in **server-rendered HTML** — JS-injected schema is processed late
and can be missed, especially for time-sensitive Product/Offer data.

**GEO tie-in.** Clean Organization, Article author/publisher, and FAQ/QAPage markup give AI answer
engines explicit entities and quotable Q&A — improving citability. Pair with `content-brief`'s
self-contained answer blocks. For the AI-visibility measurement, reference the `geo-audit` skill
(Ahrefs Brand Radar — `brand-radar-cited-pages`).

**VALIDATE — falsifiable.** Generate each block with required + recommended properties, real
verifiable values (clearly-marked `PLACEHOLDER` where data is unknown), absolute URLs, and ISO-8601
dates. Check: `@context` present, valid `@type`, no placeholder text shipped, no relative URLs.
For each recommendation state: **Observation** (page type + what's missing), **Dependency** (the
markup must match visible on-page content — Google penalizes mismatch), and **How we'd know it
failed** — a leading indicator: "Rich Results Test / Search Console 'Enhancements' still reports
the item as invalid", or for GEO, "page still absent from `brand-radar-cited-pages` after re-crawl."

**ACT — output.** Write `projects/<client>/research/schema-recommendations.md`: per page —
detected markup, recommended types, the **ready-to-paste JSON-LD** (in fenced code blocks),
validation notes, and the falsifiability block. Tell the user to run each block through Google's
Rich Results Test / Schema.org validator before deploy, and to put it in the server-rendered HTML.

## E-E-A-T author-document model

For Article / BlogPosting and any YMYL page, model the author as a canonical schema.org `Person`
kept in **one source-of-truth document** — separate from anything UI-only:
- **Canonical `Person` (goes into JSON-LD):** `name`, `jobTitle` (role), `description` (bio),
  `knowsAbout[]` / `hasCredential[]` (`EducationalOccupationalCredential`) for credentials, and
  `sameAs[]` — authoritative identity URLs (LinkedIn, ORCID, Crunchbase, Wikidata) that let AI
  engines resolve the author to a real entity.
- **UI-only `socialLinks[]`:** decorative profile/share links for the page chrome. Keep these
  **out of** the `Person` schema — only identity-establishing URLs belong in `sameAs[]`; mixing in
  marketing links dilutes the entity signal.
- **YMYL sign-off:** for health/finance/legal pages, add a named expert `reviewedBy` (`Person`)
  plus a dated `reviewer` line in visible copy. Schema and on-page byline/reviewer must match.

**Observation** — YMYL page with a generic or no author entity. **Dependency** — every `sameAs[]`
URL must actually reference the same person and be reachable; the visible byline + reviewer must
match the schema. **How we'd know it failed** — Rich Results Test reports the `Person`/`author` as
incomplete, the author still fails to resolve to a known entity (no Knowledge-Panel / Wikidata
match), or the page stays absent from `brand-radar-cited-pages` for expertise-led queries.

## Validating dynamically-injected JSON-LD

If the schema is added client-side (Google Tag Manager, React/Vue hydration, a `<script>` that
writes the LD-JSON after load), a **static crawl will not see it** — crawlers fetch raw HTML and
strip JS. Validate the *rendered DOM*, not the source:
- Use Google's **Rich Results Test / URL Inspection** (they render JS) or a **real browser** —
  inspect `document.querySelectorAll('script[type="application/ld+json"]')` in DevTools after load.
- Treat a "missing schema" finding from `site-audit` / any static crawl as **unconfirmed** until
  checked in a rendered view — it is a common false positive for JS-injected markup.

**Observation** — static crawl reports no schema, but the page renders it via JS. **Dependency** —
Googlebot must actually render and index the injected block (server-rendered is still safer for
time-sensitive Product/Offer). **How we'd know it failed** — Rich Results Test on the live URL
shows the item present and valid even though the static crawl flagged it missing.

## Notes
- Never invent ratings, prices, or reviews to satisfy a schema's required fields — mark unknowns
  as placeholders and tell the client what real data to supply.
- One JSON-LD `<script>` can hold a `@graph` of multiple connected entities — prefer that over
  many scattered scripts. Use absolute dates (today 2026-06-23).
- Reference upstream: AgriciDaniel/claude-seo `seo-schema` — adapted to Ahrefs Site Audit, our
  falsifiability, and GEO citability.

---
name: local-seo
description: >
  Local SEO and Google Business Profile optimization — GBP, NAP/citation consistency, local
  landing pages, reviews strategy, and map-pack rank tracking. Use when asked about "local SEO",
  "Google Business Profile", "GBP", "the map pack", "rank in <city>", "local citations", "NAP
  consistency", or "get more reviews". Produces a prioritized fix list for winning the local pack
  and local organic results in target cities.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# local-seo

Wins the local pack and local organic for a business's target cities. Covers Google Business
Profile, citation/NAP health, local landing pages, reviews, and pack tracking. Uses Ahrefs MCP for
the rank/keyword side (see `knowledge/ahrefs-mcp-map.md`); call `doc` before first use.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — establish the footprint.** Resolve project (`./bin/mkt config show --project
<client>`); read `client.yml` for the canonical **NAP** (name/address/phone), service areas, and
target cities. Classify the business: **brick-and-mortar** (physical address), **service-area
business / SAB** (no public address), or **hybrid** — this changes GBP setup and page strategy.
Pull tracked locations with `management-locations`; pull local rankings with `rank-tracker-overview`
and `rank-tracker-serp-overview` filtered to each city/location, and competitor positions via
`rank-tracker-competitors-overview`. Capture the live pack with `serp-overview` (location-set) +
`WebSearch`/`WebFetch` for GBP fields that aren't in Ahrefs.

**ANALYZE — five levers.**
1. **GBP optimization** — correct **primary category** (the single biggest local lever; a wrong one
   suppresses the pack), secondary categories, complete services/products, hours, photos, posts,
   and verification. Geo-coordinates accurate to 5+ decimals.
2. **NAP / citation consistency** — name/address/phone identical across the site, GBP, and top
   directories (Apple Business Connect, Bing Places, BBB, industry/local citations). Inconsistency
   = the most common pack-ranking drag. List every discrepancy found.
3. **Local landing pages** — one credible page per city/service the business genuinely serves
   (not doorway/spam pages); city in title/H1/URL, embedded map, local proof. Dedicated service
   pages are a top local organic factor.
4. **Reviews strategy** — rating health (target 4.5+), **velocity** (steady fresh reviews — long
   gaps correlate with pack decline), a review-generation ask in the customer flow, and owner
   responses to all reviews.
5. **Local pack tracking** — track the money terms per city in `rank-tracker-overview`; watch
   competitor movement with `rank-tracker-competitors-pages` / `-stats`.

**VALIDATE — falsifiable.** Each fix gets: **Observation** (the gap + source, e.g. "primary
category is 'Contractor' not 'Roofing Contractor' per GBP, 2026-06-23"), **Dependency** (what must
hold — proximity to searcher, page genuinely serves that city), and **How we'd know it failed** —
a leading indicator: "pack position for '<service> <city>' flat in `rank-tracker-overview` 6 weeks
post-fix", or "NAP still mismatched on N directories at re-audit". Be honest that proximity
dominates pack ranking — some queries can't be won from outside the radius.

**ACT — output.** Write `projects/<client>/research/local-seo.md`: a prioritized fix table
(High/Med/Low) — fix, lever, observation, falsifiable test, leading indicator, effort — plus a
per-city snapshot (current pack/organic position vs top competitor) and a NAP/citation discrepancy
list with the canonical NAP to enforce.

## Geo-grid map-pack simulation, cross-platform NAP & review integrity

Adapted from claude-seo `seo-maps` — three deeper checks that extend the levers above.

1. **Geo-grid (7×7) pack visibility.** A single tracked point hides proximity bias — pack position
   swings block-by-block. Lay a grid of coordinates (e.g. 7×7 ≈ 49 points) across each target city
   and simulate the pack rank at every node (one location-set `serp-overview` /
   `rank-tracker-serp-overview` call per coordinate). Output a per-node rank map → derive **ATGR**
   (average total grid rank) and **% of grid in top-3**. This is the right read for diaspora-corridor
   targeting: measure visibility across the whole corridor city, not one pin.
   *Observation:* "ATGR 6.4, only 18% of 49 nodes in top-3 for '<service> <city>', 2026-06-23."
   *Dependency:* node coordinates fall inside the area the business truthfully serves.
   *How we'd know it failed:* ATGR / top-3 grid share flat across re-runs 6 weeks post-fix.
2. **Cross-platform NAP verification.** Verify the canonical NAP on **Google, Bing Places, Apple
   Business Connect, and OpenStreetMap** (OSM feeds many AI assistants and map apps) — not the site
   alone. List each platform's name/address/phone/geo and flag every mismatch.
   *Observation:* "phone differs on Apple; OSM missing the listing entirely, 2026-06-23."
   *How we'd know it failed:* discrepancy count > 0 at re-audit, or AI answers still cite stale NAP.
3. **Review velocity + fake-review pattern check.** Beyond rating, track **velocity** (reviews/month
   trend; flag gaps) and scan for **inauthentic patterns** — bursts of same-day reviews, repeated
   phrasing, reviewer accounts with one review, or a rating spike decoupled from order volume.
   Genuine velocity lifts the pack; a fake-review burst risks filtering/suspension.
   *Observation:* "12 five-star reviews in one day from single-review accounts, 2026-06-23."
   *How we'd know it failed:* flagged reviews disappear (Google filter) or velocity reverts to zero.

## Notes
- AI assistants source local data from Bing/Apple/Yelp/BBB, **not directly from GBP** — fixing
  citations also lifts AI-answer visibility; cross-reference the `geo-audit` skill for that read.
- Don't create doorway pages — only cities the business truthfully serves.
- If a tool returns `render_with` metadata in chat, call the named render tool; write the report
  to the markdown file above. Use absolute dates (today 2026-06-23).
- Reference upstream: AgriciDaniel/claude-seo `seo-local` / `seo-maps` — adapted to Ahrefs Rank
  Tracker locations + our falsifiability.

---
name: internal-linking
description: >
  Plan strategic internal-link architecture — hub-and-spoke topic clusters, orphan-page rescue,
  anchor-text distribution, and link-equity flow to money pages. Use when asked for "internal
  linking", "link architecture", "topic clusters", "hub and spoke", "orphan pages", "site
  architecture", "siloing", "anchor text strategy", "distribute link equity", or "how should
  pages link to each other". Takes a keyword-research cluster output + the client domain and
  produces an internal-link matrix (from→to with recommended anchors), an orphan-rescue list, and
  a prioritized "add these links first" action list — each link recommendation falsifiable.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# internal-linking

Designs the **link architecture** that connects keyword clusters and programmatic pages into
crawlable, equity-flowing silos — and routes that equity toward money/conversion pages. This is
*planning*, not auditing: `technical-seo-audit` flags broken/orphaned links as issues; this skill
decides the target graph. Prefer Ahrefs MCP (`knowledge/ahrefs-mcp-map.md`); call `doc` on a tool
before first use. Reuse the hub-spoke seed in `playbooks/programmatic-seo.md` §7.

## Inputs

- `projects/<client>/research/keyword-map.md` + `keywords.csv` (from `keyword-research`) — clusters,
  intent, target pages. One cluster = one pillar candidate.
- `client.yml` — domain, money/conversion pages (sales, pricing, demo, signup, key services).

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — map the current graph.** Resolve project (`./bin/mkt config show --project <client>`).
Pull the live internal-link structure:
- `site-explorer-pages-by-internal-links` — inbound internal links per URL. Sort it: the long tail
  with **0–1 inbound internal links = orphans / near-orphans**; the top fat-head pages are where
  equity is hoarded.
- `site-explorer-linked-anchors-internal` — the internal anchor-text profile (what text currently
  points where). Flags exact-match over-optimization and generic "click here / read more" waste.
- `site-explorer-pages-by-traffic` + `site-explorer-top-pages` — which pages actually hold equity
  and traffic, so we link *from* strength *into* targets.
- Cross-check orphans against `keywords.csv` — an orphan that's a real cluster target is high-value
  rescue; an orphan with no demand may just be prunable.

**ANALYZE — design the target graph.**
- **Cluster → hub-and-spoke.** Each keyword-research cluster becomes one **pillar (hub)** ↔ N
  **spokes**. Pillar = the broad/commercial head target; spokes = the informational long-tail pages.
  Where `keyword-research` used SERP-overlap to group terms, that same overlap defines which spokes
  are sibling-related and should cross-link.
- **Link rules** (the silo): every spoke links **up** to its pillar; pillar links **down** to every
  spoke; siblings within a cluster cross-link where contextually relevant; pillars link laterally to
  adjacent pillars only when topically justified (avoid diluting the silo).
- **Equity flow to money pages.** Identify high-equity/high-traffic pages from PERCEIVE and route
  contextual links **into** money/conversion pages from them. Money pages are the *sink* of the
  graph, not just nav-linked.
- **Anchor distribution.** Vary anchors per target: a mix of exact, partial, and
  semantic/branded — relevance-scored to the destination's primary keyword. Replace generic anchors
  surfaced by `-linked-anchors-internal`. No single exact-match anchor should dominate a target
  (over-optimization risk).
- **Cannibalization flag.** If two pages target the same intent/keyword (same `target_page` collision
  in `keywords.csv`, or both rank for one term in `site-explorer-organic-keywords`), don't cross-link
  them as equals — pick the canonical, point the other's equity *into* it, and flag for consolidation.

**VALIDATE — every link recommendation falsifiable.** For each prioritized link state:
- **Observation** — why it's recommended (e.g. "target has 0 inbound internal links per
  `site-explorer-pages-by-internal-links` 2026-06-23; it's the pillar for cluster X").
- **Dependency** — what must hold (source page is indexed and has equity; anchor is contextually
  relevant; not a cannibalization pair).
- **How we'd know this failed** — leading indicator: e.g. "after adding the link, target stays at 0–1
  internal links / un-crawled at next `site-audit-issues` run", or "target still not in index at
  4 weeks (GSC)", or "pillar's tracked terms don't move in `rank-tracker-overview` at 8 weeks."

## ACT — output

Write `projects/<client>/research/internal-linking.md` containing:
- **Internal-link matrix** — a `from → to` table: source URL, destination URL, recommended anchor
  (relevance-scored), link type (spoke→pillar / pillar→spoke / sibling / →money-page), priority.
- **Orphan-rescue list** — every 0–1-inbound-link page that maps to a real cluster target, with the
  2–3 best source pages to link it from.
- **"Add these links first" action list** — ranked by equity impact (links into money pages and
  orphan pillars first), each carrying the VALIDATE block above.
- **Cannibalization flags** — page pairs to consolidate/canonicalize before linking.

## Notes

- Inputs from `keyword-research`; hand orphan/cannibalization findings to `technical-seo-audit` and
  feed the silo design back into `programmatic-seo` / `comparison-pages` hub builds.
- Cap links per page sensibly (don't bury the silo in a 200-link footer); contextual in-body links
  pass more value than boilerplate.
- This skill plans the graph — it doesn't edit the live site. Implementation is a CMS task.
- Adapted from claude-seo (`seo-cluster` hub-spoke matrices, `seo-page` orphan audit),
  seo-geo-claude-skills (`internal-linking-optimizer`), marketingskills (`site-architecture`) —
  here grounded in Ahrefs internal-link + anchor tools and the framework's falsifiability discipline.

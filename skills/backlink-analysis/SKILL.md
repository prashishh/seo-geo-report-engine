---
name: backlink-analysis
description: >
  Assess a domain's link profile health and growth, surface link-building targets, and find
  reclaim opportunities. Use when asked for "backlink analysis", "link profile", "referring
  domains", "who links to us", "link building targets", "link prospects", "broken link
  building", "link gap vs <competitor>", or "are our backlinks healthy". Produces
  research/backlinks.md with a prioritized prospect list (domains linking to competitors not us)
  plus broken-link reclaim targets.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# backlink-analysis

Reads a domain's backlink profile, judges its **health and growth**, and turns competitor link
data into a prioritized prospect list. Output is `projects/<client>/research/backlinks.md`.
Ahrefs MCP is the engine (see `knowledge/ahrefs-mcp-map.md`).

Methodology is **PERCEIVE → ANALYZE → VALIDATE → ACT**. Every prospect is falsifiable: state why
the link is plausible (it links to ≥2 competitors / it's a dead page we can replace), and the
signal that would tell us the outreach failed.

## Inputs
- `projects/<client>/client.yml` — `domain`, `competitors[]`, `ahrefs.project_id`. Resolve with
  `./bin/mkt config show --project <client>`. Today is absolute (e.g. `2026-06-23`); call `doc`
  on a tool before first use; monetary values are USD cents (÷100).
- Prior snapshots in `data/` (refdomains history) to measure growth.

## Workflow

### 1. PERCEIVE — our profile and its trend
- `site-explorer-backlinks-stats` + `site-explorer-referring-domains` — total backlinks, ref
  domains, DR distribution of linking domains.
- `site-explorer-refdomains-history` — ref-domain growth/decay over the window (the health
  signal: net new linking domains, not raw backlink count).
- `site-explorer-anchors` / `-linked-anchors-external` — anchor distribution (over-optimized
  exact-match or branded/natural?).
- `site-explorer-pages-by-backlinks` — our own most-linked pages (what earns links today).

### 2. ANALYZE — health verdict
- **Velocity** — is ref-domain growth positive and steady, or spiky/declining? Spikes can be
  spam; declines can be link rot.
- **Quality** — share of links from DR≥30 domains vs low-DR/spam; topical relevance.
- **Anchors** — flag exact-match anchor ratios that risk over-optimization.
- State a one-line verdict (healthy / at-risk / thin) with the numbers behind it.

### 3. VALIDATE — find prospects (link gap) and reclaim targets
- **Link gap** — for each competitor run `site-explorer-referring-domains`; find domains linking
  to **≥2 competitors but not us** (warm prospects). Use `site-explorer-pages-by-backlinks` on
  competitors to see which page earned each link (the content you'd pitch). For a full gap with
  scoring, **coordinate with `competitor-analysis`** — reuse its backlink-gap pull, don't
  duplicate it.
- **Broken-link reclaim** — `site-explorer-broken-backlinks` on our domain (lost links to
  reclaim) and on competitors (dead pages with live links = recreate-and-pitch targets).

### 4. ACT — write the prioritized list
Write `projects/<client>/research/backlinks.md` (dated):
1. **Profile health** — ref domains, growth, DR mix, anchor profile, the one-line verdict.
2. **Prioritized prospect list** — domain · linking-DR · #competitors it links to · the
   competitor page earning the link · the asset we'd pitch · priority tag (`warm` / `cold`).
   Rank warm multi-competitor links first.
3. **Broken-link / reclaim targets** — dead URL · referring domain · our replacement asset.
4. **Next moves** — each falsifiable: bet → dependency → leading indicator (e.g. "Bet: 10
   warm prospects yield 3 links in 6 weeks; fails if <1 placed after first outreach round").

## Notes
- **Data priority: Ahrefs MCP > CLI connectors > web.** Web only to verify a live page/contact.
- Feeds **`report-generator`** (ref-domain growth = authority KPI) and **`kpi-dashboard`**
  (DR + referring domains, the authority layer). Hands the prospect list to outreach.
- Keep the list tight and real — 20–40 scored prospects beat a 1,000-row export.

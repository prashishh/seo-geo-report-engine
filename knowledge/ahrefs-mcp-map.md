# Ahrefs MCP — capability map

The Ahrefs MCP server is **already connected** (no key needed). It is the framework's
primary live data engine. Skills should prefer these tools over CLI connectors.

**Always call `doc` for a tool before first use** to learn its exact params.
**Monetary values are USD cents — divide by 100.**
When a tool response carries `render_with` metadata, you MUST call the named render tool
(`render-data-table`, `render-scorecard`, `render-time-series-chart`) — don't dump raw rows.

> Tool names below omit the long server prefix `mcp__d192ea5b-…__`. They are the suffixes.

## Keyword research
| Tool | Use |
|---|---|
| `keywords-explorer-overview` | Volume, KD, CPC, traffic potential for seed keywords |
| `keywords-explorer-matching-terms` | "All keywords containing X" expansion |
| `keywords-explorer-related-terms` | Semantically related / "also rank for" |
| `keywords-explorer-search-suggestions` | Autocomplete-style suggestions |
| `keywords-explorer-volume-by-country` | Localize volume per market |
| `keywords-explorer-volume-history` | Seasonality / trend of a term |

## Competitor & organic intelligence (Site Explorer)
| Tool | Use |
|---|---|
| `site-explorer-organic-keywords` | Keywords a domain/URL ranks for |
| `site-explorer-organic-competitors` | Who competes in organic for a domain |
| `site-explorer-top-pages` / `-pages-by-traffic` | A competitor's best pages |
| `site-explorer-metrics` / `-metrics-history` | Org traffic, value, keyword counts over time |
| `site-explorer-domain-rating` / `-domain-rating-history` | DR strength + trend |
| `site-explorer-keywords-history` | Keyword count history |
| `site-explorer-ai-responses-count` | How often a domain appears in AI answers |

## Backlinks
| Tool | Use |
|---|---|
| `site-explorer-all-backlinks` | Backlink list |
| `site-explorer-referring-domains` / `-refdomains-history` | Ref domains + growth |
| `site-explorer-broken-backlinks` | Reclaim / competitor broken-link targets |
| `site-explorer-anchors` / `-linked-anchors-*` | Anchor profile |
| `site-explorer-pages-by-backlinks` | Top linked pages (link-building targets) |

## Rank tracking
| Tool | Use |
|---|---|
| `rank-tracker-overview` | Tracked-keyword positions for the project |
| `rank-tracker-serp-overview` | SERP composition for a tracked term |
| `rank-tracker-competitors-overview` / `-domains` / `-pages` / `-stats` | Position vs competitors |

## GEO / AI search — **Brand Radar** (the GEO engine)
| Tool | Use |
|---|---|
| `brand-radar-mentions-overview` / `-mentions-history` | Brand mentions in AI answers over time |
| `brand-radar-sov-overview` / `-sov-history` | Share of voice vs competitors in AI |
| `brand-radar-impressions-overview` / `-impressions-history` | AI impression volume |
| `brand-radar-ai-responses` / `-ai-responses-entities` | Actual AI responses + entities cited |
| `brand-radar-cited-domains` / `-cited-pages` | Which domains/pages AI cites for the topic |
| `management-brand-radar-reports` / `-prompts` | List configured GEO reports & prompts |
| `*-entities` variants | Break any Brand Radar metric down by entity/brand |

## Site audit (technical SEO)
| Tool | Use |
|---|---|
| `site-audit-projects` | List audit projects |
| `site-audit-issues` | Crawl issues by severity |
| `site-audit-page-content` / `-page-explorer` | Per-page content & on-page data |

## Search Console (owned data)
`gsc-keywords`, `gsc-pages`, `gsc-keyword-history`, `gsc-page-history`,
`gsc-performance-history`, `gsc-performance-by-position`, `gsc-ctr-by-position`,
`gsc-metrics-by-country`, `gsc-anonymous-queries`.

## Web analytics (owned traffic)
`web-analytics-stats`, `-top-pages`, `-sources`, `-source-channels`, `-countries`,
`-devices`, `-referrers`, `-entry-pages`, `-utm-params` (+ `*-chart` variants).

## SERP
`serp-overview` — full SERP for a query (features, positions).

## Management & meta
`management-projects`, `management-project-keywords`, `management-project-competitors`,
`management-locations`, `management-keyword-list-keywords`,
`subscription-info-limits-and-usage` (watch quota), `public-domain-rating-free` (free DR check).

## Rendering (chat surfaces)
`render-data-table`, `render-scorecard`, `render-time-series-chart` — call when a tool
says `render_with`. For **PDF deliverables**, use the framework's own SVG kit
(`tools/charts`) instead — those embed in the printed report.

---
**Project ids:** store per client in `client.yml` under `ahrefs.project_id` and
`ahrefs.brand_radar_report_id`. List them with `management-projects` /
`management-brand-radar-reports` and paste the ids in.

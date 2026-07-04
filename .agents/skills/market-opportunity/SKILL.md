---
name: market-opportunity
description: >
  Size a market and frame the opportunity so discovery-audit and proposal-builder can act on it.
  Use when asked to "size the market", "TAM SAM SOM", "market opportunity", "is there
  product-market fit", "market sizing for the proposal", or "competitive landscape map". Produces
  a TAM/SAM/SOM (top-down AND bottom-up), a price-vs-complexity competitor map, Porter's Five
  Forces, a Sean-Ellis PMF qualifier that gates spend, and an ICE-scored opportunity shortlist.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# market-opportunity

Sizes a market and frames the opportunity as a feed into `discovery-audit` (the intake brief) and
`proposal-builder` (the pitch). The IP is **dual validation** — every market number is computed
two independent ways (top-down from industry figures, bottom-up from demand-side signals) and the
gap between them is the honesty check. Prefer Ahrefs MCP (see `knowledge/ahrefs-mcp-map.md`); call
`doc` on a tool before first use. The methodology lives in `playbooks/market-sizing.md` — read it.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — gather.** Resolve the project (`./bin/mkt config show --project <client>`); read
`client.yml` for domain, category, price point, locales, competitors, ICP. Establish the market
frame: what is being sold, to whom, in which geographies, at what price.
- **Demand-side bottom-up signal.** Pull total search volume for the category's commercial-intent
  head + body terms with `keywords-explorer-overview` (read `volume` and `traffic_potential`),
  expand the term set with `keywords-explorer-matching-terms` / `-related-terms`, and split it by
  market with `keywords-explorer-volume-by-country`. This is your bottom-up demand proxy — real
  buyers searching, per geography — not a borrowed analyst number.
- **Top-down inputs.** Capture published industry size, growth rate, and ARPU/ACV (from
  `client.yml`, the brief, or `WebSearch` for analyst figures — cite source + date).
- **Competitor set.** From `client.yml` competitors + `site-explorer-organic-competitors`, list
  rivals; pull `site-explorer-domain-rating` and `site-explorer-metrics` for relative scale.

**ANALYZE — size, map, force, gate, score.**
1. **TAM / SAM / SOM, both directions** (full worked method in the playbook):
   - *Top-down:* TAM = industry size; SAM = TAM × (segments you serve); SOM = SAM × realistic
     share over the plan horizon.
   - *Bottom-up:* TAM ≈ addressable buyers × ARPU; SAM = restrict to served geos/segments (use the
     `-volume-by-country` split as the geo weighting); SOM = SAM × capturable demand (search
     volume you can realistically rank for / convert, given DR and funnel).
   - **Reconcile.** Put the two TAMs side by side. A < ~2–3× gap is healthy; a large gap means one
     side rests on a bad assumption — say which, and which number you carry forward.
2. **Price-vs-complexity 2D positioning map.** Plot each competitor on price (low→high) × product
   complexity / implementation effort (simple→complex). Name the quadrant the client occupies and
   the **white space** (an empty or thin quadrant with demand behind it).
3. **Porter's Five Forces.** Rate each force (low/med/high) with a one-line evidence note:
   rivalry, new entrants, supplier power, buyer power, substitutes. This frames how defensible any
   SOM capture is.
4. **PMF qualifier (Sean-Ellis "very disappointed" gate).** State the PMF read: do ≥40% of users
   say they'd be "very disappointed" without the product (or the best proxy available — retention,
   organic pull, referral)? This is the **scale-vs-iterate gate**: **below the bar → recommend
   iterate (cheap discovery/positioning tests), NOT heavy paid spend**; at/above → scaling spend is
   defensible. The proposal must inherit this gate so it never recommends heavy spend pre-PMF.

**VALIDATE — every recommendation falsifiable.** For the headline sizing and each shortlisted
opportunity, state:
- **Observation** — the data behind it (cite the Ahrefs tool / source + date, absolute dates only).
- **Dependency** — what must hold for the number to be real (e.g. "served geos = the 3 countries
  carrying 80% of `-volume-by-country`", "ARPU holds at the assumed ACV", "we can rank for the
  commercial head terms given our DR").
- **How we'd know this failed** — a leading indicator (e.g. "bottom-up TAM is >3× the top-down,
  unreconciled", "PMF proxy < 40% yet plan assumes scale spend", "white-space quadrant has no
  search demand behind it in `keywords-explorer-overview`").

**ACT — opportunity shortlist + output.** Score each candidate opportunity (segment, geo, wedge,
channel) with **ICE** = Impact × Confidence × Ease (1–10 each; rank by the product). Then write
one file: `projects/<client>/research/market-opportunity.md` containing:
- TAM/SAM/SOM table with **both** top-down and bottom-up columns + the reconciliation note.
- The price-vs-complexity map (an SVG via `tools/charts`, or an ASCII quadrant inline) with the
  white-space call-out.
- Porter's Five Forces table.
- The PMF qualifier verdict + the explicit **scale-vs-iterate** recommendation.
- The ICE-ranked opportunity shortlist with the falsifiability block per row.

## Notes
- **Feeds downstream:** `discovery-audit` pulls the sizing + white space into the intake brief;
  `proposal-builder` inherits the SOM (for scenario projections) and the PMF gate (to set spend
  posture). Don't restate — point both at this file.
- Don't fabricate a TAM from one analyst headline; the bottom-up search-demand cross-check is the
  whole point. If the two sides can't be reconciled, report the range, not a false-precision point.
- Monetary fields from Ahrefs (CPC, traffic value) are **USD cents** — divide by 100.
- If a tool returns `render_with` metadata in chat, call the named render tool; for the MD/CSV
  deliverable, write data directly and embed charts as SVG from `tools/charts`.
- Reference `playbooks/market-sizing.md` for the worked examples (fintech remittance corridor,
  B2B hardware) and the exact formulas.

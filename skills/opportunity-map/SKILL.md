---
name: opportunity-map
description: >
  Turn competitor + keyword + GEO + demand diagnosis into a sized greenfield opportunity map and a
  concrete, sequenced capture plan to overtake competitors. Use when asked "where is the
  opportunity", "where can we win", "how do we get to #1 / beat <competitor>", "what should we build
  to win", "find the greenfield / whitespace", "growth plan", "how do we capture this market", or
  when a competitor analysis exists but the next move is open-ended. Finds the four gap types (demand,
  AI-citation, format, segment), scores each by demand x winnability x fit, picks the right capture
  mechanism per opportunity (programmatic SEO, comparison hub, GEO play, tool, education cluster), and
  sequences a flank-then-moat takeover. Produces research/opportunity-map.md. This is the step that
  converts diagnosis into a plan; the /growth-plan command orchestrates it end to end.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# opportunity-map

The engine that answers "where is the gap, how big is it, and exactly what do we build to capture it
and get on top of the competition." It exists because diagnosis (competitor-analysis, keyword-research,
geo-audit) tells you where you stand but not what to do; this turns that into a sized, sequenced,
falsifiable capture plan. Full methodology in `playbooks/opportunity-capture.md` (read it first).

## When to reach for this
After (or alongside) the diagnostic skills, whenever the ask is "so what do we do to win." It is the
missing middle between `competitor-analysis` and the build skills (`programmatic-seo`,
`comparison-pages`, `content-brief`). If a project has a competitor read but no ranked, mechanism-driven
plan, run this.

## Inputs (use what exists; pull what is missing)
- `research/` diagnostics: competitor-analysis, keyword map, geo-audit / ai-citation-log, technical
  audit, backlinks, voice-of-customer. Read them all first.
- Live data to fill gaps: Ahrefs (keyword gap, competitor organic keywords, KD, DR), the `web-research`
  skill for GEO open-field probing and competitor fact-checks, GA4/GSC for fit validation.
- `client.yml` for the goal (what "winning" converts to) and the competitor set.

## Workflow (PERCEIVE -> ANALYZE -> VALIDATE -> ACT)

1. **PERCEIVE (discover the four gaps).** Per `playbooks/opportunity-capture.md` section 1, find every
   gap: **demand** (competitor-ranks-we-do-not, low-KD real-volume terms, weak SERPs), **citation**
   (AI-answer open fields and beatable competitor citations, via the geo-audit / web-research probe),
   **format** (demand with no tool / comparison / dataset / interactive), and **segment/journey** (an
   ICP or journey stage the incumbents abandon). Record evidence + who owns it now.

2. **ANALYZE (size and rank).** Score each cluster **Demand x Winnability x Fit** (section 2). Fit is
   the guardrail: high volume with the wrong audience is a **Trap**, not an opportunity (confirm
   against GA4 where possible). Label each Greenfield / Contested / Fortress / Trap. Rank descending.

3. **VALIDATE (pick the mechanism, honestly).** Match each high-score cluster to ONE primary capture
   mechanism by fit, not habit (section 3 table): programmatic SEO, comparison hub, GEO/AEO play, free
   tool, education cluster, refresh, local, or earned mentions. Flag any cluster with a data
   dependency you do not have (live prices, feeds) as a build-blocker, not a content play. Kill any
   plan that fails the thin-content gate.

4. **ACT (sequence the takeover + write it).** Order the plan flank-then-moat (section 4): quick wins
   (greenfield, weeks) -> beachhead expansion (own a segment + its AI citations) -> compounding moat
   (brand demand, proprietary data/tools, earned authority). Name the ONE competitor you flank and the
   weakness you exploit; say explicitly what you do NOT attack (the fortress) and why. Write
   `research/opportunity-map.md` with the three outputs (section 6): the ranked **Opportunity Map**
   table, the **Capture Plan** (mechanism + concrete build + projected impact + effort + wave + kill
   condition per opportunity), and the one-paragraph **Takeover thesis**. Then hand each capture item
   to its build skill as input.

## Output contract
`research/opportunity-map.md` must contain, for the top opportunities: the ranked map, a capture
mechanism per opportunity, a concrete build spec (which pages / hub / tool / cluster), a projected
impact with its assumption, an effort estimate, a sequence wave, and a falsifiable kill condition.
Every number ties to a source; nothing is unfalsifiable.

## Notes
- This is where "programmatic SEO or GEO or whatever" gets decided, per opportunity, on evidence.
- Pairs downstream with `proposal-builder` / `report-generator` to turn the plan into a client PDF, and
  with `kpi-dashboard` to track the projected captures. Upstream it consumes `skill-navigator`'s route.
- Greenfield means demand with a weak or absent incumbent, not zero demand. A gap with no demand is not
  an opportunity; say so and move on.

---
description: Turn diagnosis into a sized greenfield opportunity map + a sequenced, mechanism-driven capture plan to overtake competitors.
argument-hint: "<project>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# /growth-plan <project>

The **prescription** pass for **$1** (defaults to the active project, resolve with
`./bin/mkt config show`). Where `/discovery-audit` answers "where do we stand," this answers "so what
do we build to win, in what order, to get on top of the competition." It runs the `opportunity-map`
skill over the diagnostic evidence and produces `research/opportunity-map.md`: a sized opportunity map,
a capture plan with a chosen mechanism per opportunity, and a flank-then-moat takeover thesis.

This is the step the framework used to do only when a brief forced it. Now it is standard: every
engagement gets a ranked, mechanism-driven, falsifiable plan, not just a diagnosis.

## Steps

1. **Load context + evidence.** `./bin/mkt config show --project $1`. Read `client.yml` (the goal,
   the competitor set, DR/market) and everything already in `projects/$1/research/`: competitor
   analysis, keyword map, geo-audit / ai-citation-log, technical audit, backlinks, VOC. If the
   diagnostics are thin, run `/discovery-audit $1` first (or at least `competitor-analysis` +
   `keyword-research` + `geo-audit`).

2. **Run `opportunity-map`** (methodology: `playbooks/opportunity-capture.md`):
   - **Discover the four gaps** (demand, AI-citation, format, segment). Fill missing evidence with
     live pulls: Ahrefs keyword-gap + competitor organic keywords + KD/DR (budget-aware, save to
     `data/`), and the `web-research` probe for GEO open fields and competitor facts.
   - **Size and rank** each cluster Demand x Winnability x Fit; label Greenfield / Contested /
     Fortress / Trap. Use GA4/GSC to sanity-check fit where access exists; otherwise flag fit as an
     assumption to validate.
   - **Pick one capture mechanism per opportunity** (programmatic SEO, comparison hub, GEO/AEO play,
     free tool, education cluster, refresh, local, earned mentions), on evidence not habit. Flag any
     cluster that depends on data the client does not have as a build-blocker.
   - **Sequence the takeover** flank-then-moat: quick wins -> beachhead expansion -> compounding moat
     (brand demand, proprietary data/tools, earned authority). Name the ONE competitor you flank and
     the weakness you exploit; state what you deliberately do NOT attack (the fortress) and why.

3. **Write `projects/$1/research/opportunity-map.md`** with the three outputs: the ranked
   **Opportunity Map** table, the **Capture Plan** (mechanism + concrete build + projected impact +
   assumption + effort + wave + kill condition per opportunity), and the one-paragraph **Takeover
   thesis**. Every number ties to a source; nothing is unfalsifiable.

4. **Hand off downstream.** Point each capture item at its build skill (`programmatic-seo`,
   `comparison-pages`, `content-brief` + `internal-linking`, `aeo-content-patterns`, a tool spec), and
   tell the user the natural next step: `/growth-proposal $1` to turn the plan into a client PDF, and
   `kpi-dashboard` to track the projected captures.

## Notes
- Run after `/discovery-audit` (or the core diagnostics). It consumes their outputs; it does not
  re-diagnose from scratch.
- Everything is falsifiable (PERCEIVE -> ANALYZE -> VALIDATE -> ACT): observation, dependency, kill
  condition. Label assumed numbers as assumed.
- Budget-aware: reuse saved pulls under `data/`; watch Ahrefs quota with
  `subscription-info-limits-and-usage`. Use the cheap `web-research` probe for GEO open-field checks.
- Greenfield means demand with a weak or absent incumbent, not zero demand. Do not dress a no-demand
  gap up as an opportunity.

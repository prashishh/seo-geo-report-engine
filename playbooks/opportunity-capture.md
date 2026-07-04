# Opportunity capture methodology

This is the engine that closes the gap between **diagnosis** (where you stand, who competes, what AI
says) and **prescription** (the sized greenfield and the specific machine, sequenced to overtake the
competition). Every diagnostic skill feeds it: [[competitor-analysis]], [[keyword-research]],
[[geo-audit]], [[technical-seo-audit]], [[backlink-analysis]], [[customer-research]]. The
`opportunity-map` skill and the `/growth-plan` command run this playbook.

Its job is to answer three questions every engagement must answer and that we have historically
answered only when the brief forced it: **where is the gap, how big and winnable is it, and exactly
what do we build (programmatic SEO, comparison hub, GEO play, tool, cluster) to capture it and get on
top of the competitor.**

## 1. Whitespace discovery: the four kinds of gap

Opportunity hides in four places. Look for all four; most engagements over-index on the first.

1. **Demand gap.** High search or AI-query demand with weak or no strong incumbent. Signals: keyword
   gap (competitors rank, we do not), low-KD terms with real volume, SERPs where the top results are
   thin or off-intent, and the "how much / how to / best / which" long tail that data-and-news
   incumbents ignore. (Real examples: a fintech found `ipo result check` at 11,000/mo, KD 0; a hospitality
   SaaS found guest-side "how much to tip X" terms at KD 0-1.)
2. **Citation gap (GEO).** AI-answer queries with no cited authority (open fields) or where a
   competitor is cited but beatable. The newest, least-contested whitespace, because most competitors
   are not yet optimizing for it. (One audit found two money queries where no brand was cited at all.)
3. **Format gap.** Demand exists but nobody serves it in the best format: a free tool or calculator, a
   comparison hub, a programmatic dataset, video, an interactive, or proper structured data. The
   incumbent serves it as a thin blog post; you serve the definitive asset.
4. **Segment / journey gap.** An ICP or a stage of the journey the incumbents underserve: beginners, a
   vertical, a corridor, the education-to-execution handoff. The competitor is a specialist who
   abandons the rest. (Example: the beginner journey that pro-data portals will not serve.)

For each candidate, record the **evidence** (the data point), the **current best-result quality**, and
**who, if anyone, owns it** today.

## 2. Sizing: the Opportunity Score

Do not just list gaps. Size and rank them. For each opportunity cluster estimate:

- **Demand** = addressable volume (search volume + AI-query frequency) x intent value
  (commercial > comparison/BOFU > informational).
- **Winnability** = our authority (DR) versus the difficulty (KD) and the incumbent's real strength on
  those terms. High when KD is low and the incumbent is weak or absent.
- **Fit** = does capturing it convert to the client's actual goal (revenue, signups), or is it vanity
  traffic? This is the guardrail that catches the audience-mismatch trap:
  high volume plus wrong audience equals low fit.

**Opportunity Score = Demand x Winnability x Fit** (normalized 0-100). Rank descending, then label each:

- **Greenfield** — open, winnable, high fit. Attack first.
- **Contested but winnable** — a competitor is there but beatable. Attack second.
- **Fortress** — the incumbent's moat (their brand terms, live-data core, deep authority). Do NOT
  attack head-on; it is a multi-year war.
- **Trap** — volume without fit. Skip, or bridge deliberately, never chase.

## 3. Capture mechanism selection: how to take it

Match each high-score cluster to the machine that captures it. This is the "programmatic SEO or GEO or
whatever" decision, made by **fit to the opportunity shape**, not by habit.

| Opportunity shape | Capture mechanism | Skill / tool |
|---|---|---|
| Large structured combinatorial demand ({service} x {city}, per-entity pages) | Programmatic SEO (template x data, with the thin-content gate) | `programmatic-seo` |
| Commercial "vs / alternative / best-of" demand | Comparison hub | `comparison-pages` |
| AI-answer open fields / citation gaps | GEO/AEO citation play (answer-first, schema, llms.txt, earned mentions) | `geo-audit` + `aeo-content-patterns` |
| High-volume tool / calculator intent | Free tool or interactive that bridges to the product | build spec (a magnet) |
| Informational + trust demand | Topic-cluster education hub | `content-brief` + `internal-linking` |
| Decaying owned assets | Content refresh | `content-refresh` |
| Local / geo demand | Local + programmatic | `local-seo` + `programmatic-seo` |
| Demand-rich but authority-limited | Digital PR / earned mentions (also fuels GEO) | `backlink-analysis` |

Each opportunity gets ONE primary mechanism plus supporting ones. A cluster with a live-data
dependency you do not have (real-time prices, IPO feeds) is a build-blocker, not a content play; defer
it until the data exists or it fails the thin-content gate.

## 4. The takeover sequence: how to get on top of competitors

Ordering matters more than the list. The competitor-takeover logic:

- **Do not attack the fortress.** The leader's brand-name terms and high-authority core (live data,
  category brand) are a multi-year war a challenger loses head-on. Flank it.
- **Flank via the gaps they abandon** — the format, segment, and citation gaps where their authority
  does not transfer. Win these first: greenfield, low-KD, high-fit, ships in weeks.
- **Build the compounding moat** — the plays that strengthen over time and that the incumbent cannot
  easily copy: **brand demand** (own-name search), **AI-citation authority**, **proprietary data or
  tools**, and an **owned audience**. This is how you eventually overtake, not by out-publishing the
  leader on their own terms.
- **Name the ONE competitor you are flanking** and the specific weakness you exploit (a data portal
  that cannot teach; a specialist that abandons beginners; a news site with no tools).

Sequence into three waves: **(1) Quick wins** (greenfield, weeks), **(2) Beachhead expansion** (own a
whole segment/cluster and its AI citations), **(3) Moat** (brand + proprietary data + earned
authority). Enter fortress terms only after you have the authority and a differentiator.

## 5. Projected impact and falsifiable tests

Every opportunity in the plan carries: **projected capture** (traffic / citations / signups, with the
assumption stated), the **mechanism**, the **effort**, the **sequence wave**, and a **kill condition**
("how we would know this failed"). No unfalsifiable "this will grow traffic." Tie projections to
assumptions a client can challenge.

## 6. Outputs

1. **Opportunity Map** — a ranked table: opportunity | gap type (demand/citation/format/segment) |
   demand | winnability | fit | score | label (greenfield / contested / fortress / trap).
2. **Capture Plan** — per top opportunity: the mechanism, the concrete build (page set / hub / tool /
   cluster), projected impact, effort, wave, and kill condition.
3. **Takeover thesis** — one paragraph: how we get on top of the named competitor, what we flank, what
   we do not attack, and the compounding moat we build.

Write these to `research/opportunity-map.md`, then hand the capture plan into the build skills
(`programmatic-seo`, `comparison-pages`, `content-brief`, etc.) as the input they need. This is the
step that turns a competitor analysis into a plan to win.

## Guardrails (lessons from the field)

- Volume without fit is a trap; verify against owned analytics (GA4) before chasing it.
- Do not build programmatic pages on data you do not have; the thin-content gate is not optional.
- Citation gaps close fast; ship GEO open-field plays before incumbents map the category to themselves.
- Greenfield does not mean zero demand; it means demand with a weak or absent incumbent. A "gap" with
  no demand is not an opportunity.
- Rank by score, present the top few, and say what you deliberately are not doing and why.

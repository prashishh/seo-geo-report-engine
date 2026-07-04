# Proposal methodology — how to build a growth proposal that holds up

The portable IP behind the `proposal-builder` skill. A growth proposal isn't a pitch — it's a
**falsifiable plan**: here's where you are, here's the headroom, here's the sequence that captures
it, and here's exactly what has to be true for the numbers to land. It must work in any vertical;
the running examples are **B2B hardware** (noise-control panels) and a **fintech remittance corridor**
(a money-transfer route, e.g. UK→Nigeria).

> House method: **PERCEIVE → ANALYZE → VALIDATE → ACT.** Perceive the current state with data,
> analyze the opportunity, validate every projection against an assumption a reader can attack, then
> act with a sequenced roadmap. If a slide can't survive a skeptical CFO, cut or fix it.

---

## 1. The 3-pillar spine (reusable across verticals)

Every program sequences the same way, because demand capture fails without foundation and traffic
fails without conversion. Name the pillars for the client's world, but keep the spine:

| Pillar | Job | "Done" looks like |
|---|---|---|
| **1 · Foundation** | Fix what caps everything else: crawlability, site health, IA, schema, brand basics, tracking. | The site can rank and convert; AI crawlers can read it; we can measure it. |
| **2 · Wide Net / Acquisition** | Open demand at scale: content clusters, programmatic/comparison pages, links + brand mentions, GEO citability, paid where it pays back. | Qualified traffic climbs across owned, earned, and AI surfaces. |
| **3 · Conversion / Lifecycle** | Turn traffic into revenue and keep it: CRO, landing pages, lifecycle/retention, LTV. | Each visit is worth more; the funnel compounds. |

- **B2B hardware:** Foundation = spec/PLP schema + site speed; Wide Net = "how acoustic panels work"
  cluster + "X vs FoamCo" comparisons + trade-press mentions; Conversion = quote-request CRO + sample
  program + reorder lifecycle.
- **Fintech corridor:** Foundation = corridor pages indexable + regulatory trust signals + tracking;
  Wide Net = "send money to <country>" + fee/FX comparison pages + remittance-community mentions
  (Reddit/YouTube); Conversion = first-transfer activation + referral + repeat-send retention.

Sequence is the message: **you can't out-acquire a broken foundation, and you can't out-convert empty
traffic.** Front-load Foundation; overlap Wide Net once the floor is solid; Conversion runs
throughout but intensifies as traffic arrives.

---

## 2. Sizing the opportunity (top-down ∩ bottom-up)

Two independent estimates that should roughly agree; if they don't, you've found a wrong assumption.

**Bottom-up (search/AI demand — preferred, it's measurable).**
1. Build the category keyword set (`keywords-explorer-matching-terms` / `-related-terms`); pull
   volume + KD (`keywords-explorer-overview`); localize per market (`-volume-by-country`).
2. **Total addressable demand** = Σ monthly volume across the relevant clusters.
3. **Winnable demand** = the slice where median cluster KD ≤ our DR-implied ceiling
   (`site-explorer-domain-rating`). This is the honest number — quote *winnable*, not *total*.
4. **Capturable traffic** = winnable volume × realistic CTR by target position (be conservative;
   position 3-5 ≠ position 1). Add AI-surface upside from `brand-radar-*` only if measured.
5. **Value** = capturable traffic × conversion rate × value-per-conversion (AOV / take-rate / LTV).

**Top-down (market sanity check).** Category/TAM from the brief or public data → realistic share.
If bottom-up says we can capture more than a sane share of the category, the CTR or conversion
assumption is too hot — revise.

> Hardware: Σ volume on panel/acoustic-treatment terms × winnable share × CTR × quote-rate × avg
> order. Corridor: Σ "send money to X" volume × winnable share × CTR × signup→first-transfer rate ×
> contribution per transfer. Same skeleton, different value-per-conversion.

State the sizing as a short chain of named inputs, not a single figure dropped from the sky.

---

## 3. Scenarios from explicit assumptions (conservative / probable / aggressive)

Never project a single line. Build **three**, and make the **assumptions the variable** — not vibes.

1. **List the levers** that drive the outcome and put a number on each: capture rate of winnable
   volume, target-position CTR, conversion rate, value-per-conversion, ramp/time-to-rank, link/mention
   velocity, AI SoV lift. Put them in an **assumptions table** the client can edit.
2. **Define the three scenarios as assumption sets**, not as "low/mid/high guesses":
   - **Conservative** — slow ramp, lower capture & CTR, no AI upside, longer time-to-rank. The floor.
   - **Probable** — base-rate assumptions from comparable programs / current trajectory. Your honest bet.
   - **Aggressive** — faster ramp, higher capture, AI-surface tailwind, seasonal pushes land. The ceiling.
3. **Derive, don't assert.** Each scenario's curve is computed from its assumption set, so the three
   share one formula and only the inputs differ. Show the math implicitly via the table.
4. **Anchor at TODAY.** Index the projection chart to the current baseline (today = 100 or actual)
   so the lift is honest and the starting point is real.
5. **Mark reality.** Use chart `band` for the conservative-to-aggressive range and `markers` for known
   events (a seasonal peak — Dashain for the hardware client, Eid/holiday remittance spikes for the
   corridor). Don't hide seasonality; price it in.

The scenario table (`type: scenarios` in `proposal.schema.md`) lists the same metrics per scenario at
M3 and M6 so the reader compares like-for-like.

---

## 4. Picking the headline KPIs

Three to five, no more. A good headline KPI is **(a) tied to revenue, (b) movable by the plan, and
(c) measurable on our cadence.** Map one primary KPI to each pillar plus one north-star:

- **North-star** — the revenue-proximal number the client already cares about (qualified
  leads/quotes for hardware; activated first-transfers or send-volume for the corridor).
- **Foundation KPI** — a health gate (Core Web Vitals pass-rate, indexable-page %, crawl errors → 0).
- **Acquisition KPI** — winnable-volume capture (non-brand organic clicks, tracked-position share,
  **AI share-of-voice** via `brand-radar-sov-overview`).
- **Conversion KPI** — funnel value (conversion rate, cost-per-acquisition, LTV / repeat rate).

Avoid vanity (raw impressions, total keywords). Every KPI needs a **baseline** (today's number), a
**target** (at M3/M6), and a **leading indicator** that moves first — so progress is visible before
the lagging revenue number does.

---

## 5. The falsifiability bar

This is the differentiator and the house standard. **Every projection and recommendation states
three things:**

- **Observation** — the data that motivates it (cite the Ahrefs tool + date).
- **Depends on** — the assumption it rests on (the one a CFO would attack).
- **How we'd know it failed** — the kill condition + a **leading indicator** that fires early.

> Corridor example — *Observation:* "send money to <country>" has N searches/mo and the SERP is
> aggregator-led, not bank-led. *Depends on:* our corridor pages can reach top-5 and CTR holds at the
> assumed rate. *How we'd know it failed:* if the lead corridor page isn't top-10 by week 8
> (`rank-tracker-overview`) or signup→first-transfer stays below the assumed rate at M3, the capture
> assumption is wrong — re-forecast down.

If a claim can't be written this way, it's marketing, not a plan — cut it or make it testable. In the
spec, label any illustrative/assumed number as such; never imply data you didn't pull.

---

## 6. Deck structure (maps to `proposal.schema.md`)

Tight — the reference decks are ~10 pages. One strong chart per section.

1. **Cover** — client brandmark, title, one-line promise, date.
2. **Executive summary + 3 pillar cards** (`type: summary`) — the whole argument in 4-5 bullets and
   three named pillars with their timing.
3. **The opportunity** (`type: prose` + chart) — winnable vs total demand; where the headroom is.
4. **Audience / ICP** (`type: prose`) — segments and where they are (search, social, AI answers).
5. **Pillar deep-dives** (`type: pillars_detail`) — per pillar: workstreams + concrete
   **deliverables** boxes. This is what they're buying.
6. **Roadmap** (`type: roadmap`) — workstream gantt; intensity by month; front-loaded Foundation.
7. **Scenario projection** (`type: scenarios`) — the three-line chart anchored at TODAY + the
   metrics table; the assumptions table lives here.
8. **KPI scorecards** (`type: scorecards`) — baseline → target per headline KPI.
9. **Next step / CTA** (`type: cta`) — one clear action and a contact. Don't bury the ask.

Brand from `client.yml: brand` (`primary` + `accent`). Charts are numeric (the `kind` field formats
`$`/`%`). Render with `./bin/mkt proposal build --project <slug>`, then **review the PDF** — cover,
pillar cards, chart legibility, page breaks, cross-section number consistency — and iterate.

---

## Checklist before you ship

- [ ] Opportunity sized **bottom-up and top-down**; the two agree (or the gap is explained).
- [ ] Quoted **winnable** demand, not total. DR-aware feasibility applied.
- [ ] Three scenarios derived from **one explicit assumptions table**, anchored at TODAY.
- [ ] 3-5 headline KPIs, each with baseline + target + leading indicator; no vanity metrics.
- [ ] Every projection/rec carries **observation → depends on → how we'd know it failed**.
- [ ] Seasonality and ramp priced in (markers/band), not hidden.
- [ ] Numbers consistent across summary, scenario chart, table, and scorecards.
- [ ] Any assumed/illustrative figure is **labeled**; nothing implies data we didn't pull.
- [ ] Deck is ~10 pages, one strong chart per section, brand colors applied, PDF reviewed.

Data priority everywhere: **Ahrefs MCP > CLI connectors > web** spot-checks. Dates absolute
(today 2026-06-23). Monetary values from Ahrefs are USD cents — divide by 100.

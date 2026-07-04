# Market sizing — methodology

Portable methodology for sizing a market and framing the opportunity. The `market-opportunity`
skill encodes this; this file is the IP. Five parts: (1) TAM/SAM/SOM two ways, (2) the
price-vs-complexity map, (3) Porter's Five Forces, (4) the PMF qualifier and why it gates spend,
(5) ICE scoring. Absolute dates only (today 2026-06-23).

---

## 1. TAM / SAM / SOM — top-down AND bottom-up

Three nested numbers:

- **TAM** (Total Addressable Market) — everyone who could ever buy the category, no constraints.
- **SAM** (Serviceable Addressable Market) — the slice you can actually serve (geos, segments,
  languages, regulatory reach, product fit).
- **SOM** (Serviceable Obtainable Market) — the slice you can realistically *win* over the plan
  horizon, given authority, budget, competition, and funnel conversion.

Always compute each **two independent ways** and reconcile. One number alone is a guess; two that
agree is a finding; two that disagree tells you which assumption is wrong.

### Top-down (industry → you)
Start from a published market figure and narrow with multipliers.
```
TAM = published industry revenue (cite analyst + date)
SAM = TAM × (share of segments/geos you serve)
SOM = SAM × (realistic market share over horizon)
```
Fast, but inherits the analyst's framing and is easy to inflate ("1% of a huge market").

### Bottom-up (units → market)
Build from countable units you can defend.
```
TAM = (addressable buyers) × (ARPU or ACV per year)
SAM = restrict buyers to served geos/segments
SOM = SAM × (capturable demand you can reach + convert)
```
Slower, harder to fake, far more credible. **The demand-side proxy** the framework uses for the
bottom-up build is *search demand*: total commercial-intent search volume for the category, split
by country, is a live readout of how many buyers are actively in-market — per geography, this
quarter — rather than a borrowed estimate.

Ahrefs inputs (see `knowledge/ahrefs-mcp-map.md`):
- `keywords-explorer-overview` → `volume`, `traffic_potential` for category head/body terms.
- `keywords-explorer-matching-terms` / `-related-terms` → complete the commercial term set.
- `keywords-explorer-volume-by-country` → the geo split used to weight SAM and bound SOM.

### Reconcile
Lay the two TAMs side by side. Healthy: within ~2–3×. Large gap → one side has a broken
assumption (usually an inflated top-down multiplier or a too-narrow buyer count). Name it, pick the
number you carry forward, and report a **range** rather than false-precision point estimates.

### Worked example A — fintech remittance corridor (bottom-up led)
Product: a remittance app for the **US → Philippines** corridor; take rate 1.2%.
- *Top-down:* global remittance flows ≈ $830B/yr (World Bank, 2024); US→PH corridor ≈ $14B/yr.
  TAM (revenue pool at 1.2%) ≈ **$168M/yr**. SAM = digital-first senders ≈ 55% → **$92M/yr**.
  SOM = 3% share in 3 yrs → **$2.8M/yr**.
- *Bottom-up:* ~4.4M Filipino-Americans; assume ~1.5M send regularly, avg $3,300/yr remitted →
  flow ≈ $4.95B from this segment; at 1.2% → TAM ≈ **$59M/yr**. Demand cross-check:
  `keywords-explorer-volume-by-country` on "send money to philippines", "remittance to
  philippines", "<competitor> alternative" → say ~90K US searches/mo of commercial intent; at a
  realistic capture + signup + active-sender conversion this bounds an obtainable sender count.
  SOM from capturable search demand → **$1.6M/yr**.
- *Reconcile:* top-down TAM ($168M) is ~3× bottom-up ($59M). The gap is the top-down assumption
  that the whole $14B corridor is addressable — most flows through incumbents (banks, Western
  Union) and informal channels. **Carry the bottom-up $59M TAM and the $1.6–2.8M SOM range.** That
  reconciliation *is* the deliverable — not a single confident number.

### Worked example B — B2B hardware (top-down led, bottom-up checked)
Product: an industrial acoustic sensor sold to manufacturing plants; ACV ≈ $18K/yr.
- *Top-down:* predictive-maintenance hardware market ≈ $9B/yr; acoustic-sensing slice ≈ 6% →
  TAM ≈ **$540M/yr**. SAM = N. America + EU mid/large discrete-manufacturing plants → ~45% →
  **$243M/yr**. SOM = 1.5% in 3 yrs → **$3.6M/yr**.
- *Bottom-up:* ~25,000 target plants in served geos × ~30% with a fit use-case = 7,500 buyers ×
  $18K ACV → TAM ≈ **$135M/yr**. (Long-cycle B2B has thin search volume, so demand-side here is a
  sanity bound, not the driver: `keywords-explorer-overview` on "acoustic condition monitoring",
  "ultrasonic leak detection sensor" confirms a small but real, high-intent term set — enough to
  validate the wedge exists, not to size it.)
- *Reconcile:* top-down ($540M) is ~4× bottom-up ($135M) — the 6% category slice was generous.
  **Carry bottom-up $135M TAM**; hold SOM at the more conservative end. Lesson: in low-search B2B,
  bottom-up unit math leads and search demand only *qualifies the wedge*.

---

## 2. Price-vs-complexity positioning map

A 2D scatter of competitors on two axes:
- **X — price** (low → high): list/entry price or typical deal size.
- **Y — product complexity / implementation effort** (simple/self-serve → complex/high-touch).

Plot every competitor (size dots by scale — DR or revenue if known). Read it for:
- **Where the client sits** (which quadrant).
- **White space** — an empty or thin quadrant *that has demand behind it*. An empty quadrant with
  no search demand is not opportunity, it is a graveyard; validate the gap against
  `keywords-explorer-overview` before calling it.

```
complex  │  Enterprise A          Enterprise B
         │
         │            ┌──────────────┐
         │            │ WHITE SPACE? │   ← validate demand before claiming
         │            └──────────────┘
 simple  │  SelfServe C    SelfServe D
         └────────────────────────────────
            low price            high price
```
Render as SVG via `tools/charts` for deliverables, or inline ASCII for chat.

---

## 3. Porter's Five Forces

Rate each force **low / medium / high** with one line of evidence. Forces frame how *defensible*
any SOM capture is — high-rivalry, high-substitute markets erode share even when you win it.

| Force | Question | Evidence to cite |
|---|---|---|
| Competitive rivalry | How many strong, similar rivals? | competitor DR/traffic, SoV spread |
| Threat of new entrants | How easy to enter (capital, regulation, brand)? | barriers, switching cost |
| Supplier power | Can suppliers/platforms squeeze you? | channel/platform dependence |
| Buyer power | Can buyers force price down? | concentration, alternatives, price sensitivity |
| Threat of substitutes | Can buyers solve the problem another way? | adjacent categories, DIY, status quo |

A market can be large (good TAM) yet structurally unattractive (high rivalry + high buyer power +
strong substitutes). Say so — it changes the spend recommendation.

---

## 4. PMF qualifier — and why it gates spend

**Sean-Ellis test:** survey active users — *"How would you feel if you could no longer use this
product?"* If **≥ 40%** answer **"very disappointed,"** you have product-market fit signal. Below
that, you don't — yet.

When direct survey data isn't available, use the best proxy and label it as such:
- strong **retention curve flattening** (cohorts that stop churning),
- **organic pull** (unprompted signups, branded search rising in `keywords-explorer-volume-history`),
- **referral / word-of-mouth** coefficient.

### Why it gates spend — the scale-vs-iterate decision
PMF is the switch between two completely different playbooks:

| PMF signal | Posture | What the proposal should recommend |
|---|---|---|
| **Below bar** (< 40% / weak proxy) | **ITERATE** | Cheap discovery: positioning tests, ICP interviews, landing-page experiments, organic content. **No heavy paid spend** — you'd be pouring budget into a leaky funnel. |
| **At/above bar** (≥ 40% / strong proxy) | **SCALE** | Paid acquisition, programmatic content, channel expansion — spend is now defensible because the funnel holds. |

This gate is **load-bearing for `proposal-builder`**: a proposal that recommends heavy paid spend
for a pre-PMF client is malpractice. The market-opportunity deliverable must carry the verdict
forward so the proposal inherits the correct spend posture.

**Falsifiable:** state the PMF read, its source/proxy, and how you'd know it's wrong (e.g. "proxy
said scale, but 8-week retention in cohort data is still decaying → revert to iterate").

---

## 5. ICE scoring — the opportunity shortlist

Score each candidate opportunity (a segment, geo, wedge, or channel) on three 1–10 axes:

```
ICE = Impact × Confidence × Ease
```
- **Impact** — if it works, how much does it move SOM / revenue?
- **Confidence** — how sure are we, given the evidence? (search demand, PMF, competitor map)
- **Ease** — how cheap/fast to execute, given DR, budget, team?

Rank by the product. Pair the table with the falsifiability block per row (observation /
dependency / how we'd know it failed). ICE is deliberately rough — it forces ranking and exposes
where Confidence is low (i.e. where to test before you spend). Keep the shortlist to the top
5–8; a ranked few beats an unranked many.

---

## Output

The skill writes `projects/<client>/research/market-opportunity.md`: TAM/SAM/SOM table (both
methods + reconciliation), price-vs-complexity map, Five Forces table, PMF verdict with the
scale-vs-iterate recommendation, and the ICE-ranked shortlist. It feeds `discovery-audit` and
`proposal-builder`.

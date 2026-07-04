---
name: positioning-messaging
description: >
  Build a client's positioning and messaging architecture from named frameworks (April Dunford,
  Geoffrey Moore, StoryBrand SB7, Andy Raskin, Osterwalder VPC, Messaging House). Use when asked to
  "nail our positioning", "build a messaging framework", "what's our value prop", "write our
  one-liner / tagline / elevator pitch / hero headline", "category and competitive alternatives",
  "say-this-not-that guide", or "on-brand language for the site". Produces a Positioning & Messaging
  Pack that the content-brief, comparison-pages, programmatic-seo, and proposal-builder skills all
  consume as their source of truth for value-prop language. Writes the canonical one-liner, pillars,
  and say-this-not-that back into client.yml so every other skill inherits it.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# positioning-messaging

Owns the **GTM/positioning/messaging layer that sits ABOVE SEO** — the brand-language spine every
downstream skill currently invents ad hoc. The output is a **Positioning & Messaging Pack** plus a
canonical `messaging:` block written back into `client.yml`. This is **qualitative work: no Ahrefs
MCP is required.** Competitor language is gathered with `WebFetch`/`WebSearch` (and optionally
`site-explorer-top-pages` to find which competitor pages carry their messaging). Methodology lives in
`playbooks/positioning-methodology.md` — read it before running. Today is **2026-06-23**.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — intake.** Resolve the project (`./bin/mkt config show --project <client>`); read
`client.yml` for `industry`, `icp`, `competitors`, and the `positioning` seed. Read any
`research/*.md` voice-of-customer (reviews, interviews, support tickets, sales-call notes) — VOC is
the evidence base; positioning asserted without it is a guess. For each competitor, `WebFetch` the
homepage (and its product/pricing page) to capture their headline, category claim, and proof. If you
need to find a competitor's strongest messaging page, `site-explorer-top-pages` surfaces their
highest-traffic pages (`doc` the tool first). Note the date of every capture — competitor copy drifts.

**ANALYZE — build the architecture.** Work the frameworks in order:
1. **Competitive alternative & category (Dunford).** What does the prospect do *today* if we don't
   exist (status quo, spreadsheet, rival)? Fill Dunford's 5 components — competitive alternatives,
   unique attributes, the **value** those attributes enable, the **customers** who care most, the
   **market category** that frames it — then write Moore's positioning statement: *For [target] who
   [need], [product] is a [category] that [benefit], unlike [alternative], because [proof].*
2. **Messaging House.** Roof = one-line value prop. Three **pillars** = the differentiators (each a
   benefit, not a feature). Foundation = proof per pillar (metric, customer, mechanism). Map pillars
   to VPC pain-relievers/gain-creators and the SB7 SB7 arc (customer-as-hero, brand-as-guide).
3. **Copy primitives — 3 variants each:** one-liner (SB7: problem → solution → result), tagline
   (≤5 words), elevator pitch (≤60 words, Raskin "change is coming" stakes framing optional), hero
   headline. Variants must differ in *angle*, not wording.
4. **Say this / not that** table: on-brand term, the off-brand term it replaces, and *why*
   (commodity language, competitor-owned, or off-positioning).

**VALIDATE — every claim falsifiable.** For the positioning and each pillar, state:
- **Observation** — the VOC quote or competitor-gap that motivates it (cite source + capture date).
- **Dependency** — what must be true (e.g. "prospects actually rank this differentiator", "no named
  competitor already owns this category word", "proof point is real and defensible").
- **How we'd know this failed** — a leading indicator: sales can't repeat the one-liner unprompted;
  a message-test landing page underperforms the control on CTR; the chosen category returns rivals,
  not us, in a `WebSearch`; reviewers describe us in the *not-that* words. QA gate below must pass.

**ACT — ship + propagate.** Write the Pack and update the source of truth:
- `projects/<client>/deliverables/positioning-messaging-pack.md` — Dunford 5 + Moore statement,
  Messaging House, all copy primitives (3 variants each), say-this/not-that table, the
  validation/falsifiability blocks, and a **validation plan** (who to interview, which headline to
  A/B test, success threshold).
- Write the **canonical** one-liner, the 3 pillars, and the say-this-not-that pairs into a new
  `messaging:` block in `client.yml` (see template below) — *this is what makes other skills inherit
  it.* Preserve existing keys; add, don't overwrite (`Edit`, not full rewrite).

## `messaging:` block (write into client.yml)

```yaml
messaging:                          # canonical brand-language spine — other skills read this
  one_liner: "<the chosen one-liner>"
  category: "<market category>"
  competitive_alternative: "<what they do without us>"
  pillars:
    - { name: "<pillar 1>", proof: "<metric/customer/mechanism>" }
    - { name: "<pillar 2>", proof: "<proof>" }
    - { name: "<pillar 3>", proof: "<proof>" }
  tagline: "<≤5 words>"
  say_this_not_that:
    - { say: "<on-brand>", not: "<off-brand>" }
  updated: "2026-06-23"
```

## QA gate (must pass before writing the Pack)
- One-liner is jargon-free and a non-customer could repeat it; tagline ≤5 words.
- The category word does **not** already belong to a named competitor (`WebSearch` it).
- Every pillar has at least one real proof point; no pillar is a restated feature.
- Every say-this/not-that pair has a reason; none contradicts the pillars.
- Each pillar carries observation / dependency / how-we'd-know-it-failed.

## Notes
- **A client whose `positioning` field is a prose seed with empty messaging** — this skill is how you
  fill it. Run it before `comparison-pages`, `content-brief`, or `proposal-builder` so they stop
  inventing value-prop language.
- Adapted from claude-gtm-plugin (brand-messaging-and-positioning), marketingskills
  (product-marketing foundation doc + customer-research), and seo-geo-claude-skills (the handoff-
  artifact pattern — here the `messaging:` block is the artifact).

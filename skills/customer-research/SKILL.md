---
name: customer-research
description: >
  Mine real customer language, pains, jobs, and triggers from research assets and public
  communities to ground positioning, briefs, and pages in voice-of-customer. Use when asked
  to "do customer research", "voice of customer", "VOC mining", "what do customers actually
  say", "build personas", "mine reviews / G2 / Trustpilot / Reddit / support tickets", "jobs
  to be done / JTBD", or "what pains should we target". Two modes: parse the client's own
  research assets (transcripts, surveys, tickets, NPS) and/or scan public watering holes
  (Reddit, G2, Trustpilot, LinkedIn, HN). Outputs a confidence-labeled VOC quote bank,
  JTBD / pain-trigger-outcome clusters, personas, and a "language to use / objections to
  answer" table that positioning-messaging and content-brief read as input.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# customer-research

Extracts the **empirical voice of the customer** — the actual words people use for their
problems, the jobs they hire a product to do, and the triggers that make them buy. This is the
foundation under the GTM layer: `positioning-messaging`, `content-brief`, `comparison-pages`,
and `geo-audit` all consume its outputs. It is **research-oriented, not Ahrefs-backed** — there
is no Ahrefs tool for human language, so it runs on the client's own assets plus `WebSearch` /
`WebFetch` over public communities, with reasoning. (Pair with `keyword-research` if you also
need search-demand framing.)

## Two modes (run one or both)

- **Mode 1 — Assets.** Parse the client's first-party material in `projects/<client>/inputs/`:
  call transcripts, sales-call notes, survey free-text, support tickets, NPS verbatims, churn
  notes, win/loss. Highest-trust signal — these are real customers, but biased toward people
  who *already* engaged. `Glob`/`Grep` the folder; read each file fully.
- **Mode 2 — Watering holes.** When assets are thin or you need outside-in demand, `WebSearch`
  + `WebFetch` across **Reddit, G2, Trustpilot, Capterra, LinkedIn, Hacker News** for the
  client's category and named competitors (from `client.yml`). Public, broad, but noisy and
  self-selected (loud reviewers skew negative/positive). Always capture the **source URL**. If a
  site blocks direct crawling (Reddit frequently does), fall back to the `web-research` skill's
  deep-research mode to get a synthesized, cited read instead of an empty result.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — gather raw quotes.** Resolve the project (`./bin/mkt config show --project
<client>`); read `client.yml` for category, competitors, ICP, target market. Inventory
`inputs/` (Mode 1). For Mode 2, run searches like `site:reddit.com <category> frustrating`,
`<competitor> review G2`, `<category> "I wish" OR "the problem with"`, `<competitor>
alternative why`. Collect verbatim snippets — never paraphrase at this stage. Each captured
quote keeps: exact text, source (file or URL), date, and which competitor/topic it concerns.

**ANALYZE — cluster with three frameworks.**
- **Jobs-to-be-Done** — "When [situation], I want to [motivation], so I can [outcome]." Tag the
  functional, emotional, and social job behind each quote.
- **Pain → Trigger → Outcome** — the felt problem, the event that makes it urgent (the buying
  trigger), and the result they're hiring for. Group quotes into themes on this axis.
- **Frequency + intensity scoring** — `frequency` = how many *independent* sources raise a
  theme; `intensity` = emotional charge / cost of the pain. A theme that's frequent **and**
  intense is a positioning anchor; intense-but-rare is a niche play; frequent-but-mild is table
  stakes.

**VALIDATE — confidence-label every theme (the critical discipline).** Outputs are only as good
as their sourcing, so each theme carries:
- **Confidence** — **high** only if it appears **unprompted across 3+ independent sources**
  (e.g. two Reddit threads + one G2 review, not three quotes from one survey question).
  **Medium** = 2 independent sources or strong but single-channel. **Low** = single mention, OR
  **prompted** (a survey question that fed the answer), OR paraphrased — flag these explicitly.
- **Sample bias** — state who is over/under-represented: assets skew to engaged users; G2/
  Trustpilot skew to extremes; Reddit/HN skew technical and to non-customers. Name it per theme.
- **How we'd know this failed** — a falsifiable check: e.g. "if positioning leads on this pain
  and demo-request CVR doesn't move vs control in 6 weeks, the theme was loud-minority noise,"
  or "if sales calls (Mode 1) never surface it once added to the discovery script, it's a
  forum artifact, not a buyer pain."

**ACT — output.** Write to `projects/<client>/research/` (deliverable-grade VOC pages may also
go to `projects/<client>/deliverables/`):
- **`voc.md`** — the quote bank: every theme with its verbatim quotes, **source URL/file**,
  date, JTBD framing, frequency/intensity scores, and confidence + sample-bias labels.
- **Personas** (in `voc.md` or `personas.md`) — 2–4 segments grounded in clustered quotes, each
  with its dominant job, top pains, buying trigger, and a **confidence label** (do not invent
  demographics the data doesn't support; say "inferred, low confidence" when you do).
- **"Language to use / objections to answer" table** — two columns: the customer's own phrasing
  to adopt in copy (left), and the real objections/blockers to pre-empt (right), each cited to a
  quote. This table is the explicit hand-off that `positioning-messaging` and `content-brief`
  read.

## Notes
- Quote integrity is the product: copy verbatim, attribute every quote, never fabricate. An
  unsourced quote is a bug.
- Today is `2026-06-23`; date every quote and search so freshness is auditable.
- Feeds downstream: real phrasing → `content-brief`; real objections → `comparison-pages`; real
  pains/jobs → `positioning-messaging`; real question patterns → `geo-audit` (AI query phrasing).
- Respect source terms — summarize and link out; don't scrape gated/private content. Public
  community posts are quoted with attribution.
- Adapted from: marketingskills `customer-research` (confidence-labeling discipline) and
  claude-gtm-plugin `copywriting-core` VOC mining (watering-hole + quote-bank method).

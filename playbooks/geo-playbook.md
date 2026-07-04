# GEO playbook — generative-engine optimization methodology

The portable IP behind the `geo-audit` skill. GEO = making a brand **visible, cited, and correctly
described** inside AI answers (ChatGPT, Perplexity, Google AI Overviews / AI Mode, Claude, Copilot).

> **Reframe — "GEO is still SEO."** Google's own guidance (AI Overviews / AI Mode docs, Mar 2025) is
> that there is *no separate GEO checklist*: the same crawlable, helpful, well-structured content that
> ranks is what gets cited. So we don't invent a parallel discipline — we extend SEO toward
> answer-extraction. Everything below is falsifiable; treat it as a hypothesis the data confirms or kills.

## House method: PERCEIVE → ANALYZE → VALIDATE → ACT

- **Perceive** — measure current AI visibility with Brand Radar (don't assume).
- **Analyze** — score the page/brand against the 5 pillars below.
- **Validate** — every recommendation states the observation, what it depends on, and *how we'd know it failed*.
- **Act** — ship the top fixes; re-measure the leading indicator on a fixed cadence.

## The core insight — brand mentions > backlinks

**Brand mentions correlate ~3x more strongly with AI visibility than backlinks** (Ahrefs, Dec 2025,
~75K domains). Unlinked mentions on high-trust community/UGC surfaces move the needle most:

| Signal | Relative strength | Where to earn it |
|---|---|---|
| YouTube mentions | strongest (~0.74 corr) | demos, reviews, founder talks, podcasts |
| Reddit mentions | high | authentic threads, AMAs, helpful answers |
| Wikipedia presence | high | notable, sourced entity / topic pages |
| LinkedIn | moderate | exec posts, company page, employee reach |
| Domain Rating (backlinks) | low (~0.27 corr) | still useful for ranking, weaker for *citation* |

Implication: a GEO program that only builds links is mis-allocated. Spend on **earned brand presence**
where LLMs ingest training and retrieval data (YouTube, Reddit, Wikipedia, LinkedIn, comparison sites).

## The 5 evaluation pillars (weights sum to 100)

### 1. Citability — 25%
Can a model lift a clean, correct, self-contained passage?
- **Citable passages ~134–167 words** — long enough to stand alone, short enough to quote whole.
- **Frontload the answer**: direct answer in the first 40–60 words of a section; ~44% of AI citations
  come from the first 30% of the page.
- **Self-contained**: each block makes sense without the paragraph above it.
- **Attributed, specific claims**: stats with a source, dates, named primary data — not vague opinion.
- **Definition shape**: "X is …" sentences and "X vs Y" framings extract cleanly.
- Weak signals (penalize): buried conclusions, unsupported opinion, generic filler.

### 2. Structural readability — 20%
Make the structure do the extraction work.
- **Question-based H2/H3** that mirror real prompts ("How does X work?", "Is X worth it?").
- **Tables** for comparisons/specs; **numbered/bulleted lists** for steps; **FAQ blocks** for PAA-style Qs.
- One idea per section; descriptive subheads; short paragraphs.

### 3. Multi-modal — 15%
Pages with images/video/diagrams get a citation lift and feed multi-modal models.
- Original images, diagrams, an embedded/linked **YouTube** explainer, interactive tools/calculators.
- Real alt text and captions; transcripts for video.

### 4. Authority & brand signals — 20%
LLMs prefer sources they can trust and date.
- **Named author with credentials**, visible publish + **last-updated dates**, **primary sources** cited.
- **Entity presence** for the brand/people on **Wikipedia, Reddit, YouTube, LinkedIn** (see core insight).
- **Freshness**: content < 3 months old is ~3x more likely to be cited — keep cornerstone pages current.

### 5. Technical accessibility — 20%
If a crawler can't read it, it can't cite it.
- **Server-side rendering / static HTML** for the answer content — never JS-only injection.
- **robots.txt allows the answer/search crawlers** (see `knowledge/ai-crawlers.md`).
- **Schema** (Article, FAQPage, HowTo, Organization, Product) for machine-readable facts.
- **`/llms.txt`** present (transparency; see below) and a clean, fast, indexable page.

## llms.txt — how to build one

A Markdown file at the **domain root** (`https://example.com/llms.txt`) that points models to your
best, canonical content. **Honest caveat:** Mueller/Illyes and SE Ranking's ~300K-domain study found
*no current citation-ranking weight* — major engines don't yet consume it. Ship it for transparency and
future-proofing, **not** as a citation lever; don't oversell it to clients.

Structure: `# H1 brand`, a `>` one-line summary, optional prose, then `##` link sections.

```markdown
# Acme Corp
> Acme builds noise-control panels for studios and offices. This file lists our canonical resources.

## Docs
- [Installation guide](https://acme.com/docs/install): step-by-step acoustic panel install
- [Spec sheet](https://acme.com/docs/specs): NRC ratings, sizes, materials

## Key pages
- [How acoustic panels work](https://acme.com/learn/how-panels-work): the physics, plainly
- [Acme vs FoamCo](https://acme.com/compare/foamco): independent comparison

## Optional
- [Press & mentions](https://acme.com/press)
```

## Measuring with Brand Radar (the engine)

Treat AI visibility as a tracked metric, not a one-off. Use Ahrefs Brand Radar MCP
(see `knowledge/ahrefs-mcp-map.md`); report id lives in `client.yml: ahrefs.brand_radar_report_id`.

- **Baseline & trend** — `brand-radar-sov-overview` + `-sov-history` (share of voice vs competitors),
  `brand-radar-mentions-overview/-history`, `brand-radar-impressions-overview`.
- **What AI actually says** — `brand-radar-ai-responses` + `-ai-responses-entities` (the answer text and
  the entities co-cited with you — surfaces wrong facts and missing associations).
- **Who AI cites** — `brand-radar-cited-domains` + `-cited-pages` for the topic: the sources you must get
  mentioned on or out-cite. `site-explorer-ai-responses-count` checks how often a domain appears in answers.
- **Cadence**: re-pull SoV/mentions every 2–4 weeks; movement is the leading indicator that fixes worked.

## Falsifiability — make every rec testable

For each recommendation, write three lines:
- **Observation** — what the data shows (e.g. "competitor cited in 6/10 prompts; us in 1/10").
- **Depends on** — the assumption (e.g. "AI Overviews weight the cited-pages we're absent from").
- **How we'd know it failed** — the kill condition + **leading indicator** (e.g. "if mentions SoV doesn't
  rise within 6 weeks of earning 3 Reddit/YouTube mentions, the mention→visibility link is weak here").

Data priority everywhere: **Ahrefs MCP > CLI connectors > web** spot-checks.

---
name: content-brief
description: >
  Produce a writer-ready content brief for a target keyword or cluster — intent, required
  subtopics/entities, FAQ questions, target length, internal links, and E-E-A-T signals, plus
  GEO citability guidance. Use when asked to "write a content brief", "make a brief for <topic>",
  "create an outline for an article", "what should this page cover", "make this brief on-brand",
  "run the seven sweeps", or "brief the writer on <keyword>". Grounded in the live SERP and real
  competitor pages so the writer can outrank them.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# content-brief

Gives a writer everything needed to build a page that wins the SERP **and** gets cited by AI
answers. Built from the live SERP + competitor pages via Ahrefs MCP (see
`knowledge/ahrefs-mcp-map.md`); call `doc` before first use. Takes a keyword/cluster — often
straight from the `keyword-research` output.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — read the SERP.** Resolve project (`./bin/mkt config show --project <client>`). Pull
the SERP with `serp-overview` (target keyword + locale): note the page types ranking, SERP
features (PAA, featured snippet, AI Overview), and who's there. Identify the real competitors
(filter out Wikipedia/Reddit/news/job boards). For each, pull `site-explorer-top-pages` /
`site-explorer-pages-by-traffic` to find the exact ranking URL and its sibling pages, and
`site-explorer-organic-keywords` on that URL to see every term it already ranks for.

**ANALYZE — extract the requirements.** Before deriving structure, pull two on-brand inputs:
- **Voice of customer** — read `customer-research`'s `research/voc.md` for the client: lift real
  customer phrasing, the words they use for the problem, and their top objections. Seed FAQ
  questions and subtopic framing from these, not from how the client describes itself.
- **Positioning** — consume the canonical one-liner + pillars from the `positioning-messaging`
  output (`client.yml` `messaging` block). The brief's angle, meta, and proof points must ladder
  to a named pillar so the writer stays on-brand.

From SERP + competitors derive:
- **Intent** — informational / commercial / transactional / navigational (must match the
  dominant page type, or the brief is wrong before it's written).
- **Subtopics & entities** — the H2/H3 coverage every top page shares, plus gaps (topics
  competitors miss or cover shallowly = the unique angle). Pull related terms from
  `keywords-explorer-related-terms` to surface entities to name.
- **Questions** — harvest PAA-style questions from `serp-overview` and `keywords-explorer-
  search-suggestions` for an FAQ section.
- **Target length** — informed by competitor depth, not a fixed number; cite the range observed.
- **Internal links** — 3–5 on-site targets (hub/pillar + supporting pages) via
  `site-explorer-pages-by-internal-links`.
- **E-E-A-T signals** — author/credentials, sources to cite, original data/examples, the
  experience proof this client can credibly show. Every subtopic must be something the client can
  *truthfully* write about — don't invent expertise or services.

**GEO citability (so AI answers cite this page).** Build the page to be quotable:
- Front-load a **self-contained ~134–167-word answer** under each H2 that fully answers the
  heading without needing the rest of the page.
- Make claims **attributed** (named source, date, number) so an LLM can lift them with confidence.
- Use clear, literal headings that match how people ask; add FAQ/Q&A blocks.
- For the full AI-visibility read, reference the **`geo-audit`** skill (Ahrefs Brand Radar) and the
  **geo-playbook** methodology.

**VALIDATE — falsifiable.** State for the page: **Observation** (what the SERP/competitors show),
**Dependency** (intent match + client can credibly cover it + DR in range), and **How we'd know it
failed** — a leading indicator: "not in top 20 for the target term in `rank-tracker-overview` at 8
weeks", or "absent from `brand-radar-cited-pages` for the prompt set after re-crawl."

**ACT — output.** Write `projects/<client>/research/briefs/<slug>.md`: target keyword + cluster,
intent, competitor table (URL, est. traffic, depth), the winning outline (H2/H3 with per-section
notes & word-count guidance), entities to name, FAQ questions, meta title/description (with char
limits), internal links, E-E-A-T checklist, GEO citability block, and the falsifiability block.

## GEO citability checklist (per page)

Hand the writer a tickable list so the page is built to be lifted by AI answers (cross-reference
the **`aeo-content-patterns`** skill for templates):
- [ ] **Answer-first** — first paragraph under each H2 answers the heading in 1–3 sentences before any setup.
- [ ] **Question-shaped headings** — H2/H3 phrased as the literal question a user asks.
- [ ] **Standalone definitions** — each key term gets a self-contained 25–50-word definition that reads correctly out of context.
- [ ] **Attributed quotable stats** — every number carries a named source + date so an LLM cites it with confidence.
- [ ] **Schema** — FAQPage and/or HowTo JSON-LD spec'd for the writer (defer to `schema-markup`).
- [ ] **Freshness + authorship** — visible last-updated date and an author with `Person` schema (name, credentials).

*How we'd know it failed:* page absent from `brand-radar-cited-pages` for the prompt set 4+ weeks
after re-crawl, or no FAQPage/HowTo block detected on the live URL.

## Seven Sweeps — conversion-editing QA pass

A final falsifiable edit pass before the brief ships to the writer (and a checklist the writer
re-runs on the draft). Each sweep = one read-through, one lens:
1. **Clarity** — would a first-time reader understand every sentence on first pass? Cut jargon.
2. **Voice** — does it sound like the brand one-liner/pillars, in the customer's own words (VOC)?
3. **Benefits** — is every feature tied to an outcome the reader cares about?
4. **Proof** — is each claim backed by data, example, or named source?
5. **Specificity** — replace vague modifiers ("fast", "many") with concrete numbers/examples.
6. **Emotion** — does it name the reader's real pain/objection (from `voc.md`) and resolve it?
7. **Friction** — is the next action obvious, and every objection answered before it's raised?

*How we'd know it failed:* draft still contains unsourced claims or off-pillar phrasing after the
pass, or no clear CTA per section.

## Notes
- Keep it writer-ready, not theoretical: every section should answer "what do I write here?"
- "Just an outline" mode: deliver only the H2/H3 hierarchy + word counts, skip competitor/E-E-A-T.
- Monetary fields are **USD cents** — divide by 100. Use absolute dates (today 2026-06-23).
- Reference upstream: AgriciDaniel/claude-seo `seo-content-brief` — adapted to Ahrefs SERP/Site
  Explorer, our falsifiability, and GEO citability for AI answers.

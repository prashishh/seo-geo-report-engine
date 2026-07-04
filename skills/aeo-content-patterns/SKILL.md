---
name: aeo-content-patterns
description: >
  Optimize a specific PAGE for AI-answer citability — answer-first structure, question-shaped
  headings, standalone definitions, quotable sourced statements, FAQ/HowTo schema, freshness and
  author signals. Use when asked to "make this page citable by AI", "optimize a page for
  ChatGPT/Perplexity/AI Overviews", "AEO for this article", "why won't AI cite this page",
  "add answer-first structure", "GEO rewrite", "featured-snippet optimization", or
  "AI-answer optimization". Produces a before/after GEO score, a rewrite spec, an AI Query
  Coverage list, and ready-to-paste FAQ/HowTo JSON-LD. Page-level complement to geo-audit
  (which is brand / share-of-voice level via Brand Radar); pairs with schema-markup and feeds
  content-brief and comparison-pages with concrete citability structure.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# aeo-content-patterns

Rewrites **one page** to be the thing an AI engine lifts verbatim and cites. `geo-audit` answers
*whether* AI cites the brand (Brand Radar, share-of-voice); this answers *how to fix a page so it
gets cited*. It is reasoning + page-content driven (WebFetch the live URL, or read the draft),
**not** an Ahrefs-keyword task — the only Ahrefs touch is optional context (below). Encode reusable
patterns in `playbooks/geo-playbook.md` (extend it; don't duplicate the score rubric here).

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — gather the page.** Resolve the project (`./bin/mkt config show --project <client>`);
read `client.yml` for brand, ICP, primary entity, author/expert names. Get the content:
`WebFetch` the live URL (or `Read` the draft). Capture: H1/H2/H3 outline, the first 80 words under
each heading, any tables/lists, the `<head>` (publish date, `dateModified`, author byline), and
existing JSON-LD. *Optional Ahrefs context only:* `brand-radar-cited-pages` / `-cited-domains` to
see which page structures AI already cites for this topic, and `site-explorer-ai-responses-count`
for the domain's AI-answer baseline. Skip if Brand Radar isn't configured — it's not required.

**ANALYZE — score citability, then map AI queries.** Score 0–100 across eight dimensions
(weights in `playbooks/geo-playbook.md`; keep them identical):
1. **Answer-first** — is the direct answer in the first sentence/paragraph under the heading, or
   buried after preamble? (highest weight)
2. **Question-shaped headings** — do H2/H3 read as real queries ("What is X?", "How does X work?",
   "X vs Y", "Is X worth it?") rather than label nouns?
3. **Standalone definitions** — at least one **25–50 word** self-contained definition of the
   primary entity that makes sense lifted out of context, no "this"/"that" backrefs.
4. **Quotable attributed statements** — declarative, citable sentences with a named source/number
   ("According to <Org>'s 2026 data, …") an engine can quote with attribution.
5. **Factual density / citations** — specific numbers, dates, named entities, outbound citations
   to primary sources vs vague prose.
6. **Tables & lists over prose** — comparison tables, ordered steps, bulleted criteria (the
   structures AI extracts most reliably).
7. **Schema match** — `FAQPage` / `HowTo` (and `Article`) JSON-LD whose Q/A and steps **mirror
   visible on-page content** (mismatched/invisible schema scores 0 — it's a violation).
8. **Freshness & author** — visible publish + `dateModified` dates, byline tied to `Person`/author
   schema, credentials (E-E-A-T). Stale or anonymous = low.

Then map **real AI query patterns** to the structures each demands, e.g.:
`best X for Y` → criteria list + a ranked/comparison table; `X vs Y` → two-column table + a
one-line verdict up top; `how to choose X` → ordered decision steps (`HowTo`); `what is X` →
standalone definition; `is X worth it / X pricing` → a direct yes/no + a number in sentence one.
Produce an **AI Query Coverage** list: each query, the on-page structure that should win it, and
covered / partial / missing.

**VALIDATE — every recommendation falsifiable.** For each rewrite instruction state:
- **Observation** — the deficit found (e.g. "answer to 'What is X?' starts at word 140; first
  paragraph is brand throat-clearing" — cite the heading + fetch date 2026-06-23).
- **Dependency** — what must hold for the fix to earn a citation (the question matches real AI
  demand; the claim is true and sourced; JSON-LD validates and matches visible text; the page is
  actually crawlable by GPTBot/PerplexityBot — see `knowledge/` AI-crawler list).
- **How we'd know this failed** — a leading indicator: after publish, `brand-radar-cited-pages`
  still doesn't list this URL for the topic at 4–6 weeks; or the page never surfaces in
  ChatGPT/Perplexity/AI-Overview spot-checks for its target queries (`WebSearch` + manual prompt
  capture). Note when low citation is a brand-authority problem (route to `geo-audit`), not a
  page-structure one — so we don't over-claim this skill can fix it.

**ACT — output.** Write `projects/<client>/research/aeo-page-<slug>.md` containing:
- **Before → after GEO score** — the eight-dimension table with current score, target score, and
  the per-dimension gap.
- **Rewrite spec** — concrete, paste-ready instructions per section: the answer-first opening
  sentence to add, headings reworded to question form, the 25–50 word standalone definition, which
  prose blocks to convert to a table/steps, quotable sourced statements to insert.
- **AI Query Coverage** list (query → winning structure → covered/partial/missing).
- **Ready-to-paste JSON-LD** — `FAQPage` and/or `HowTo` (plus `Article`/`Person` freshness+author)
  whose content mirrors the rewritten page. Defer deep schema validation to the `schema-markup`
  skill; flag any field that needs real data (author URL, `dateModified`).

## Notes
- Truthfulness gate: never fabricate quotes, stats, or credentials to raise the score — an
  invented "according to" is a worse failure than a low score. Mark unsourced claims `[NEEDS DATA]`.
- Schema that doesn't match visible content is a penalty, not a win — keep JSON-LD and on-page text
  in lockstep, and hand final validation to `schema-markup`.
- Feeds `content-brief` (citability section of new briefs) and `comparison-pages` (vs-page table +
  verdict structure). Brand-level AI visibility stays with `geo-audit`.
- Adapted from upstream: seo-geo-claude-skills `geo-content-optimizer`, marketingskills `ai-seo`,
  sanity-aeo (`aeo-considerations`, `eeat-principles`), claude-gtm-plugin — here re-grounded on the
  live page, the eight-dimension score, and our falsifiable PERCEIVE→ACT loop.

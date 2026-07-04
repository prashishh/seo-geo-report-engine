---
name: human-seo-editor
description: >
  Rewrite and QA SEO/GEO drafts that read too obviously AI-generated, templated, fragmented,
  over-punchy, or generic. Use when asked to make programmatic SEO pages sound human, improve
  article flow, add realism, reduce AI-ish phrasing, apply editorial standards, run a human
  quality pass, or turn generated drafts into credible publishable pages. Pairs with
  customer-research, content-brief, aeo-content-patterns, and programmatic-seo.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# human-seo-editor

Turn generated SEO/GEO drafts into credible human articles without weakening search intent,
citability, or factual discipline. This is an editorial QA skill, not an "AI detector" evasion
skill. The goal is useful, specific, sourced, natural writing.

## Inputs

- Draft page(s): HTML/Markdown in `projects/<client>/deliverables/` or `research/`.
- `projects/<client>/client.yml` for positioning and brand voice.
- `projects/<client>/research/voc.md` from `customer-research` whenever available.
- Briefs from `content-brief` and page-level AEO specs from `aeo-content-patterns`.

Resolve context first:

```bash
./bin/mkt config show --project <client>
```

## Editorial Method

### 1. Diagnose the AI-ish pattern

Scan the draft and record concrete issues:

- **Rhythm sameness:** every paragraph is 1-2 short punchy sentences.
- **Disconnected blocks:** sections state facts but do not explain why the next idea follows.
- **Consultant fog:** abstract phrases like "foundation debt", "digital transformation", "unlock value",
  or "not X, but Y" when a concrete system, page, metric, or buyer problem should be named.
- **Generic transitions:** "In today's world", "That is where X comes in", "It matters because".
- **Brochure voice:** claims sound like sales copy, not an operator explaining a real workflow.
- **Template residue:** sibling pages repeat the same CTA, sentence shapes, examples, or proof.
- **Unsupported confidence:** broad claims without a named source, product fact, or example.
- **Over-optimized headings:** headings match keywords but do not match a real reader's question.

Use `rg` across siblings to catch repeated phrases before editing.

### 2. Ground the page before rewriting

Add at least one grounding source to each major section:

- A first-party product fact or workflow detail.
- A real customer/VOC phrase from `voc.md`.
- A cited external source with a date.
- A concrete scenario, example, edge case, or failure mode.
- A role-specific detail that makes the page differ from siblings.

If a section cannot be grounded, shorten it or remove it.

### 3. Rewrite for human continuity

Preserve the brief's intent and AEO answer-first requirements, but add connective tissue:

- Start important sections with the answer, then explain the operational reason.
- Use causal transitions: "That creates...", "The practical issue is...", "For a hotel team...".
- Vary paragraph length naturally.
- Use bullets and tables when the reader needs a scan, gap list, current-state read, or decision matrix.
- Prefer one specific sentence over three generic benefit lines.
- Show tradeoffs and limits. Human writing admits where a claim depends on context.
- Replace generic CTAs with page-specific next steps.

Avoid default AI tells unless the source or brand truly uses them:

- em dashes as a repeated rhythm device
- "not just X, but Y"
- "seamless", "robust", "unlock", "leverage", "game-changer"
- stacked sentence fragments
- repeated "no app, no friction" on every page without a fresh angle

### 4. Keep SEO/GEO intact

Do not remove:

- The primary query in the title/H1 where the brief requires it.
- Answer-first sentences under H2/H3.
- FAQ/HowTo structures that mirror visible page content.
- Tables/lists that make the answer extractable.
- Internal links required by `internal-linking`.

If a GEO pattern makes the prose stiff, keep the direct answer but make the explanation below it
more natural.

### 5. Run the Human Publish Gate

Before calling a draft publish-ready, check:

- [ ] No visible `{{TODO}}`, `[NEEDS DATA]`, `[NEEDS SOURCED NORM]`, `[AUTHOR:]`, or unapproved
      `[unverified]` markers remain.
- [ ] Every number, norm, statistic, rating, and competitor claim is sourced or removed.
- [ ] Each section has one reason to exist beyond keyword coverage.
- [ ] At least one concrete example appears every 250-400 words on long pages.
- [ ] Adjacent generated pages do not share the same body paragraph with swapped nouns.
- [ ] The page has a named author/reviewer when the topic affects money, legal, health, or work.
- [ ] Schema matches visible content exactly.

## Output

Write one of:

- Edited page file, if the user asked for implementation.
- `projects/<client>/research/editorial-qa-<slug>.md`, if the user asked for review only.

When reviewing only, lead with publish blockers, then high-impact rewrite notes, then optional
style improvements.

## Falsifiability

State how we would know the edit failed:

- readers bounce or do not scroll past the first answer block;
- page indexes but does not retain rankings after sibling pages publish;
- AI answers cite the page but misrepresent the brand because the entity/proof is unclear;
- sales/client feedback says the page sounds generic or inaccurate.

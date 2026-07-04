---
name: ai-citation-sprint
description: >
  Run a fast SEO/GEO/AEO execution sprint that makes a product easier for AI engines to find,
  understand, cite, and recommend. Use when asked for an AEO sprint, AI citation sprint, GEO
  bootstrap, "be like AEO Engine", 100-day AI search plan, CITE-style audit, AI visibility
  execution roadmap, or an end-to-end product SEO/GEO bootstrap. Orchestrates existing skills:
  geo-audit, aeo-content-patterns, schema-markup, technical-seo-audit, internal-linking,
  customer-research, programmatic-seo, backlink-analysis, rank-tracking, and report-generator.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# ai-citation-sprint

Orchestrate a product's path from "AI systems do not know or cite us" to a measured, defensible
AI-search presence. This skill is inspired by public AEO agency patterns such as AEO Engine's
managed execution model: audit, prompt mapping, source pages, schema/entity fixes, authority
signals, and weekly measurement. Keep using Ahrefs/Brand Radar until the framework's replacement
provider layer is finalized.

## Core Principle

Do not stop at a diagnostic report. Every sprint must create or improve assets that AI systems can
actually cite: source pages, comparison pages, proof pages, schemas, `llms.txt`, internal links,
third-party corroboration, and measurement logs.

## CITE+ Framework

Score every project across five pillars:

1. **Coverage** — Does the brand appear across the prompts, SERPs, directories, communities, and
   third-party sources where AI systems look?
2. **Indexability** — Are the canonical pages crawlable, internally linked, included in sitemaps,
   and free of robots/canonical/schema blockers?
3. **Trust** — Are claims backed by reviews, case studies, named people, citations, credentials,
   and credible third-party mentions?
4. **Entity** — Is the brand clearly defined: who it serves, what category it belongs to, what it
   offers, and how it differs from alternatives?
5. **Extraction** — Are pages structured so AI can lift the answer: direct definitions, tables,
   FAQs, HowTo steps, sourced statements, and schema matching visible text?

## Workflow

### 1. PERCEIVE — baseline visibility

- Resolve project: `./bin/mkt config show --project <client>`.
- Read `client.yml`, `BUILD-STATUS.md`, existing research, and deliverables.
- Use Ahrefs MCP per `knowledge/ahrefs-mcp-map.md`:
  - Brand Radar for mentions, share of voice, cited domains/pages, AI responses.
  - Rank Tracker and SERP overview for search visibility.
  - Site Audit / Site Explorer for crawl and authority context.
- If Brand Radar is not configured, create a manual prompt grid and append to
  `projects/<client>/data/ai-citation-log.csv`. Run that grid live with the `web-research` skill's
  probe mode (OpenRouter, `perplexity/sonar`) — it costs a fraction of a cent per prompt, so the
  whole grid is cheap to run on a schedule even without Brand Radar.

### 2. ANALYZE — map prompts to source pages

Create `research/ai-citation-sprint.md` with:

- Prompt classes: what-is, how-to, best-for, vs/alternative, pricing, trust/proof, local/use-case.
- Target page for each prompt.
- Current citation state: cited / absent / wrong / competitor-cited.
- Missing source-page type: hub, comparison, FAQ, proof, case study, glossary, calculator, guide.

### 3. VALIDATE — blockers before content

Run or route to:

- `technical-seo-audit` for crawl/indexability.
- `schema-markup` for Organization, Product/SoftwareApplication, FAQ, HowTo, Breadcrumb, Article.
- `customer-research` for VOC and community language.
- `positioning-messaging` if the entity/category language is unclear.

Block publication if the brand cannot truthfully support the claims a page needs.

### 4. ACT — build answer assets

Use the narrowest skill that fits:

- `aeo-content-patterns` for page-level citability rewrites.
- `content-brief` for writer-ready briefs.
- `programmatic-seo` for safe scale pages with unique row data.
- `comparison-pages` for alternatives/vs pages.
- `human-seo-editor` for final editorial pass.
- `internal-linking` for hub/spoke and source-page routing.
- `backlink-analysis`, `local-seo`, and `customer-research` for third-party corroboration,
  directories, reviews, community mentions, and partner citations.

### 5. MEASURE — weekly sprint readout

Track:

- AI engines citing brand: ChatGPT, Perplexity, Google AI Overviews/AI Mode, Gemini, Claude,
  Copilot where available.
- Cited pages/domains and competitor citations.
- Indexed source pages.
- Top-20/page-1 rankings for source-page queries.
- Organic sessions, assisted conversions, demo/contact events, and AI referrals where detectable.

Append snapshots to project `data/` and render reports through `report-generator`.

## Outputs

- `research/ai-citation-sprint.md` — CITE+ score, prompt map, blockers, asset plan.
- `data/ai-citation-log.csv` — append-only prompt history.
- `deliverables/llms.txt` and/or `llms-full.txt` plan when relevant.
- Page briefs/rewrites generated by the routed skills.
- Weekly/monthly report via `report-generator`.

## What We Do Better Than A Monitoring-Only Tool

- We produce the asset plan, not only the score.
- We preserve a falsifiable trail: observation, dependency, failure indicator.
- We keep content human-reviewed through `human-seo-editor`.
- We separate owned data, provider estimates, and manual prompt evidence so reporting is honest.

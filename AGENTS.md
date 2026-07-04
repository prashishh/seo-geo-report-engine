# seo-geo-report-engine — operating manual

This is the **parent framework** for running marketing / SEO / GEO / growth engagements.
Capabilities (skills, workflows, tools, templates, playbooks) live **here, in the parent**.
Each client lives in `projects/<client>/` and is **pure data** — it inherits every capability
from this parent. Build a capability once; every project gets it.

> Works two ways: **(1)** launch Claude Code in this folder and everything is in scope, or
> **(2)** install this folder as a plugin (`seo-geo-report-engine`) and the skills/commands/agents
> are available anywhere. Same source of truth (`.claude/` symlinks → root `skills|commands|agents`).

---

## Operating model — the brain, not the builder

This framework produces strategy and handoff-ready artifacts; it **does not publish, deploy, or
ship anything to a live site**. That is always the client's own team's job. What it delivers:

- **Strategy** — positioning, keyword/page architecture, GTM, prioritization.
- **Findings** — trends, live data reads, competitor movement, what changed and why.
- **Ready-to-implement artifacts** — briefs, page specs/HTML, schema, llms.txt — handed off for
  the client's engineers/CMS team to build and ship on their own timeline and review process.
- **Feedback** — recommendations, risk flags, and a falsifiable read on what's working.

So: no skill or workflow should assume it needs "CMS access" or "publish access" to finish its
job — the job is done when the deliverable is handoff-ready. Dashboard/status language says
**"ready to hand off"** and **"needs review before handoff,"** never "ready to publish." When a
project's BUILD-STATUS lists open items, frame them as what the *client's* team needs to confirm
or supply.

**Client-facing copy rules.** Reports name competitors and cite real numbers (no vague
euphemisms), never name the underlying data providers (use neutral source labels: "live search
data", "public review data", "public company profiles"), label every modeled figure an estimate,
and drop uncertain data rather than show it. No em dashes in client copy.

---

## The layers

| Layer | Path | What it is | Who edits |
|-------|------|-----------|-----------|
| **Skills** | `skills/<name>/SKILL.md` | Capabilities the model invokes automatically (narrow, reusable). | Framework |
| **Workflows** | `commands/<name>.md` | Slash commands that orchestrate skills + agents into a full deliverable. | Framework |
| **Agents** | `agents/<name>.md` | Specialist subagents (seo / geo / content / data / report). | Framework |
| **Tools** | `tools/**` | Deterministic, **stdlib-only Python** scripts. Run via `./bin/mkt`. | Framework |
| **Templates** | `templates/**` | Deliverable skeletons (proposal, reports, briefs, `client.yml`). | Framework |
| **Playbooks** | `playbooks/*.md` | Portable methodology. Skills point here. | Framework |
| **Knowledge** | `knowledge/*.md` | Shared reference (rubrics, schema, AI-crawler list). | Framework |
| **Projects** | `projects/<client>/` | One client = one folder of data. **Gitignored except the demo.** | Per client |

**Golden rule:** logic lives in `tools/` + `playbooks/`. Skills/commands are thin wrappers that
point at them. This keeps everything usable in Claude Code, Codex, and plain shell alike.

---

## Activating a project

Most skills/tools operate on an **active project**. Set it one of three ways (highest priority first):

1. An explicit `--project <name>` / path argument passed to a tool.
2. `MKT_PROJECT=<name>` environment variable.
3. The folder you're working in, if it is under `projects/`.

Resolve it anytime with:

```bash
./bin/mkt config show              # active project + merged config
./bin/mkt config show --project demo
```

A project is defined by `projects/<client>/client.yml` (profile, domain, competitors,
target keywords, locales, brand voice, API project ids). See `templates/client.yml.example`
and the shipped fictional example in `projects/demo/`.

Project output goes in that project's own folders — never the parent:
`inputs/` (briefs, exports), `research/` (audits, keyword/competitor data),
`deliverables/` (proposals, reports), `data/` (snapshots, rank history, csv).

---

## Data sources — priority order

1. **DataForSEO** (`tools/connectors/dataforseo.py`) — the pay-as-you-go backbone: SERP + AI
   Overview, keywords + KD, ranked keywords, keyword + link gap, backlinks, Lighthouse CWV,
   domain/traffic intelligence, Google Business ratings, Ads Transparency, Google Trends, and
   direct LLM querying across ChatGPT/Gemini/Claude/Perplexity. ~$1–2 for a full first-scan.
2. **Ahrefs MCP** (if connected) — Rank Tracker, Site Explorer, Keywords Explorer, Site Audit,
   Brand Radar (GEO/AI visibility), Web Analytics, GSC. Prefer it when present; when a response
   has `render_with` metadata, call the named render tool. Monetary values are in **USD cents** —
   divide by 100.
3. **Web** — `WebFetch` / `WebSearch` for SERP spot-checks, AI Overview capture, competitor pages.
4. **OpenRouter (`web-research` skill)** — live, cited multi-source research (Perplexity Sonar
   deep-research) and cheap AI-citation probing, when static web tools aren't enough or the
   question is literally "what does AI currently say about this brand."

Keys: copy `config/secrets.example.env` → `config/secrets.env` (gitignored). See the README for
the key-by-key table with costs.

---

## Routing — what to reach for

**Not sure where to start?** → `skill-navigator` turns a vague client goal into an ordered, multi-skill plan.

| The user wants… | Use |
|---|---|
| New client setup | `/new-client` → then `/discovery-audit` |
| Full intake audit | `/discovery-audit` |
| The client-facing first-scan pitch report, end to end | `/client-report` → `first-scan-report` |
| Where's the opportunity / how do we beat competitor X | `opportunity-map` → `/growth-plan` |
| A growth proposal | `/growth-proposal` → `proposal-builder` |
| Weekly / monthly client report | `/weekly-report` · `/monthly-report` → `report-generator` |
| Positioning / messaging / value prop | `positioning-messaging` *(GTM)* |
| Voice-of-customer / persona research | `customer-research` *(GTM)* |
| Market sizing / TAM-SAM-SOM / PMF | `market-opportunity` *(GTM)* |
| Keyword research + clustering | `keyword-research` |
| AI-search / GEO visibility (brand level) | `geo-audit` |
| Make one page AI-citable (page level) | `aeo-content-patterns` |
| Google AI Overview / live SERP / PAA | `serp-intel` |
| Cross-engine AI-visibility scan (ChatGPT/Gemini/Claude/Perplexity/AIO) | `llm-visibility` |
| AI Share of Voice (weighted prompt set → SoV% → trend) | `llm-visibility` (prompt_set → sov) |
| Domain authority consensus (client + competitors) | `domain-authority` |
| Live cited web research / "what does AI say about us" | `web-research` |
| Competitor gap analysis | `competitor-analysis` |
| Weekly competitor monitoring | `/competitor-watch` |
| Programmatic / bulk pages | `programmatic-seo` |
| "X vs competitor" pages | `comparison-pages` |
| Content brief for a writer | `content-brief` |
| Refresh decaying content | `content-refresh` |
| Internal-link architecture | `internal-linking` |
| Technical / on-page audit | `technical-seo-audit` |
| International / hreflang setup | `hreflang-i18n` |
| Local / Google Business Profile | `local-seo` |
| Schema / structured data | `schema-markup` |
| Backlink analysis + link gap | `backlink-analysis` |
| Rank tracking | `rank-tracking` |
| KPI dashboard | `kpi-dashboard` |

**The GTM layer feeds SEO.** `positioning-messaging` + `customer-research` produce the canonical
brand language + voice-of-customer (written to `client.yml: messaging:` and `research/voc.md`) that
`content-brief`, `comparison-pages`, `programmatic-seo`, and `proposal-builder` all inherit.

When in doubt, read the relevant `playbooks/*.md` — that's the methodology the skill encodes.

---

## Conventions

- **Tools are stdlib-only.** No `pip install` required. Run them through `./bin/mkt` (it finds a
  Python ≥ 3.8 automatically).
- **Deliverables are HTML → PDF** via headless Chrome (`tools/pdf`). Charts are inline **SVG**
  from `tools/charts` (no matplotlib).
- **Every recommendation is falsifiable** (PERCEIVE → ANALYZE → VALIDATE → ACT).
  State the observation, the dependency, and "how we'd know this failed."
- **Don't put client data in the parent.** Don't put framework logic in a project. Real client
  projects are gitignored; only the fictional `projects/demo/` ships with the repo.
- Dates: write absolute (`2026-07-04`), not "today".

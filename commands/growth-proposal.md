---
description: Build a branded growth-proposal PDF — gather research + client.yml, invoke proposal-builder, render and review.
argument-hint: "<project>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /growth-proposal <project>

Thin workflow that produces the **growth-proposal PDF** (the 3-pillar deck) for **$1**
(defaults to the active project — resolve with `./bin/mkt config show`). The methodology and all the
real work live in the **`proposal-builder`** skill and `playbooks/proposal-methodology.md`; this
command just gathers the inputs, invokes the skill, renders, and reviews.

## Steps

1. **Gather inputs.** `./bin/mkt config show --project $1`. Read `client.yml` (profile, ICP,
   competitors, target keywords, brand colors, market) and everything in `projects/$1/research/` —
   especially `DISCOVERY.md` if `/discovery-audit` has run. Glob the brief/notes in
   `projects/$1/inputs/`. If `research/` is empty, suggest running **`/discovery-audit $1`** first
   (the proposal is stronger with evidence), or let the skill fill the minimal gaps itself.

2. **Invoke `proposal-builder`.** Hand it the project. The skill: resolves context, fills only the
   research gaps the deck needs (Ahrefs MCP first), picks the spine (Foundation → Wide Net/
   Acquisition → Conversion/Lifecycle), sizes the opportunity, builds conservative/probable/
   aggressive scenarios from explicit assumptions, and composes `projects/$1/proposal.yml` per
   `templates/proposal/proposal.schema.md`.

3. **Render the PDF.**
   ```bash
   ./bin/mkt proposal build --project $1
   ```
   → writes `projects/$1/deliverables/$1-growth-proposal.{html,pdf}`.

4. **Review the PDF.** Open / Read the rendered pages. Check: cover, the three pillar cards, chart
   readability, page breaks, no escaped-quote artifacts, and that numbers are consistent across
   sections (the scenario table matches the chart matches the scorecards). Iterate on `proposal.yml`
   and rebuild until clean.

5. **Report back.** Summarize the headline KPIs, the scenario assumptions, and any open questions
   the user should confirm before this goes to the client.

## Notes
- Every projection must be **falsifiable** — tied to an assumption the reader can challenge. Label
  illustrative/assumed numbers as such; never imply data we didn't pull.
- Brand comes from `client.yml: brand` (`primary` + `accent`); falls back to `config/framework.yml`.
- Keep it tight — the reference decks are ~10 pages, one strong chart per section.

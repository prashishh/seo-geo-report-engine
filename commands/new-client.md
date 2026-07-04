---
description: Scaffold a new client project — folders, client.yml, CLAUDE.md — then interview for the essentials and fill the profile.
argument-hint: "<slug>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /new-client <slug>

Stand up a new client project at `projects/$1/`. The slug (`$1`) is kebab-case and becomes the
output filename prefix everywhere. A project is **pure data** — it inherits every capability from
this parent framework (see the root `CLAUDE.md`). This command does the scaffold, then interviews
the user for the profile that the skills downstream depend on.

## Steps

1. **Guard.** If `projects/$1/` already exists, stop and tell the user (offer to open `client.yml`
   instead). Slug must be kebab-case — lowercase, hyphens, no spaces.

2. **Scaffold the folders.**
   ```bash
   mkdir -p projects/$1/{inputs,research,deliverables,data}
   ```
   - `inputs/` — briefs, exports, source material the client gave us.
   - `research/` — keyword / competitor / GEO / audit outputs we generate.
   - `deliverables/` — proposals, reports, comparison pages (the handover).
   - `data/` — snapshots, rank history, csv (`data/raw/` is gitignored).

3. **Copy the templates** (don't author from scratch — copy then edit):
   ```bash
   cp templates/client.yml.example projects/$1/client.yml
   cp templates/project/CLAUDE.md   projects/$1/CLAUDE.md
   ```

4. **Interview the user for the essentials.** Ask in one batched message; let them answer what they
   know and leave the rest blank. Capture:
   - **Name** + **domain** (apex, e.g. `acme.com`).
   - **Industry** (one line) and **market** (primary geo) + **languages**.
   - **Positioning** — 2–3 lines: what they sell, to whom, the wedge.
   - **ICP** — the ideal customer profiles / segments.
   - **Competitors** — name + domain for each (used by competitor + comparison skills).
   - **Target keywords** — seed terms for keyword / rank / programmatic work.
   - **Brand colors** — `primary` and `accent` hex (for proposal/report decks).
   - **Ahrefs ids** — `project_id` (Rank Tracker / Site Audit) and `brand_radar_report_id` (GEO).
     If the user doesn't have them, offer to list with `management-projects` and
     `management-brand-radar-reports` (Ahrefs MCP) and match by domain, then paste the ids in.
   - **Owned analytics** (optional) — GA4 property id, GSC site (`sc-domain:…` or URL).

5. **Fill `projects/$1/client.yml`.** Edit in every answer; set `slug: $1`. Leave fields the user
   couldn't answer blank rather than inventing values — downstream skills will flag the gap. Keep
   `positioning` honest and specific (no boilerplate).

6. **Set the engagement header.** Edit `projects/$1/CLAUDE.md`: replace `<Client>` / `<slug>` and
   add any goals, constraints, deadlines, or brand-voice notes the user gave. Use absolute dates
   (today is 2026-06-23).

7. **Confirm + hand off.** Show the user the filled `client.yml` for a sanity check. Then recommend
   **`/discovery-audit $1`** to run the full intake audit (keyword, technical, competitor, GEO,
   backlink) that feeds the growth proposal.

## Notes
- **Never put client data in the parent**, and never put framework logic in the project.
- Don't fabricate Ahrefs ids, volumes, or competitors to fill the form — blanks are honest.
- If the user only has a domain, you can pre-seed competitors with `site-explorer-organic-competitors`
  and keywords with `site-explorer-organic-keywords` (Ahrefs MCP) and confirm them in the interview.

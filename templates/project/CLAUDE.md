# <Client> — project context

This folder is **data only**. All capability (skills, workflows, tools) is inherited from the
parent `seo-geo-report-engine` framework. See the parent `CLAUDE.md` for routing.

## This client
- Profile, competitors, keywords, brand, and API project ids live in `client.yml`.
- Resolve merged config: `./bin/mkt config show --project <slug>` (or set `MKT_PROJECT=<slug>`).

## Folders
- `inputs/` — briefs, exports, source material the client gave us.
- `research/` — keyword / competitor / GEO / audit outputs we generate.
- `deliverables/` — proposals, reports, comparison pages (the things we hand over).
- `data/` — snapshots, rank history, csv. `data/raw/` is gitignored.

## Engagement notes
<!-- goals, constraints, deadlines, brand voice, do/don't — keep current; use absolute dates -->

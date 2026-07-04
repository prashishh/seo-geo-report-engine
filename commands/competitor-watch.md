---
description: Weekly competitor monitoring — diff this week's competitor snapshots against last week and recommend 48-hour responses.
argument-hint: "[project]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
---

# /competitor-watch [project]

Weekly competitor watch for **$1** (defaults to the active project — resolve with
`./bin/mkt config show`). Pulls a fresh snapshot of each competitor, **diffs it against the last
stored snapshot**, and writes a dated brief of what changed plus recommended 48-hour responses.
This is the recurring companion to the one-time `competitor-analysis` skill; methodology and the
48-hour discipline live in `playbooks/competitor-intel.md`.

## Steps

1. **Load context.** `./bin/mkt config show --project $1`. Read `client.yml` → our `domain`,
   `competitors[]`, `market`, `ahrefs.project_id`. If competitors are empty, stop and tell the
   user to populate `client.yml` (or run the `competitor-analysis` skill first).

2. **Load the previous snapshot.** Look in `projects/<client>/data/competitor-snapshots/`. Use the
   most recent `competitor-snapshot-<YYYY-MM-DD>.json`. If none exists, this is the **baseline
   run** — capture the snapshot, note there's no diff yet, and skip to step 6.

3. **Pull current snapshots (Ahrefs MCP first — `knowledge/ahrefs-mcp-map.md`).** Per competitor
   domain capture:
   - **Organic keywords** — `site-explorer-organic-keywords` → store the top set so you can derive
     **new** and **lost** keywords next week (which terms moved into / out of top-10).
   - **Referring domains** — `site-explorer-referring-domains` → **new ref domains** this week.
   - **Top pages** — `site-explorer-top-pages` / `site-explorer-pages-by-traffic` → **new or
     newly-surging pages** (a page that wasn't there or jumped in traffic = a fresh content bet).
   - **Domain Rating** — `site-explorer-domain-rating` → **DR change** vs last snapshot.
   - **Ads** — `WebFetch` the **Meta Ad Library** (`https://www.facebook.com/ads/library/`) for
     each competitor → **new active creatives / offers**. Note new seasonal or discount pushes.
   - (Optional, if `ahrefs.project_id` is set) `rank-tracker-competitors-overview` for tracked-term
     position moves against us.

4. **Diff against the previous snapshot.** For each competitor compute:
   - Organic keywords **gained** and **lost** (top-10 in/out).
   - **New referring domains** (and whether any link to ≥2 competitors — a prospect for us too).
   - **New / surging top pages** (new content topics to react to).
   - **DR delta** (+/-).
   - **New ads / offers** since last week.

5. **Write the brief.** `projects/<client>/research/competitor-watch-<YYYY-MM-DD>.md` (use the
   absolute run date). Structure:
   - **What changed** — per competitor, the gained/lost keywords, new ref domains, new/surging
     pages, DR delta, new ads/offers. Lead with what's material; drop noise.
   - **So what** — interpret: is a competitor launching a topic cluster, buying links, running a
     seasonal promo, or moving on a term we own?
   - **Recommended 48-hour responses** — concrete, falsifiable actions to ship within two days
     (e.g. "match their `<offer>` on our PPC landing page"; "publish a counter to their new
     `<topic>` page"; "reach out to the 3 new ref domains linking to two competitors"). Each item:
     *observation → response → dependency → leading indicator that tells us within ~2 weeks if it
     worked*.

6. **Save the new snapshot.** Write the current pulls to
   `projects/<client>/data/competitor-snapshots/competitor-snapshot-<YYYY-MM-DD>.json` so next
   week diffs against it. Keep history — never overwrite prior snapshots.

## Cadence
Run weekly. For a true automated cadence, schedule it with the **`/loop`** skill
(`/loop 1w /competitor-watch <project>`) or the **`/schedule`** routines (a weekly cron cloud
agent). The 48-hour response window is the point — surface moves while they're still reactable.

## Notes
- **Data priority: Ahrefs MCP > CLI > web** (web only for the Meta Ad Library). Call `doc` on a
  tool before first use; monetary values are USD cents (÷100).
- Snapshots are append-only client data — they live under `projects/<client>/data/`, never the
  parent. The brief lives under `research/`.
- Findings here feed back into the `competitor-analysis` deliverable and the growth proposal when
  the picture shifts materially.

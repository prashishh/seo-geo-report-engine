---
name: agency-dashboard
description: >
  Build or refresh the seo-geo-report-engine agency dashboard: a live operating console showing the
  framework, all client projects, status, blockers, research and deliverables produced, handoff
  readiness, and next actions. Use when asked for a dashboard, agency portal, project status
  overview, onboarding portal, client inventory, project health report, or "one stop agency
  dashboard".
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# agency-dashboard

A live operating console for the framework and its client projects, built to be worked from
instead of Claude Code once a project is underway. Everything renders from project files on
every request — never hand-maintain status in HTML.

## Command

```bash
./bin/mkt dashboard serve          # live server, opens the browser; re-reads files on refresh
./bin/mkt dashboard build          # static export to projects/_dashboard/ (no server needed)
```

Prefer `serve` — it's a real HTTP server (`tools/dashboard/build.py`'s `_Handler`), so adding a
skill, a project, or a file shows up on the next refresh with zero rebuild step. `build` is for a
portable snapshot (e.g. to hand someone a folder of static HTML).

## What It Reads

- `skills/*/SKILL.md`, `commands/*.md`, `agents/*.md`, `playbooks/*.md`, `tools/*/` — the live
  capability inventory (grouped, described in plain English, each one clickable for detail).
- `projects/*/client.yml` for client identity, domain, ICP, competitors, keywords, Ahrefs ids,
  messaging one-liner.
- `projects/*/BUILD-STATUS.md` for human-written status and blockers.
- `research/`, `deliverables/`, `inputs/`, and `data/` inventories, with file mtimes for the
  recent-activity feed.
- HTML deliverables for placeholder counts: `{{TODO}}`, `[NEEDS...]`, `[AUTHOR:]`,
  `[unverified]`, and `[confirm client may display]`.

## Pages

- **Overview** — portfolio snapshot (projects, pages drafted, research artifacts, skills, tracking
  configured, handoff review items), a delivery-stage pipeline, a "needs attention" panel, a
  recent-activity feed, the capability layer summary, and project cards.
- **Capabilities** — the five-layer explainer (workflows/skills/agents/tools/playbooks) plus every
  skill grouped by area; click any skill or playbook for its own detail page.
- **Per-project** — stage/health/handoff pills, a completion ring, a headline quote (the client's
  messaging one-liner), the rendered `BUILD-STATUS.md`, and every artifact grouped
  strategy-first (inputs → research & strategy → schema/specs → pages produced → other
  deliverables → tracking data) with the built pages last, since that's execution output, not
  the thinking.
- **In-console viewers** — every file type opens inside the console, not a raw tab: markdown
  renders as formatted text, CSV as a table, JSON pretty-printed, and built HTML pages render in
  an embedded preview frame (with an "Open full page" escape hatch).

This framework's job stops at strategy, research, trend-finding, and ready-to-implement page
files. It does not publish or deploy anything for a client — that's their own team's job. So the
dashboard never implies we're the ones shipping: it reports what's ready to **hand off** and what
still **needs review**, never "ready to publish."

## Status Heuristics

- **Blocked:** handoff blockers or `{{TODO}}` markers remain in deliverables.
- **Ready to hand off:** pages exist and only review/source placeholders remain.
- **In production:** research exists but deliverables are thin.
- **Setup needed:** `client.yml` exists but little/no project work exists.

Treat these as operating heuristics, not client-facing truth. If a project has a richer
`BUILD-STATUS.md`, that file overrides the nuance.

## Design Rules (established by user feedback, keep applying them)

- No colored edge-border accents on cards/panels (an AI-generated-design tell) — carry color
  through filled number badges, small tag dots, status pills, and tinted blocks instead.
- Zero em dashes anywhere rendered, UI copy or file content. Use the `_nd()` normalizer on any new
  rendered text.
- Modern, ClickUp/Linear-style visual language: soft shadows, generous radius, restrained color,
  not a 2000s admin panel.

## Maintenance Rules

- Do not put framework logic inside client project folders.
- Do not copy client data into skills.
- Keep the generator stdlib-only (no pip installs) — it must also run headless/unattended.
- Add dashboard-specific UI assets inside `tools/dashboard/` or inline them in the generated HTML.

---
name: skill-navigator
description: >
  Meta-router that turns a vague client ask into an ordered, multi-skill workflow with
  ready-to-run handoff prompts. Use when the user says "where do I start", "what should we
  do for this client", "which skill for X", "plan the engagement", "how do I approach this",
  or hands over a broad multi-skill goal with no obvious single skill. Reads the LIVE
  skills/ and commands/ inventory at runtime, matches intent to a primary skill + up to two
  supporting skills + the right /command, and emits an ordered plan where every step has a
  copy-paste prompt and the client.yml fields / research artifacts it depends on.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# skill-navigator

Pure orchestration. The user has a goal but doesn't know which capability to reach for — or
the goal spans several. This skill **reads the live catalog**, picks the shortest correct path
through it, and hands back an ordered plan the user (or the next agent) can run step by step.
It does **no MCP calls and produces no analysis** — it routes. The CLAUDE.md routing table is a
starting hint, but the inventory on disk is the source of truth: a skill exists only if its
folder does.

## Methodology (PERCEIVE → ANALYZE → VALIDATE → ACT)

**PERCEIVE — read the live inventory.** Never hardcode the skill/command list; the catalog
grows. Resolve the project if one is implied (`./bin/mkt config show --project <client>`), then:

```bash
ls -1 skills/                                   # every available skill
ls -1 commands/                                 # every /command workflow
for f in skills/*/SKILL.md; do printf '\n=== %s ===\n' "$f"; sed -n '1,12p' "$f"; done
sed -n '1,40p' commands/*.md                    # what each /command orchestrates
```

Read the `description` frontmatter of candidate skills and the intro of candidate commands so
matching is grounded in what each actually does — not in this file's memory of them. If a
client is named, read `projects/<client>/client.yml` and `ls projects/<client>/research/` to
see which inputs/artifacts already exist (so the plan starts where the client actually is).

**ANALYZE — match intent → ordered path.** Decompose the ask into intents, then map each to the
inventory:
- **Primary skill** — the one capability that most directly satisfies the core ask.
- **Up to 2 supporting skills** — what the primary needs upstream (e.g. `keyword-research`
  before `content-brief`) or what naturally follows downstream.
- **A /command if one fits** — commands orchestrate multiple skills into a full deliverable
  (e.g. `/discovery-audit`, `/growth-proposal`). Prefer a command over hand-chaining skills
  when it already encodes the same path.
- **Order by dependency**, not by preference: a step that consumes `research/keywords.csv` comes
  after the step that writes it. GTM skills (`positioning-messaging`, `customer-research`) feed
  SEO/content skills — sequence them first when the brand language doesn't exist yet.

**VALIDATE — every routing call is falsifiable.** For the plan as a whole, and any non-obvious
step, state:
- **Observation** — the phrase in the ask + the catalog entry that justifies the match (cite the
  skill's `description`).
- **Dependency** — the `client.yml` fields or research artifacts the step needs to run (e.g.
  `competitors:`, `target_keywords:`, `research/voc.md`, `data/rank-history.csv`). Flag any that
  are missing — a missing dependency becomes its own earlier step.
- **How we'd know this routing was wrong** — a leading indicator: e.g. "primary skill produces no
  usable output because `client.yml` has no `competitors:`", or "user re-asks the same question
  after step 1 → wrong primary skill, re-route." Note when the ask is ambiguous enough that you
  should ask one clarifying question before emitting the plan.

**Inventory-bound — hard rule.** Only route to skills/commands that appeared in the `ls` output
above. Never invent, rename, or assume a capability. If the ask needs something the catalog
doesn't have, say so explicitly and route to the closest existing skill (or suggest the gap),
rather than fabricating a skill name.

**ACT — emit the routing plan.** Output **inline** an ordered plan. For each step:

1. **Step N — `<skill-or-/command>`** (primary/supporting) — one line on why it's here.
2. **Needs** — the `client.yml` fields + research artifacts the step consumes (mark missing ones).
3. **Produces** — the artifact(s) it writes (so the next step's "Needs" line is traceable).
4. **Handoff prompt** — a copy-paste, self-contained instruction the user can drop into a fresh
   turn to run that step, with the client and key parameters filled in. Example:
   `Run keyword-research for demo on seeds "acoustic panels, soundproofing" for en-GB.`

End with a one-line **critical path** (the minimum ordered sequence) and any **clarifying
question** if the ask was ambiguous.

Optionally also write the plan to `projects/<client>/inputs/engagement-plan.md` (same content)
when a client is active and the user wants it persisted — otherwise keep it inline only.

## Notes
- This is a router, not a doer: don't run the downstream skills yourself unless asked — hand off.
- Re-read the inventory every invocation; a plan baked from memory goes stale as the catalog grows.
- When a /command and a hand-chained skill path both fit, prefer the command and name the skills
  it wraps so the user sees the whole path.
- If nothing in the catalog fits, say so plainly — a wrong route costs more than an honest gap.
- Absolute dates only (today 2026-06-23). No MCP, no client analysis — pure orchestration.

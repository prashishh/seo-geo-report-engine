---
name: web-vitals
description: >
  Measure a live page's real Core Web Vitals online via Google PageSpeed Insights (Lighthouse lab
  + CrUX field data) and turn the result into a prioritized, falsifiable fix list. Use when asked to
  "check web vitals", "run a PageSpeed / Lighthouse test", "what is the LCP/INP/CLS of this page",
  "is this page fast", "page speed audit", "measure performance of a URL", "why is my page slow",
  or "get real-user performance data". Pulls live mobile + desktop scores for any URL, flags each
  metric good / needs-improvement / poor against Google's thresholds, and lists the biggest
  opportunities. Hands the actual optimization work to core-web-vitals and performance.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# web-vitals

Gets the **real, online** Core Web Vitals for a live URL and reads them honestly. This is the
*measurement* skill; the *optimization* methodology lives in `core-web-vitals` and `performance`.

## Why a separate skill
`core-web-vitals` and `performance` describe how to FIX speed. This skill answers "where do we
actually stand right now?" using live data from Google's PageSpeed Insights API — both the
**field** (CrUX, real Chrome users, what Google ranks on) and **lab** (Lighthouse, a single
controlled load) numbers. Never report lab numbers as if they were field reality.

## Tool
Stdlib, no install. Hits the free PageSpeed Insights API:

```bash
./bin/mkt 2>/dev/null  # (just to resolve a usable python)
python3 tools/connectors/pagespeed.py <url>            # mobile
python3 tools/connectors/pagespeed.py <url> desktop
python3 tools/connectors/pagespeed.py <url> both       # mobile + desktop
```

It returns: `performance_score`, `field_cwv` (LCP / INP / CLS / FCP / TTFB with a good /
needs-improvement / poor verdict each), `field_overall`, the `lab` timings, and the top
`opportunities`. **API key:** the call works anonymously but is rate-limited (HTTP 429). For
repeated use add a free `GOOGLE_PSI_API_KEY` to `config/secrets.env` (one click at
developers.google.com/speed). The tool retries with backoff and prints a clear message if throttled.

## Workflow (PERCEIVE → ANALYZE → VALIDATE → ACT)

1. **PERCEIVE.** Run the tool for the target URL, **mobile first** (Google indexes mobile). Pull
   `both` when desktop matters too. If the field block is empty, the URL lacks enough CrUX traffic —
   say so, and fall back to the lab numbers *explicitly labeled as lab-only*.

2. **ANALYZE.** Grade each Core Web Vital against the thresholds:
   - **LCP** (loading): good ≤ 2.5s · poor > 4.0s
   - **INP** (interactivity): good ≤ 200ms · poor > 500ms
   - **CLS** (visual stability): good ≤ 0.10 · poor > 0.25
   Lead with the **field** verdict (that's the real-user truth and the ranking signal); use lab +
   `opportunities` to explain *why* a failing metric fails. A page can pass field while failing lab,
   or vice-versa — call that out, don't average them.

3. **VALIDATE.** Each recommendation is falsifiable: name the metric it should move, the expected
   direction, and how we'd know it failed. Example: "Preload the LCP hero image → field LCP p75
   drops below 2.5s within ~28 days of CrUX data; *failed if* p75 is unchanged after a full CrUX
   window despite the image confirmed preloaded."

4. **ACT.** Produce a short prioritized list ordered by *field impact × effort*, mapping each fix to
   the skill that does it: render-blocking / unused JS / image weight → `performance`; layout-shift
   and LCP-element work → `core-web-vitals`; render-path or indexability blockers → `technical-seo-audit`.
   Hand off rather than re-deriving their methodology here.

## Save & track
Write the run to the active project so it trends over time:
`projects/<client>/research/web-vitals-<date>.md` (the table of scores) and, for a tracked page,
append the field p75s to `data/web-vitals-history.csv` so `kpi-dashboard` / `report-generator` can
chart movement. Page experience is one input to rankings, not the whole story — frame it that way.

## Notes
- Field data lags ~28 days (CrUX is a rolling 28-day window), so a fix shipped today shows up later —
  set that expectation in any report.
- No project context needed to spot-check a URL; with a project active, save the output as above.
- Pairs with `web-quality-audit` (broader Lighthouse: a11y / SEO / best-practices) when the ask is
  wider than speed.

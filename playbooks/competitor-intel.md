# Playbook — Competitor Intelligence

The portable methodology behind the `competitor-analysis` skill and the `/competitor-watch`
command. This is the IP; the skill/command are thin wrappers that point here. Engine is Ahrefs
MCP (`knowledge/ahrefs-mcp-map.md`); data priority is **Ahrefs MCP > CLI connectors > web**.

Operating loop is **PERCEIVE → ANALYZE → VALIDATE → ACT**. Nothing ships without a falsifiable
claim: an observation, the dependency it rests on, and the leading indicator that proves it wrong.

---

## 1. Choosing the *true* competitor set

There are two kinds of "competitor", and conflating them wastes a quarter:

- **Business rivals** — who the client sells against. Lives in `client.yml: competitors[]`.
- **Organic competitors** — who actually contests the same SERPs. From
  `site-explorer-organic-competitors`.

They overlap less than clients assume. A big-name rival may rank for nothing we care about; an
unknown affiliate or marketplace may own our money SERPs.

**Selection test — overlap on *money* keywords, not any keyword.** A domain qualifies only if it
overlaps with us on commercial/transactional terms or our `target_keywords` — not on incidental
informational long-tail. Validate by:
1. Take the union of organic competitors + `client.yml` rivals.
2. For each, pull `site-explorer-organic-keywords` and intersect with our money terms.
3. Spot-check 3–5 head terms in `serp-overview` — are they actually on the page with us?
4. Keep 3–5. Label each: **organic rival**, **business rival**, or **both**. Drop domains that
   only overlap on terms we don't monetize, however large they look.

> Falsifiable framing: "X is a true competitor because it ranks top-10 on N of our money terms."
> If a re-pull shows it shares <2 money terms, it drops out.

---

## 2. The gap-scoring model

For every gap keyword (they rank, we don't / rank >20):

```
score = Volume  ×  Intent  ×  Feasibility
```

- **Volume** — prefer **traffic potential** (`keywords-explorer-overview`) over raw exact volume;
  a term's parent topic often carries more traffic than the head phrase alone.
- **Intent** — weight by commercial value:
  `transactional/commercial (×1.0) > comparison/BOFU (×0.8) > navigational (×0.5) >
  informational/TOFU (×0.3)`. Money terms win ties.
- **Feasibility = KD measured against *our* DR**, not in the abstract:
  - KD ≤ our DR band → **quick win** (publish/optimize, expect weeks).
  - KD modestly above our DR → **build-up** (needs internal links + a few external links).
  - KD well above our DR → **long play** (a link-building campaign, flag the cost honestly).
  Pull our DR with `site-explorer-domain-rating`; check `-domain-rating-history` for momentum.
  A page where a competitor outranks us with a *weaker* page is the highest-feasibility attack.

Rank descending and tag each row `quick win` / `build-up` / `long play`. Resist scoring 500 rows —
15–30 well-scored gaps drive more action than an exhaustive dump.

**The four gaps to score and stack:**
- **Keyword gap** — terms they rank for, we don't (`site-explorer-organic-keywords`, both sides).
- **Content gap** — their best pages/topics we lack (`site-explorer-top-pages` /
  `-pages-by-traffic`), clustered into themes + formats.
- **Backlink gap** — domains linking to **≥2 competitors but not us**
  (`site-explorer-referring-domains` per competitor) = warm prospects; plus
  `site-explorer-broken-backlinks` on competitors = reclaim/recreate targets;
  `site-explorer-pages-by-backlinks` shows which pages earn the links.
- **SERP/authority gap** — live positions and feasibility via
  `rank-tracker-competitors-*`, `serp-overview`, and DR comparison.

---

## 3. Prioritization — where to attack first

Sequence by **impact × speed × defensibility**:
1. **Quick wins first** — high score + KD ≤ our DR. Banked momentum funds the slow plays.
2. **Then build-ups** that cluster around a theme — one content hub lifts a whole keyword set and
   compounds.
3. **Long plays last and explicitly costed** — name the link campaign and timeline; don't hide it.
4. **Defensibility check** — skip SERPs owned by unbeatable entities (giant brands, Reddit, a SERP
   feature you can't capture) even if the gap is large. A gap you can't close is not a priority.

Every attack-list item is falsifiable:
> *observation → bet → dependency → leading indicator (and the value that means it failed).*
> e.g. "Competitor ranks #4 for `<term>` (vol 1.4k, KD 18) with a thin page; our DR is 41.
> **Bet:** a stronger comparison page reaches top-10 in 8–10 weeks. **Depends on:** indexation +
> 2–3 internal links. **Fails if:** not in the top 30 six weeks after indexation."

---

## 4. The weekly watch loop

`/competitor-watch` makes intel a habit, not a one-off. Each week, per competitor, snapshot →
diff → react → store:

- **Snapshot:** organic keywords (for new/lost next week), referring domains (new this week), top
  pages (new/surging), Domain Rating, and new Meta Ad Library creatives.
- **Diff** against the prior snapshot in `projects/<client>/data/competitor-snapshots/`:
  keywords gained/lost, new ref domains, new/surging pages, DR delta, new ads/offers.
- **React within 48 hours** (see §5). Stale intel is just trivia.
- **Store** the new snapshot (append-only, dated) so next week has a baseline.

Automate the cadence with the **`/loop`** skill (`/loop 1w /competitor-watch <project>`) or
**`/schedule`** routines (weekly cron cloud agent). Baseline run = capture only, no diff yet.

---

## 5. Ad-library & promo discipline

Organic is half the war; offers move money this quarter. Web is the source here (Ahrefs doesn't
cover live creatives) — `WebFetch` the **Meta Ad Library**
(`https://www.facebook.com/ads/library/`) and the **Google Ads Transparency Center**
(`https://adstransparency.google.com/`), and cross-check `site-explorer-paid-pages`.

Track, per competitor:
- **Creatives** — the hooks/angles they're testing (and which run long = winners worth studying).
- **Offers** — discounts, bundles, guarantees, free-trial terms.
- **Seasonal pushes** — timing of campaigns vs the calendar (BFCM, fiscal year-end, category peaks).

**The 48-hour rule:** a new offer or a competitor moving on a term we own is a reactable event.
Match, counter, or consciously decline — within two days, while it still matters. Log the decision
so the next watch can judge whether the response worked (the leading indicator).

---

## 6. How this feeds downstream

- **`comparison-pages`** — the keyword gap (especially `vs`/`alternative` terms) and the ad/promo
  angles become the spec for "us vs <competitor>" pages, with the competitor's own offers as the
  contrast to beat.
- **Growth proposal** (`proposal-builder`) — the prioritized attack list becomes the acquisition
  pillar; gap volumes size the opportunity; the falsifiable bets become the roadmap's KPIs and the
  scenario projection's assumptions.
- **Weekly/monthly reports** — watch diffs supply the "competitive landscape" section and justify
  in-flight pivots.

---

## Source-of-truth checklist
- Call `doc` on any Ahrefs tool before first use; monetary values are USD cents (÷100).
- Save raw pulls to `projects/<client>/data/`; deliverables to `projects/<client>/research/`.
- Never put client data in the parent; never put framework logic in a project.
- Dates absolute (e.g. `2026-06-23`), never "today".

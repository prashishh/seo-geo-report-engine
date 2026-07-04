---
name: domain-authority
description: >
  Robust, multi-source domain authority for a client AND all its competitors in one command. Pulls the
  authority number from every source we can reach (DataForSEO rank, Ahrefs DR, Open PageRank, Moz DA),
  normalizes each to 0-100, and reports a consensus plus the spread (where sources disagree). Use when
  asked to "get the DA / DR", "how strong is this domain", "compare our authority to competitors",
  "domain authority for these sites", "who has the strongest backlink profile", or "score this
  competitor/prospect list by authority". More sources = more strength; no single tool's quirk drives it.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  author: seo-geo-report-engine
  version: "1.0"
---

# domain-authority

Authority ("how much trust a domain has earned") is a proxy, and every provider computes it differently,
so one number is fragile. This reads it from EVERY source available and reports the consensus + spread.

```
python3 tools/seo/authority.py --project <slug>                 # client + client.yml competitors
python3 tools/seo/authority.py --domains a.com b.com c.com      # ad-hoc set
python3 tools/seo/authority.py --project <slug> --out projects/<slug>/data/raw/dataforseo/authority-<date>.json
```

## Sources (each optional and graceful, missing keys are skipped)
- **DataForSEO** - always on (we own it): `rank` 0-1000 + referring domains + backlinks, one bulk call.
- **Ahrefs** - Domain Rating 0-100 (the recognized number), one call per domain, if `AHREFS_API_KEY` set.
- **Open PageRank (DomCop)** - FREE 0-10 link score, 100 domains/call, if `OPENPAGERANK_API_KEY` set
  (free key from domcop.com/openpagerank). The best "bulk authority at $0" source.
- **Moz** - Domain Authority 0-100 (the other recognized number), if `MOZ_TOKEN` set.

Output: a ranked table of client + competitors with each source's normalized score, the **consensus**
(mean of available sources), and the **spread** (max-min). Big spread = the sources disagree, investigate
before quoting. Writes `data/authority.csv`. If an API source is unavailable and you only need a
recognized number for a few domains, grab Moz DA / Semrush Authority Score free by hand (see
`knowledge/seo-geo-tooling-landscape.md`).

## Notes
- Powers the `first-scan-report` authority section and the `competitor-analysis` / `kpi-dashboard`
  authority pillar. Cross-check the headline number against Ahrefs before quoting a client (Ahrefs DR is
  the client-recognized metric; DataForSEO/Open PageRank are the cheap bulk cross-checks).
- The recipe stays internal; show the client the consensus number, not the method.
- To add sources: Open PageRank + Moz keys light up two more columns instantly (config/secrets.env).

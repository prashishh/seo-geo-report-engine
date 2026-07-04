"""Backlink profile + link-GAP for a client's peer set (DataForSEO Backlinks).

Two things the report needs and nothing else was surfacing:
  1. Profile comparison - referring domains, total backlinks, link-authority rank, and spam/toxicity
     for the client + every rival, in a few cheap bulk calls.
  2. The link GAP - the referring domains that link to the strongest competitors but NOT to the client.
     That is a ready-made outreach target list: the single most actionable off-page deliverable we can
     hand a client's team (brain not builder - we produce the list, they run the outreach).

    python tools/seo/backlinks.py --project <slug>

Writes data/raw/dataforseo/backlinks-<date>.json (report) + data/backlink-gap-targets.csv (handoff).
Backlinks endpoints are location-agnostic (a global link graph), so no --location is needed.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402


def _root(dom):
    return (dom or "").replace("https://", "").replace("http://", "").replace("www.", "").strip("/").lower()


# link-farm / PBN / auto-directory signatures to keep out of a real outreach list
JUNK_SUB = ("directory", "articles", "guestpost", "guest-post", "backlink", "seolink", "submit",
            "classified", "listing", "bookmark", "ping", "linkbuilding", "rankerdirectory", "postonseo",
            "buzzshrink", "windowssearch")
JUNK_TLD = (".website", ".im", ".xyz", ".click", ".link", ".online", ".site", ".space", ".fun", ".buzz")


def _is_quality(g):
    dom = _root(g.get("domain"))
    if not dom or "." not in dom:
        return False
    if any(j in dom for j in JUNK_SUB) or dom.endswith(JUNK_TLD):
        return False
    # Rank >= 100 (0-1000 scale) reliably separates real industry/editorial sites (pymnts 182,
    # hoteltechreport 140) from the random foreign scrapers that clear a lower bar (serv00 73, philca 91).
    return (g.get("rank") or 0) >= 100 and (g.get("spam") or 0) < 25


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--gap-limit", type=int, default=120)
    ap.add_argument("--date", default="latest")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)
    client = cfg.get("client_name") or cfg.get("name") or cfg.get("domain")
    client_dom = _root(cfg.get("domain"))
    pairs = [(client, client_dom)]
    for c in (cfg.get("competitors", []) or []):
        if isinstance(c, dict) and c.get("domain"):
            pairs.append((c.get("name") or c["domain"], _root(c["domain"])))
    domains = [dom for _, dom in pairs if dom]

    # 1. bulk profile metrics for everyone (one call each, cents total)
    ranks = d.backlinks_bulk_ranks(domains)
    refs = d.backlinks_bulk_referring_domains(domains)
    bls = d.backlinks_bulk_backlinks(domains)
    spam = d.backlinks_bulk_spam_score(domains)
    profiles = {}
    print(f"\nBacklink profiles ({args.project})")
    for name, dom in pairs:
        rk = ranks.get(dom)
        profiles[name] = {"domain": dom, "referring_domains": refs.get(dom), "backlinks": bls.get(dom),
                          "rank": rk, "rank_norm": round(rk / 10.0, 1) if isinstance(rk, (int, float)) else None,
                          "spam_score": spam.get(dom)}
        p = profiles[name]
        tag = "  <- client" if name == client else ""
        print(f"  {name:20s} refdomains={str(p['referring_domains'] or '-'):>6}  backlinks={str(p['backlinks'] or '-'):>8}"
              f"  rank={str(p['rank_norm'] or '-'):>5}  spam={str(p['spam_score'] or '-'):>3}{tag}")

    # 1b. the client's OWN top referring domains (surfaces earned press: time.com, forbes.com, etc.)
    client_refs = []
    try:
        for it in d.referring_domains(client_dom, limit=100):
            dom = _root(it.get("domain"))
            if dom and dom != client_dom:
                client_refs.append({"domain": dom, "rank": it.get("rank"),
                                    "backlinks": it.get("backlinks")})
    except Exception as e:
        print(f"  [client refs error] {str(e)[:100]}")
    client_refs.sort(key=lambda r: -(r.get("rank") or 0))

    # 2. the link GAP: domains linking to the strongest rivals but not the client.
    rivals = sorted([(n, dm) for n, dm in pairs if n != client and dm],
                    key=lambda x: -(refs.get(x[1]) or 0))
    gap, targets_used = [], []
    for topn in (3, 2):
        targets_used = [dm for _, dm in rivals[:topn]]
        if len(targets_used) < 2:
            break
        try:
            gap = d.backlinks_domain_intersection(targets_used, exclude=[client_dom], limit=args.gap_limit)
        except Exception as e:
            print(f"  [gap error] {str(e)[:100]}")
            gap = []
        gap = [g for g in gap if _root(g.get("domain")) != client_dom]
        if len(gap) >= 8:
            break
    gap.sort(key=lambda g: -(g.get("rank") or 0))
    quality = [g for g in gap if _is_quality(g)]
    leaders = ", ".join(n for n, _ in rivals[: len(targets_used)])
    print(f"\nLink gap: {len(gap)} shared referring domains ({len(quality)} legitimate) link to "
          f"[{leaders}] but not to {client}")
    for g in gap[:10]:
        q = "  QUALITY" if _is_quality(g) else ""
        print(f"    {(_root(g.get('domain')) or '?'):40s} rank {str(g.get('rank')):>4}  spam {str(g.get('spam')):>3}{q}")

    out = {"client": client, "client_domain": client_dom, "profiles": profiles,
           "client_top_refs": client_refs[:40],
           "gap_targets_from": [n for n, _ in rivals[: len(targets_used)]],
           "gap_count": len(gap), "gap_quality_count": len(quality),
           "gap_quality": quality, "gap": gap}
    pdir = cfg.project_dir
    p = pdir / "data" / "raw" / "dataforseo" / f"backlinks-{args.date}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    # handoff CSV: the legitimate outreach target list (junk/link-farm domains filtered out)
    with (pdir / "data" / "backlink-gap-targets.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["referring_domain", "authority_rank_0_1000", "spam_score", "links_to_competitors"])
        for g in quality:
            w.writerow([_root(g.get("domain")), g.get("rank"), g.get("spam"), leaders])
    print(f"\nsaved -> {p}  +  data/backlink-gap-targets.csv ({len(quality)} legitimate outreach targets)")


if __name__ == "__main__":
    main()

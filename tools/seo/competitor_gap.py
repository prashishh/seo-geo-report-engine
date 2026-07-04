"""Competitor keyword + traffic gap: the "steal list" for a pitch report (via DataForSEO Labs).

Answers the two questions a prospect actually feels: "what are competitors winning that I'm not?" and
"how big is that in traffic and dollars?" For each competitor it pulls the ranked-keyword footprint and
the traffic/traffic-value stat block, subtracts what the client already ranks for, and returns a
prioritized steal list plus the head-to-head traffic-value gap. US/Labs markets only (Nepal excluded).

    python tools/seo/competitor_gap.py --project demo --location 2840 \
        --topic ai cloud data devops modernization engineering migration analytics \
        --out projects/demo/data/raw/dataforseo/competitor-gap-2026-07-01.json

Traffic + traffic-value are DataForSEO estimates; frame them as directional to the client.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d                         # noqa: E402
from lib.config import load, load_secrets                       # noqa: E402
from seo.keyword_research import topic_terms, is_relevant, _domain_root_word  # noqa: E402


def _norm(x):
    return (x or "").lower().replace("https://", "").replace("http://", "").replace("www.", "").strip("/ ").split("/")[0]


def _domain_of(c):
    return _norm(c.get("domain") if isinstance(c, dict) else c)


def research(client, competitors, location=2840, language="en", topic=None, per_comp=150):
    load_secrets()
    client = _norm(client)
    comps = [(c.get("name") if isinstance(c, dict) else _domain_of(c), _domain_of(c)) for c in competitors]
    terms = topic_terms([], [client] + [n for n, _ in comps], topic)
    brand_roots = {_domain_root_word(client)} | {_domain_root_word(dom) for _, dom in comps}

    overviews = {}
    for dom in [client] + [dom for _, dom in comps]:
        try:
            overviews[dom] = d.domain_rank_overview(dom, location, language)
        except Exception as e:
            overviews[dom] = {"target": dom, "_err": str(e)[:100]}

    # what the client already ranks for (subtract from the steal list)
    client_kw = set()
    try:
        ck = d.ranked_keywords(client, location, language, limit=min(700, per_comp * 5))
        client_kw = {i["keyword"].lower() for i in ck["items"]}
    except Exception:
        pass

    steal = {}
    footprints = []
    for name, dom in comps:
        try:
            rk = d.ranked_keywords(dom, location, language, limit=per_comp)
        except Exception as e:
            footprints.append({"competitor": name, "domain": dom, "_err": str(e)[:100]})
            continue
        rel = 0
        for it in rk["items"]:
            kw = (it.get("keyword") or "").lower()
            if not kw or kw in client_kw or not is_relevant(kw, terms, brand_roots):
                continue
            rel += 1
            cur = steal.get(kw)
            if not cur or (it.get("volume") or 0) > (cur["volume"] or 0):
                steal[kw] = {"keyword": kw, "volume": it.get("volume"), "held_by": name,
                             "their_rank": it.get("rank")}
        footprints.append({"competitor": name, "domain": dom, "total_keywords": rk["total"],
                           "relevant_stealable": rel})

    steal_list = sorted(steal.values(), key=lambda x: -(x["volume"] or 0))
    # traffic-value gap
    def etv(dom): return (overviews.get(dom, {}) or {}).get("etv") or 0
    def tv(dom): return (overviews.get(dom, {}) or {}).get("traffic_value") or 0
    comp_etv = sum(etv(dom) for _, dom in comps)
    comp_tv = sum(tv(dom) for _, dom in comps)
    totals = {"client_etv": round(etv(client)), "client_traffic_value": round(tv(client)),
              "competitor_etv_total": round(comp_etv), "competitor_traffic_value_total": round(comp_tv),
              "steal_count": len(steal_list),
              "steal_volume": sum(s["volume"] or 0 for s in steal_list)}
    return {"client": client, "location": location, "overviews": overviews,
            "footprints": footprints, "steal_list": steal_list, "totals": totals}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--language", default="en")
    ap.add_argument("--topic", nargs="*")
    ap.add_argument("--per-comp", type=int, default=150)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load(args.project)
    res = research(cfg.get("domain"), cfg.get("competitors", []) or [], args.location, args.language,
                   args.topic, args.per_comp)
    t = res["totals"]
    print(f"\nCompetitor gap for {res['client']}  loc {args.location}")
    print(f"client traffic ~{t['client_etv']:,}/mo (value ${t['client_traffic_value']:,}); "
          f"competitors ~{t['competitor_etv_total']:,}/mo (value ${t['competitor_traffic_value_total']:,})")
    print(f"steal list: {t['steal_count']} relevant keywords rivals rank for that you don't "
          f"(~{t['steal_volume']:,} searches/mo)\n")
    for s in res["steal_list"][:15]:
        print(f"  vol {str(s['volume'] or 0):>7}  [{s['held_by']}]  {s['keyword']}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(res, indent=2))
        print(f"\nsaved -> {args.out}")


if __name__ == "__main__":
    main()

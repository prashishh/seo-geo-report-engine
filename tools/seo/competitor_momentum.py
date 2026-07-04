"""Competitor momentum: funding + hiring direction + news, for a client's peer set (via PredictLeads).

The freshest competitive-intel and a hard greenfield proof: it shows where the field's capital and
hiring are concentrated (saturated lanes) versus absent (open lanes). Reads client.yml competitors,
pulls funding rounds, open roles by department, and recent news for each, and writes a momentum summary
the first-scan report reads.

    python tools/seo/competitor_momentum.py --project <slug>

PredictLeads funding coverage can be incomplete (it may miss some rounds), so treat total_raised as a
floor and reconcile against the public record before quoting it to a client. Hiring and latest-round
dates are the reliable, freshest signals.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import predictleads as pl        # noqa: E402
from lib.config import load, load_secrets          # noqa: E402

DEPT = {"software_development": "Engineering", "engineering": "Engineering", "information_technology": "Engineering",
        "data_analysis": "Engineering", "sales": "Sales/GTM", "marketing": "Marketing",
        "product_management": "Product", "research": "Research", "support": "Support",
        "human_resources": "HR", "finance": "Finance", "operations": "Ops", "management": "Mgmt", "design": "Design"}


def _domain(c):
    d = c.get("domain") if isinstance(c, dict) else c
    return (d or "").lower().replace("https://", "").replace("www.", "").strip("/")


def _name(c, dom):
    return c.get("name") if isinstance(c, dict) and c.get("name") else dom.split(".")[0].title()


def pull(name, dom):
    fin = pl.financing_events(dom, limit=30)
    news = pl.news_events(dom, limit=100)
    jobs = pl.job_openings(dom, limit=250)
    total = sum((f.get("amount_normalized") or 0) for f in fin)
    dated = [f for f in fin if f.get("effective_date")]
    latest = max(dated, key=lambda f: f["effective_date"]) if dated else (fin[0] if fin else None)
    depts = Counter()
    for j in jobs:
        for c in (j.get("categories") or []):
            depts[DEPT.get(c, c)] += 1
    recent = sorted([n for n in news if n.get("effective_date")], key=lambda n: n["effective_date"], reverse=True)[:5]
    return {"domain": dom, "total_raised": total, "rounds": len(fin),
            "latest_round": ({"type": (latest or {}).get("financing_type_normalized"),
                              "amount": (latest or {}).get("amount_normalized"),
                              "date": (latest or {}).get("effective_date")} if latest else None),
            "open_roles": len(jobs), "top_depts": depts.most_common(6), "depts": dict(depts),
            "news_categories": Counter(n.get("category") for n in news).most_common(8),
            "recent_news": [{"date": n.get("effective_date"), "category": n.get("category"),
                             "summary": (n.get("summary") or n.get("article_sentence") or "")[:140]} for n in recent]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--date", default="")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)
    client = (_name({"name": cfg.get("client_name") or cfg.get("name")}, _domain({"domain": cfg.get("domain")})),
              _domain({"domain": cfg.get("domain")}))
    comps = [(_name(c, _domain(c)), _domain(c)) for c in (cfg.get("competitors", []) or [])]
    out, field_depts = {}, Counter()
    for nm, dom in [client] + comps:
        if not dom:
            continue
        try:
            o = pull(nm, dom)
        except Exception as e:
            o = {"domain": dom, "error": str(e)[:120]}
        out[nm] = o
        if nm != client[0]:
            for d, c in o.get("depts", {}).items():
                field_depts[d] += c

    def m(v): return f"${v/1e6:.0f}M" if v else "$0"
    print(f"\nCompetitor momentum ({args.project})")
    print(f"{'Company':18s} {'Raised(PL)':>10} {'Latest round':>24} {'Roles':>6}  Top hiring")
    for nm, o in out.items():
        lr = o.get("latest_round") or {}
        lrs = f"{lr.get('type') or '-'} {m(lr.get('amount') or 0)} {lr.get('date') or ''}"
        print(f"{nm:18s} {m(o.get('total_raised', 0)):>10} {lrs:>24} {str(o.get('open_roles', 0)):>6}  "
              f"{', '.join(f'{d}:{c}' for d, c in o.get('top_depts', [])[:4])}")
    fin_roles = field_depts.get("Finance", 0)
    total_roles = sum(field_depts.values())
    print(f"\nField hiring: {total_roles} open roles across rivals. "
          f"Engineering {field_depts.get('Engineering',0)}, Sales/GTM {field_depts.get('Sales/GTM',0)}, "
          f"Finance {fin_roles}, HR {field_depts.get('HR',0)}.")

    pdir = cfg.project_dir
    p = pdir / "data" / "raw" / "predictleads" / f"momentum-{args.date or 'latest'}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"client": client[0], "field_depts": dict(field_depts),
                             "total_field_roles": total_roles, "companies": out}, indent=2))
    print(f"\nsaved -> {p}")


if __name__ == "__main__":
    main()

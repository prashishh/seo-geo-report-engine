"""Estimated traffic + traffic-share for a client vs its peer set (via DataForSEO Labs).

The single most fee-justifying visual: turns the abstract authority gap into a market-share story
("you are ~4% of category traffic; the leader is 61%"). Estimated organic traffic (ETV) per domain in
one bulk call. Label as an estimate in client copy; it is a directional share read, not measured GA.

    python tools/seo/traffic_share.py --project <slug>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402


def _dom(x):
    return (x.get("domain") if isinstance(x, dict) else x or "").lower().replace("www.", "").strip("/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--language", default="en")
    ap.add_argument("--date", default="latest")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)
    client = _dom(cfg.get("domain"))
    names = {client: cfg.get("client_name") or cfg.get("name") or client}
    domains = [client]
    for c in (cfg.get("competitors", []) or []):
        dom = _dom(c)
        if dom:
            domains.append(dom)
            names[dom] = c.get("name") if isinstance(c, dict) else dom
    etv = d.bulk_traffic_estimation(domains, args.location, args.language)
    total = sum(v or 0 for v in etv.values()) or 1
    rows = sorted([{"company": names.get(dom, dom), "domain": dom, "etv": round(etv.get(dom) or 0),
                    "share_pct": round(100 * (etv.get(dom) or 0) / total, 1)} for dom in domains],
                  key=lambda r: -r["etv"])
    client_share = next((r["share_pct"] for r in rows if r["domain"] == client), 0)
    leader = rows[0]
    out = {"client": names[client], "client_share_pct": client_share, "leader": leader["company"],
           "leader_share_pct": leader["share_pct"], "rows": rows}
    p = cfg.project_dir / "data" / "raw" / "dataforseo" / f"traffic-{args.date}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(f"\nEstimated organic traffic share ({args.project})")
    for r in rows:
        print(f"  {r['company']:18s} etv ~{r['etv']:>9,}/mo   {r['share_pct']:>5}% of the set")
    print(f"\n{names[client]} is ~{client_share}% of the tracked category traffic; {leader['company']} "
          f"is ~{leader['share_pct']}%.\nsaved -> {p}")


if __name__ == "__main__":
    main()

"""What content wins for each competitor: their top organic pages by estimated traffic.

For the client + each rival it pulls the highest-traffic pages (URL, est. visits/mo, keyword count)
so the report can show "this is the content the field is winning with, and where you are missing a
page". Writes the {name: {domain, pages:[...]}} artifact `first_scan.py`'s competitor-winning section
reads.

    python tools/seo/top_pages.py --project <slug> --location 2036 --per 6

Cents per domain.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--per", type=int, default=6, help="top pages per domain")
    ap.add_argument("--date", default="latest")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)
    companies = [(cfg.get("client_name") or cfg.get("name") or cfg.get("domain"), cfg.get("domain"))]
    for c in (cfg.get("competitors", []) or []):
        if isinstance(c, dict) and c.get("domain"):
            companies.append((c.get("name") or c.get("domain"), c["domain"]))
    out = {}
    print(f"\nTop-traffic pages ({args.project})")
    for name, dom in companies:
        if not dom:
            continue
        try:
            pages = d.top_pages(dom, args.location, limit=args.per)
            pages = [p for p in pages if p.get("url") and p.get("etv")]
            out[name] = {"domain": dom, "pages": pages}
            top = pages[0] if pages else {}
            print(f"  {name:20s} {len(pages):2d} pages  top: {round(top.get('etv') or 0):>7,} visits  {top.get('url','')[:60]}")
        except Exception as e:
            out[name] = {"domain": dom, "error": str(e)[:100]}
            print(f"  {name:20s} error: {str(e)[:80]}")

    p = cfg.project_dir / "data" / "raw" / "dataforseo" / f"top-pages-{args.date}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(f"\nsaved -> {p}")


if __name__ == "__main__":
    main()

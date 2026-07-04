"""Google AI Overview visibility tracker (via DataForSEO SERP).

For a set of a client's money keywords, capture Google's AI Overview: does it trigger, what does it
say, which domains does it cite, and is the client cited. This is the most important AI-search surface
and complements the Perplexity probe (web-research) and Ahrefs Brand Radar in a multi-engine AI stack.

    python tools/geo/ai_visibility.py --project demo --location 2840 \
        --keywords "best broker in nepal" "how to invest in share market in nepal"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402


def scan(keywords, client_domain, location=2840, language="en"):
    load_secrets()
    cd = (client_domain or "").lower().replace("www.", "")
    rows = []
    for kw in keywords:
        ov = d.ai_overview(kw, location=location, language=language)
        domains = [x.lower().replace("www.", "") for x in ov.get("cited_domains", [])]
        cited = ov["triggered"] and cd in domains
        rows.append({
            "keyword": kw,
            "aio_triggered": ov["triggered"],
            "client_cited": cited,
            "cited_domains": ov.get("cited_domains", []),
            "text": ov.get("text", "")[:500],
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--language", default="en")
    ap.add_argument("--domain")
    ap.add_argument("--keywords", nargs="*")
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load(args.project)
    domain = args.domain or cfg.get("domain")
    keywords = args.keywords or cfg.get("target_keywords", [])[:10]
    rows = scan(keywords, domain, args.location, args.language)

    triggered = sum(1 for r in rows if r["aio_triggered"])
    cited = sum(1 for r in rows if r["client_cited"])
    print(f"\nGoogle AI Overview scan for {domain}  ({len(rows)} keywords, loc {args.location})")
    print(f"AI Overview triggered on {triggered}/{len(rows)} queries; {domain} cited in {cited}.\n")
    for r in rows:
        flag = "CITED" if r["client_cited"] else ("no" if r["aio_triggered"] else "no AIO")
        print(f"  [{flag:>6}] {r['keyword']}")
        if r["aio_triggered"]:
            print(f"           cites: {', '.join(r['cited_domains'][:6])}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps({"domain": domain, "location": args.location, "rows": rows}, indent=2))
        print(f"\nsaved -> {args.out}")


if __name__ == "__main__":
    main()

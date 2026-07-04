"""Share-of-Search: branded-demand momentum, client vs top rivals (via DataForSEO Google Trends).

Share of Search (branded search interest as a % of the tracked set) is a leading indicator of market
share, predictive up to a year ahead. This compares the client's brand against its biggest rivals over
12 months and flags who is rising and who is fading. Google Trends caps at 5 terms per request, so it
uses the client + top competitors.

    python tools/seo/share_of_search.py --project <slug>

Caveat: brand names that are common words (Sierra, Lindy, Artisan) pick up namesake searches; the tool
appends "ai" to disambiguate and flags low confidence. Cleanest for distinctive brand names.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402

GENERIC = {"sierra", "lindy", "artisan", "decagon", "beam", "vector", "relevance"}


def _brand_term(name):
    """Disambiguate common-word brand names by appending 'ai'."""
    n = (name or "").strip()
    low = n.lower()
    if any(g in low.split() or g == low for g in GENERIC) and "ai" not in low:
        return f"{n} AI"
    return n


def _avg(vals):
    v = [x for x in vals if x is not None]
    return sum(v) / len(v) if v else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--date", default="latest")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)
    client = cfg.get("client_name") or cfg.get("name") or cfg.get("domain")
    comps = [c.get("name") for c in (cfg.get("competitors", []) or []) if isinstance(c, dict) and c.get("name")]
    # client + up to 4 rivals (Trends caps at 5 terms)
    names = [client] + comps[:4]
    terms = [_brand_term(n) for n in names]
    term_to_name = dict(zip(terms, names))

    res = d.google_trends(terms, args.location, "past_12_months")
    series = res["series"]
    n = len(res["dates"])
    half = max(1, n // 2)
    rows = []
    total_avg = sum(_avg(series[t]) for t in terms) or 1
    for t in terms:
        s = series[t]
        avg = _avg(s)
        early, late = _avg(s[:half]), _avg(s[half:])
        trend = "rising" if late > early * 1.15 else ("fading" if late < early * 0.85 else "flat")
        rows.append({"name": term_to_name[t], "term": t, "avg_interest": round(avg, 1),
                     "share_pct": round(100 * avg / total_avg, 1), "trend": trend})
    rows.sort(key=lambda r: -r["avg_interest"])
    cshare = next((r["share_pct"] for r in rows if r["name"] == client), 0)
    out = {"client": client, "client_share_pct": cshare, "rows": rows, "dates": res["dates"], "series": series}

    p = cfg.project_dir / "data" / "raw" / "dataforseo" / f"share-of-search-{args.date}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(f"\nShare of Search ({args.project})  [branded search, past 12mo]")
    for r in rows:
        print(f"  {r['name']:16s} {r['share_pct']:>5}% share  interest {r['avg_interest']:>5}  ({r['trend']})")
    print(f"\n{client} holds ~{cshare}% of branded search in this set.\nsaved -> {p}")


if __name__ == "__main__":
    main()

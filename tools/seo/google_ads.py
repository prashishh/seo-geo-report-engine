"""Competitor Google ad activity (via DataForSEO Google Ads Transparency).

Shows how many live ads each competitor runs, so the report can say "the field is buying attention and
you are not". Matching is conservative: it only counts a verified advertiser whose name normalizes to the
brand, so namesakes (e.g. a "Sierra Air Conditioning" for sierra.ai) are excluded rather than misattributed.

    python tools/seo/google_ads.py --project <slug>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402

# obvious non-tech namesakes to reject even if the token matches
NAMESAKE = ("air conditioning", "plumbing", "realty", "dental", "roofing", "hvac", "restaurant",
            "insurance", "law firm", "clinic", "auto", "landscap")


def _norm(title):
    t = (title or "").lower()
    t = re.sub(r"[.,]", "", t)
    for suf in (" incorporated", " inc", " llc", " ltd", " ai", " technologies", " labs", " platform"):
        if t.endswith(suf):
            t = t[: -len(suf)]
    return t.strip()


def match_advertiser(brand, ads):
    b = _norm(brand)
    best, conf = None, "not found"
    for a in ads:
        title = a.get("title") or ""
        if not a.get("verified") or any(n in title.lower() for n in NAMESAKE):
            continue
        nt = _norm(title)
        # exact, or the advertiser name starts with the brand (e.g. "Acme Gifts International Pty Ltd"),
        # or the brand starts with a shorter advertiser name. Requires >=4 chars to avoid loose matches.
        match = nt == b or nt == b.replace(" ", "") or (len(b) >= 4 and (nt.startswith(b + " ") or b.startswith(nt + " ")))
        if match and (not best or (a.get("ads_count") or 0) > (best.get("ads_count") or 0)):
            best, conf = a, "high"
    return best, conf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--date", default="latest")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)
    companies = [(cfg.get("client_name") or cfg.get("name") or cfg.get("domain"), cfg.get("domain"))]
    for c in (cfg.get("competitors", []) or []):
        if isinstance(c, dict) and c.get("name"):
            companies.append((c["name"], c.get("domain")))
    out = {}
    for name, dom in companies:
        try:
            ads = d.ads_advertisers(name, args.location)
            best, conf = match_advertiser(name, ads)
            aid = (best or {}).get("advertiser_id") if best else None
            out[name] = {"domain": dom, "ads_count": (best or {}).get("ads_count") if best else 0,
                         "match_title": (best or {}).get("title") if best else None,
                         "advertiser_id": aid, "confidence": conf, "advertisers_seen": len(ads),
                         "transparency_url": (f"https://adstransparency.google.com/advertiser/{aid}?region=US" if aid else None)}
        except Exception as e:
            out[name] = {"domain": dom, "error": str(e)[:100]}
        o = out[name]
        print(f"  {name:16s} ads={o.get('ads_count')}  conf={o.get('confidence')}  match='{o.get('match_title')}'")

    p = cfg.project_dir / "data" / "raw" / "dataforseo" / f"google-ads-{args.date}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(f"\nsaved -> {p}  (report uses high-confidence matches only)")


if __name__ == "__main__":
    main()

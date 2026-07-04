"""Reputation + voice-of-customer scorecard for a client's peer set (via the Perplexity probe).

The trust axis + the switching wedge: for each company it reads G2 / Capterra / Trustpilot / Reddit and
returns the rating, review volume, and the mined top praise and complaint THEMES, with sources. It
degrades honestly when reviews are scarce (nulls + a note) rather than inventing numbers. B2B review
coverage lives on G2/Capterra, which structured review APIs do not cover, so a cited web read is the
robust owned path for early-stage software companies.

    python tools/seo/reputation.py --project <slug>

Cents per company. Themes come from real review language; label ratings as sourced estimates in copy.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import openrouter as orr        # noqa: E402
from connectors import dataforseo as dfs         # noqa: E402
from lib.config import load, load_secrets        # noqa: E402

PROMPT = (
    "For the company {name} ({domain}), summarize its customer REPUTATION as of 2026 using whichever "
    "review sources apply to this kind of business: Google reviews, ProductReview.com.au, Trustpilot, "
    "G2, Capterra, and Reddit. Return ONLY a JSON object, no prose, no code fence:\n"
    '{{"rating": <number 1-5 or null>, "rating_source": "Google"|"ProductReview"|"Trustpilot"|"G2"|"Capterra"|"mixed"|null, '
    '"review_count": <integer or null>, "top_praise": [up to 3 short phrases], '
    '"top_complaints": [up to 3 short phrases], "note": "one short line"}}\n'
    "Base praise/complaints on ACTUAL review language. If public reviews are scarce, use null for "
    "rating/review_count and say so in note. Do not invent numbers. Ignore unrelated companies with "
    "similar names."
)


# scam-checker / namesake contamination: phrases that flag a DIFFERENT (usually European scam) entity,
# not a real complaint about a business that carries a legitimate Google rating.
SCAM_FLAGS = ("suspicious", "scam", "fraud", "douteux", "phishing", "stolen", "not legit", "illegit",
              "fake site", "phone number", "payment by transfer", "wire transfer", "avoid this site",
              # geographic namesake markers: a real complaint about an AU business won't cite these
              "germany", "belgium", "france", "netherlands", "pays ", "euro", "€")
_NULLISH = {"", "null", "none", "n/a", "na", "-", "nil", "unknown", "no complaints", "none found"}


def _clean_themes(items, rating, source):
    """Drop nullish/hallucinated entries and scam-checker noise that belongs to a namesake, not to a
    business that holds a real rating. Returns a clean list of theme strings."""
    out = []
    for x in items or []:
        s = str(x).strip()
        if s.lower() in _NULLISH:
            continue
        legit = source == "Google" and isinstance(rating, (int, float)) and rating >= 4.0
        if legit and any(k in s.lower() for k in SCAM_FLAGS):
            continue
        out.append(s)
    return out


def _title_match(brand, title):
    generic = {"the", "pty", "ltd", "inc", "co", "group", "australia", "au", "promotional", "products", "gifts"}
    bt = {t for t in re.sub(r"[^a-z0-9 ]", "", (brand or "").lower()).split() if t not in generic and len(t) > 2}
    tt = set(re.sub(r"[^a-z0-9 ]", "", (title or "").lower()).split())
    return bool(bt & tt)


def _parse(text):
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--location", type=int, default=2840, help="for the Google Business rating lookup")
    ap.add_argument("--date", default="latest")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)
    companies = [(cfg.get("client_name") or cfg.get("name") or cfg.get("domain"), cfg.get("domain"))]
    for c in (cfg.get("competitors", []) or []):
        if isinstance(c, dict):
            companies.append((c.get("name") or c.get("domain"), c.get("domain")))
    out = {}
    print(f"\nReputation + voice-of-customer ({args.project})")
    for name, dom in companies:
        data = {}
        # 1. hard Google Business rating (best-effort; verify the returned title matches the brand)
        try:
            g = dfs.my_business_info(name, args.location)
            if g.get("rating") and _title_match(name, g.get("title") or ""):
                data.update({"rating": g.get("rating"), "rating_source": "Google",
                             "review_count": g.get("reviews"), "google_title": g.get("title")})
        except Exception:
            pass
        # 2. Perplexity for themes (+ a rating fallback from any review source)
        try:
            resp = orr.probe(PROMPT.format(name=name, domain=dom))
            p = _parse(resp.get("answer") or resp.get("text") or resp.get("content") or "")
            if data.get("rating") is None:
                data["rating"] = p.get("rating")
                data["rating_source"] = p.get("rating_source")
                data["review_count"] = p.get("review_count")
            data["top_praise"] = _clean_themes(p.get("top_praise"), data.get("rating"), data.get("rating_source"))
            data["top_complaints"] = _clean_themes(p.get("top_complaints"), data.get("rating"), data.get("rating_source"))
            data["note"] = p.get("note")
            data["sources"] = [s.get("url") for s in (resp.get("sources") or [])][:5]
        except Exception as e:
            data.setdefault("error", str(e)[:90])
        # Trust tier: only the verified Google Business count is reliable. Perplexity-sourced counts swing
        # wildly run to run (514 vs 5000 vs 50000), so suppress non-Google counts rather than show a guess.
        if data.get("rating_source") != "Google":
            data["review_count"] = None
        out[name] = data
        r = data.get("rating")
        comp = (data.get("top_complaints") or ["-"])[0]
        print(f"  {name:16s} {(str(r)+' ('+str(data.get('rating_source'))+')') if r else 'no rating':>18}  "
              f"({data.get('review_count') or '?'} reviews)  top gripe: {comp}")

    pdir = cfg.project_dir
    (pdir / "data" / "raw" / "openrouter").mkdir(parents=True, exist_ok=True)
    (pdir / "data" / "raw" / "openrouter" / f"reputation-{args.date}.json").write_text(json.dumps(out, indent=2))
    with (pdir / "data" / "reputation.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["company", "rating", "source", "reviews", "top_praise", "top_complaint"])
        for name, d in out.items():
            w.writerow([name, d.get("rating"), d.get("rating_source"), d.get("review_count"),
                        "; ".join(d.get("top_praise") or []), "; ".join(d.get("top_complaints") or [])])
    print(f"\nsaved -> data/raw/openrouter/reputation-{args.date}.json + data/reputation.csv")


if __name__ == "__main__":
    main()

"""Opportunity scoring: turn a keyword pool into a scored greenfield map (via DataForSEO KD).

Scores every candidate keyword (the client's targets + the competitor steal list) on Demand x
Winnability x Fit, labels each Greenfield / Contested / Fortress / Trap, and emits both a bubble-matrix
chart spec (Demand vs Winnability, top-right = greenfield) and a ranked shortlist. This is the
prescription half of the pitch: not just "here is the gap" but "here is exactly where to attack first".

    python tools/seo/opportunity_score.py --project demo --location 2840 \
        --fit ai cloud data devops modernization migration --out projects/demo/data/opportunity-scored.json

Reads the competitor-gap + keyword-research artifacts the project already has. KD is DataForSEO Labs
(US/UK/India... not Nepal). Keep the scoring formula internal; show the client the map, not the math.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402

# thresholds for quadrant labels (0-100 demand/win)
D_HI, W_HI = 45, 55

# non-buyer noise that leaks in from competitors' careers/glossary/blog footprint. A pitch shortlist
# must be COMMERCIAL buyer demand, not job-seeker / student / definition queries.
JUNK = ("job", "jobs", "vacanc", "salary", "salaries", "career", "resume", " cv", "interview",
        "course", "certification", "certificate", "tutorial", "syllabus", "student", "what is",
        "which ", "how to become", "meaning", "definition", "examples", "example of", " free",
        "login", "download", " pdf", "wiki", "vs ", "reddit", "quora")
BUY_SIGNALS = {"services", "service", "consulting", "consultant", "company", "companies", "solutions",
               "solution", "partner", "agency", "development", "outsourcing", "firm", "provider",
               "vendor", "platform", "software", "tool", "for", "enterprise", "modernization",
               "migration", "integration", "implementation"}


def is_buyer(kw, intent):
    k = " " + (kw or "").lower() + " "
    if any(j in k for j in JUNK):
        return False
    if intent in ("commercial", "transactional"):
        return True
    if intent in ("informational", "navigational"):
        return False
    return bool(set(kw.lower().split()) & BUY_SIGNALS)   # unknown intent: keep only if commercial signal


def _latest(pdir, pattern):
    fs = sorted(Path(pdir).glob(pattern))
    return fs[-1] if fs else None


def _tokens(s):
    return set("".join(c if c.isalnum() or c.isspace() else " " for c in (s or "").lower()).split())


def tier(demand, win):
    if demand >= D_HI and win >= W_HI:
        return "greenfield"
    if demand >= D_HI and win < W_HI:
        return "fortress"
    if demand < D_HI and win >= W_HI:
        return "contested"     # winnable niche
    return "trap"


def score_pool(candidates, location, language, fit_terms, chart_max_vol=40000):
    """candidates: {keyword: {volume, held_by?, kd?}}. Fills missing KD, scores, labels."""
    load_secrets()
    keys = list(candidates)
    need_kd = [k for k, v in candidates.items() if v.get("kd") is None]
    for i in range(0, len(need_kd), 700):
        try:
            got = d.keyword_difficulty(need_kd[i:i + 700], location, language)
            for k, kd in got.items():
                if k.lower() in candidates:
                    candidates[k.lower()]["kd"] = kd
        except Exception:
            break
    # intent, to keep the shortlist to COMMERCIAL buyer demand
    for i in range(0, len(keys), 700):
        try:
            it = d.search_intent(keys[i:i + 700], language)
            for k, lab in it.items():
                if k.lower() in candidates:
                    candidates[k.lower()]["intent"] = lab
        except Exception:
            break
    vols = [v.get("volume") or 0 for v in candidates.values()]
    vmax = max(vols + [1])
    scored = []
    for kw, v in candidates.items():
        vol = v.get("volume") or 0
        kd = v.get("kd")
        demand = round(100 * math.log(vol + 1) / math.log(vmax + 1), 1)
        win = round(100 - kd, 1) if isinstance(kd, (int, float)) else 55.0
        fit = 90 if (_tokens(kw) & set(fit_terms)) else 60
        opp = round(demand * 0.40 + win * 0.35 + fit * 0.25, 1)
        scored.append({"keyword": kw, "volume": vol, "kd": kd, "held_by": v.get("held_by"),
                       "intent": v.get("intent"), "buyer": is_buyer(kw, v.get("intent")),
                       "demand": demand, "winnability": win, "fit": fit, "opportunity": opp,
                       "tier": tier(demand, win)})
    scored.sort(key=lambda x: -x["opportunity"])
    buyer = [s for s in scored if s["buyer"]]
    # chart points: readable winnable BUYER set (cap head-term clutter) + a couple fortress for contrast
    winnable = [s for s in buyer if (s["volume"] or 0) <= chart_max_vol]
    fortress = [s for s in buyer if s["tier"] == "fortress"][:2]
    picks, seen = [], set()
    for s in (winnable[:16] + fortress):
        if s["keyword"] not in seen:
            seen.add(s["keyword"]); picks.append(s)
    points = [{"label": (s["keyword"][:24]), "x": s["winnability"], "y": s["demand"],
               "size": s["volume"] or 1, "tier": s["tier"]} for s in picks]
    greenfield = [s for s in buyer if s["tier"] in ("greenfield", "contested")][:12]
    return {"scored": scored, "points": points, "greenfield": greenfield,
            "buyer_count": len(buyer),
            "counts": {t: sum(1 for s in buyer if s["tier"] == t)
                       for t in ("greenfield", "contested", "fortress", "trap")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--language", default="en")
    ap.add_argument("--fit", nargs="*", default=[])
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load(args.project)
    pdir = cfg.project_dir
    candidates = {}
    # competitor steal list
    gap_f = _latest(pdir, "data/raw/**/competitor-gap-*.json")
    if gap_f:
        for s in json.loads(gap_f.read_text()).get("steal_list", []):
            candidates[s["keyword"].lower()] = {"volume": s.get("volume"), "held_by": s.get("held_by")}
    # client's own target keywords (kw research)
    kw_f = _latest(pdir, "data/raw/**/kw-*.json") or _latest(pdir, "data/raw/**/kw-small-*.json")
    if kw_f:
        for t in json.loads(kw_f.read_text()).get("targets", []):
            k = (t.get("keyword") or "").lower()
            if k:
                candidates.setdefault(k, {"volume": t.get("volume"), "kd": t.get("kd")})
    if not candidates:
        print("no candidates found (run competitor_gap.py / keyword_research.py first)"); return

    res = score_pool(candidates, args.location, args.language, [f.lower() for f in args.fit])
    c = res["counts"]
    print(f"\nOpportunity scoring for {cfg.get('domain')}: {len(res['scored'])} candidates")
    print(f"  greenfield {c['greenfield']} | contested(winnable niche) {c['contested']} | "
          f"fortress {c['fortress']} | trap {c['trap']}\n")
    print("Top winnable opportunities (greenfield + contested):")
    for s in res["greenfield"][:12]:
        kd = f"KD{s['kd']}" if s["kd"] is not None else "KD-"
        print(f"  opp {s['opportunity']:>5}  vol {str(s['volume'] or 0):>7}  {kd:>5}  "
              f"[{s['tier']}]  {s['keyword']}")

    out = Path(args.out) if args.out else (pdir / "data" / "opportunity-scored.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()

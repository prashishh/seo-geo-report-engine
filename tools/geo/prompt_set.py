"""Volume-weighted prompt-set generator for the Brand-Radar-equivalent (via DataForSEO).

A defensible AI Share-of-Voice needs a REPRESENTATIVE prompt set, not 6 cherry-picked questions. This
expands a client's seeds/topics into a broad set of real-demand queries, each weighted by its search
volume, so downstream SoV is "share within your tracked demand," not a vibe. This is the single biggest
credibility fix in turning llm-visibility into a real Brand Radar.

    python tools/geo/prompt_set.py --project demo --location 2840 \
        --seeds "invest nepal share market" "best broker nepal" --limit 120 \
        --out projects/demo/data/prompt-set.json

Labs markets (US/India/UK...) get keyword_ideas expansion; Labs-unsupported markets (Nepal) fall back to
the client's target_keywords + Google Ads volume. Topic-filter with --topic to keep it on-subject.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402

GENERIC = {"the", "a", "an", "to", "of", "for", "in", "on", "and", "or", "how", "does", "is", "best",
           "top", "app", "software", "tool", "vs", "review", "price", "near", "me"}


def _tokens(s):
    return [t for t in "".join(c if c.isalnum() or c.isspace() else " " for c in (s or "").lower()).split()]


def _topic_terms(seeds, targets, explicit):
    if explicit:
        return {t.lower() for t in explicit}
    terms = set()
    for s in list(seeds) + list(targets):
        for tok in _tokens(s):
            if len(tok) >= 3 and tok not in GENERIC:
                terms.add(tok)
    return terms


def build(seeds, targets, location, language, limit, topic):
    load_secrets()
    terms = _topic_terms(seeds, targets, topic)
    relevant = lambda kw: bool(set(_tokens(kw)) & terms) if terms else True
    pool = {}  # keyword -> volume

    # Labs expansion where available
    labs = True
    try:
        for seed in (seeds or targets[:5]):
            for r in d.keyword_ideas(seed, location, language, limit=limit):
                kw, vol = (r.get("keyword") or "").lower(), r.get("volume")
                if kw and relevant(kw):
                    pool[kw] = max(pool.get(kw, 0), vol or 0)
    except Exception:
        labs = False

    # always fold in the explicit target keywords with real Google Ads volume
    try:
        for r in d.keyword_volume(targets or list(pool)[:20], location, language):
            kw, vol = (r.get("keyword") or "").lower(), r.get("volume")
            if kw:
                pool[kw] = max(pool.get(kw, 0), vol or 0)
    except Exception:
        for kw in targets:
            pool.setdefault(kw.lower(), 0)

    ranked = sorted(pool.items(), key=lambda kv: -(kv[1] or 0))[:limit]
    prompts = [{"prompt": kw, "volume": vol} for kw, vol in ranked]
    return {"location": location, "language": language, "labs": labs,
            "topic_terms": sorted(terms), "count": len(prompts),
            "total_volume": sum(p["volume"] for p in prompts), "prompts": prompts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--language", default="en")
    ap.add_argument("--seeds", nargs="*", default=[])
    ap.add_argument("--targets", nargs="*")
    ap.add_argument("--topic", nargs="*")
    ap.add_argument("--limit", type=int, default=120)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load(args.project) if args.project else None
    targets = args.targets or (cfg.get("target_keywords", []) if cfg else [])
    res = build(args.seeds, targets, args.location, args.language, args.limit, args.topic)

    print(f"\nPrompt set ({args.project or 'ad-hoc'}): {res['count']} prompts, "
          f"total weighted volume {res['total_volume']:,}  (labs={res['labs']})")
    for p in res["prompts"][:15]:
        print(f"  {str(p['volume'] or 0):>8}  {p['prompt']}")
    if res["count"] > 15:
        print(f"  ... +{res['count']-15} more")

    out = args.out
    if not out and cfg and cfg.project_dir:
        out = cfg.project_dir / "data" / "prompt-set.json"
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(res, indent=2))
        print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()

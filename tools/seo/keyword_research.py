"""Keyword research + opportunity scoring (via DataForSEO).

Now that DataForSEO Labs is unlocked, this pulls the full keyword picture for a project in one run and
scores every keyword by opportunity (volume x winnability x intent). It auto-detects whether the market
is Labs-supported: for the ~94 Labs locations (US, India, UK, ...) it uses keyword_overview (volume +
KD + intent), keyword_ideas (expansion), ranked_keywords (competitor footprints), and a true content
gap (keywords a competitor ranks for that the client does not). For Labs-unsupported markets (Nepal),
it falls back to Google Ads volume + live-SERP competitors, and marks KD as unavailable.

    python tools/seo/keyword_research.py --project demo --location 2840 \
        --seeds "specialty coffee" "coffee subscription" --out projects/demo/data/raw/dataforseo/kw-2026-07-01.json

Difficulty/volume are DataForSEO reads; cross-check the headline numbers against Ahrefs before quoting
them to a client. Keep the scoring formula internal (recipe stays behind the curtain).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402

INTENT_MULT = {"commercial": 1.2, "transactional": 1.3, "informational": 1.0,
               "navigational": 0.6, None: 1.0}

# Generic tokens that must NOT, on their own, qualify a keyword as topically relevant. Labs expansion
# and competitor ranked-keywords are noisy (brand-navigational + tangential high-volume terms leak in);
# we require at least one SPECIFIC topic token and drop obvious junk.
GENERIC = {"the", "a", "an", "to", "of", "for", "in", "on", "and", "or", "how", "does", "do", "is",
           "best", "top", "app", "apps", "software", "platform", "tool", "tools", "system", "service",
           "company", "llc", "inc", "login", "sign", "near", "me", "vs", "review", "reviews", "price",
           "pricing", "cost", "free", "hotel", "hotels", "resort", "resorts", "room", "rooms"}
JUNK = ("login", "sign in", "log in", ".com", "customer service", "phone number", "careers", "stock")


def _tokens(s):
    return [t for t in "".join(c if c.isalnum() or c.isspace() else " " for c in (s or "").lower()).split()]


def _domain(c):
    return c.get("domain") if isinstance(c, dict) else c


def _domain_root_word(domain):
    host = (domain or "").lower().replace("www.", "").split("/")[0]
    return host.split(".")[0] if host else ""


def topic_terms(seeds, targets, explicit=None):
    """The specific tokens a keyword must contain to count as on-topic (drops brand/tangential noise)."""
    if explicit:
        return {t.lower() for t in explicit}
    terms = set()
    for s in list(seeds) + list(targets):
        for tok in _tokens(s):
            if len(tok) >= 3 and tok not in GENERIC:
                terms.add(tok)
    return terms


def is_relevant(keyword, terms, brand_roots):
    kw = (keyword or "").lower()
    if not kw or any(j in kw for j in JUNK):
        return False
    toks = set(_tokens(kw))
    if toks & brand_roots:                      # drop competitor/brand navigational terms
        return False
    return bool(toks & terms)                   # must share a specific topic token


def opportunity(volume, kd, intent):
    """Internal priority score: reward volume + commercial/transactional intent, punish difficulty."""
    v = volume or 0
    win = (100 - kd) / 100 if isinstance(kd, (int, float)) else 0.5   # unknown KD -> neutral
    return round(v * win * INTENT_MULT.get(intent, 1.0))


def labs_supported(sample_kw, location, language):
    """Probe once: is this location served by DataForSEO Labs?"""
    try:
        d.keyword_overview([sample_kw], location=location, language=language)
        return True
    except Exception:
        return False


def research(targets, seeds, competitors, client_domain, location=2840, language="en",
             ideas_limit=150, comp_limit=150, topic=None):
    load_secrets()
    labs = labs_supported(targets[0] if targets else (seeds[0] if seeds else "seo"), location, language)
    terms = topic_terms(seeds, targets, topic)
    brand_roots = {_domain_root_word(client_domain)} | {
        _domain_root_word(_domain(c)) for c in competitors} | {
        (c.get("name", "").lower().split()[0] if isinstance(c, dict) and c.get("name") else "")
        for c in competitors}
    brand_roots.discard("")
    out = {"labs": labs, "location": location, "language": language, "topic_terms": sorted(terms),
           "targets": [], "ideas": [], "competitor_footprints": [], "content_gap": []}

    # --- target keywords (always show every requested target, even if Labs has no data) ---
    if labs:
        got = {r["keyword"].lower(): r for r in d.keyword_overview(targets, location, language)}
        for kw in targets:
            r = got.get(kw.lower(), {"keyword": kw, "volume": None, "kd": None, "intent": None})
            r["score"] = opportunity(r.get("volume"), r.get("kd"), r.get("intent"))
            out["targets"].append(r)
    else:
        intent = {}
        try:
            intent = d.search_intent(targets, language)
        except Exception:
            pass
        for r in d.keyword_volume(targets, location, language):
            r["kd"] = None
            r["intent"] = intent.get(r["keyword"])
            r["score"] = opportunity(r.get("volume"), None, r.get("intent"))
            out["targets"].append(r)
    out["targets"].sort(key=lambda x: -(x.get("score") or 0))

    # --- expansion ideas (Labs only) ---
    known = {t["keyword"].lower() for t in out["targets"]}
    if labs and seeds:
        seen = set()
        for seed in seeds:
            try:
                for r in d.keyword_ideas(seed, location, language, limit=ideas_limit):
                    kw = (r.get("keyword") or "").lower()
                    if kw and kw not in known and kw not in seen and is_relevant(kw, terms, brand_roots):
                        seen.add(kw)
                        r["score"] = opportunity(r.get("volume"), r.get("kd"), None)
                        out["ideas"].append(r)
            except Exception as e:
                out.setdefault("errors", []).append(f"ideas[{seed}]: {str(e)[:120]}")
        out["ideas"].sort(key=lambda x: -(x.get("score") or 0))

    # --- competitor footprints + true content gap ---
    client_kw = set()
    if labs and client_domain:
        try:
            ck = d.ranked_keywords(client_domain, location, language, limit=comp_limit * 5)
            client_kw = {i["keyword"].lower() for i in ck["items"]}
        except Exception:
            pass
    for c in competitors:
        dom = _domain(c)
        if not dom:
            continue
        name = c.get("name") if isinstance(c, dict) else dom
        try:
            if labs:
                rk = d.ranked_keywords(dom, location, language, limit=comp_limit)
                top = rk["items"]
                out["competitor_footprints"].append({"competitor": name, "domain": dom,
                                                      "total_keywords": rk["total"], "top": top[:15]})
                for i in top:                                  # gap = they rank, client does not
                    kw = i["keyword"].lower()
                    if (kw not in client_kw and kw not in known
                            and is_relevant(kw, terms, brand_roots)):
                        out["content_gap"].append({"keyword": i["keyword"], "volume": i.get("volume"),
                                                   "held_by": name, "their_rank": i.get("rank")})
            else:                                              # SERP-derived (any location)
                pass
        except Exception as e:
            out.setdefault("errors", []).append(f"footprint[{dom}]: {str(e)[:120]}")

    # Non-Labs competitor read: who holds the top spots for each target term (live SERP)
    if not labs:
        for kw in targets[:8]:
            try:
                sc = d.serp_competitors(kw, location, language, depth=5)
                out["competitor_footprints"].append({"keyword": kw,
                                                      "top": [{"rank": s["rank"], "domain": s["domain"]} for s in sc]})
            except Exception as e:
                out.setdefault("errors", []).append(f"serp[{kw}]: {str(e)[:120]}")

    # dedupe + sort gap by volume
    seen_gap = {}
    for g in out["content_gap"]:
        k = g["keyword"].lower()
        if k not in seen_gap or (g.get("volume") or 0) > (seen_gap[k].get("volume") or 0):
            seen_gap[k] = g
    out["content_gap"] = sorted(seen_gap.values(), key=lambda x: -(x.get("volume") or 0))
    return out


def write_csv(path, out):
    with Path(path).open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bucket", "keyword", "volume", "kd", "intent", "score", "note"])
        for t in out["targets"]:
            w.writerow(["target", t.get("keyword"), t.get("volume"), t.get("kd"), t.get("intent"),
                        t.get("score"), ""])
        for i in out["ideas"][:60]:
            w.writerow(["idea", i.get("keyword"), i.get("volume"), i.get("kd"), "", i.get("score"), ""])
        for g in out["content_gap"][:60]:
            w.writerow(["gap", g.get("keyword"), g.get("volume"), "", "", "", f"held by {g.get('held_by')}"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--language", default="en")
    ap.add_argument("--domain")
    ap.add_argument("--targets", nargs="*")
    ap.add_argument("--seeds", nargs="*", default=[])
    ap.add_argument("--topic", nargs="*", help="specific tokens a keyword must contain to be on-topic")
    ap.add_argument("--out")
    ap.add_argument("--csv")
    args = ap.parse_args()

    cfg = load(args.project) if args.project else None
    domain = args.domain or (cfg.get("domain") if cfg else None)
    targets = args.targets or (cfg.get("target_keywords", []) if cfg else [])
    competitors = (cfg.get("competitors", []) if cfg else []) or []

    out = research(targets, args.seeds, competitors, domain, args.location, args.language, topic=args.topic)

    mode = "Labs (KD available)" if out["labs"] else "no-Labs fallback (KD unavailable for this market)"
    print(f"\nKeyword research for {domain}  loc {args.location}  [{mode}]")
    print(f"\nTop target keywords by opportunity score:")
    for t in out["targets"][:12]:
        kd = t.get("kd"); kd = f"KD{kd}" if kd is not None else "KD-"
        print(f"  {(t.get('score') or 0):>8}  vol {str(t.get('volume') or 0):>7}  {kd:>5}  {t.get('intent') or '':<13} {t.get('keyword')}")
    if out["ideas"]:
        print(f"\nTop expansion ideas ({len(out['ideas'])} found, new vs targets):")
        for i in out["ideas"][:10]:
            kd = i.get("kd"); kd = f"KD{kd}" if kd is not None else "KD-"
            print(f"  {(i.get('score') or 0):>8}  vol {str(i.get('volume') or 0):>7}  {kd:>5}  {i.get('keyword')}")
    if out["content_gap"]:
        print(f"\nContent gap ({len(out['content_gap'])} keywords rivals rank for, client does not):")
        for g in out["content_gap"][:12]:
            print(f"  vol {str(g.get('volume') or 0):>7}  [{g.get('held_by')}]  {g.get('keyword')}")
    if out.get("errors"):
        print(f"\nnotes: {len(out['errors'])} soft errors; first: {out['errors'][0]}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(out, indent=2))
        print(f"\nsaved -> {args.out}")
    csv_path = args.csv
    if not csv_path and cfg and cfg.project_dir:
        csv_path = cfg.project_dir / "data" / "keywords-scored.csv"
    if csv_path:
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        write_csv(csv_path, out)
        print(f"csv   -> {csv_path}")


if __name__ == "__main__":
    main()

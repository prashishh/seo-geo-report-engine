"""Multi-engine AI-visibility tracker (via DataForSEO).

For a client's money-query grid, ask every major answer engine the same questions and report, per
query and per engine: is the brand MENTIONED (named in the answer), is it CITED (its domain in the
sources), who is cited/named instead, and the cross-engine score "cited or mentioned in N of M engines".

Engines (all through the one DataForSEO account):
  * google_aio  - Google AI Overview (SERP surface; citation-based)      d.ai_overview()
  * perplexity  - Perplexity sonar (always cites its sources)            d.llm_query()
  * chatgpt     - OpenAI GPT (names brands from knowledge; add search)   d.llm_query()
  * gemini      - Google Gemini                                          d.llm_query()
  * claude      - Anthropic Claude                                       d.llm_query()

This is the operational core of GEO measurement: it unifies what geo-audit (Brand Radar, aggregate),
serp-intel (Google AIO), and web-research (Perplexity probe) each saw separately into one scan, so a
project can track "cited in >=3 of 5 engines" as the durable-visibility bar over time.

    python tools/geo/llm_visibility.py --project demo --location 2840 \
        --brand "Acme Roastworks" acme-roastworks --engines google_aio perplexity chatgpt gemini claude \
        --out projects/demo/data/raw/dataforseo/llm-visibility-2026-07-01.json

Cost per query is roughly: google_aio ~$0.002, perplexity ~$0.005, chatgpt/gemini/claude ~$0.0002
each (no web search) up to ~$0.03 (search-capable reasoning model). A 6-query x 5-engine scan is a
few cents. AI answers are volatile: treat any single scan as sampled and re-run on a cadence.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from lib.config import load, load_secrets        # noqa: E402

# Default engine set. web_search on where the engine cites sources cheaply (perplexity/gemini);
# off for chatgpt/claude (knowledge-mention only, near-free) unless --web-search-all is passed.
DEFAULT_ENGINES = [
    {"key": "google_aio", "kind": "aio"},
    {"key": "perplexity", "kind": "llm", "provider": "perplexity", "model": "sonar", "web_search": True},
    {"key": "chatgpt", "kind": "llm", "provider": "chat_gpt", "model": "gpt-4o-mini", "web_search": False},
    {"key": "gemini", "kind": "llm", "provider": "gemini", "model": "gemini-2.5-flash", "web_search": True},
    {"key": "claude", "kind": "llm", "provider": "claude", "model": "claude-haiku-4-5", "web_search": False},
]


def _norm(s: str) -> str:
    return (s or "").lower().replace("www.", "").strip()


def _domain_root(domain: str) -> str:
    """acme-roastworks.example -> acme-roastworks (for loose name matching)."""
    host = _norm(domain).split("/")[0]
    parts = host.split(".")
    return parts[0] if parts else host


def _hit(terms, text, domains):
    """True if any brand/competitor term appears in the answer text or the cited domains."""
    t = _norm(text)
    dset = {_norm(x) for x in domains}
    for term in terms:
        n = _norm(term)
        if not n:
            continue
        if "." in n:                       # looks like a domain
            if any(n == dom or n in dom or dom in n for dom in dset):
                return True
        if n in t:                          # name mention in the answer text
            return True
    return False


def _competitors_found(comp_map, text, domains):
    """Return the names of competitors mentioned/cited in this answer."""
    found = []
    for name, terms in comp_map.items():
        if _hit(terms, text, domains):
            found.append(name)
    return found


def scan(prompts, brand_terms, engines, competitors=None, location=2840, language="en"):
    """competitors: {display_name: [term, term, ...]}. Returns (rows, totals)."""
    load_secrets()
    comp_map = competitors or {}
    rows, total_cost = [], 0.0
    for prompt in prompts:
        for eng in engines:
            row = {"prompt": prompt, "engine": eng["key"], "model": None, "answered": False,
                   "brand_mentioned": False, "brand_cited": False, "cited_domains": [],
                   "competitors_present": [], "snippet": "", "cost": 0.0, "error": None}
            try:
                if eng["kind"] == "aio":
                    ov = d.ai_overview(prompt, location=location, language=language)
                    row["model"] = "google-ai-overview"
                    row["answered"] = ov["triggered"]
                    domains = ov.get("cited_domains", [])
                    text = ov.get("text", "")
                    row["cost"] = 0.002
                else:
                    q = d.llm_query(prompt, provider=eng["provider"], model=eng.get("model"),
                                    web_search=eng.get("web_search", False))
                    row["model"] = q.get("model")
                    text = q.get("text", "")
                    domains = q.get("cited_domains", [])
                    row["answered"] = bool(text)
                    row["cost"] = float(q.get("cost") or 0.0)
                row["cited_domains"] = domains
                row["brand_cited"] = _hit([t for t in brand_terms if "." in _norm(t)], "", domains)
                row["brand_mentioned"] = _hit(brand_terms, text, domains)
                row["competitors_present"] = _competitors_found(comp_map, text, domains)
                row["snippet"] = text[:300]
            except Exception as e:                          # one engine failing must not kill the scan
                row["error"] = str(e)[:200]
            total_cost += row["cost"]
            rows.append(row)
    return rows, {"cost": round(total_cost, 4)}


def summarize(rows, prompts, engines):
    """Per-prompt cross-engine score + which competitors dominate across the grid."""
    eng_keys = [e["key"] for e in engines]
    per_prompt = []
    comp_counter = {}
    for prompt in prompts:
        pr = [r for r in rows if r["prompt"] == prompt]
        present = [r["engine"] for r in pr if r["brand_mentioned"] or r["brand_cited"]]
        per_prompt.append({"prompt": prompt, "score": f"{len(present)}/{len(eng_keys)}",
                           "engines_present": present})
        for r in pr:
            for c in r["competitors_present"]:
                comp_counter[c] = comp_counter.get(c, 0) + 1
    top_comp = sorted(comp_counter.items(), key=lambda kv: -kv[1])
    return {"per_prompt": per_prompt, "competitor_frequency": top_comp}


def append_log(project_dir, rows, date):
    """Append normalized rows to data/ai-visibility.csv (a stable multi-engine log)."""
    log = Path(project_dir) / "data" / "ai-visibility.csv"
    log.parent.mkdir(parents=True, exist_ok=True)
    new = not log.exists()
    with log.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "engine", "model", "prompt", "brand_mentioned", "brand_cited",
                        "competitors_present", "cited_domains"])
        for r in rows:
            w.writerow([date, r["engine"], r["model"], r["prompt"], r["brand_mentioned"],
                        r["brand_cited"], ";".join(r["competitors_present"]),
                        ";".join(r["cited_domains"][:8])])
    return log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--location", type=int, default=2840)
    ap.add_argument("--language", default="en")
    ap.add_argument("--domain")
    ap.add_argument("--brand", nargs="*", help="brand name terms + domain (defaults to domain root)")
    ap.add_argument("--prompts", nargs="*", help="natural-language money queries (defaults to target_keywords)")
    ap.add_argument("--prompt-set", help="path to a prompt-set.json (from prompt_set.py) for a weighted grid")
    ap.add_argument("--engines", nargs="*", help="subset of engine keys; default = all 5")
    ap.add_argument("--web-search-all", action="store_true", help="force web search on every engine")
    ap.add_argument("--date", default="")
    ap.add_argument("--out")
    ap.add_argument("--no-log", action="store_true")
    args = ap.parse_args()

    cfg = load(args.project) if args.project else {}
    domain = args.domain or cfg.get("domain")
    if args.prompt_set:
        ps = json.loads(Path(args.prompt_set).read_text())
        prompts = [p["prompt"] for p in ps.get("prompts", [])]
    else:
        prompts = args.prompts or cfg.get("target_keywords", [])[:8]
    brand_terms = list(args.brand or [])
    if domain:
        brand_terms += [domain, _domain_root(domain)]
    brand_terms = sorted(set(t for t in brand_terms if t))

    # competitor map from client.yml (name + domain + name-root)
    comp_map = {}
    for c in cfg.get("competitors", []) or []:
        if isinstance(c, dict):
            name = c.get("name") or c.get("domain")
            terms = [t for t in [c.get("name"), c.get("domain"),
                                 _domain_root(c.get("domain", ""))] if t]
            comp_map[name] = terms

    engines = DEFAULT_ENGINES
    if args.engines:
        engines = [e for e in DEFAULT_ENGINES if e["key"] in args.engines]
    if args.web_search_all:
        engines = [{**e, "web_search": True} if e["kind"] == "llm" else e for e in engines]

    rows, totals = scan(prompts, brand_terms, engines, comp_map, args.location, args.language)
    summ = summarize(rows, prompts, engines)

    eng_keys = [e["key"] for e in engines]
    print(f"\nMulti-engine AI-visibility scan for {domain}")
    print(f"brand terms: {', '.join(brand_terms)}")
    print(f"{len(prompts)} prompts x {len(eng_keys)} engines ({', '.join(eng_keys)})  cost ~${totals['cost']}\n")
    for pp in summ["per_prompt"]:
        present = ", ".join(pp["engines_present"]) or "none"
        print(f"  [{pp['score']:>4}] {pp['prompt']}")
        print(f"          present in: {present}")
    if summ["competitor_frequency"]:
        print("\nWho the engines cite/name instead (competitor: hits across grid):")
        for name, n in summ["competitor_frequency"][:10]:
            print(f"  {n:>2}x  {name}")
    errs = [r for r in rows if r["error"]]
    if errs:
        print(f"\n{len(errs)} engine call(s) errored (e.g. {errs[0]['engine']}: {errs[0]['error'][:80]})")

    date = args.date or "undated"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(
            {"domain": domain, "location": args.location, "date": date, "engines": eng_keys,
             "rows": rows, "summary": summ, "totals": totals}, indent=2))
        print(f"\nsaved -> {args.out}")
    if args.project and not args.no_log:
        proj_dir = cfg.project_dir or Path(f"projects/{args.project}")
        log = append_log(proj_dir, rows, date)
        print(f"logged -> {log}")


if __name__ == "__main__":
    main()

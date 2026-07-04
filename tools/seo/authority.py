"""Robust multi-source domain authority for a client + all its competitors.

Authority ("how strong is this domain") is a proxy, and every provider computes it differently, so a
single number is fragile. This pulls it from EVERY source we can reach, normalizes each to 0-100,
and reports a consensus plus the spread (disagreement is a signal). More sources = more strength.

Sources (each optional and graceful; missing keys are skipped, not fatal):
  * DataForSEO  - always on (we own it): 'rank' 0-1000 + referring domains + backlinks, one bulk call.
  * Open PageRank (DomCop) - FREE API (OPENPAGERANK_API_KEY), 0-10 PageRank-style score, 100 domains/call.
  * Moz Links API - Domain Authority 0-100 (MOZ_TOKEN), the client-recognized number.
  * Ahrefs - Domain Rating 0-100 (AHREFS_API_KEY), the other recognized number, one call per domain.

    python tools/seo/authority.py --project demo          # client + client.yml competitors
    python tools/seo/authority.py --domains a.com b.com c.com    # ad-hoc set

If a source's API is unavailable and you still need its recognized number for a handful of domains, grab
it by hand (Moz Link Explorer / Semrush free Website Authority Checker) - see knowledge/seo-geo-tooling-landscape.md.
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import dataforseo as d          # noqa: E402
from connectors import ahrefs as ah              # noqa: E402
from lib.config import load, load_secrets        # noqa: E402

TODAY = "2026-07-01"


def _norm_domain(x):
    return (x or "").lower().replace("https://", "").replace("http://", "").replace("www.", "").strip("/ ").split("/")[0]


def _domain_of(c):
    return _norm_domain(c.get("domain") if isinstance(c, dict) else c)


# --------------------------------------------------------------------- sources
def source_dataforseo(domains):
    """rank 0-1000 -> /10 for a 0-100 read, plus referring domains + backlinks (bulk, cheap)."""
    out = {}
    try:
        ranks = d.backlinks_bulk_ranks(domains)
        refs = d.backlinks_bulk_referring_domains(domains)
        bls = d.backlinks_bulk_backlinks(domains)
        for dom in domains:
            rank = ranks.get(dom)
            out[dom] = {"dfs_rank": rank, "dfs_norm": (rank / 10.0) if isinstance(rank, (int, float)) else None,
                        "referring_domains": refs.get(dom), "backlinks": bls.get(dom)}
    except Exception as e:
        print(f"  [dataforseo source error] {str(e)[:120]}")
    return out


def source_openpagerank(domains):
    """Free DomCop Open PageRank API: 0-10 decimal -> x10 for 0-100. Needs OPENPAGERANK_API_KEY."""
    key = os.environ.get("OPENPAGERANK_API_KEY")
    if not key:
        return {}
    out = {}
    # up to 100 domains per call
    for i in range(0, len(domains), 100):
        batch = domains[i:i + 100]
        qs = "&".join(f"domains[]={urllib.parse.quote(x)}" for x in batch)
        req = urllib.request.Request(f"https://openpagerank.com/api/v1.0/getPageRank?{qs}",
                                     headers={"API-OPR": key})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            for row in data.get("response", []):
                dom = _norm_domain(row.get("domain"))
                opr = row.get("page_rank_decimal")
                out[dom] = {"opr": opr, "opr_norm": (opr * 10.0) if isinstance(opr, (int, float)) else None}
        except Exception as e:
            print(f"  [openpagerank source error] {str(e)[:120]}")
            break
    return out


def source_moz(domains):
    """Moz Links API url_metrics -> Domain Authority 0-100. Needs MOZ_TOKEN (or MOZ_ACCESS_ID/MOZ_SECRET)."""
    token = os.environ.get("MOZ_TOKEN")
    aid, sec = os.environ.get("MOZ_ACCESS_ID"), os.environ.get("MOZ_SECRET_KEY")
    if not (token or (aid and sec)):
        return {}
    out = {}
    headers = {"Content-Type": "application/json"}
    if token:
        headers["x-moz-token"] = token
    else:
        headers["Authorization"] = "Basic " + base64.b64encode(f"{aid}:{sec}".encode()).decode()
    body = json.dumps({"targets": [f"{dom}/" for dom in domains]}).encode()
    req = urllib.request.Request("https://lsapi.seomoz.com/v2/url_metrics", data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read().decode())
        for res in data.get("results", []):
            dom = _norm_domain(res.get("page") or res.get("target"))
            out[dom] = {"moz_da": res.get("domain_authority"), "moz_spam": res.get("spam_score")}
    except Exception as e:
        print(f"  [moz source error] {str(e)[:140]}")
    return out


def source_ahrefs(domains):
    """Ahrefs Domain Rating 0-100 (one call per domain). Needs AHREFS_API_KEY."""
    if not os.environ.get("AHREFS_API_KEY"):
        return {}
    out = {}
    for dom in domains:
        try:
            resp = ah.get("site-explorer/domain-rating", {"target": dom, "date": TODAY})
            dr = ((resp or {}).get("domain_rating") or {}).get("domain_rating")
            out[dom] = {"ahrefs_dr": dr}
        except Exception as e:
            out[dom] = {"ahrefs_dr": None, "_err": str(e)[:80]}
    return out


# --------------------------------------------------------------------- merge
def authority(domains):
    domains = [_norm_domain(x) for x in domains]
    srcs = {"dataforseo": source_dataforseo(domains), "openpagerank": source_openpagerank(domains),
            "moz": source_moz(domains), "ahrefs": source_ahrefs(domains)}
    active = [name for name, data in srcs.items() if data]
    rows = []
    for dom in domains:
        row = {"domain": dom}
        for data in srcs.values():
            row.update(data.get(dom, {}))
        norms = [row.get(k) for k in ("dfs_norm", "opr_norm", "moz_da", "ahrefs_dr") if isinstance(row.get(k), (int, float))]
        row["consensus"] = round(sum(norms) / len(norms), 1) if norms else None
        row["sources_used"] = len(norms)
        row["spread"] = round(max(norms) - min(norms), 1) if len(norms) >= 2 else None
        rows.append(row)
    rows.sort(key=lambda r: -(r.get("consensus") or 0))
    return {"active_sources": active, "rows": rows, "date": TODAY}


def write_csv(path, res):
    cols = ["domain", "consensus", "sources_used", "spread", "dfs_norm", "opr_norm", "moz_da", "ahrefs_dr",
            "dfs_rank", "referring_domains", "backlinks"]
    with Path(path).open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in res["rows"]:
            w.writerow([r.get(c) for c in cols])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--domain", help="client domain (defaults to client.yml)")
    ap.add_argument("--domains", nargs="*", help="ad-hoc domain set (overrides project)")
    ap.add_argument("--out")
    ap.add_argument("--csv")
    args = ap.parse_args()
    load_secrets()

    cfg = load(args.project) if args.project else None
    if args.domains:
        domains, client = [_norm_domain(x) for x in args.domains], None
    else:
        client = _norm_domain(args.domain or (cfg.get("domain") if cfg else None))
        comps = [_domain_of(c) for c in (cfg.get("competitors", []) if cfg else [])]
        domains = [client] + [c for c in comps if c and c != client]
    if not domains or not domains[0]:
        print("no domains (pass --domains or --project with client.yml)"); return

    res = authority(domains)
    print(f"\nMulti-source domain authority ({args.project or 'ad-hoc'})  date {res['date']}")
    print(f"sources active: {', '.join(res['active_sources']) or 'dataforseo only'}"
          f"   (add OPENPAGERANK_API_KEY / MOZ_TOKEN for more)\n")
    hdr = f"  {'domain':28s} {'CONS':>5} {'DFS':>5} {'OPR':>5} {'MOZ':>5} {'DR':>4} {'refDoms':>8} {'spread':>6}"
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for r in res["rows"]:
        star = "  <- client" if client and r["domain"] == client else ""
        def g(k, w=5, dp=0):
            v = r.get(k)
            return (f"{v:>{w}.{dp}f}" if isinstance(v, (int, float)) else f"{'-':>{w}}")
        print(f"  {r['domain']:28s} {g('consensus',5,1)} {g('dfs_norm')} {g('opr_norm')} "
              f"{g('moz_da')} {g('ahrefs_dr',4)} {g('referring_domains',8)} {g('spread',6,1)}{star}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(res, indent=2))
        print(f"\nsaved -> {args.out}")
    csv_path = args.csv
    if not csv_path and cfg and cfg.project_dir:
        csv_path = cfg.project_dir / "data" / "authority.csv"
    if csv_path:
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        write_csv(csv_path, res)
        print(f"csv   -> {csv_path}")


if __name__ == "__main__":
    main()

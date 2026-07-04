"""AI Share-of-Voice engine (the Brand-Radar-equivalent core).

Reads a multi-engine llm-visibility scan and computes Share of Voice: each brand's mentions/citations,
weighted by query search volume, as a % of all tracked brands, per engine and blended. Appends to a
history CSV so the dashboard/report can trend it. Follows Ahrefs' definitions: mention = brand named,
citation = brand's site linked, impression = a mention weighted by the query's search volume.

    # 1. build a weighted prompt set   2. scan it   3. compute SoV
    python tools/geo/prompt_set.py    --project demo --location 2840 --out .../prompt-set.json
    python tools/geo/llm_visibility.py --project demo --location 2840 --prompt-set .../prompt-set.json --out .../scan.json
    python tools/geo/sov.py           --project demo --scan .../scan.json --prompt-set .../prompt-set.json

Honesty rule baked in: SoV is "within the tracked demand set" (state the sample size), and any single
scan is noisy, so trend it, do not quote one reading. Keep the method internal; show the client the number.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.config import load          # noqa: E402


def _root(domain):
    return (domain or "").lower().replace("www.", "").split("/")[0].split(".")[0]


def compute(scan, weights, client_label):
    rows = scan.get("rows", [])
    engines = scan.get("engines") or sorted({r["engine"] for r in rows})
    # impressions[engine][brand] and blended
    impr = {e: {} for e in engines}
    present_hits = {e: 0 for e in engines}      # prompts where client present (unweighted)
    prompts = sorted({r["prompt"] for r in rows})
    for r in rows:
        e, p = r["engine"], r["prompt"]
        w = (weights.get(p, 0) or 0) + 1        # +1 smoothing: every prompt counts, volume weights more
        present = []
        if r.get("brand_mentioned") or r.get("brand_cited"):
            present.append(client_label)
            if r["engine"] == e:
                present_hits[e] += 1
        present += list(r.get("competitors_present", []) or [])
        for b in present:
            impr[e][b] = impr[e].get(b, 0) + w
    # brands = client + every competitor seen
    brands = {client_label}
    for e in engines:
        brands |= set(impr[e])
    brands = sorted(brands)
    # SoV per engine + blended
    sov = {b: {"per_engine": {}, "blended": 0.0} for b in brands}
    blended_impr = {b: 0 for b in brands}
    for e in engines:
        tot = sum(impr[e].values()) or 1
        for b in brands:
            v = impr[e].get(b, 0)
            sov[b]["per_engine"][e] = round(100 * v / tot, 1)
            blended_impr[b] += v
    tot_all = sum(blended_impr.values()) or 1
    for b in brands:
        sov[b]["blended"] = round(100 * blended_impr[b] / tot_all, 1)
    n_prompts = len(prompts)
    client_present_rate = {e: round(100 * present_hits[e] / n_prompts, 0) if n_prompts else 0 for e in engines}
    ranked = sorted(brands, key=lambda b: -sov[b]["blended"])
    return {"engines": engines, "brands": ranked, "sov": sov, "client": client_label,
            "n_prompts": n_prompts, "client_present_rate": client_present_rate,
            "total_weight": sum((weights.get(p, 0) or 0) + 1 for p in prompts)}


def append_history(project_dir, res, date):
    hp = Path(project_dir) / "data" / "sov-history.csv"
    hp.parent.mkdir(parents=True, exist_ok=True)
    new = not hp.exists()
    with hp.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "brand", "scope", "sov_pct", "is_client", "n_prompts"])
        for b in res["brands"]:
            w.writerow([date, b, "blended", res["sov"][b]["blended"], b == res["client"], res["n_prompts"]])
    return hp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--scan", required=True, help="llm-visibility scan JSON")
    ap.add_argument("--prompt-set", help="prompt-set JSON for volume weights (else equal weight)")
    ap.add_argument("--client", help="client brand label (defaults to domain root)")
    ap.add_argument("--date", default="")
    ap.add_argument("--out")
    ap.add_argument("--no-history", action="store_true")
    args = ap.parse_args()

    scan = json.loads(Path(args.scan).read_text())
    weights = {}
    if args.prompt_set:
        ps = json.loads(Path(args.prompt_set).read_text())
        weights = {p["prompt"]: p.get("volume") for p in ps.get("prompts", [])}
    cfg = load(args.project) if args.project else None
    client_label = args.client or _root(scan.get("domain") or (cfg.get("domain") if cfg else "client"))

    res = compute(scan, weights, client_label)

    print(f"\nAI Share of Voice ({args.project or 'ad-hoc'})  {res['n_prompts']} prompts x "
          f"{len(res['engines'])} engines  [scope: tracked demand set]")
    weighted = "volume-weighted" if weights else "equal-weight (no prompt-set)"
    print(f"weighting: {weighted}\n")
    eng = res["engines"]
    hdr = f"  {'brand':22s} {'BLENDED':>8}   " + " ".join(f"{e[:7]:>8}" for e in eng)
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for b in res["brands"]:
        star = "  <- client" if b == res["client"] else ""
        per = " ".join(f"{res['sov'][b]['per_engine'].get(e,0):>7.1f}%" for e in eng)
        print(f"  {b:22s} {res['sov'][b]['blended']:>7.1f}%   {per}{star}")
    cpr = res["client_present_rate"]
    print(f"\n  client present-rate per engine: " + ", ".join(f"{e}:{int(cpr[e])}%" for e in eng))

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(res, indent=2))
        print(f"\nsaved -> {args.out}")
    if args.project and cfg and cfg.project_dir and not args.no_history:
        hp = append_history(cfg.project_dir, res, args.date or scan.get("date") or "undated")
        print(f"history -> {hp}")


if __name__ == "__main__":
    main()

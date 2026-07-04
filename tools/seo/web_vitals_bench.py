"""Core Web Vitals benchmark: client vs competitors (via DataForSEO Lighthouse, no Google key).

Lab Core Web Vitals (LCP / CLS / blocking) + a mobile performance score for each origin, ~$0.005/page.
Lab is a controlled test that works for ANY site, including a brand-new one with no real-user traffic.
(Real-user field data would need Google CrUX; lab is the universal, key-free read.)

    python tools/seo/web_vitals_bench.py --project <slug>
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

THRESH = {"LCP": (2500, 4000), "CLS": (0.1, 0.25), "TBT": (200, 600)}  # (good, poor)


def _dom(x):
    return (x.get("domain") if isinstance(x, dict) else x or "").lower().replace("www.", "").strip("/")


def _verdict(metric, v):
    if v is None:
        return None
    g, p = THRESH[metric]
    return "good" if v <= g else ("needs-improvement" if v <= p else "poor")


def assess(url):
    lh = d.lighthouse(url, mobile=True)
    lv, cv, tv = _verdict("LCP", lh["lcp_ms"]), _verdict("CLS", lh["cls"]), _verdict("TBT", lh["tbt_ms"])
    passed = all(x == "good" for x in (lv, cv, tv) if x) if (lv and cv and tv) else None
    return {"url": url, "lab_performance": lh["performance"], "cwv_passed": passed,
            "lcp_ms": lh["lcp_ms"], "LCP_verdict": lv, "cls": lh["cls"], "CLS_verdict": cv,
            "tbt_ms": lh["tbt_ms"], "TBT_verdict": tv, "mode": "lab"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--date", default="latest")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)
    companies = [(cfg.get("client_name") or cfg.get("name") or _dom(cfg.get("domain")), _dom(cfg.get("domain")))]
    for c in (cfg.get("competitors", []) or []):
        dd = _dom(c)
        if dd:
            companies.append((c.get("name") if isinstance(c, dict) else dd, dd))
    out = {}
    print(f"\nCore Web Vitals ({args.project})  [mobile, lab test via Lighthouse]")
    for name, dom in companies:
        try:
            a = assess(f"https://{dom}/")
        except Exception as e:
            a = {"url": f"https://{dom}/", "error": str(e)[:90]}
        out[name] = a
        if a.get("error"):
            st = f"error: {a['error'][:45]}"
        else:
            cwv = "PASS" if a["cwv_passed"] else ("FAIL" if a["cwv_passed"] is False else "?")
            st = f"perf {a['lab_performance']}/100  CWV {cwv} (LCP {a['LCP_verdict']}, CLS {a['CLS_verdict']}, blocking {a['TBT_verdict']})"
        print(f"  {name:18s} {st}")

    pdir = cfg.project_dir
    (pdir / "data" / "raw" / "pagespeed").mkdir(parents=True, exist_ok=True)
    (pdir / "data" / "raw" / "pagespeed" / f"webvitals-{args.date}.json").write_text(json.dumps(out, indent=2))
    with (pdir / "data" / "web-vitals.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["company", "lab_performance", "cwv_passed", "LCP_verdict", "CLS_verdict", "TBT_verdict"])
        for name, a in out.items():
            w.writerow([name, a.get("lab_performance"), a.get("cwv_passed"), a.get("LCP_verdict"),
                        a.get("CLS_verdict"), a.get("TBT_verdict")])
    print(f"\nsaved -> data/raw/pagespeed/webvitals-{args.date}.json + data/web-vitals.csv")


if __name__ == "__main__":
    main()

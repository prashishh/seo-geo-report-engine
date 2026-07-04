"""Public social/profile footprint snapshot for a client and competitors.

Internal source names stay out of client reports. This script writes structured
data that reports can summarize as "public company/social profiles".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import apify  # noqa: E402
from lib.config import load, load_secrets  # noqa: E402

TODAY = "2026-07-01"


LINKEDIN = {
    "Acme Roastworks": "https://www.linkedin.com/company/acme-roastworks",
    "Globex Coffee": "https://www.linkedin.com/company/globex-coffee",
    "Initech Brew Co.": "https://www.linkedin.com/company/initech-brew",
    "Vandelay Roasters": "https://www.linkedin.com/company/vandelay-roasters",
}


def _company_rows(cfg):
    rows = [{"name": cfg.get("name") or "Client", "domain": cfg.get("domain")}]
    for c in cfg.get("competitors", []) or []:
        if isinstance(c, dict):
            rows.append({"name": c.get("name"), "domain": c.get("domain")})
    return rows


def _num(text):
    if not text:
        return None
    m = re.search(r"([\d,.]+)\s*([KMB])?", text, re.I)
    if not m:
        return None
    n = float(m.group(1).replace(",", ""))
    mult = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get((m.group(2) or "").upper(), 1)
    return int(n * mult)


def _extract(markdown):
    text = markdown or ""
    lower = text.lower()
    out = {"followers": None, "employees": None, "headquarters": None, "locations": [], "raw_excerpt": text[:1600]}
    f = re.search(r"([\d,.]+\s*[KMB]?)\s+followers", text, re.I)
    if f:
        out["followers"] = _num(f.group(1))
    e = re.search(r"company size\s*[:\n ]+([^\n]+)", text, re.I) or re.search(r"([\d,]+\s*-\s*[\d,]+)\s+employees", text, re.I)
    if e:
        out["employees"] = e.group(1).strip()
    h = re.search(r"headquarters\s*[:\n ]+([^\n]+)", text, re.I)
    if h:
        out["headquarters"] = h.group(1).strip()
    for city in ("Jacksonville", "Hyderabad", "London", "New York", "San Francisco", "Pune", "Bengaluru", "Krakow"):
        if city.lower() in lower:
            out["locations"].append(city)
    out["locations"] = sorted(set(out["locations"]))
    return out


def crawl_linkedin(urls):
    payload = {
        "startUrls": [{"url": u} for u in urls],
        "maxCrawlPages": len(urls),
        "maxCrawlDepth": 0,
        "crawlerType": "playwright:chrome",
        "saveMarkdown": True,
        "saveHtml": False,
        "saveScreenshots": False,
        "removeElementsCssSelector": "script, style, noscript, svg, img",
    }
    return apify.run_actor_sync_dataset("apify/website-content-crawler", payload, timeout=300) or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)

    companies = _company_rows(cfg)
    urls = []
    url_to_name = {}
    for c in companies:
        u = LINKEDIN.get(c["name"])
        if u:
            urls.append(u)
            url_to_name[u.rstrip("/")] = c["name"]

    items = crawl_linkedin(urls)
    by_name = {c["name"]: {"name": c["name"], "domain": c.get("domain"), "linkedin_url": LINKEDIN.get(c["name"])}
               for c in companies}
    for item in items:
        url = (item.get("url") or "").rstrip("/")
        name = url_to_name.get(url)
        if not name:
            for u, n in url_to_name.items():
                if u in url:
                    name = n
                    break
        if not name:
            continue
        md = item.get("markdown") or item.get("text") or ""
        by_name[name].update(_extract(md))
        by_name[name]["captured"] = bool(md)

    out = {"date": TODAY, "source_label": "public social/company profiles", "rows": list(by_name.values())}
    out_path = Path(args.out) if args.out else cfg.project_dir / "data" / "social-footprint.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"saved -> {out_path}")
    for r in out["rows"]:
        print(r.get("name"), r.get("followers"), r.get("employees"), r.get("headquarters"), "captured", r.get("captured"))


if __name__ == "__main__":
    main()

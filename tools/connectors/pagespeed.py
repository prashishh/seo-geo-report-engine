"""PageSpeed Insights (Lighthouse lab + CrUX field) — live Core Web Vitals for a URL.

Stdlib only. Hits Google's free PageSpeed Insights API and distils it to the metrics that
matter: the field (real-user, CrUX) and lab (Lighthouse) Core Web Vitals plus the top
opportunities. Powers the `web-vitals` skill.

    python tools/connectors/pagespeed.py https://example.com            # mobile
    python tools/connectors/pagespeed.py https://example.com desktop
    python tools/connectors/pagespeed.py https://example.com both       # mobile + desktop

GOOGLE_PSI_API_KEY in config/secrets.env is optional (raises the quota); the API also works
without a key, just rate-limited. No pip installs.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Core Web Vitals "good" thresholds (field / p75).
THRESHOLDS = {
    "LCP": (2500, 4000, "ms"),   # good < 2.5s, poor > 4s
    "INP": (200, 500, "ms"),     # good < 200ms, poor > 500ms
    "CLS": (0.1, 0.25, ""),      # good < 0.10, poor > 0.25
    "FCP": (1800, 3000, "ms"),
    "TTFB": (800, 1800, "ms"),
}
FIELD_KEYS = {
    "LCP": "LARGEST_CONTENTFUL_PAINT_MS",
    "INP": "INTERACTION_TO_NEXT_PAINT",
    "CLS": "CUMULATIVE_LAYOUT_SHIFT_SCORE",
    "FCP": "FIRST_CONTENTFUL_PAINT_MS",
    "TTFB": "EXPERIMENTAL_TIME_TO_FIRST_BYTE",
}


def fetch(url: str, strategy: str = "mobile", token: str | None = None,
          timeout: int = 90, retries: int = 3) -> dict:
    token = token or os.environ.get("GOOGLE_PSI_API_KEY")
    params = [("url", url), ("strategy", strategy), ("category", "performance")]
    if token:
        params.append(("key", token))
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params),
                                 headers={"Accept": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(8 * (attempt + 1))  # backoff for the anonymous quota window
                continue
            if e.code == 429:
                raise RuntimeError(
                    "PageSpeed Insights rate-limited (HTTP 429). Add a free key to "
                    "config/secrets.env as GOOGLE_PSI_API_KEY to lift the quota "
                    "(get one at https://developers.google.com/speed/docs/insights/v5/get-started)."
                ) from e
            raise


def _verdict(metric: str, value) -> str:
    if value is None or metric not in THRESHOLDS:
        return "n/a"
    good, poor, _ = THRESHOLDS[metric]
    v = value / 100 if metric == "CLS" else value  # CrUX returns CLS×100
    if v <= good:
        return "good"
    if v <= poor:
        return "needs-improvement"
    return "poor"


def summarize(data: dict) -> dict:
    lh = data.get("lighthouseResult", {})
    audits = lh.get("audits", {})
    cats = lh.get("categories", {})

    def lab(key):
        return audits.get(key, {}).get("displayValue")

    le = data.get("loadingExperience", {}).get("metrics", {})

    def field(name):
        m = le.get(FIELD_KEYS[name], {})
        p = m.get("percentile")
        if p is None:
            return None
        val = round(p / 100, 3) if name == "CLS" else p
        return {"p75": val, "verdict": _verdict(name, p)}

    opps = []
    for a in audits.values():
        det = a.get("details", {})
        if det.get("type") == "opportunity" and (a.get("numericValue") or 0) > 0:
            opps.append((a.get("numericValue"), a.get("title"), a.get("displayValue") or ""))
    opps.sort(reverse=True)

    return {
        "url": data.get("id"),
        "strategy": lh.get("configSettings", {}).get("formFactor"),
        "fetched": lh.get("fetchTime"),
        "performance_score": round((cats.get("performance", {}).get("score") or 0) * 100),
        "field_cwv": {k: field(k) for k in FIELD_KEYS},
        "field_overall": data.get("loadingExperience", {}).get("overall_category"),
        "lab": {"LCP": lab("largest-contentful-paint"), "CLS": lab("cumulative-layout-shift"),
                "TBT": lab("total-blocking-time"), "FCP": lab("first-contentful-paint"),
                "SI": lab("speed-index"), "TTI": lab("interactive")},
        "opportunities": [{"title": t, "est_savings": d} for _, t, d in opps[:8]],
    }


def run(url: str, strategy: str = "mobile") -> list[dict]:
    strategies = ["mobile", "desktop"] if strategy == "both" else [strategy]
    return [summarize(fetch(url, s)) for s in strategies]


if __name__ == "__main__":
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from lib.config import load_env, root
        load_env(root() / "config" / "secrets.env")
    except Exception:
        pass
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    strat = sys.argv[2] if len(sys.argv) > 2 else "mobile"
    print(json.dumps(run(url, strat), indent=2))

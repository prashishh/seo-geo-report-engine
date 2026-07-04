"""Ad-messaging teardown: what each competitor is buying attention with (via the Perplexity probe).

Upgrades the ad COUNTS (from google_ads.py) to the ANGLE: for each competitor it reads their live ads,
landing pages, and campaign coverage and returns the main message, the hooks, and the offer they run.
DataForSEO's ad-creative endpoint is not usable, and Meta's free API returns only political ads, so a
cited web read is the reliable owned path to the messaging intel.

    python tools/seo/ad_messaging.py --project <slug>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connectors import openrouter as orr        # noqa: E402
from lib.config import load, load_secrets        # noqa: E402

PROMPT = (
    "For {name} ({domain}), an AI agents / AI digital-worker SaaS company, what advertising and "
    "marketing MESSAGING is it running in 2026 across Google, Meta, LinkedIn ads and campaigns? "
    "Return ONLY a JSON object, no prose, no code fence:\n"
    '{{"main_message": "one short line", "hooks": [up to 3 short phrases], "offer": "one short line or null", '
    '"channels": [platforms], "note": "one short line"}}\n'
    "Base it on their ACTUAL ads and landing pages. If they do not appear to advertise, say so in note "
    "with nulls. Ignore unrelated products with similar names."
)


def _parse(text):
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    try:
        return json.loads(m.group(0)) if m else {}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--date", default="latest")
    args = ap.parse_args()
    load_secrets()
    cfg = load(args.project)
    comps = [(c.get("name") or c.get("domain"), c.get("domain"))
             for c in (cfg.get("competitors", []) or []) if isinstance(c, dict)]
    out = {}
    print(f"\nAd-messaging teardown ({args.project})")
    for name, dom in comps:
        try:
            resp = orr.probe(PROMPT.format(name=name, domain=dom))
            data = _parse(resp.get("answer") or resp.get("text") or "")
            data["sources"] = [s.get("url") for s in (resp.get("sources") or [])][:4]
        except Exception as e:
            data = {"error": str(e)[:90]}
        out[name] = data
        print(f"  {name:16s} {(data.get('main_message') or data.get('note') or '-')[:70]}")

    p = cfg.project_dir / "data" / "raw" / "openrouter" / f"ad-messaging-{args.date}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(f"\nsaved -> {p}")


if __name__ == "__main__":
    main()

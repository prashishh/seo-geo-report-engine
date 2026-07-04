"""PredictLeads connector (stdlib only): competitor funding, hiring, news, and tech intelligence.

The freshest "never seen this in a deck" competitor signal: hiring velocity by department (direction a
company is moving), funding/M&A/exec-move news, and technology changes, sourced from each company's own
careers page + newsroom. JSON:API format. Auth via X-Api-Key / X-Api-Token headers (config/secrets.env).

    from connectors.predictleads import news_events, financing_events, job_openings, technologies
    fin = financing_events("11x.ai")     # funding rounds
    jobs = job_openings("decagon.ai")    # open roles (hiring direction)
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://predictleads.com/api/v3"


def _headers():
    k = os.environ.get("PREDICTLEADS_API_KEY")
    t = os.environ.get("PREDICTLEADS_API_TOKEN")
    if not (k and t):
        raise RuntimeError("PREDICTLEADS_API_KEY / PREDICTLEADS_API_TOKEN not set (config/secrets.env).")
    return {"X-Api-Key": k, "X-Api-Token": t, "Accept": "application/json"}


def get(path: str, params: dict = None, timeout: int = 60, retries: int = 3):
    url = f"{BASE}/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers=_headers())
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8")), r.status
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code in (429, 502, 503) and attempt < retries - 1:
                time.sleep(3 * (attempt + 1)); continue
            return {"error": e.code, "body": body}, e.code
        except Exception as e:
            return {"error": str(e)[:200]}, 0


# ---------------- typed helpers (JSON:API -> list of attribute dicts) ----------------
def _items(resp):
    data = (resp or {}).get("data")
    if isinstance(data, list):
        return [d.get("attributes", d) for d in data]
    if isinstance(data, dict):
        return [data.get("attributes", data)]
    return []


def company(domain: str):
    resp, _ = get(f"companies/{domain}")
    return _items(resp)


def financing_events(domain: str, limit: int = 50):
    resp, _ = get(f"companies/{domain}/financing_events", {"limit": limit})
    return _items(resp)


def news_events(domain: str, categories=None, limit: int = 100):
    params = {"limit": limit}
    if categories:
        params["categories[]"] = list(categories)
    resp, _ = get(f"companies/{domain}/news_events", params)
    return _items(resp)


def job_openings(domain: str, limit: int = 100, active_only: bool = True):
    params = {"limit": limit}
    if active_only:
        params["not_closed"] = "true"
    resp, _ = get(f"companies/{domain}/job_openings", params)
    return _items(resp)


def technologies(domain: str, limit: int = 100):
    resp, _ = get(f"companies/{domain}/technologies", {"limit": limit})
    return _items(resp)


def connections(domain: str, limit: int = 50):
    resp, _ = get(f"companies/{domain}/connections", {"limit": limit})
    return _items(resp)

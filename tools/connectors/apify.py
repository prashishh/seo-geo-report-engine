"""Minimal Apify REST connector (stdlib only).

Keeps Apify as an internal data source. Client-facing reports should cite the
public source type, not this connector or actor names.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.apify.com/v2"


def _token() -> str:
    tok = os.environ.get("APIFY_API_TOKEN")
    if not tok:
        raise RuntimeError("APIFY_API_TOKEN is not set")
    return tok


def _url(path: str, params=None) -> str:
    params = dict(params or {})
    params["token"] = _token()
    return f"{BASE}/{path.lstrip('/')}?{urllib.parse.urlencode(params)}"


def get(path: str, params=None, timeout: int = 60):
    with urllib.request.urlopen(_url(path, params), timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def post(path: str, payload, params=None, timeout: int = 300):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        _url(path, params),
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:800]
        raise RuntimeError(f"Apify HTTP {e.code}: {detail}") from e
    return json.loads(body) if body.strip() else None


def run_actor_sync_dataset(actor_id: str, payload, timeout: int = 300):
    actor = actor_id.replace("/", "~")
    return post(f"acts/{actor}/run-sync-get-dataset-items", payload, timeout=timeout)

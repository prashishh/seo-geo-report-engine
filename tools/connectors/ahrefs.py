"""Ahrefs API v3 — minimal stdlib HTTP fallback.

The Ahrefs MCP is primary; use this only when the MCP is unavailable (e.g. Codex/headless).
    from connectors.ahrefs import get
    data = get("site-explorer/domain-rating", {"target": "example.com", "date": "2026-06-23"})
Needs AHREFS_API_KEY in config/secrets.env (loaded by lib.config.load_env) or the environment.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

BASE = "https://api.ahrefs.com/v3"


def get(endpoint: str, params: dict | None = None, token: str | None = None, timeout: int = 60):
    token = token or os.environ.get("AHREFS_API_KEY")
    if not token:
        raise RuntimeError("AHREFS_API_KEY not set (config/secrets.env). The MCP is preferred anyway.")
    url = f"{BASE}/{endpoint.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lib.config import load_env, root
    load_env(root() / "config" / "secrets.env")
    ep = sys.argv[1] if len(sys.argv) > 1 else "subscription-info/limits-and-usage"
    print(json.dumps(get(ep), indent=2))

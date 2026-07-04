"""OpenRouter — unified LLM API used here for live, cited web research and AI-citation probing.

Powers the `web-research` skill: deep multi-hop research with sources (Perplexity Sonar Deep
Research) and cheap single-shot "what does AI say about X" probes (Perplexity Sonar) used
alongside Ahrefs Brand Radar as a live GEO/AI-citation signal.

Stdlib only.
    from connectors.openrouter import deep_research, probe
    result = deep_research("what do hotel guests say about digital tipping")
    result = probe("What platform do hotels use for cashless staff tipping?")

Needs OPENROUTER_API_KEY in config/secrets.env (loaded by lib.config.load_env) or the
environment. Get a key at https://openrouter.ai/keys — Perplexity Sonar calls are billed
pay-as-you-go from there, no separate Perplexity account needed.
"""
from __future__ import annotations

import http.client
import json
import os
import socket
import time
import urllib.error
import urllib.request

API = "https://openrouter.ai/api/v1/chat/completions"

# Model choice controls cost. Deep Research is a multi-step search + reasoning agent (verified
# ~$2/$8 per M tokens + ~$5/1000 searches -> roughly $0.04-0.05 per call). The base `sonar` model
# is a single always-on grounded call (~$1/$1 per M tokens -> a fraction of a cent per call) --
# cheap enough to run a whole prompt grid of brand-citation probes without worrying about spend.
DEEP_RESEARCH_MODEL = "perplexity/sonar-deep-research"
PROBE_MODEL = "perplexity/sonar"

# Deep Research keeps the connection open while it runs multiple internal search+reason steps;
# on a flaky network that can end the response early (http.client.IncompleteRead) well before our
# read timeout fires. Both are worth a retry -- they're transient, not an error in the request.
_TRANSIENT = (http.client.IncompleteRead, ConnectionError, socket.timeout, TimeoutError)


def chat(model: str, prompt: str, token: str | None = None, timeout: int = 240, retries: int = 4) -> dict:
    """Raw call to OpenRouter's OpenAI-shaped chat completions endpoint."""
    token = token or os.environ.get("OPENROUTER_API_KEY")
    if not token:
        raise RuntimeError(
            "OPENROUTER_API_KEY not set (config/secrets.env). Get a key at "
            "https://openrouter.ai/keys — Sonar calls are pay-as-you-go from there."
        )
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request(
        API, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/seo-geo-report-engine",
            "X-Title": "seo-geo-report-engine",
        },
    )
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            detail = e.read().decode("utf-8", "replace")[:500] if e.fp else str(e)
            raise RuntimeError(f"OpenRouter HTTP {e.code}: {detail}") from e
        except _TRANSIENT as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(4 * (attempt + 1))
                continue
            raise RuntimeError(
                f"OpenRouter connection dropped after {retries} attempts ({e!r}). "
                "This happens on slow/flaky links with the deep-research model, which keeps the "
                "connection open through several internal search steps -- try again, or use the "
                "cheaper `probe()` mode which returns in one quick round trip."
            ) from e
    raise RuntimeError(f"OpenRouter request failed: {last_err!r}")


def _normalize(resp: dict) -> dict:
    choice = (resp.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = message.get("content", "")

    # Citations show up in two different shapes depending on model/route:
    #  (a) top-level `citations` (list of URLs) + `search_results` (title/url/snippet) -- the
    #      shape Perplexity's own API docs describe;
    #  (b) OpenAI-style `message.annotations` with {"type": "url_citation", "url_citation": {...}}
    #      -- what OpenRouter actually returns for perplexity/sonar as observed 2026-07-01.
    # Normalize both into one list of {url, title}.
    sources = []
    seen_urls = set()
    for sr in resp.get("search_results") or []:
        url = sr.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            sources.append({"url": url, "title": sr.get("title", ""), "date": sr.get("date", "")})
    for ann in message.get("annotations") or []:
        uc = ann.get("url_citation") or {}
        url = uc.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            sources.append({"url": url, "title": uc.get("title", ""), "date": ""})
    if not sources:
        for url in resp.get("citations") or []:
            if url not in seen_urls:
                seen_urls.add(url)
                sources.append({"url": url, "title": "", "date": ""})

    return {
        "answer": content,
        "sources": sources,
        "citations": [s["url"] for s in sources],
        "model": resp.get("model"),
        "usage": resp.get("usage", {}),
    }


def deep_research(query: str, model: str = DEEP_RESEARCH_MODEL, **kw) -> dict:
    """Autonomous multi-step research with a synthesized answer plus a real citation list.

    Use for voice-of-customer mining, competitor fact gathering, market sizing/statistics —
    anything that needs synthesis across many live sources, not a single page fetch. This is
    the expensive mode (~$0.04-0.05/call); use it for depth, not bulk probing.
    """
    prompt = (
        f"Research this and answer with concrete, current, sourced facts: {query}\n\n"
        "Be specific, cite what you find, and flag anything you could not verify."
    )
    return _normalize(chat(model, prompt, **kw))


def probe(prompt: str, model: str = PROBE_MODEL, **kw) -> dict:
    """Cheap, single grounded query — literally ask what an AI engine says right now.

    Use for GEO/AI-citation probing: run the same brand-check prompt across a prompt grid
    (see the geo-audit / ai-citation-sprint skills) to see whether a brand gets mentioned and
    which sources get cited instead. Costs a fraction of a cent per call — safe to run at
    volume as a live cross-check alongside Ahrefs Brand Radar, especially useful when Brand
    Radar or the Ahrefs MCP is unavailable.
    """
    return _normalize(chat(model, prompt, **kw))


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lib.config import load_env, root
    load_env(root() / "config" / "secrets.env")
    mode = sys.argv[1] if len(sys.argv) > 1 else "probe"
    q = sys.argv[2] if len(sys.argv) > 2 else "What is digital tipping for hotels?"
    fn = deep_research if mode == "deep" else probe
    print(json.dumps(fn(q), indent=2))

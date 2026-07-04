"""DataForSEO, the committed data backbone (stdlib only).

One pay-as-you-go API covering five engines, all confirmed live on this account (2026-07-01):
  * SERP        - live Google SERP incl. the AI Overview block + People-Also-Ask (serp, ai_overview, paa)
  * Labs        - keyword difficulty + volume + intent, keyword ideas, a domain's ranked keywords, and
                  competitor keyword gaps (keyword_overview, keyword_difficulty, keyword_ideas,
                  ranked_keywords, domain_intersection, competitors_domain)
  * Backlinks   - profile summary, referring domains, bulk DR-equivalent rank (backlinks_summary,
                  referring_domains, backlinks_bulk_ranks)
  * OnPage      - single-page technical crawl (onpage_instant)
  * AI Optimization - query ChatGPT / Gemini / Perplexity / Claude directly and capture the answer +
                  its citations (llm_query, llm_models) -- a live, multi-engine GEO-visibility engine

Codex-safe (no Ahrefs MCP needed). Credentials are per-profile: DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD
in config/secrets.<profile>.env (see lib.config.load_secrets). Basic auth is login:password.

    from connectors.dataforseo import serp, ai_overview, keyword_overview, ranked_keywords, llm_query
    ov  = ai_overview("best broker in nepal", location=2524)       # Google AI Overview + citations
    kw  = keyword_overview(["best crm software"], location=2840)   # volume + KD + intent in one call
    ans = llm_query("best CRM for small business?", provider="perplexity")  # what the model says + cites

Locations: 2840 = US, 2524 = Nepal, 2356 = India, 2826 = UK. Language codes: "en", "ne", ...
Caveat: DataForSEO Labs covers ~94 locations and Nepal (2524) is NOT one of them; for Labs-unsupported
markets use keyword_volume (Google Ads, any location) + serp_competitors (SERP-derived, any location).
"""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request

BASE = "https://api.dataforseo.com/v3"


def _auth() -> str:
    login = os.environ.get("DATAFORSEO_LOGIN")
    pw = os.environ.get("DATAFORSEO_PASSWORD")
    if not (login and pw):
        raise RuntimeError(
            "DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD not set. They live in the active profile file "
            "config/secrets.<profile>.env (switch with ./bin/mkt profile use <name>)."
        )
    return base64.b64encode(f"{login}:{pw}".encode()).decode()


def _req(method: str, endpoint: str, payload=None, timeout: int = 120, retries: int = 3):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Basic {_auth()}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE}/{endpoint.lstrip('/')}", data=data, method=method, headers=headers)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(3 * (attempt + 1)); continue
            raise RuntimeError(f"DataForSEO HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}") from e


def post(endpoint: str, payload, timeout: int = 120):
    return _req("POST", endpoint, payload, timeout)


def get(endpoint: str, timeout: int = 60):
    return _req("GET", endpoint, None, timeout)


def result(resp: dict):
    """Unwrap tasks[0].result, raising on a task-level API error."""
    tasks = resp.get("tasks") or []
    if not tasks:
        raise RuntimeError(f"DataForSEO: no tasks in response ({resp.get('status_message')})")
    t = tasks[0]
    if t.get("status_code") != 20000:
        raise RuntimeError(f"DataForSEO task {t.get('status_code')}: {t.get('status_message')}")
    return t.get("result")


def balance() -> float:
    """Account money balance in USD (auth check + budget)."""
    r = result(get("appendix/user_data"))
    return (r[0].get("money", {}) or {}).get("balance") if r else None


# ---------------- SERP + AI Overview ----------------
def serp(keyword: str, location: int = 2840, language: str = "en", depth: int = 20, device: str = "desktop"):
    """Live Google organic SERP (advanced): organic, PAA, featured snippet, AI Overview, related."""
    payload = [{"keyword": keyword, "location_code": location, "language_code": language,
                "depth": depth, "device": device}]
    r = result(post("serp/google/organic/live/advanced", payload))
    return r[0] if r else None


def _items(serp_result, item_type):
    return [it for it in (serp_result or {}).get("items", []) if it.get("type") == item_type]


def ai_overview(keyword: str, location: int = 2840, language: str = "en"):
    """Return the Google AI Overview block for a query: whether it triggered, its text, and the
    domains/URLs it cites. This is the most important AI-search surface and the core of GEO tracking."""
    sr = serp(keyword, location, language, depth=20)
    blocks = _items(sr, "ai_overview")
    if not blocks:
        return {"keyword": keyword, "triggered": False, "text": "", "references": [], "cited_domains": []}
    b = blocks[0]
    # AI Overview text lives in nested item elements; references carry title/url/domain.
    text_parts, refs = [], []
    for el in b.get("items", []) or []:
        if el.get("text"):
            text_parts.append(el["text"])
        for r in el.get("references", []) or []:
            refs.append({"title": r.get("title"), "url": r.get("url"), "domain": r.get("domain")})
    for r in b.get("references", []) or []:
        refs.append({"title": r.get("title"), "url": r.get("url"), "domain": r.get("domain")})
    seen, dedup = set(), []
    for r in refs:
        if r["url"] and r["url"] not in seen:
            seen.add(r["url"]); dedup.append(r)
    return {"keyword": keyword, "triggered": True, "text": " ".join(text_parts).strip(),
            "references": dedup, "cited_domains": sorted({r["domain"] for r in dedup if r.get("domain")})}


def paa(serp_result):
    """People-Also-Ask questions from a serp() result."""
    out = []
    for blk in _items(serp_result, "people_also_ask"):
        for el in blk.get("items", []) or []:
            if el.get("title"):
                out.append(el["title"])
    return out


# ---------------- Keyword intelligence (DataForSEO Labs + Google Ads) ----------------
# All confirmed working on this account (2026-07-01). Labs covers ~94 locations; Nepal (2524) is not
# among them, so for Nepal-style markets fall back to keyword_volume (Google Ads) + serp_competitors.

def keyword_volume(keywords, location: int = 2840, language: str = "en"):
    """Google Ads monthly search volume + cpc + competition for exact keywords (any location)."""
    payload = [{"keywords": list(keywords), "location_code": location, "language_code": language}]
    r = result(post("keywords_data/google_ads/search_volume/live", payload))
    return [{"keyword": it.get("keyword"), "volume": it.get("search_volume"),
             "cpc": it.get("cpc"), "competition": it.get("competition")} for it in (r or [])]


def keyword_overview(keywords, location: int = 2840, language: str = "en"):
    """Volume + CPC + competition + KEYWORD DIFFICULTY + search intent for each keyword in ONE Labs call.
    This is the Ahrefs Keywords-Explorer-overview equivalent; DataForSEO now returns KD directly."""
    payload = [{"keywords": list(keywords), "location_code": location, "language_code": language}]
    r = result(post("dataforseo_labs/google/keyword_overview/live", payload))
    out = []
    for it in ((r[0].get("items") if r else []) or []):
        ki = it.get("keyword_info") or {}
        out.append({"keyword": it.get("keyword"),
                    "volume": ki.get("search_volume"), "cpc": ki.get("cpc"),
                    "competition": ki.get("competition_level"),
                    "kd": (it.get("keyword_properties") or {}).get("keyword_difficulty"),
                    "intent": (it.get("search_intent_info") or {}).get("main_intent")})
    return out


def keyword_difficulty(keywords, location: int = 2840, language: str = "en"):
    """Cheap bulk keyword difficulty (0-100) for many keywords at once. {keyword: kd}."""
    payload = [{"keywords": list(keywords), "location_code": location, "language_code": language}]
    r = result(post("dataforseo_labs/google/bulk_keyword_difficulty/live", payload))
    return {it.get("keyword"): it.get("keyword_difficulty") for it in ((r[0].get("items") if r else []) or [])}


def search_intent(keywords, language: str = "en"):
    """Main search intent (commercial / informational / navigational / transactional) per keyword."""
    payload = [{"keywords": list(keywords), "language_code": language}]
    r = result(post("dataforseo_labs/google/search_intent/live", payload))
    out = {}
    for it in ((r[0].get("items") if r else []) or []):
        out[it.get("keyword")] = (it.get("keyword_intent") or {}).get("label")
    return out


def keyword_metrics(keywords, location: int = 2840, language: str = "en"):
    """One row per keyword: volume/cpc/competition/KD/intent. Uses Labs keyword_overview where the
    location is supported, and falls back to Google Ads volume + intent for Labs-unsupported markets."""
    try:
        rows = {r["keyword"]: r for r in keyword_overview(keywords, location, language)}
        if rows:
            return [rows.get(k, {"keyword": k}) for k in keywords]
    except Exception:
        pass
    vol = {v["keyword"]: v for v in keyword_volume(keywords, location, language)}
    try:
        intent = search_intent(keywords, language)
    except Exception:
        intent = {}
    return [{"keyword": k, "volume": vol.get(k, {}).get("volume"), "cpc": vol.get(k, {}).get("cpc"),
             "competition": vol.get(k, {}).get("competition"), "kd": None,
             "intent": intent.get(k)} for k in keywords]


def keyword_ideas(seed, location: int = 2840, language: str = "en", limit: int = 100):
    """Expand a seed keyword into related keyword ideas with volume + KD (the expansion engine)."""
    payload = [{"keywords": [seed] if isinstance(seed, str) else list(seed),
                "location_code": location, "language_code": language, "limit": limit}]
    r = result(post("dataforseo_labs/google/keyword_ideas/live", payload))
    out = []
    for it in ((r[0].get("items") if r else []) or []):
        ki = it.get("keyword_info") or {}
        out.append({"keyword": it.get("keyword"), "volume": ki.get("search_volume"), "cpc": ki.get("cpc"),
                    "kd": (it.get("keyword_properties") or {}).get("keyword_difficulty")})
    return out


def ranked_keywords(target: str, location: int = 2840, language: str = "en", limit: int = 100):
    """Every keyword a domain/URL ranks for, ordered by volume (the Ahrefs organic-keywords equivalent).
    Returns {total, items:[{keyword, rank, volume, url}]}."""
    payload = [{"target": target, "location_code": location, "language_code": language, "limit": limit,
                "order_by": ["keyword_data.keyword_info.search_volume,desc"]}]
    r = result(post("dataforseo_labs/google/ranked_keywords/live", payload))
    r0 = (r[0] if r else {}) or {}
    items = []
    for it in r0.get("items", []) or []:
        kd = it.get("keyword_data") or {}
        ki = kd.get("keyword_info") or {}
        se = (it.get("ranked_serp_element") or {}).get("serp_item") or {}
        items.append({"keyword": kd.get("keyword"), "rank": se.get("rank_absolute"),
                      "volume": ki.get("search_volume"), "url": se.get("url")})
    return {"total": r0.get("total_count"), "items": items}


def domain_intersection(target1: str, target2: str, location: int = 2840, language: str = "en", limit: int = 100):
    """Keywords BOTH domains rank for, with each one's position (the competitor keyword-gap engine).
    Returns [{keyword, volume, rank1, rank2}] ordered by volume."""
    payload = [{"target1": target1, "target2": target2, "location_code": location, "language_code": language,
                "limit": limit, "order_by": ["keyword_data.keyword_info.search_volume,desc"]}]
    r = result(post("dataforseo_labs/google/domain_intersection/live", payload))
    out = []
    for it in ((r[0].get("items") if r else []) or []):
        kd = it.get("keyword_data") or {}
        ki = kd.get("keyword_info") or {}
        s1 = (it.get("first_domain_serp_element") or {}).get("serp_item") or {}
        s2 = (it.get("second_domain_serp_element") or {}).get("serp_item") or {}
        out.append({"keyword": kd.get("keyword"), "volume": ki.get("search_volume"),
                    "rank1": s1.get("rank_absolute"), "rank2": s2.get("rank_absolute")})
    return out


def competitors_domain(target: str, location: int = 2840, language: str = "en", limit: int = 20):
    """Domains that compete with `target` in organic search, with overlap metrics (Labs). Returns
    [{domain, avg_position, intersections, visibility}] ordered by how much they overlap."""
    payload = [{"target": target, "location_code": location, "language_code": language, "limit": limit}]
    r = result(post("dataforseo_labs/google/competitors_domain/live", payload))
    out = []
    for it in ((r[0].get("items") if r else []) or []):
        m = (it.get("full_domain_metrics") or {}).get("organic") or {}
        out.append({"domain": it.get("domain"), "avg_position": it.get("avg_position"),
                    "intersections": it.get("intersections"), "visibility": m.get("etv")})
    return out


def serp_competitors(keyword: str, location: int = 2840, language: str = "en", depth: int = 10):
    """Domains ranking for a keyword, derived from the live SERP (works in ANY location, incl. Nepal).
    Returns ordered [{rank, domain, url, title}]."""
    sr = serp(keyword, location, language, depth=depth)
    return [{"rank": it.get("rank_group"), "domain": it.get("domain"),
             "url": it.get("url"), "title": it.get("title")}
            for it in _items(sr, "organic")]


# ---------------- Domain intelligence (Labs + Domain Analytics) ----------------
def domain_rank_overview(target: str, location: int = 2840, language: str = "en"):
    """One-call 'digital presence at a glance': organic keyword count, estimated traffic (etv),
    traffic value, and position distribution (pos_1 / 2_3 / 4_10). Labs (US/India/UK... not Nepal)."""
    r = result(post("dataforseo_labs/google/domain_rank_overview/live",
                    [{"target": target, "location_code": location, "language_code": language}]))
    it = ((r[0].get("items") if r else []) or [{}])[0]
    m = ((it.get("metrics") or {}).get("organic")) or {}
    return {"target": target, "keywords": m.get("count"), "etv": m.get("etv"),
            "traffic_value": m.get("estimated_paid_traffic_cost"), "pos_1": m.get("pos_1"),
            "pos_2_3": m.get("pos_2_3"), "pos_4_10": m.get("pos_4_10"), "is_new": m.get("is_new")}


def bulk_traffic_estimation(targets, location: int = 2840, language: str = "en"):
    """Estimated organic traffic for up to 1000 domains in ONE call (rank the whole competitor set)."""
    r = result(post("dataforseo_labs/google/bulk_traffic_estimation/live",
                    [{"targets": list(targets), "location_code": location, "language_code": language}]))
    out = {}
    for it in ((r[0].get("items") if r else []) or []):
        out[it.get("target")] = ((it.get("metrics") or {}).get("organic") or {}).get("etv")
    return out


def top_pages(target: str, location: int = 2840, language: str = "en", limit: int = 10):
    """A domain's top pages by organic reach: WHAT CONTENT actually drives a competitor's traffic.
    Returns [{url, etv, keywords}] ordered by estimated traffic. Great for 'what competitors are winning'."""
    payload = [{"target": target, "location_code": location, "language_code": language, "limit": limit,
                "order_by": ["metrics.organic.etv,desc"]}]
    r = result(post("dataforseo_labs/google/relevant_pages/live", payload))
    out = []
    for it in ((r[0].get("items") if r else []) or []):
        m = ((it.get("metrics") or {}).get("organic")) or {}
        out.append({"url": it.get("page_address") or it.get("url"), "etv": m.get("etv"),
                    "keywords": m.get("count")})
    return out


def google_trends(keywords, location: int = 2840, time_range: str = "past_12_months"):
    """Google Trends interest-over-time for up to 5 keywords (branded-demand / share-of-search).
    Returns {keywords, dates, series:{kw:[values]}}. ~$0.01/call."""
    r = result(post("keywords_data/google_trends/explore/live",
                    [{"keywords": list(keywords), "location_code": location, "time_range": time_range}]))
    items = ((r[0].get("items") if r else []) or [])
    graph = next((i for i in items if i.get("type") == "google_trends_graph"), None)
    kws = list(keywords)
    series = {k: [] for k in kws}
    dates = []
    for pt in ((graph.get("data") if graph else []) or []):
        dates.append(pt.get("date_to"))
        vals = pt.get("values") or []
        for i, k in enumerate(kws):
            series[k].append(vals[i] if i < len(vals) and isinstance(vals[i], (int, float)) else 0)
    return {"keywords": kws, "dates": dates, "series": series}


def lighthouse(url: str, mobile: bool = True):
    """Google Lighthouse for a URL: lab Core Web Vitals + performance score. ~$0.005/call, works for ANY
    site (no Google API key). Returns {performance 0-100, lcp_ms, cls, tbt_ms, fcp_ms, si_ms, tti_ms}."""
    r = result(post("on_page/lighthouse/live/json", [{"url": url, "for_mobile": bool(mobile)}]))
    lh = (r[0] if r else {}) or {}
    aud = lh.get("audits") or {}
    def nv(k, dp=0):
        v = (aud.get(k) or {}).get("numericValue")
        return round(v, dp) if isinstance(v, (int, float)) else None
    perf = ((lh.get("categories") or {}).get("performance") or {}).get("score")
    return {"url": url, "performance": round(perf * 100) if isinstance(perf, (int, float)) else None,
            "lcp_ms": nv("largest-contentful-paint"), "cls": nv("cumulative-layout-shift", 3),
            "tbt_ms": nv("total-blocking-time"), "fcp_ms": nv("first-contentful-paint"),
            "si_ms": nv("speed-index"), "tti_ms": nv("interactive")}


def ads_advertisers(keyword: str, location: int = 2840, language: str = "en"):
    """Google Ads Transparency: verified advertisers matching a brand/keyword + their approx live ad
    count. Use to show 'who is running Google ads and how heavily'. ~$0.002/call.
    Returns [{advertiser_id, title, verified, ads_count}]."""
    r = result(post("serp/google/ads_advertisers/live/advanced",
                    [{"keyword": keyword, "location_code": location, "language_code": language}]))
    items = (r[0].get("items") if r else []) or []
    return [{"advertiser_id": it.get("advertiser_id"), "title": it.get("title"),
             "verified": it.get("verified"), "ads_count": it.get("approx_ads_count")}
            for it in items if it.get("type") == "ads_advertiser"]


def domain_technologies(target: str):
    """What a site runs: CMS, analytics, framework, host, ecommerce. Gates feasibility + qualifies leads."""
    r = result(post("domain_analytics/technologies/domain_technologies/live", [{"target": target}]))
    it = (r[0] if r else {}) or {}
    techs = it.get("technologies") or {}
    flat = []
    if isinstance(techs, dict):
        for group, cats in techs.items():
            if isinstance(cats, dict):
                for cat, names in cats.items():
                    flat += names if isinstance(names, list) else []
    return {"target": target, "technologies": sorted(set(flat)), "raw_groups": list(techs) if isinstance(techs, dict) else []}


# ---------------- Backlinks ----------------
def backlinks_summary(target: str):
    """Backlink profile summary (DataForSEO 'rank' ~ DR-equivalent, referring domains, backlinks)."""
    r = result(post("backlinks/summary/live", [{"target": target, "internal_list_limit": 10}]))
    return r[0] if r else None


def referring_domains(target: str, limit: int = 100):
    """The domains linking to `target`, ordered by their own rank. [{domain, rank, backlinks, ...}]."""
    payload = [{"target": target, "limit": limit, "order_by": ["rank,desc"]}]
    r = result(post("backlinks/referring_domains/live", payload))
    return (r[0].get("items") if r else []) or []


def backlinks_bulk_ranks(targets):
    """DataForSEO 'rank' (0-1000 DR-equivalent) for up to 1000 domains in ONE cheap call.
    Ideal for scoring a competitor list. Returns {target: rank}."""
    r = result(post("backlinks/bulk_ranks/live", [{"targets": list(targets)}]))
    return {it.get("target"): it.get("rank") for it in ((r[0].get("items") if r else []) or [])}


def backlinks_bulk_referring_domains(targets):
    """Referring-domain count for up to 1000 domains in one call. Returns {target: count}."""
    r = result(post("backlinks/bulk_referring_domains/live", [{"targets": list(targets)}]))
    return {it.get("target"): it.get("referring_domains") for it in ((r[0].get("items") if r else []) or [])}


def backlinks_bulk_backlinks(targets):
    """Total backlink count for up to 1000 domains in one call. Returns {target: count}."""
    r = result(post("backlinks/bulk_backlinks/live", [{"targets": list(targets)}]))
    return {it.get("target"): it.get("backlinks") for it in ((r[0].get("items") if r else []) or [])}


def backlinks_bulk_spam_score(targets):
    """Backlink spam/toxicity 0-100 for up to 1000 domains in one call (link-health badge)."""
    r = result(post("backlinks/bulk_spam_score/live", [{"targets": list(targets)}]))
    return {it.get("target"): it.get("spam_score") for it in ((r[0].get("items") if r else []) or [])}


def backlinks_competitors(target: str, limit: int = 20):
    """The true LINK-GRAPH competitor set: domains sharing the most referring domains with `target`.
    Often differs from the SERP competitor set. Returns [{domain, intersections, rank}]."""
    r = result(post("backlinks/competitors/live", [{"target": target, "limit": limit}]))
    return [{"domain": it.get("target"), "intersections": it.get("intersections"), "rank": it.get("rank")}
            for it in ((r[0].get("items") if r else []) or [])]


def backlinks_domain_intersection(targets, exclude=None, limit: int = 100):
    """Referring DOMAINS that link to `targets` but NOT to `exclude` (the link-prospect gap list).
    Each item nests per-target detail under domain_intersection["1"|"2"|...]; the referring domain is the
    inner `target` field and its authority is `rank` (0-1000). Returns [{domain, rank, spam, intersections}]
    with the best (highest-rank) slot per referring domain. Different endpoint from the Labs keyword gap."""
    payload = {"targets": {str(i + 1): t for i, t in enumerate(targets)}, "limit": limit}
    if exclude:
        payload["exclude_targets"] = list(exclude)
    r = result(post("backlinks/domain_intersection/live", [payload]))
    out = []
    for it in ((r[0].get("items") if r else []) or []):
        slots = [s for s in (it.get("domain_intersection") or {}).values() if isinstance(s, dict)]
        if not slots:
            continue
        best = max(slots, key=lambda s: s.get("rank") or 0)
        out.append({"domain": best.get("target"),
                    "rank": max((s.get("rank") or 0) for s in slots),
                    "spam": best.get("backlinks_spam_score"),
                    "intersections": (it.get("summary") or {}).get("intersections_count") or len(slots)})
    return out


# ---------------- Reputation: brand mentions + reviews + local ----------------
def content_analysis_summary(keyword: str):
    """Web-wide brand/keyword MENTION volume + net sentiment + top domains (reputation-monitoring read).
    Returns {total_mentions, sentiment, top_domains}."""
    r = result(post("content_analysis/summary/live", [{"keyword": keyword, "page_type": ["ecommerce", "news", "blogs"]}]))
    it = (r[0] if r else {}) or {}
    senti = it.get("sentiment_connotations") or {}
    return {"keyword": keyword, "total_mentions": it.get("total_count"),
            "rank": it.get("rank"), "sentiment": senti,
            "top_domains": [d.get("domain") for d in (it.get("top_domains") or [])][:10]}


def business_listings_search(categories, location_coordinate=None, title=None, limit: int = 20):
    """DataForSEO's own Google Maps DB: the local competitor set in a category (ratings, review counts,
    claimed status) with NO client input. location_coordinate = 'lat,lng,zoom'. No monthly commitment."""
    payload = {"categories": list(categories) if isinstance(categories, (list, tuple)) else [categories], "limit": limit}
    if location_coordinate:
        payload["location_coordinate"] = location_coordinate
    if title:
        payload["title"] = title
    r = result(post("business_data/business_listings/search/live", [payload]))
    return [{"title": it.get("title"), "rating": (it.get("rating") or {}).get("value"),
             "reviews": (it.get("rating") or {}).get("votes_count"), "category": it.get("category"),
             "domain": it.get("domain"), "claimed": it.get("is_claimed")}
            for it in ((r[0].get("items") if r else []) or [])]


def my_business_info(keyword: str, location: int = 2840, language: str = "en"):
    """Google Business Profile snapshot for a brand: rating, review count, category, attributes."""
    r = result(post("business_data/google/my_business_info/live",
                    [{"keyword": keyword, "location_code": location, "language_code": language}]))
    it = ((r[0].get("items") if r else []) or [{}])[0]
    rat = it.get("rating") or {}
    return {"title": it.get("title"), "rating": rat.get("value"), "reviews": rat.get("votes_count"),
            "category": it.get("category"), "domain": it.get("domain"), "claimed": it.get("is_claimed")}


def llm_mentions(keyword: str, limit: int = 50):
    """AI Share-of-Voice at scale: brand mention counts across LLM answers WITHOUT prompting per query.
    Complements llm_query (per-prompt). Note: $100/mo minimum (spendable on any DataForSEO API)."""
    r = result(post("ai_optimization/llm_mentions/search/live", [{"keyword": keyword, "limit": limit}]))
    it = (r[0] if r else {}) or {}
    return {"keyword": keyword, "total_mentions": it.get("total_count"),
            "items": (it.get("items") or [])[:limit]}


# ---------------- OnPage (technical crawl) ----------------
def onpage_instant(url: str):
    """Single-page technical read: status, load time, on-page checks, word count. Cheap ($0.00015)."""
    r = result(post("on_page/instant_pages", [{"url": url}]))
    it = ((r[0].get("items") if r else []) or [{}])[0]
    return {"url": it.get("url"), "status_code": it.get("status_code"),
            "checks": it.get("checks"), "meta": it.get("meta"),
            "page_timing": it.get("page_timing")}


# ---------------- AI Optimization: query real LLMs, capture answer + citations ----------------
# The live GEO-visibility engine: ask ChatGPT / Gemini / Perplexity / Claude a prompt and see what it
# answers and WHO it cites. This is what Ahrefs Brand Radar (aggregate) and a Perplexity-only probe
# cannot do at the per-prompt, cross-engine level. Confirmed 2026-07-01; Perplexity returns citations.
_LLM_DEFAULT_MODEL = {"chat_gpt": "gpt-4o-mini", "gemini": "gemini-2.5-flash",
                      "perplexity": "sonar", "claude": "claude-haiku-4-5"}
_LLM_ALIAS = {"chatgpt": "chat_gpt", "openai": "chat_gpt", "gpt": "chat_gpt"}


def llm_models(provider: str = "chat_gpt"):
    """List the models available for a provider (chat_gpt / gemini / perplexity / claude)."""
    provider = _LLM_ALIAS.get(provider, provider)
    r = result(get(f"ai_optimization/{provider}/llm_responses/models"))
    return r or []


def llm_query(prompt: str, provider: str = "perplexity", model: str = None, web_search: bool = True):
    """Ask a real LLM a prompt and return {provider, model, text, citations, cited_domains,
    fan_out_queries, cost}. `citations` are the sources the model used (present when web_search and the
    model supports it; Perplexity always cites). Use to test whether a brand shows up in AI answers."""
    provider = _LLM_ALIAS.get(provider, provider)
    model = model or _LLM_DEFAULT_MODEL.get(provider, "sonar")
    payload = [{"user_prompt": prompt, "model_name": model, "web_search": web_search}]
    r = result(post(f"ai_optimization/{provider}/llm_responses/live", payload))
    r0 = (r[0] if r else {}) or {}
    text_parts, cites = [], []
    for it in r0.get("items", []) or []:
        for sec in it.get("sections", []) or []:
            if sec.get("text"):
                text_parts.append(sec["text"])
            for a in sec.get("annotations") or []:
                url = a.get("url") if isinstance(a, dict) else None
                if url:
                    cites.append(url)
    from urllib.parse import urlparse
    domains = sorted({urlparse(u).netloc.replace("www.", "") for u in cites if u})
    return {"provider": provider, "model": r0.get("model_name") or model,
            "web_search": r0.get("web_search"), "text": " ".join(text_parts).strip(),
            "citations": cites, "cited_domains": domains,
            "fan_out_queries": r0.get("fan_out_queries"), "cost": r0.get("money_spent")}


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lib.config import load_secrets
    prof = load_secrets()
    print(f"profile={prof}  balance=${balance()}")
    if len(sys.argv) > 1:
        print(json.dumps(ai_overview(sys.argv[1], location=int(sys.argv[2]) if len(sys.argv) > 2 else 2840), indent=2))

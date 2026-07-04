"""First-scan "hook" report: a client-ready digital-presence teardown from one scan.

The hook that acquires the client: show their current digital footprint, what competitors are doing and
winning, where they are absent, where the real opportunity is, and the strategy to take it. It reads the
scan artifacts a project already has (authority, AI Share of Voice, keyword opportunity) and assembles a
report.yml the existing renderer turns into a branded PDF. The recipe stays internal; the client sees
the finding and the plan, not the method.

    # produce the inputs first (cheap):
    python tools/seo/authority.py        --project <slug> --out .../authority-<date>.json
    python tools/seo/keyword_research.py --project <slug> --topic ... --out .../kw-<date>.json
    python tools/geo/llm_visibility.py   --project <slug> --out .../llm-visibility-<date>.json
    # then assemble + render:
    python tools/report/first_scan.py    --project <slug> --render

Every section is optional: if an input artifact is missing, its section is skipped, so a partial scan
still yields a coherent report. Numbers are DataForSEO/Ahrefs reads; label them as such to the client.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.config import load          # noqa: E402
from geo import sov as SOV           # noqa: E402

ORD = {1: "1st", 2: "2nd", 3: "3rd"}


def _ord(n):
    return ORD.get(n, f"{n}th")


def _latest(project_dir, pattern):
    files = sorted(Path(project_dir).glob(pattern))
    return files[-1] if files else None


def _root(domain):
    return (domain or "").lower().replace("www.", "").split("/")[0].split(".")[0]


def _norm_domain(x):
    return (x or "").lower().replace("https://", "").replace("http://", "").replace("www.", "").strip("/ ").split("/")[0]


def _client_name(cfg):
    return cfg.get("client_name") or cfg.get("client") or cfg.get("name") or _root(cfg.get("domain")).title()


def _comp_names(cfg):
    """domain-root -> display name from client.yml competitors."""
    m = {}
    for c in (cfg.get("competitors", []) or []):
        if isinstance(c, dict) and c.get("domain"):
            m[_root(c["domain"])] = c.get("name") or _root(c["domain"]).title()
    return m


# --------------------------------------------------------------------- sections
def authority_section(num, cfg, project_dir):
    data = None
    for f in reversed(sorted(project_dir.glob("data/raw/**/authority-*.json"))):
        d = json.loads(f.read_text())
        if d.get("rows"):
            data = d; break
    if not data:
        return None, None
    names = _comp_names(cfg)
    client = _norm_domain(cfg.get("domain"))
    names[_root(client)] = _client_name(cfg)          # client uses its display name
    disp = lambda dom: names.get(_root(dom), _root(dom).title())
    rows = [r for r in data["rows"] if isinstance(r.get("consensus"), (int, float))]
    if not rows:
        return None, None
    chart_rows = [[disp(r["domain"]), round(r["consensus"])] for r in rows]
    # client rank
    ranked = [_norm_domain(r["domain"]) for r in rows]
    crank = ranked.index(client) + 1 if client in ranked else None
    leader = rows[0]
    cval = next((round(r["consensus"]) for r in rows if _norm_domain(r["domain"]) == client), None)
    headline = None
    if crank and cval is not None:
        headline = (f"**Authority: you sit {_ord(crank)} of {len(rows)}** in the category "
                    f"(authority {cval} vs the leader {disp(leader['domain'])} "
                    f"at {round(leader['consensus'])}). Authority here is a cross-source consensus "
                    f"({', '.join(data.get('active_sources', []))}).")
    sec = {
        "type": "prose", "num": num, "title": "Authority: how you stack up",
        "paragraphs": ["Domain authority estimates how much trust a site has earned. We read it from "
                       "several independent sources and take the consensus, so no single tool's quirk "
                       "drives the picture. Taller is stronger."],
        "figure_title": "Cross-source domain authority (0-100)",
        "figure_unit": f"consensus of {len(data.get('active_sources', []))} sources, {data.get('date','')}",
        "chart": {"type": "bar_h", "kind": "compact", "highlight": _client_name(cfg),
                  "rows": chart_rows},
        "figure_note": "Authority is earned mostly through other reputable sites linking to you. "
                       "It is a proxy, not a Google metric, but it tracks how hard a domain is to outrank.",
    }
    return sec, headline


def _poss(name):
    """Possessive that reads right for names ending in s (Acme Holdings' not Holdings's)."""
    name = name or ""
    return name + ("'" if name.endswith(("s", "S")) else "'s")


def backlinks_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/dataforseo/backlinks-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    client = _client_name(cfg)
    profiles = data.get("profiles") or {}
    rows = [[n, p.get("referring_domains")] for n, p in profiles.items()
            if isinstance(p.get("referring_domains"), (int, float))]
    if len(rows) < 3:
        return None, None
    rows = sorted(rows, key=lambda x: -x[1])
    order = [n for n, _ in rows]
    crank = order.index(client) + 1 if client in order else None
    cval = next((v for n, v in rows if n == client), None)
    lead_n, lead_v = rows[0]
    cspam = (profiles.get(client) or {}).get("spam_score")
    bullets = []
    if cval is not None and crank:
        bullets.append(
            f"Links from other websites are still the strongest off-page ranking signal and a direct "
            f"input to the authority that wins both search and AI citations. {client} has {cval:,} "
            f"referring domains, {_ord(crank)} of {len(rows)} in this set; {lead_n} has {lead_v:,}.")
    # Earned-press strength: name any tier-1 media/authority domains the client already holds links from.
    PRESS = {"time.com": "TIME", "forbes.com": "Forbes", "cntraveler.com": "Condé Nast Traveler",
             "nytimes.com": "The New York Times", "nationalgeographic.com": "National Geographic",
             "theguardian.com": "The Guardian", "bbc.com": "BBC", "bbc.co.uk": "BBC",
             "lonelyplanet.com": "Lonely Planet", "travelandleisure.com": "Travel + Leisure",
             "cnn.com": "CNN", "washingtonpost.com": "The Washington Post"}
    held = []
    for r in (data.get("client_top_refs") or []):
        dom = (r.get("domain") or "").replace("www.", "")
        for k, label in PRESS.items():
            if dom == k or dom.endswith("." + k):
                if label not in held:
                    held.append(label)
    if held:
        names = held[:4]
        joined = (", ".join(names[:-1]) + " and " + names[-1]) if len(names) > 1 else names[0]
        bullets.append(
            f"The quality of your links is the real asset: {client} already holds links from {joined}, "
            f"tier-1 authority most competitors cannot buy. The gap is not credibility, it is volume of "
            f"relevant links. Turn that press equity into a wider set of citable pages and travel-media coverage.")
    # Quality caveat: is the leaders' volume lead inflated by low-quality links? (spam-score read)
    lead_spam = (profiles.get(lead_n) or {}).get("spam_score")
    if isinstance(lead_spam, (int, float)) and isinstance(cspam, (int, float)) and lead_spam >= cspam + 6:
        bullets.append(
            f"Volume is not the whole story. {_poss(lead_n)} link profile carries a {lead_spam}/100 spam "
            f"score versus {_poss(client)} {cspam}/100, so a large share of that lead is low-quality "
            f"directory and link-farm links, not editorial coverage. The goal is quality links, not the count.")
    gap_from = ", ".join(data.get("gap_targets_from") or []) or "the leaders"
    quality = data.get("gap_quality") or []
    if quality:
        n = len(quality)
        top = [(g.get("domain") or "").replace("www.", "") for g in quality[:3] if g.get("domain")]
        noun = "is a real, relevant site" if n == 1 else f"{n} are real, relevant sites"
        subj = "One" if n == 1 else ""
        bullets.append(
            (f"We pulled the domains that link to {gap_from} but not to {client}. {subj} {noun} worth "
             f"pursuing").replace("  ", " ")
            + (f" (for example {', '.join(top)})" if top else "") + ", and the full vetted list is handed "
            f"off as a ready outreach target set. Every one it converts closes the gap above.")
    else:
        bullets.append(
            f"We checked the specific domains the leaders link from that {client} does not have, and almost "
            f"all are low-quality directories, not editorial sites, so there is no clean list to copy. The "
            f"winnable move is quality over volume: relevant industry and association directories, supplier "
            f"and marketplace profiles, local and trade press, and case-study or partner mentions from the "
            f"customers you already serve.")
    if isinstance(cspam, (int, float)) and cspam >= 25:
        bullets.append(f"One caution: {_poss(client)} own backlink profile shows an elevated spam score "
                       f"({cspam}/100). A link audit and disavow pass should come before new link building.")
    if not bullets:
        return None, None
    sec = {"type": "scenarios", "num": num, "title": "Backlinks: the authority gap and how to close it",
           "bullets": bullets,
           "figure_title": "Referring domains by company", "figure_unit": "unique linking domains",
           "chart": {"type": "bar_h", "kind": "compact", "highlight": client, "rows": rows},
           "figure_note": "Referring domains count unique websites linking to each domain, the clearest "
                          "measure of earned authority. The gap list is a concrete, handoff-ready target set."}
    return sec, None


def press_section(num, cfg, project_dir):
    """Credibility the client already owns (press + awards), and whether it converts to a link. Only
    renders when client.yml lists `press:`. Data-driven: cross-checks each outlet against the live
    backlink data, so it never claims a link the backlink index does not show."""
    press = [p for p in (cfg.get("press") or []) if isinstance(p, dict) and p.get("outlet")]
    if not press:
        return None, None
    client = _client_name(cfg)
    # which press outlets actually link (present in the client's referring domains)?
    refdoms = []
    j = _latest(project_dir, "data/raw/dataforseo/backlinks-*.json")
    if j:
        refdoms = [(r.get("domain") or "").replace("www.", "")
                   for r in (json.loads(j.read_text()).get("client_top_refs") or [])]

    seen, uniq, linked = set(), [], 0
    for p in press:
        o = p["outlet"]
        if o.lower() in seen:
            continue
        seen.add(o.lower()); uniq.append(o)
        dom = (p.get("domain") or "").replace("www.", "").lower()
        if dom and any(dom == rd or rd.endswith("." + dom) or dom.endswith("." + rd) for rd in refdoms if rd):
            linked += 1
    named = (", ".join(uniq[:-1]) + " and " + uniq[-1]) if len(uniq) > 1 else uniq[0]
    paras = [f"{client} owns something no competitor in this set can buy: tier-1 press. It has been "
             f"featured in {named}. For an unknown luxury camp in a remote park, this is the single most "
             f"powerful top-of-funnel asset, the first touch that turns a stranger into a brand searcher."]
    if linked == 0:
        paras.append("Here is the gap, and the opportunity. None of these features currently pass a "
                     "measurable link to your site, so the search and AI-citation value is still on the "
                     "table. Two moves capture it: get the features to link, and build award-anchored, "
                     "answer-first pages you control so that when a traveler asks an AI for the best lodge "
                     "in Nepal, the machine repeats your credentials back in the answer.")
    else:
        paras.append(f"{linked} of these features link to you, passing real authority. The next move is to "
                     "turn each into an award-anchored, answer-first page you control, so AI engines repeat "
                     "your credentials when travelers ask for the best lodge in Nepal.")
    sec = {"type": "prose", "num": num, "title": "Press and awards: credibility you already own",
           "paragraphs": paras}
    return sec, None


def sov_section(num, cfg, project_dir):
    scan_f = (_latest(project_dir, "data/raw/**/llm-visibility-*.json")
              or _latest(project_dir, "data/raw/**/ai-matrix-*.json")
              or _latest(project_dir, "data/raw/llm-visibility-*.json"))
    if not scan_f:
        return None, None
    scan = json.loads(scan_f.read_text())
    ps_f = project_dir / "data" / "prompt-set.json"
    weights = {}
    if ps_f.exists():
        weights = {p["prompt"]: p.get("volume") for p in json.loads(ps_f.read_text()).get("prompts", [])}
    client_label = _client_name(cfg)
    res = SOV.compute(scan, weights, client_label)
    chart_rows = [[b, res["sov"][b]["blended"]] for b in res["brands"] if res["sov"][b]["blended"] > 0]
    if not chart_rows:
        chart_rows = [[b, res["sov"][b]["blended"]] for b in res["brands"][:6]]
    cblended = res["sov"].get(client_label, {}).get("blended", 0)
    leader = res["brands"][0]
    lead_val = res["sov"][leader]["blended"]
    present_engines = [e for e, v in res["client_present_rate"].items() if v > 0]
    headline = (f"**AI visibility: you hold {cblended}% share of voice** across {len(res['engines'])} AI "
                f"engines on {res['n_prompts']} real queries; {leader} holds {lead_val}%. You appear in "
                f"{len(present_engines)} of {len(res['engines'])} engines"
                + (f" ({', '.join(present_engines)})" if present_engines else "")
                + ". When someone asks an AI in your category, this is who it names.")
    sec = {
        "type": "prose", "num": num, "title": "AI visibility: is AI recommending you?",
        "paragraphs": ["More buyers now ask ChatGPT, Gemini, Perplexity, Claude, and Google's AI Overview "
                       "for recommendations instead of scrolling search results. Share of Voice is how "
                       "often each brand is named or cited across those engines, weighted by how much "
                       "people search each query. This is who the models put in front of your buyers."],
        "figure_title": "AI Share of Voice (% of brand mentions across engines)",
        "figure_unit": f"{res['n_prompts']} queries x {len(res['engines'])} engines",
        "chart": {"type": "bar_h", "kind": "compact", "highlight": client_label, "rows": chart_rows},
        "figure_note": "Scope is your tracked demand set. A single scan is a sample; the value is the "
                       "trend as we move you up it.",
    }
    return sec, headline


def keyword_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/**/kw-*.json") or _latest(project_dir, "data/raw/kw-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    targets = [t for t in data.get("targets", []) if (t.get("volume") or 0) > 0][:6]
    gap = data.get("content_gap", [])[:6]
    rows = []
    for t in targets:
        kd = t.get("kd")
        rows.append([t.get("keyword"), f"{t.get('volume') or 0:,}", (f"{kd}" if kd is not None else "-"),
                     (t.get("intent") or "").title()])
    top = targets[0] if targets else None
    headline = None
    if top:
        headline = (f"**The opportunity is real demand you are not yet capturing.** "
                    f"'{top.get('keyword')}' alone is {top.get('volume'):,} searches/mo"
                    + (f", and rivals already rank for {len(data.get('content_gap', []))} terms you do not."
                       if gap else "."))
    sec = {"type": "scenarios", "num": num, "title": "Search demand and where the gap is",
           "bullets": ["These are the highest-intent queries in your market with real monthly demand. "
                       "Volume is what people search; difficulty (KD) is how contested it is."],
           "figure_title": "", "table": {"headers": ["Query", "Searches/mo", "Difficulty", "Intent"],
                                          "rows": rows, "align": ["left", "right", "right", "left"]}}
    if gap:
        sec["note"] = ("Competitors already rank for: "
                       + ", ".join(f"{g.get('keyword')} ({g.get('volume') or 0:,}/mo, {g.get('held_by')})"
                                   for g in gap[:5]) + " - demand they capture and you do not, yet.")
    return sec, headline


def steal_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/**/competitor-gap-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    t = data["totals"]
    ov = data.get("overviews", {})
    names = _comp_names(cfg)
    client = _norm_domain(cfg.get("domain"))
    names[_root(client)] = _client_name(cfg)
    disp = lambda dom: names.get(_root(dom), _root(dom).title())
    etv_rows = sorted([[disp(dom), round(o.get("etv") or 0)] for dom, o in ov.items()
                       if isinstance(o.get("etv"), (int, float))], key=lambda r: -r[1])[:8]
    steal_rows = [[s["keyword"], f"{s.get('volume') or 0:,}", s.get("held_by")]
                  for s in data.get("steal_list", [])[:12]]
    compv, cetv = t.get("competitor_traffic_value_total", 0), t.get("competitor_etv_total", 0)
    cli = t.get("client_etv", 0)
    steal_count, steal_vol = t.get("steal_count", 0), t.get("steal_volume", 0)
    if not compv and not cetv:
        return None, None
    # When the client is a small niche player against much larger rivals, their TOTAL traffic value is
    # not the addressable opportunity (a giant's $500M/mo is not a niche player's opening). Lead with the keyword gap.
    niche = cetv > 300 * max(cli, 1)
    if niche and steal_count:
        headline = (f"**Rivals rank for {steal_count} buyer keywords, about {steal_vol:,} searches/mo, that "
                    f"you are absent from.** That gap in your niche, not their global traffic, is the "
                    f"addressable opening.")
        bullets = [f"The leaders are far larger overall, so the game is not matching their total traffic. It "
                   f"is the {steal_count} commercial terms in your niche they rank for and you do not, about "
                   f"{steal_vol:,} searches a month of demand that already converts for them.",
                   "Winning even a handful of these niche terms is realistic and compounds, where chasing "
                   "the incumbents' head terms would not."]
    else:
        steal_note = f" {steal_count} buyer keywords they rank for and you do not." if steal_count else ""
        headline = (f"**You are leaving about ${compv:,}/mo of organic traffic value on the table.** "
                    f"Competitors capture ~{cetv:,} visits/mo; you capture ~{cli:,}.{steal_note}")
        bullets = [f"Competitors in your set capture an estimated {cetv:,} organic visits/mo, worth about "
                   f"${compv:,} if bought as ads. Your site captures about {cli:,}."]
        if steal_count:
            bullets.append(f"They rank for {steal_count} commercial keywords you are absent from, roughly "
                           f"{steal_vol:,} searches every month.")
        bullets.append("This is the size of the opening: demand that already exists and already converts for "
                       "someone else.")
    sec = {"type": "scenarios", "num": num, "title": "The traffic and revenue you are not capturing",
           "bullets": bullets, "note": "Traffic and value are directional estimates from live search data."}
    # only add the traffic bar if the dedicated traffic-share section is not already showing it
    if not _latest(project_dir, "data/raw/dataforseo/traffic-*.json") and etv_rows:
        sec["figure_title"] = "Estimated organic traffic by company"
        sec["figure_unit"] = "visits/mo, live data"
        sec["chart"] = {"type": "bar_h", "kind": "compact", "highlight": _client_name(cfg), "rows": etv_rows}
    if steal_rows:
        sec["table"] = {"headers": ["Keyword competitors rank for", "Searches/mo", "Held by"],
                        "rows": steal_rows, "align": ["left", "right", "left"]}
    return sec, headline


def greenfield_section(num, cfg, project_dir):
    j = project_dir / "data" / "opportunity-scored.json"
    if not j.exists():
        return None, None
    data = json.loads(j.read_text())
    pts, gf, c = data.get("points", []), data.get("greenfield", []), data.get("counts", {})
    if not pts:
        return None, None
    gf_rows = [[s["keyword"], f"{s.get('volume') or 0:,}", (f"{s['kd']}" if s.get("kd") is not None else "-"),
                s["tier"].title()] for s in gf[:10]]
    gfn = c.get("greenfield", 0)
    if gfn == 1:
        headline = ("**1 greenfield opportunity**: real buyer demand, winnable difficulty, and no competitor "
                    "has locked in the AI answer. In a niche corridor that single open term is where to start.")
    else:
        headline = (f"**{gfn} greenfield opportunities**: real buyer demand, winnable difficulty, and no "
                    f"competitor has locked in the AI answer. This is where to attack first.")
    sec = {"type": "scenarios", "num": num, "title": "Greenfield opportunity map",
           "bullets": ["Each bubble is a buyer query. Right means winnable (lower difficulty), up means more "
                       "demand, bigger means more searches. The green zone (top-right) is open demand you can "
                       "take without fighting the giants head-on.",
                       f"Greenfield {c.get('greenfield', 0)}  |  Winnable niche {c.get('contested', 0)}  |  "
                       f"Fortress, hard {c.get('fortress', 0)}."],
           "figure_title": "Demand vs winnability", "figure_unit": "buyer queries, live data",
           "chart": {"type": "bubble", "points": pts, "x_label": "WINNABILITY", "y_label": "DEMAND"},
           "table": {"headers": ["Greenfield query", "Searches/mo", "Difficulty", "Lane"],
                     "rows": gf_rows, "align": ["left", "right", "right", "left"]}}
    return sec, headline


_ENG_LABEL = {"google_aio": "AI Overview", "perplexity": "Perplexity", "chatgpt": "ChatGPT",
              "gemini": "Gemini", "claude": "Claude"}


def ai_matrix_section(num, cfg, project_dir):
    scan_f = _latest(project_dir, "data/raw/**/ai-matrix-*.json")
    if not scan_f:
        return None, None
    scan = json.loads(scan_f.read_text())
    rows = scan.get("rows", [])
    engines = scan.get("engines") or sorted({r["engine"] for r in rows})
    prompts, seen = [], set()
    for r in rows:
        if r["prompt"] not in seen:
            seen.add(r["prompt"]); prompts.append(r["prompt"])
    idx = {(r["prompt"], r["engine"]): r for r in rows}
    cells, present, total = [], 0, 0
    for p in prompts:
        row = []
        for e in engines:
            r = idx.get((p, e), {})
            total += 1
            if r.get("brand_cited"):
                st = "cited"; present += 1
            elif r.get("brand_mentioned"):
                st = "named"; present += 1
            elif r.get("competitors_present"):
                st = "competitor"
            else:
                st = "absent"
            row.append(st)
        cells.append(row)
    eng_labels = [_ENG_LABEL.get(e, e) for e in engines]
    short = [(p[:44] + "…") if len(p) > 45 else p for p in prompts]
    headline = (f"**In AI answers to buyer questions, you appear in {present} of {total} places.** "
                f"Competitors own the rest. This is the shortlist your buyers now ask AI for first.")
    sec = {"type": "scenarios", "num": num, "title": "AI visibility matrix: who AI recommends",
           "bullets": ["Buyers increasingly ask AI engines for a vendor shortlist. This maps each buyer "
                       "question against each engine: are you cited, named, or absent while a competitor "
                       "is named instead."],
           "figure_title": "",
           "chart": {"type": "heatmap", "row_labels": short, "col_labels": eng_labels, "cells": cells}}
    return sec, headline


def competitor_winning_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/**/top-pages-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    rows = []
    for name, v in data.items():
        for pg in (v.get("pages") or [])[:3]:
            url = pg.get("url") or ""
            path = "/" + url.split("/", 3)[-1] if url.count("/") >= 3 else url
            rows.append([name, (path[:50] + "…") if len(path) > 51 else path, f"{round(pg.get('etv') or 0):,}"])
    if not rows:
        return None, None
    # Data-driven note: are the winning pages education/blog content or product/category pages?
    guide_tokens = ("blog", "guide", "insight", "resource", "idea", "knowledge", "learn", "article",
                    "news", "/decoder", "glossary", "tips", "how-to", "faq", "things-to", "best-", "food")
    urls = [pg.get("url", "").lower() for v in data.values() for pg in (v.get("pages") or [])[:3]]
    guides = sum(1 for u in urls if any(t in u for t in guide_tokens))
    # the single highest-traffic page that is editorial content, if any leader runs a content play
    guide_pages = [(name, pg) for name, v in data.items() for pg in (v.get("pages") or [])[:3]
                   if any(t in (pg.get("url", "").lower()) for t in guide_tokens)]
    if urls and guides >= max(2, len(urls) // 2):
        note = ("Their traffic leaders are editorial content (guides, articles, blog), not just their own "
                "pages. The winnable move is to out-teach them on the specific buyer questions in your "
                "lanes so you earn the click before the comparison starts.")
    else:
        note = ("Their traffic leaders are mostly their own home and category pages, built around what "
                "buyers search. The winnable move is to build the pages you are missing and out-structure "
                "theirs, so you rank for the terms that matter.")
        if guide_pages:
            top_guide = max(guide_pages, key=lambda x: x[1].get("etv") or 0)[0]
            note += (f" Notably, {top_guide}'s single biggest page is an editorial post, not a room page: "
                     f"content marketing most of the field ignores and you can win.")
    sec = {"type": "table", "num": num, "title": "What competitors are winning with",
           "table": {"headers": ["Competitor", "Top-traffic page", "Est. visits/mo"],
                     "rows": rows[:12], "align": ["left", "left", "right"]},
           "note": note}
    return sec, None


def traffic_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/dataforseo/traffic-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    client = _client_name(cfg)
    rows = [[r["company"], r["etv"]] for r in data.get("rows", []) if r.get("etv")]
    if len(rows) < 3:
        return None, None
    headline = (f"**You are about {data['client_share_pct']}% of your category's traffic; "
                f"{data['leader']} is {data['leader_share_pct']}%.** Organic share is winnable and far "
                f"cheaper to take than paid.")
    sec = {"type": "scenarios", "num": num, "title": "Traffic share: how much of the category you own",
           "bullets": ["This is estimated organic traffic, a directional share read. It reframes the "
                       "authority gap as a market-share story: who owns the category's attention today, "
                       "and how much is still open to take."],
           "figure_title": "Estimated organic traffic by company", "figure_unit": "visits/mo, estimate",
           "chart": {"type": "bar_h", "kind": "compact", "highlight": client, "rows": rows},
           "note": "Organic share is earned with content and proof, not ad spend, so a focused team can "
                   "take it without out-spending the field."}
    return sec, headline


def share_of_search_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/dataforseo/share-of-search-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    client = _client_name(cfg)
    rows = [[r["name"], r["share_pct"]] for r in data.get("rows", [])]
    if len(rows) < 3:
        return None, None
    rising = [r["name"] for r in data["rows"] if r.get("trend") == "rising"]
    cr = next((r for r in data["rows"] if r["name"] == client), None)
    ctrend = cr["trend"] if cr else "flat"
    headline = (f"**You hold about {data['client_share_pct']}% of branded search in your set, and it is "
                f"{ctrend}.** Share of search is a leading indicator of market share, so this is the demand "
                f"you are building before it converts.")
    sec = {"type": "scenarios", "num": num, "title": "Share of search: branded demand momentum",
           "bullets": ["Branded search interest predicts market share up to a year ahead. This is who "
                       "buyers are actively looking for by name today.",
                       f"Rising in the set: {', '.join(rising) or 'no one clearly'}."],
           "figure_title": "Share of branded search", "figure_unit": "past 12 months",
           "chart": {"type": "bar_h", "kind": "compact", "highlight": client, "rows": rows},
           "note": "Branded search on common-word names can include namesakes, so treat as directional. "
                   "Growing branded demand is the compounding defense behind every other play."}
    return sec, headline


def _m(v):
    if not v:
        return "$0"
    return f"${v/1e9:.1f}B" if v >= 1e9 else f"${v/1e6:.0f}M"


def momentum_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/predictleads/momentum-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    comps = data.get("companies", {})
    client = _client_name(cfg)
    roles_rows = sorted([[n, o.get("open_roles") or 0] for n, o in comps.items()], key=lambda x: -x[1])
    fd = data.get("field_depts", {})
    total = data.get("total_field_roles") or sum(fd.values())
    fin, eng, sal = fd.get("Finance", 0), fd.get("Engineering", 0), fd.get("Sales/GTM", 0)
    rounds = [(n, (o.get("latest_round") or {}).get("amount"), (o.get("latest_round") or {}).get("type"),
               (o.get("latest_round") or {}).get("date")) for n, o in comps.items()
              if (o.get("latest_round") or {}).get("amount")]
    rounds.sort(key=lambda r: -(r[1] or 0))
    big = "; ".join(f"{n} raised {_m(a)} ({(t or '').replace('_',' ')}, {dt})" for n, a, t, dt in rounds[:3])
    headline = (f"**The field is scaling fast, and the hiring shows where.** Your rivals have "
                f"{total} open roles right now, concentrated in engineering ({eng}) and sales ({sal}). "
                f"Where they are not hiring is where the open ground is.")
    sec = {"type": "scenarios", "num": num, "title": "Where rivals are spending and hiring",
           "bullets": [(f"Recent funding: {big}. Funded rivals spend on the lanes they hire for, which is "
                        f"why those are the hardest to enter head-on." if big else
                        f"Public funding records show no major recent rounds in this set, so nobody has a "
                        f"war chest advantage: execution decides this market."),
                       f"Hiring shows the same story: {total} open roles across your rivals, "
                       f"{eng} in engineering and {sal} in sales/GTM."],
           "figure_title": "Open roles by company", "figure_unit": "public hiring records",
           "chart": {"type": "bar_h", "kind": "compact", "highlight": client, "rows": roles_rows},
           "note": "Where the money and hiring are absent is where the open ground is."}
    return sec, headline


def google_ads_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/dataforseo/google-ads-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    client = _client_name(cfg)
    rows = [[n, o.get("ads_count") or 0] for n, o in data.items()
            if o.get("confidence") == "high" or n == client]
    if client not in [r[0] for r in rows]:
        rows.append([client, 0])
    rows = sorted(rows, key=lambda x: -x[1])
    if len([r for r in rows if r[1] > 0]) < 2:
        return None, None
    lead = rows[0]
    bullets = [f"Google's Ads Transparency Center shows {lead[0]} running about {lead[1]} live ads. "
               f"{client} runs {dict((r[0], r[1]) for r in rows).get(client, 0)}. Every rival's live ads "
               f"are viewable in Google's public Ads Transparency Center.",
               "This is not a call to match their spend. It shows the field is buying attention while you "
               "are not, so paid is a selective lever once your proof pages exist to convert it."]
    amj = _latest(project_dir, "data/raw/openrouter/ad-messaging-*.json")
    if amj:
        am = json.loads(amj.read_text())
        msg = [f"{n} leads with '{d.get('main_message')}'" for n, d in am.items()
               if d.get("main_message") and "does not appear" not in str(d.get("main_message")).lower()]
        if msg:
            bullets.append("What some rivals say in their ads: " + "; ".join(msg[:3]) + ".")
    sec = {"type": "scenarios", "num": num, "title": "Where the field is buying attention: Google ads",
           "bullets": bullets,
           "figure_title": "Live Google ads by company", "figure_unit": "Ads Transparency, high-confidence matches",
           "chart": {"type": "bar_h", "kind": "compact", "highlight": client, "rows": rows},
           "figure_note": "Only advertisers matched with high confidence are shown; ambiguous single-name matches are excluded."}
    return sec, None


def social_section(num, cfg, project_dir):
    j = project_dir / "data" / "social-footprint.json"
    if not j.exists():
        return None, None
    blob = json.loads(j.read_text())
    rows = blob.get("rows") or []
    # Channel is data-driven: B2B defaults to LinkedIn, consumer/travel brands set channel="Instagram".
    channel = blob.get("channel") or "LinkedIn"
    fol = {}
    for r in rows:
        f = r.get("followers") or r.get("follower_count") or r.get("linkedin_followers") or r.get("instagram_followers")
        if isinstance(f, (int, float)) and r.get("name"):
            fol[r["name"]] = int(f)
    if len(fol) < 3:
        return None, None
    client = _client_name(cfg)
    chart = sorted([[n, v] for n, v in fol.items()], key=lambda x: -x[1])
    cval = fol.get(client)
    lead = chart[0]
    rank = next((i + 1 for i, (n, _) in enumerate(chart) if n == client), None)
    headline, competitive = None, False
    if cval is not None and rank:
        # competitive = in the top half AND holding at least half the leader's following
        competitive = rank <= (len(chart) + 1) // 2 and cval >= 0.5 * lead[1]
        if competitive:
            headline = (f"**Your social following is competitive: {client} is {_ord(rank)} of {len(chart)} on "
                        f"{channel} ({cval:,}).** The gap is not reach, it is turning that audience into "
                        f"bookings and AI visibility.")
        else:
            headline = (f"**Your social reach trails the field.** {client} has about {cval:,} {channel} "
                        f"followers; {lead[0]} has {lead[1]:,}. This is a low-cost channel to close.")
    if channel == "Instagram":
        intro = ("Instagram is where design-forward consumer brands get discovered and where a photogenic "
                 "product seeds the branded searches that convert. This is the aspirational front door "
                 "before anyone buys.")
        lead_bullet = ("Your reach here is solid; the opportunity is converting followers into reviews, "
                       "branded search, and the AI citations that win the shortlist." if competitive else
                       "This is a low-cost, high-leverage channel where you are currently underweight.")
    else:
        intro = ("LinkedIn is one of the most-cited sources in AI answers and a proven channel for this "
                 "category. This is where buyers research and where presence compounds into visibility.")
        lead_bullet = ("Your reach here is solid; the opportunity is converting followers into the content "
                       "and citations that win search and AI answers." if competitive else
                       "This is a low-cost, high-leverage channel where you are currently underweight.")
    sec = {"type": "scenarios", "num": num, "title": "Social presence",
           "bullets": [intro, lead_bullet],
           "figure_title": f"{channel} followers", "figure_unit": "public profiles",
           "chart": {"type": "bar_h", "kind": "compact", "highlight": client, "rows": chart},
           "note": f"{channel} reach compounds quickly for this category. This is a low-cost, high-leverage channel to own."}
    return sec, headline


def reputation_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/openrouter/reputation-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    rated = [(n, d) for n, d in data.items() if d.get("rating")]
    if len(rated) < 3:
        return None, None
    client = _client_name(cfg)
    # Only show the complaint column if at least one verified complaint survived cleaning; an all-"-"
    # column reads like we found nothing. When present, the ratings + review-volume story carries it.
    def _comp(d):
        c = [x for x in (d.get("top_complaints") or []) if x and str(x).strip() not in ("-", "")]
        return c[0][:62] if c else ""
    has_comp = any(_comp(d) for n, d in data.items() if not d.get("error"))
    rows = []
    for name, d in data.items():
        if d.get("error") or not d.get("rating"):
            continue  # skip rows we could not verify a rating for (avoids implying a rival has none)
        r, rc = d.get("rating"), d.get("review_count")
        row = [name, f"{r} stars", str(rc) if rc else "-"]
        if has_comp:
            row.append(_comp(d) or "-")
        rows.append(row)
    # Is the client itself far behind on review VOLUME? For a local/SMB brand that is often the real
    # wedge: a strong star rating on almost no reviews is thin social proof in local + AI search.
    lead = ""
    cd = data.get(client) or {}
    crc = cd.get("review_count") if isinstance(cd.get("review_count"), int) else None
    vol = [(n, d.get("review_count")) for n, d in data.items()
           if isinstance(d.get("review_count"), int) and n != client]
    if crc is not None and vol:
        top_n, top_v = max(vol, key=lambda x: x[1])
        if top_v >= 50 and crc < top_v * 0.25:
            cr = cd.get("rating")
            lead = (f"{client} shows a {cr}-star rating on just {crc:,} public reviews; {top_n} has "
                    f"{top_v:,}. In local and AI search, review volume is the social proof that gets you "
                    f"shown and cited. Closing this gap is one of the fastest, lowest-cost trust wins. ")
    headers = ["Company", "Rating", "Reviews"] + (["Top complaint (the wedge)"] if has_comp else [])
    align = ["left", "right", "right"] + (["left"] if has_comp else [])
    wedge = ("Each rival's recurring complaint is the wedge: point your comparison pages and outbound at "
             "their weakest point, and pre-empt the complaints that would land on you."
             if has_comp else
             "Review counts are read from verified public listings. The gap is not your rating, it is how "
             "few people have reviewed you: more reviews is direct social proof for both buyers and AI.")
    sec = {"type": "table", "num": num, "title": "Reputation and the switching wedge",
           "table": {"headers": headers, "rows": rows, "align": align},
           "note": lead + wedge}
    return sec, None


def web_vitals_section(num, cfg, project_dir):
    j = _latest(project_dir, "data/raw/pagespeed/webvitals-*.json")
    if not j:
        return None, None
    data = json.loads(j.read_text())
    client = _client_name(cfg)
    rows = [[n, o.get("lab_performance") or 0] for n, o in data.items()
            if isinstance(o.get("lab_performance"), (int, float))]
    if len(rows) < 3:
        return None, None
    rows = sorted(rows, key=lambda x: -x[1])
    passers = [n for n, o in data.items() if o.get("cwv_passed")]
    crank = next((i + 1 for i, (n, _) in enumerate(rows) if n == client), None)
    c = data.get(client, {})
    perf = c.get("lab_performance")
    # A top-of-set speed score is a genuine strength worth stating up front.
    lead_in = ""
    if crank == 1:
        lead_in = f"Good news first: {client} has the fastest site in this competitive set. "
    elif crank and crank <= max(2, len(rows) // 3):
        lead_in = f"{client} is among the faster sites in this set ({_ord(crank)} of {len(rows)}). "
    if c.get("cwv_passed"):
        cnote = f"scores {perf} of 100 on a mobile speed test and passes Core Web Vitals"
    elif c.get("cwv_passed") is False:
        cnote = (f"scores {perf} of 100 on a mobile speed test but still fails Core Web Vitals "
                 f"(LCP {c.get('LCP_verdict')}, layout shift {c.get('CLS_verdict')}, blocking {c.get('TBT_verdict')})")
    else:
        cnote = f"scores {perf} of 100 on a mobile speed test"
    sec = {"type": "scenarios", "num": num, "title": "Site speed and Core Web Vitals",
           "bullets": [f"{lead_in}Core Web Vitals are a Google ranking input and a real conversion lever. On "
                       f"mobile, {client} {cnote}."
                       + (f" Rivals passing Core Web Vitals: {', '.join(passers)}." if passers else
                          " No competitor in this set passes Core Web Vitals, so this is shared, winnable ground.")],
           "figure_title": "Mobile performance score", "figure_unit": "0-100, higher is better",
           "chart": {"type": "bar_h", "kind": "compact", "highlight": client, "rows": rows},
           "note": "This is a controlled lab test that works for any site, including a brand-new one."}
    return sec, None


def build_spec(cfg, project_dir, date):
    client = _client_name(cfg)
    num = lambda i: f"{i:02d}"
    sections, headlines = [], []
    i = 2
    for fn in (authority_section, backlinks_section, press_section, traffic_section, share_of_search_section,
               steal_section, momentum_section, keyword_section, greenfield_section,
               competitor_winning_section, reputation_section, google_ads_section, social_section,
               web_vitals_section, sov_section, ai_matrix_section):
        sec, head = fn(num(i), cfg, project_dir)
        if sec:
            sections.append(sec); i += 1
            if head:
                headlines.append(head)

    # opportunity lanes from positioning if present, else generic
    lanes = []
    msg = cfg.get("messaging") or {}
    if isinstance(msg.get("lanes"), list):
        lanes = [l for l in msg["lanes"][:3] if isinstance(l, dict) and l.get("items")]
    if not lanes:
        lanes = [
            {"tag": "Lane 1", "name": "Own the AI answer", "when": "where you are absent today",
             "items": ["Be the cited source when AI names your category", "Answer-first pages + third-party mentions"]},
            {"tag": "Lane 2", "name": "Capture the demand gap", "when": "searches rivals hold",
             "items": ["Build the pages for the queries you are missing", "High-intent, winnable difficulty first"]},
            {"tag": "Lane 3", "name": "Grow authority", "when": "the compounding moat",
             "items": ["Earn the mentions that lift authority + AI citation", "Turn tools/data into linkable assets"]},
        ]

    summary = {
        "type": "summary", "num": "01", "title": "Where you stand today",
        "bullets": headlines or ["A live read of your current digital footprint versus the competitors "
                                 "who are winning your buyers, and the shortest path to overtake them."],
        "pillars": lanes,
    }
    plan = {
        "type": "cta", "num": num(i), "title": "The opportunity, and how we take it",
        "body": f"This is a live snapshot of {_poss(client)} digital footprint against the field. The gaps "
                f"above are the opening: the queries and AI answers your competitors have not locked down. "
                f"We have the machine and the plan to move you up each one, and to prove it with the same "
                f"live data you just saw. The full strategy and 90-day sequence is the next step.",
        "contact": "Prepared from live search, review, and AI-answer data",
    }
    spec = {
        "meta": {"dense": True, "badge": "Digital Presence Scan", "client": client,
                 "title": f"{client}: Your Digital Footprint and the Opportunity",
                 "subtitle": "Where you stand, who is winning your buyers, and the winnable path to overtake them. "
                             f"Live data, {date}.",
                 "date": date, "author": "seo-geo-report-engine"},
        "sections": [summary] + sections + [plan],
    }
    return spec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--date", default="2026-07-01")
    ap.add_argument("--out")
    ap.add_argument("--render", action="store_true", help="also render the PDF via the doc pipeline")
    args = ap.parse_args()

    cfg = load(args.project)
    pdir = cfg.project_dir
    spec = build_spec(cfg, pdir, args.date)

    # write YAML spec (json is valid yaml, and the renderer uses yaml_min which parses json too)
    spec_path = Path(args.out) if args.out else (pdir / "first-scan-report.yml")
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    # emit as JSON (valid YAML subset) to avoid a yaml writer dependency
    spec_path.write_text(json.dumps(spec, indent=2))
    n_sec = len(spec["sections"])
    print(f"assembled first-scan report: {n_sec} sections -> {spec_path}")
    for s in spec["sections"]:
        print(f"  {s.get('num','')} {s.get('title','')} [{s['type']}]")

    if args.render:
        from proposal.build import render_file
        out_pdf = pdir / "deliverables" / f"{args.project}-first-scan.pdf"
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        path = render_file(str(spec_path), out=str(out_pdf), project=args.project)
        print(f"rendered -> {path}")


if __name__ == "__main__":
    main()

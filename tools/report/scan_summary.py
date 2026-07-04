"""Populate the internal dashboard from a project's scan artifacts.

Reports (PDF) go to the client; the dashboard is the internal live view. This reads every scan artifact
a project has and writes two markdown files the dashboard renders: research/competitive-scan.md (the
latest-data working view) and BUILD-STATUS.md (status + headline numbers + what is next). Run after the
scan tools; safe to re-run (it overwrites both files with the freshest read).

    python tools/report/scan_summary.py --project <slug> --date 2026-07-02
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.config import load          # noqa: E402


def _latest(pdir, pattern):
    fs = sorted(Path(pdir).glob(pattern))
    return json.loads(fs[-1].read_text()) if fs else None


def _rowfile(pdir, pattern, key):
    for f in reversed(sorted(Path(pdir).glob(pattern))):
        d = json.loads(f.read_text())
        if isinstance(d, dict) and d.get(key):
            return d
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--date", default="")
    args = ap.parse_args()
    cfg = load(args.project)
    pdir = cfg.project_dir
    client = cfg.get("client_name") or cfg.get("name") or cfg.get("domain")
    date = args.date or "latest"

    auth = _rowfile(pdir, "data/raw/**/authority-*.json", "rows")
    traffic = _latest(pdir, "data/raw/**/traffic-*.json")
    scan = _latest(pdir, "data/raw/**/ai-matrix-*.json")
    mom = _latest(pdir, "data/raw/predictleads/momentum-*.json")
    wv = _latest(pdir, "data/raw/pagespeed/webvitals-*.json")
    ads = _latest(pdir, "data/raw/**/google-ads-*.json")
    opp = _latest(pdir, "data/opportunity-scored.json")
    gap = _latest(pdir, "data/raw/**/competitor-gap-*.json")
    rep = _latest(pdir, "data/raw/openrouter/reputation-*.json")
    sos = _latest(pdir, "data/raw/dataforseo/share-of-search-*.json")
    adm = _latest(pdir, "data/raw/openrouter/ad-messaging-*.json")
    bl = _latest(pdir, "data/raw/dataforseo/backlinks-*.json")

    snap, body = [], []

    # authority
    if auth and auth.get("rows"):
        rows = [r for r in auth["rows"] if isinstance(r.get("referring_domains"), int)]
        rows.sort(key=lambda r: -(r["referring_domains"] or 0))
        cd = (cfg.get("domain") or "").lower().replace("www.", "")
        rank = next((i + 1 for i, r in enumerate(rows) if cd in r["domain"]), None)
        cref = next((r["referring_domains"] for r in rows if cd in r["domain"]), None)
        if rank:
            snap.append(f"- **Authority:** {rank} of {len(rows)} by referring domains ({cref} vs up to {rows[0]['referring_domains']:,})")
        body.append("## Authority (referring domains)\n\n| Company | Referring domains |\n|---|---:|\n"
                    + "\n".join(f"| {r['domain']} | {r.get('referring_domains') or 0:,} |" for r in rows))

    # backlink profile + link gap
    if bl and bl.get("profiles"):
        profs = bl["profiles"]
        prows = sorted(((n, p) for n, p in profs.items() if isinstance(p.get("referring_domains"), int)),
                       key=lambda x: -(x[1].get("referring_domains") or 0))
        cp = profs.get(client) or {}
        gapc, gq = bl.get("gap_count") or 0, bl.get("gap_quality_count") or 0
        if cp.get("referring_domains") is not None:
            snap.append(f"- **Backlinks:** {client} {cp.get('referring_domains'):,} ref domains, "
                        f"spam {cp.get('spam_score')}/100; link gap {gapc} shared ({gq} legitimate)")
        tbl = "\n".join(f"| {n} | {p.get('referring_domains') or 0:,} | {p.get('backlinks') or 0:,} | "
                        f"{p.get('rank_norm') if p.get('rank_norm') is not None else '-'} | {p.get('spam_score') if p.get('spam_score') is not None else '-'} |"
                        for n, p in prows)
        body.append("## Backlink profile + link gap\n\n"
                     f"Link gap: **{gapc}** referring domains link to [{', '.join(bl.get('gap_targets_from') or [])}] "
                     f"but not to {client}; **{gq}** are legitimate (rest are directories/link farms). "
                     "Full vetted target list in `data/backlink-gap-targets.csv`.\n\n"
                     "| Company | Referring domains | Backlinks | Authority (0-100) | Spam |\n|---|---:|---:|---:|---:|\n" + tbl)

    # traffic share
    if traffic:
        snap.append(f"- **Traffic share:** {client} ~{traffic['client_share_pct']}% of the set; {traffic['leader']} ~{traffic['leader_share_pct']}%")
        body.append("## Traffic share (estimated organic)\n\n| Company | Visits/mo (est) | Share |\n|---|---:|---:|\n"
                    + "\n".join(f"| {r['company']} | {r['etv']:,} | {r['share_pct']}% |" for r in traffic["rows"]))

    # share of search
    if sos and sos.get("rows"):
        rising = [r["name"] for r in sos["rows"] if r.get("trend") == "rising"]
        snap.append(f"- **Share of search:** {client} ~{sos.get('client_share_pct')}% of branded search; "
                    f"rising: {', '.join(rising) or 'none'}")
        body.append("## Share of search (branded demand, 12mo)\n\n| Company | Share | Trend |\n|---|---:|---|\n"
                    + "\n".join(f"| {r['name']} | {r['share_pct']}% | {r.get('trend')} |" for r in sos["rows"]))

    # AI visibility
    if scan and scan.get("rows"):
        present = sum(1 for r in scan["rows"] if r.get("brand_mentioned") or r.get("brand_cited"))
        total = len(scan["rows"])
        tally = Counter()
        for r in scan["rows"]:
            for x in r.get("competitors_present", []):
                tally[x] += 1
        named = ", ".join(f"{n} ({c})" for n, c in tally.most_common(5))
        snap.append(f"- **AI visibility:** present in {present} of {total} answer cells; named instead: {named}")
        body.append(f"## AI visibility\n\nPresent in **{present} of {total}** cells across the engines. "
                    f"Named instead: {named}.")

    # web vitals (lab, via Lighthouse)
    wv_ok = bool(wv) and any(o.get("lab_performance") is not None for o in wv.values())
    if wv_ok:
        lines = []
        for name, a in wv.items():
            if a.get("error"):
                st = "error"
            elif a.get("cwv_passed") is not None:
                st = ("PASS" if a.get("cwv_passed") else "FAIL") + f" (LCP {a.get('LCP_verdict')}, CLS {a.get('CLS_verdict')}, blocking {a.get('TBT_verdict')})"
            else:
                st = f"perf {a.get('lab_performance')}"
            lines.append(f"| {name} | {st} | {a.get('lab_performance')} |")
        c = wv.get(client, {})
        cst = (("PASS" if c.get("cwv_passed") else "FAIL") if c.get("cwv_passed") is not None
               else f"perf {c.get('lab_performance')}/100")
        snap.append(f"- **Core Web Vitals (lab):** {client} {cst}")
        body.append("## Core Web Vitals (mobile, lab)\n\n| Company | Lab CWV | Perf |\n|---|---|---:|\n" + "\n".join(lines))

    # momentum
    if mom and mom.get("companies"):
        fd = mom.get("field_depts", {})
        snap.append(f"- **Field momentum:** {mom.get('total_field_roles')} rival open roles "
                    f"(Eng {fd.get('Engineering',0)}, Sales {fd.get('Sales/GTM',0)}, Finance {fd.get('Finance',0)})")
        rows = []
        for n, o in mom["companies"].items():
            lr = o.get("latest_round") or {}
            amt = lr.get("amount")
            amts = (f"${amt/1e9:.1f}B" if amt and amt >= 1e9 else f"${amt/1e6:.0f}M" if amt else "-")
            rows.append(f"| {n} | {amts} {lr.get('type') or ''} {lr.get('date') or ''} | {o.get('open_roles',0)} |")
        body.append("## Competitor momentum (funding + hiring)\n\n| Company | Latest round | Open roles |\n|---|---|---:|\n" + "\n".join(rows))

    # google ads (counts + live-gallery links + messaging)
    if ads:
        hi = {n: o for n, o in ads.items() if o.get("confidence") == "high"}
        if hi:
            lead = max(hi.items(), key=lambda kv: (kv[1].get("ads_count") or 0))
            snap.append(f"- **Google ads:** {lead[0]} ~{lead[1].get('ads_count')} live; {client} {ads.get(client,{}).get('ads_count',0)}")
            am = adm or {}
            lines = []
            for n, o in sorted(hi.items(), key=lambda kv: -(kv[1].get("ads_count") or 0)):
                view = f"[view live ads]({o['transparency_url']})" if o.get("transparency_url") else "-"
                msg = (am.get(n, {}) or {}).get("main_message") or ""
                if "does not appear" in str(msg).lower():
                    msg = ""
                lines.append(f"| {n} | {o.get('ads_count')} | {view} | {msg[:50]} |")
            body.append("## Google ad activity\n\n| Company | Live ads | Gallery | Ad message |\n|---|---:|---|---|\n" + "\n".join(lines))

    # reputation + voice of customer
    if rep and any(d.get("rating") for d in rep.values()):
        rated = [(n, d) for n, d in rep.items() if d.get("rating")]
        worst = min(rated, key=lambda kv: kv[1]["rating"]) if rated else None
        if worst:
            snap.append(f"- **Reputation wedge:** {worst[0]} lowest-rated at {worst[1]['rating']} stars "
                        f"(gripe: {(worst[1].get('top_complaints') or ['-'])[0]})")
        lines = []
        for name, d in rep.items():
            if d.get("error"):
                continue
            r = f"{d['rating']} stars" if d.get("rating") else "no reviews yet"
            lines.append(f"| {name} | {r} | {d.get('review_count') or '-'} | {(d.get('top_complaints') or ['-'])[0]} |")
        body.append("## Reputation and voice-of-customer (switching wedge)\n\n"
                    "| Company | Rating | Reviews | Top complaint |\n|---|---:|---:|---|\n" + "\n".join(lines))

    # greenfield / gap
    if opp and opp.get("counts"):
        c = opp["counts"]
        snap.append(f"- **Greenfield:** {c.get('greenfield',0)} greenfield + {c.get('contested',0)} winnable-niche buyer opportunities")
    if gap and gap.get("totals"):
        t = gap["totals"]
        snap.append(f"- **Steal list:** {t.get('steal_count')} keywords rivals rank for and the client does not")

    # deliverable
    pdfs = sorted((pdir / "deliverables").glob("*.pdf")) if (pdir / "deliverables").exists() else []
    deliverable = pdfs[-1].name if pdfs else None

    scan_md = (f"# {client} - competitive scan (latest data)\n\n"
               f"Updated {date}. Internal working view; sources: live search, public profiles, public "
               f"funding and hiring records. Figures marked estimate are directional.\n\n"
               f"## Snapshot\n\n" + "\n".join(snap) + "\n\n" + "\n\n".join(body) + "\n")
    (pdir / "research").mkdir(parents=True, exist_ok=True)
    (pdir / "research" / "competitive-scan.md").write_text(scan_md)

    status_md = (f"# {client} - build status\n\nUpdated {date}.\n\n"
                 f"## Scan (latest run)\n"
                 f"- [{'x' if auth else ' '}] Authority + referring-domain gap\n"
                 f"- [{'x' if traffic else ' '}] Traffic share\n"
                 f"- [{'x' if gap else ' '}] Keyword + competitor gap (steal list)\n"
                 f"- [{'x' if opp else ' '}] Greenfield opportunity scoring\n"
                 f"- [{'x' if scan else ' '}] Multi-engine AI-visibility matrix\n"
                 f"- [{'x' if wv_ok else ' '}] Core Web Vitals benchmark (lab, via Lighthouse)\n"
                 f"- [{'x' if mom else ' '}] Competitor momentum (funding + hiring + news)\n"
                 f"- [{'x' if ads else ' '}] Google ad activity\n\n"
                 f"## Deliverable\n- {('Strategy report: deliverables/' + deliverable) if deliverable else 'not yet rendered'}\n\n"
                 f"## Headline numbers\n\n" + "\n".join(snap) + "\n\n"
                 f"## Next (report roadmap)\n"
                 f"- Reputation + voice-of-customer scorecard (switching wedge)\n"
                 f"- Share-of-search branded-demand line\n"
                 f"- Ad-creative teardown, web-mentions sentiment, competitor page screenshots\n")
    (pdir / "BUILD-STATUS.md").write_text(status_md)

    print(f"populated dashboard for {client}:")
    print(f"  research/competitive-scan.md  ({len(body)} data sections)")
    print(f"  BUILD-STATUS.md")


if __name__ == "__main__":
    main()

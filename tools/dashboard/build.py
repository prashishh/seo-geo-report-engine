"""Agency operating console — live local server + static export (stdlib only).

The dashboard renders from your project + framework files. Two ways to use it:

  ./bin/mkt dashboard serve   # RECOMMENDED — live server; every refresh re-reads the
                              # files, so new skills/projects/pages appear automatically.
  ./bin/mkt dashboard build   # static export to projects/_dashboard/ (portable, no server)

Add a skill (skills/<x>/SKILL.md), a project (projects/<x>/client.yml), or a page and it
shows up on next load — nothing here is hand-maintained.
"""
from __future__ import annotations

import html
import math
import mimetypes
import re
import urllib.parse
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from lib.config import load_yaml, root

esc = html.escape


def _nd(s):
    """Strip em/en dashes from short display strings (no AI-tell punctuation)."""
    s = str(s)
    return s.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")

PLACEHOLDERS = ["{{TODO", "[NEEDS", "[AUTHOR:", "[unverified]", "[confirm client may display]"]

SKILL_GROUPS = [
    ("Go-to-market", "Define who the client is, the market, and the language before any SEO.", "violet",
     ["positioning-messaging", "customer-research", "market-opportunity"]),
    ("Keyword & content", "Find what to rank for and produce the pages that win it.", "blue",
     ["keyword-research", "competitor-analysis", "content-brief", "content-refresh",
      "internal-linking", "programmatic-seo", "comparison-pages", "human-seo-editor"]),
    ("Technical SEO", "Make sure search engines can crawl, index, and trust the site.", "cyan",
     ["technical-seo-audit", "hreflang-i18n", "schema-markup", "local-seo",
      "web-vitals", "core-web-vitals", "performance", "web-quality-audit"]),
    ("GEO / AI search", "Get the brand found, understood, and cited inside AI answers.", "green",
     ["geo-audit", "aeo-content-patterns", "ai-citation-sprint"]),
    ("Authority & tracking", "Build links, choose data sources, and measure movement over time.", "amber",
     ["backlink-analysis", "rank-tracking", "seo-data-router"]),
    ("Deliverables & ops", "Turn the work into client-ready outputs and run the engagement.", "rose",
     ["proposal-builder", "report-generator", "kpi-dashboard", "skill-navigator", "agency-dashboard"]),
]

LAYERS = [
    ("Workflows", "Commands you run by name",
     "One command runs a whole job end-to-end by chaining skills and agents together. This is how you kick off a piece of work.",
     "/discovery-audit · /growth-proposal · /weekly-report", "blue"),
    ("Skills", "Capabilities the AI uses on its own",
     "Narrow, reusable moves the assistant invokes the moment your request matches; you describe the goal and it picks the skill. These are the bulk of the system.",
     "keyword-research · schema-markup · geo-audit", "green"),
    ("Specialist agents", "Focused sub-assistants it delegates to",
     "For a contained job the system hands off to a specialist (an SEO analyst, a GEO analyst, a data researcher) that has its own tools and reports back.",
     "seo-analyst · geo-analyst · report-writer", "violet"),
    ("Tools", "Deterministic scripts",
     "Plain Python that does the mechanical work with no AI guesswork: render a PDF, generate pages in bulk, draw a chart, call an API.",
     "pdf · charts · programmatic · connectors", "cyan"),
    ("Playbooks", "The methodology",
     "The written 'how we do it' that the skills follow, so the approach stays consistent and portable across every client.",
     "content-decay · i18n-seo · market-sizing", "amber"),
]
LAYER_COUNT_KEYS = ["Workflows", "Skills", "Specialist agents", "Tools", "Playbooks"]

TOOL_NOTES = {
    "charts": "Draws charts as pure SVG (no heavy libraries) for reports and decks.",
    "pdf": "Turns an HTML page into a polished PDF using headless Chrome.",
    "proposal": "Renders proposals, reports, and docs from a content spec.",
    "programmatic": "Generates many pages at once from one template × a data set.",
    "connectors": "Talks to Ahrefs / DataForSEO when the live MCP isn't available.",
    "dashboard": "Builds this operating console.",
    "report": "Helpers that assemble weekly / monthly client reports.",
    "serp": "Captures live search-results data for spot checks.",
    "lib": "Shared config + figures out which client you're working on.",
}

ICON = {
    "grid": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>',
    "file": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "eye": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/></svg>',
    "ext": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
    "back": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
}


# ---------------- helpers ----------------
def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def _files(path: Path, pattern="*"):
    if not path.exists():
        return []
    return sorted((p for p in path.rglob(pattern) if p.is_file() and p.name != ".DS_Store"),
                  key=lambda p: str(p).lower())


def _flat(rel: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", rel.lower()).strip("-")


def _placeholder_counts(project_dir: Path, bases) -> dict:
    counts = {m: 0 for m in PLACEHOLDERS}
    for base_name in bases:
        for p in _files(project_dir / base_name):
            if p.suffix.lower() in (".xlsx", ".pdf", ".png", ".jpg"):
                continue
            text = _read(p)
            for marker in PLACEHOLDERS:
                counts[marker] += text.count(marker)
    return counts


def _health(dc, deliverable_count, research_count):
    if dc["{{TODO"]:
        return "Blocked", "danger"
    if sum(v for k, v in dc.items() if k != "[unverified]") or dc["[unverified]"]:
        return "Needs review", "warn"
    if deliverable_count:
        return "Ready", "ok"
    if research_count:
        return "In production", "info"
    return "Setup needed", "muted"


def _stage(research_count, deliverable_count, data_count):
    if data_count and deliverable_count:
        return "Measuring"
    if deliverable_count:
        return "Built"
    if research_count:
        return "Research"
    return "Setup"


# ---------------- markdown ----------------
def _inline(t):
    t = esc(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    return t


def md_to_html(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out, i, n, para = [], 0, len(md.replace("\r\n", "\n").split("\n")), []

    def flush():
        if para:
            out.append("<p>" + _inline(" ".join(para).strip()) + "</p>")
            para.clear()

    while i < n:
        line = lines[i]
        if line.lstrip().startswith("```"):
            flush(); i += 1; buf = []
            while i < n and not lines[i].lstrip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>" + esc("\n".join(buf)) + "</code></pre>"); continue
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]) and "|" in lines[i + 1]:
            flush()
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(line); i += 2; body = []
            while i < n and "|" in lines[i] and lines[i].strip():
                body.append(cells(lines[i])); i += 1
            t = ["<table><thead><tr>"] + [f"<th>{_inline(c)}</th>" for c in head] + ["</tr></thead><tbody>"]
            for r in body:
                t.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>"); out.append("".join(t)); continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush(); lvl = len(m.group(1)); out.append(f"<h{lvl}>{_inline(m.group(2).strip())}</h{lvl}>"); i += 1; continue
        if re.match(r"^\s*([-*_])\1{2,}\s*$", line):
            flush(); out.append("<hr>"); i += 1; continue
        if line.lstrip().startswith(">"):
            flush(); buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            out.append("<blockquote>" + _inline(" ".join(buf)) + "</blockquote>"); continue
        if re.match(r"^\s*[-*]\s+", line):
            flush(); buf = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                buf.append(re.sub(r"^\s*[-*]\s+", "", lines[i])); i += 1
            out.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in buf) + "</ul>"); continue
        if re.match(r"^\s*\d+\.\s+", line):
            flush(); buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append(re.sub(r"^\s*\d+\.\s+", "", lines[i])); i += 1
            out.append("<ol>" + "".join(f"<li>{_inline(x)}</li>" for x in buf) + "</ol>"); continue
        if not line.strip():
            flush(); i += 1; continue
        para.append(line); i += 1
    flush()
    return "\n".join(out)


# ---------------- capability parsing ----------------
def _frontmatter(text):
    m = re.search(r"^---\s*$(.*?)^---\s*$(.*)$", text, re.S | re.M)
    if m:
        return m.group(1), m.group(2)
    return text[:600], text


def _fm_field(block, key):
    dm = re.search(rf"^{key}:\s*(.*)$", block, re.M)
    if not dm:
        return ""
    rest = block[dm.end():]
    val = dm.group(1).strip().lstrip(">|").strip()
    for ln in rest.split("\n"):
        if re.match(r"^[a-zA-Z_-]+:\s", ln) or ln.strip() == "---":
            break
        val += " " + ln.strip()
    return re.sub(r"\s+", " ", val).strip().strip('">').strip()


def _clean_summary(desc, limit=180):
    s = re.split(r"\bUse when\b", desc, 1, flags=re.I)[0].strip()
    if len(s) < 24:
        s = desc
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > limit:
        cut = s[:limit]
        s = cut[:cut.rfind(" ")].rstrip(",;:") + "…"
    return s


def _triggers(desc):
    found = re.findall(r'"([^"]{3,70})"', desc)
    seen, out = set(), []
    for f in found:
        k = f.lower()
        if k not in seen:
            seen.add(k); out.append(f)
    return out[:12]


def _produces(desc, body):
    m = re.search(r"(Produces|Outputs?|Writes|Generates)\s+([^.]+)\.", desc + " " + body, re.I)
    return (m.group(1) + " " + m.group(2).strip() + ".") if m else ""


def parse_skill(path: Path):
    txt = _read(path)
    fm, body = _frontmatter(txt)
    name = _fm_field(fm, "name") or path.parent.name
    desc = _fm_field(fm, "description")
    body = re.sub(r"^#\s+.*\n", "", body.strip(), count=1).strip()
    return {"name": name, "summary": _nd(_clean_summary(desc)), "triggers": _triggers(desc),
            "produces": _nd(_produces(desc, body)), "body": body, "desc": desc}


def collect_capabilities():
    r = root()
    skills = {p.parent.name: parse_skill(p) for p in sorted((r / "skills").glob("*/SKILL.md"))}
    grouped, used = [], set()
    for label, blurb, color, names in SKILL_GROUPS:
        items = [skills[nm] for nm in names if nm in skills]
        used.update(s["name"] for s in items)
        if items:
            grouped.append((label, blurb, color, items))
    other = [s for nm, s in skills.items() if s["name"] not in used]
    if other:
        grouped.append(("More", "Additional capabilities.", "slate", sorted(other, key=lambda s: s["name"])))
    commands = []
    for c in sorted((r / "commands").glob("*.md")):
        fm, body = _frontmatter(_read(c))
        commands.append({"name": c.stem, "summary": _nd(_clean_summary(_fm_field(fm, "description"), 220))})
    agents = []
    for a in sorted((r / "agents").glob("*.md")):
        fm, _ = _frontmatter(_read(a))
        agents.append({"name": _fm_field(fm, "name") or a.stem,
                       "summary": _nd(_clean_summary(_fm_field(fm, "description"), 220))})
    tools = [(p.name, TOOL_NOTES.get(p.name, "")) for p in sorted((r / "tools").glob("*/"))
             if p.is_dir() and not p.name.startswith("_")]
    playbooks = [p.stem for p in sorted((r / "playbooks").glob("*.md"))]
    return {"skills": grouped, "skills_flat": skills, "skill_total": len(skills),
            "commands": commands, "agents": agents, "tools": tools, "playbooks": playbooks}


# ---------------- project parsing ----------------
def _page_title(p: Path, fallback):
    txt = _read(p)
    m = re.search(r"<title[^>]*>(.*?)</title>", txt, re.I | re.S)
    if m:
        t = re.split(r"\s*[|—–]\s*", m.group(1).strip())[0].strip()
        if t:
            return re.sub(r"\s+", " ", t)
    m = re.search(r"<h1[^>]*>(.*?)</h1>", txt, re.I | re.S)
    if m:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
    return fallback.replace("-", " ").title()


PAGE_GROUPS = [("Core pages", "pages"), ("Capability pages", "capability"),
               ("Department pages", "department"), ("Comparison pages", "comparison"),
               ("Integration pages", "integration")]
CORE_ORDER = ["digital-tipping-hotels", "how-it-works", "best-digital-tipping", "staff-retention"]


def _artifact(p, project_dir):
    rel = str(p.relative_to(project_dir))
    suf = p.suffix.lower().lstrip(".")
    kind = {"md": "md", "html": "html", "pdf": "pdf", "csv": "data", "json": "data",
            "yml": "data", "yaml": "data", "txt": "text", "xlsx": "input"}.get(suf, "other")
    a = {"rel": rel, "abs": p, "name": p.name, "kind": kind, "suffix": suf,
         "folder": rel.split("/")[-2] if "/" in rel else ""}
    if kind == "html":
        a["title"] = _page_title(p, p.stem)
    return a


def collect_projects():
    r = root()
    projects = []
    for cf in sorted((r / "projects").glob("*/client.yml")):
        d = cf.parent
        if d.name.startswith("_"):
            continue
        client = load_yaml(cf) or {}
        research = [_artifact(p, d) for p in _files(d / "research")]
        deliverables = [_artifact(p, d) for p in _files(d / "deliverables")]
        inputs = [_artifact(p, d) for p in _files(d / "inputs")]
        data = [_artifact(p, d) for p in _files(d / "data")]
        built = [a for a in deliverables if a["kind"] == "html"]
        other = [a for a in deliverables if a["kind"] != "html"]
        dc = _placeholder_counts(d, ("deliverables",))
        health, hclass = _health(dc, len(deliverables), len(research))
        ah = client.get("ahrefs", {}) or {}
        projects.append({
            "slug": d.name, "dir": d, "client": client, "name": client.get("name") or d.name,
            "domain": client.get("domain") or "", "industry": client.get("industry") or "",
            "market": client.get("market") or "", "positioning": client.get("positioning") or "",
            "icp": client.get("icp", []) or [], "competitors": client.get("competitors", []) or [],
            "keywords": client.get("target_keywords", []) or [], "ahrefs": ah,
            "messaging": client.get("messaging", {}) or {},
            "research": research, "deliverables": deliverables, "built": built, "other": other,
            "inputs": inputs, "data": data, "dc": dc, "health": health, "hclass": hclass,
            "stage": _stage(len(research), len(deliverables), len(data)),
            "status_md": _read(d / "BUILD-STATUS.md"),
            "tracking": bool(ah.get("project_id") or ah.get("brand_radar_report_id")),
        })
    return projects


# ---------------- link builder (works for live server AND static export) ----------------
class L:
    def __init__(self, mode):
        self.mode = mode  # "live" | "static"

    def overview(self):
        return "/" if self.mode == "live" else "index.html"

    def capabilities(self):
        return "/capabilities" if self.mode == "live" else "capabilities.html"

    def skill(self, n):
        return f"/skill/{n}" if self.mode == "live" else f"skill-{n}.html"

    def playbook(self, n):
        return f"/playbook/{n}" if self.mode == "live" else f"playbook-{n}.html"

    def project(self, s):
        return f"/project/{s}" if self.mode == "live" else f"project-{s}.html"

    def view(self, s, rel):
        return f"/view/{s}/{rel}" if self.mode == "live" else f"view-{s}-{_flat(rel)}.html"

    def page(self, s, rel):
        return f"/page/{s}/{rel}" if self.mode == "live" else f"page-{s}-{_flat(rel)}.html"

    def data(self, s, rel):
        return f"/data/{s}/{rel}" if self.mode == "live" else f"data-{s}-{_flat(rel)}.html"

    def raw(self, s, rel):
        return f"/raw/{s}/{rel}" if self.mode == "live" else f"../{s}/{rel}"


# how each file opens inside the console
def open_kind(art):
    suf = art["suffix"]
    if art["kind"] == "md":
        return "view"
    if suf in ("html", "htm", "pdf"):
        return "page"
    if suf in ("csv", "json", "yml", "yaml", "txt"):
        return "data"
    return "raw"  # binary (xlsx, images) -> download


def art_link(L_, slug, art):
    kind = open_kind(art)
    href = {"view": L_.view, "page": L_.page, "data": L_.data, "raw": L_.raw}[kind](slug, art["rel"])
    tag = {"view": "read", "page": "view", "data": art["suffix"], "raw": art["suffix"]}[kind]
    target = ' target="_blank" rel="noopener"' if kind == "raw" else ""
    return (f'<a class="fitem"{target} href="{href}"><i>{ICON["file"]}</i>'
            f'<span class="fn">{esc(art["name"])}</span><span class="ftag">{esc(tag)}</span></a>')


# ---------------- presentation ----------------
def _pill(t, k):
    return f'<span class="pill {k}">{esc(t)}</span>'


def _dot(k):
    return f'<span class="dot {k}"></span>'


STAGE_COLOR = {"Setup": "slate", "Research": "blue", "Built": "cyan", "Measuring": "violet"}


def _stage_pill(stage):
    color = STAGE_COLOR.get(stage, "slate")
    return f'<span class="pill stagepill c-{color}">{esc(stage)}</span>'


def _ring(pct, size=52, stroke=5):
    pct = max(0, min(100, int(round(pct))))
    r = (size - stroke) / 2
    circ = 2 * math.pi * r
    offset = circ * (1 - pct / 100)
    color = "var(--brand)" if pct == 100 else ("#f59e0b" if pct >= 40 else "#ef4444")
    cx = cy = size / 2
    return (f'<svg class="ring" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="var(--line2)" stroke-width="{stroke}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke}" '
            f'stroke-dasharray="{circ:.2f}" stroke-dashoffset="{offset:.2f}" stroke-linecap="round" '
            f'transform="rotate(-90 {cx} {cy})"/>'
            f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="12.5" font-weight="800" '
            f'fill="var(--ink)">{pct}%</text></svg>')


def art_href(L_, slug, art):
    kind = open_kind(art)
    return {"view": L_.view, "page": L_.page, "data": L_.data, "raw": L_.raw}[kind](slug, art["rel"])


def _recent_activity(projects, L_, limit=8):
    items = []
    for p in projects:
        for a in p["research"] + p["deliverables"] + p["inputs"] + p["data"]:
            try:
                mtime = a["abs"].stat().st_mtime
            except Exception:
                continue
            items.append((mtime, p, a))
    if not items:
        return ""
    items.sort(key=lambda x: -x[0])
    rows = ""
    for mtime, p, a in items[:limit]:
        when = datetime.fromtimestamp(mtime).strftime("%b %d, %H:%M")
        href = art_href(L_, p["slug"], a)
        rows += (f'<a class="activity-row" href="{href}">'
                 f'<div class="activity-main"><b>{esc(a["name"])}</b>'
                 f'<span>{esc(p["name"])} · {esc(a["rel"])}</span></div>'
                 f'<span class="activity-when">{esc(when)}</span></a>')
    return f"""<section class="panel">
      <div class="panel-head"><h2>Recent activity</h2><span class="cnt">{len(items)}</span></div>
      <p class="muted small" style="margin:-2px 0 12px">The latest files touched across every project, newest first.</p>
      <div class="activity-list">{rows}</div>
    </section>"""


def _shell(L_, active, projects, title, subtitle, body, back=None):
    nav = ""
    for k, href, ic, lbl in [("overview", L_.overview(), ICON["grid"], "Overview"),
                             ("capabilities", L_.capabilities(), ICON["spark"], "Capabilities")]:
        nav += f'<a class="nav-item {"active" if active==k else ""}" href="{href}"><i>{ic}</i><span>{lbl}</span></a>'
    proj = "".join(
        f'<a class="nav-item proj {"active" if active==p["slug"] else ""}" href="{L_.project(p["slug"])}">'
        f'{_dot(p["hclass"])}<span>{esc(p["name"])}</span></a>' for p in projects)
    live = self_mode_badge(L_)
    backhtml = f'<a class="back" href="{back[1]}"><i>{ICON["back"]}</i> {esc(back[0])}</a>' if back else ""
    now = datetime.now().strftime("%b %d, %Y · %H:%M")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · seo-geo-report-engine</title>
<style>{CSS}</style></head><body><div class="app">
<aside class="sidebar">
  <a class="brand" href="{L_.overview()}"><span class="logo">◆</span><div><b>seo-geo-report-engine</b><small>operating console</small></div></a>
  <nav>{nav}</nav>
  <div class="nav-sec">Projects <span class="cnt">{len(projects)}</span></div>
  <nav>{proj}</nav>
  <div class="side-foot">{live}</div>
</aside>
<main class="main">
  <div class="pagehead"><div>{backhtml}<h1>{esc(title)}</h1><p class="sub">{subtitle}</p></div>
  <div class="stamp">{now}</div></div>
  {body}
</main></div>{SEARCH_JS if active=='overview' else ''}</body></html>"""


def self_mode_badge(L_):
    if L_.mode == "live":
        return '<span class="livedot"></span> Live · reads your files on every refresh'
    return 'Static export · run <code>./bin/mkt dashboard serve</code> for live mode'


# ---- overview ----
def _project_card(L_, p):
    chips = (f'<span class="chip"><b>{len(p["built"])}</b> pages</span>'
             f'<span class="chip"><b>{len(p["research"])}</b> research</span>'
             f'<span class="chip"><b>{len(p["inputs"])}</b> inputs</span>')
    markers = sum(p["dc"].values())
    ready = "Ready to hand off" if markers == 0 else f"{markers} item(s) to review before handoff"
    pct = 100 if markers == 0 else max(8, 100 - min(90, markers))
    search = esc(_nd((p["name"] + " " + p["domain"] + " " + p["industry"]).lower()))
    return f"""<a class="card project" href="{L_.project(p['slug'])}" data-search="{search}">
      <div class="card-top"><div>{_stage_pill(p['stage'])}<h3>{esc(p['name'])}</h3></div>{_pill(p['health'], p['hclass'])}</div>
      <div class="muted-line">{esc(p['domain'] or 'no domain set')} · {esc(p['market'] or 'no market')}</div>
      <p class="card-desc">{esc(_nd((p['industry'] or p['positioning'])[:120]))}</p>
      <div class="chips">{chips}</div>
      <div class="card-foot ring-foot">
        <div class="ring-combo">{_ring(pct)}<span>{esc(ready)}</span></div>
        <span class="go">Open →</span>
      </div></a>"""


def _exec_metric(label, value, note="", tone="neutral"):
    note_html = f"<small>{esc(note)}</small>" if note else ""
    return f'<div class="exec-metric {tone}"><strong>{esc(value)}</strong><span>{esc(label)}</span>{note_html}</div>'


def _portfolio_snapshot(projects, caps):
    total = len(projects)
    pages = sum(len(p["built"]) for p in projects)
    research = sum(len(p["research"]) for p in projects)
    deliverables = sum(len(p["deliverables"]) for p in projects)
    tracking = sum(1 for p in projects if p["tracking"])
    review_markers = sum(sum(p["dc"].values()) for p in projects)
    ready = sum(1 for p in projects if p["hclass"] == "ok")
    qa = sum(1 for p in projects if p["hclass"] == "warn")
    return f"""
    <section class="exec-hero">
      <div class="exec-copy">
        <div class="eyebrow">Portfolio snapshot</div>
        <h2>Agency operating system</h2>
        <p>We're the strategy brain: research, trends, page-ready deliverables, and recommendations for each client's own team to build and ship. Built from the repository, so this stays a live snapshot of the work.</p>
      </div>
      <div class="exec-grid">
        {_exec_metric("projects", str(total), f"{ready} ready, {qa} in review", "ok" if qa == 0 else "warn")}
        {_exec_metric("pages drafted", str(pages), f"{deliverables} deliverables total", "neutral")}
        {_exec_metric("research artifacts", str(research), "strategy, briefs, audits", "neutral")}
        {_exec_metric("skills available", str(caps["skill_total"]), "inherited by every project", "neutral")}
        {_exec_metric("tracking configured", f"{tracking}/{total}", "Ahrefs ids for now", "info" if tracking else "warn")}
        {_exec_metric("handoff review items", str(review_markers), "source, author, and fact checks", "ok" if review_markers == 0 else "warn")}
      </div>
    </section>"""


def _stage_pipeline(projects):
    stages = ["Setup", "Research", "Built", "Measuring"]
    counts = {s: 0 for s in stages}
    for p in projects:
        counts[p["stage"]] = counts.get(p["stage"], 0) + 1
    max_count = max(counts.values() or [1], default=1)
    items = ""
    for stage in stages:
        count = counts.get(stage, 0)
        pct = 14 if max_count == 0 else max(14, int(count / max_count * 100))
        items += f"""<div class="stage-step">
          <div class="stage-top"><b>{esc(str(count))}</b><span>{esc(stage)}</span></div>
          <div class="stage-bar"><i style="width:{pct}%"></i></div>
        </div>"""
    return f"""<section class="panel compact-panel">
      <div class="panel-head"><h2>Delivery pipeline</h2><span class="cnt">{len(projects)}</span></div>
      <div class="stage-grid">{items}</div>
    </section>"""


def _attention_panel(projects, L_):
    rows = []
    for p in projects:
        markers = sum(p["dc"].values())
        if markers:
            rows.append((p, f"{markers} item(s) to review", "Resolve sources, authors, and verification notes before handoff."))
        elif not p["tracking"]:
            rows.append((p, "Tracking ids missing", "Add Ahrefs project / Brand Radar ids or planned replacements."))
        elif not p["data"]:
            rows.append((p, "No data snapshots yet", "Capture rank, KPI, GSC/GA4, and AI citation baselines."))
        elif not p["status_md"].strip():
            rows.append((p, "No build status", "Add a project BUILD-STATUS.md for executive continuity."))
    if not rows:
        rows_html = '<div class="attention-empty">No immediate portfolio alerts.</div>'
    else:
        rows_html = "".join(
            f"""<a class="attention-row" href="{L_.project(p['slug'])}">
              {_dot(p['hclass'])}<div><b>{esc(p['name'])}</b><span>{esc(title)}</span></div>
              <small>{esc(note)}</small></a>"""
            for p, title, note in rows[:6]
        )
    return f"""<section class="panel compact-panel">
      <div class="panel-head"><h2>Needs attention</h2><span class="cnt">{len(rows)}</span></div>
      <div class="attention-list">{rows_html}</div>
    </section>"""


def render_overview(projects, caps, L_):
    counts = {"Skills": caps["skill_total"], "Workflows": len(caps["commands"]),
              "Specialist agents": len(caps["agents"]), "Tools": len(caps["tools"]),
              "Playbooks": len(caps["playbooks"])}
    tiles = ""
    for name, what, why, ex, color in LAYERS:
        tiles += f'<a class="tile c-{color}" href="{L_.capabilities()}"><span class="tnum">{counts[name]}</span><div class="tmeta"><span class="tl">{esc(name)}</span><span class="td">{esc(what)}</span></div></a>'
    cards = "".join(_project_card(L_, p) for p in projects) or '<p class="muted">No projects yet.</p>'
    body = f"""
    {_portfolio_snapshot(projects, caps)}
    <div class="overview-split">
      {_stage_pipeline(projects)}
      {_attention_panel(projects, L_)}
    </div>
    {_recent_activity(projects, L_)}
    <section class="panel">
      <div class="panel-head"><h2>What this system can do</h2><a class="link" href="{L_.capabilities()}">Explore capabilities →</a></div>
      <p class="muted small" style="margin:-4px 0 14px">Built in layers. Click any layer for the full, plain-English breakdown.</p>
      <div class="tiles">{tiles}</div>
    </section>
    <section class="panel">
      <div class="panel-head"><h2>Projects <span class="cnt">{len(projects)}</span></h2>
        <input id="search" class="search" placeholder="Filter projects…" oninput="filterCards()"></div>
      <div class="grid" id="cards">{cards}</div>
    </section>"""
    return _shell(L_, "overview", projects, "Agency console",
                  "Your capabilities and live projects, in one place.", body)


# ---- capabilities ----
def render_capabilities(projects, caps, L_):
    counts = {"Skills": caps["skill_total"], "Workflows": len(caps["commands"]),
              "Specialist agents": len(caps["agents"]), "Tools": len(caps["tools"]),
              "Playbooks": len(caps["playbooks"])}
    layers = ""
    for name, what, why, ex, color in LAYERS:
        layers += f"""<div class="layer c-{color}"><div class="layer-n"><b>{counts[name]}</b><span>{esc(name)}</span></div>
          <div class="layer-b"><strong>{esc(what)}</strong><p>{esc(why)}</p><div class="ex">{esc(ex)}</div></div></div>"""
    groups = ""
    for label, blurb, color, items in caps["skills"]:
        cards = ""
        for s in items:
            cards += f"""<a class="skillcard" href="{L_.skill(s['name'])}">
              <div class="sc-head"><b>{esc(s['name'])}</b><i class="go">{ICON['arrow']}</i></div>
              <p>{esc(s['summary'])}</p></a>"""
        groups += f"""<div class="capsec c-{color}"><div class="capsec-head"><h3>{esc(label)}</h3><span>{esc(blurb)}</span></div>
          <div class="scgrid">{cards}</div></div>"""
    cmds = "".join(f'<div class="caprow"><b>/{esc(c["name"])}</b><span>{esc(c["summary"])}</span></div>' for c in caps["commands"])
    ags = "".join(f'<div class="caprow"><b>{esc(a["name"])}</b><span>{esc(a["summary"])}</span></div>' for a in caps["agents"])
    tls = "".join(f'<div class="caprow"><b>{esc(n)}</b><span>{esc(note)}</span></div>' for n, note in caps["tools"])
    pbs = "".join(f'<a class="skill" href="{L_.playbook(n)}">{esc(n)}</a>' for n in caps["playbooks"])
    body = f"""
    <section class="panel">
      <div class="panel-head"><h2>How the system is built</h2></div>
      <p class="muted small" style="margin:-2px 0 14px">Five layers. You trigger a <b>workflow</b>; it orchestrates <b>skills</b>; skills delegate to <b>agents</b> and call <b>tools</b>; everything follows a <b>playbook</b>.</p>
      <div class="layers">{layers}</div>
    </section>
    <section class="panel">
      <div class="panel-head"><h2>Skills by area</h2><span class="cnt">{caps['skill_total']}</span></div>
      <p class="muted small" style="margin:-2px 0 16px">The capabilities the assistant invokes automatically. Click any one to see what it does, when it fires, and what it produces.</p>
      {groups}
    </section>
    <div class="cap2">
      <section class="panel"><div class="panel-head"><h2>Workflows</h2><span class="cnt">{len(caps['commands'])}</span></div>
        <p class="muted small" style="margin:-2px 0 12px">Run by name to execute a whole job end-to-end.</p>{cmds}</section>
      <section class="panel"><div class="panel-head"><h2>Specialist agents</h2><span class="cnt">{len(caps['agents'])}</span></div>
        <p class="muted small" style="margin:-2px 0 12px">Focused sub-assistants the system delegates to.</p>{ags}</section>
    </div>
    <div class="cap2">
      <section class="panel"><div class="panel-head"><h2>Tool kits</h2><span class="cnt">{len(caps['tools'])}</span></div>
        <p class="muted small" style="margin:-2px 0 12px">Deterministic scripts that do the mechanical work.</p>{tls}</section>
      <section class="panel"><div class="panel-head"><h2>Playbooks</h2><span class="cnt">{len(caps['playbooks'])}</span></div>
        <p class="muted small" style="margin:-2px 0 12px">The methodology behind the skills. Click to read.</p><div class="skillwrap">{pbs}</div></section>
    </div>"""
    return _shell(L_, "capabilities", projects, "Capabilities",
                  "Everything this system can do for a client, and what each piece means.", body)


def render_skill(skill, projects, caps, L_):
    trig = "".join(f'<span class="trig">{esc(t)}</span>' for t in skill["triggers"]) or '<span class="muted small">Invoked from context.</span>'
    produces = f'<div class="kv"><span>What it produces</span><p>{esc(skill["produces"])}</p></div>' if skill["produces"] else ""
    bodyhtml = md_to_html(_nd(skill["body"])) if skill["body"].strip() else "<p class='muted'>See the playbook it references.</p>"
    body = f"""
    <div class="panel">
      <div class="skill-hero"><div class="badge-skill">SKILL</div><p class="lead">{esc(skill['summary'])}</p></div>
      <div class="kv"><span>When it fires</span><div class="trigs">{trig}</div></div>
      {produces}
    </div>
    <div class="panel"><div class="panel-head"><h2>How it works</h2></div><div class="md">{bodyhtml}</div></div>"""
    return _shell(L_, "capabilities", projects, skill["name"], "Skill capability",
                  body, back=("All capabilities", L_.capabilities()))


def render_playbook(name, projects, L_):
    md = _nd(_read(root() / "playbooks" / f"{name}.md"))
    body = f'<article class="panel md reader">{md_to_html(md)}</article>'
    return _shell(L_, "capabilities", projects, name.replace("-", " ").title(),
                  "Playbook · methodology", body, back=("All capabilities", L_.capabilities()))


# ---- project ----
def render_project(p, projects, L_):
    slug = p["slug"]
    comp = _nd(", ".join(c.get("name", str(c)) if isinstance(c, dict) else str(c) for c in p["competitors"])) or "not set"
    icp = _nd(", ".join(p["icp"][:4])) or "not set"
    kws = _nd(", ".join(p["keywords"][:6])) or "not set"
    one = _nd(p["messaging"].get("one_liner") if isinstance(p["messaging"], dict) else "")
    facts = f"""<div class="facts">
      <div><span>Domain</span><b>{'<a href="https://'+esc(p['domain'])+'" target="_blank" rel="noopener">'+esc(p['domain'])+'</a>' if p['domain'] else '—'}</b></div>
      <div><span>Market</span><b>{esc(p['market'] or 'not set')}</b></div>
      <div><span>Industry</span><b>{esc(_nd(p['industry']) or 'not set')}</b></div>
      <div><span>Tracking</span><b>{'Ahrefs configured' if p['tracking'] else 'Ahrefs ids missing'}</b></div>
      <div class="wide"><span>Ideal customers</span><b>{esc(icp)}</b></div>
      <div class="wide"><span>Competitors</span><b>{esc(comp)}</b></div>
      <div class="wide"><span>Target keywords</span><b>{esc(kws)}</b></div></div>"""
    headline_html = f'<div class="headline-quote">"{esc(one)}"</div>' if one else ""
    status_html = md_to_html(_nd(p["status_md"])) if p["status_md"].strip() else \
        f'<p class="muted">No BUILD-STATUS.md yet. Stage: <b>{esc(p["stage"])}</b>.</p>'

    # built pages, grouped + ordered + human titles + preview links
    by_folder = {}
    for a in p["built"]:
        by_folder.setdefault(a["folder"] or "pages", []).append(a)
    pages_html = ""
    for label, folder in PAGE_GROUPS:
        items = by_folder.get(folder, [])
        if not items:
            continue
        if folder == "pages":
            items = sorted(items, key=lambda a: (CORE_ORDER.index(a["abs"].stem) if a["abs"].stem in CORE_ORDER else 99, a["title"]))
        else:
            items = sorted(items, key=lambda a: a["title"])
        cards = ""
        for a in items:
            cards += f"""<div class="pagecard">
              <div class="pc-main"><b>{esc(a['title'])}</b><span>/{esc(a['abs'].stem)}</span></div>
              <div class="pc-act"><a class="mini" href="{L_.page(slug, a['rel'])}"><i>{ICON['eye']}</i>Preview</a>
              <a class="mini ghost" href="{L_.raw(slug, a['rel'])}" target="_blank" rel="noopener"><i>{ICON['ext']}</i>Open</a></div></div>"""
        pages_html += f'<div class="pgroup"><div class="pglabel">{esc(label)} <span>{len(items)}</span></div><div class="pagegrid">{cards}</div></div>'
    if pages_html:
        pages_html = f'<div class="panel"><div class="panel-head"><h2>Pages produced</h2><span class="cnt">{len(p["built"])}</span></div><p class="muted small" style="margin:-2px 0 14px">Click <b>Preview</b> to see the rendered page inside the console.</p>{pages_html}</div>'

    def filepanel(title, items, desc=""):
        if not items:
            return ""
        d = f'<p class="muted small" style="margin:-2px 0 12px">{esc(desc)}</p>' if desc else ""
        links = "".join(art_link(L_, slug, a) for a in items)
        return f'<div class="panel"><div class="panel-head"><h2>{esc(title)}</h2><span class="cnt">{len(items)}</span></div>{d}<div class="filelist">{links}</div></div>'

    rmd = [a for a in p["research"] if a["kind"] == "md"]
    rother = [a for a in p["research"] if a["kind"] != "md"]
    dmd = [a for a in p["other"] if a["kind"] == "md"]
    draw = [a for a in p["other"] if a["kind"] != "md"]

    dc = p["dc"]
    labels = {"{{TODO": "Missing template fields", "[NEEDS": "Needs sourced data / norms",
              "[AUTHOR:": "Needs a named author (E-E-A-T)", "[unverified]": "Unverified competitor facts",
              "[confirm client may display]": "Confirm partner names"}
    rows = ""
    for m in PLACEHOLDERS:
        v = dc[m]
        kl = "ok" if v == 0 else ("danger" if m == "{{TODO" else "warn")
        rows += f'<div class="rdrow"><span class="rdn">{_dot(kl)}{esc(labels[m])}</span><b>{v}</b></div>'
    total = sum(dc.values())
    pct = 100 if total == 0 else max(8, 100 - min(90, total))
    ready = _pill("Ready to hand off", "ok") if total == 0 else _pill(f"{total} to review", "warn")

    body = f"""<div class="phead">
      <div class="phead-main">{_stage_pill(p['stage'])} {_pill(p['health'], p['hclass'])} {ready}</div>
      <div class="phead-ring">{_ring(pct, size=64, stroke=6)}<span>handoff ready</span></div>
    </div>
    {headline_html}
    {facts}
    <div class="panel"><div class="panel-head"><h2>Status</h2></div><div class="md">{status_html}</div></div>
    {filepanel("Input assets", p["inputs"], "The brief and source files this engagement started from.")}
    {filepanel("Research & strategy", rmd, "The thinking: keyword strategy, page architecture, briefs, voice-of-customer.")}
    {filepanel("Research data", rother, "Keyword exports, page rows, and other working data.")}
    {filepanel("Schema & specs", dmd, "Structured-data blocks and asset specifications.")}
    {pages_html}
    {filepanel("Other deliverables", draw, "llms.txt and other shipped files.")}
    {filepanel("Tracking data", p["data"], "Rank, KPI, and AI-citation snapshots over time.")}
    <div class="panel"><div class="panel-head"><h2>Handoff checklist</h2></div><p class="muted small" style="margin:-2px 0 12px">What to review before this goes to the client's own team to build and ship.</p><div class="readiness">{rows}</div></div>"""
    return _shell(L_, slug, projects, p["name"], esc(_nd(p["positioning"][:150] or p["industry"])),
                  body, back=("All projects", L_.overview()))


def render_md_view(p, art, projects, L_):
    body = f"""<div class="viewerbar"><span class="vpath">{esc(art['rel'])}</span></div>
    <article class="panel md reader">{md_to_html(_nd(_read(art['abs'])))}</article>"""
    return _shell(L_, p["slug"], projects, art["name"], f"{esc(p['name'])} · file",
                  body, back=(p["name"], L_.project(p["slug"])))


def render_page_view(p, art, projects, L_):
    title = art.get("title") or art["abs"].stem.replace("-", " ").title()
    body = f"""<div class="previewbar">
      <span class="vpath">{esc(art['rel'])}</span>
      <a class="mini ghost" href="{L_.raw(p['slug'], art['rel'])}" target="_blank" rel="noopener"><i>{ICON['ext']}</i>Open full page</a></div>
    <div class="frame-wrap"><iframe class="preview" src="{L_.raw(p['slug'], art['rel'])}" title="{esc(title)}"></iframe></div>"""
    return _shell(L_, p["slug"], projects, title, f"{esc(p['name'])} · rendered page",
                  body, back=(p["name"], L_.project(p["slug"])))


def render_data_view(p, art, projects, L_):
    txt = _nd(_read(art["abs"]))
    suf = art["suffix"]
    if suf == "csv":
        import csv as _csv
        rows = list(_csv.reader(txt.splitlines()))
        if rows:
            thead = "".join(f"<th>{esc(c)}</th>" for c in rows[0])
            trows = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            content = f'<div class="md"><table><thead><tr>{thead}</tr></thead><tbody>{trows}</tbody></table></div>'
        else:
            content = '<p class="muted">Empty file.</p>'
    elif suf == "json":
        import json as _json
        try:
            content = f'<pre class="codeblock">{esc(_json.dumps(_json.loads(txt), indent=2))}</pre>'
        except Exception:
            content = f'<pre class="codeblock">{esc(txt)}</pre>'
    else:  # yml, yaml, txt
        content = f'<pre class="codeblock">{esc(txt)}</pre>'
    body = f"""<div class="viewerbar"><span class="vpath">{esc(art['rel'])}</span>
      <a class="mini ghost" href="{L_.raw(p['slug'], art['rel'])}" target="_blank" rel="noopener"><i>{ICON['ext']}</i>Raw</a></div>
    <article class="panel reader">{content}</article>"""
    return _shell(L_, p["slug"], projects, art["name"], f"{esc(p['name'])} · data file",
                  body, back=(p["name"], L_.project(p["slug"])))


# ---------------- static export ----------------
def build(out=None):
    r = root()
    out_dir = Path(out) if out else r / "projects" / "_dashboard"
    if not out_dir.is_absolute():
        out_dir = r / out_dir
    if out_dir.suffix == ".html":
        out_dir = out_dir.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    projects = collect_projects()
    caps = collect_capabilities()
    Ls = L("static")
    (out_dir / "index.html").write_text(render_overview(projects, caps, Ls), encoding="utf-8")
    (out_dir / "capabilities.html").write_text(render_capabilities(projects, caps, Ls), encoding="utf-8")
    for s in caps["skills_flat"].values():
        (out_dir / f"skill-{s['name']}.html").write_text(render_skill(s, projects, caps, Ls), encoding="utf-8")
    for nm in caps["playbooks"]:
        (out_dir / f"playbook-{nm}.html").write_text(render_playbook(nm, projects, Ls), encoding="utf-8")
    for p in projects:
        (out_dir / f"project-{p['slug']}.html").write_text(render_project(p, projects, Ls), encoding="utf-8")
        for a in p["research"] + p["deliverables"] + p["inputs"] + p["data"]:
            k = open_kind(a)
            if k == "view":
                (out_dir / f"view-{p['slug']}-{_flat(a['rel'])}.html").write_text(render_md_view(p, a, projects, Ls), encoding="utf-8")
            elif k == "page":
                (out_dir / f"page-{p['slug']}-{_flat(a['rel'])}.html").write_text(render_page_view(p, a, projects, Ls), encoding="utf-8")
            elif k == "data":
                (out_dir / f"data-{p['slug']}-{_flat(a['rel'])}.html").write_text(render_data_view(p, a, projects, Ls), encoding="utf-8")
    return str(out_dir / "index.html")


# ---------------- live server ----------------
def _find(projects, slug):
    return next((p for p in projects if p["slug"] == slug), None)


def _artifact_by_rel(p, rel):
    return next((a for a in p["research"] + p["deliverables"] + p["inputs"] + p["data"] if a["rel"] == rel), None)


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype="text/html; charset=utf-8", code=200):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if not getattr(self, "_head_only", False):
            self.wfile.write(data)

    def do_HEAD(self):
        self._head_only = True
        try:
            self.route(urllib.parse.unquote(self.path.split("?")[0]))
        finally:
            self._head_only = False

    def do_GET(self):
        path = urllib.parse.unquote(self.path.split("?")[0])
        try:
            self.route(path)
        except Exception as e:  # noqa
            self._send(f"<pre>{esc(str(e))}</pre>", code=500)

    def route(self, path):
        Ls = L("live")
        projects = collect_projects()
        caps = collect_capabilities()
        if path in ("/", "/index.html"):
            return self._send(render_overview(projects, caps, Ls))
        if path == "/capabilities":
            return self._send(render_capabilities(projects, caps, Ls))
        if path.startswith("/skill/"):
            s = caps["skills_flat"].get(path[len("/skill/"):])
            return self._send(render_skill(s, projects, caps, Ls) if s else "Not found", code=200 if s else 404)
        if path.startswith("/playbook/"):
            nm = path[len("/playbook/"):]
            if (root() / "playbooks" / f"{nm}.md").exists():
                return self._send(render_playbook(nm, projects, Ls))
            return self._send("Not found", code=404)
        if path.startswith("/project/"):
            p = _find(projects, path[len("/project/"):])
            return self._send(render_project(p, projects, Ls) if p else "Not found", code=200 if p else 404)
        if path.startswith("/view/"):
            rest = path[len("/view/"):]
            slug, rel = rest.split("/", 1)
            p = _find(projects, slug)
            a = _artifact_by_rel(p, rel) if p else None
            return self._send(render_md_view(p, a, projects, Ls) if a else "Not found", code=200 if a else 404)
        if path.startswith("/page/"):
            rest = path[len("/page/"):]
            slug, rel = rest.split("/", 1)
            p = _find(projects, slug)
            a = _artifact_by_rel(p, rel) if p else None
            return self._send(render_page_view(p, a, projects, Ls) if a else "Not found", code=200 if a else 404)
        if path.startswith("/data/"):
            rest = path[len("/data/"):]
            slug, rel = rest.split("/", 1)
            p = _find(projects, slug)
            a = _artifact_by_rel(p, rel) if p else None
            return self._send(render_data_view(p, a, projects, Ls) if a else "Not found", code=200 if a else 404)
        if path.startswith("/raw/"):
            rest = path[len("/raw/"):]
            slug, rel = rest.split("/", 1)
            base = (root() / "projects" / slug).resolve()
            target = (base / rel).resolve()
            if str(target).startswith(str(base)) and target.is_file():
                ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
                if target.suffix.lower() in (".csv", ".txt", ".md", ".yml", ".yaml"):
                    ctype = "text/plain; charset=utf-8"
                return self._send(target.read_bytes(), ctype=ctype)
            return self._send("Not found", code=404)
        return self._send("Not found", code=404)


def serve(host="127.0.0.1", port=8787, out=None, open_browser=True):
    httpd = ThreadingHTTPServer((host, port), _Handler)
    url = f"http://{host}:{port}/"
    print(url, flush=True)
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return url


CSS = """
*{box-sizing:border-box}
:root{--bg:#f6f7f9;--panel:#fff;--line:#e8ebef;--line2:#f0f2f5;--ink:#0f172a;--ink2:#334155;
--muted:#64748b;--faint:#94a3b8;--brand:#2bbf77;--brand-ink:#0b7a47;--brand-soft:#e9f8f1;--navy:#0e2a47;
--ok-b:#e7f7ee;--ok-t:#0b7a47;--warn-b:#fdf0dd;--warn-t:#b45309;--danger-b:#fdeceb;--danger-t:#c0362c;
--info-b:#e9effe;--info-t:#2657d6;--mut-b:#eef1f5;--mut-t:#51607a;
--shadow:0 1px 2px rgba(15,23,42,.04),0 1px 3px rgba(15,23,42,.06);--shadow-h:0 8px 26px rgba(15,23,42,.10)}
html,body{margin:0}
body{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
color:var(--ink);background:var(--bg);font-size:14.5px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
code{font-family:ui-monospace,Menlo,monospace;font-size:.86em;background:var(--line2);padding:1px 5px;border-radius:5px}
.app{display:flex;min-height:100vh}
.sidebar{width:264px;flex:0 0 264px;background:var(--panel);border-right:1px solid var(--line);position:sticky;top:0;height:100vh;overflow:auto;padding:18px 14px;display:flex;flex-direction:column;gap:5px}
.brand{display:flex;gap:11px;align-items:center;padding:6px 8px 14px}
.brand .logo{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,var(--brand),#1ea968);color:#fff;display:grid;place-items:center;font-size:16px;box-shadow:var(--shadow)}
.brand b{display:block;font-size:14px;letter-spacing:-.2px}.brand small{color:var(--faint);font-size:11.5px}
.nav-item{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:9px;color:var(--ink2);font-weight:550;font-size:13.5px;transition:background .12s,color .12s}
.nav-item i{width:17px;height:17px;display:inline-flex;color:var(--faint)}.nav-item i svg{width:17px;height:17px}
.nav-item:hover{background:var(--line2)}.nav-item.active{background:var(--brand-soft);color:var(--brand-ink)}.nav-item.active i{color:var(--brand-ink)}
.nav-item.proj{font-size:13px;padding:7px 10px}
.dot{width:8px;height:8px;border-radius:50%;flex:0 0 8px;display:inline-block;background:var(--faint)}
.dot.ok{background:#22c55e}.dot.warn{background:#f59e0b}.dot.danger{background:#ef4444}.dot.info{background:#3b82f6}.dot.muted{background:#cbd5e1}
.nav-sec{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--faint);font-weight:700;padding:14px 10px 4px;display:flex;justify-content:space-between}
.nav-sec .cnt{background:var(--line2);color:var(--muted);border-radius:20px;padding:0 7px;font-size:10.5px}
.side-foot{margin-top:auto;color:var(--faint);font-size:11px;padding:12px 8px 2px;line-height:1.6}
.livedot{width:7px;height:7px;border-radius:50%;background:#22c55e;display:inline-block;margin-right:4px;box-shadow:0 0 0 3px rgba(34,197,94,.18)}
.main{flex:1;min-width:0;padding:26px 34px 60px;max-width:1180px}
.pagehead{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}
.pagehead h1{font-size:23px;margin:2px 0 3px;letter-spacing:-.4px}.pagehead .sub{color:var(--muted);margin:0;font-size:13.5px}
.stamp{color:var(--faint);font-size:12px;white-space:nowrap}
.back{display:inline-flex;align-items:center;gap:6px;color:var(--muted);font-size:12.5px;font-weight:600;margin-bottom:8px}
.back i{width:15px;height:15px}.back i svg{width:15px;height:15px}.back:hover{color:var(--brand-ink)}
.lead{color:var(--ink2);font-size:15.5px;margin:0}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:18px;box-shadow:var(--shadow)}
.compact-panel{margin-bottom:0}
.panel-head{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:14px}
.panel-head h2{font-size:15px;margin:0;letter-spacing:-.2px}
.panel-head .cnt{background:var(--mut-b);color:var(--mut-t);border-radius:20px;padding:1px 9px;font-size:12px;font-weight:700}
.link{color:var(--brand-ink);font-weight:600;font-size:13px}.muted{color:var(--muted)}.small{font-size:12.5px}
/* executive snapshot */
.exec-hero{background:linear-gradient(135deg,#0e2a47,#173f5f);color:#fff;border-radius:18px;padding:26px;margin-bottom:18px;display:grid;grid-template-columns:1.05fr 1.6fr;gap:24px;box-shadow:0 16px 42px rgba(14,42,71,.18)}
.exec-copy .eyebrow{color:#9bc8dd}.exec-copy h2{font-size:28px;line-height:1.05;margin:6px 0 10px;letter-spacing:-.7px}
.exec-copy p{color:#d9e8f0;margin:0;max-width:520px}
.exec-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.exec-metric{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.18);border-radius:13px;padding:13px 14px;min-height:96px;backdrop-filter:blur(4px)}
.exec-metric strong{display:block;font-size:26px;line-height:1;letter-spacing:-.5px}
.exec-metric span{display:block;color:#dbe8f0;font-size:12px;margin-top:7px;text-transform:uppercase;letter-spacing:.05em;font-weight:700}
.exec-metric small{display:block;color:#a8cfdf;font-size:12px;margin-top:7px;line-height:1.35}
.exec-metric.warn{background:rgba(245,158,11,.16);border-color:rgba(245,158,11,.34)}
.exec-metric.ok{background:rgba(34,197,94,.14);border-color:rgba(34,197,94,.30)}
.exec-metric.info{background:rgba(59,130,246,.14);border-color:rgba(59,130,246,.30)}
.overview-split{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px}
.stage-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.stage-step{background:var(--bg);border:1px solid var(--line);border-radius:11px;padding:12px}
.stage-top{display:flex;align-items:baseline;gap:7px;margin-bottom:10px}.stage-top b{font-size:23px;letter-spacing:-.4px}.stage-top span{color:var(--muted);font-size:12px;font-weight:700}
.stage-bar{height:7px;background:var(--line2);border-radius:999px;overflow:hidden}.stage-bar i{display:block;height:100%;background:linear-gradient(90deg,var(--brand),#1ea968);border-radius:999px}
.attention-list{display:flex;flex-direction:column;gap:7px}.attention-row{display:grid;grid-template-columns:auto minmax(0,1fr) minmax(150px,.8fr);gap:10px;align-items:center;border:1px solid var(--line);background:var(--bg);border-radius:10px;padding:9px 11px}
.attention-row:hover{border-color:var(--brand);background:#fff}.attention-row b{font-size:13px}.attention-row span{display:block;color:var(--muted);font-size:12px}.attention-row small{color:var(--faint);font-size:11.5px;line-height:1.35}
.attention-empty{background:var(--brand-soft);color:var(--brand-ink);border-radius:10px;padding:12px 14px;font-weight:700;font-size:13px}
/* overview tiles */
.tiles{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
.tile{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:14px 15px;display:block;transition:border-color .12s,transform .12s,box-shadow .12s}
.tile:hover{border-color:var(--brand);transform:translateY(-2px);box-shadow:var(--shadow)}
.tile b{display:block;font-size:25px;letter-spacing:-.5px;line-height:1}
.tile .tl{display:block;font-weight:650;font-size:13px;margin-top:7px}
.tile .td{display:block;color:var(--muted);font-size:11.5px;margin-top:3px;line-height:1.4}
/* layers explainer */
.layers{display:flex;flex-direction:column;gap:10px}
.layer{display:flex;gap:16px;align-items:stretch;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--panel)}
.layer-n{flex:0 0 130px;background:var(--bg);padding:14px 16px;display:flex;flex-direction:column;justify-content:center;border-right:1px solid var(--line)}
.layer-n b{font-size:24px;letter-spacing:-.5px}.layer-n span{color:var(--brand-ink);font-weight:650;font-size:13px}
.layer-b{padding:13px 16px}.layer-b strong{font-size:14px}.layer-b p{margin:3px 0 7px;color:var(--ink2);font-size:13px}
.ex{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:var(--muted);background:var(--line2);padding:3px 8px;border-radius:6px;display:inline-block}
/* skills grid */
.capsec{margin-bottom:18px}
.capsec-head{display:flex;align-items:baseline;gap:10px;margin-bottom:10px;flex-wrap:wrap}
.capsec-head h3{font-size:14px;margin:0}.capsec-head span{color:var(--muted);font-size:12.5px}
.scgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
.skillcard{border:1px solid var(--line);border-radius:11px;padding:13px 14px;background:var(--bg);display:block;transition:border-color .12s,transform .12s,box-shadow .12s}
.skillcard:hover{border-color:var(--brand);background:#fff;transform:translateY(-2px);box-shadow:var(--shadow)}
.sc-head{display:flex;align-items:center;justify-content:space-between}
.sc-head b{font-size:13.5px}.sc-head .go{width:15px;height:15px;color:var(--faint)}.sc-head .go svg{width:15px;height:15px}
.skillcard:hover .go{color:var(--brand-ink)}
.skillcard p{margin:5px 0 0;color:var(--muted);font-size:12.5px;line-height:1.5}
.cap2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.caprow{display:flex;gap:12px;padding:9px 2px;border-bottom:1px solid var(--line2)}
.caprow:last-child{border-bottom:0}.caprow b{flex:0 0 150px;font-size:13px}.caprow span{color:var(--muted);font-size:12.5px}
/* skill detail */
.skill-hero{display:flex;flex-direction:column;gap:10px;margin-bottom:8px}
.badge-skill{align-self:flex-start;background:var(--brand-soft);color:var(--brand-ink);font-weight:800;font-size:10.5px;letter-spacing:.08em;padding:4px 9px;border-radius:6px}
.kv{padding:14px 0 4px;border-top:1px solid var(--line2);margin-top:12px}
.kv>span{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--faint);font-weight:700;margin-bottom:8px}
.kv p{margin:0;color:var(--ink2)}
.trigs{display:flex;flex-wrap:wrap;gap:7px}
.trig{background:var(--bg);border:1px solid var(--line);border-radius:20px;padding:4px 11px;font-size:12px;color:var(--ink2)}
/* search,pills,grid,cards (shared) */
.search{border:1px solid var(--line);background:var(--bg);border-radius:9px;padding:7px 12px;font-size:13px;width:230px;color:var(--ink);outline:none}
.search:focus{border-color:var(--brand);background:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;display:block;box-shadow:var(--shadow);transition:transform .14s,box-shadow .14s,border-color .14s}
.card.project:hover{transform:translateY(-3px);box-shadow:var(--shadow-h);border-color:#dfe4ea}
.card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.card-top h3{font-size:17px;margin:2px 0 0;letter-spacing:-.3px}
.eyebrow{text-transform:uppercase;letter-spacing:.07em;font-size:10.5px;color:var(--faint);font-weight:700}
.muted-line{color:var(--muted);font-size:12.5px;margin:8px 0 0}
.card-desc{color:var(--ink2);font-size:13px;margin:8px 0 12px;min-height:34px}
.chips{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:13px}
.chip{background:var(--bg);border:1px solid var(--line);border-radius:7px;padding:4px 9px;font-size:12px;color:var(--muted)}.chip b{color:var(--ink);font-weight:700}
.bar{height:6px;background:var(--line2);border-radius:20px;overflow:hidden;margin-bottom:11px}
.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--brand),#1ea968);border-radius:20px}
.card-foot{display:flex;justify-content:space-between;font-size:12px;color:var(--muted)}.card-foot .go{color:var(--brand-ink);font-weight:700}
.pill{display:inline-flex;align-items:center;height:23px;padding:0 9px;border-radius:20px;font-size:11.5px;font-weight:700;white-space:nowrap}
.pill.ok{background:var(--ok-b);color:var(--ok-t)}.pill.warn{background:var(--warn-b);color:var(--warn-t)}.pill.danger{background:var(--danger-b);color:var(--danger-t)}.pill.info{background:var(--info-b);color:var(--info-t)}.pill.muted{background:var(--mut-b);color:var(--mut-t)}
/* project detail */
.phead{margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.phead-main{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.phead-ring{display:flex;align-items:center;gap:10px;color:var(--muted);font-size:12px;font-weight:650;text-transform:uppercase;letter-spacing:.04em}
.headline-quote{font-size:18px;font-weight:600;color:var(--navy);line-height:1.45;margin:0 0 18px;padding:16px 20px;background:var(--brand-soft);border-radius:14px}
.pill.stagepill{background:var(--accent-soft,var(--mut-b));color:var(--accent,var(--mut-t))}
.ring text{font-family:Inter,ui-sans-serif,system-ui,sans-serif}
.ring-foot{display:flex;align-items:center;justify-content:space-between;gap:10px}
.ring-combo{display:flex;align-items:center;gap:10px;font-size:12px;color:var(--muted);font-weight:600}
.ring-combo .ring{flex:0 0 auto}
.activity-list{display:flex;flex-direction:column;gap:2px}
.activity-row{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:10px 4px;border-bottom:1px solid var(--line2);transition:background .12s}
.activity-row:last-child{border-bottom:0}
.activity-row:hover{background:var(--bg)}
.activity-main{min-width:0;display:flex;flex-direction:column}
.activity-main b{font-size:13px;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.activity-main span{font-size:11.5px;color:var(--faint);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.activity-when{flex:0 0 auto;font-size:11.5px;color:var(--faint);font-variant-numeric:tabular-nums}
.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin-bottom:18px}
.facts>div{background:var(--panel);padding:12px 14px}.facts .wide{grid-column:span 4}
.facts span{display:block;color:var(--faint);font-size:11px;text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px}
.facts b{font-weight:600;font-size:13.5px}.facts a{color:var(--brand-ink)}
.pgroup{margin-top:14px}
.pglabel{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--faint);font-weight:700;margin:6px 0 8px;display:flex;gap:8px;align-items:center}
.pglabel span{background:var(--line2);color:var(--muted);border-radius:20px;padding:0 7px;font-size:10.5px}
.pagegrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:9px}
.pagecard{display:flex;justify-content:space-between;align-items:center;gap:10px;border:1px solid var(--line);border-radius:10px;padding:11px 13px;background:var(--bg)}
.pagecard:hover{border-color:#dfe4ea;background:#fff}
.pc-main{min-width:0}.pc-main b{display:block;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pc-main span{color:var(--faint);font-size:11px;font-family:ui-monospace,Menlo,monospace}
.pc-act{display:flex;gap:6px;flex:0 0 auto}
.mini{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:600;color:var(--brand-ink);background:var(--brand-soft);padding:5px 9px;border-radius:7px}
.mini.ghost{color:var(--ink2);background:var(--panel);border:1px solid var(--line)}
.mini i{width:13px;height:13px}.mini i svg{width:13px;height:13px}
.mini:hover{filter:brightness(.97)}
.filelist{display:grid;grid-template-columns:repeat(2,1fr);gap:7px}
.fitem{display:flex;align-items:center;gap:9px;padding:9px 11px;border:1px solid var(--line);border-radius:9px;background:var(--bg);font-size:13px;transition:border-color .12s,background .12s}
.fitem:hover{border-color:var(--brand);background:#fff}
.fitem i{width:15px;height:15px;color:var(--faint);flex:0 0 15px}.fitem i svg{width:15px;height:15px}
.fitem .fn{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--ink2);font-weight:550}
.fitem .ftag{font-size:10.5px;color:var(--faint);background:var(--line2);padding:1px 6px;border-radius:5px;text-transform:uppercase}
.readiness{display:flex;flex-direction:column;gap:2px}
.rdrow{display:flex;justify-content:space-between;align-items:center;padding:9px 2px;border-bottom:1px solid var(--line2)}.rdrow:last-child{border-bottom:0}
.rdn{display:flex;align-items:center;gap:9px;color:var(--ink2)}.rdrow b{font-variant-numeric:tabular-nums}
/* preview iframe */
.previewbar,.viewerbar{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:12px}
.vpath{color:var(--faint);font-size:12px;font-family:ui-monospace,Menlo,monospace}
.frame-wrap{border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:var(--shadow);background:#fff}
.preview{width:100%;height:78vh;border:0;display:block;background:#fff}
/* markdown */
.md{color:var(--ink2);font-size:14px;line-height:1.65}
.md h1{font-size:21px;margin:6px 0 12px;color:var(--ink)}
.md h2{font-size:17px;margin:22px 0 10px;color:var(--ink);padding-bottom:6px;border-bottom:1px solid var(--line)}
.md h3{font-size:15px;margin:18px 0 7px;color:var(--ink)}.md h4{font-size:13.5px;margin:14px 0 6px;color:var(--ink2)}
.md p{margin:0 0 11px}.md ul,.md ol{margin:0 0 12px;padding-left:22px}.md li{margin:4px 0}
.md table{border-collapse:collapse;width:100%;margin:4px 0 16px;font-size:13px;display:block;overflow-x:auto}
.md th,.md td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
.md th{background:var(--bg);font-weight:700;color:var(--ink)}.md tr:nth-child(even) td{background:#fcfdfe}
.md blockquote{margin:0 0 12px;padding:9px 15px;border-left:3px solid var(--brand);background:var(--brand-soft);border-radius:0 8px 8px 0;color:var(--ink2)}
.md pre{background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:10px;overflow-x:auto;font-size:12.5px;margin:0 0 14px}
.md pre code{background:none;color:inherit;padding:0}.md hr{border:0;border-top:1px solid var(--line);margin:18px 0}
.md a{color:var(--brand-ink);text-decoration:underline;text-underline-offset:2px}
.reader{max-width:1080px}.skillwrap{display:flex;flex-wrap:wrap;gap:7px}
.codeblock{background:#0f172a;color:#e2e8f0;padding:16px 18px;border-radius:10px;overflow-x:auto;font-size:12.5px;line-height:1.6;font-family:ui-monospace,Menlo,monospace;margin:0;white-space:pre-wrap;word-break:break-word}
/* color tokens (carried by filled badges + tag dots, never edge stripes) */
.c-violet{--accent:#7c5cff;--accent-soft:#f1edff}.c-blue{--accent:#3b76ff;--accent-soft:#e9f0ff}
.c-cyan{--accent:#0f9bb0;--accent-soft:#e1f5f8}.c-green{--accent:#16a34a;--accent-soft:#e7f7ee}
.c-amber{--accent:#e08405;--accent-soft:#fdf0db}.c-rose{--accent:#e0408f;--accent-soft:#fce7f1}.c-slate{--accent:#64748b;--accent-soft:#eef1f6}
.tile{display:flex;gap:12px;align-items:center;background:var(--panel)}
.tile:hover{border-color:var(--accent,var(--brand))}
.tnum{flex:0 0 auto;min-width:44px;height:44px;padding:0 11px;display:inline-flex;align-items:center;justify-content:center;background:var(--accent-soft,var(--line2));color:var(--accent,var(--ink));border-radius:12px;font-weight:800;font-size:20px;letter-spacing:-.5px}
.tmeta{min-width:0}.tmeta .tl{margin-top:0}
.layer .layer-n{background:var(--accent-soft,var(--bg))}
.layer .layer-n b{color:var(--accent,var(--ink))}.layer .layer-n span{color:var(--accent,var(--brand-ink))}
.capsec .capsec-head h3{display:flex;align-items:center;gap:9px}
.capsec .capsec-head h3::before{content:"";width:11px;height:11px;border-radius:4px;background:var(--accent,var(--brand));display:inline-block;flex:0 0 11px}
.capsec .skillcard:hover{border-color:var(--accent,var(--brand))}
.capsec .skillcard:hover .go{color:var(--accent,var(--brand-ink))}
.brand{cursor:pointer;border-radius:10px;transition:background .12s}.brand:hover{background:var(--line2)}
.skill{background:var(--bg);border:1px solid var(--line);border-radius:7px;padding:4px 10px;font-size:12.5px;color:var(--ink2)}
.skill:hover{border-color:var(--brand);color:var(--brand-ink)}
@media(max-width:1000px){.exec-hero,.overview-split{grid-template-columns:1fr}.exec-grid{grid-template-columns:repeat(2,1fr)}.stage-grid{grid-template-columns:repeat(2,1fr)}.tiles{grid-template-columns:repeat(2,1fr)}.cap2{grid-template-columns:1fr}.filelist{grid-template-columns:1fr}.facts{grid-template-columns:repeat(2,1fr)}.facts .wide{grid-column:span 2}.layer-n{flex-basis:110px}}
@media(max-width:760px){.app{flex-direction:column}.sidebar{position:static;width:100%;height:auto;flex-direction:row;flex-wrap:wrap;border-right:0;border-bottom:1px solid var(--line);align-items:center}.brand{flex:1 1 100%;padding:6px 8px}.nav-sec,.side-foot{display:none}.main{padding:20px 18px 50px}.pagehead{flex-direction:column;align-items:flex-start;gap:8px}.layer{flex-direction:column}.layer-n{flex-basis:auto;border-right:0;border-bottom:1px solid var(--line);flex-direction:row;gap:8px;align-items:baseline}}
@media(max-width:560px){.exec-grid,.stage-grid,.tiles{grid-template-columns:1fr}.attention-row{grid-template-columns:auto 1fr}.attention-row small{grid-column:2}.grid{grid-template-columns:1fr}.facts{grid-template-columns:1fr}.facts .wide{grid-column:span 1}}
"""

SEARCH_JS = """<script>function filterCards(){var q=(document.getElementById('search').value||'').toLowerCase();
document.querySelectorAll('#cards .project').forEach(function(c){c.style.display=(c.getAttribute('data-search')||'').indexOf(q)>-1?'':'none';});}</script>"""

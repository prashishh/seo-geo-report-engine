"""Render a growth-proposal spec (YAML/JSON) into a branded, charted PDF.

Division of labor: the model composes the *content* (a proposal.yml following
templates/proposal/proposal.schema.md); this renderer deterministically lays it
out with the brand palette + SVG charts and prints it via headless Chrome.

    ./bin/mkt proposal build --project demo
    ./bin/mkt proposal build --project demo --out /tmp/demo.pdf

Spec is found at (first hit): --in arg, projects/<p>/proposal.yml,
projects/<p>/research/proposal.yml.
"""
from __future__ import annotations

import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/

from charts import svg as C            # noqa: E402
from lib.config import load, load_yaml  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BRAND_KEYS = {"primary", "accent", "muted", "ink", "paper"}


# --------------------------------------------------------------------------- helpers
def _inline(s):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(str(s)))


def _bullets(items):
    return '<ul class="lead">' + "".join(f"<li>{_inline(b)}</li>" for b in (items or [])) + "</ul>"


def _head(num, title):
    chip = f'<span class="s-num">{escape(str(num))}</span>' if num not in (None, "") else ""
    return f'<div class="s-head">{chip}<h2 class="s-title">{escape(title)}</h2></div>'


def _chart(spec, brand):
    spec = dict(spec)
    t = spec.pop("type")
    fn = getattr(C, t, None)
    if not fn:
        return f'<div class="note">[unknown chart type: {escape(t)}]</div>'
    if "markers" in spec and isinstance(spec["markers"], dict):
        spec["markers"] = {int(k): v for k, v in spec["markers"].items()}
    for k in ("band", "highlight_range"):
        if isinstance(spec.get(k), list):
            spec[k] = tuple(spec[k])
    return fn(brand=brand, **spec)


def _figure(title, body, unit=None, note=None):
    head = ""
    if title or unit:
        head = (f'<div class="fhead"><span class="ftitle">{escape(title or "")}</span>'
                f'<span class="small">{escape(unit or "")}</span></div>')
    n = f'<div class="fnote">{_inline(note)}</div>' if note else ""
    return f'<div class="figure">{head}{body}{n}</div>'


def _kvtable(headers, rows, align=None):
    align = align or (["left"] + ["right"] * (len(headers) - 1))
    th = "".join(f'<th style="text-align:{align[i]}">{escape(str(h))}</th>' for i, h in enumerate(headers))
    trs = []
    for r in rows:
        if isinstance(r, dict) and "group" in r:
            trs.append(f'<tr class="group-row"><td colspan="{len(headers)}">{escape(str(r["group"]))}</td></tr>')
        else:
            tds = "".join(f'<td style="text-align:{align[i]}">{_inline(c)}</td>' for i, c in enumerate(r))
            trs.append(f"<tr>{tds}</tr>")
    return f'<table class="kv"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'


# --------------------------------------------------------------------------- sections
def render_section(sec, brand):
    t = sec.get("type")
    num, title = sec.get("num", ""), sec.get("title", "")
    brk = " break" if sec.get("page_break") else ""

    if t == "summary":
        cards = ""
        for p in sec.get("pillars", []):
            items = "".join(f"<li>{_inline(i)}</li>" for i in p.get("items", []))
            when = f'<div class="when">{escape(p["when"])}</div>' if p.get("when") else ""
            cards += (f'<div class="pillar"><div class="cap"><div class="tag">{escape(p.get("tag",""))}</div>'
                      f'<div class="name">{escape(p.get("name",""))}</div>{when}</div><ul>{items}</ul></div>')
        return (f'<div class="section{brk}">{_head(num or "00", title or "Executive summary")}'
                f'{_bullets(sec.get("bullets"))}<div class="spacer"></div>'
                f'<div class="pillars">{cards}</div></div>')

    if t == "prose":
        body = _bullets(sec.get("bullets")) if sec.get("bullets") else ""
        for para in sec.get("paragraphs", []):
            body += f"<p>{_inline(para)}</p>"
        if sec.get("callout"):
            body += f'<div class="callout">{_inline(sec["callout"])}</div>'
        if sec.get("chart"):
            body += _figure(sec.get("figure_title"), _chart(sec["chart"], brand),
                            sec.get("figure_unit"), sec.get("figure_note"))
        return f'<div class="section{brk}">{_head(num, title)}{body}</div>'

    if t == "pillars_detail":
        body = ""
        for g in sec.get("groups", []):
            d = ""
            if g.get("deliverables"):
                lis = "".join(f"<li>{_inline(x)}</li>" for x in g["deliverables"])
                d = f'<div class="deliverables"><div class="lbl">Deliverables</div><ul class="lead">{lis}</ul></div>'
            body += (f'<div class="group"><h4>{escape(g.get("name",""))}</h4>'
                     f'{_bullets(g.get("bullets"))}{d}</div>')
        return f'<div class="section{brk}">{_head(num, title)}{body}</div>'

    if t == "roadmap":
        gantt = _chart({"type": "gantt", **sec["gantt"]}, brand) if sec.get("gantt") else ""
        return (f'<div class="section{brk}">{_head(num, title)}'
                f'{_figure(sec.get("figure_title","Workstream timeline"), gantt, sec.get("figure_unit"), sec.get("note"))}</div>')

    if t == "scenarios":
        body = _bullets(sec.get("bullets")) if sec.get("bullets") else ""
        if sec.get("chart"):
            body += _figure(sec.get("figure_title"), _chart(sec["chart"], brand),
                            sec.get("figure_unit"), sec.get("figure_note"))
        if sec.get("table"):
            body += _kvtable(sec["table"]["headers"], sec["table"]["rows"], sec["table"].get("align"))
        if sec.get("note"):
            body += f'<div class="note">{_inline(sec["note"])}</div>'
        return f'<div class="section{brk}">{_head(num, title)}{body}</div>'

    if t == "scorecards":
        cards = _chart({"type": "scorecards", "cards": sec["cards"], "cols": sec.get("cols", 4)}, brand)
        return f'<div class="section{brk}">{_head(num, title)}{cards}</div>'

    if t == "table":
        body = _kvtable(sec["table"]["headers"], sec["table"]["rows"], sec["table"].get("align"))
        if sec.get("note"):
            body += f'<div class="note">{_inline(sec["note"])}</div>'
        return f'<div class="section{brk}">{_head(num, title)}{body}</div>'

    if t == "cta":
        contact = f'<p class="small" style="color:#cdd8e4">{_inline(sec.get("contact",""))}</p>' if sec.get("contact") else ""
        return (f'<div class="section{brk}"><div class="cta"><h3>{escape(title)}</h3>'
                f'<p>{_inline(sec.get("body",""))}</p>{contact}</div></div>')

    return f'<div class="section{brk}">{_head(num, title)}<div class="note">[unknown section: {escape(str(t))}]</div></div>'


def _cover(meta):
    badge = escape(meta.get("badge", "Growth Proposal"))
    client = escape(meta.get("client", ""))
    sub = f'<p class="sub">{escape(meta["subtitle"])}</p>' if meta.get("subtitle") else ""
    foot = " · ".join(x for x in [meta.get("date"), meta.get("author")] if x)
    return (f'<div class="cover"><div class="kicker"><span class="brandmark">{client}</span>'
            f'<span>{badge}</span></div><h1>{escape(meta.get("title","Growth Proposal"))}</h1>{sub}'
            f'<hr class="rule"><p class="small">{escape(foot)}</p></div>')


def _css(brand):
    base = (ROOT / "templates" / "proposal" / "base.css").read_text(encoding="utf-8")
    overrides = "".join(f"--{k}:{brand[k]};" for k in BRAND_KEYS if brand.get(k))
    if brand.get("font_stack"):
        overrides += f"--font:{brand['font_stack']};"
    return base + f"\n:root{{{overrides}}}"


# Opt-in compact mode (`meta.dense: true`): removes the full-page cover break and the
# per-section page-break-avoid (the two biggest sources of trailing white space), and
# tightens type/spacing so a data-heavy report packs into fewer pages. Figures, tables,
# and pillar/card blocks still avoid mid-break so nothing splits awkwardly.
DENSE_CSS = """
.dense .cover{ page-break-after:auto; padding-top:0; }
.dense .cover h1{ font-size:30px; margin:8px 0 6px; }
.dense .cover .rule{ margin:12px 0 18px; }
.dense .section{ page-break-inside:auto; margin:0 0 15px; }
.dense .s-head{ margin-bottom:9px; padding-bottom:6px; }
.dense .s-title{ font-size:17px; }
.dense p{ margin:5px 0; font-size:12px; line-height:1.5; }
.dense ul.lead li{ padding:3px 0 3px 18px; font-size:12px; line-height:1.45; }
.dense .figure{ margin:8px 0; padding:10px 12px; page-break-inside:avoid; }
.dense .pillars, .dense table.kv, .dense .pillar, .dense .deliverables, .dense .callout{ page-break-inside:avoid; }
.dense table.kv td{ padding:4px 8px; font-size:11px; }
.dense table.kv th{ padding:6px 8px; font-size:11px; }
.dense .callout{ margin:8px 0; padding:8px 12px; }
.dense .group{ margin:9px 0; }
.dense .pillar li{ font-size:11px; padding:3px 0 3px 14px; }
.dense .cta{ padding:18px 20px; }
.dense .note, .dense .figure .fnote{ font-size:10.5px; margin-top:6px; }
"""


def render_html(spec, brand):
    meta = spec.get("meta", {})
    dense = bool(meta.get("dense"))
    body_attr = " class='dense'" if dense else ""
    extra = DENSE_CSS if dense else ""
    sections = "".join(render_section(s, brand) for s in spec.get("sections", []) if s.get("type") != "cover")
    # Offline-first: rely on the system font stack (--font). No remote font fetch
    # (that makes headless Chrome hang). Drop an Inter .woff2 into templates/proposal/fonts
    # and @font-face it in base.css if you want pixel-identical Inter across machines.
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{_css(brand)}{extra}</style></head><body{body_attr}>{_cover(meta)}{sections}</body></html>"
    )


def _find_spec(cfg, src):
    if src:
        return Path(src)
    if cfg.project_dir:
        for cand in (cfg.project_dir / "proposal.yml",
                     cfg.project_dir / "research" / "proposal.yml",
                     cfg.project_dir / "proposal.json"):
            if cand.exists():
                return cand
    raise FileNotFoundError("No proposal spec found. Pass --in or create projects/<p>/proposal.yml")


def render_file(src, out=None, project=None):
    """Render ANY sections spec (proposal / report / comparison) to PDF. Used by `doc build`."""
    cfg = load(project)
    spec = load_yaml(src)
    html = render_html(spec, cfg.brand())
    pdf_path = Path(out) if out else Path.cwd() / (Path(src).stem + ".pdf")
    html_path = pdf_path.with_suffix(".html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    from pdf.render import html_to_pdf
    html_to_pdf(html_path, pdf_path)
    return str(pdf_path)


def build(project=None, out=None, src=None):
    cfg = load(project)
    spec_path = _find_spec(cfg, src)
    if not out and cfg.project_dir:
        slug = cfg.get("slug") or cfg.project
        out = str(cfg.project_dir / "deliverables" / f"{slug}-growth-proposal.pdf")
    return render_file(spec_path, out=out, project=project)

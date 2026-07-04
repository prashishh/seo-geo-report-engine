"""Pure-Python inline-SVG chart kit (stdlib only).

Reproduces the chart types in the reference growth decks:
    bar_h        - horizontal bars (occupation mix, market funnel)
    bar_v        - vertical columns, optional highlighted range (seasonality)
    lines        - multi-series projection lines with markers + shaded band
    stacked_cols - stacked columns (acquisition-mix shift)
    gantt        - workstream activity-intensity timeline
    scorecards   - KPI number cards
    table        - simple data table (for PDF; Ahrefs render-* is for chat)

Every function returns a self-contained <svg> string (colors inlined) that drops
straight into an HTML template for Chrome -> PDF. Pass a `brand` palette dict
(see config framework.yml) or rely on the defaults.
"""
from __future__ import annotations

from html import escape

DEFAULT = {
    "primary": "#0E2A47",
    "accent": "#2BBF77",
    "muted": "#7C8DA0",
    "ink": "#1B2733",
    "paper": "#FFFFFF",
    "grid": "#E6EBF0",
    "band": "#FFF4CC",
}
# Ordered series colors (navy -> teal -> green -> grays), matching the decks.
SERIES = ["#0E2A47", "#1F6F8B", "#2BBF77", "#7C8DA0", "#9FB1C1", "#C5D0DB"]


def _p(brand=None):
    p = dict(DEFAULT)
    if brand:
        p.update({k: v for k, v in brand.items() if v})
    return p


def fmt(v, kind=None):
    if kind == "pct":
        return f"{v:.1f}%"
    if kind == "usd":
        a = abs(v)
        if a >= 1_000_000_000:
            return f"${v/1e9:.1f}B"
        if a >= 1_000_000:
            return f"${v/1e6:.1f}M"
        if a >= 1_000:
            return f"${v/1e3:.0f}K"
        return f"${v:,.0f}"
    if kind == "compact":
        a = abs(v)
        if a >= 1_000_000:
            return f"{v/1e6:.1f}M"
        if a >= 1_000:
            return f"{v/1e3:.0f}K"
        return f"{v:,.0f}"
    if isinstance(v, float):
        return f"{v:,.1f}"
    return f"{v:,}"


def _txt(x, y, s, size=13, fill="#1B2733", anchor="start", weight="400", opacity=1.0):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}" opacity="{opacity}" '
        f'font-family="Inter, -apple-system, Segoe UI, Roboto, Arial, sans-serif">{escape(str(s))}</text>'
    )


def _open(w, h, title=None, subtitle=None, brand=None):
    p = _p(brand)
    s = [
        f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Inter, -apple-system, Segoe UI, Roboto, Arial, sans-serif">',
        f'<rect width="{w}" height="{h}" fill="{p["paper"]}"/>',
    ]
    if title:
        s.append(_txt(0, 22, title, size=17, fill=p["ink"], weight="700"))
    if subtitle:
        s.append(_txt(w, 20, subtitle.upper(), size=10, fill=p["muted"], anchor="end", weight="600"))
    return s, p


# --------------------------------------------------------------------------- bars
def bar_h(rows, title=None, subtitle=None, kind="compact", brand=None,
          w=720, row_h=34, pad_left=150, highlight=None):
    """rows: list of (label, value). highlight: label to accent."""
    s, p = _open(w, 60 + row_h * len(rows), title, subtitle, brand)
    top = 48
    vmax = max((v for _, v in rows), default=1) or 1
    plot_w = w - pad_left - 70
    for i, (label, val) in enumerate(rows):
        y = top + i * row_h
        bw = max(2, plot_w * (val / vmax))
        color = p["accent"] if (highlight and label == highlight) else p["primary"]
        s.append(_txt(pad_left - 10, y + row_h * 0.62, label, size=12, fill=p["ink"], anchor="end"))
        s.append(f'<rect x="{pad_left}" y="{y+6}" width="{bw:.1f}" height="{row_h-14}" rx="3" fill="{color}"/>')
        s.append(_txt(pad_left + bw + 8, y + row_h * 0.62, fmt(val, kind), size=12, fill=p["muted"], weight="600"))
    s.append("</svg>")
    return "\n".join(s)


def bar_v(rows, title=None, subtitle=None, kind="compact", brand=None,
          w=720, h=300, highlight_range=None, band_label=None):
    """rows: list of (label, value). highlight_range: (start_idx, end_idx) inclusive."""
    s, p = _open(w, h, title, subtitle, brand)
    top, bottom, left = 50, h - 34, 44
    vmax = max((v for _, v in rows), default=1) or 1
    n = len(rows)
    plot_w = w - left - 16
    gap = plot_w / n
    bw = gap * 0.6
    if highlight_range:
        a, b = highlight_range
        x0 = left + a * gap
        x1 = left + (b + 1) * gap
        s.append(f'<rect x="{x0:.1f}" y="{top-14}" width="{x1-x0:.1f}" height="{bottom-top+14}" fill="{p["band"]}"/>')
        if band_label:
            s.append(_txt((x0 + x1) / 2, top - 18, band_label, size=10, fill=p["muted"], anchor="middle", weight="600"))
    for i, (label, val) in enumerate(rows):
        x = left + i * gap + (gap - bw) / 2
        bh = (bottom - top) * (val / vmax)
        inside = highlight_range and highlight_range[0] <= i <= highlight_range[1]
        color = p["primary"] if inside else p["muted"]
        s.append(f'<rect x="{x:.1f}" y="{bottom-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="2" fill="{color}"/>')
        s.append(_txt(x + bw / 2, bottom + 16, label, size=10, fill=p["muted"], anchor="middle"))
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------------------- lines
def lines(series, x_labels, title=None, subtitle=None, kind="usd", brand=None,
          w=720, h=360, band=None, markers=None):
    """series: dict name->[values]; band: (start_idx,end_idx) shaded; markers: {idx:label}."""
    s, p = _open(w, h, title, subtitle, brand)
    top, bottom, left, right = 54, h - 40, 56, w - 58  # right gutter holds end-of-line value labels
    allv = [v for vs in series.values() for v in vs]
    vmax = max(allv) if allv else 1
    vmin = min(0, min(allv) if allv else 0)
    n = len(x_labels)
    xs = [left + (right - left) * (i / (n - 1 if n > 1 else 1)) for i in range(n)]

    def yf(v):
        return bottom - (bottom - top) * ((v - vmin) / (vmax - vmin or 1))

    # gridlines + y labels
    for g in range(5):
        gv = vmin + (vmax - vmin) * g / 4
        gy = yf(gv)
        s.append(f'<line x1="{left}" y1="{gy:.1f}" x2="{right}" y2="{gy:.1f}" stroke="{p["grid"]}" stroke-width="1"/>')
        s.append(_txt(left - 8, gy + 4, fmt(gv, kind), size=10, fill=p["muted"], anchor="end"))
    if band:
        s.append(f'<rect x="{xs[band[0]]:.1f}" y="{top}" width="{xs[band[1]]-xs[band[0]]:.1f}" '
                 f'height="{bottom-top}" fill="{p["band"]}" opacity="0.7"/>')
    if markers:
        for idx, lab in markers.items():
            s.append(f'<line x1="{xs[idx]:.1f}" y1="{top}" x2="{xs[idx]:.1f}" y2="{bottom}" '
                     f'stroke="{p["muted"]}" stroke-width="1" stroke-dasharray="3 3" opacity="0.5"/>')
            s.append(_txt(xs[idx], top - 6, lab, size=9, fill=p["muted"], anchor="middle", weight="600"))
    for x, lab in zip(xs, x_labels):
        s.append(_txt(x, bottom + 16, lab, size=10, fill=p["muted"], anchor="middle"))
    for k, (name, vs) in enumerate(series.items()):
        color = SERIES[k % len(SERIES)]
        pts = " ".join(f"{x:.1f},{yf(v):.1f}" for x, v in zip(xs, vs))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
        for x, v in zip(xs, vs):
            s.append(f'<circle cx="{x:.1f}" cy="{yf(v):.1f}" r="3.2" fill="{color}"/>')
        s.append(_txt(xs[-1] + 6, yf(vs[-1]) + 4, fmt(vs[-1], kind), size=10, fill=color, weight="700"))
    # legend
    lx = left
    for k, name in enumerate(series.keys()):
        color = SERIES[k % len(SERIES)]
        s.append(f'<rect x="{lx}" y="{h-22}" width="14" height="3" rx="1.5" fill="{color}"/>')
        s.append(_txt(lx + 20, h - 18, name, size=10, fill=p["ink"]))
        lx += 26 + len(name) * 7
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------------------- stacked
def stacked_cols(columns, title=None, subtitle=None, brand=None, w=720, h=340, kind="pct"):
    """columns: list of (col_label, [(seg_label, value), ...]). Values stack to 100%-ish."""
    s, p = _open(w, h, title, subtitle, brand)
    top, bottom, left = 50, h - 30, 16
    n = len(columns)
    plot_w = w - left - 16
    gap = plot_w / n
    bw = gap * 0.62
    seg_names = [seg for _, segs in columns for seg, _ in segs]
    order = list(dict.fromkeys(seg_names))
    cmap = {name: SERIES[i % len(SERIES)] for i, name in enumerate(order)}
    for i, (clabel, segs) in enumerate(columns):
        total = sum(v for _, v in segs) or 1
        x = left + i * gap + (gap - bw) / 2
        y = top
        for seg, v in segs:
            seg_h = (bottom - top) * (v / total)
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{seg_h:.1f}" fill="{cmap[seg]}"/>')
            if seg_h > 16:
                s.append(_txt(x + bw / 2, y + seg_h / 2 + 4, f"{seg} {fmt(v, kind)}",
                              size=9, fill="#FFFFFF", anchor="middle", weight="600"))
            y += seg_h
        s.append(_txt(x + bw / 2, bottom + 16, clabel, size=10, fill=p["muted"], anchor="middle", weight="600"))
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------------------- gantt
def gantt(rows, months, title=None, subtitle=None, brand=None, w=720, row_h=26, legend=None):
    """rows: list of (label, [intensity per month]) where intensity in 0..3 (0=blank).
    legend: optional list of (level_name) for 1,2,3."""
    s, p = _open(w, 60 + row_h * len(rows) + 24, title, subtitle, brand)
    top, left = 52, 150
    plot_w = w - left - 16
    n = len(months)
    cw = plot_w / n
    shades = {1: p["muted"], 2: "#1F6F8B", 3: p["primary"]}
    for j, m in enumerate(months):
        s.append(_txt(left + j * cw + cw / 2, top - 8, m, size=10, fill=p["muted"], anchor="middle", weight="600"))
    for i, (label, vals) in enumerate(rows):
        y = top + i * row_h
        s.append(_txt(left - 10, y + row_h * 0.62, label, size=11, fill=p["ink"], anchor="end"))
        for j, lv in enumerate(vals):
            if lv:
                x = left + j * cw
                s.append(f'<rect x="{x+2:.1f}" y="{y+5}" width="{cw-4:.1f}" height="{row_h-12}" rx="3" fill="{shades.get(lv, p["muted"])}"/>')
    if legend:
        ly = top + row_h * len(rows) + 16
        lx = left
        for lv, name in enumerate(legend, start=1):
            s.append(f'<rect x="{lx}" y="{ly-10}" width="14" height="10" rx="2" fill="{shades.get(lv, p["muted"])}"/>')
            s.append(_txt(lx + 20, ly, name, size=10, fill=p["ink"]))
            lx += 36 + len(name) * 7
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------------------- scorecards
def scorecards(cards, brand=None, w=720, cols=4, card_h=92):
    """cards: list of dicts {label, value, delta?(str), good?(bool)}."""
    p = _p(brand)
    rows = (len(cards) + cols - 1) // cols
    h = rows * (card_h + 12)
    gap = 12
    cw = (w - gap * (cols - 1)) / cols
    s = [f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" '
         f'font-family="Inter, -apple-system, Segoe UI, Roboto, Arial, sans-serif">']
    for i, c in enumerate(cards):
        r, col = divmod(i, cols)
        x = col * (cw + gap)
        y = r * (card_h + 12)
        s.append(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{card_h}" rx="10" fill="#F6F8FA" stroke="{p["grid"]}"/>')
        s.append(_txt(x + 16, y + 28, c["label"].upper(), size=10, fill=p["muted"], weight="600"))
        s.append(_txt(x + 16, y + 60, c["value"], size=26, fill=p["primary"], weight="700"))
        if c.get("delta"):
            color = p["accent"] if c.get("good", True) else "#D1495B"
            s.append(_txt(x + 16, y + 80, c["delta"], size=11, fill=color, weight="600"))
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------------------- table
def table(headers, rows, brand=None, w=720, align=None):
    p = _p(brand)
    align = align or ["left"] * len(headers)
    th = "".join(
        f'<th style="text-align:{align[i]};padding:8px 10px;border-bottom:2px solid {p["primary"]};'
        f'font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:{p["muted"]}">{escape(str(h))}</th>'
        for i, h in enumerate(headers)
    )
    trs = []
    for r in rows:
        tds = "".join(
            f'<td style="text-align:{align[i]};padding:7px 10px;border-bottom:1px solid {p["grid"]};'
            f'font-size:12.5px;color:{p["ink"]}">{escape(str(c))}</td>'
            for i, c in enumerate(r)
        )
        trs.append(f"<tr>{tds}</tr>")
    return (f'<table style="width:100%;border-collapse:collapse;'
            f'font-family:Inter,-apple-system,Segoe UI,Roboto,Arial,sans-serif">'
            f"<thead><tr>{th}</tr></thead><tbody>{''.join(trs)}</tbody></table>")


# --------------------------------------------------------------------------- opportunity matrix
TIER_COLOR = {"greenfield": "#2BBF77", "contested": "#1F6F8B", "fortress": "#7C8DA0", "trap": "#E1526B"}


def bubble(points, title=None, subtitle=None, brand=None, w=720, h=440,
           x_label="WINNABILITY", y_label="DEMAND"):
    """2x2 opportunity matrix. points: [{label, x(0-100 winnability), y(0-100 demand),
    size(value for bubble area), tier}]. The top-right (high demand + high win) is the greenfield zone."""
    s, p = _open(w, h, title, subtitle, brand)
    left, right, top, bot = 60, w - 24, 46, h - 46
    pw, ph = right - left, bot - top
    def px(x): return left + pw * (max(0, min(100, x)) / 100)
    def py(y): return bot - ph * (max(0, min(100, y)) / 100)
    # greenfield quadrant tint (top-right) + quadrant split lines
    s.append(f'<rect x="{px(50):.1f}" y="{py(100):.1f}" width="{px(100)-px(50):.1f}" '
             f'height="{py(50)-py(100):.1f}" fill="#2BBF77" opacity="0.07"/>')
    s.append(f'<line x1="{px(50):.1f}" y1="{top}" x2="{px(50):.1f}" y2="{bot}" stroke="{p["grid"]}" stroke-dasharray="4 4"/>')
    s.append(f'<line x1="{left}" y1="{py(50):.1f}" x2="{right}" y2="{py(50):.1f}" stroke="{p["grid"]}" stroke-dasharray="4 4"/>')
    s.append(f'<rect x="{left}" y="{top}" width="{pw:.1f}" height="{ph:.1f}" fill="none" stroke="{p["grid"]}"/>')
    # axis labels + quadrant captions
    s.append(_txt((left + right) / 2, bot + 30, x_label + "  →", size=10, fill=p["muted"], anchor="middle", weight="600"))
    s.append(f'<text x="18" y="{(top+bot)/2:.1f}" font-size="10" fill="{p["muted"]}" font-weight="600" '
             f'text-anchor="middle" transform="rotate(-90 18 {(top+bot)/2:.1f})" '
             f'font-family="Inter, sans-serif">{escape(y_label)}  →</text>')
    s.append(_txt(px(75), top + 16, "GREENFIELD", size=10, fill="#2BBF77", anchor="middle", weight="700"))
    s.append(_txt(px(25), top + 16, "LOW-DEMAND", size=9, fill=p["muted"], anchor="middle", weight="600"))
    s.append(_txt(px(25), bot - 8, "FORTRESS", size=9, fill=p["muted"], anchor="middle", weight="600"))
    s.append(_txt(px(75), bot - 8, "CONTESTED", size=9, fill=p["muted"], anchor="middle", weight="600"))
    smax = max((pt.get("size") or 1 for pt in points), default=1) or 1
    for pt in points:
        cx, cy = px(pt["x"]), py(pt["y"])
        r = 8 + 26 * ((pt.get("size") or 1) / smax) ** 0.5
        col = TIER_COLOR.get((pt.get("tier") or "").lower(), p["primary"])
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}" opacity="0.78"/>')
        s.append(_txt(cx, cy - r - 4, pt["label"], size=10.5, fill=p["ink"], anchor="middle", weight="600"))
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------------------- status heatmap (AI visibility matrix)
STATUS = {"cited": ("#1B8A5A", "C"), "named": ("#2BBF77", "N"), "mentioned": ("#2BBF77", "N"),
          "weak": ("#F0B429", "~"), "absent": ("#E6EBF0", ""), "competitor": ("#0E2A47", "X")}


def heatmap(row_labels, col_labels, cells, title=None, subtitle=None, brand=None,
            w=720, row_label_w=250, cell_h=30, legend=True):
    """AI-visibility matrix. cells: 2D list [row][col] of status strings
    (cited / named / weak / absent / competitor). Colored grid + legend."""
    n_rows, n_cols = len(row_labels), len(col_labels)
    head_h = 58
    leg_h = 26 if legend else 0
    h = head_h + n_rows * cell_h + leg_h + 10
    s, p = _open(w, h, title, subtitle, brand)
    grid_left = row_label_w
    cw = (w - grid_left - 8) / max(1, n_cols)
    # column headers
    for j, c in enumerate(col_labels):
        s.append(_txt(grid_left + cw * (j + 0.5), head_h - 8, c, size=10, fill=p["muted"], anchor="middle", weight="600"))
    # rows
    for i, rlab in enumerate(row_labels):
        y = head_h + i * cell_h
        s.append(_txt(grid_left - 10, y + cell_h * 0.66, (rlab[:46] + "…") if len(rlab) > 47 else rlab,
                      size=11, fill=p["ink"], anchor="end"))
        for j in range(n_cols):
            st = (cells[i][j] if i < len(cells) and j < len(cells[i]) else "absent") or "absent"
            color, glyph = STATUS.get(st.lower(), ("#E6EBF0", ""))
            x = grid_left + cw * j
            s.append(f'<rect x="{x+2:.1f}" y="{y+2:.1f}" width="{cw-4:.1f}" height="{cell_h-4:.1f}" rx="4" fill="{color}"/>')
            if glyph:
                tc = "#FFFFFF" if st.lower() in ("cited", "competitor") else p["ink"]
                s.append(_txt(x + cw / 2, y + cell_h * 0.66, glyph, size=11, fill=tc, anchor="middle", weight="700"))
    if legend:
        ly = head_h + n_rows * cell_h + 18
        items = [("Cited", "#1B8A5A"), ("Named", "#2BBF77"), ("Weak", "#F0B429"),
                 ("Absent", "#E6EBF0"), ("Competitor owns", "#0E2A47")]
        lx = grid_left
        for label, col in items:
            s.append(f'<rect x="{lx:.1f}" y="{ly-10}" width="12" height="12" rx="3" fill="{col}"/>')
            s.append(_txt(lx + 17, ly, label, size=10, fill=p["muted"]))
            lx += 30 + len(label) * 6.4
    s.append("</svg>")
    return "\n".join(s)

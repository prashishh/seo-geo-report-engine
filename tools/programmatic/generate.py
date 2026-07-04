"""Bulk-generate one page per data row from a single template (stdlib only).

Feeds a rows file (.csv or .json list-of-dicts) through a template file (HTML or
Markdown with {placeholder} fields matching row keys) and writes one output file
per row into an output dir, named by a slugified key. Powers the programmatic-seo
and comparison-pages skills (see playbooks/programmatic-seo.md).

    python tools/programmatic/generate.py \
        --rows rows.csv --template tpl.html \
        --out deliverables/programmatic --slug-field keyword

A row whose template references a key the row lacks does NOT crash: the missing
field is rendered as a visible "{{TODO:field}}" marker so QA can catch the gap.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

PLACEHOLDER = re.compile(r"\{([a-zA-Z0-9_]+)\}")


def slugify(value) -> str:
    """Lowercase, ASCII-ish, hyphen-separated slug safe for a filename."""
    s = re.sub(r"[^a-z0-9]+", "-", str(value).strip().lower())
    return s.strip("-") or "page"


def load_rows(rows_path) -> list:
    """Read rows from .csv (header row -> dict) or .json (list of dicts)."""
    p = Path(rows_path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("rows", [data])
        if not isinstance(data, list):
            raise ValueError("JSON rows file must be a list of objects (or {'rows': [...]})")
        return [dict(r) for r in data]
    rows = list(csv.DictReader(text.splitlines()))
    if not rows:
        raise ValueError(f"No data rows found in {p}")
    return rows


class _TodoMap(dict):
    """Mapping that turns any missing placeholder into a visible TODO marker."""

    def __missing__(self, key):
        return "{{TODO:" + key + "}}"


def render(template: str, row: dict) -> str:
    """Substitute {placeholders}; unknown keys become {{TODO:key}}, no crash."""
    # str.format would choke on stray braces in HTML/CSS; substitute only the
    # placeholders we actually recognize, leaving everything else untouched.
    mapping = _TodoMap({k: ("" if v is None else str(v)) for k, v in row.items()})
    return PLACEHOLDER.sub(lambda m: mapping[m.group(1)], template)


def generate(rows_path, template_path, out_dir, slug_field, ext=None) -> list:
    """Write one file per row. Returns the list of written paths.

    ext: output extension (e.g. "html", "md"); defaults to the template's.
    """
    rows = load_rows(rows_path)
    template = Path(template_path).read_text(encoding="utf-8")
    ext = (ext or Path(template_path).suffix.lstrip(".") or "html").lstrip(".")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    written, seen = [], {}
    for i, row in enumerate(rows):
        raw = row.get(slug_field) or f"page-{i + 1}"
        slug = slugify(raw)
        # de-dupe collisions deterministically (slug, slug-2, slug-3, ...)
        seen[slug] = seen.get(slug, 0) + 1
        if seen[slug] > 1:
            slug = f"{slug}-{seen[slug]}"
        dest = out / f"{slug}.{ext}"
        dest.write_text(render(template, row), encoding="utf-8")
        written.append(str(dest))
    return written


def main():
    ap = argparse.ArgumentParser(
        prog="programmatic.generate",
        description="Generate one page per data row from a {placeholder} template.",
    )
    ap.add_argument("--rows", required=True, help="rows file (.csv or .json list of dicts)")
    ap.add_argument("--template", required=True, help="template file (.html or .md)")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--slug-field", required=True, help="row key used to name each file")
    ap.add_argument("--ext", help="output extension (default: template's)")
    args = ap.parse_args()

    written = generate(args.rows, args.template, args.out, args.slug_field, ext=args.ext)
    print(f"wrote {len(written)} page(s) to {args.out}")
    for path in written:
        print(path)


if __name__ == "__main__":
    main()

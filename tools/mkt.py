#!/usr/bin/env python3
"""seo-geo-report-engine CLI. Run via ./bin/mkt (it finds a Python >= 3.8).

Subcommands:
    config show [--project X]      Resolve + print the active project's merged config.
    selftest                       Verify the YAML reader, chart kit, and PDF engine.
    chart <type> --in spec.json --out f.svg   Render one chart from a JSON spec.
    pdf --in page.html --out f.pdf            Render HTML to PDF (headless Chrome).
    proposal build [--project X]   Build the growth-proposal PDF (see tools/proposal).
    dashboard build [--out f.html] Build the agency project dashboard.
    dashboard serve [--port 8787]  Build and serve the dashboard locally.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # make lib/ charts/ ... importable


def cmd_config(args):
    from lib.config import load
    cfg = load(project=args.project)
    print(json.dumps(cfg.as_dict(), indent=2, ensure_ascii=False))


def cmd_profile(args):
    from lib.config import root, active_profile
    f = root() / "config" / "active-profile"
    if args.action == "use":
        f.write_text(args.name.strip() + "\n")
        print(f"active profile -> {args.name.strip()}")
    else:
        print(active_profile())


def cmd_chart(args):
    from charts import svg
    spec = json.loads(Path(args.infile).read_text(encoding="utf-8"))
    ctype = spec.pop("type", args.type)
    fn = getattr(svg, ctype, None)
    if not fn:
        sys.exit(f"unknown chart type: {ctype}")
    out = fn(**spec)
    Path(args.out).write_text(out, encoding="utf-8")
    print(args.out)


def cmd_pdf(args):
    from pdf.render import html_to_pdf
    print(html_to_pdf(args.infile, args.out))


def cmd_proposal(args):
    from proposal.build import build
    print(build(project=args.project, out=args.out, src=args.infile))


def cmd_doc(args):
    from proposal.build import render_file
    print(render_file(args.infile, out=args.out, project=args.project))


def cmd_dashboard(args):
    from dashboard.build import build, serve
    if args.action == "build":
        print(build(out=args.out))
    else:
        serve(host=args.host, port=args.port, out=args.out)


def cmd_selftest(args):
    ok = True
    # 1. yaml
    from lib import yaml_min
    data = yaml_min.safe_load(
        "a: 1\nb:\n  - x\n  - y\nc: [p, q, r]\nd:\n  k: 'hi'\n  n: 2.5\nlist:\n  - name: A\n    v: 1\n  - name: B\n    v: 2\n"
    )
    exp = {"a": 1, "b": ["x", "y"], "c": ["p", "q", "r"], "d": {"k": "hi", "n": 2.5},
           "list": [{"name": "A", "v": 1}, {"name": "B", "v": 2}]}
    print("yaml reader:", "OK" if data == exp else f"FAIL -> {data}")
    ok &= data == exp
    # 2. charts
    from charts import svg
    s = svg.lines({"Probable": [100, 185, 385]}, ["TODAY", "M3", "M6"], title="t")
    print("chart kit: ", "OK" if s.startswith("<svg") and "polyline" in s else "FAIL")
    ok &= s.startswith("<svg")
    # 3. pdf engine
    from pdf.render import find_browser
    b = find_browser()
    print("pdf engine:", f"OK ({b})" if b else "no Chromium browser found (WeasyPrint fallback)")
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(prog="mkt")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("config")
    p.add_argument("action", choices=["show"])
    p.add_argument("--project")
    p.set_defaults(func=cmd_config)

    p = sub.add_parser("profile")
    p.add_argument("action", choices=["show", "use"])
    p.add_argument("name", nargs="?", help="profile to switch to (for 'use'): personal | business")
    p.set_defaults(func=cmd_profile)

    p = sub.add_parser("selftest")
    p.set_defaults(func=cmd_selftest)

    p = sub.add_parser("chart")
    p.add_argument("type")
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_chart)

    p = sub.add_parser("pdf")
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_pdf)

    p = sub.add_parser("proposal")
    p.add_argument("action", choices=["build"])
    p.add_argument("--project")
    p.add_argument("--in", dest="infile")
    p.add_argument("--out")
    p.set_defaults(func=cmd_proposal)

    p = sub.add_parser("doc")  # render any sections spec (report / comparison / proposal)
    p.add_argument("action", choices=["build"])
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--out")
    p.add_argument("--project")
    p.set_defaults(func=cmd_doc)

    p = sub.add_parser("dashboard")
    p.add_argument("action", choices=["build", "serve"])
    p.add_argument("--out")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8787)
    p.set_defaults(func=cmd_dashboard)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

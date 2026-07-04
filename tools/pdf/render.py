"""HTML -> PDF via headless Chrome/Brave/Chromium (stdlib only).

Chrome renders our SVG charts + CSS exactly as a browser would, so the PDF looks
like the reference decks. Page size / margins are controlled by CSS `@page` in the
HTML. Falls back to WeasyPrint if no Chromium-family browser is found.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
PATH_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "brave-browser", "microsoft-edge"]


def find_browser():
    if os.environ.get("MKT_BROWSER") and Path(os.environ["MKT_BROWSER"]).exists():
        return os.environ["MKT_BROWSER"]
    for c in CANDIDATES:
        if Path(c).exists():
            return c
    for n in PATH_NAMES:
        p = shutil.which(n)
        if p:
            return p
    # Windows common paths
    for c in [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]:
        if Path(c).exists():
            return c
    return None


def html_to_pdf(html_path, pdf_path, timeout=60):
    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path).resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    browser = find_browser()
    if browser:
        if pdf_path.exists():
            pdf_path.unlink()
        with tempfile.TemporaryDirectory() as profile:
            cmd = [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-first-run",
                "--disable-extensions",
                f"--user-data-dir={profile}",
                "--no-pdf-header-footer",
                "--virtual-time-budget=2000",
                f"--print-to-pdf={pdf_path}",
                html_path.as_uri(),
            ]
            # headless=new often renders the PDF quickly but is slow to exit. Poll for the
            # output file and terminate Chrome as soon as it's written and size-stable.
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            deadline = time.time() + timeout
            last = -1
            while time.time() < deadline:
                if proc.poll() is not None:
                    break
                if pdf_path.exists():
                    sz = pdf_path.stat().st_size
                    if sz > 0 and sz == last:
                        break  # stable -> render finished
                    last = sz
                time.sleep(0.4)
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                return str(pdf_path)
            sys.stderr.write("chrome produced no pdf\n")
    # fallback
    try:
        from weasyprint import HTML  # type: ignore
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return str(pdf_path)
    except Exception as e:
        raise RuntimeError(
            f"No Chromium-family browser found and WeasyPrint unavailable ({e}). "
            "Install Chrome or set MKT_BROWSER to a Chromium binary."
        )


def string_to_pdf(html, pdf_path, timeout=60):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp = f.name
    try:
        return html_to_pdf(tmp, pdf_path, timeout=timeout)
    finally:
        os.unlink(tmp)

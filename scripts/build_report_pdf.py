"""Render report/report.md to a PDF in the required format and check the page limit.

The rubric asks for at most five A4 pages, excluding figures, references and appendices, in an 11pt font with
1-inch margins. This script writes two PDFs with Chrome (headless):

    report/report.pdf          the submission: full report with figures, references and appendices
    results/tmp/report-count.pdf   the same text without figures, references and appendices, for counting

and exits with status 1 if the counted version is longer than five pages.

Usage:
    python scripts/build_report.py && python scripts/build_report_pdf.py
Requires the `markdown` package and Google Chrome (or set CHROME=/path/to/chrome).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = ROOT / "report" / "report.md"
PDF = ROOT / "report" / "report.pdf"
COUNT_PDF = ROOT / "results" / "tmp" / "report-count.pdf"
PAGE_LIMIT = 5

CSS = """
@page { size: A4; margin: 1in; }
body { font-family: "Times New Roman", Times, serif; font-size: 11pt; line-height: 1.25; color: #000; }
h1 { font-size: 16pt; margin: 0 0 4pt; }
h2 { font-size: 13pt; margin: 12pt 0 4pt; }
h3 { font-size: 11.5pt; margin: 9pt 0 3pt; }
p { margin: 0 0 6pt; text-align: justify; }
img { display: block; max-width: 100%; max-height: 8.5cm; margin: 6pt auto 2pt; }
table { border-collapse: collapse; margin: 4pt auto 8pt; font-size: 9pt; page-break-inside: avoid; }
th, td { border-top: 0.5pt solid #000; border-bottom: 0.5pt solid #000; padding: 2pt 5pt; text-align: center; }
th { font-weight: bold; }
code { font-family: "Courier New", monospace; font-size: 10pt; }
pre { font-size: 9pt; background: none; }
a { color: #000; }
p > em:only-child { font-size: 10pt; }
p:has(+ table) { break-after: avoid; }
"""

FIGURE = re.compile(r"^!\[[^\]]*\]\([^)]*\)\s*\n+\*Figure [^\n]*\*\s*$", re.MULTILINE)


def chrome() -> str:
    candidates = [os.environ.get("CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chrome")]
    for path in candidates:
        if path and Path(path).exists():
            return path
    raise SystemExit("Chrome not found; set CHROME=/path/to/chrome")


def to_pdf(md_text: str, out: Path) -> int:
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
    page = REPORT_MD.with_name(f".{out.stem}.html")  # beside report.md so relative image paths resolve
    page.write_text(html, encoding="utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([chrome(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        "--allow-file-access-from-files", f"--print-to-pdf={out}", page.as_uri()],
                       check=True, capture_output=True)
    finally:
        page.unlink(missing_ok=True)
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True, check=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", info).group(1))


def counted_text(md_text: str) -> str:
    """Report text without figures (and their captions), references and appendices."""
    text = md_text.split("\n## References", 1)[0]
    return FIGURE.sub("", text)


def main() -> int:
    md_text = REPORT_MD.read_text(encoding="utf-8")
    pages = to_pdf(md_text, PDF)
    counted = to_pdf(counted_text(md_text), COUNT_PDF)
    print(f"{PDF.relative_to(ROOT)}: {pages} pages in total")
    print(f"counted pages (no figures, references or appendices): {counted} (limit {PAGE_LIMIT})")
    return 0 if counted <= PAGE_LIMIT else 1


if __name__ == "__main__":
    raise SystemExit(main())

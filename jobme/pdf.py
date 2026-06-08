"""Modular HTML -> PDF rendering.

Two interchangeable backends are registered. Each is imported lazily so a missing
optional dependency only errors when that backend is actually selected.

- ``playwright`` (default): headless Chromium -- best CSS/print fidelity. Requires a
  one-time ``playwright install chromium``.
- ``weasyprint``: pure-Python HTML/CSS engine. On Windows it needs GTK native libs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from pypdf import PdfReader


def _render_playwright(html_path: Path, out_path: Path) -> None:
    from playwright.sync_api import sync_playwright

    file_url = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(file_url, wait_until="networkidle")
            page.pdf(
                path=str(out_path),
                format="Letter",
                print_background=True,
                prefer_css_page_size=True,
            )
        finally:
            browser.close()


def _render_weasyprint(html_path: Path, out_path: Path) -> None:
    from weasyprint import HTML

    HTML(filename=str(html_path)).write_pdf(str(out_path))


BACKENDS: dict[str, Callable[[Path, Path], None]] = {
    "playwright": _render_playwright,
    "weasyprint": _render_weasyprint,
}


def html_to_pdf(html_path: Path, out_path: Path, backend: str = "playwright") -> Path:
    """Render ``html_path`` to ``out_path`` using the named backend."""
    try:
        render = BACKENDS[backend]
    except KeyError:
        raise ValueError(
            f"Unknown PDF backend {backend!r}. Available: {', '.join(BACKENDS)}"
        ) from None
    render(html_path, out_path)
    return out_path


def page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF."""
    return len(PdfReader(str(pdf_path)).pages)

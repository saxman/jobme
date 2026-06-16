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


def _check_playwright() -> None:
    # Importing succeeds even when the browser isn't downloaded, so verify the
    # converter end to end by launching and closing headless Chromium.
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        p.chromium.launch().close()


def _check_weasyprint() -> None:
    # On Windows the GTK native libs load at import time, so importing is the test.
    import weasyprint  # noqa: F401


BACKENDS: dict[str, Callable[[Path, Path], None]] = {
    "playwright": _render_playwright,
    "weasyprint": _render_weasyprint,
}

BACKEND_CHECKS: dict[str, Callable[[], None]] = {
    "playwright": _check_playwright,
    "weasyprint": _check_weasyprint,
}


def _resolve_backend(backend: str) -> Callable[[Path, Path], None]:
    try:
        return BACKENDS[backend]
    except KeyError:
        raise ValueError(
            f"Unknown PDF backend {backend!r}. Available: {', '.join(BACKENDS)}"
        ) from None


def check_backend(backend: str) -> None:
    """Verify the backend's dependencies are installed, raising if not.

    Call before expensive work (LLM calls) so a missing converter fails fast.
    """
    _resolve_backend(backend)
    try:
        BACKEND_CHECKS[backend]()
    except Exception as error:
        raise RuntimeError(
            f"PDF backend {backend!r} is not ready: {error}"
        ) from error


def html_to_pdf(html_path: Path, out_path: Path, backend: str = "playwright") -> Path:
    """Render ``html_path`` to ``out_path`` using the named backend."""
    render = _resolve_backend(backend)
    render(html_path, out_path)
    return out_path


def page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF."""
    return len(PdfReader(str(pdf_path)).pages)

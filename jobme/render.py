"""Turn approved content into self-contained, print-ready HTML via an LLM.

These functions operate on an AIMU ``ModelClient`` so the caller can keep a single
conversation across follow-up turns (e.g. the resume page-fit/condense loop).
"""

from __future__ import annotations

import re

from . import prompts


def strip_code_fences(text: str) -> str:
    """Remove a surrounding ```html ... ``` (or bare ```) fence if the model added one."""
    text = text.strip()
    fence = re.match(r"^```[a-zA-Z]*\n(.*)\n```$", text, flags=re.DOTALL)
    if fence:
        return fence.group(1).strip()
    return text


def render_resume_html(client, exemplar_html: str, content: str) -> str:
    """First turn: produce the tailored resume HTML in the exemplar's style."""
    task = prompts.RESUME_HTML_TASK.format(exemplar_html=exemplar_html, content=content)
    return strip_code_fences(client.chat(task))


def condense_resume_html(client, pages: int, target: int) -> str:
    """Follow-up turn on the same client: shrink the resume to fit ``target`` pages."""
    task = prompts.RESUME_CONDENSE_TASK.format(pages=pages, target=target)
    return strip_code_fences(client.chat(task))


def expand_resume_typography(client, fill: float, target: int) -> str:
    """Follow-up turn: stretch layout/typography to fill closer to ``target`` pages.

    Adjusts spacing and sizing only -- content is unchanged -- so this never touches the
    accuracy-reviewed text. Used for small shortfalls the typography can tastefully close.
    """
    task = prompts.RESUME_EXPAND_TYPOGRAPHY_TASK.format(fill=fill, target=target)
    return strip_code_fences(client.chat(task))


def render_cover_html(client, exemplar_html: str, content: str) -> str:
    """Render the approved cover letter text as a styled HTML letter."""
    task = prompts.COVER_HTML_TASK.format(exemplar_html=exemplar_html, content=content)
    return strip_code_fences(client.chat(task))

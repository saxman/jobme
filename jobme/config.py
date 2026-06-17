"""Run configuration: model and PDF backend resolution.

Resolution order for the model: explicit CLI flag -> ``JOBME_MODEL`` env var ->
the built-in default. The model string is an AIMU ``"provider:model_id"`` value
(e.g. ``"anthropic:claude-sonnet-4-6"`` or ``"ollama:qwen3:8b"``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "anthropic:claude-opus-4-8"
DEFAULT_PDF_BACKEND = "playwright"
MAX_REVIEW_ROUNDS = 3
MAX_PAGE_FIT_RETRIES = 4
TARGET_RESUME_PAGES = 2

# The fit loop aims for the resume's continuous fill (content height in pages, via
# page_fill) to reach RESUME_FILL_TARGET. Each round picks one LLM action by priority:
# condense if over TARGET_RESUME_PAGES, add genuine CV content for a shortfall larger than
# TYPOGRAPHY_MAX_STRETCH, else nudge typography. The emitted resume is the fullest render
# that still fits the page limit (best-fill-so-far), so it never ships an overshoot.
#
# NOTE on the numbers: continuous fill runs *well short* of 2.0 for a physically full two
# pages, because page breaks can't split a line/bullet so the layout leaves some slack. With
# the example template a full two pages is ~1.3-1.4 fill; past ~1.4 it spills to a third
# page. So RESUME_FILL_TARGET is ~1.3, not ~2.0. Tighter-margin templates fill higher.
RESUME_FILL_TARGET = 1.3
TYPOGRAPHY_MAX_STRETCH = 0.25

# If the best achievable fill stays below this even after a content expansion, warn that the
# CV likely lacks enough relevant content to fill two pages.
LOW_FILL_WARNING = 1.1

# Transient API failures (network blips, rate limits, 5xx) retry with exponential backoff:
# delays of API_RETRY_BASE_DELAY * 2**attempt seconds, up to MAX_API_RETRIES times.
MAX_API_RETRIES = 3
API_RETRY_BASE_DELAY = 2.0


@dataclass
class Config:
    """Resolved settings for a single tailoring run."""

    jd_path: Path
    input_dir: Path
    output_dir: Path
    model: str
    pdf_backend: str
    name: str | None = None  # optional explicit job slug/title


def resolve_model(flag: str | None) -> str:
    """Resolve the model string from flag -> JOBME_MODEL env -> default."""
    return flag or os.environ.get("JOBME_MODEL") or DEFAULT_MODEL

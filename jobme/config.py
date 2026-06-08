"""Run configuration: model and PDF backend resolution.

Resolution order for the model: explicit CLI flag -> ``JOBME_MODEL`` env var ->
the built-in default. The model string is an AIMU ``"provider:model_id"`` value
(e.g. ``"anthropic:claude-sonnet-4-6"`` or ``"ollama:qwen3:8b"``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "anthropic:claude-sonnet-4-6"
DEFAULT_PDF_BACKEND = "playwright"
MAX_REVIEW_ROUNDS = 3
MAX_PAGE_FIT_RETRIES = 2
TARGET_RESUME_PAGES = 2


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

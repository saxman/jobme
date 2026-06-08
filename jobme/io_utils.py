"""Input loading and output-directory helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Inputs:
    """The static assets plus the per-run job description."""

    cv_markdown: str
    resume_html: str
    job_description: str
    cover_letter_samples: list[str] = field(default_factory=list)


def _read(path: Path, label: str) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required {label} not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"{label} is empty: {path}")
    return text


def load_inputs(input_dir: Path, jd_path: Path) -> Inputs:
    """Load the CV, resume, optional cover-letter samples, and the job description."""
    cv = _read(input_dir / "cv.md", "CV markdown (input/cv.md)")
    resume = _read(input_dir / "resume.html", "HTML resume (input/resume.html)")
    jd = _read(jd_path, "job description")

    # Cover letters are optional: cover_letter1.txt, cover_letter2.txt, ... (flat, .txt).
    samples: list[str] = []
    for path in sorted(input_dir.glob("cover_letter*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            samples.append(text)

    return Inputs(
        cv_markdown=cv,
        resume_html=resume,
        job_description=jd,
        cover_letter_samples=samples,
    )


def slugify(value: str) -> str:
    """Turn an arbitrary label into a filesystem-safe slug."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value[:80] or "job"


def make_output_dir(output_dir: Path, slug: str) -> Path:
    """Create and return ``output_dir/slug`` (parents included)."""
    target = output_dir / slug
    target.mkdir(parents=True, exist_ok=True)
    return target

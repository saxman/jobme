"""Command-line interface for jobme.

    uv run scripts/jobme.py --jd path/to/jd.txt \
        [--model anthropic:claude-sonnet-4-6] [--pdf-backend playwright|weasyprint] \
        [--name "Company - Title"] [--input-dir input] [--output-dir output]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from . import pipeline
from .config import DEFAULT_PDF_BACKEND, Config, resolve_model
from .pdf import BACKENDS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jobme",
        description="Tailor a resume and cover letter to a job posting and produce PDFs.",
    )
    parser.add_argument("--jd", required=True, type=Path, help="Path to the job description file.")
    parser.add_argument(
        "--model",
        default=None,
        help="AIMU model string (provider:model_id). Overrides JOBME_MODEL env; "
        "defaults to anthropic:claude-sonnet-4-6.",
    )
    parser.add_argument(
        "--pdf-backend",
        default=DEFAULT_PDF_BACKEND,
        choices=sorted(BACKENDS),
        help="HTML->PDF backend (default: playwright).",
    )
    parser.add_argument("--name", default=None, help="Explicit 'Company - Title' label for the output folder.")
    parser.add_argument("--input-dir", default=Path("input"), type=Path, help="Directory with cv.md, resume.html, cover_letter*.txt.")
    parser.add_argument("--output-dir", default=Path("output"), type=Path, help="Where per-job results are written.")
    return parser


def _load_env() -> None:
    """Load .env files from the working directory up to the filesystem root.

    load_dotenv() stops at the first .env found, so a project-local .env (e.g. one
    holding only JOBME_MODEL) would shadow a parent .env holding ANTHROPIC_API_KEY.
    Walk every ancestor and load each, nearest first; override=False keeps the
    nearer file's values winning over the farther one's.
    """
    for directory in (Path.cwd(), *Path.cwd().parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)


def main(argv: list[str] | None = None) -> int:
    _load_env()  # pick up ANTHROPIC_API_KEY / JOBME_MODEL from .env files, parents included
    args = _build_parser().parse_args(argv)

    config = Config(
        jd_path=args.jd,
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        model=resolve_model(args.model),
        pdf_backend=args.pdf_backend,
        name=args.name,
    )

    try:
        pipeline.run(config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[jobme] error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

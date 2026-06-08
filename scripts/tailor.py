#!/usr/bin/env python
"""Thin entrypoint: `uv run scripts/tailor.py --jd <path> [...]`.

Delegates to jobme.cli.main so the same logic backs the `jobme` console script.
"""

import sys
from pathlib import Path

# Allow running directly from a checkout without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jobme.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())

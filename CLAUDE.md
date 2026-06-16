# CLAUDE.md

Guidance for working in this repo. See [README.md](README.md) for end-user docs.

## What this is

`jobme` tailors a resume and cover letter to a job posting and produces send-ready PDFs.
It's a multi-step agentic pipeline built on **AIMU** (`aimu` on PyPI, >=0.7.0), which wraps
the LLM providers. Python >=3.11, managed with **uv**.

## Commands

```bash
uv sync                              # install deps (incl. aimu from PyPI)
uv run playwright install chromium   # one-time, for the default PDF backend

# Run the pipeline (the package's only real entry point; defaults to input/ and output/):
uv run scripts/jobme.py --jd path/to/posting.txt [--input-dir DIR --output-dir DIR]
```

There is **no automated test suite**. Verify changes by running the pipeline end-to-end.
To avoid API cost/keys during development, run against a local model:
`--model ollama:qwen3:8b` (any installed Ollama model). The default model is
`anthropic:claude-sonnet-4-6`, which needs `ANTHROPIC_API_KEY` (env or `.env`).

## Architecture

CLI ([scripts/jobme.py](scripts/jobme.py) → [jobme/cli.py](jobme/cli.py)) builds a
`Config` and calls [`jobme.pipeline.run`](jobme/pipeline.py). The package:

- [jobme/pipeline.py](jobme/pipeline.py) — orchestration. Steps: derive job slug → tailor
  resume → render resume HTML + **2-page fit loop** → tailor cover letter → render cover
  HTML → PDFs → write `summary.md` + `trace.json`.
- [jobme/prompts.py](jobme/prompts.py) — all prompt templates (system + task strings).
- [jobme/render.py](jobme/render.py) — LLM content → self-contained HTML (strips code fences).
- [jobme/pdf.py](jobme/pdf.py) — modular HTML→PDF (`BACKENDS` registry) + `page_count` (pypdf).
- [jobme/config.py](jobme/config.py) — `Config`, model resolution, and the tunable constants.
- [jobme/io_utils.py](jobme/io_utils.py) — input loading, slugify, output-dir creation.

### Key AIMU APIs used

- `aimu.chat(msg, model=, system=)`, `aimu.client(model, system=)`, `aimu.agent(model, system=, name=)`.
- **`aimu.agents.EvaluatorOptimizer(generator=, evaluator=, max_rounds=, pass_keyword="PASS")`**
  drives both the resume and cover-letter "generate → review → revise until PASS" loops.
  Both review steps enforce the same bar: **accuracy** (no claim unsupported by the CV) and
  **intrigue**. Give generator/evaluator distinct `name=` so `loop.messages` (used for the
  trace) keeps them separate.
- Models are `"provider:model_id"` strings. When changing model/agent code, check the
  installed AIMU API rather than assuming.

## Conventions & gotchas

- **Two-page resume is enforced by real page count**, not the LLM: render → `page_count` →
  if over `TARGET_RESUME_PAGES`, re-prompt to condense (up to `MAX_PAGE_FIT_RETRIES`).
- **Inputs:** `cv.md` = content source of truth, `resume.html` = style/format template,
  `cover_letter*.txt` = optional voice samples. The pipeline must never invent facts absent
  from `cv.md` — keep that constraint in the prompts if you edit them.
- **Config knobs** live in [jobme/config.py](jobme/config.py): `DEFAULT_MODEL`,
  `DEFAULT_PDF_BACKEND`, `MAX_REVIEW_ROUNDS`, `MAX_PAGE_FIT_RETRIES`, `TARGET_RESUME_PAGES`.
- **PDF backends** are lazily imported so a missing one only errors when selected.
  `weasyprint` needs GTK native libs on Windows; `playwright` is the default.
- **`example/` is the committed demo** (synthetic inputs + a sample run in `example/output/`).
  Nothing else is git-ignored: `input/` and `output/` are tracked, but this public repo
  commits nothing to them. Real use happens in a **private mirror**, where the user's real CV
  and runs live in `input/`/`output/` (committed there only). Never commit real personal data
  to this public project; do real runs in the mirror.
- This public repo is meant to be mirrored into private copies that `git fetch upstream`;
  keep changes mergeable and don't commit personal data here.

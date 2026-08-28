# CLAUDE.md

Guidance for working in this repo. See [README.md](README.md) for end-user docs.

## What this is

`jobme` tailors a resume and cover letter to a job posting and produces send-ready PDFs.
It's a multi-step agentic pipeline built on **AIMU** (`aimu` on PyPI, >=0.25.0), which wraps
the LLM providers. Python >=3.11, managed with **uv**.

## Commands

```bash
uv sync                              # install deps (incl. aimu from PyPI)
uv run playwright install chromium   # one-time, for the default PDF backend

# Run the pipeline (the package's only real entry point; defaults to input/ and output/):
uv run scripts/jobme.py --jd path/to/posting.txt [--input-dir DIR --output-dir DIR]
```

The test suite is mock-only (`uv run pytest`): no model, no network, no keys. It covers the
callback, warning, and cancellation plumbing and the Kokua adapter, not the pipeline's output.
Verify a pipeline change by running it end-to-end.
To avoid API cost/keys during development, run against a local model:
`--model ollama:qwen3:8b` (any installed Ollama model). The default model is
`anthropic:claude-opus-4-8`, which needs `ANTHROPIC_API_KEY` (env or `.env`).

## Architecture

CLI ([scripts/jobme.py](scripts/jobme.py) → [jobme/cli.py](jobme/cli.py)) builds a
`Config` and calls [`jobme.pipeline.run`](jobme/pipeline.py). The package:

- [jobme/pipeline.py](jobme/pipeline.py) — orchestration. Steps: derive job slug → tailor
  resume → render resume HTML + **2-page fit loop** → tailor cover letter → render cover
  HTML → PDFs → write `summary.md` + `trace.json`.
- [jobme/prompts.py](jobme/prompts.py) — all prompt templates (system + task strings).
- [jobme/render.py](jobme/render.py) — LLM content → self-contained HTML (strips code fences).
- [jobme/pdf.py](jobme/pdf.py) — modular HTML→PDF (`BACKENDS` registry), `check_backend`
  (preflight the converter before LLM calls), `page_count` (pypdf), and `page_fill`
  (fractional page fill measured in headless Chromium; `None` if unavailable).
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

- **Two-page resume is enforced by real measurement**, not the LLM. The fit loop renders →
  `page_count` + `page_fill`, then each round picks one LLM action by priority: (1) over
  `TARGET_RESUME_PAGES` → condense; (2) underfilled below `RESUME_FILL_TARGET` by more than
  `TYPOGRAPHY_MAX_STRETCH` → add genuine CV content via a **stateless `aimu.chat` that
  re-supplies the CV/JD/draft** under the accuracy system prompt (the renderer has no CV; and
  an `aimu.agent` with a system prompt resets its history every run, so re-feed context
  rather than rely on conversational memory); (3) a smaller shortfall → nudge typography
  (`fit_resume_html`, content-preserving). The pipeline emits the **best fitting render across
  all rounds** (the fullest one with `page_count <= TARGET_RESUME_PAGES`), so it never ships
  an overshoot. Caveat: `page_fill` is continuous content height, which runs *short* of
  physical pages (page-break gaps), so a full two physical pages is well below fill 2.0 —
  don't read `RESUME_FILL_TARGET` as "2.0 minus epsilon". If even after expansion the best
  fill stays below `LOW_FILL_WARNING`, jobme prints a warning that the CV is likely too thin.
  Bounded by `MAX_PAGE_FIT_RETRIES`.
- **Transient API errors** (network/rate-limit/5xx) are retried with backoff: each pipeline
  step in `run()` is wrapped in `_with_retry` (steps are self-contained and re-runnable).
- **Inputs:** `cv.md` = content source of truth, `resume.html` = style/format template,
  `cover_letter*.txt` = optional voice samples, `guidance.md` = optional free-form generation
  guidance. The pipeline must never invent facts absent from `cv.md` — keep that constraint in
  the prompts if you edit them.
- **Optional `guidance.md`** (loaded into `Inputs.guidance`) is appended via `_with_guidance`
  to the system prompt of every text-producing step (resume/cover generators, content
  expansion, both HTML renderers) using `prompts.GUIDANCE_BLOCK`, which subordinates it to the
  accuracy rule. Not applied to evaluators or the slug step.
- **The exemplar `resume.html` drives fill**, not just style. The renderer mimics its layout,
  so keep it a *complete, densely-filled two-page* resume (a sparse stub anchors the renderer
  toward sparse output). Its print CSS must let sections **flow across the page break** — use
  `break-after: avoid` on headings/roles and `break-inside: avoid` on bullets, NOT
  `break-inside: avoid` on whole `section`s (that strands big gaps and caps fill at ~1.05).
- **Config knobs** live in [jobme/config.py](jobme/config.py): `DEFAULT_MODEL`,
  `DEFAULT_PDF_BACKEND`, `MAX_REVIEW_ROUNDS`, `MAX_PAGE_FIT_RETRIES`, `TARGET_RESUME_PAGES`,
  `RESUME_FILL_TARGET`, `TYPOGRAPHY_MAX_STRETCH` (shortfall above which the loop adds content
  instead of nudging type), `LOW_FILL_WARNING`, and `MAX_API_RETRIES`/`API_RETRY_BASE_DELAY`.
- **PDF backends** are lazily imported so a missing one only errors when selected.
  `weasyprint` needs GTK native libs on Windows; `playwright` is the default.
- **`example/` is the committed demo** (synthetic inputs + a sample run in `example/output/`).
  Nothing else is git-ignored: `input/` and `output/` are tracked, but this public repo
  commits nothing to them. Real use happens in a **private mirror**, where the user's real CV
  and runs live in `input/`/`output/` (committed there only). Never commit real personal data
  to this public project; do real runs in the mirror.
- This public repo is meant to be mirrored into private copies that `git fetch upstream`;
  keep changes mergeable and don't commit personal data here.
- **`jobme/kokua_toolset.py` is the only Kokua-aware module.** It exports the `TOOLSET` Kokua
  discovers through the `kokua.toolsets` entry point in `pyproject.toml`. jobme does not depend on
  Kokua and must keep importing and running without it, so nothing else in the package may import
  `kokua`. The design is in
  [docs/superpowers/specs/2026-08-28-kokua-integration-design.md](docs/superpowers/specs/2026-08-28-kokua-integration-design.md).
  Two traps it documents: `pdf.py` uses Playwright's **sync** API, so a run has to stay on a worker
  thread with no event loop, and the adapter must not copy the CLI's `.env` walking, which is
  cwd-dependent.
- **There is now a test suite**, mock-only: `uv run pytest` (see Commands above for what it covers).

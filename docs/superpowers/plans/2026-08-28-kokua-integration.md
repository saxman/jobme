# jobme as a Kokua Capability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let Kokua tailor a resume and cover letter to a job posting by driving jobme's existing pipeline, through a toolset jobme ships and a skill that teaches the procedure.

**Architecture:** jobme gains one Kokua-aware module, `jobme/kokua_toolset.py`, registered through the `kokua.toolsets` entry-point group so Kokua discovers it without any change to Kokua's package. The pipeline gains a progress callback, a warnings key, and a cancellation event so a run can be watched and stopped from a Kokua turn. The tool runs the blocking pipeline on a worker thread and marshals progress back onto the event loop.

**Tech Stack:** Python 3.11+, uv, AIMU 0.26.0, Kokua (sibling checkout at `../kokua`), pytest, pytest-asyncio, Playwright.

**Spec:** [docs/superpowers/specs/2026-08-28-kokua-integration-design.md](../specs/2026-08-28-kokua-integration-design.md)

## Global Constraints

- **No em dashes.** Not in prose, docstrings, comments, commit messages, or user-facing strings. Recast with a comma, colon, semicolon, or parentheses. Do not substitute `--` for a dash you wanted. This is a rule in both repositories.
- **Inclusive terminology**: allowlist/blocklist, primary/replica, placeholder/example, main branch.
- **Self-documenting code.** Comment only where the purpose is not obvious, where the code deviates from the obvious approach, or where a caveat cannot be designed away. Never write a comment that restates a name.
- **Kokua's `src/` and `pyproject.toml` must not change.** The only Kokua-repo changes in this plan are documentation (Task 5).
- **jobme must remain installable and runnable without Kokua.** `uv run scripts/jobme.py --jd ...` keeps working unchanged, and `import jobme` must not require Kokua.
- **Never commit real personal data** to this repository. `example/` holds synthetic inputs; `input/` and `output/` are tracked but stay empty here. Real runs happen in the private mirror.
- **Kokua doc line length is 120.** jobme has no configured limit; match the surrounding file.
- Version floors: jobme requires `aimu>=0.26.0`, Kokua requires `aimu>=0.25.0`, and the sibling `../aimu` checkout is 0.26.0, so both are satisfied in one environment.
- The toolset name, the `config.toml` section, and the entry-point key are all the literal string `jobme`.
- The skill's name is the literal string `job-application`.

## File Structure

**jobme repo:**

| File | Responsibility |
|---|---|
| `jobme/pipeline.py` (modify) | Gains `progress`, `cancel`, a `warnings` key, and `RunCancelled` |
| `jobme/kokua_toolset.py` (create) | The only Kokua-aware module: `TOOLSET`, two tools, settings resolution, result formatting |
| `jobme/skill/SKILL.md` (create) | The `job-application` procedure, content rather than code |
| `tests/test_pipeline_runtime.py` (create) | Progress, warnings, and cancellation in the pipeline |
| `tests/test_kokua_toolset.py` (create) | The adapter, with `pipeline.run` stubbed |
| `pyproject.toml` (modify) | Entry point, dev and kokua extras, pytest configuration |
| `README.md` (modify) | A "Use from Kokua" section |
| `CLAUDE.md` (modify) | The rule that `jobme/kokua_toolset.py` is the only Kokua-aware module |

**Kokua repo:** `docs/how-to/install-a-third-party-toolset.md` (create) and `CHANGELOG.md` (modify). Nothing else.

**Deviation from the spec, applied by this plan:** the spec names the adapter `jobme/kokua.py`. This plan uses `jobme/kokua_toolset.py` instead, because inside a module at `jobme/kokua.py` the line `from kokua.registry import Toolset` reads like a self-import even though Python 3's absolute imports resolve it correctly. The spec has been amended to match.

---

### Task 1: The pipeline reports progress, returns warnings, and can be cancelled

**Files:**
- Modify: `pyproject.toml`
- Modify: `jobme/pipeline.py`
- Create: `tests/__init__.py` (empty)
- Test: `tests/test_pipeline_runtime.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `jobme.pipeline.RunCancelled(RuntimeError)`
  - `jobme.pipeline.run(config: Config, *, progress: Callable[[str], None] = print, cancel: threading.Event | None = None) -> dict`, whose returned dict keeps every key it has today (`output_dir`, `resume_html`, `resume_pdf`, `cover_html`, `cover_pdf`, `resume_pages`, `resume_fill`, `summary`) and adds `warnings: list[str]`.
  - `jobme.pipeline._check_cancel(cancel: threading.Event | None) -> None`
  - `jobme.pipeline._with_retry(label: str, fn: Callable[[], T], progress: Callable[[str], None]) -> T`
  - `jobme.pipeline._render_resume(model, inputs, content, out_dir, pdf_backend, *, progress, cancel) -> tuple[Path, Path, int, float | None, list[str]]`

- [ ] **Step 1: Add the test tooling to `pyproject.toml`**

Add after the `[project.scripts]` table:

```toml
[project.optional-dependencies]
# Mock-only test suite: no model, no network, no API keys.
dev = [
    "pytest",
    "pytest-asyncio",
]
```

And at the end of the file:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
# The Kokua toolset's tools are async, so their tests are coroutines with no explicit marker.
asyncio_mode = "auto"
```

Then run `uv sync --all-extras` and create an empty `tests/__init__.py`.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_pipeline_runtime.py`:

```python
"""How a caller other than the CLI drives the pipeline: progress lines, warnings, cancellation.

Every model call is stubbed. Nothing here reaches a provider, a browser, or the network.
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from jobme import pipeline
from jobme.config import Config
from jobme.io_utils import Inputs


def _config(tmp_path: Path) -> Config:
    jd_path = tmp_path / "posting.txt"
    jd_path.write_text("We are hiring an engineer.", encoding="utf-8")
    return Config(
        jd_path=jd_path,
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
        model="ollama:placeholder",
        pdf_backend="playwright",
    )


def _stub_steps(monkeypatch, tmp_path: Path, warnings: list[str]) -> None:
    """Replace every step that would call a model, render, or measure a PDF."""
    inputs = Inputs(cv_markdown="cv", resume_html="<html></html>", job_description="jd")
    monkeypatch.setattr(pipeline, "load_inputs", lambda input_dir, jd_path: inputs)
    monkeypatch.setattr(pipeline, "check_backend", lambda backend: None)
    monkeypatch.setattr(pipeline, "_job_slug", lambda model, job_description, name: "acme-engineer")
    monkeypatch.setattr(pipeline, "_tailor_resume", lambda model, inputs: ("resume content", object()))
    monkeypatch.setattr(
        pipeline,
        "_render_resume",
        lambda model, inputs, content, out_dir, pdf_backend, *, progress, cancel: (
            out_dir / "resume.html",
            out_dir / "resume.pdf",
            2,
            1.28,
            list(warnings),
        ),
    )
    monkeypatch.setattr(pipeline, "_tailor_cover", lambda model, inputs: ("cover content", object()))
    monkeypatch.setattr(
        pipeline,
        "_render_cover",
        lambda model, inputs, content, out_dir, pdf_backend: (
            out_dir / "cover_letter.html",
            out_dir / "cover_letter.pdf",
        ),
    )
    monkeypatch.setattr(pipeline, "_write_summary", lambda *args: tmp_path / "summary.md")


def test_run_reports_progress_through_the_callback_instead_of_printing(monkeypatch, tmp_path, capsys):
    _stub_steps(monkeypatch, tmp_path, warnings=[])
    lines: list[str] = []

    pipeline.run(_config(tmp_path), progress=lines.append)

    assert any("acme-engineer" in line for line in lines)
    assert capsys.readouterr().out == ""


def test_run_returns_the_fit_loops_warnings(monkeypatch, tmp_path):
    _stub_steps(monkeypatch, tmp_path, warnings=["the CV may lack enough relevant content"])

    result = pipeline.run(_config(tmp_path), progress=lambda line: None)

    assert result["warnings"] == ["the CV may lack enough relevant content"]


def test_run_without_warnings_returns_an_empty_list(monkeypatch, tmp_path):
    _stub_steps(monkeypatch, tmp_path, warnings=[])

    result = pipeline.run(_config(tmp_path), progress=lambda line: None)

    assert result["warnings"] == []


def test_run_stops_between_steps_when_the_cancel_event_is_set(monkeypatch, tmp_path):
    _stub_steps(monkeypatch, tmp_path, warnings=[])
    cancel = threading.Event()
    cancel.set()

    with pytest.raises(pipeline.RunCancelled):
        pipeline.run(_config(tmp_path), progress=lambda line: None, cancel=cancel)


def test_check_cancel_passes_when_there_is_no_event():
    pipeline._check_cancel(None)
    pipeline._check_cancel(threading.Event())


def test_with_retry_reports_a_transient_failure_through_progress(monkeypatch):
    monkeypatch.setattr(pipeline.time, "sleep", lambda seconds: None)
    lines: list[str] = []
    attempts = {"count": 0}

    def flaky() -> str:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise ConnectionError("reset by peer")
        return "done"

    assert pipeline._with_retry("tailoring resume", flaky, lines.append) == "done"
    assert any("tailoring resume" in line for line in lines)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_pipeline_runtime.py -v`
Expected: FAIL. `AttributeError: module 'jobme.pipeline' has no attribute 'RunCancelled'` and `_check_cancel`, and `run()` rejecting the `progress` keyword.

- [ ] **Step 4: Add `RunCancelled` and `_check_cancel` to `jobme/pipeline.py`**

Add `import threading` to the imports. Immediately after the `_T = TypeVar("_T")` line, add:

```python
class RunCancelled(RuntimeError):
    """The caller asked for the run to stop. Raised at a step boundary, never mid-step.

    A Kokua turn can be stopped while the pipeline runs on a worker thread, and a thread cannot be
    interrupted. Checking an event between steps is what stops the spend on model calls nobody is
    waiting for any more.
    """


def _check_cancel(cancel: threading.Event | None) -> None:
    if cancel is not None and cancel.is_set():
        raise RunCancelled("cancelled before the next step")
```

- [ ] **Step 5: Turn `_with_retry`'s print into a progress call**

Change the signature at `jobme/pipeline.py:58` and its one print:

```python
def _with_retry(label: str, fn: Callable[[], _T], progress: Callable[[str], None]) -> _T:
    """Run ``fn``, retrying transient API failures with exponential backoff.

    Each pipeline step is self-contained and re-runnable (fresh client/loop, idempotent
    file writes), so a retry simply re-executes the whole step. Non-transient errors
    propagate immediately.
    """
    for attempt in range(MAX_API_RETRIES + 1):
        try:
            return fn()
        except _TRANSIENT_API_ERRORS as error:
            if attempt == MAX_API_RETRIES:
                raise
            delay = API_RETRY_BASE_DELAY * 2**attempt
            progress(
                f"[jobme]   {label}: transient API error ({type(error).__name__}); "
                f"retry {attempt + 1}/{MAX_API_RETRIES} in {delay:.0f}s..."
            )
            time.sleep(delay)
    raise AssertionError("unreachable")  # loop either returns or raises
```

`progress` is positional and required here, deliberately: every call site is in this module, and a default would let a new one silently swallow its retry notice.

- [ ] **Step 6: Make `_render_resume` take `progress`/`cancel` and return its warnings**

Change its signature and return type:

```python
def _render_resume(
    model: str,
    inputs: Inputs,
    content: str,
    out_dir: Path,
    pdf_backend: str,
    *,
    progress: Callable[[str], None],
    cancel: threading.Event | None,
) -> tuple[Path, Path, int, float | None, list[str]]:
```

Replace each of the four `print(...)` calls in its body with `progress(...)` of the same string. Add `_check_cancel(cancel)` as the first statement inside both `for _ in range(MAX_PAGE_FIT_RETRIES):` loops, so a cancelled run stops before paying for another round.

Replace the low-fill warning block and the return with:

```python
    warnings: list[str] = []
    if content_expanded and fill is not None and fill < LOW_FILL_WARNING:
        warning = (
            f"best resume fills only ~{fill:.2f} of {TARGET_RESUME_PAGES} pages even after "
            "expansion; the CV may lack enough relevant content for a full two-page resume"
        )
        warnings.append(warning)
        progress(f"[jobme] WARNING: {warning}.")

    return html_path, pdf_path, pages, fill, warnings
```

The warning is both returned and reported: returned so a caller can put it in front of a user, reported so CLI output keeps the line it has today.

- [ ] **Step 7: Thread everything through `run`**

Replace `run` at `jobme/pipeline.py:308` with:

```python
def run(
    config: Config,
    *,
    progress: Callable[[str], None] = print,
    cancel: threading.Event | None = None,
) -> dict:
    """Run the full pipeline for one job posting; returns paths to produced files.

    ``progress`` receives each status line. It defaults to ``print`` so the CLI is unaffected;
    an embedder (Kokua's toolset) passes a callback that puts the line on its channel instead.
    ``cancel`` is checked between steps: a set event ends the run with :class:`RunCancelled`
    rather than paying for the calls still ahead of it.
    """
    inputs = load_inputs(config.input_dir, config.jd_path)
    check_backend(config.pdf_backend)  # fail fast before any LLM calls
    _check_cancel(cancel)
    slug = _with_retry("job slug", lambda: _job_slug(config.model, inputs.job_description, config.name), progress)
    out_dir = make_output_dir(config.output_dir, slug)

    progress(f"[jobme] Job: {slug}")
    progress(f"[jobme] Model: {config.model} | PDF backend: {config.pdf_backend}")

    _check_cancel(cancel)
    progress("[jobme] Tailoring resume (accuracy & intrigue review)...")
    resume_content, resume_loop = _with_retry(
        "tailoring resume", lambda: _tailor_resume(config.model, inputs), progress
    )
    (out_dir / "resume_content.md").write_text(resume_content, encoding="utf-8")

    _check_cancel(cancel)
    progress("[jobme] Rendering resume HTML and fitting to 2 pages...")
    resume_html, resume_pdf, pages, fill, warnings = _with_retry(
        "rendering resume",
        lambda: _render_resume(
            config.model, inputs, resume_content, out_dir, config.pdf_backend, progress=progress, cancel=cancel
        ),
        progress,
    )

    _check_cancel(cancel)
    progress("[jobme] Writing cover letter (accuracy & intrigue review)...")
    cover_content, cover_loop = _with_retry(
        "writing cover letter", lambda: _tailor_cover(config.model, inputs), progress
    )
    (out_dir / "cover_letter.txt").write_text(cover_content, encoding="utf-8")

    _check_cancel(cancel)
    progress("[jobme] Rendering cover letter HTML and PDF...")
    cover_html, cover_pdf = _with_retry(
        "rendering cover letter",
        lambda: _render_cover(config.model, inputs, cover_content, out_dir, config.pdf_backend),
        progress,
    )

    artifacts = [resume_html, resume_pdf, cover_html, cover_pdf]
    summary_path = _write_summary(out_dir, config, slug, pages, fill, artifacts, resume_loop, cover_loop)

    progress(f"\n[jobme] Done. Output in {out_dir}")
    for path in [*artifacts, summary_path]:
        progress(f"  - {path}")

    return {
        "output_dir": out_dir,
        "resume_html": resume_html,
        "resume_pdf": resume_pdf,
        "cover_html": cover_html,
        "cover_pdf": cover_pdf,
        "resume_pages": pages,
        "resume_fill": fill,
        "summary": summary_path,
        "warnings": warnings,
    }
```

- [ ] **Step 8: Run the tests to verify they pass**

Run: `uv run pytest tests/test_pipeline_runtime.py -v`
Expected: PASS, 6 tests.

- [ ] **Step 9: Verify the CLI is unchanged**

Run: `uv run scripts/jobme.py --help`
Expected: the usage text, no traceback. `grep -n "print(" jobme/pipeline.py` should now find nothing.

- [ ] **Step 10: Commit**

```bash
git add pyproject.toml jobme/pipeline.py tests/__init__.py tests/test_pipeline_runtime.py
git commit -m "feat(pipeline): report progress through a callback, return warnings, allow cancellation

An embedder cannot use print for progress, cannot see the low-fill warning
buried in stdout, and cannot stop a run it is no longer waiting for. The CLI
passes none of the three and behaves exactly as before."
```

---

### Task 2: The toolset registers, resolves its settings, and reports setup

**Files:**
- Create: `jobme/kokua_toolset.py`
- Modify: `pyproject.toml`
- Test: `tests/test_kokua_toolset.py`

**Interfaces:**
- Consumes: `jobme.pipeline.RunCancelled` and the extended `run` from Task 1.
- Produces:
  - `jobme.kokua_toolset.TOOLSET: kokua.registry.Toolset`, `TOOLSET.name == "jobme"`
  - `jobme.kokua_toolset.TOOLSET_NAME: str = "jobme"`
  - `jobme.kokua_toolset.Settings` (frozen dataclass: `input_dir: Path`, `output_dir: Path`, `model: str`, `pdf_backend: str`)
  - `jobme.kokua_toolset.resolve_settings(config) -> Settings`
  - `jobme.kokua_toolset.REQUIRED_INPUTS: tuple[str, ...] = ("cv.md", "resume.html")`
  - `jobme.kokua_toolset.build(ctx) -> list`, returning `[tailor_application, check_application_setup]`
  - the async tool `check_application_setup() -> str`

- [ ] **Step 1: Make Kokua available for development**

Add to `pyproject.toml`, extending the `[project.optional-dependencies]` table from Task 1 and adding a source:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
]
# The Kokua adapter's tests import Kokua. Kokua is not on PyPI, so this extra is only
# installable from a sibling checkout; see [tool.uv.sources] below. jobme itself never
# depends on Kokua, and the pipeline runs with it absent.
kokua = [
    "kokua",
]

[tool.uv.sources]
kokua = { path = "../kokua", editable = true }
```

Run `uv sync --all-extras` and confirm `uv run python -c "import kokua; print(kokua.__file__)"` points at the sibling checkout.

- [ ] **Step 2: Register the entry point**

Add to `pyproject.toml`:

```toml
# Kokua discovers a toolset through this group, with no change to its own package. The key is
# the name an agent declares in [agents.<name>].tools, and it must equal TOOLSET.name.
[project.entry-points."kokua.toolsets"]
jobme = "jobme.kokua_toolset:TOOLSET"
```

- [ ] **Step 3: Write the failing tests**

Create `tests/test_kokua_toolset.py`:

```python
"""The Kokua adapter: settings resolution, the setup report, and the registration contract.

Mock-only. ``pipeline.run`` is stubbed everywhere it is reached, so nothing here calls a model,
launches a browser, or touches the network.
"""

from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path

import pytest

pytest.importorskip("kokua", reason="the Kokua adapter tests need the kokua extra installed")

from kokua.config import AssistantConfig  # noqa: E402
from kokua.registry import LiveState, ToolsetContext  # noqa: E402

from jobme import kokua_toolset  # noqa: E402
from jobme.config import DEFAULT_MODEL  # noqa: E402
from jobme.kokua_toolset import TOOLSET, TOOLSET_NAME, build, resolve_settings  # noqa: E402


def _config(tmp_path: Path, **settings) -> AssistantConfig:
    config = AssistantConfig(data_dir=tmp_path / "data", config_path=tmp_path / "config.toml")
    config.toolset_settings[TOOLSET_NAME] = {
        "input_dir": "",
        "output_dir": "",
        "model": "",
        "pdf_backend": "playwright",
        **settings,
    }
    return config


def _tools(config: AssistantConfig, notify=None) -> dict:
    ctx = ToolsetContext(state=LiveState(config=config, notify=notify), agent=None, agent_name="assistant")
    return {fn.__name__: fn for fn in build(ctx)}


def _seed_inputs(input_dir: Path) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "cv.md").write_text("# CV", encoding="utf-8")
    (input_dir / "resume.html").write_text("<html></html>", encoding="utf-8")


def test_empty_settings_resolve_under_the_kokua_data_directory(tmp_path):
    settings = resolve_settings(_config(tmp_path))

    assert settings.input_dir == tmp_path / "data" / "jobme" / "input"
    assert settings.output_dir == tmp_path / "data" / "jobme" / "output"


def test_explicit_settings_win(tmp_path):
    settings = resolve_settings(
        _config(tmp_path, input_dir=str(tmp_path / "elsewhere"), model="ollama:qwen3:8b")
    )

    assert settings.input_dir == tmp_path / "elsewhere"
    assert settings.model == "ollama:qwen3:8b"


def test_an_empty_model_falls_through_to_jobmes_own_default(tmp_path, monkeypatch):
    monkeypatch.delenv("JOBME_MODEL", raising=False)

    assert resolve_settings(_config(tmp_path)).model == DEFAULT_MODEL


def test_both_tools_are_offered_even_with_nothing_set_up(tmp_path):
    assert set(_tools(_config(tmp_path))) == {"tailor_application", "check_application_setup"}


async def test_check_reports_each_missing_input(tmp_path, monkeypatch):
    monkeypatch.setattr(kokua_toolset, "check_backend", lambda backend: None)

    report = await _tools(_config(tmp_path))["check_application_setup"]()

    assert "cv.md: MISSING" in report
    assert "resume.html: MISSING" in report


async def test_check_reports_a_ready_setup(tmp_path, monkeypatch):
    monkeypatch.setattr(kokua_toolset, "check_backend", lambda backend: None)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "placeholder")
    config = _config(tmp_path, model="anthropic:claude-opus-4-8")
    _seed_inputs(resolve_settings(config).input_dir)

    report = await _tools(config)["check_application_setup"]()

    assert "MISSING" not in report
    assert "ANTHROPIC_API_KEY" not in report


async def test_check_names_the_absent_api_key_variable(tmp_path, monkeypatch):
    monkeypatch.setattr(kokua_toolset, "check_backend", lambda backend: None)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    config = _config(tmp_path, model="anthropic:claude-opus-4-8")
    _seed_inputs(resolve_settings(config).input_dir)

    assert "ANTHROPIC_API_KEY" in await _tools(config)["check_application_setup"]()


async def test_check_reports_an_unusable_pdf_backend(tmp_path, monkeypatch):
    def refuse(backend: str) -> None:
        raise RuntimeError("chromium is not installed")

    monkeypatch.setattr(kokua_toolset, "check_backend", refuse)

    assert "chromium is not installed" in await _tools(_config(tmp_path))["check_application_setup"]()


def test_the_entry_point_key_matches_the_toolset_name():
    registered = {entry.name: entry for entry in entry_points(group="kokua.toolsets")}

    assert "jobme" in registered, "run `uv sync --all-extras` so the entry point is installed"
    assert registered["jobme"].load() is TOOLSET
    assert TOOLSET.name == "jobme"


def test_every_declared_setting_has_a_section_key():
    assert {setting.key for setting in TOOLSET.settings} == {
        "input_dir",
        "output_dir",
        "model",
        "pdf_backend",
    }
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `uv run pytest tests/test_kokua_toolset.py -v`
Expected: FAIL at collection with `ModuleNotFoundError: No module named 'jobme.kokua_toolset'`.

If instead the whole module SKIPS, the `kokua` extra is not installed: run `uv sync --all-extras` and try again. A silent skip here would hide every remaining test in this plan.

- [ ] **Step 5: Write the adapter's settings, setup report, and toolset**

Create `jobme/kokua_toolset.py`:

```python
"""jobme as a Kokua toolset: the only module in this package that knows Kokua exists.

Kokua discovers this through the ``kokua.toolsets`` entry point in ``pyproject.toml``, which is the
same seam every toolset Kokua itself ships arrives through. jobme does not depend on Kokua: an entry
point is inert unless something loads its group, so nothing here is imported unless Kokua's plugin
loader does it.

Two things about the shape are worth knowing before changing it.

``jobme/pdf.py`` uses Playwright's **sync** API, which raises when a loop is running in the calling
thread. That is why a run goes to ``asyncio.to_thread`` and why it can never be moved onto the event
loop, however tempting a direct ``await`` looks.

Unlike ``jobme.cli``, this module does not walk parent directories for ``.env`` files. That is
cwd-dependent behavior belonging to a command line; under Kokua the API key comes from the process
environment, and ``check_application_setup`` says so when it is absent.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from aimu.tools import tool
from kokua.registry import Setting, Toolset, ToolsetContext

from . import pipeline
from .config import DEFAULT_PDF_BACKEND, Config, resolve_model
from .io_utils import slugify
from .pdf import check_backend

TOOLSET_NAME = "jobme"

#: Without these two the pipeline cannot start. Cover-letter samples and guidance.md are optional.
REQUIRED_INPUTS = ("cv.md", "resume.html")

#: The skill that teaches the procedure, reported by check_application_setup so a user who copied
#: the toolset in but not the skill finds out before wondering why the assistant improvises.
SKILL_NAME = "job-application"

# Which environment variable a provider's key lives in. Ollama needs none, so its absence from this
# map is the answer rather than a gap.
_API_KEY_ENV = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}


@dataclass(frozen=True)
class Settings:
    """One run's resolved configuration, with every ``[jobme]`` default already applied."""

    input_dir: Path
    output_dir: Path
    model: str
    pdf_backend: str


def resolve_settings(config) -> Settings:
    """Read the ``[jobme]`` section, resolving an empty value to its derived default.

    A ``Setting`` default is static and has no view of ``AssistantConfig``, so "" is how a default
    that depends on ``$KOKUA_HOME`` gets declared at all. ``[github_backup].repo`` uses the same
    pattern. An empty model falls all the way through to jobme's own resolution, so ``JOBME_MODEL``
    keeps working and Kokua's assistant model is deliberately not consulted: tailoring a resume is
    not the job the conversation model was chosen for.
    """
    section = config.toolset_settings.get(TOOLSET_NAME, {})
    base = config.data_dir / TOOLSET_NAME
    return Settings(
        input_dir=Path(section.get("input_dir") or base / "input").expanduser(),
        output_dir=Path(section.get("output_dir") or base / "output").expanduser(),
        model=resolve_model(section.get("model") or None),
        pdf_backend=section.get("pdf_backend") or DEFAULT_PDF_BACKEND,
    )


def _missing_api_key(model: str) -> Optional[str]:
    """The environment variable this model needs and does not have, if any."""
    variable = _API_KEY_ENV.get(model.split(":", 1)[0])
    return variable if variable and not os.environ.get(variable) else None


def build(ctx: ToolsetContext) -> list:
    """Both tools, always.

    Unlike ``github_backup``, which offers nothing until its repository is configured, a missing
    ``cv.md`` is exactly what ``check_application_setup`` exists to report. Hiding the toolset when
    inputs are absent would remove the thing that explains the absence.
    """
    config = ctx.config

    @tool
    async def check_application_setup() -> str:
        """Report whether jobme can tailor an application: inputs, PDF backend, API key, skill.

        Read-only and cheap. Call this before the first tailoring run of a session, so a missing CV
        or an uninstalled browser surfaces before several minutes of billed model calls.
        """
        settings = resolve_settings(config)
        lines = [f"Input directory: {settings.input_dir}", f"Output directory: {settings.output_dir}"]

        for name in REQUIRED_INPUTS:
            state = "present" if (settings.input_dir / name).is_file() else "MISSING (required)"
            lines.append(f"{name}: {state}")

        samples = sorted(settings.input_dir.glob("cover_letter*.txt")) if settings.input_dir.is_dir() else []
        lines.append(f"cover_letter*.txt voice samples: {len(samples)} (optional)")
        guidance = (settings.input_dir / "guidance.md").is_file()
        lines.append(f"guidance.md: {'present' if guidance else 'absent'} (optional)")

        lines.append(f"Model: {settings.model}")
        variable = _missing_api_key(settings.model)
        if variable:
            lines.append(f"{variable} is not set in Kokua's environment, so this model cannot be reached.")

        try:
            await asyncio.to_thread(check_backend, settings.pdf_backend)
            lines.append(f"PDF backend {settings.pdf_backend}: ready")
        except Exception as error:
            lines.append(f"PDF backend {settings.pdf_backend}: unusable ({error})")

        skill = config.skills_dir / SKILL_NAME / "SKILL.md"
        lines.append(f"{SKILL_NAME} skill: {'installed' if skill.is_file() else 'not installed'}")

        return "\n".join(lines)

    return [check_application_setup]


GUIDANCE = (
    " You can tailor the user's resume and cover letter to a specific job posting with "
    "`tailor_application`, which produces send-ready PDFs. A run takes several minutes and costs "
    "real money, so confirm the posting and the job title with the user before calling it, and "
    "never call it twice for one posting without being asked. Call `check_application_setup` before "
    "the first run of a session, and whenever a run fails, so a missing input is found cheaply. "
    "Never write resume or cover-letter content yourself: jobme's guarantee is that nothing appears "
    "in either document that is not supported by the user's cv.md, and text you compose has no such "
    "guarantee. If the user wants a claim the resume does not make, tell them to add it to cv.md."
)

TOOLSET = Toolset(
    name=TOOLSET_NAME,
    description="Tailor a resume and cover letter to a job posting and produce send-ready PDFs.",
    build=build,
    guidance=GUIDANCE,
    settings=(
        # "" means "derive it": input_dir and output_dir land under $KOKUA_HOME/data/jobme, and an
        # empty model falls through to JOBME_MODEL and then jobme's own default.
        Setting("input_dir", str, ""),
        Setting("output_dir", str, ""),
        Setting("model", str, ""),
        Setting("pdf_backend", str, DEFAULT_PDF_BACKEND),
    ),
)
```

`Config`, `slugify`, `shutil`, `threading`, `datetime`, `Callable`, and `pipeline` are imported here and used by Task 3; leave them in place.

- [ ] **Step 6: Run the tests**

Run: `uv run pytest tests/test_kokua_toolset.py -v`
Expected: every test PASSES except `test_both_tools_are_offered_even_with_nothing_set_up`, which FAILS because `tailor_application` does not exist yet. That failure is Task 3's starting point.

- [ ] **Step 7: Confirm jobme still works without Kokua**

Run:

```bash
uv run python -c "
import sys, jobme
assert 'kokua' not in sys.modules, 'importing jobme must not pull in Kokua'
print(jobme.run)
"
```

Expected: prints the function. This is the invariant that matters and it holds even with Kokua
installed: only `jobme.kokua_toolset` imports Kokua, and nothing in the package imports that.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml jobme/kokua_toolset.py tests/test_kokua_toolset.py
git commit -m "feat(kokua): register jobme as a toolset, with settings and a setup report

The entry point is how Kokua discovers a third party's capability, so nothing
in Kokua changes. Empty settings derive their defaults under \$KOKUA_HOME."
```

(The `tailor_application` test stays red until Task 3. If your workflow forbids committing with a failing test, do Tasks 2 and 3 as one commit.)

---

### Task 3: `tailor_application` runs the pipeline and publishes the PDFs

**Files:**
- Modify: `jobme/kokua_toolset.py`
- Test: `tests/test_kokua_toolset.py`

**Interfaces:**
- Consumes: `resolve_settings`, `Settings`, `REQUIRED_INPUTS`, `build` from Task 2; `pipeline.run` and `pipeline.RunCancelled` from Task 1.
- Produces: the async tool `tailor_application(job_description: str, name: str = "") -> str`, plus `_channel_progress(notify, loop) -> Callable[[str], None]`, `_publish(result, downloads) -> list[tuple[str, Path, str]]`, and `_format_result(result, downloads) -> str`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_kokua_toolset.py`:

```python
def _fake_run(tmp_path: Path, warnings=(), lines=("[jobme] Job: acme-engineer",)):
    """Stand in for pipeline.run: emits progress, writes the artifacts, returns the real shape."""

    def run(config, *, progress, cancel):
        out_dir = config.output_dir / "20260828-120000_acme-engineer"
        out_dir.mkdir(parents=True, exist_ok=True)
        for line in lines:
            progress(line)
        resume_pdf = out_dir / "resume.pdf"
        cover_pdf = out_dir / "cover_letter.pdf"
        resume_pdf.write_bytes(b"%PDF-resume")
        cover_pdf.write_bytes(b"%PDF-cover")
        return {
            "output_dir": out_dir,
            "resume_html": out_dir / "resume.html",
            "resume_pdf": resume_pdf,
            "cover_html": out_dir / "cover_letter.html",
            "cover_pdf": cover_pdf,
            "resume_pages": 2,
            "resume_fill": 1.31,
            "summary": out_dir / "summary.md",
            "warnings": list(warnings),
        }

    return run


async def test_tailor_application_publishes_both_pdfs_to_the_downloads_folder(tmp_path, monkeypatch):
    config = _config(tmp_path)
    _seed_inputs(resolve_settings(config).input_dir)
    monkeypatch.setattr(kokua_toolset.pipeline, "run", _fake_run(tmp_path))

    report = await _tools(config)["tailor_application"]("We are hiring an engineer.")

    published = sorted(path.name for path in config.downloads_path.iterdir())
    assert published == [
        "20260828-120000-acme-engineer_cover_letter.pdf",
        "20260828-120000-acme-engineer_resume.pdf",
    ]
    assert "/download/20260828-120000-acme-engineer_resume.pdf" in report
    assert "2 page" in report


async def test_tailor_application_streams_progress_to_the_channel(tmp_path, monkeypatch):
    config = _config(tmp_path)
    _seed_inputs(resolve_settings(config).input_dir)
    monkeypatch.setattr(kokua_toolset.pipeline, "run", _fake_run(tmp_path, lines=("[jobme] Job: acme",)))
    sent: list[str] = []

    async def notify(text: str) -> None:
        sent.append(text)

    await _tools(config, notify=notify)["tailor_application"]("We are hiring an engineer.")

    assert sent == ["[jobme] Job: acme"]


async def test_tailor_application_works_without_a_channel(tmp_path, monkeypatch):
    config = _config(tmp_path)
    _seed_inputs(resolve_settings(config).input_dir)
    monkeypatch.setattr(kokua_toolset.pipeline, "run", _fake_run(tmp_path))

    report = await _tools(config, notify=None)["tailor_application"]("We are hiring an engineer.")

    assert "/download/" in report


async def test_tailor_application_surfaces_warnings_in_its_result(tmp_path, monkeypatch):
    config = _config(tmp_path)
    _seed_inputs(resolve_settings(config).input_dir)
    monkeypatch.setattr(
        kokua_toolset.pipeline, "run", _fake_run(tmp_path, warnings=["the CV may lack enough content"])
    )

    report = await _tools(config)["tailor_application"]("We are hiring an engineer.")

    assert "the CV may lack enough content" in report


async def test_tailor_application_refuses_without_a_cv(tmp_path, monkeypatch):
    def explode(config, *, progress, cancel):
        raise AssertionError("the pipeline must not start without the required inputs")

    monkeypatch.setattr(kokua_toolset.pipeline, "run", explode)

    report = await _tools(_config(tmp_path))["tailor_application"]("We are hiring an engineer.")

    assert "cv.md" in report and "check_application_setup" in report


async def test_tailor_application_refuses_an_empty_posting(tmp_path, monkeypatch):
    def explode(config, *, progress, cancel):
        raise AssertionError("the pipeline must not start without a posting")

    config = _config(tmp_path)
    _seed_inputs(resolve_settings(config).input_dir)
    monkeypatch.setattr(kokua_toolset.pipeline, "run", explode)

    assert "posting" in await _tools(config)["tailor_application"]("   ")


async def test_a_cancelled_run_reports_rather_than_raises(tmp_path, monkeypatch):
    def cancelled(config, *, progress, cancel):
        raise kokua_toolset.pipeline.RunCancelled("cancelled before the next step")

    config = _config(tmp_path)
    _seed_inputs(resolve_settings(config).input_dir)
    monkeypatch.setattr(kokua_toolset.pipeline, "run", cancelled)

    assert "cancelled" in (await _tools(config)["tailor_application"]("We are hiring.")).lower()


async def test_a_failed_run_reports_the_reason(tmp_path, monkeypatch):
    def fail(config, *, progress, cancel):
        raise ValueError("CV markdown (input/cv.md) is empty")

    config = _config(tmp_path)
    _seed_inputs(resolve_settings(config).input_dir)
    monkeypatch.setattr(kokua_toolset.pipeline, "run", fail)

    report = await _tools(config)["tailor_application"]("We are hiring.")

    assert "cv.md" in report and "empty" in report
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_kokua_toolset.py -v`
Expected: FAIL with `KeyError: 'tailor_application'` on each new test.

- [ ] **Step 3: Add the progress bridge and the result formatting**

Insert into `jobme/kokua_toolset.py`, after `_missing_api_key`:

```python
def _discard(done) -> None:
    """Consume a progress send's outcome.

    Without this a channel that dropped a line surfaces later as asyncio's "exception was never
    retrieved" warning, which says nothing useful about a run that otherwise succeeded.
    """
    if not done.cancelled():
        done.exception()


def _channel_progress(notify, loop) -> Callable[[str], None]:
    """Turn the pipeline thread's progress lines into channel messages, without blocking it.

    Fire and forget on purpose: the thread must not wait on a socket, and a lost progress line is
    not worth failing a run over. Degrades to a no-op when there is no channel, which is the case
    for a spawned worker.
    """
    if notify is None:
        return lambda line: None

    def send(line: str) -> None:
        future = asyncio.run_coroutine_threadsafe(notify(line), loop)
        future.add_done_callback(_discard)

    return send


def _publish(result: dict, downloads: Path) -> list[tuple[str, Path, str]]:
    """Copy the finished PDFs where the web front end serves them, prefixed by the run's folder name.

    That folder is already timestamped and slugged, and the downloads folder is flat and served by
    basename, so the prefix is what keeps two applications from both claiming resume.pdf.
    """
    downloads.mkdir(parents=True, exist_ok=True)
    prefix = slugify(Path(result["output_dir"]).name)
    published = []
    for label, key in (("Resume", "resume_pdf"), ("Cover letter", "cover_pdf")):
        source = Path(result[key])
        target = downloads / f"{prefix}_{source.name}"
        shutil.copy2(source, target)
        published.append((label, target, f"/download/{target.name}"))
    return published


def _format_result(result: dict, downloads: Path) -> str:
    """The whole outcome in one tool result: where it went, how it fits, and every warning.

    Both a filesystem path and a /download link are given for each PDF. The link only resolves in
    the web front end, and a toolset has no way to ask which front end is attached.
    """
    fill = result["resume_fill"]
    lines = [
        f"Tailored application written to {result['output_dir']}.",
        f"Resume: {result['resume_pages']} page(s)" + (f", fill ~{fill:.2f}." if fill is not None else "."),
    ]
    for label, path, link in _publish(result, downloads):
        lines.append(f"{label}: {path} (web UI: {link})")
    lines += [f"Warning: {warning}." for warning in result.get("warnings", [])]
    return "\n".join(lines)
```

- [ ] **Step 4: Add the tool itself**

Inside `build`, before `check_application_setup`, add:

```python
    @tool
    async def tailor_application(job_description: str, name: str = "") -> str:
        """Tailor the user's resume and cover letter to a job posting and produce PDFs.

        Pass the posting's full text, not a summary or a URL: the whole pipeline is grounded in the
        text it is given. `name` is an optional "Company - Title" label for the output folder. This
        takes several minutes and costs real money, so confirm with the user before calling it.
        """
        settings = resolve_settings(config)
        posting = job_description.strip()
        if not posting:
            return "No job posting text was supplied. Pass the posting's full text as job_description."

        missing = [name_ for name_ in REQUIRED_INPUTS if not (settings.input_dir / name_).is_file()]
        if missing:
            return (
                f"Cannot tailor an application: {', '.join(missing)} not found in {settings.input_dir}. "
                "Call check_application_setup for the full picture."
            )

        settings.output_dir.mkdir(parents=True, exist_ok=True)
        jd_path = settings.output_dir / f"posting-{datetime.now():%Y%m%d-%H%M%S}.txt"
        jd_path.write_text(posting, encoding="utf-8")

        run_config = Config(
            jd_path=jd_path,
            input_dir=settings.input_dir,
            output_dir=settings.output_dir,
            model=settings.model,
            pdf_backend=settings.pdf_backend,
            name=name or None,
        )
        cancel = threading.Event()
        progress = _channel_progress(ctx.state.notify, asyncio.get_running_loop())

        try:
            result = await asyncio.to_thread(_run_pipeline, run_config, progress, cancel)
        except asyncio.CancelledError:
            # A stopped turn cannot interrupt the thread, so ask the run to stop at its next step
            # boundary. Without this it keeps spending on model calls nobody is waiting for.
            cancel.set()
            raise
        except (FileNotFoundError, ValueError, RuntimeError) as error:
            return f"The application run failed: {error}."

        if result is None:
            return "The application run was cancelled before it finished."
        return _format_result(result, config.downloads_path)
```

And add, next to `_publish`:

```python
def _run_pipeline(run_config: Config, progress: Callable[[str], None], cancel: threading.Event) -> Optional[dict]:
    """Run the pipeline on a worker thread, answering None for a cancelled run.

    The cancellation is absorbed here rather than raised out of the thread because the awaiting task
    is usually gone by then, and an exception set on a future nobody retrieves is logged as a warning
    that describes the wrong problem.
    """
    try:
        return pipeline.run(run_config, progress=progress, cancel=cancel)
    except pipeline.RunCancelled:
        return None
```

Finally change `build`'s return to `return [tailor_application, check_application_setup]`.

- [ ] **Step 5: Run the whole suite**

Run: `uv run pytest -v`
Expected: PASS, with no skipped modules. If `tests/test_kokua_toolset.py` reports as skipped, run `uv sync --all-extras` first.

- [ ] **Step 6: Commit**

```bash
git add jobme/kokua_toolset.py tests/test_kokua_toolset.py
git commit -m "feat(kokua): tailor_application runs the pipeline and publishes its PDFs

The pipeline is synchronous and Playwright's sync API refuses a thread with a
running loop, so the run goes to a worker thread and its progress is marshalled
back onto the loop. A stopped turn sets the cancel event rather than leaving the
thread to spend on calls nobody awaits."
```

---

### Task 4: The skill and jobme's documentation

**Files:**
- Create: `jobme/skill/SKILL.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: the tool names `tailor_application` and `check_application_setup` from Tasks 2 and 3.
- Produces: nothing code depends on. `SKILL_NAME` in `jobme/kokua_toolset.py` already expects the directory to be named `job-application`.

- [ ] **Step 1: Write the skill**

Create `jobme/skill/SKILL.md`:

```markdown
---
name: job-application
description: Tailor the user's resume and cover letter to a specific job posting and produce send-ready PDFs. Use when the user shares a job posting, asks to apply somewhere, or asks for a resume tailored to a role.
license: Apache-2.0
compatibility: Requires the `jobme` toolset (pip install jobme, then declare "jobme" in the agent's tools).
metadata:
  author: jobme
---

# Tailoring a job application

A run costs real money and takes several minutes, and every document it produces is grounded in
the user's `cv.md`. Both facts drive the steps below: get the inputs right before spending, and
never put words in the user's mouth afterwards.

## Steps

1. **Get the whole posting, verbatim.** If the user pastes it, use exactly what they pasted. If
   they give a URL, fetch it first and show them what came back before going further. Never
   summarize a posting into `tailor_application`: the pipeline tailors against the text it is
   given, so a summary quietly produces a worse resume and nothing about the result looks wrong.

2. **Check the setup before the first run of a session.** Call `check_application_setup`. It is
   read-only and fast, and it catches a missing `cv.md`, an uninstalled browser, or an absent API
   key before several minutes of billed calls rather than after. Skip it only if a run already
   succeeded in this conversation.

3. **Confirm before running.** Tell the user the company and title you read off the posting, say
   the run takes a few minutes and costs money, and wait for them to agree. Kokua may also ask
   them to approve the tool call; that is a backstop, not a substitute for setting the
   expectation.

4. **Call `tailor_application`** with the posting's full text, and pass `name` as
   `"Company - Title"` whenever you can read both off the posting. That label names the output
   folder, which is what makes an application findable weeks later.

5. **Report every warning verbatim.** The tool returns page count, fill, download links, and any
   warnings. A low-fill warning means the CV does not contain enough relevant material for a
   full two-page resume. Say that plainly. Rewording it into "looks good" is the failure this
   step exists to prevent.

6. **Never write resume or cover-letter content yourself.** jobme's guarantee is that nothing
   appears in either document that the CV does not support. If the user wants a claim the resume
   does not make, the answer is to add it to `cv.md` and run again, not to draft a sentence for
   them.

## Notes

- The PDFs are copied into Kokua's downloads folder, so the `/download/...` links work in the web
  UI. The tool also gives the full path, which is what a terminal user needs.
- Inputs live in the directory `check_application_setup` names, `[jobme] input_dir` in
  `config.toml`. `cv.md` is the content source of truth and `resume.html` is the style template.
  `cover_letter*.txt` files are optional voice samples; `guidance.md` is optional free-form
  guidance applied to every generation step.
- If a run fails, call `check_application_setup` before retrying. Retrying blind spends the same
  money on the same failure.
```

- [ ] **Step 2: Verify the skill's frontmatter parses**

Run:

```bash
uv run python -c "
import pathlib, re
text = pathlib.Path('jobme/skill/SKILL.md').read_text()
head = re.match(r'---\n(.*?)\n---\n', text, re.S).group(1)
print(head.splitlines()[0])
"
```

Expected: `name: job-application`.

- [ ] **Step 3: Add the README section**

Append to `README.md`:

```markdown
## Use from Kokua

jobme registers itself as a [Kokua](https://github.com/saxman/kokua) toolset, so the assistant can
tailor an application in conversation. Kokua discovers it through an entry point; nothing in Kokua
changes.

1. Install jobme into Kokua's environment. `uv pip install --editable` installs it without
   touching Kokua's `pyproject.toml`, which matches "nothing in Kokua changes" above:

   ```bash
   cd ../kokua && uv pip install --editable ../jobme
   uv run playwright install chromium   # once, for the default PDF backend
   ```

   If you'd rather have jobme recorded as a dependency of your own Kokua checkout, `uv add
   --editable ../jobme` does that, at the cost of a `pyproject.toml` edit that a later `git pull`
   in Kokua can conflict with.

2. Declare the toolset in `$KOKUA_HOME/config.toml`, and gate the expensive tool:

   ```toml
   [agents.assistant]
   tools = ["jobme", ...]

   [security]
   confirm_tools = ["tailor_application", ...]

   [jobme]
   input_dir = ""        # empty: $KOKUA_HOME/data/jobme/input
   output_dir = ""       # empty: $KOKUA_HOME/data/jobme/output
   model = ""            # empty: JOBME_MODEL, then jobme's default
   pdf_backend = "playwright"
   ```

   Gating `tailor_application` means a run always needs your approval. It also means jobme can
   never run in a scheduled task, since a gated tool auto-denies in an unattended turn. That is
   deliberate for a tool this expensive.

3. Install the skill that teaches the procedure:

   ```bash
   cp -r jobme/skill "$KOKUA_HOME/data/skills/job-application"
   ```

   `kokua skills install` only reads Kokua's own bundled skills, so this one is copied by hand.
   `check_application_setup` reports whether it is in place.

4. Put `cv.md` and `resume.html` in the input directory (plus any `cover_letter*.txt` samples and
   a `guidance.md`), then ask the assistant to check the setup.

The assistant's model and jobme's model are separate settings. `[jobme] model` is what tailors the
documents; leaving it empty uses `JOBME_MODEL` or jobme's own default.
```

- [ ] **Step 4: Add the rule to `CLAUDE.md`**

Add to the "Conventions & gotchas" list in `CLAUDE.md`:

```markdown
- **`jobme/kokua_toolset.py` is the only Kokua-aware module.** It exports the `TOOLSET` Kokua
  discovers through the `kokua.toolsets` entry point in `pyproject.toml`. jobme does not depend on
  Kokua and must keep importing and running without it, so nothing else in the package may import
  `kokua`. The design is in
  [docs/superpowers/specs/2026-08-28-kokua-integration-design.md](docs/superpowers/specs/2026-08-28-kokua-integration-design.md).
  Two traps it documents: `pdf.py` uses Playwright's **sync** API, so a run has to stay on a worker
  thread with no event loop, and the adapter must not copy the CLI's `.env` walking, which is
  cwd-dependent.
- **There is now a test suite**, mock-only: `uv run pytest`. It covers the pipeline's progress,
  warnings, and cancellation plumbing and the whole Kokua adapter, with every model call stubbed.
  The pipeline itself is still verified by running it end to end.
```

Also update the "What this is" and "Commands" sections: the line "There is **no automated test suite**" is now false. Replace it with:

```markdown
The test suite is mock-only (`uv run pytest`): no model, no network, no keys. It covers the
callback, warning, and cancellation plumbing and the Kokua adapter, not the pipeline's output.
Verify a pipeline change by running it end-to-end.
```

- [ ] **Step 5: Check for em dashes in everything you wrote**

Run: `grep -rn "—\|–" README.md CLAUDE.md jobme/skill/SKILL.md jobme/kokua_toolset.py jobme/pipeline.py`
Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add jobme/skill/SKILL.md README.md CLAUDE.md
git commit -m "docs: the job-application skill and how to use jobme from Kokua

The skill is the procedure over the toolset's tools: get the posting verbatim,
check the setup before spending, confirm, and relay every warning unsoftened."
```

---

### Task 5: Kokua's how-to (separate repository)

**Files:**
- Create: `../kokua/docs/how-to/install-a-third-party-toolset.md`
- Modify: `../kokua/CHANGELOG.md`

**Interfaces:**
- Consumes: the config keys and tool names from Tasks 2, 3, and 4.
- Produces: nothing code depends on.

- [ ] **Step 1: Confirm the docs layout before writing**

Run: `ls ../kokua/docs/how-to/ && head -20 ../kokua/CHANGELOG.md`
Match the heading style, front matter (if any), and changelog format you find. The instructions below are content, not a license to diverge from the house style.

- [ ] **Step 2: Write the how-to**

Create `../kokua/docs/how-to/install-a-third-party-toolset.md`, at 120 columns, no em dashes, covering:

- What an entry point is and why Kokua needs no change: a package publishing `[project.entry-points."kokua.toolsets"]` is discovered by `kokua.plugins.discover_toolsets` at startup, and the key it registers is the name an agent declares in `[agents.<name>].tools`.
- Installing one: `uv pip install --editable ../jobme` inside Kokua's checkout (leaves
  `pyproject.toml` untouched), or `pip install <package>` once published. Mention `uv add
  --editable` as the alternative for a user who wants it recorded as a dependency of their own
  checkout, and the tradeoff: it edits `pyproject.toml`, so a later `git pull` in Kokua can
  conflict.
- Declaring it: add the name to `[agents.assistant].tools`. A capability is declared, never defaulted, so installing alone grants nothing.
- Its settings: a toolset owns a `[<name>]` section, seeded with the defaults it declares. Show jobme's four keys as the worked example.
- Gating it: add an expensive or irreversible tool to `[security].confirm_tools`, and state the consequence that a gated tool auto-denies in a scheduled proactive turn.
- Confirming it loaded: `uv run kokua` and ask the assistant to list its capabilities, or check the startup warning about a configured section no installed toolset owns.
- A pointer to jobme (https://github.com/saxman/jobme) as a complete worked example, noting that it also ships a skill copied by hand into `$KOKUA_HOME/data/skills` because `kokua skills install` reads only Kokua's own bundled skills.

- [ ] **Step 3: Add the changelog entry**

Add one line to the unreleased section of `../kokua/CHANGELOG.md`, in the existing format, saying that a how-to for installing a third-party toolset was added, with jobme as the worked example.

- [ ] **Step 4: Check the constraints**

Run: `grep -n "—\|–" ../kokua/docs/how-to/install-a-third-party-toolset.md; awk 'length > 120 {print FILENAME": "NR}' ../kokua/docs/how-to/install-a-third-party-toolset.md`
Expected: no output from either.

- [ ] **Step 5: Commit in the Kokua repository**

```bash
cd ../kokua
git checkout -b jobme-toolset-how-to
git add docs/how-to/install-a-third-party-toolset.md CHANGELOG.md
git commit -m "docs(how-to): installing a third-party toolset, with jobme as the example

Kokua's plugin seam had no page of its own: the entry-point contract was
documented only from the inside, in the architecture explanation."
cd ../jobme
```

---

### Task 6: End-to-end verification

**Files:** none. Nothing is committed by this task except the note in Step 6.

**Interfaces:**
- Consumes: everything from Tasks 1 through 5.
- Produces: a verified installation, or a list of defects to fix before the branch merges.

- [ ] **Step 1: Install into Kokua and confirm discovery**

```bash
cd ../kokua
uv pip install --editable ../jobme
uv run python -c "
from kokua.plugins import discover_toolsets
print(sorted(discover_toolsets()))
"
```

Expected: the list includes `jobme`.

- [ ] **Step 2: Configure a local model so the run costs nothing**

In `$KOKUA_HOME/config.toml`, add `"jobme"` to `[agents.assistant].tools`, add `"tailor_application"` to `[security].confirm_tools`, and set `[jobme] model = "ollama:qwen3:8b"` (or any installed Ollama model).

- [ ] **Step 3: Seed the inputs and the skill**

```bash
mkdir -p "$KOKUA_HOME/data/jobme/input"
cp ../jobme/example/input/cv.md ../jobme/example/input/resume.html "$KOKUA_HOME/data/jobme/input/"
cp -r ../jobme/jobme/skill "$KOKUA_HOME/data/skills/job-application"
```

Confirm the example filenames first with `ls ../jobme/example/input/`; copy whatever the synthetic CV and template are actually called.

- [ ] **Step 4: Run it through the web UI**

```bash
uv run kokua --frontend web
```

Paste a job posting and ask the assistant to tailor an application. Confirm each of these, and write down any that fail:

1. The assistant calls `check_application_setup` before its first run.
2. The tool-approval prompt appears for `tailor_application`.
3. Progress lines appear in the conversation *during* the run, not all at the end.
4. The reply carries the page count, the fill, and both `/download/` links.
5. Clicking a link downloads the PDF.
6. `$KOKUA_HOME/data/jobme/output/<timestamp>_<slug>/` holds the full run, summary and trace included.

- [ ] **Step 5: Verify cancellation actually stops the spend**

Start another run and send `/stop` during the resume-tailoring step. Confirm the turn ends immediately, and that within one step boundary the progress lines stop rather than continuing to the end of the pipeline. Watching the Ollama server's log (or the output folder failing to gain a `cover_letter.txt`) is the evidence.

- [ ] **Step 6: Record the result**

If everything passed, add a "Verified" line with the date and the model used to the end of the spec at `docs/superpowers/specs/2026-08-28-kokua-integration-design.md` and commit it. If anything failed, fix it in the task that owns it and re-run this one.

---

## Notes for the executor

- **The `kokua` extra can silently skip.** `tests/test_kokua_toolset.py` opens with `pytest.importorskip("kokua")`, so a missing sibling checkout turns the adapter suite into a green skip. Any step that says "expect PASS" for that file means the tests ran. Check the summary line for skips.
- **`asyncio.to_thread` is not cancellable.** Awaiting it can be cancelled; the thread cannot. This is why the cancel event exists and why `_run_pipeline` absorbs `RunCancelled` inside the thread.
- **Do not move the pipeline onto the event loop.** Playwright's sync API raises when a loop is running in the calling thread.
- **Task 5 commits in a different repository.** Keep the two histories separate; do not add Kokua files to a jobme commit.

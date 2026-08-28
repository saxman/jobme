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


def build(ctx: ToolsetContext) -> list:
    """Both tools, always.

    Unlike ``github_backup``, which offers nothing until its repository is configured, a missing
    ``cv.md`` is exactly what ``check_application_setup`` exists to report. Hiding the toolset when
    inputs are absent would remove the thing that explains the absence.
    """
    config = ctx.config

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

    return [tailor_application, check_application_setup]


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

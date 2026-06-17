"""Multi-step agentic pipeline: tailor -> review -> render -> PDF.

Built on AIMU's ``EvaluatorOptimizer`` (generate -> evaluate -> revise until the
reviewer emits ``PASS``) for both the resume and the cover letter, sharing the same
accuracy (no fabrication) and intrigue bar.
"""

from __future__ import annotations

import json
from pathlib import Path

import aimu
from aimu.agents import EvaluatorOptimizer

from . import prompts, render
from .config import (
    Config,
    MAX_PAGE_FIT_RETRIES,
    MAX_REVIEW_ROUNDS,
    RESUME_FILL_TARGET,
    TARGET_RESUME_PAGES,
    TYPOGRAPHY_MAX_STRETCH,
)
from .io_utils import Inputs, load_inputs, make_output_dir, slugify
from .pdf import check_backend, html_to_pdf, page_count, page_fill


# --- Steps ---------------------------------------------------------------------


def _job_slug(model: str, job_description: str, name: str | None) -> str:
    if name:
        return slugify(name)
    label = aimu.chat(
        prompts.SLUG_TASK.format(job_description=job_description),
        model=model,
        system=prompts.SLUG_SYSTEM,
    )
    return slugify(label)


def _tailor_resume(model: str, inputs: Inputs) -> tuple[str, EvaluatorOptimizer]:
    """Tailor resume content to the JD, reviewed for accuracy and intrigue."""
    loop = EvaluatorOptimizer(
        generator=aimu.agent(model, system=prompts.RESUME_GENERATOR_SYSTEM, name="resume-writer"),
        evaluator=aimu.agent(model, system=prompts.RESUME_EVALUATOR_SYSTEM, name="resume-reviewer"),
        max_rounds=MAX_REVIEW_ROUNDS,
        pass_keyword="PASS",
    )
    task = prompts.RESUME_GENERATOR_TASK.format(
        cv=inputs.cv_markdown, job_description=inputs.job_description
    )
    return loop.run(task), loop


def _render_resume(
    model: str,
    inputs: Inputs,
    content: str,
    out_dir: Path,
    pdf_backend: str,
    resume_loop: EvaluatorOptimizer,
) -> tuple[Path, Path, int, float | None]:
    """Render content to HTML, then fit it close to (but never over) two pages.

    Each round picks one action: condense if over the hard page limit; else, if
    underfilled, add genuine CV content once for a large shortfall (the renderer has no
    CV, so this re-engages the accuracy-reviewed content generator) or stretch typography
    for a small one. Typography only ever closes a small gap -- a large shortfall that
    content can't fill means the CV is genuinely thin, so we accept a shorter resume
    rather than inflate the type.

    The <=TARGET_RESUME_PAGES guarantee holds by construction: only renders that fit are
    eligible to be emitted (best-fill-so-far), so an expansion that overshoots is simply
    discarded. Degrades to condense-only when fill can't be measured (no Chromium).
    """
    client = aimu.client(model, system=prompts.RESUME_HTML_SYSTEM)
    content_path = out_dir / "resume_content.md"
    html_path = out_dir / "resume.html"
    pdf_path = out_dir / "resume.pdf"

    def rerender(html: str) -> tuple[int, float | None]:
        html_path.write_text(html, encoding="utf-8")
        html_to_pdf(html_path, pdf_path, backend=pdf_backend)
        return page_count(pdf_path), page_fill(html_path)

    html = render.render_resume_html(client, inputs.resume_html, content)
    pages, fill = rerender(html)
    disk_html = html  # tracks which render currently backs html_path/pdf_path

    # Best version that fits the page limit, with the content it was rendered from.
    best = (html, content, pages, fill) if pages <= TARGET_RESUME_PAGES else None

    condensed = False
    content_expanded = False
    for _ in range(MAX_PAGE_FIT_RETRIES):
        if pages > TARGET_RESUME_PAGES:
            print(f"[jobme]   resume is {pages} pages; condensing to {TARGET_RESUME_PAGES}...")
            html = render.condense_resume_html(client, pages, TARGET_RESUME_PAGES)
            condensed = True
        elif condensed or fill is None or fill >= RESUME_FILL_TARGET:
            break  # condensed (don't bounce back over), unmeasurable, or full enough
        elif RESUME_FILL_TARGET - fill > TYPOGRAPHY_MAX_STRETCH:
            if content_expanded:
                break  # CV content is exhausted; too short for type to close tastefully
            print(f"[jobme]   resume fills ~{fill:.2f} pages; adding CV detail...")
            content = resume_loop.generator.run(
                prompts.RESUME_EXPAND_CONTENT_TASK.format(fill=fill, target=TARGET_RESUME_PAGES)
            )
            html = render.render_resume_html(client, inputs.resume_html, content)
            content_expanded = True
        else:
            print(f"[jobme]   resume fills ~{fill:.2f} pages; stretching layout...")
            html = render.expand_resume_typography(client, fill, TARGET_RESUME_PAGES)

        pages, fill = rerender(html)
        disk_html = html
        if pages <= TARGET_RESUME_PAGES and (best is None or (fill or 0) > (best[3] or 0)):
            best = (html, content, pages, fill)

    # Emit the best fitting version; the latest render may be an overshoot we discard.
    # If no render ever fit (couldn't condense within budget), keep the last attempt.
    if best is not None:
        html, content, pages, fill = best
        if html is not disk_html:
            html_path.write_text(html, encoding="utf-8")
            html_to_pdf(html_path, pdf_path, backend=pdf_backend)
    content_path.write_text(content, encoding="utf-8")

    return html_path, pdf_path, pages, fill


def _tailor_cover(model: str, inputs: Inputs) -> tuple[str, EvaluatorOptimizer]:
    """Write a cover letter in the candidate's voice, reviewed like the resume."""
    if inputs.cover_letter_samples:
        joined = "\n\n---\n\n".join(inputs.cover_letter_samples)
        samples_block = prompts.COVER_SAMPLES_BLOCK.format(samples=joined)
        voice_clause = ", matching the candidate's writing style from the samples"
    else:
        samples_block = ""
        voice_clause = ""

    loop = EvaluatorOptimizer(
        generator=aimu.agent(model, system=prompts.COVER_GENERATOR_SYSTEM, name="cover-writer"),
        evaluator=aimu.agent(model, system=prompts.COVER_EVALUATOR_SYSTEM, name="cover-reviewer"),
        max_rounds=MAX_REVIEW_ROUNDS,
        pass_keyword="PASS",
    )
    task = prompts.COVER_GENERATOR_TASK.format(
        cv=inputs.cv_markdown,
        job_description=inputs.job_description,
        voice_clause=voice_clause,
        samples_block=samples_block,
    )
    return loop.run(task), loop


def _render_cover(
    model: str, inputs: Inputs, content: str, out_dir: Path, pdf_backend: str
) -> tuple[Path, Path]:
    client = aimu.client(model, system=prompts.COVER_HTML_SYSTEM)
    html_path = out_dir / "cover_letter.html"
    pdf_path = out_dir / "cover_letter.pdf"
    html = render.render_cover_html(client, inputs.resume_html, content)
    html_path.write_text(html, encoding="utf-8")
    html_to_pdf(html_path, pdf_path, backend=pdf_backend)
    return html_path, pdf_path


# --- Summary / trace -----------------------------------------------------------


def _format_trace(messages: dict) -> str:
    """Render an EvaluatorOptimizer/Agent message history (dict by agent name) as text."""
    out: list[str] = []
    for agent_name, turns in messages.items():
        out.append(f"\n#### Agent: {agent_name}")
        for msg in turns:
            role = msg.get("role", "?")
            content = msg.get("content", "")
            if not isinstance(content, str):
                content = json.dumps(content, default=str)
            out.append(f"\n**{role}:**\n\n{content}")
    return "\n".join(out)


def _write_summary(
    out_dir: Path,
    config: Config,
    slug: str,
    pages: int,
    fill: float | None,
    artifacts: list[Path],
    resume_loop: EvaluatorOptimizer,
    cover_loop: EvaluatorOptimizer,
) -> Path:
    trace = {"resume": resume_loop.messages, "cover_letter": cover_loop.messages}
    (out_dir / "trace.json").write_text(
        json.dumps(trace, indent=2, default=str), encoding="utf-8"
    )

    fit = "OK" if pages <= TARGET_RESUME_PAGES else f"over by {pages - TARGET_RESUME_PAGES}"
    fill_note = f", filling ~{fill:.2f}" if fill is not None else ""
    files = "\n".join(f"- `{p.name}`" for p in artifacts)
    body = (
        f"# jobme run summary: {slug}\n\n"
        f"- **Model:** `{config.model}`\n"
        f"- **PDF backend:** `{config.pdf_backend}`\n"
        f"- **Resume pages:** {pages} (target {TARGET_RESUME_PAGES} -- {fit}{fill_note})\n\n"
        f"## Files produced\n{files}\n"
        f"- `resume_content.md`, `cover_letter.txt` (approved text)\n"
        f"- `trace.json` (machine-readable agent trace)\n\n"
        f"## Agent reasoning trace -- Resume\n{_format_trace(resume_loop.messages)}\n\n"
        f"## Agent reasoning trace -- Cover letter\n{_format_trace(cover_loop.messages)}\n"
    )
    summary_path = out_dir / "summary.md"
    summary_path.write_text(body, encoding="utf-8")
    return summary_path


# --- Entry point ---------------------------------------------------------------


def run(config: Config) -> dict:
    """Run the full pipeline for one job posting; returns paths to produced files."""
    inputs = load_inputs(config.input_dir, config.jd_path)
    check_backend(config.pdf_backend)  # fail fast before any LLM calls
    slug = _job_slug(config.model, inputs.job_description, config.name)
    out_dir = make_output_dir(config.output_dir, slug)

    print(f"[jobme] Job: {slug}")
    print(f"[jobme] Model: {config.model} | PDF backend: {config.pdf_backend}")

    print("[jobme] Tailoring resume (accuracy & intrigue review)...")
    resume_content, resume_loop = _tailor_resume(config.model, inputs)
    (out_dir / "resume_content.md").write_text(resume_content, encoding="utf-8")

    print("[jobme] Rendering resume HTML and fitting to 2 pages...")
    resume_html, resume_pdf, pages, fill = _render_resume(
        config.model, inputs, resume_content, out_dir, config.pdf_backend, resume_loop
    )

    print("[jobme] Writing cover letter (accuracy & intrigue review)...")
    cover_content, cover_loop = _tailor_cover(config.model, inputs)
    (out_dir / "cover_letter.txt").write_text(cover_content, encoding="utf-8")

    print("[jobme] Rendering cover letter HTML and PDF...")
    cover_html, cover_pdf = _render_cover(
        config.model, inputs, cover_content, out_dir, config.pdf_backend
    )

    artifacts = [resume_html, resume_pdf, cover_html, cover_pdf]
    summary_path = _write_summary(
        out_dir, config, slug, pages, fill, artifacts, resume_loop, cover_loop
    )

    print(f"\n[jobme] Done. Output in {out_dir}")
    for path in [*artifacts, summary_path]:
        print(f"  - {path}")

    return {
        "output_dir": out_dir,
        "resume_html": resume_html,
        "resume_pdf": resume_pdf,
        "cover_html": cover_html,
        "cover_pdf": cover_pdf,
        "resume_pages": pages,
        "resume_fill": fill,
        "summary": summary_path,
    }

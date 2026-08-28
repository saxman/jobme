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


def test_run_stops_mid_run_and_never_reaches_the_later_steps(monkeypatch, tmp_path):
    """Setting the event before the first checkpoint (above) only proves the cheapest one works,
    before anything has been spent. The checkpoint that matters is the one guarding calls after
    money has already been spent, so set the event from inside a stubbed step and confirm both
    that RunCancelled propagates and that no later step ran."""
    inputs = Inputs(cv_markdown="cv", resume_html="<html></html>", job_description="jd")
    cancel = threading.Event()
    called: list[str] = []

    monkeypatch.setattr(pipeline, "load_inputs", lambda input_dir, jd_path: inputs)
    monkeypatch.setattr(pipeline, "check_backend", lambda backend: None)
    monkeypatch.setattr(pipeline, "_job_slug", lambda model, job_description, name: "acme-engineer")

    def tailor_resume(model, inputs):
        called.append("_tailor_resume")
        cancel.set()  # mimics a /stop landing while this step was in flight
        return "resume content", object()

    monkeypatch.setattr(pipeline, "_tailor_resume", tailor_resume)

    def render_resume(*args, **kwargs):
        called.append("_render_resume")
        return tmp_path / "resume.html", tmp_path / "resume.pdf", 2, 1.28, []

    monkeypatch.setattr(pipeline, "_render_resume", render_resume)

    def tailor_cover(model, inputs):
        called.append("_tailor_cover")
        return "cover content", object()

    monkeypatch.setattr(pipeline, "_tailor_cover", tailor_cover)

    def render_cover(*args, **kwargs):
        called.append("_render_cover")
        return tmp_path / "cover_letter.html", tmp_path / "cover_letter.pdf"

    monkeypatch.setattr(pipeline, "_render_cover", render_cover)

    def write_summary(*args):
        called.append("_write_summary")
        return tmp_path / "summary.md"

    monkeypatch.setattr(pipeline, "_write_summary", write_summary)

    with pytest.raises(pipeline.RunCancelled):
        pipeline.run(_config(tmp_path), progress=lambda line: None, cancel=cancel)

    assert called == ["_tailor_resume"]


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


def test_with_retry_checks_cancel_before_sleeping_out_the_backoff(monkeypatch):
    """A cancelled run must not sleep out a multi-second backoff and then pay for the retry
    anyway; the event has to be checked before the sleep, not just before the next attempt."""
    monkeypatch.setattr(pipeline.time, "sleep", lambda seconds: None)
    cancel = threading.Event()

    def always_flaky() -> str:
        cancel.set()  # mimics a /stop landing while the transient error was being handled
        raise ConnectionError("reset by peer")

    with pytest.raises(pipeline.RunCancelled):
        pipeline._with_retry("tailoring resume", always_flaky, lambda line: None, cancel)

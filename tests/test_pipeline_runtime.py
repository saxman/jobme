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

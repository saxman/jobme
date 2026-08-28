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


def test_the_setup_check_is_offered_even_with_nothing_set_up(tmp_path):
    assert "check_application_setup" in _tools(_config(tmp_path))


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


def test_both_tools_are_offered_even_with_nothing_set_up(tmp_path):
    assert set(_tools(_config(tmp_path))) == {"tailor_application", "check_application_setup"}


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

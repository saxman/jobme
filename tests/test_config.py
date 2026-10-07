"""Model resolution: explicit value -> JOBME_MODEL -> default, and which one won."""

from __future__ import annotations

from jobme.config import DEFAULT_MODEL, ModelSource, resolve_model


def test_an_explicit_model_wins_over_the_environment(monkeypatch):
    monkeypatch.setenv("JOBME_MODEL", "ollama:from-env")

    assert resolve_model("ollama:explicit") == ("ollama:explicit", ModelSource.EXPLICIT)


def test_jobme_model_wins_over_the_default(monkeypatch):
    monkeypatch.setenv("JOBME_MODEL", "ollama:from-env")

    assert resolve_model(None) == ("ollama:from-env", ModelSource.ENVIRONMENT)


def test_the_default_applies_when_nothing_is_set(monkeypatch):
    monkeypatch.delenv("JOBME_MODEL", raising=False)

    assert resolve_model(None) == (DEFAULT_MODEL, ModelSource.DEFAULT)


def test_an_empty_jobme_model_counts_as_unset(monkeypatch):
    monkeypatch.setenv("JOBME_MODEL", "")

    assert resolve_model(None) == (DEFAULT_MODEL, ModelSource.DEFAULT)

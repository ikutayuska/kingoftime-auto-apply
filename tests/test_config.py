import importlib
import sys
import pytest


def import_app(monkeypatch):
    sys.modules.pop("kot_auto_apply", None)
    return importlib.import_module("kot_auto_apply")


def test_required_username_and_password(monkeypatch):
    monkeypatch.delenv("KOT_USERNAME", raising=False)
    monkeypatch.delenv("KOT_PASSWORD", raising=False)
    monkeypatch.setenv("KOT_OFFICE_KEYWORDS", "東京オフィス")

    with pytest.raises(SystemExit):
        import_app(monkeypatch)


def test_requires_at_least_one_location_keyword(monkeypatch):
    monkeypatch.setenv("KOT_USERNAME", "dummy_user")
    monkeypatch.setenv("KOT_PASSWORD", "dummy_password")
    monkeypatch.delenv("KOT_OFFICE_KEYWORDS", raising=False)
    monkeypatch.delenv("KOT_REMOTE_KEYWORDS", raising=False)

    with pytest.raises(SystemExit):
        import_app(monkeypatch)


def test_load_keywords_from_env(monkeypatch):
    monkeypatch.setenv("KOT_USERNAME", "dummy_user")
    monkeypatch.setenv("KOT_PASSWORD", "dummy_password")
    monkeypatch.setenv("KOT_OFFICE_KEYWORDS", "東京オフィス, 本社 ")
    monkeypatch.setenv("KOT_REMOTE_KEYWORDS", "在宅, リモート ")

    app = import_app(monkeypatch)

    assert app.OFFICE_ADDRESSES == ["東京オフィス", "本社"]
    assert app.REMOTE_KEYWORDS == ["在宅", "リモート"]


def test_headless_true(monkeypatch):
    monkeypatch.setenv("KOT_USERNAME", "dummy_user")
    monkeypatch.setenv("KOT_PASSWORD", "dummy_password")
    monkeypatch.setenv("KOT_OFFICE_KEYWORDS", "東京オフィス")
    monkeypatch.setenv("KOT_HEADLESS", "true")

    app = import_app(monkeypatch)

    assert app.HEADLESS is True
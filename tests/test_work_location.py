import importlib
import sys


def load_app(monkeypatch):
    monkeypatch.setenv("KOT_USERNAME", "dummy_user")
    monkeypatch.setenv("KOT_PASSWORD", "dummy_password")
    monkeypatch.setenv("KOT_OFFICE_KEYWORDS", "東京オフィス,本社")
    monkeypatch.setenv("KOT_REMOTE_KEYWORDS", "在宅,リモート")

    sys.modules.pop("kot_auto_apply", None)
    return importlib.import_module("kot_auto_apply")


def test_determine_work_location_office(monkeypatch):
    app = load_app(monkeypatch)

    row_text = "05/20（水） 東京オフィス 勤務"
    assert app.determine_work_location(row_text) == "出社"


def test_determine_work_location_remote(monkeypatch):
    app = load_app(monkeypatch)

    row_text = "05/20（水） 在宅勤務"
    assert app.determine_work_location(row_text) == "在宅"


def test_determine_work_location_remote_has_priority(monkeypatch):
    app = load_app(monkeypatch)

    row_text = "05/20（水） 東京オフィス 在宅"
    assert app.determine_work_location(row_text) == "在宅"


def test_determine_work_location_unknown(monkeypatch):
    app = load_app(monkeypatch)

    row_text = "05/20（水） 通常勤務"
    assert app.determine_work_location(row_text) == "不明"


def test_determine_work_location_empty_text(monkeypatch):
    app = load_app(monkeypatch)

    assert app.determine_work_location("") == "不明"
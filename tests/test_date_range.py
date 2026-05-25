import importlib
import sys
from datetime import date


def load_app(monkeypatch):
    monkeypatch.setenv("KOT_USERNAME", "dummy_user")
    monkeypatch.setenv("KOT_PASSWORD", "dummy_password")
    monkeypatch.setenv("KOT_OFFICE_KEYWORDS", "東京オフィス")
    monkeypatch.setenv("KOT_REMOTE_KEYWORDS", "在宅")
    monkeypatch.setenv("KOT_TIMEZONE", "Asia/Tokyo")

    sys.modules.pop("kot_auto_apply", None)
    return importlib.import_module("kot_auto_apply")


def test_extract_date_success(monkeypatch):
    app = load_app(monkeypatch)

    text = "05/20（水） 在宅勤務"
    assert app.extract_date(text) == "05/20(水)"


def test_extract_date_not_found(monkeypatch):
    app = load_app(monkeypatch)

    text = "日付なし 在宅勤務"
    assert app.extract_date(text) is None


def test_get_current_week_weekdays(monkeypatch):
    app = load_app(monkeypatch)

    class FixedDateTime:
        @classmethod
        def now(cls, tz=None):
            class FixedDate:
                def date(self):
                    return date(2026, 5, 20)  # 水曜日

            return FixedDate()

    monkeypatch.setattr(app, "datetime", FixedDateTime)

    assert app.get_current_week_weekdays() == [
        "05/18",
        "05/19",
        "05/20",
        "05/21",
        "05/22",
    ]
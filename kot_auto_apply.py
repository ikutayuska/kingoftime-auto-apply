import os
import re
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright

load_dotenv()

USERNAME = os.getenv("KOT_USERNAME")
PASSWORD = os.getenv("KOT_PASSWORD")
URL = os.getenv("KOT_URL", "https://login.ta.kingoftime.jp/admin")
TIMEZONE = os.getenv("KOT_TIMEZONE", "Asia/Tokyo")
HEADLESS = os.getenv("KOT_HEADLESS", "false").lower() == "true"
BROWSER_CHANNEL = os.getenv("KOT_BROWSER_CHANNEL")

OFFICE_ADDRESSES = [
    x.strip() for x in os.getenv("KOT_OFFICE_KEYWORDS", "").split(",") if x.strip()
]
REMOTE_KEYWORDS = [
    x.strip() for x in os.getenv("KOT_REMOTE_KEYWORDS", "").split(",") if x.strip()
]

TRANSIT_REMARK = os.getenv("KOT_TRANSIT_REMARK", "出社により交通費申請")
REMOTE_REMARK = os.getenv(
    "KOT_REMOTE_REMARK", "在宅勤務によるスマートワーキング手当申請"
)

if not USERNAME or not PASSWORD:
    raise SystemExit("Please set KOT_USERNAME and KOT_PASSWORD environment variables.")

if not OFFICE_ADDRESSES and not REMOTE_KEYWORDS:
    raise SystemExit(
        "Please set KOT_OFFICE_KEYWORDS and/or KOT_REMOTE_KEYWORDS in environment variables."
    )


def get_current_week_weekdays() -> list[str]:
    """Return this week's weekdays (Mon-Fri) in MM/DD format."""
    today = datetime.now(ZoneInfo(TIMEZONE)).date()
    current_monday = today - timedelta(days=today.weekday())
    return [(current_monday + timedelta(days=i)).strftime("%m/%d") for i in range(5)]


def determine_work_location(row_text: str) -> str:
    """Determine work location from a row text."""
    for kw in REMOTE_KEYWORDS:
        if kw in row_text:
            return "在宅"

    for office in OFFICE_ADDRESSES:
        if office in row_text:
            return "出社"

    if "位置" not in row_text:
        return "不明"

    return "不明"


def login(page) -> None:
    """Login to KING OF TIME."""
    page.goto(URL, wait_until="domcontentloaded")
    page.get_by_role("textbox", name="ID").fill(USERNAME)
    page.get_by_role("textbox", name="パスワード").fill(PASSWORD)
    page.get_by_role("button", name="ログイン").click()
    page.wait_for_load_state("networkidle")
    time.sleep(1.5)
    print("ログイン完了")


def extract_date(text: str) -> str | None:
    """Extract the first date in MM/DD(曜) format from attendance row text."""
    pattern = r"(\d{2}/\d{2})（([月火水木金土日])）"
    match = re.search(pattern, text)
    if not match:
        return None
    month_day, weekday = match.groups()
    return f"{month_day}({weekday})"


def register_trans_expense(row, page) -> None:
    """Apply commuting expense when office work is detected."""
    combo = row.get_by_role("combobox")
    if combo.count() > 0:
        combo.select_option(label="スケジュール申請")
        print("スケジュール申請を選択（通勤費）")
    time.sleep(0.5)

    page.locator("label").filter(has_text="日割り通勤費").click()
    page.locator("#remark").fill(TRANSIT_REMARK)
    page.get_by_role("button", name="スケジュール申請").nth(1).click()
    print("通勤費申請完了")
    time.sleep(0.5)


def register_remote_allowance(row, page) -> None:
    """Apply remote allowance when remote work is detected."""
    combo = row.get_by_role("combobox")
    if combo.count() > 0:
        combo.select_option(label="スケジュール申請")
        print("補助項目申請を選択（スマートワーキング手当）")
    time.sleep(0.5)

    page.locator("label").filter(has_text="スマートワーキング手").click()
    page.locator("#remark").fill(REMOTE_REMARK)
    page.get_by_role("button", name="スケジュール申請").nth(1).click()
    print("スマートワーキング手当申請完了")
    time.sleep(0.5)


def run(playwright: Playwright) -> None:
    launch_kwargs = {"headless": HEADLESS}
    if BROWSER_CHANNEL:
        launch_kwargs["channel"] = BROWSER_CHANNEL

    browser = playwright.chromium.launch(**launch_kwargs)
    context = browser.new_context()
    page = context.new_page()

    login(page)

    rows = page.get_by_role("row").all()
    print(f"行数: {len(rows)}")

    target_dates = get_current_week_weekdays()
    print(f"対象日付（今週平日）: {target_dates}")

    for row in rows[3:]:
        row_text = row.inner_text()
        date = extract_date(row_text)
        if not date:
            print("日付取得失敗、スキップ。")
            continue

        if date[:5] not in target_dates:
            continue

        location = determine_work_location(row_text)
        print(f"{date} | 勤務場所: {location}")

        if location == "出社":
            register_trans_expense(row, page)
        elif location == "在宅":
            register_remote_allowance(row, page)
        else:
            print("出社・在宅不明のためスキップ。")

    context.close()
    browser.close()
    print("全処理完了")


def main() -> None:
    with sync_playwright() as playwright:
        run(playwright)


if __name__ == "__main__":
    main()

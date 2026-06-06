
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, Error as PlaywrightError

PORTAL_URL = "https://springzabdesk.szabist-isb.edu.pk/"
BASE_URL = "https://springzabdesk.szabist-isb.edu.pk"

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
CAPTURE_DIR = RAW_DIR / "portal_captures"
TEXT_DUMPS_DIR = RAW_DIR / "text_dumps"
SYNC_LOG_PATH = TEXT_DUMPS_DIR / "sync_log.txt"

CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
TEXT_DUMPS_DIR.mkdir(parents=True, exist_ok=True)


def reset_previous_run():
    for folder in [CAPTURE_DIR, TEXT_DUMPS_DIR]:
        for item in folder.iterdir():
            if item.is_file():
                item.unlink()


def log(message):
    print(message)
    with open(SYNC_LOG_PATH, "a", encoding="utf-8") as file:
        file.write(message + "\n")


def clean_filename(text):
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    return text.strip("_").lower()


def extract_visible_text(page):
    try:
        return page.locator("body").inner_text(timeout=5000)
    except Exception:
        return ""


def save_page_artifacts(page, filename_prefix):
    html_path = CAPTURE_DIR / f"{filename_prefix}.html"
    txt_path = TEXT_DUMPS_DIR / f"{filename_prefix}.txt"

    html_path.write_text(page.content(), encoding="utf-8")
    raw_text = extract_visible_text(page)
    txt_path.write_text(raw_text, encoding="utf-8")

    log(f"Saved {html_path.name}")
    log(f"Saved {txt_path.name}")


def get_link_href(page, text_value):
    locator = page.locator("a", has_text=text_value).first
    href = locator.get_attribute("href")

    if not href:
        raise ValueError(f"Could not find href for: {text_value}")

    if href.startswith("/"):
        href = BASE_URL + href

    return href


def get_course_links(page):
    course_names = []
    links = page.locator("a").all()

    for link in links:
        text = link.inner_text().strip()
        href = link.get_attribute("href")

        if href and "chkSubmit" in href and text and text not in course_names:
            course_names.append(text)

    return course_names


def wait_for_login(page):
    log("============================================================")
    log("GradeScope Portal Sync")
    log("Login manually in the opened ZABDesk browser.")
    log("Sync starts immediately after login is detected.")
    log("Do not close the browser while sync is running.")
    log("============================================================")

    try:
        page.wait_for_function(
            """
            () => {
                const links = Array.from(document.querySelectorAll("a"));
                const hasAttendance = links.some(a => a.innerText.includes("View Attendance"));
                const hasResults = links.some(a => a.innerText.includes("Current Semester Results"));
                return hasAttendance && hasResults;
            }
            """,
            timeout=180000
        )
        log("Login detected.")
        log("Starting portal capture...")
    except PlaywrightError:
        raise RuntimeError(
            "Login was not detected. Make sure you logged in successfully and did not close the browser."
        )


def open_course_detail(page, course_name):
    course_link = page.locator("a", has_text=course_name).first
    course_link.click()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(700)


def capture_course_details(page, main_url, page_type):
    log(f"Opening {page_type} main page...")
    page.goto(main_url, wait_until="domcontentloaded")
    page.wait_for_timeout(900)

    save_page_artifacts(page, f"{page_type}_main_page")

    courses = get_course_links(page)
    log(f"Found {len(courses)} courses on {page_type} page.")

    for index, course_name in enumerate(courses, start=1):
        safe_name = clean_filename(course_name)
        log(f"{page_type.upper()} {index}/{len(courses)} -> {course_name}")

        page.goto(main_url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        open_course_detail(page, course_name)
        save_page_artifacts(page, f"{page_type}_{index}_{safe_name}")

    log(f"{page_type.capitalize()} capture complete.")


def run_scraper():
    reset_previous_run()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1440, "height": 940})

        log("Opening ZABDesk portal...")
        page.goto(PORTAL_URL, wait_until="domcontentloaded")

        wait_for_login(page)

        save_page_artifacts(page, "logged_in_homepage")

        attendance_url = get_link_href(page, "View Attendance")
        results_url = get_link_href(page, "Current Semester Results")

        log("Attendance URL detected.")
        log("Results URL detected.")

        capture_course_details(page, attendance_url, "attendance")
        capture_course_details(page, results_url, "results")

        browser.close()
        log("Portal sync finished successfully.")


if __name__ == "__main__":
    run_scraper()

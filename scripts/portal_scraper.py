import re
from pathlib import Path
from playwright.sync_api import sync_playwright, Error as PlaywrightError
import os
os.system("playwright install chromium")

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
        folder.mkdir(parents=True, exist_ok=True)
        for item in folder.iterdir():
            if item.is_file():
                item.unlink()


def log(message):
    print(message)
    with open(SYNC_LOG_PATH, "a", encoding="utf-8") as file:
        file.write(message + "\n")


def clean_filename(text):
    text = re.sub(r"[^a-zA-Z0-9]+", "_", str(text))
    return text.strip("_").lower()


def absolute_url(href):
    if not href:
        return None

    if href.startswith("http"):
        return href

    if href.startswith("/"):
        return BASE_URL + href

    return BASE_URL + "/" + href


def extract_visible_text(page):
    try:
        return page.locator("body").inner_text(timeout=5000)
    except Exception:
        return ""


def save_page_artifacts(page, filename_prefix):
    html_path = CAPTURE_DIR / f"{filename_prefix}.html"
    txt_path = TEXT_DUMPS_DIR / f"{filename_prefix}.txt"

    html_path.write_text(page.content(), encoding="utf-8")
    txt_path.write_text(extract_visible_text(page), encoding="utf-8")

    log(f"Saved {html_path.name}")
    log(f"Saved {txt_path.name}")


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
                const hasCurrentResults = links.some(a => a.innerText.includes("Current Semester Results"));
                const hasPreviousResults = links.some(a => a.innerText.includes("Previous Semesters Result"));
                return hasAttendance && hasCurrentResults && hasPreviousResults;
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


def get_link_href(page, text_value):
    locator = page.locator("a", has_text=text_value).first
    href = locator.get_attribute("href")

    if not href:
        raise ValueError(f"Could not find href for: {text_value}")

    return absolute_url(href)


def get_course_links(page):
    course_names = []
    links = page.locator("a").all()

    for link in links:
        text = link.inner_text().strip()
        href = link.get_attribute("href")

        if href and "chkSubmit" in href and text and text not in course_names:
            course_names.append(text)

    return course_names


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


def get_select_options(page):
    select = page.locator("select").first
    options = select.locator("option").all()

    semester_options = []

    for option in options:
        label = option.inner_text().strip()
        value = option.get_attribute("value")

        if label and "select" not in label.lower():
            semester_options.append(
                {
                    "label": label,
                    "value": value if value else label,
                }
            )

    return semester_options


def submit_previous_semester_form(page):
    submit_candidates = [
        "input[type='submit']",
        "button[type='submit']",
        "input[value='Submit']",
        "input[value='submit']",
        "button:has-text('Submit')",
    ]

    for selector in submit_candidates:
        locator = page.locator(selector)
        if locator.count() > 0:
            locator.first.click()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(900)
            return

    page.keyboard.press("Enter")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(900)


def capture_previous_semester_results(page, previous_url):
    log("Opening previous semester results page...")

    page.goto(previous_url, wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    save_page_artifacts(page, "previous_semester_selector_page")

    options = get_select_options(page)
    log(f"Found {len(options)} previous semester options.")

    if not options:
        log("No previous semester dropdown options found.")
        return

    for index, option in enumerate(options, start=1):
        semester_label = option["label"]
        semester_value = option["value"]
        safe_semester = clean_filename(semester_label)

        log(f"PREVIOUS GPA {index}/{len(options)} -> {semester_label}")

        page.goto(previous_url, wait_until="domcontentloaded")
        page.wait_for_timeout(700)

        select = page.locator("select").first

        try:
            select.select_option(label=semester_label)
        except Exception:
            select.select_option(value=semester_value)

        page.wait_for_timeout(300)
        submit_previous_semester_form(page)

        save_page_artifacts(page, f"previous_semester_result_{index}_{safe_semester}")

    log("Previous semester GPA capture complete.")


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
        current_results_url = get_link_href(page, "Current Semester Results")
        previous_results_url = get_link_href(page, "Previous Semesters Result")

        log("Attendance URL detected.")
        log("Current semester results URL detected.")
        log("Previous semester results URL detected.")

        capture_course_details(page, attendance_url, "attendance")
        capture_course_details(page, current_results_url, "results")
        capture_previous_semester_results(page, previous_results_url)

        browser.close()
        log("Portal sync finished successfully.")


if __name__ == "__main__":
    run_scraper()

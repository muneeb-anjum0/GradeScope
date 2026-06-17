
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

PORTAL_URL = "https://springzabdesk.szabist-isb.edu.pk/"
BASE_URL = "https://springzabdesk.szabist-isb.edu.pk"

OUTPUT_DIR = Path("portal_captures")
OUTPUT_DIR.mkdir(exist_ok=True)


def save_page(page, filename_prefix):
    html_path = OUTPUT_DIR / f"{filename_prefix}.html"
    png_path = OUTPUT_DIR / f"{filename_prefix}.png"

    with open(html_path, "w", encoding="utf-8") as file:
        file.write(page.content())

    page.screenshot(path=str(png_path), full_page=True)

    print(f"Saved {html_path}")
    print(f"Saved {png_path}")


def clean_filename(text):
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    return text.strip("_").lower()


def get_link_href(page, text_value):
    locator = page.locator(f"a:has-text('{text_value}')").first
    href = locator.get_attribute("href")

    if not href:
        raise ValueError(f"Could not find href for: {text_value}")

    if href.startswith("/"):
        href = BASE_URL + href

    return href


def get_course_links(page):
    courses = []

    links = page.locator("a").all()

    for link in links:
        text = link.inner_text().strip()
        href = link.get_attribute("href")

        if href and "chkSubmit" in href:
            courses.append({
                "course_name": text,
                "href": href
            })

    return courses


def capture_course_details(page, main_url, page_type):
    print(f"\nOpening {page_type} main page...")
    page.goto(main_url)
    time.sleep(5)

    save_page(page, f"{page_type}_main_page")

    courses = get_course_links(page)
    print(f"Found {len(courses)} courses on {page_type} page.")

    for index, course in enumerate(courses, start=1):
        course_name = course["course_name"]
        safe_name = clean_filename(course_name)

        print(f"\n{page_type.upper()} {index}: {course_name}")

        page.goto(main_url)
        time.sleep(2)

        course_locator = page.locator(f"a:has-text('{course_name}')").first
        course_locator.click()

        time.sleep(5)

        save_page(page, f"{page_type}_{index}_{safe_name}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        page.goto(PORTAL_URL)
        print("Portal opened.")

        print("\nLOGIN MANUALLY.")
        print("After login, wait. Do not close the browser.")
        print("You have 60 seconds.\n")
        time.sleep(60)

        save_page(page, "logged_in_homepage")

        attendance_url = get_link_href(page, "View Attendance")
        results_url = get_link_href(page, "Current Semester Results")

        print("\nAttendance URL:", attendance_url)
        print("Results URL:", results_url)

        capture_course_details(page, attendance_url, "attendance")
        capture_course_details(page, results_url, "results")

        print("\nDone. All detail pages saved inside portal_captures folder.")
        browser.close()


if __name__ == "__main__":
    main()

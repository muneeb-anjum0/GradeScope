
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

ROOT = Path.cwd()
CAPTURE_DIR = ROOT / "data" / "raw" / "portal_captures"
OUTPUT_PATH = ROOT / "data" / "summaries" / "scraped_attendance_summary.csv"

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def clean(text):
    return " ".join(str(text).replace("\xa0", " ").split())


def extract_course_info(soup):
    course = ""
    instructor = ""
    program = ""
    section = ""

    for row in soup.find_all("tr"):
        cells = [clean(cell.get_text(" ")) for cell in row.find_all(["td", "th"])]

        if len(cells) >= 4 and "Program:" in cells[0]:
            program = cells[1]
            section = cells[3]

        if len(cells) >= 2 and "Course:" in cells[0]:
            course = cells[1]

        if len(cells) >= 2 and "Instructor:" in cells[0]:
            instructor = cells[1]

    return course, instructor, program, section


def parse_attendance_file(file_path):
    html = file_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    course, instructor, program, section = extract_course_info(soup)

    total_lectures = 0
    present = 0
    absent = 0
    late = 0

    for row in soup.find_all("tr"):
        cells = [clean(cell.get_text(" ")) for cell in row.find_all("td")]

        if len(cells) == 3 and cells[0].isdigit():
            total_lectures += 1
            status = cells[2].lower()

            if status == "present":
                present += 1
            elif status == "absent":
                absent += 1
            elif status == "late":
                late += 1

    attendance_percentage = 0

    if total_lectures > 0:
        attendance_percentage = round(((present + late) / total_lectures) * 100, 2)

    return {
        "subject": course,
        "instructor": instructor,
        "program": program,
        "section": section,
        "total_lectures": total_lectures,
        "total_present": present,
        "total_absent": absent,
        "total_late": late,
        "attendance_percentage": attendance_percentage
    }


def run_attendance_parser():
    attendance_files = sorted(CAPTURE_DIR.glob("attendance_[0-9]*_*.html"))

    if not attendance_files:
        raise FileNotFoundError("No attendance detail files found. Run scraper first.")

    rows = [parse_attendance_file(file_path) for file_path in attendance_files]

    df = pd.DataFrame(rows)

    df["attendance_risk"] = df["attendance_percentage"].apply(
        lambda x: "High Risk" if x < 80 else "Safe"
    )

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    run_attendance_parser()

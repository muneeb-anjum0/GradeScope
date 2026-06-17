
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import re

ROOT = Path.cwd()
CAPTURE_DIR = ROOT / "data" / "raw" / "portal_captures"
OUTPUT_PATH = ROOT / "data" / "summaries" / "scraped_marks_summary.csv"

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def clean(text):
    return " ".join(str(text).replace("\xa0", " ").split())


def to_number(value):
    value = clean(value)

    if value.lower() in ["not entered", "-", ""]:
        return 0

    try:
        return float(value)
    except:
        return 0


def extract_total_marks(value):
    value = clean(value)
    match = re.search(r"([\d.]+)\s*/\s*100\s*\((\d+)%\)", value)

    if match:
        return float(match.group(1)), float(match.group(2))

    return 0, 0


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


def parse_result_file(file_path):
    html = file_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    course, instructor, program, section = extract_course_info(soup)

    quiz_marks = 0
    assignment_marks = 0
    mid_marks = 0
    final_marks = 0
    total_marks = 0
    total_percentage = 0
    grade = "-"
    reason = ""

    for row in soup.find_all("tr"):
        cells = [clean(cell.get_text(" ")) for cell in row.find_all(["td", "th"])]

        if len(cells) < 2:
            continue

        head = cells[0]
        obtained = cells[-1]

        if head.startswith("Quiz ("):
            quiz_marks = to_number(obtained)

        elif head.startswith("Assignment ("):
            assignment_marks = to_number(obtained)

        elif head.startswith("Mid Term Paper ("):
            mid_marks = to_number(obtained)

        elif head.startswith("Final Paper ("):
            final_marks = to_number(obtained)

        elif head == "Total Marks":
            total_marks, total_percentage = extract_total_marks(obtained)

        elif head == "Grade":
            grade = obtained

        elif head == "Reason":
            reason = obtained

    return {
        "subject": course,
        "program": program,
        "section": section,
        "instructor": instructor,
        "quiz_marks": quiz_marks,
        "assignment_marks": assignment_marks,
        "mid_marks": mid_marks,
        "final_marks": final_marks,
        "total_obtained_marks": total_marks,
        "current_marks_percentage": total_percentage,
        "grade": grade,
        "reason": reason
    }


def run_marks_parser():
    result_files = sorted(CAPTURE_DIR.glob("results_[0-9]*_*.html"))

    if not result_files:
        raise FileNotFoundError("No result detail files found. Run scraper first.")

    rows = [parse_result_file(file_path) for file_path in result_files]

    df = pd.DataFrame(rows)

    df["marks_risk"] = df["current_marks_percentage"].apply(
        lambda x: "High Risk" if x < 55 else "Safe"
    )

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    run_marks_parser()

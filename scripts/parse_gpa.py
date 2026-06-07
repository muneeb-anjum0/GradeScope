from pathlib import Path
import re

import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

CAPTURE_DIR = ROOT / "data" / "raw" / "portal_captures"
SUMMARY_DIR = ROOT / "data" / "summaries"

SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

GPA_SUMMARY_PATH = SUMMARY_DIR / "scraped_gpa_summary.csv"
GPA_COURSES_PATH = SUMMARY_DIR / "scraped_gpa_courses.csv"


def clean_text(value):
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_semester_order(semester):
    semester = str(semester).strip()

    match = re.search(r"(Spring|Fall)\s+(\d{4})", semester, re.IGNORECASE)

    if not match:
        return 999999

    term = match.group(1).lower()
    year = int(match.group(2))

    term_order = 1 if term == "spring" else 2

    return year * 10 + term_order


def parse_info_pairs(table):
    info = {}

    rows = table.find_all("tr")

    for row in rows:
        cells = [clean_text(cell.get_text(" ")) for cell in row.find_all(["td", "th"])]

        if len(cells) >= 2:
            key = cells[0].replace(":", "").strip()
            value = cells[1].strip()

            if key:
                info[key] = value

    return info


def find_result_tables(soup):
    tables = soup.find_all("table")

    info_table = None
    course_table = None

    for table in tables:
        text = clean_text(table.get_text(" "))

        if "Student Name" in text and ("Semester GPA" in text or "CGPA" in text):
            info_table = table

        if "Course Name" in text and "Credit Hours" in text and "Grade" in text and "Grade Points" in text:
            course_table = table

    return info_table, course_table


def parse_course_rows(course_table, semester):
    rows = []

    if course_table is None:
        return rows

    for tr in course_table.find_all("tr"):
        cells = [clean_text(cell.get_text(" ")) for cell in tr.find_all(["td", "th"])]

        if len(cells) < 4:
            continue

        if "Course Name" in cells[0]:
            continue

        course_name = cells[0]
        credit_hours = cells[1]
        grade = cells[2]
        grade_points = cells[3]

        if not course_name or course_name.lower() == "course name":
            continue

        rows.append(
            {
                "semester": semester,
                "course_name": course_name,
                "credit_hours": credit_hours,
                "grade": grade,
                "grade_points": grade_points,
            }
        )

    return rows


def parse_gpa_file(path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    page_text = clean_text(soup.get_text(" "))

    if "Student Semester Result" not in page_text:
        return None, []

    info_table, course_table = find_result_tables(soup)

    if info_table is None:
        return None, []

    info = parse_info_pairs(info_table)

    student_name = info.get("Student Name", "")
    registration_number = info.get("Registration Number", "")
    semester = info.get("Semester", "")
    semester_gpa = info.get("Semester GPA", "")

    if not semester or not semester_gpa:
        return None, []

    try:
        semester_gpa_value = float(semester_gpa)
    except Exception:
        semester_gpa_value = None

    courses = parse_course_rows(course_table, semester)

    total_credit_hours = 0
    counted_courses = 0

    for course in courses:
        try:
            total_credit_hours += float(course["credit_hours"])
            counted_courses += 1
        except Exception:
            pass

    summary = {
        "semester": semester,
        "semester_order": normalize_semester_order(semester),
        "semester_gpa": semester_gpa_value,
        "student_name": student_name,
        "registration_number": registration_number,
        "total_courses": len(courses),
        "counted_courses": counted_courses,
        "total_credit_hours": total_credit_hours,
        "source_file": path.name,
    }

    return summary, courses


def main():
    html_files = sorted(CAPTURE_DIR.glob("previous_semester_result_*.html"))

    summaries = []
    all_courses = []

    for html_file in html_files:
        summary, courses = parse_gpa_file(html_file)

        if summary:
            summaries.append(summary)
            all_courses.extend(courses)

    if summaries:
        gpa_df = pd.DataFrame(summaries)
        gpa_df = gpa_df.drop_duplicates(subset=["semester"], keep="last")
        gpa_df = gpa_df.sort_values("semester_order")
    else:
        gpa_df = pd.DataFrame(
            columns=[
                "semester",
                "semester_order",
                "semester_gpa",
                "student_name",
                "registration_number",
                "total_courses",
                "counted_courses",
                "total_credit_hours",
                "source_file",
            ]
        )

    if all_courses:
        courses_df = pd.DataFrame(all_courses)
        courses_df = courses_df.drop_duplicates(
            subset=["semester", "course_name"],
            keep="last"
        )
    else:
        courses_df = pd.DataFrame(
            columns=[
                "semester",
                "course_name",
                "credit_hours",
                "grade",
                "grade_points",
            ]
        )

    gpa_df.to_csv(GPA_SUMMARY_PATH, index=False)
    courses_df.to_csv(GPA_COURSES_PATH, index=False)

    print(f"Saved GPA summary: {GPA_SUMMARY_PATH}")
    print(f"Saved GPA courses: {GPA_COURSES_PATH}")
    print(f"Semesters parsed: {len(gpa_df)}")
    print(f"Course rows parsed: {len(courses_df)}")


if __name__ == "__main__":
    main()
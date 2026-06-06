
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

CAPTURE_DIR = Path("portal_captures")

def clean(text):
    return " ".join(text.replace("\xa0", " ").split())

def extract_course_info(soup):
    course = ""
    instructor = ""
    program = ""
    section = ""

    rows = soup.find_all("tr")

    for row in rows:
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

def main():
    attendance_files = sorted(CAPTURE_DIR.glob("attendance_[0-9]*_*.html"))

    if not attendance_files:
        print("No attendance detail files found.")
        return

    rows = []

    for file_path in attendance_files:
        rows.append(parse_attendance_file(file_path))

    df = pd.DataFrame(rows)

    df["attendance_risk"] = df["attendance_percentage"].apply(
        lambda x: "High Risk" if x < 75 else "Warning" if x < 80 else "Safe"
    )

    df.to_csv("scraped_attendance_summary.csv", index=False)

    print("Saved scraped_attendance_summary.csv")
    print(df)

if __name__ == "__main__":
    main()

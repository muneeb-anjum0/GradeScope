
from pathlib import Path
import pandas as pd

ROOT = Path.cwd()

ATTENDANCE_PATH = ROOT / "data" / "summaries" / "scraped_attendance_summary.csv"
MARKS_PATH = ROOT / "data" / "summaries" / "scraped_marks_summary.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "gradescope_final_dashboard.csv"

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def final_risk(row):
    attendance = row.get("attendance_percentage", 0)
    marks = row.get("current_marks_percentage", 0)
    reason = str(row.get("reason", "")).lower()

    if attendance < 80 or marks < 55 or "short attendance" in reason:
        return "High Risk"

    return "Safe"


def recommendation(row):
    recs = []

    if row["attendance_percentage"] < 80:
        recs.append("Attendance is below the safe 80% level. Attend every upcoming class.")

    if row["current_marks_percentage"] < 55:
        recs.append("Marks are below passing level. Prioritize this subject before finals.")

    if "short attendance" in str(row.get("reason", "")).lower():
        recs.append("Portal shows short attendance issue. Confirm with the department.")

    if row["final_marks"] == 0:
        recs.append("Final marks are not entered yet, so current result is incomplete.")

    if not recs:
        recs.append("Subject is currently safe. Maintain attendance and marks.")

    return " ".join(recs)


def run_merge():
    if not ATTENDANCE_PATH.exists():
        raise FileNotFoundError("Missing scraped_attendance_summary.csv. Run attendance parser first.")

    if not MARKS_PATH.exists():
        raise FileNotFoundError("Missing scraped_marks_summary.csv. Run marks parser first.")

    attendance = pd.read_csv(ATTENDANCE_PATH)
    marks = pd.read_csv(MARKS_PATH)

    final_df = pd.merge(
        attendance,
        marks,
        on=["subject", "program", "section", "instructor"],
        how="outer"
    )

    numeric_columns = [
        "attendance_percentage",
        "total_present",
        "total_absent",
        "total_late",
        "quiz_marks",
        "assignment_marks",
        "mid_marks",
        "final_marks",
        "total_obtained_marks",
        "current_marks_percentage"
    ]

    for col in numeric_columns:
        if col in final_df.columns:
            final_df[col] = pd.to_numeric(final_df[col], errors="coerce").fillna(0)

    final_df["final_risk_status"] = final_df.apply(final_risk, axis=1)
    final_df["recommendation"] = final_df.apply(recommendation, axis=1)

    final_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved {OUTPUT_PATH}")
    return final_df


if __name__ == "__main__":
    run_merge()

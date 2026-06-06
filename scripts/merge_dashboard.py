
import pandas as pd

attendance = pd.read_csv("scraped_attendance_summary.csv")
marks = pd.read_csv("scraped_marks_summary.csv")

final_df = pd.merge(
    attendance,
    marks,
    on=["subject", "program", "section", "instructor"],
    how="outer"
)

def final_risk(row):
    attendance = row.get("attendance_percentage", 0)
    marks = row.get("current_marks_percentage", 0)
    reason = str(row.get("reason", "")).lower()

    if attendance < 75 or marks < 50 or "short attendance" in reason:
        return "High Risk"

    if attendance < 80 or marks < 65:
        return "Warning"

    return "Safe"

def recommendation(row):
    recs = []

    if row["attendance_percentage"] < 75:
        recs.append("Attendance is below 75%. Attend every upcoming class.")

    elif row["attendance_percentage"] < 80:
        recs.append("Attendance is close to danger zone. Avoid absents.")

    if row["current_marks_percentage"] < 50:
        recs.append("Marks are weak. Focus strongly before finals.")

    elif row["current_marks_percentage"] < 65:
        recs.append("Marks are average. Improve quizzes, assignments, and final prep.")

    if "short attendance" in str(row.get("reason", "")).lower():
        recs.append("Portal shows short attendance issue. Confirm with exam/department office.")

    if row["final_marks"] == 0:
        recs.append("Final marks are not entered yet, so current result is incomplete.")

    if not recs:
        recs.append("Subject looks stable. Maintain performance.")

    return " ".join(recs)

final_df["final_risk_status"] = final_df.apply(final_risk, axis=1)
final_df["recommendation"] = final_df.apply(recommendation, axis=1)

final_df.to_csv("final_scraped_academic_dashboard.csv", index=False)

print("Saved final_scraped_academic_dashboard.csv")
print(final_df)

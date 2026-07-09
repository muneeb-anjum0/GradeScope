import argparse
from pathlib import Path
import shutil
import subprocess
import sys

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CAPTURE_DIR = RAW_DIR / "portal_captures"
TEXT_DUMPS_DIR = RAW_DIR / "text_dumps"
SUMMARIES_DIR = DATA_DIR / "summaries"
PROCESSED_DIR = DATA_DIR / "processed"

FINAL_DATA_PATH = PROCESSED_DIR / "gradescope_final_dashboard.csv"
ATTENDANCE_PATH = SUMMARIES_DIR / "scraped_attendance_summary.csv"
MARKS_PATH = SUMMARIES_DIR / "scraped_marks_summary.csv"
GPA_SUMMARY_PATH = SUMMARIES_DIR / "scraped_gpa_summary.csv"
GPA_COURSES_PATH = SUMMARIES_DIR / "scraped_gpa_courses.csv"
SYNC_LOG_PATH = TEXT_DUMPS_DIR / "sync_log.txt"

app = FastAPI(title="GradeScope API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    df = pd.read_csv(path)
    return df.fillna("").to_dict(orient="records")


def file_status(path: Path) -> dict:
    return {
        "exists": path.exists(),
        "updated_at": path.stat().st_mtime if path.exists() else None,
        "rows": len(pd.read_csv(path)) if path.exists() else 0,
    }


def ensure_playwright_chromium() -> dict | None:
    process = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = (process.stdout or "") + (process.stderr or "")
    if process.returncode == 0:
        return None

    return {
        "script": "playwright install chromium",
        "returncode": process.returncode,
        "output": output,
    }


def run_script(script_name: str) -> dict:
    if script_name == "portal_scraper.py":
        install_result = ensure_playwright_chromium()
        if install_result:
            return install_result

    process = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script_name)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = (process.stdout or "") + (process.stderr or "")
    return {
        "script": script_name,
        "returncode": process.returncode,
        "output": output,
    }


@app.get("/api/status")
def status():
    return {
        "dashboard": file_status(FINAL_DATA_PATH),
        "attendance": file_status(ATTENDANCE_PATH),
        "marks": file_status(MARKS_PATH),
        "gpa": file_status(GPA_SUMMARY_PATH),
        "gpa_courses": file_status(GPA_COURSES_PATH),
    }


@app.get("/api/dashboard")
def dashboard():
    return read_csv(FINAL_DATA_PATH)


@app.get("/api/attendance")
def attendance():
    return read_csv(ATTENDANCE_PATH)


@app.get("/api/marks")
def marks():
    return read_csv(MARKS_PATH)


@app.get("/api/gpa")
def gpa():
    return read_csv(GPA_SUMMARY_PATH)


@app.get("/api/gpa-courses")
def gpa_courses():
    return read_csv(GPA_COURSES_PATH)


@app.get("/api/raw-notes")
def raw_notes():
    if not TEXT_DUMPS_DIR.exists():
        return []
    notes = []
    for path in sorted(TEXT_DUMPS_DIR.glob("*.txt")):
        notes.append({"name": path.name, "text": path.read_text(encoding="utf-8", errors="replace")})
    return notes


@app.post("/api/sync")
def sync():
    steps = [
        "portal_scraper.py",
        "parse_attendance.py",
        "parse_marks.py",
        "parse_gpa.py",
        "merge_dashboard.py",
    ]
    logs = []
    for step in steps:
        result = run_script(step)
        logs.append(result)
        if result["returncode"] != 0:
            raise HTTPException(status_code=500, detail={"failed_step": step, "logs": logs})

    if not FINAL_DATA_PATH.exists() or not read_csv(FINAL_DATA_PATH):
        raise HTTPException(status_code=500, detail={"failed_step": "merge_dashboard.py", "logs": logs})

    return {"ok": True, "logs": logs}


@app.post("/api/clear-data")
def clear_data():
    for path in [FINAL_DATA_PATH, ATTENDANCE_PATH, MARKS_PATH, GPA_SUMMARY_PATH, GPA_COURSES_PATH]:
        if path.exists():
            path.unlink()

    for folder in [TEXT_DUMPS_DIR, CAPTURE_DIR]:
        if folder.exists():
            for item in folder.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

    return {"ok": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the GradeScope backend.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload.")
    args = parser.parse_args()

    uvicorn.run("main:app", host=args.host, port=args.port, reload=not args.no_reload)

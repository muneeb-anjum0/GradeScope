# GradeScope

GradeScope is a local academic dashboard with a FastAPI backend and a React/Vite frontend.

## Project Layout

```text
GradeScope/
  backend/        FastAPI API, scraper, parsers, and local data outputs
  frontend/       React + Vite UI
  docs/           Data dictionary and privacy notes
  notebooks/      Older exploration notebooks
```

## Start The Backend

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
Set-Location backend
..\.venv\Scripts\python.exe main.py
```

Backend URLs:

```text
API:  http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs
```

If `python main.py` reports `WinError 10013` or says the socket cannot be opened, something is probably already using port `8000`. Check it with:

```powershell
Get-NetTCPConnection -LocalPort 8000
```

If `http://127.0.0.1:8000/api/status` works, the backend is already running. Otherwise stop the old process or run a temporary backend on another port:

```powershell
python main.py --port 8001
```

If `.venv` is missing, create it first:

```powershell
python -m venv .venv
```

## Start The Frontend

Open a second PowerShell window:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The frontend calls the backend at `http://127.0.0.1:8000`.

## Main API Endpoints

```text
GET  /api/status
GET  /api/dashboard
GET  /api/attendance
GET  /api/marks
GET  /api/gpa
GET  /api/gpa-courses
GET  /api/raw-notes
POST /api/sync
POST /api/clear-data
```

`POST /api/sync` opens the portal scraper flow. Log in manually when the browser appears; the scraper continues after login is detected.

The live sync browser is tuned for speed: it blocks images, fonts, and media, uses short settle waits, and saves the HTML/text needed by the parsers.

## Data Notes

Generated local data lives under:

```text
backend/data/raw/
backend/data/summaries/
backend/data/processed/
```

These folders may be empty in a fresh checkout. If the dashboard is blank, run sync from the UI or generate the parser outputs first.

## Audit Notes

- The deleted root `.bat` files are no longer required; use the PowerShell commands above.
- The active backend entrypoint is `backend/main.py`.
- The active frontend entrypoint is `frontend/src/App.tsx`.
- Current backend output expected by the API is `backend/data/processed/gradescope_final_dashboard.csv`.

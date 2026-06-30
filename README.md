# GradeScope

GradeScope is a local academic dashboard for tracking academic progress in one place instead of jumping across portal pages and losing context.

It combines a FastAPI backend, a React/Vite frontend, and a portal sync flow that collects attendance, marks, GPA, and dashboard data.

## Start

```bat
start-all.bat
```

Open:

```text
http://127.0.0.1:5173
```

Backend:

```text
http://127.0.0.1:8000
```

## Sync

`POST /api/sync` opens the portal login flow. Log in manually; GradeScope continues once login is detected.

The sync browser blocks unnecessary assets and saves only the HTML/text needed for parsing.

## API

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

## Data

```text
backend/data/raw/
backend/data/summaries/
backend/data/processed/
```

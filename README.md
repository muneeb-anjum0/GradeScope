# GradeScope

## Academic Risk Dashboard with Portal Automation

GradeScope is a Python and Jupyter Notebook project that turns raw university portal data into a clean academic risk dashboard.

It automates portal capture, parses attendance and marks from HTML pages, merges the extracted data, calculates academic risk, and generates visual insights with subject-wise recommendations.

## Why GradeScope Exists

Most student portals show data, but they do not explain risk clearly.

GradeScope answers:

> Which subjects need urgent attention before it is too late?

## Core Features

- Portal automation using Playwright
- Attendance page capture
- Marks page capture
- HTML parsing using BeautifulSoup
- Subject-wise attendance calculation
- Present, absent, and late count extraction
- Quiz, assignment, midterm, final, and total marks extraction
- Grade and short-attendance reason extraction
- Combined academic risk scoring
- Subject-wise recommendations
- Professional charts
- HTML report generation
- Demo dataset for public GitHub use
- Privacy-safe project structure

## Dashboard Preview

### Executive Summary

![KPI Summary](assets/charts/kpi_summary.png)

### Attendance Health

![Attendance Health](assets/charts/attendance_health_pro.png)

### Marks Performance

![Marks Performance](assets/charts/marks_performance_pro.png)

### Risk Distribution

![Risk Distribution](assets/charts/risk_distribution_donut.png)

### Attendance vs Marks Risk Map

![Risk Map](assets/charts/risk_map_pro.png)

## Tech Stack

- Python
- Jupyter Notebook
- Pandas
- NumPy
- Matplotlib
- BeautifulSoup
- Playwright

## Project Structure

```text
gradescope/
│
├── README.md
├── requirements.txt
├── .gitignore
├── SZABIST_Academic_Dashboard.ipynb
├── scraper.ipynb
│
├── data/
│   ├── raw/
│   ├── processed/
│   │   ├── demo_gradescope_dashboard.csv
│   │   └── gradescope_final_dashboard.csv
│   └── summaries/
│
├── scripts/
│   ├── scraper.py
│   ├── parse_attendance.py
│   ├── parse_marks.py
│   └── merge_dashboard.py
│
├── assets/
│   ├── charts/
│   └── reports/
│
└── docs/
    ├── DATA_DICTIONARY.md
    └── PRIVACY_CHECKLIST.md
```

## Main Outputs

| Output | Purpose |
|---|---|
| `data/processed/demo_gradescope_dashboard.csv` | Public-safe demo dataset |
| `data/processed/gradescope_final_dashboard.csv` | Final processed dashboard dataset |
| `assets/reports/gradescope_report.html` | Professional HTML dashboard report |
| `assets/charts/` | Generated visual dashboard charts |
| `docs/DATA_DICTIONARY.md` | Explanation of dataset columns |
| `docs/PRIVACY_CHECKLIST.md` | Safety checklist before uploading |

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
python -m playwright install
```

Then open:

```text
SZABIST_Academic_Dashboard.ipynb
```

For scraping and parsing workflow, open:

```text
scraper.ipynb
```

## Privacy Notice

This project is designed for personal academic analytics.

Do not upload:

- `.env`
- Real portal captures
- Portal screenshots with personal details
- Raw private academic data
- Login credentials

Use the demo dataset for public GitHub repositories.

## Future Improvements

- Streamlit web dashboard
- Weekly auto-refresh
- Email alerts for low attendance
- PDF report export
- Grade prediction model
- Absence impact calculator
- Course-wise study priority planner

## Status

GradeScope is fully functional as an academic portal automation and analytics project.
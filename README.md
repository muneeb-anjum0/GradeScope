# GradeScope

GradeScope is a local academic analytics dashboard built for students of SZABIST University who want a clearer view of their attendance, marks, GPA, and subject risk from the ZABDESK Academic Portal.

The application opens ZABDESK in a real browser, lets the student log in manually, captures attendance and result pages, parses the data, and displays everything in a clean Streamlit dashboard.

GradeScope runs locally. It does not require portal credentials inside the code, and it does not store passwords.

---

# Table of Contents

* [Overview](#overview)
* [Why This Project Exists](#why-this-project-exists)
* [Core Features](#core-features)
* [ZABDESK Portal Workflow](#zabdesk-portal-workflow)
* [Risk Rules](#risk-rules)
* [Screenshots](#screenshots)
* [Quick Start Using ZIP](#quick-start-using-zip)
* [Quick Start Using Git](#quick-start-using-git)
* [Manual Setup](#manual-setup)
* [Project Structure](#project-structure)
* [Important Files](#important-files)
* [Tech Stack](#tech-stack)
* [Current Status](#current-status)
* [Possible Improvements](#possible-improvements)
* [Disclaimer](#disclaimer)

---

# Overview

Student portals often show academic data, but they usually do not explain what needs attention.

GradeScope solves that by turning ZABDESK portal data into a focused local dashboard. It helps students quickly understand attendance risk, marks performance, GPA trend, missing finals, and subject priority.

The project is designed around the SZABIST Academic Portal, ZABDESK.

```text
ZABDESK Portal
      ↓
Manual Student Login
      ↓
Portal Page Capture
      ↓
HTML and Text Extraction
      ↓
Attendance, Marks, and GPA Parsing
      ↓
CSV Dataset Generation
      ↓
Streamlit Dashboard
```

---

# Why This Project Exists

ZABDESK provides important academic information, but students still have to manually open multiple pages and interpret the risk themselves.

GradeScope answers practical questions such as:

* Which subjects are below 80 percent attendance?
* Which subjects are below 55 percent marks?
* Which subjects have missing final marks?
* What is the semester GPA trend?
* What is the cumulative GPA trend?
* Which subjects should be fixed first?
* What data was captured from the portal?
* What tables are powering each chart?

---

# Core Features

## Dashboard

* Local Streamlit dashboard
* Clean white UI
* Live academic stat cards
* Attendance health chart
* Marks performance chart
* SGPA and CGPA trend graph
* Assessment contribution chart
* Grade distribution chart
* Subject health heatmap
* Performance spread chart
* Attendance versus marks risk map
* Priority action plan for high-risk subjects

## Portal Sync

* Opens the SZABIST ZABDESK Academic Portal in a real browser
* Student logs in manually
* Detects successful login
* Captures attendance pages
* Captures current semester result pages
* Captures previous semester GPA pages
* Saves raw HTML and raw text locally
* Parses captured data into structured CSV files

## Data Views

* Raw Notes page for captured portal text
* Tables page for all parsed and merged datasets
* GPA table
* GPA course table
* Attendance table
* Marks table
* Risk map table
* Final merged dashboard table
* Parser output tables

## Local Data Controls

* Clear local dashboard data from inside the app
* Reset before a new scrape
* Keep scripts and setup files untouched
* Remove private captured portal data safely

---

# ZABDESK Portal Workflow

GradeScope is built for the SZABIST ZABDESK Academic Portal.

The app does not bypass login. It opens the portal and waits for the student to log in manually.

```text
1. Start GradeScope
2. Open Portal Sync
3. Click Start live portal sync
4. ZABDESK opens in a browser
5. Student logs in manually
6. GradeScope detects the logged-in session
7. Attendance pages are captured
8. Current semester results are captured
9. Previous semester GPA pages are captured
10. Data is parsed and merged
11. Dashboard updates locally
```

---

# Risk Rules

GradeScope uses simple academic risk rules.

| Metric     |          Safe Level | Risk Condition   |
| ---------- | ------------------: | ---------------- |
| Attendance | 80 percent or above | Below 80 percent |
| Marks      | 55 percent or above | Below 55 percent |

These rules are used to flag subjects that need attention.

---

# Screenshots

Place screenshots in the `assets/charts/` folder and keep the filenames matched with the paths below.

## KPI Summary

![KPI Summary](assets/charts/kpi_summary.png)

## Attendance Health

![Attendance Health](assets/charts/attendance_health_pro.png)

## Marks Performance

![Marks Performance](assets/charts/marks_performance_pro.png)


## Risk Map

![Risk Map](assets/charts/risk_map_pro.png)

If an image does not load, check the filename inside `assets/charts/` and update the path in this README.

---

# Quick Start Using ZIP

A ready-to-use `.zip` file is included in this repository.

Use the ZIP version if you want to download and run the project without manually cloning the repository.

## Steps

1. Download the ZIP file from this repository.
2. Extract it anywhere on your computer.
3. Open the extracted folder.
4. Run the setup file:

```text
setup.bat
```

5. Start the app:

```text
start_gradescope.bat
```

6. The Streamlit app will open in your browser.

---

# Quick Start Using Git

Clone the repository:

```bash
git clone <your-repository-link>
cd gradescope
```

Install dependencies:

```bash
setup.bat
```

Start the app:

```bash
start_gradescope.bat
```

---

# Manual Setup

Use this method if you want to run everything from the terminal.

```bash
pip install -r requirements.txt
python -m playwright install
streamlit run app.py
```

---

# How to Sync ZABDESK Data

After starting the app:

1. Open the sidebar.
2. Click `Portal Sync`.
3. Click `Start live portal sync`.
4. Wait for ZABDESK to open.
5. Log in manually.
6. Do not close the browser while GradeScope is capturing pages.
7. Wait for all parser steps to finish.
8. Return to the dashboard.

The dashboard will update using the locally captured and parsed data.

---

# Project Structure

```text
gradescope/
├── app.py
├── setup.bat
├── start_gradescope.bat
├── requirements.txt
├── README.md
├── SZABIST_Academic_Dashboard.ipynb
├── scraper.ipynb
├── scripts/
│   ├── portal_scraper.py
│   ├── parse_attendance.py
│   ├── parse_marks.py
│   ├── parse_gpa.py
│   └── merge_dashboard.py
├── data/
│   ├── processed/
│   │   └── demo_gradescope_dashboard.csv
│   ├── raw/
│   └── summaries/
├── assets/
│   ├── charts/
│   └── reports/
│       └── gradescope_report.html
└── docs/
    ├── DATA_DICTIONARY.md
    └── PRIVACY_CHECKLIST.md
```

---

# Important Files

| File                                           | Purpose                                 |
| ---------------------------------------------- | --------------------------------------- |
| `app.py`                                       | Main Streamlit dashboard                |
| `setup.bat`                                    | Windows setup script                    |
| `start_gradescope.bat`                         | Starts the local app                    |
| `requirements.txt`                             | Python dependencies                     |
| `scripts/portal_scraper.py`                    | Opens ZABDESK and captures portal pages |
| `scripts/parse_attendance.py`                  | Extracts attendance data                |
| `scripts/parse_marks.py`                       | Extracts current semester marks         |
| `scripts/parse_gpa.py`                         | Extracts previous semester GPA data     |
| `scripts/merge_dashboard.py`                   | Builds the final dashboard dataset      |
| `data/processed/demo_gradescope_dashboard.csv` | Public-safe demo dataset                |
| `docs/DATA_DICTIONARY.md`                      | Dataset column reference                |
| `docs/PRIVACY_CHECKLIST.md`                    | Privacy checklist before publishing     |

---

# Tech Stack

| Area                 | Tools              |
| -------------------- | ------------------ |
| Language             | Python             |
| Dashboard            | Streamlit          |
| Browser Automation   | Playwright         |
| HTML Parsing         | BeautifulSoup      |
| Data Processing      | Pandas, NumPy      |
| Charts               | Plotly, Matplotlib |
| Development Workflow | Jupyter Notebook   |
| Platform             | Windows            |

---

# Data Generated by the App

GradeScope creates local data files during portal sync.

```text
data/raw/
data/summaries/
data/processed/
```

Typical generated files include:

```text
scraped_attendance_summary.csv
scraped_marks_summary.csv
scraped_gpa_summary.csv
scraped_gpa_courses.csv
gradescope_final_dashboard.csv
```

The app also stores raw captured portal text and HTML locally during scraping.

These files should not be uploaded publicly unless sanitized.

---



# Current Status

GradeScope is currently a working local academic dashboard.

It can:

* Open the SZABIST ZABDESK portal
* Wait for manual student login
* Capture attendance pages
* Capture current semester result pages
* Capture previous semester GPA pages
* Parse attendance data
* Parse marks data
* Parse SGPA and CGPA data
* Merge parsed data into a dashboard dataset
* Display polished charts
* Display source tables
* Display raw sync notes
* Clear local data safely

---

# Possible Improvements

* PDF report export
* Better mobile layout
* Demo mode for public hosting
* Attendance recovery calculator
* Grade prediction
* Weekly reminder system
* Course priority planner
* Exportable semester report
* Better handling for different ZABDESK layouts

---

# Disclaimer

This project is for personal academic tracking and portfolio demonstration.

It is not an official SZABIST product.

It is not affiliated with SZABIST University or the ZABDESK Academic Portal.

Use it responsibly. Keep private student data local and do not publish real academic records.

---

# Development Note

GradeScope started as a Jupyter Notebook experiment and later became a full local dashboard app.

The notebooks were used for exploration, parsing, testing, and building the data pipeline. The final product is the Streamlit app powered by `app.py`.

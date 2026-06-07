from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path.cwd()

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
TEXT_DUMPS_DIR = RAW_DIR / "text_dumps"
CAPTURE_DIR = RAW_DIR / "portal_captures"
SUMMARIES_DIR = DATA_DIR / "summaries"
PROCESSED_DIR = DATA_DIR / "processed"

FINAL_DATA_PATH = PROCESSED_DIR / "gradescope_final_dashboard.csv"
ATTENDANCE_PATH = SUMMARIES_DIR / "scraped_attendance_summary.csv"
MARKS_PATH = SUMMARIES_DIR / "scraped_marks_summary.csv"
GPA_SUMMARY_PATH = SUMMARIES_DIR / "scraped_gpa_summary.csv"
GPA_COURSES_PATH = SUMMARIES_DIR / "scraped_gpa_courses.csv"
SYNC_LOG_PATH = TEXT_DUMPS_DIR / "sync_log.txt"

for folder in [TEXT_DUMPS_DIR, CAPTURE_DIR, SUMMARIES_DIR, PROCESSED_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="GradeScope",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
:root {
    --bg: #f7f9fc;
    --card: #ffffff;
    --card-soft: #f9fbff;
    --text: #07111f;
    --muted: #637083;
    --faint: #94a3b8;
    --line: #e2e8f0;
    --line-strong: #cbd5e1;

    --blue: #2563eb;
    --blue-soft: #eff6ff;
    --green: #16a34a;
    --green-soft: #ecfdf5;
    --red: #dc2626;
    --red-soft: #fef2f2;
    --amber: #d97706;
    --amber-soft: #fffbeb;
    --purple: #7c3aed;
    --purple-soft: #f5f3ff;
    --cyan: #0891b2;
    --cyan-soft: #ecfeff;

    --shadow: 0 24px 70px rgba(15, 23, 42, 0.10);
    --shadow-soft: 0 12px 35px rgba(15, 23, 42, 0.07);
    --shadow-tiny: 0 8px 18px rgba(15, 23, 42, 0.05);
}

#MainMenu, footer, header {
    visibility: hidden;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

html {
    scroll-behavior: smooth;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(circle at 12% 7%, rgba(37, 99, 235, 0.14), transparent 26%),
        radial-gradient(circle at 86% 4%, rgba(22, 163, 74, 0.11), transparent 25%),
        radial-gradient(circle at 70% 55%, rgba(124, 58, 237, 0.08), transparent 30%),
        linear-gradient(180deg, #ffffff 0%, var(--bg) 56%, #eef4fb 100%);
}

.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
    max-width: 1380px;
}

section[data-testid="stSidebar"] {
    background: transparent !important;
    padding: 10px 0 10px 12px !important;
    border: none !important;
}

section[data-testid="stSidebar"] > div {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,252,255,0.95));
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: 30px;
    box-shadow: var(--shadow);
    min-height: calc(100vh - 20px);
    max-height: calc(100vh - 20px);
    overflow: visible !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 16px 16px 14px 16px !important;
}

[data-testid="stSidebarCollapseButton"] {
    color: var(--text) !important;
}

h1, h2, h3, h4, h5, h6 {
    letter-spacing: -0.04em;
    color: var(--text);
}

div[data-testid="stButton"] {
    width: 100%;
}

.stButton {
    width: 100%;
}

.stButton > button {
    width: 100% !important;
    min-height: 50px;
    border-radius: 18px;
    border: 1px solid var(--line);
    background: linear-gradient(180deg, #ffffff, #f8fbff);
    color: var(--text);
    font-weight: 850;
    font-size: 14px;
    text-align: left;
    justify-content: flex-start;
    padding-left: 18px;
    box-shadow: var(--shadow-tiny);
    transition: all 0.18s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    border-color: #93c5fd;
    background: linear-gradient(180deg, #f8fbff, #ffffff);
    box-shadow: var(--shadow-soft);
}

.stButton > button:active {
    transform: translateY(0);
}

[data-testid="stDownloadButton"] button {
    background: #ffffff !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    border-radius: 16px !important;
    font-weight: 850 !important;
    box-shadow: var(--shadow-tiny) !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: #f8fbff !important;
    color: var(--text) !important;
    border-color: #93c5fd !important;
}

[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span {
    color: var(--text) !important;
    font-weight: 750 !important;
}

.sidebar-brand {
    padding: 18px 16px 16px 16px;
    margin-bottom: 14px;
    animation: fadeUp .45s ease both;
}

.sidebar-title-main {
    font-size: 35px;
    font-weight: 980;
    letter-spacing: -0.08em;
    color: var(--text);
    line-height: 0.92;
    margin: 0;
}

.sidebar-subtitle {
    margin-top: 10px;
    color: var(--muted);
    font-size: 12px;
    line-height: 1.45;
    font-weight: 700;
}

.sidebar-section-title {
    font-size: 10.5px;
    font-weight: 950;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--muted);
    margin: 15px 4px 8px 4px;
}

.sidebar-card {
    border: 1px solid var(--line);
    background: rgba(255,255,255,0.80);
    border-radius: 20px;
    padding: 13px;
    margin-top: 9px;
    box-shadow: 0 10px 22px rgba(15,23,42,0.04);
    animation: fadeUp .5s ease both;
}

.sidebar-card-title {
    font-size: 10.5px;
    font-weight: 950;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-bottom: 8px;
}

.sidebar-card-body {
    font-size: 12.5px;
    line-height: 1.55;
    color: var(--text);
}

.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 999px;
    margin-right: 7px;
    background: var(--green);
    box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.12);
}

.status-dot.red {
    background: var(--red);
    box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.12);
}

.hero-shell {
    position: relative;
    overflow: hidden;
    border-radius: 34px;
    padding: 34px;
    margin-bottom: 24px;
    background:
        radial-gradient(circle at 82% 16%, rgba(37, 99, 235, 0.13), transparent 28%),
        radial-gradient(circle at 18% 90%, rgba(22, 163, 74, 0.11), transparent 27%),
        linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,251,255,0.94));
    border: 1px solid rgba(226,232,240,0.92);
    box-shadow: var(--shadow);
    animation: fadeUp .48s ease both;
}

.hero-shell:before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(15,23,42,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(15,23,42,0.025) 1px, transparent 1px);
    background-size: 28px 28px;
    mask-image: linear-gradient(90deg, black, transparent 78%);
    pointer-events: none;
}

.hero-kicker {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    background: var(--blue-soft);
    color: var(--blue);
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.hero-title {
    position: relative;
    font-size: clamp(38px, 5vw, 66px);
    line-height: 0.95;
    font-weight: 980;
    letter-spacing: -0.075em;
    max-width: 820px;
}

.hero-copy {
    position: relative;
    max-width: 820px;
    color: var(--muted);
    font-size: 16px;
    line-height: 1.68;
    margin-top: 14px;
}

.hero-meta-row {
    position: relative;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 20px;
}

.mini-chip {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 9px 12px;
    border-radius: 999px;
    background: #ffffff;
    border: 1px solid var(--line);
    color: var(--text);
    font-size: 12px;
    font-weight: 850;
    box-shadow: var(--shadow-tiny);
}

.page-head {
    margin-bottom: 22px;
    animation: fadeUp .45s ease both;
}

.page-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    border-radius: 999px;
    background: var(--blue-soft);
    color: var(--blue);
    font-size: 12px;
    font-weight: 900;
    margin-bottom: 12px;
}

.page-title {
    font-size: clamp(38px, 5vw, 60px);
    line-height: 0.98;
    font-weight: 980;
    letter-spacing: -0.075em;
    color: var(--text);
}

.page-copy {
    max-width: 800px;
    margin-top: 12px;
    color: var(--muted);
    font-size: 16px;
    line-height: 1.7;
}

.health-card {
    position: relative;
    overflow: hidden;
    min-height: 132px;
    border-radius: 26px;
    border: 1px solid rgba(226,232,240,0.94);
    background:
        radial-gradient(circle at top right, rgba(37,99,235,0.08), transparent 35%),
        #ffffff;
    box-shadow: var(--shadow-soft);
    padding: 21px;
    animation: fadeUp .52s ease both;
    transition: all .2s ease;
}

.health-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow);
}

.health-label {
    font-size: 11px;
    font-weight: 950;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 13px;
}

.health-value {
    font-size: 38px;
    line-height: 1;
    font-weight: 980;
    letter-spacing: -0.06em;
    color: var(--text);
}

.health-foot {
    margin-top: 13px;
}

.pill {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 7px 10px;
    font-size: 11.5px;
    font-weight: 850;
}

.pill.blue {
    background: var(--blue-soft);
    color: var(--blue);
}

.pill.green {
    background: var(--green-soft);
    color: var(--green);
}

.pill.red {
    background: var(--red-soft);
    color: var(--red);
}

.pill.amber {
    background: var(--amber-soft);
    color: var(--amber);
}

.grid-card {
    border-radius: 24px;
    border: 1px solid rgba(226,232,240,0.94);
    background:
        linear-gradient(180deg, #ffffff, #fbfdff);
    box-shadow: var(--shadow-soft);
    padding: 20px;
    min-height: 150px;
    animation: fadeUp .52s ease both;
    transition: all .2s ease;
}

.grid-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow);
}

.grid-label {
    font-size: 11px;
    font-weight: 950;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 11px;
}

.grid-value {
    font-size: 31px;
    font-weight: 980;
    letter-spacing: -0.055em;
    color: var(--text);
    margin-bottom: 8px;
}

.grid-copy {
    color: var(--muted);
    font-size: 13.5px;
    line-height: 1.55;
}

.chart-card {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
    margin-top: 32px;
    margin-bottom: 12px;
    animation: fadeUp .5s ease both;
}

.chart-title {
    font-size: 32px;
    font-weight: 980;
    letter-spacing: -0.07em;
    color: var(--text);
    margin-bottom: 6px;
}

.chart-copy {
    font-size: 15px;
    color: var(--muted);
    line-height: 1.6;
    margin-bottom: 12px;
}

.action-card {
    border-radius: 22px;
    border: 1px solid rgba(226,232,240,0.94);
    background: #ffffff;
    box-shadow: var(--shadow-soft);
    padding: 18px;
    margin-bottom: 12px;
    animation: fadeUp .45s ease both;
}

.action-title {
    font-size: 18px;
    font-weight: 950;
    letter-spacing: -0.04em;
    color: var(--text);
    margin-bottom: 8px;
}

.action-meta {
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 9px;
}

.action-copy {
    font-size: 14px;
    line-height: 1.65;
    color: var(--text);
}

.surface {
    border-radius: 26px;
    border: 1px solid rgba(226,232,240,0.94);
    background: #ffffff;
    box-shadow: var(--shadow-soft);
    padding: 24px;
    animation: fadeUp .5s ease both;
}

.danger-surface {
    background: #fff7f7;
    border-color: #fecaca;
}

.reset-card {
    border-radius: 26px;
    border: 1px solid #fecaca;
    background:
        radial-gradient(circle at top right, rgba(220,38,38,0.08), transparent 32%),
        #fff7f7;
    box-shadow: var(--shadow-soft);
    padding: 24px;
    margin-top: 18px;
}

.reset-title {
    font-size: 24px;
    font-weight: 950;
    letter-spacing: -0.05em;
    color: var(--text);
    margin-bottom: 8px;
}

.reset-copy {
    font-size: 14px;
    color: var(--muted);
    line-height: 1.65;
    margin-bottom: 14px;
}

.footer-note {
    margin-top: 30px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 13px;
}

textarea {
    border-radius: 18px !important;
}

[data-testid="stDataFrame"] {
    border-radius: 20px;
    overflow: hidden;
    box-shadow: var(--shadow-soft);
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* SIDEBAR COMPACT FIX */
section[data-testid="stSidebar"] {
    padding: 2px 0 2px 8px !important;
}

section[data-testid="stSidebar"] > div {
    min-height: calc(100vh - 4px) !important;
    max-height: calc(100vh - 4px) !important;
    padding-top: 0 !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 6px !important;
    padding-left: 14px !important;
    padding-right: 14px !important;
}

.sidebar-brand {
    margin-top: 0 !important;
    margin-bottom: 12px !important;
    padding: 14px 14px 13px 14px !important;
    border-radius: 22px !important;
}

.sidebar-title-main {
    font-size: 32px !important;
    margin-top: 0 !important;
    margin-bottom: 8px !important;
}

.sidebar-subtitle {
    margin-top: 6px !important;
    font-size: 11.5px !important;
    line-height: 1.35 !important;
}

.sidebar-section-title {
    margin-top: 10px !important;
    margin-bottom: 6px !important;
}

.stButton > button {
    min-height: 46px !important;
    border-radius: 15px !important;
}

.sidebar-card {
    padding: 11px !important;
    margin-top: 7px !important;
    border-radius: 17px !important;
}

.sidebar-card-body {
    line-height: 1.45 !important;
    font-size: 12px !important;
}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "data_cleared" not in st.session_state:
    st.session_state.data_cleared = False


def set_page(page_name):
    st.session_state.page = page_name


def load_csv(path):
    if st.session_state.get("data_cleared", False):
        return pd.DataFrame()

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def format_time(path):
    if st.session_state.get("data_cleared", False):
        return "Not built yet"

    if not path.exists():
        return "Not built yet"

    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%d %b %Y, %I:%M %p")


def short_subject(value):
    text = str(value)

    replacements = {
        "Software Construction and Development": "SCD",
        "Lab: Software Construction and Development": "SCD Lab",
        "Formal Methods in Software Engineering": "Formal Methods",
        "Artificial Intelligence": "AI",
        "Information Security": "InfoSec",
        "Professional Practices": "Pro Practices",
        "Web Engineering": "Web Eng",
        "Teachings of Holy Quran": "Quran",
    }

    for full, short in replacements.items():
        text = text.replace(full, short)

    return text


def prepare_df(df):
    if df.empty:
        return df

    df = df.copy()

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
        "current_marks_percentage",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "subject" in df.columns:
        df["subject_short"] = df["subject"].apply(short_subject)
    else:
        df["subject_short"] = "Subject"

    return df


def prepare_gpa_df(df):
    if df.empty:
        return df

    df = df.copy()

    if "semester_gpa" in df.columns:
        df["semester_gpa"] = pd.to_numeric(df["semester_gpa"], errors="coerce").fillna(0)

    if "semester_order" in df.columns:
        df["semester_order"] = pd.to_numeric(df["semester_order"], errors="coerce").fillna(999999)
        df = df.sort_values("semester_order")

    if "semester_gpa" in df.columns:
        df["cumulative_gpa"] = df["semester_gpa"].expanding().mean().round(2)

    return df


def cumulative_gpa(gpa_df):
    if gpa_df.empty or "semester_gpa" not in gpa_df.columns:
        return 0

    values = pd.to_numeric(gpa_df["semester_gpa"], errors="coerce").dropna()

    if values.empty:
        return 0

    return round(float(values.mean()), 2)


def snapshot(df, gpa_df):
    if df.empty:
        base = {
            "subjects": 0,
            "high_risk": 0,
            "safe": 0,
            "avg_attendance": 0,
            "avg_marks": 0,
            "below_attendance": 0,
            "below_marks": 0,
            "missing_finals": 0,
            "absents": 0,
        }
    else:
        base = {
            "subjects": len(df),
            "high_risk": int((df["final_risk_status"] == "High Risk").sum()),
            "safe": int((df["final_risk_status"] == "Safe").sum()),
            "avg_attendance": round(df["attendance_percentage"].mean(), 2),
            "avg_marks": round(df["current_marks_percentage"].mean(), 2),
            "below_attendance": int((df["attendance_percentage"] < 80).sum()),
            "below_marks": int((df["current_marks_percentage"] < 55).sum()),
            "missing_finals": int((df["final_marks"] == 0).sum()) if "final_marks" in df.columns else 0,
            "absents": int(df["total_absent"].sum()) if "total_absent" in df.columns else 0,
        }

    base["gpa_semesters"] = len(gpa_df) if not gpa_df.empty else 0
    base["latest_gpa"] = round(float(gpa_df["semester_gpa"].iloc[-1]), 2) if not gpa_df.empty else 0
    base["cumulative_gpa"] = cumulative_gpa(gpa_df)

    return base


def raw_text_files():
    if st.session_state.get("data_cleared", False):
        return []

    if not TEXT_DUMPS_DIR.exists():
        return []

    return sorted(TEXT_DUMPS_DIR.glob("*.txt"))


def clear_local_data():
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

    try:
        st.cache_data.clear()
    except Exception:
        pass

    st.session_state.data_cleared = True


def mark_data_loaded():
    st.session_state.data_cleared = False


def page_header(kicker, title, copy):
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-kicker">{kicker}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-copy">{copy}</div>
            <div class="hero-meta-row">
                <div class="mini-chip">Local data</div>
                <div class="mini-chip">ZABDesk sync</div>
                <div class="mini-chip">80% attendance line</div>
                <div class="mini-chip">55% passing line</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def kpi(label, value, foot, tone="blue"):
    st.markdown(
        f"""
        <div class="health-card">
            <div class="health-label">{label}</div>
            <div class="health-value">{value}</div>
            <div class="health-foot"><span class="pill {tone}">{foot}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )


def fact_card(label, value, copy):
    st.markdown(
        f"""
        <div class="grid-card">
            <div class="grid-label">{label}</div>
            <div class="grid-value">{value}</div>
            <div class="grid-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def chart_open(title, copy):
    st.markdown(
        f"""
        <div class="chart-card">
            <div class="chart-title">{title}</div>
            <div class="chart-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def chart_close():
    return


def white_chart(fig, height=430):
    fig.update_layout(
        template="simple_white",
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#0f172a", size=13),
        margin=dict(l=40, r=40, t=38, b=45),
        legend_title="",
        legend=dict(
            font=dict(color="#0f172a", size=12),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#e2e8f0",
            borderwidth=1,
        ),
    )

    fig.update_xaxes(
        color="#0f172a",
        title_font=dict(color="#0f172a", size=13),
        tickfont=dict(color="#0f172a", size=12),
        linecolor="#0f172a",
        linewidth=1,
        gridcolor="#e5e7eb",
        zerolinecolor="#94a3b8",
        showline=True,
    )

    fig.update_yaxes(
        color="#0f172a",
        title_font=dict(color="#0f172a", size=13),
        tickfont=dict(color="#0f172a", size=12),
        linecolor="#0f172a",
        linewidth=1,
        gridcolor="#e5e7eb",
        zerolinecolor="#94a3b8",
        showline=True,
    )

    return fig


def render_sidebar(df, gpa_df):
    snap = snapshot(df, gpa_df)
    dashboard_ready = FINAL_DATA_PATH.exists() and not st.session_state.get("data_cleared", False)
    gpa_ready = GPA_SUMMARY_PATH.exists() and not st.session_state.get("data_cleared", False)

    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-title-main">GradeScope</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)

    if st.sidebar.button("Dashboard", key="nav_dashboard", use_container_width=True):
        set_page("dashboard")
        st.rerun()

    if st.sidebar.button("Portal Sync", key="nav_sync", use_container_width=True):
        set_page("sync")
        st.rerun()

    if st.sidebar.button("Tables", key="nav_tables", use_container_width=True):
        set_page("tables")
        st.rerun()

    if st.sidebar.button("Raw Notes", key="nav_raw", use_container_width=True):
        set_page("raw")
        st.rerun()

    if st.sidebar.button("Settings", key="nav_settings", use_container_width=True):
        set_page("settings")
        st.rerun()

    st.sidebar.markdown('<div class="sidebar-section-title">Live Facts</div>', unsafe_allow_html=True)

    st.sidebar.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-card-title">Current Dataset</div>
            <div class="sidebar-card-body">
                <span class="status-dot {'red' if not dashboard_ready else ''}"></span>
                Dashboard: {"Ready" if dashboard_ready else "Missing"}<br>
                Subjects: <b>{snap["subjects"]}</b><br>
                High risk: <b>{snap["high_risk"]}</b><br>
                Missing finals: <b>{snap["missing_finals"]}</b>
            </div>
        </div>
        
        <div class="sidebar-card">
            <div class="sidebar-card-title">Rules</div>
            <div class="sidebar-card-body">
                Attendance safe zone: <b>80%</b><br>
                Passing marks line: <b>55%</b>
            </div>
        </div>

       
        """,
        unsafe_allow_html=True
    )


def assessment_contribution_df(df):
    if df.empty:
        return pd.DataFrame(columns=["Component", "Marks"])

    components = {
        "Quiz": "quiz_marks",
        "Assignment": "assignment_marks",
        "Mid": "mid_marks",
        "Final": "final_marks",
    }

    rows = []

    for label, col in components.items():
        if col in df.columns:
            rows.append(
                {
                    "Component": label,
                    "Marks": float(pd.to_numeric(df[col], errors="coerce").fillna(0).sum()),
                }
            )

    return pd.DataFrame(rows)


def grade_distribution_df(df):
    if df.empty or "grade" not in df.columns:
        return pd.DataFrame(columns=["Grade", "Count"])

    grade_df = (
        df["grade"]
        .fillna("Not Entered")
        .replace("", "Not Entered")
        .value_counts()
        .reset_index()
    )

    grade_df.columns = ["Grade", "Count"]
    return grade_df


def subject_health_heatmap_df(df):
    if df.empty:
        return pd.DataFrame()

    data = df.copy()

    if "subject_short" not in data.columns and "subject" in data.columns:
        data["subject_short"] = data["subject"].apply(short_subject)

    total_classes = (
        pd.to_numeric(data.get("total_present", 0), errors="coerce").fillna(0)
        + pd.to_numeric(data.get("total_absent", 0), errors="coerce").fillna(0)
        + pd.to_numeric(data.get("total_late", 0), errors="coerce").fillna(0)
    )

    absent_pressure = (
        pd.to_numeric(data.get("total_absent", 0), errors="coerce").fillna(0)
        / total_classes.replace(0, pd.NA)
        * 100
    ).fillna(0)

    return pd.DataFrame(
        {
            "Subject": data["subject_short"],
            "Attendance %": pd.to_numeric(data.get("attendance_percentage", 0), errors="coerce").fillna(0),
            "Marks %": pd.to_numeric(data.get("current_marks_percentage", 0), errors="coerce").fillna(0),
            "Absence pressure %": absent_pressure.round(2),
        }
    )


def risk_map_df(df):
    if df.empty:
        return pd.DataFrame()

    columns = [
        "subject",
        "subject_short",
        "attendance_percentage",
        "current_marks_percentage",
        "total_absent",
        "final_risk_status",
        "recommendation",
    ]

    available = [col for col in columns if col in df.columns]
    return df[available].copy()


def render_gpa_section(gpa_df, cumulative_value):
    chart_open(
        "SGPA and CGPA trend",
        f"Two-line worm graph showing semester GPA and cumulative GPA. Current CGPA: {cumulative_value}"
    )

    if gpa_df.empty:
        st.markdown(
            """
            <div class="surface">
                No previous semester GPA data found yet. Run Portal Sync first.
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=gpa_df["semester"],
            y=gpa_df["semester_gpa"],
            mode="lines+markers+text",
            name="SGPA",
            line=dict(width=4, shape="spline", color="#2563eb"),
            marker=dict(size=11, color="#2563eb", line=dict(color="#ffffff", width=2)),
            text=gpa_df["semester_gpa"].round(2),
            textposition="top center",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=gpa_df["semester"],
            y=gpa_df["cumulative_gpa"],
            mode="lines+markers+text",
            name="CGPA",
            line=dict(width=4, shape="spline", color="#16a34a"),
            marker=dict(size=11, color="#16a34a", line=dict(color="#ffffff", width=2)),
            text=gpa_df["cumulative_gpa"].round(2),
            textposition="bottom center",
        )
    )

    fig.update_yaxes(range=[0, 4.1], title="GPA")
    fig.update_xaxes(title="Semester")

    st.plotly_chart(white_chart(fig, 450), use_container_width=True, config={"displayModeBar": False})
    chart_close()


def render_assessment_donut(df):
    chart_open(
        "Assessment contribution",
        "Share of currently entered marks by component."
    )

    contribution_df = assessment_contribution_df(df)

    if contribution_df.empty or contribution_df["Marks"].sum() == 0:
        st.markdown('<div class="surface">No assessment marks available yet.</div>', unsafe_allow_html=True)
        return

    fig = px.pie(contribution_df, names="Component", values="Marks", hole=0.58)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(white_chart(fig, 410), use_container_width=True, config={"displayModeBar": False})
    chart_close()


def render_grade_donut(df):
    chart_open(
        "Grade distribution",
        "Current distribution of grades across tracked subjects."
    )

    grade_df = grade_distribution_df(df)

    if grade_df.empty:
        st.markdown('<div class="surface">No grade data available yet.</div>', unsafe_allow_html=True)
        return

    fig = px.pie(grade_df, names="Grade", values="Count", hole=0.55)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(white_chart(fig, 410), use_container_width=True, config={"displayModeBar": False})
    chart_close()


def render_subject_health_heatmap(df):
    chart_open(
        "Subject health heatmap",
        "Compact subject-level view of attendance, marks, and absence pressure."
    )

    heatmap_df = subject_health_heatmap_df(df)

    if heatmap_df.empty:
        st.markdown('<div class="surface">No subject health data available yet.</div>', unsafe_allow_html=True)
        return

    metrics = ["Attendance %", "Marks %", "Absence pressure %"]

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_df[metrics].T.values,
            x=heatmap_df["Subject"],
            y=metrics,
            colorscale="RdYlGn",
            text=heatmap_df[metrics].T.round(1).values,
            texttemplate="%{text}",
            colorbar=dict(title="Value"),
        )
    )

    fig.update_xaxes(title="")
    fig.update_yaxes(title="")
    st.plotly_chart(white_chart(fig, 360), use_container_width=True, config={"displayModeBar": False})
    chart_close()


def render_distribution_box(df):
    chart_open(
        "Performance spread",
        "Distribution of attendance percentage and marks percentage across subjects."
    )

    if df.empty:
        st.markdown('<div class="surface">No distribution data available yet.</div>', unsafe_allow_html=True)
        return

    box_df = pd.DataFrame(
        {
            "Attendance %": pd.to_numeric(df.get("attendance_percentage", 0), errors="coerce").fillna(0),
            "Marks %": pd.to_numeric(df.get("current_marks_percentage", 0), errors="coerce").fillna(0),
        }
    )

    long_df = box_df.melt(var_name="Metric", value_name="Value")

    fig = px.box(long_df, x="Metric", y="Value", points="all")
    fig.update_yaxes(range=[0, 110], title="Percentage")
    fig.update_xaxes(title="")
    st.plotly_chart(white_chart(fig, 390), use_container_width=True, config={"displayModeBar": False})
    chart_close()


def render_dashboard(df, gpa_df):
    snap = snapshot(df, gpa_df)

    page_header(
        "Dashboard",
        "Academic control room",
        "A polished local dashboard for attendance, marks, GPA movement, subject health, and practical risk signals."
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        kpi("Subjects", snap["subjects"], "tracked", "blue")
    with c2:
        kpi("High Risk", snap["high_risk"], "needs action", "red")
    with c3:
        kpi("Attendance", f"{snap['avg_attendance']}%", "80% target", "green" if snap["avg_attendance"] >= 80 else "red")
    with c4:
        kpi("Marks", f"{snap['avg_marks']}%", "55% target", "green" if snap["avg_marks"] >= 55 else "red")
    with c5:
        kpi("Latest GPA", f"{snap['latest_gpa']}", "latest semester", "blue")
    with c6:
        kpi("CGPA", f"{snap['cumulative_gpa']}", f"{snap['gpa_semesters']} semesters", "green")

    st.markdown("")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        fact_card("Attendance alerts", snap["below_attendance"], "Subjects below the 80% safe attendance line.")
    with f2:
        fact_card("Marks alerts", snap["below_marks"], "Subjects below the 55% passing line.")
    with f3:
        fact_card("Missing finals", snap["missing_finals"], "Subjects where final marks are not entered yet.")
    with f4:
        fact_card("Total absents", snap["absents"], "Total absents across tracked subjects.")

    render_gpa_section(gpa_df, snap["cumulative_gpa"])

    if df.empty:
        st.markdown("")
        st.markdown('<div class="surface">No local dashboard data found. Open <b>Portal Sync</b> and run a fresh sync.</div>', unsafe_allow_html=True)
        return

    colors = {"High Risk": "#dc2626", "Safe": "#16a34a"}

    chart_open("Attendance health", "Subject attendance with the 80% safe line.")
    fig = px.bar(
        df,
        x="subject_short",
        y="attendance_percentage",
        color="final_risk_status",
        color_discrete_map=colors,
        text="attendance_percentage",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color="#000000",
        line_width=2,
        annotation_text="80% safe line",
        annotation_position="top left",
        annotation_font_color="#000000",
        annotation_font_size=12,
    )
    fig.update_yaxes(range=[0, 110], title="Attendance %")
    fig.update_xaxes(title="")
    st.plotly_chart(white_chart(fig, 430), use_container_width=True, config={"displayModeBar": False})
    chart_close()

    chart_open("Marks performance", "Current marks with the 55% passing line.")
    fig = px.bar(
        df,
        x="subject_short",
        y="current_marks_percentage",
        color="final_risk_status",
        color_discrete_map=colors,
        text="current_marks_percentage",
    )
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    fig.add_hline(
        y=55,
        line_dash="dash",
        line_color="#000000",
        line_width=2,
        annotation_text="55% passing line",
        annotation_position="top left",
        annotation_font_color="#000000",
        annotation_font_size=12,
    )
    fig.update_yaxes(range=[0, 110], title="Marks %")
    fig.update_xaxes(title="")
    st.plotly_chart(white_chart(fig, 430), use_container_width=True, config={"displayModeBar": False})
    chart_close()

    left, right = st.columns(2)

    with left:
        render_assessment_donut(df)

    with right:
        render_grade_donut(df)

    render_subject_health_heatmap(df)
    render_distribution_box(df)

    chart_open("Risk map", "Each point is a subject. Lines mark 80% attendance and 55% marks.")
    plot_df = df.copy()
    duplicates = plot_df.groupby(["attendance_percentage", "current_marks_percentage"]).cumcount()

    offset_x = [-1.5, -0.75, 0, 0.75, 1.5]
    offset_y = [1.4, -1.4, 0, 2.0, -2.0]

    plot_df["x"] = plot_df["attendance_percentage"] + duplicates.map(lambda i: offset_x[i % len(offset_x)])
    plot_df["y"] = plot_df["current_marks_percentage"] + duplicates.map(lambda i: offset_y[i % len(offset_y)])
    plot_df["size"] = 11 + plot_df["total_absent"].fillna(0) * 1.8
    plot_df["size"] = plot_df["size"].clip(11, 28)

    fig = go.Figure()

    for status, color in [("Safe", "#16a34a"), ("High Risk", "#dc2626")]:
        sub = plot_df[plot_df["final_risk_status"] == status]

        if sub.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=sub["x"],
                y=sub["y"],
                mode="markers+text",
                text=sub["subject_short"],
                textposition="middle right",
                name=status,
                marker=dict(
                    size=sub["size"],
                    color=color,
                    opacity=0.88,
                    line=dict(color="#ffffff", width=2),
                ),
                customdata=sub[["subject", "attendance_percentage", "current_marks_percentage", "total_absent"]],
                hovertemplate="<b>%{customdata[0]}</b><br>Attendance: %{customdata[1]:.1f}%<br>Marks: %{customdata[2]:.0f}%<br>Absents: %{customdata[3]}<extra></extra>",
            )
        )

    fig.add_vline(x=80, line_dash="dash", line_color="#000000", line_width=2)
    fig.add_hline(y=55, line_dash="dash", line_color="#000000", line_width=2)
    fig.update_xaxes(range=[0, 110], title="Attendance %")
    fig.update_yaxes(range=[-5, 110], title="Marks %")
    st.plotly_chart(white_chart(fig, 390), use_container_width=True, config={"displayModeBar": False})
    chart_close()

    st.markdown("### Priority action plan")

    risky = df[df["final_risk_status"] == "High Risk"].sort_values(
        ["attendance_percentage", "current_marks_percentage"]
    )

    if risky.empty:
        st.markdown('<div class="surface">No high-risk subjects are currently present in the local dataset.</div>', unsafe_allow_html=True)
    else:
        for _, row in risky.iterrows():
            st.markdown(
                f"""
                <div class="action-card">
                    <div class="action-title">{row['subject']}</div>
                    <div class="action-meta">
                        Attendance: <b>{row['attendance_percentage']:.1f}%</b> |
                        Marks: <b>{row['current_marks_percentage']:.0f}%</b> |
                        Absents: <b>{int(row['total_absent'])}</b>
                    </div>
                    <div class="action-copy">{row['recommendation']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def show_table(title, copy, table_df):
    chart_open(title, copy)

    if table_df.empty:
        st.markdown('<div class="surface">No data available.</div>', unsafe_allow_html=True)
    else:
        st.dataframe(table_df, use_container_width=True, hide_index=True)

    chart_close()


def render_tables(df, gpa_df):
    page_header(
        "Tables",
        "Source data library",
        "Every dashboard visual has a clean source table here, ordered exactly how the dashboard uses it."
    )

    show_table("1. SGPA and CGPA trend table", "Data used for the SGPA and CGPA worm graph.", gpa_df)
    show_table("2. Assessment contribution table", "Data used for the assessment contribution donut chart.", assessment_contribution_df(df))
    show_table("3. Grade distribution table", "Data used for the grade distribution donut chart.", grade_distribution_df(df))
    show_table("4. Subject health heatmap table", "Data used for the subject health heatmap.", subject_health_heatmap_df(df))

    distribution_table = pd.DataFrame()

    if not df.empty:
        distribution_table = pd.DataFrame(
            {
                "subject": df["subject"] if "subject" in df.columns else df["subject_short"],
                "attendance_percentage": pd.to_numeric(df.get("attendance_percentage", 0), errors="coerce").fillna(0),
                "current_marks_percentage": pd.to_numeric(df.get("current_marks_percentage", 0), errors="coerce").fillna(0),
            }
        )

    show_table("5. Performance spread table", "Data used for the performance spread box plot.", distribution_table)

    attendance_table = pd.DataFrame()

    if not df.empty:
        cols = ["subject", "attendance_percentage", "total_present", "total_absent", "total_late", "attendance_risk"]
        attendance_table = df[[col for col in cols if col in df.columns]]

    show_table("6. Attendance chart table", "Data used for the attendance health chart.", attendance_table)

    marks_table = pd.DataFrame()

    if not df.empty:
        cols = [
            "subject",
            "quiz_marks",
            "assignment_marks",
            "mid_marks",
            "final_marks",
            "total_obtained_marks",
            "current_marks_percentage",
            "grade",
            "reason",
        ]
        marks_table = df[[col for col in cols if col in df.columns]]

    show_table("7. Marks chart table", "Data used for the marks performance chart.", marks_table)
    show_table("8. Risk map table", "Data used for the attendance versus marks risk map.", risk_map_df(df))

    priority_table = pd.DataFrame()

    if not df.empty:
        risky = df[df["final_risk_status"] == "High Risk"].copy()
        cols = ["subject", "attendance_percentage", "current_marks_percentage", "total_absent", "recommendation"]
        priority_table = risky[[col for col in cols if col in risky.columns]]

    show_table("9. Priority action table", "Subjects currently flagged as high risk.", priority_table)
    show_table("10. Final merged dashboard table", "Complete merged dataset used by the dashboard.", df)
    show_table("11. GPA course table", "Course-level grade rows extracted from previous semester result pages.", load_csv(GPA_COURSES_PATH))
    show_table("12. Attendance parser output", "Raw attendance summary CSV created by the attendance parser.", load_csv(ATTENDANCE_PATH))
    show_table("13. Marks parser output", "Raw marks summary CSV created by the marks parser.", load_csv(MARKS_PATH))


def run_step(title, command):
    st.markdown(f"#### {title}")
    output_box = st.empty()
    logs = ""

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=ROOT,
    )

    for line in iter(process.stdout.readline, ""):
        logs += line
        output_box.code(logs, language="bash")

    process.stdout.close()
    process.wait()

    if process.returncode == 0:
        st.success(f"{title} completed.")
        return True

    st.error(f"{title} failed.")
    return False


def render_sync():
    page_header(
        "Portal Sync",
        "Fresh ZABDesk capture",
        "Open ZABDesk, log in manually, then GradeScope captures attendance, marks, previous semester GPA, and rebuilds the local dataset."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        fact_card("Step 1", "Open", "The portal opens in a browser window.")
    with c2:
        fact_card("Step 2", "Capture", "Attendance, marks, and previous GPA pages are saved locally.")
    with c3:
        fact_card("Step 3", "Build", "Parsed data becomes dashboard-ready CSV files.")

    st.markdown("")

    if st.button("Start live portal sync", key="start_sync"):
        mark_data_loaded()

        if not run_step("Step 1 | Portal Sync", [sys.executable, "scripts/portal_scraper.py"]):
            return

        if not run_step("Step 2 | Parse Attendance", [sys.executable, "scripts/parse_attendance.py"]):
            return

        if not run_step("Step 3 | Parse Marks", [sys.executable, "scripts/parse_marks.py"]):
            return

        if not run_step("Step 4 | Parse Previous Semester GPA", [sys.executable, "scripts/parse_gpa.py"]):
            return

        if not run_step("Step 5 | Build Dataset", [sys.executable, "scripts/merge_dashboard.py"]):
            return

        mark_data_loaded()
        st.success("Sync completed. Open the dashboard to view refreshed data.")
        st.balloons()


def render_raw():
    page_header(
        "Raw Notes",
        "Captured portal text",
        "The rough captured text from the portal before cleaning, parsing, and dashboard shaping."
    )

    files = raw_text_files()

    if not files:
        st.markdown('<div class="surface">No raw sync text found. Run Portal Sync first.</div>', unsafe_allow_html=True)
        return

    selected = st.selectbox("Select raw text file", [file.name for file in files])
    path = TEXT_DUMPS_DIR / selected
    text = path.read_text(encoding="utf-8", errors="ignore")

    st.text_area("Raw captured text", text, height=560)
    st.download_button("Download selected text", text.encode("utf-8"), selected, "text/plain")

    if SYNC_LOG_PATH.exists():
        st.markdown("### Latest sync log")
        st.text_area("Sync log", SYNC_LOG_PATH.read_text(encoding="utf-8", errors="ignore"), height=260)


def render_settings():
    page_header(
        "Settings",
        "Data controls",
        "Reset local dashboard data before a fresh run or when you want a clean state."
    )

    dashboard_ready = FINAL_DATA_PATH.exists() and not st.session_state.get("data_cleared", False)
    gpa_ready = GPA_SUMMARY_PATH.exists() and not st.session_state.get("data_cleared", False)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            <div class="surface">
                <b>Clear local data removes:</b><br><br>
                • merged dashboard CSV<br>
                • attendance summary CSV<br>
                • marks summary CSV<br>
                • GPA summary CSV<br>
                • GPA course CSV<br>
                • raw portal captures<br>
                • raw text dumps<br><br>
                It does not delete scripts, notebooks, setup files, requirements, or charts.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="surface danger-surface">
                <b>Current local state</b><br><br>
                Merged dashboard: {"Ready" if dashboard_ready else "Missing"}<br>
                Attendance summary: {"Ready" if ATTENDANCE_PATH.exists() and not st.session_state.get("data_cleared", False) else "Missing"}<br>
                Marks summary: {"Ready" if MARKS_PATH.exists() and not st.session_state.get("data_cleared", False) else "Missing"}<br>
                GPA summary: {"Ready" if gpa_ready else "Missing"}<br>
                Raw text files: {len(raw_text_files())}<br>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="reset-card">
            <div class="reset-title">Reset loaded dashboard data</div>
            <div class="reset-copy">
                Use this before a fresh ZABDesk scrape if you want the dashboard to start from zero.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    confirm = st.checkbox("Confirm reset and clear the current local data", key="confirm_clear_data")

    if st.button("Clear all local data", key="clear_data", use_container_width=True):
        if not confirm:
            st.toast("Confirm the reset first.", icon="⚠️")
            st.warning("Please tick the confirmation checkbox before clearing data.")
        else:
            clear_local_data()
            st.toast("Local data cleared.", icon="✅")
            st.success("Local data cleared. Dashboard stats are now reset.")
            set_page("dashboard")
            st.rerun()


dashboard_df = prepare_df(load_csv(FINAL_DATA_PATH))
gpa_df = prepare_gpa_df(load_csv(GPA_SUMMARY_PATH))

render_sidebar(dashboard_df, gpa_df)

if st.session_state.page == "dashboard":
    render_dashboard(dashboard_df, gpa_df)
elif st.session_state.page == "sync":
    render_sync()
elif st.session_state.page == "tables":
    render_tables(dashboard_df, gpa_df)
elif st.session_state.page == "raw":
    render_raw()
elif st.session_state.page == "settings":
    render_settings()

st.markdown(
    """
    <div class="footer-note">
        GradeScope runs locally. Keep real portal captures and academic data private.
    </div>
    """,
    unsafe_allow_html=True,
)
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
    --bg: #f6f8fb;
    --panel: #ffffff;
    --panel-soft: #f9fbfc;
    --text: #0f172a;
    --muted: #64748b;
    --line: #e2e8f0;
    --blue: #2563eb;
    --blue-soft: #eff6ff;
    --green: #16a34a;
    --green-soft: #ecfdf3;
    --red: #dc2626;
    --red-soft: #fef2f2;
    --amber: #d97706;
    --amber-soft: #fffbeb;
    --purple: #7c3aed;
    --shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
    --shadow-soft: 0 10px 28px rgba(15, 23, 42, 0.06);
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

.stApp {
    background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 26%),
        radial-gradient(circle at top right, rgba(22, 163, 74, 0.10), transparent 28%),
        var(--bg);
    color: var(--text);
}

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1340px;
}

section[data-testid="stSidebar"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0 4px 8px !important;
}

section[data-testid="stSidebar"] > div {
    background: rgba(255,255,255,0.94);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: 28px;
    box-shadow: var(--shadow);
    margin: 0;
    min-height: calc(100vh - 8px);
    max-height: calc(100vh - 8px);
    overflow: visible !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 8px 18px 14px 18px !important;
}

[data-testid="stSidebarCollapseButton"] {
    color: var(--text) !important;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text);
    letter-spacing: -0.03em;
}

div[data-testid="stButton"] {
    width: 100%;
}

.stButton {
    width: 100%;
}

.stButton > button {
    width: 100% !important;
    min-height: 54px;
    border-radius: 17px;
    border: 1px solid var(--line);
    background: #ffffff;
    color: var(--text);
    font-weight: 800;
    font-size: 14px;
    text-align: left;
    justify-content: flex-start;
    padding-left: 18px;
    box-shadow: 0 8px 20px rgba(15,23,42,0.04);
    transition: all 0.18s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    border-color: #bfdbfe;
    background: #f8fbff;
    box-shadow: 0 14px 30px rgba(15,23,42,0.08);
}

.stButton > button:active {
    transform: translateY(0px);
}

[data-testid="stDownloadButton"] button {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 20px rgba(15,23,42,0.04) !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: #f8fbff !important;
    color: #0f172a !important;
    border-color: #bfdbfe !important;
}

[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span {
    color: #0f172a !important;
    font-weight: 700 !important;
}

.sidebar-title-main {
    font-size: 34px;
    font-weight: 950;
    letter-spacing: -0.07em;
    color: #0f172a;
    line-height: 1;
    margin-top: 0 !important;
    padding-top: 0 !important;
    margin-bottom: 18px !important;
    animation: fadeUp .45s ease both;
}

.sidebar-section-title {
    font-size: 11px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin: 18px 2px 9px 2px;
}

.sidebar-card {
    border: 1px solid var(--line);
    background: rgba(249,251,252,0.85);
    border-radius: 18px;
    padding: 13px;
    margin-top: 9px;
    animation: fadeUp .5s ease both;
}

.sidebar-card-title {
    font-size: 11px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 8px;
}

.sidebar-card-body {
    font-size: 13px;
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
}

.status-dot.red {
    background: var(--red);
}

.page-head {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: flex-start;
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
    font-weight: 850;
    margin-bottom: 12px;
}

.page-title {
    font-size: clamp(36px, 5vw, 58px);
    line-height: 0.98;
    font-weight: 900;
    letter-spacing: -0.06em;
    color: var(--text);
}

.page-copy {
    max-width: 780px;
    margin-top: 12px;
    color: var(--muted);
    font-size: 16px;
    line-height: 1.65;
}

.health-card {
    min-height: 128px;
    border-radius: 22px;
    border: 1px solid var(--line);
    background: rgba(255,255,255,0.92);
    box-shadow: var(--shadow-soft);
    padding: 20px;
    animation: fadeUp .5s ease both;
    transition: all .18s ease;
}

.health-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow);
}

.health-label {
    font-size: 12px;
    font-weight: 900;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.11em;
    margin-bottom: 12px;
}

.health-value {
    font-size: 38px;
    line-height: 1;
    font-weight: 900;
    letter-spacing: -0.05em;
    color: var(--text);
}

.health-foot {
    margin-top: 12px;
}

.pill {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 7px 10px;
    font-size: 12px;
    font-weight: 800;
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
    border-radius: 22px;
    border: 1px solid var(--line);
    background: #ffffff;
    box-shadow: var(--shadow-soft);
    padding: 18px;
    min-height: 145px;
    animation: fadeUp .5s ease both;
}

.grid-label {
    font-size: 12px;
    font-weight: 900;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 10px;
}

.grid-value {
    font-size: 28px;
    font-weight: 900;
    letter-spacing: -0.04em;
    color: var(--text);
    margin-bottom: 8px;
}

.grid-copy {
    color: var(--muted);
    font-size: 14px;
    line-height: 1.55;
}

.chart-card {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
    margin-top: 28px;
    margin-bottom: 10px;
    animation: fadeUp .5s ease both;
}

.chart-title {
    font-size: 30px;
    font-weight: 950;
    letter-spacing: -0.06em;
    color: var(--text);
    margin-bottom: 6px;
}

.chart-copy {
    font-size: 15px;
    color: var(--muted);
    line-height: 1.55;
    margin-bottom: 12px;
}

.action-card {
    border-radius: 20px;
    border: 1px solid var(--line);
    background: #ffffff;
    box-shadow: var(--shadow-soft);
    padding: 17px;
    margin-bottom: 12px;
    animation: fadeUp .45s ease both;
}

.action-title {
    font-size: 17px;
    font-weight: 900;
    letter-spacing: -0.03em;
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
    line-height: 1.6;
    color: var(--text);
}

.surface {
    border-radius: 24px;
    border: 1px solid var(--line);
    background: #ffffff;
    box-shadow: var(--shadow-soft);
    padding: 22px;
    animation: fadeUp .5s ease both;
}

.danger-surface {
    background: #fff7f7;
    border-color: #fecaca;
}

.reset-card {
    border-radius: 24px;
    border: 1px solid #fecaca;
    background: #fff7f7;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
    padding: 22px;
    margin-top: 18px;
}

.reset-title {
    font-size: 22px;
    font-weight: 900;
    letter-spacing: -0.04em;
    color: #0f172a;
    margin-bottom: 8px;
}

.reset-copy {
    font-size: 14px;
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 14px;
}

.footer-note {
    margin-top: 28px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 13px;
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    box-shadow: var(--shadow-soft);
}

textarea {
    border-radius: 16px !important;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(14px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
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


def snapshot(df):
    if df.empty:
        return {
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

    return {
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


def raw_text_files():
    if st.session_state.get("data_cleared", False):
        return []

    if not TEXT_DUMPS_DIR.exists():
        return []

    return sorted(TEXT_DUMPS_DIR.glob("*.txt"))


def clear_local_data():
    for path in [FINAL_DATA_PATH, ATTENDANCE_PATH, MARKS_PATH]:
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


def render_sidebar(df):
    snap = snapshot(df)
    dashboard_ready = FINAL_DATA_PATH.exists() and not st.session_state.get("data_cleared", False)

    st.sidebar.markdown(
        """
        <div class="sidebar-title-main">GradeScope</div>
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

        <div class="sidebar-card">
            <div class="sidebar-card-title">Last Build</div>
            <div class="sidebar-card-body">
                {format_time(FINAL_DATA_PATH)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def page_header(kicker, title, copy):
    st.markdown(
        f"""
        <div class="page-head">
            <div>
                <div class="page-kicker">{kicker}</div>
                <div class="page-title">{title}</div>
                <div class="page-copy">{copy}</div>
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
        margin=dict(l=36, r=36, t=35, b=40),
        legend_title="",
        legend=dict(
            font=dict(color="#0f172a", size=12),
            bgcolor="rgba(255,255,255,0.8)",
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


def render_dashboard(df):
    snap = snapshot(df)

    page_header(
        "Dashboard",
        "Academic overview",
        "A clean view of your current attendance, marks, risk status, and subjects that need attention."
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi("Subjects", snap["subjects"], "tracked", "blue")
    with c2:
        kpi("High Risk", snap["high_risk"], "needs action", "red")
    with c3:
        kpi("Safe", snap["safe"], "stable", "green")
    with c4:
        kpi("Attendance", f"{snap['avg_attendance']}%", "80% target", "green" if snap["avg_attendance"] >= 80 else "red")
    with c5:
        kpi("Marks", f"{snap['avg_marks']}%", "55% target", "green" if snap["avg_marks"] >= 55 else "red")

    st.markdown("")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        fact_card("Attendance alerts", snap["below_attendance"], "Subjects currently below the 80% safe attendance line.")
    with f2:
        fact_card("Marks alerts", snap["below_marks"], "Subjects currently below the 55% passing line.")
    with f3:
        fact_card("Missing finals", snap["missing_finals"], "Subjects where final marks are not entered yet.")
    with f4:
        fact_card("Total absents", snap["absents"], "Total absents counted across tracked subjects.")

    if df.empty:
        st.markdown("")
        st.markdown(
            """
            <div class="surface">
                No local dashboard data found. Open <b>Portal Sync</b> and run a fresh sync.
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    colors = {
        "High Risk": "#dc2626",
        "Safe": "#16a34a",
    }

    st.markdown("")

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
        annotation_font_size=12
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
        annotation_font_size=12
    )
    fig.update_yaxes(range=[0, 110], title="Marks %")
    fig.update_xaxes(title="")
    st.plotly_chart(white_chart(fig, 430), use_container_width=True, config={"displayModeBar": False})
    chart_close()

    chart_open("Risk breakdown", "Counts behind the current risk state.")
    risk_df = pd.DataFrame(
        {
            "Metric": ["High Risk", "Safe", "Below 80% Attendance", "Below 55% Marks"],
            "Count": [snap["high_risk"], snap["safe"], snap["below_attendance"], snap["below_marks"]],
        }
    )

    fig = px.bar(
        risk_df,
        y="Metric",
        x="Count",
        orientation="h",
        color="Metric",
        text="Count",
        color_discrete_map={
            "High Risk": "#dc2626",
            "Safe": "#16a34a",
            "Below 80% Attendance": "#d97706",
            "Below 55% Marks": "#7c3aed",
        },
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(range=[0, max(1, risk_df["Count"].max() + 1)], title="")
    fig.update_yaxes(title="")
    st.plotly_chart(white_chart(fig, 350), use_container_width=True, config={"displayModeBar": False})
    chart_close()

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
                    opacity=0.86,
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
        st.markdown(
            """
            <div class="surface">
                No high-risk subjects are currently present in the local dataset.
            </div>
            """,
            unsafe_allow_html=True
        )
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
                unsafe_allow_html=True
            )


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
        "Refresh local data",
        "Open ZABDesk, log in manually, then let GradeScope capture, parse, and rebuild the dashboard dataset."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        fact_card("Step 1", "Open", "GradeScope opens the portal in a browser window.")
    with c2:
        fact_card("Step 2", "Capture", "Attendance and marks pages are captured locally.")
    with c3:
        fact_card("Step 3", "Build", "Parsed data is merged into the dashboard dataset.")

    st.markdown("")

    if st.button("Start live portal sync", key="start_sync"):
        mark_data_loaded()

        if not run_step("Step 1 | Portal Sync", [sys.executable, "scripts/portal_scraper.py"]):
            return

        if not run_step("Step 2 | Parse Attendance", [sys.executable, "scripts/parse_attendance.py"]):
            return

        if not run_step("Step 3 | Parse Marks", [sys.executable, "scripts/parse_marks.py"]):
            return

        if not run_step("Step 4 | Build Dataset", [sys.executable, "scripts/merge_dashboard.py"]):
            return

        mark_data_loaded()
        st.success("Sync completed. Open the dashboard to view refreshed data.")
        st.balloons()


def render_raw():
    page_header(
        "Raw Notes",
        "Captured portal text",
        "Rough text captured from the portal before it is cleaned, parsed, and merged."
    )

    files = raw_text_files()

    if not files:
        st.markdown(
            """
            <div class="surface">
                No raw sync text found. Run Portal Sync first.
            </div>
            """,
            unsafe_allow_html=True
        )
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
        "Clear local data before a fresh run or when you want to reset the dashboard state."
    )

    dashboard_ready = FINAL_DATA_PATH.exists() and not st.session_state.get("data_cleared", False)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            <div class="surface">
                <b>Clear local data removes:</b><br><br>
                • merged dashboard CSV<br>
                • attendance summary CSV<br>
                • marks summary CSV<br>
                • raw portal captures<br>
                • raw text dumps<br><br>
                It does not delete scripts, notebooks, setup files, requirements, or charts.
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="surface danger-surface">
                <b>Current local state</b><br><br>
                Merged dashboard: {"Ready" if dashboard_ready else "Missing"}<br>
                Attendance summary: {"Ready" if ATTENDANCE_PATH.exists() and not st.session_state.get("data_cleared", False) else "Missing"}<br>
                Marks summary: {"Ready" if MARKS_PATH.exists() and not st.session_state.get("data_cleared", False) else "Missing"}<br>
                Raw text files: {len(raw_text_files())}<br>
            </div>
            """,
            unsafe_allow_html=True
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
        unsafe_allow_html=True
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


df = prepare_df(load_csv(FINAL_DATA_PATH))
render_sidebar(df)

if st.session_state.page == "dashboard":
    render_dashboard(df)
elif st.session_state.page == "sync":
    render_sync()
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
    unsafe_allow_html=True
)
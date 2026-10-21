from __future__ import annotations

import hmac
import os
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "employees.csv"
REQUIRED_COLUMNS = {
    "employee_id",
    "name",
    "department",
    "role",
    "date",
    "tasks_completed",
    "hours_worked",
    "rating",
    "projects",
    "absences",
}

st.set_page_config(
    page_title="TeamPulse | Workforce Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      /* TeamPulse visual system: calm light canvas, crisp cards and accessible contrast. */
      .stApp { background: #f4f7fb; }
      [data-testid="stAppViewContainer"] { background: #f4f7fb; }
      [data-testid="stHeader"] { background: rgba(244, 247, 251, .92); }
      .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }
      .tp-eyebrow {
        text-transform: uppercase; letter-spacing: .15em; font-size: .70rem;
        font-weight: 800; color: #625bf6; margin-bottom: .45rem;
      }
      .tp-title {
        font-size: clamp(2rem, 3vw, 2.65rem); line-height: 1.12; font-weight: 800;
        letter-spacing: -.045em; color: #172033; margin: 0;
      }
      .tp-subtitle { color: #64748b; margin-top: .55rem; margin-bottom: 1.4rem; font-size: 1rem; }
      [data-testid="stSidebar"] {
        background: #edf1ff; border-right: 1px solid #dfe5f3;
      }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 { color: #18233b; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
      [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #64718a; }
      [data-testid="stSidebar"] label,
      [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #33415c !important; }
      [data-testid="stMetric"] {
        background: #ffffff; border: 1px solid #e2e8f2; border-radius: 16px;
        padding: 1.05rem 1.1rem; box-shadow: 0 5px 18px rgba(23, 32, 51, .045);
        min-height: 112px;
      }
      [data-testid="stMetricLabel"] { color: #68758b !important; font-size: .83rem; font-weight: 650; }
      [data-testid="stMetricValue"] { color: #15213a !important; font-weight: 800; letter-spacing: -.035em; }
      [data-testid="stMetricDelta"] { font-size: .78rem; }
      [data-testid="stForm"] {
        border: 1px solid #e2e8f2; border-radius: 18px; padding: 1.3rem;
        background: #ffffff; box-shadow: 0 12px 34px rgba(23, 32, 51, .06);
      }
      [data-testid="stDataFrame"] { border: 1px solid #e2e8f2; border-radius: 14px; overflow: hidden; }
      [data-testid="stDownloadButton"] button,
      [data-testid="stFormSubmitButton"] button { border-radius: 10px; font-weight: 650; }
      div[data-baseweb="input"] > div,
      div[data-baseweb="select"] > div,
      div[data-baseweb="textarea"] > div { border-radius: 10px; }
      div[data-testid="stVerticalBlock"] > div:has(> [data-testid="stPlotlyChart"]),
      div[data-testid="stVerticalBlock"] > div:has(> [data-testid="stImage"]) { border-radius: 16px; }
      .tp-muted { font-size: .85rem; color: #8490a4; }
      h2, h3 { letter-spacing: -.025em; color: #1c2942; }
      hr { border-color: #e2e8f0; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _credentials() -> tuple[str | None, str | None]:
    """Read demo credentials from environment variables or Streamlit secrets."""
    username = os.getenv("TEAMPULSE_USERNAME")
    password = os.getenv("TEAMPULSE_PASSWORD")
    try:
        auth = st.secrets.get("auth", {})
        username = username or auth.get("username")
        password = password or auth.get("password")
    except Exception:
        # Streamlit raises when no local secrets file has been configured.
        pass
    return username, password


@st.cache_data(show_spinner="Loading the sample workforce data…")
def load_data(path: str) -> pd.DataFrame:
    """Load and prepare the bundled sample dataset."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find the sample dataset: {file_path}")
    data = pd.read_csv(file_path)
    missing = sorted(REQUIRED_COLUMNS.difference(data.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["tasks_completed"] = pd.to_numeric(data["tasks_completed"], errors="coerce")
    data["hours_worked"] = pd.to_numeric(data["hours_worked"], errors="coerce")
    data["rating"] = pd.to_numeric(data["rating"], errors="coerce")
    data["projects"] = pd.to_numeric(data["projects"], errors="coerce")
    data["absences"] = pd.to_numeric(data["absences"], errors="coerce")
    data = data.dropna(subset=["date", "tasks_completed", "hours_worked", "rating"])
    data["tasks_per_hour"] = data["tasks_completed"].div(
        data["hours_worked"].where(data["hours_worked"] > 0)
    )
    return data


def _show_login() -> None:
    username_expected, password_expected = _credentials()
    st.markdown('<div class="tp-eyebrow">WORKFORCE ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="tp-title">TeamPulse</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="tp-subtitle">A clearer view of team trends, workload and productivity.</p>',
        unsafe_allow_html=True,
    )
    center = st.columns([1.1, 1, 1.1])[1]
    with center:
        st.subheader("Sign in to your workspace")
        st.caption("Local portfolio demo · sample data only")
        if not username_expected or not password_expected:
            st.warning(
                "Login is not configured yet. Create `.streamlit/secrets.toml` using the "
                "example file, then restart the app."
            )
            st.code("cp .streamlit/secrets.toml.example .streamlit/secrets.toml", language="bash")
            st.stop()
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            username_ok = hmac.compare_digest(username, str(username_expected))
            password_ok = hmac.compare_digest(password, str(password_expected))
            if username_ok and password_ok:
                st.session_state["teampulse_authenticated"] = True
                st.rerun()
            else:
                st.error("Those credentials did not match. Please try again.")
    st.markdown(
        "<p class='tp-muted' style='text-align:center;margin-top:1.5rem'>"
        "Demo authentication is intended for local portfolio review only; "
        "it is not production security.</p>",
        unsafe_allow_html=True,
    )


def _employee_summary(data: pd.DataFrame) -> pd.DataFrame:
    summary = (
        data.groupby(["employee_id", "name", "department", "role"], as_index=False)
        .agg(
            tasks_total=("tasks_completed", "sum"),
            hours_total=("hours_worked", "sum"),
            avg_rating=("rating", "mean"),
            projects_total=("projects", "sum"),
            absence_days=("absences", "sum"),
        )
    )
    summary["tasks_per_hour"] = summary["tasks_total"].div(
        summary["hours_total"].where(summary["hours_total"] > 0)
    )
    summary["hours_total"] = summary["hours_total"].round(1)
    summary["avg_rating"] = summary["avg_rating"].round(2)
    summary["tasks_per_hour"] = summary["tasks_per_hour"].round(2)
    return summary.sort_values("tasks_total", ascending=False)


def _render_dashboard(raw_data: pd.DataFrame) -> None:
    st.sidebar.markdown("## TeamPulse")
    st.sidebar.caption("Workforce insights · sample workspace")
    st.sidebar.divider()
    if st.sidebar.button("Sign out", use_container_width=True):
        st.session_state["teampulse_authenticated"] = False
        st.rerun()

    st.markdown('<div class="tp-eyebrow">WORKFORCE OVERVIEW</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="tp-title">Team insights at a glance</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="tp-subtitle">Explore workload, ratings and department-level patterns '
        "across the selected period.</p>",
        unsafe_allow_html=True,
    )

    min_date = raw_data["date"].min().date()
    max_date = raw_data["date"].max().date()
    departments = sorted(raw_data["department"].dropna().unique().tolist())
    st.sidebar.markdown("### Filters")
    selected_departments = st.sidebar.multiselect("Departments", departments, default=departments)
    date_value: Any = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    employee_query = st.sidebar.text_input("Find an employee", placeholder="Name or employee ID")
    st.sidebar.caption("Filters update the metrics and charts on this page.")

    if not selected_departments:
        st.info("Choose at least one department in the sidebar to view the data.")
        return
    if isinstance(date_value, (tuple, list)) and len(date_value) == 2:
        start_date, end_date = date_value
    elif isinstance(date_value, (tuple, list)) and len(date_value) == 1:
        start_date, end_date = date_value[0], date_value[0]
    else:
        start_date = end_date = date_value

    data = raw_data.loc[
        raw_data["department"].isin(selected_departments)
        & raw_data["date"].dt.date.between(start_date, end_date)
    ].copy()
    if employee_query.strip():
        query = employee_query.strip().casefold()
        data = data.loc[
            data["name"].astype(str).str.casefold().str.contains(query, regex=False)
            | data["employee_id"].astype(str).str.casefold().str.contains(query, regex=False)
        ]

    if data.empty:
        st.warning(
            "No records match those filters. Try a different department, date range or search term."
        )
        return

    employee_count = data["employee_id"].nunique()
    department_count = data["department"].nunique()
    task_count = int(data["tasks_completed"].sum())
    hours_count = float(data["hours_worked"].sum())
    average_rating = float(data["rating"].mean())
    task_rate = task_count / hours_count if hours_count > 0 else 0.0
    absence_rate = float(data["absences"].mean() * 100)

    kpi_cols = st.columns(5)
    kpi_cols[0].metric("Employees in view", f"{employee_count:,}")
    kpi_cols[1].metric("Departments", f"{department_count}")
    kpi_cols[2].metric("Average rating", f"{average_rating:.2f} / 5")
    kpi_cols[3].metric("Tasks per hour", f"{task_rate:.2f}")
    kpi_cols[4].metric("Absence records", f"{absence_rate:.1f}%")
    st.caption(
        f"Showing {len(data):,} daily records · {start_date:%d %b %Y} – {end_date:%d %b %Y}. "
        "Ratings are descriptive averages, not a validated performance score."
    )

    department_summary = (
        data.groupby("department", as_index=False)
        .agg(
            avg_rating=("rating", "mean"),
            tasks=("tasks_completed", "sum"),
            hours=("hours_worked", "sum"),
        )
    )
    department_summary["avg_rating"] = department_summary["avg_rating"].round(2)
    department_summary["tasks_per_hour"] = department_summary["tasks"].div(
        department_summary["hours"].where(department_summary["hours"] > 0)
    ).round(2)
    daily_source = data.assign(record_date=data["date"].dt.date)
    daily_summary = daily_source.groupby("record_date", as_index=False).agg(
        tasks=("tasks_completed", "sum"), avg_rating=("rating", "mean")
    )
    daily_summary["avg_rating"] = daily_summary["avg_rating"].round(2)

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Average rating by department")
        chart_data = department_summary.sort_values("avg_rating", ascending=True).set_index(
            "department"
        )
        fig, ax = plt.subplots(figsize=(7.2, 4.3), facecolor="#ffffff")
        ax.set_facecolor("#ffffff")
        ax.barh(chart_data.index, chart_data["avg_rating"], color="#625bf6", height=0.62)
        ax.set_xlabel("Average rating (0–5)", color="#5b6780", labelpad=10)
        ax.set_ylabel("")
        ax.tick_params(axis="both", colors="#58657b", labelsize=9)
        ax.set_xlim(0, 5)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#e4e9f2")
        ax.grid(axis="x", color="#e8edf5", linewidth=0.9)
        ax.set_axisbelow(True)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with right:
        st.subheader("Daily task volume")
        fig, ax = plt.subplots(figsize=(7.2, 4.3), facecolor="#ffffff")
        ax.set_facecolor("#ffffff")
        ax.plot(
            daily_summary["record_date"], daily_summary["tasks"], color="#10a985",
            linewidth=2.5, marker="o", markersize=3, markevery=4
        )
        ax.set_xlabel("Date", color="#5b6780", labelpad=10)
        ax.set_ylabel("Tasks completed", color="#5b6780")
        ax.tick_params(axis="both", colors="#58657b", labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines["bottom"].set_color("#e4e9f2")
        ax.grid(axis="y", color="#e8edf5", linewidth=0.9)
        fig.autofmt_xdate(rotation=25)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Work hours and completed tasks")
        fig, ax = plt.subplots(figsize=(7.2, 4.3), facecolor="#ffffff")
        ax.set_facecolor("#ffffff")
        ax.scatter(
            data["hours_worked"], data["tasks_completed"], color="#5b8def",
            alpha=0.72, s=34, edgecolors="white", linewidths=0.5
        )
        ax.set_xlabel("Hours worked", color="#5b6780", labelpad=10)
        ax.set_ylabel("Tasks completed", color="#5b6780")
        ax.tick_params(axis="both", colors="#58657b", labelsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines["bottom"].set_color("#e4e9f2")
        ax.spines["left"].set_color("#e4e9f2")
        ax.grid(color="#e8edf5", linewidth=0.9)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with right:
        st.subheader("Tasks per hour by department")
        productivity = department_summary.sort_values("tasks_per_hour", ascending=True).set_index(
            "department"
        )
        fig, ax = plt.subplots(figsize=(7.2, 4.3), facecolor="#ffffff")
        ax.set_facecolor("#ffffff")
        bar_colors = ["#625bf6", "#10a985", "#f5a524", "#eb6c8f", "#3998e5", "#8b74f8"]
        ax.barh(
            productivity.index, productivity["tasks_per_hour"],
            color=bar_colors[:len(productivity)], height=0.62
        )
        ax.set_xlabel("Tasks per hour", color="#5b6780", labelpad=10)
        ax.set_ylabel("")
        ax.tick_params(axis="both", colors="#58657b", labelsize=9)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#e4e9f2")
        ax.grid(axis="x", color="#e8edf5", linewidth=0.9)
        ax.set_axisbelow(True)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.divider()
    st.subheader("Employee snapshot")
    st.caption("Aggregated values are for exploring a synthetic dataset, not ranking real people.")
    employee_summary = _employee_summary(data)
    display_columns = [
        "employee_id", "name", "department", "role", "tasks_total", "hours_total",
        "avg_rating", "projects_total", "absence_days", "tasks_per_hour",
    ]
    st.dataframe(
        employee_summary[display_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "employee_id": st.column_config.TextColumn("Employee ID"),
            "tasks_total": st.column_config.NumberColumn("Tasks", format="%d"),
            "hours_total": st.column_config.NumberColumn("Hours", format="%.1f"),
            "avg_rating": st.column_config.NumberColumn("Avg. rating", format="%.2f"),
            "projects_total": st.column_config.NumberColumn("Project records", format="%d"),
            "absence_days": st.column_config.NumberColumn("Absence records", format="%d"),
            "tasks_per_hour": st.column_config.NumberColumn("Tasks / hour", format="%.2f"),
        },
    )
    export_left, export_right = st.columns([1, 3])
    with export_left:
        st.download_button(
            "Download employee summary CSV",
            data=employee_summary[display_columns].to_csv(index=False).encode("utf-8"),
            file_name="teampulse_employee_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with export_right:
        st.download_button(
            "Download filtered daily records CSV",
            data=data.to_csv(index=False).encode("utf-8"),
            file_name="teampulse_filtered_records.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.caption(
        "TeamPulse is an educational portfolio project. This bundled data is synthetic; "
        "do not use these metrics for compensation, promotion, disciplinary action "
        "or other real HR decisions."
    )


def main() -> None:
    if not st.session_state.get("teampulse_authenticated", False):
        _show_login()
        return
    try:
        data = load_data(str(DATA_PATH))
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        st.error(f"Unable to load the dashboard data: {exc}")
        st.stop()
    _render_dashboard(data)


if __name__ == "__main__":
    main()

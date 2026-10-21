<div align="center">

<img src="assets/team-pulse-mark.svg" alt="TeamPulse mark" width="72" />

# TeamPulse — Workforce Insights

**A practical workforce analytics dashboard built with Python, pandas, SQLite and Streamlit.**

Explore department trends, workload patterns and sample employee metrics in one place.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Analytics-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2E7D32)

</div>

TeamPulse is a small portfolio project for exploring workforce-style data. The dashboard lets you filter the sample records by date and department, inspect KPIs and charts, search for an employee ID, and export the current view to CSV. A Python/SQLite pipeline is also included for validating the CSV and producing repeatable reports from the command line.

> **Data note:** The bundled dataset is synthetic and covers January–February 2024. The dashboard is for learning and demonstration only; these metrics are not suitable for real employee evaluation or HR decisions.

## What you can do

- Review high-level metrics for the currently selected data: employees, departments, average rating, tasks per hour and absence records.
- Filter the dashboard by department, date range, employee name or employee ID.
- Compare department-level average ratings and task throughput.
- Explore the relationship between hours worked and tasks completed.
- Inspect an aggregated employee table and export either the summary or filtered daily records to CSV.
- Run the SQL + Python reporting pipeline and regenerate department summaries and charts.
- Sign into the local demo dashboard using credentials stored outside version control.

## Project structure

```text
TeamPulse-Workforce-Insights/
├── app.py                         # Streamlit dashboard and demo sign-in
├── data/
│   └── employees.csv              # Synthetic sample records
├── src/
│   ├── create_db.py               # Validate CSV and load SQLite
│   ├── analyze_performance.py     # Create summaries and charts
│   ├── queries.sql                # Department, employee and daily KPI views
│   └── utils.py                   # Shared logging, CSV and chart helpers
├── outputs/                       # Example pipeline reports and charts
├── tests/                         # Automated pipeline tests
├── .streamlit/
│   ├── config.toml                # Light theme and dashboard colors
│   └── secrets.toml.example       # Local login configuration template
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Run it locally

### 1. Install Python

Use Python 3.10 or newer. Check the installed version:

```bash
python --version
```

### 2. Open the project folder

Download the ZIP from this repository and extract it, or clone your own GitHub repository after you upload the customized version. Then open a terminal in the `TeamPulse-Workforce-Insights` folder.

### 3. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install the dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

If you only need to install the application and do not plan to run the developer checks, use `pip install -e .`.

### 5. Configure the demo login

Create your local secrets file from the example.

**macOS / Linux / Git Bash:**

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

**Windows PowerShell:**

```powershell
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Open `.streamlit/secrets.toml`. For a local demo, the template contains these starter credentials:

| Field | Demo value |
|---|---|
| Username | `analyst` |
| Password | `pulse-demo-2026` |

Change the password before you share your computer or deploy the application. The actual `secrets.toml` file is ignored by Git; do not commit real credentials to GitHub.

Environment variables can also be used instead of the `[auth]` values in the secrets file:

**macOS / Linux / Git Bash:**

```bash
export TEAMPULSE_USERNAME="analyst"
export TEAMPULSE_PASSWORD="choose-a-local-password"
```

**Windows PowerShell:**

```powershell
$env:TEAMPULSE_USERNAME = "analyst"
$env:TEAMPULSE_PASSWORD = "choose-a-local-password"
```

### 6. Start the dashboard

Run this command from the project root:

```bash
streamlit run app.py
```

Streamlit normally opens a browser tab automatically. Otherwise, open the local URL printed in the terminal, usually `http://localhost:8501`.

### 7. Log in

Enter the username and password from `.streamlit/secrets.toml` (or the environment variables). With the untouched example file, use `analyst` and `pulse-demo-2026`. Use the **Sign out** button in the sidebar to return to the login screen.

> **Authentication limitation:** This is a portfolio demo, not production authentication. It does not include user registration, password reset, role-based authorization, a database-backed user store or production session controls. Do not expose it publicly with demo credentials.

## Run the SQL + Python reporting pipeline

The dashboard reads the bundled CSV directly for easy local use. To build the SQLite database and generate the separate CSV reports and charts, open another terminal from the project root (with the virtual environment activated):

```bash
python src/create_db.py --csv data/employees.csv --db hr.db
python src/analyze_performance.py --db hr.db --sql src/queries.sql --outdir outputs
```

The pipeline writes:

```text
outputs/
├── department_kpis.csv
├── performance_summary.csv
└── charts/
    ├── avg_rating_by_department.png
    ├── performance_vs_hours.png
    └── task_completion_rate.png
```

To skip chart generation and only write the summaries:

```bash
python src/analyze_performance.py --db hr.db --sql src/queries.sql --outdir outputs --no-charts
```

## Run the tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

If you installed the optional developer dependencies, you can also run:

```bash
ruff check app.py src/ tests/
black --check src/ tests/
mypy src/
```

GitHub Actions runs the project checks for the Python versions listed in `.github/workflows/ci.yml`.

## Dataset fields

| Field | Meaning |
|---|---|
| `employee_id` | Synthetic employee identifier |
| `name` | Synthetic employee label |
| `department` | Department grouping |
| `role` | Example job role |
| `date` | Date of the daily record |
| `tasks_completed` | Tasks completed in the record |
| `hours_worked` | Hours recorded for the day |
| `rating` | Sample daily rating on a 0–5 scale |
| `projects` | Project count recorded in the source dataset |
| `absences` | `1` for an absence record, otherwise `0` |

## Notes and limitations

- The dataset is synthetic. Employee labels and metrics should not be interpreted as real people or business outcomes.
- The rating field is averaged for exploration; it is not a validated measure of performance.
- Task count and tasks per hour do not measure work quality or complexity.
- The sign-in screen is only a basic local demo gate, not a security solution for a public service.
- The command-line pipeline and dashboard have separate entry points: the dashboard reads the CSV; the SQL pipeline builds a SQLite database and creates export artifacts.

## Tech stack

Python · Streamlit · pandas · SQLite · Matplotlib · pytest · pytest-cov · Ruff · Black · mypy · GitHub Actions

## Portfolio notes

TeamPulse brings together workforce-style data exploration, department comparisons, employee-level filtering, downloadable reports, and a repeatable Python/SQLite analytics pipeline. It is intended for portfolio demonstration and learning, not for real employee evaluation or HR decisions.

For this portfolio, be ready to explain the dashboard logic, metric definitions, SQL queries, data limitations, and the changes made to the reporting workflow.

## License

MIT License. See [`LICENSE`](LICENSE) for the full text and attribution notices.

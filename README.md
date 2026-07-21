# EV Data Pipeline

A small end-to-end data engineering pipeline built around the **IEA Global EV
Outlook 2025** dataset (Global EV Data Explorer). It takes a raw Excel export,
runs it through ingestion, transformation, validation and loading, and serves
the result through an interactive dashboard.

**In one sentence:** turns a manually-downloaded IEA Excel file into a
versioned, validated, query-ready database with a self-serve dashboard on top.

## Contents

- [What this project is](#what-this-project-is)
- [Quick start](#quick-start)
- [Architecture](#architecture)
- [Data source](#data-source)
- [Project structure](#project-structure)
- [Data quality notes](#data-quality-notes)

## What this project is

This isn't just an EDA notebook — it's built to mirror how a real data
pipeline is structured at work: a raw file comes in, gets versioned,
cleaned, checked for quality problems, loaded into a queryable database,
and finally served to an end user through a dashboard. Each step is its
own script, so the pipeline can be run end-to-end with one command, or
debugged one stage at a time.

**Skills this demonstrates:**

| Area | What's shown |
|---|---|
| Ingestion | Timestamped, versioned raw-file snapshots (no silent overwrites) |
| Transformation | Column normalization, dedup, splitting actuals from forecasts |
| Data quality | Automated validation gate — bad data never reaches the database |
| Storage | Analytical querying with DuckDB instead of re-reading Excel/CSV every time |
| Orchestration | Single entry point (`main.py`) chaining all stages, fails fast on bad data |
| Serving | Interactive Streamlit dashboard reading directly from the database |

## Quick start

**1. Install dependencies**

```bash
pip install pandas duckdb streamlit plotly openpyxl
```

**2. Run the pipeline** — ingest → transform → validate → load, one command:

```bash
python src/main.py
```

Each stage prints what it did, ending with a success message:

```
=== 1. Ingest ===
Ingested: ev_data_2026-07-11_034601.xlsx
Rows: 16436, Columns: 9
...
=== 3. Validate ===
[historical] checked 14616 rows, 0 issue(s) found
[projection] checked 1808 rows, 0 issue(s) found
All checks passed.
=== 4. Load ===
Loaded table 'historical': 14616 rows
Loaded table 'projection': 1808 rows
Database ready at: ...\data\ev_data.duckdb
Pipeline completed successfully.
```

This creates/updates `data/ev_data.duckdb` — the database the dashboard
reads from. (To inspect intermediate output instead, run each stage on
its own: `python src/ingest.py`, `python src/transform.py`, `python
src/validate.py`, `python src/Load.py`.)

**3. Launch the dashboard**

```bash
python -m streamlit run src/app.py
```

Opens automatically at `http://localhost:8501`. Use the filters at the
top (parameter / mode / country) to explore:

- Trend of the selected parameter over time, broken down by powertrain
  (BEV/PHEV/FCEV)
- Top 10 countries for the selected parameter in the latest year
- Year-over-year change and country coverage as stat tiles

## Architecture

```
EV Data Explorer 2025.xlsx
        │
        ▼
   [ingest.py]     copy source file into data/raw/ with a timestamped
        │           version, log row/column counts
        ▼
  [transform.py]   rename & normalize columns, drop duplicates, split
        │           into Historical vs Projection-STEPS datasets
        ▼
  [validate.py]     schema, null, duplicate, category and range checks —
        │           pipeline stops here if data quality issues are found
        ▼
    [Load.py]       load cleaned CSVs into data/ev_data.duckdb
        │
        ▼
    [app.py]        Streamlit dashboard querying DuckDB directly
```

## Data source

- IEA Global EV Outlook 2025 — "EV data by country" (Excel)
- https://www.iea.org/data-and-statistics/data-product/global-ev-outlook-2025
- 16,436 rows covering EV stock, sales, charging points, battery demand and
  more, across 63 countries/regions and years 2010–2024 (plus 2030
  projections under the STEPS scenario)

## Project structure

```
data/
  raw/                 versioned raw Excel snapshots (from ingest.py)
  processed/            cleaned CSVs (from transform.py)
  ev_data.duckdb         queryable database (from Load.py)
src/
  ingest.py              stage 1 — versioned ingestion
  transform.py            stage 2 — clean, rename, dedupe, split
  validate.py              stage 3 — data quality checks
  Load.py                   stage 4 — load into DuckDB
  main.py                    runs all stages in order
  app.py                      Streamlit dashboard (serving layer)
EV.ipynb                 exploratory analysis notebook
```

## Data quality notes

- The Historical and Projection-STEPS categories are kept in separate
  tables — mixing them (e.g. summing by year) would blend actuals with
  2030 forecasts.
- The raw source contains 12 exact duplicate rows (India / Trucks /
  Projection-STEPS entries); `transform.py` drops them, and `validate.py`
  fails the pipeline if duplicates reappear.

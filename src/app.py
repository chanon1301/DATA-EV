"""Streamlit dashboard for the EV data pipeline (serving layer)."""
from pathlib import Path

import duckdb
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "ev_data.duckdb"

# Fixed categorical order/colors (never cycled) — from the reference palette
POWERTRAIN_COLORS = {
    "BEV": "#2a78d6",   # blue
    "PHEV": "#1baf7a",  # aqua
    "FCEV": "#eda100",  # yellow
    "EV": "#008300",    # green
}
SEQUENTIAL_BLUE = "#2a78d6"
GRIDLINE = "#e1e0d9"
AXIS = "#c3c2b7"
MUTED = "#898781"
TEXT_PRIMARY = "#0b0b0b"

st.set_page_config(page_title="EV Data Explorer", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("SELECT * FROM historical").fetchdf()
    con.close()
    return df


df = load_data()

st.title("EV Data Explorer")
st.caption("Historical EV data (IEA Global EV Outlook 2025) — served from DuckDB")

# --- Filters (one row) ---
col1, col2, col3 = st.columns(3)
with col1:
    parameter = st.selectbox("Parameter", sorted(df["parameter"].unique()), index=sorted(df["parameter"].unique()).index("EV stock"))
with col2:
    mode = st.selectbox("Mode", sorted(df["mode"].unique()))
with col3:
    countries = st.multiselect("Countries", sorted(df["country"].unique()), default=["China", "USA", "Europe"])

filtered = df[(df["parameter"] == parameter) & (df["mode"] == mode)]

# --- Stat tiles ---
latest_year = int(filtered["year"].max())
prev_year = latest_year - 1
latest_total = filtered.loc[filtered["year"] == latest_year, "value"].sum()
prev_total = filtered.loc[filtered["year"] == prev_year, "value"].sum()
yoy = ((latest_total - prev_total) / prev_total * 100) if prev_total else 0

t1, t2, t3 = st.columns(3)
t1.metric(f"Total {parameter} ({latest_year})", f"{latest_total:,.0f}")
t2.metric("YoY change", f"{yoy:+.1f}%")
t3.metric("Countries tracked", df["country"].nunique())

st.divider()

# --- Line chart: trend over years, by powertrain, for selected countries ---
st.subheader(f"{parameter} trend by powertrain")
if countries:
    trend_df = filtered[filtered["country"].isin(countries)]
    fig = go.Figure()
    for country in countries:
        for powertrain in sorted(trend_df["powertrain"].unique()):
            sub = trend_df[(trend_df["country"] == country) & (trend_df["powertrain"] == powertrain)].sort_values("year")
            if sub.empty:
                continue
            color = POWERTRAIN_COLORS.get(powertrain, MUTED)
            fig.add_trace(go.Scatter(
                x=sub["year"], y=sub["value"],
                mode="lines",
                name=f"{country} · {powertrain}",
                line=dict(width=2, color=color),
            ))
    fig.update_layout(
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
        font=dict(color=TEXT_PRIMARY),
        xaxis=dict(showgrid=False, linecolor=AXIS, title="Year"),
        yaxis=dict(showgrid=True, gridcolor=GRIDLINE, linecolor=AXIS, title=parameter),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Select at least one country to see the trend.")

# --- Bar chart: top 10 countries (magnitude -> single hue) ---
st.subheader(f"Top 10 countries by {parameter} ({latest_year})")
top10 = (
    filtered[filtered["year"] == latest_year]
    .groupby("country")["value"].sum()
    .sort_values(ascending=False)
    .head(10)
    .sort_values()
)
bar_fig = go.Figure(go.Bar(
    x=top10.values, y=top10.index, orientation="h",
    marker_color=SEQUENTIAL_BLUE,
))
bar_fig.update_layout(
    plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
    font=dict(color=TEXT_PRIMARY),
    xaxis=dict(showgrid=True, gridcolor=GRIDLINE, linecolor=AXIS, title=parameter),
    yaxis=dict(showgrid=False, linecolor=AXIS),
    margin=dict(t=10, b=10),
)
st.plotly_chart(bar_fig, use_container_width=True)

with st.expander("View raw filtered data"):
    st.dataframe(filtered, use_container_width=True)

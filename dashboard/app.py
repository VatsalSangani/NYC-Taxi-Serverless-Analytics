import streamlit as st
from datetime import date
# MUST be the first Streamlit command in the whole app
st.set_page_config(page_title="NYC Taxi DQ (Yellow)", layout="wide")

from dotenv import load_dotenv
load_dotenv()

import os

from dashboard.data import load_dq_data
from dashboard.logic import (
    is_rate,
    latest_month,
    latest_value,
    monthly_series,
    top_n_latest,
    format_value,
    risk_band,
)

from charts.kpi import render_kpi
from charts.trend import render_trend
from charts.topn import render_topn
from charts.detail import render_detail


st.title("NYC Taxi Data Quality (Yellow)")
st.caption("Athena CTAS monthly metrics → Streamlit monitoring (rates vs counts aware)")

@st.cache_data(ttl=300)
def cached_load():
    return load_dq_data()

df = cached_load()
DATA_START = os.getenv("DATA_START")
DATA_END = os.getenv("DATA_END")
# Enforce configured data window in the app layer (defensive)
if DATA_START and DATA_END:
    start_dt = date.fromisoformat(DATA_START)
    end_dt = date.fromisoformat(DATA_END)

    df = df[
        (df["month_start"] >= start_dt) &
        (df["month_start"] <= end_dt)
    ]
metrics = sorted(df["metric_name"].unique().tolist())
if not metrics:
    st.error("No metrics found in dataset.")
    st.stop()

# Read data-window config from .env (applied in Athena query within data.py)
DATA_START = os.getenv("DATA_START")
DATA_END = os.getenv("DATA_END")

if DATA_START and DATA_END:
    st.caption(
        f"Data window: {DATA_START} to {DATA_END}. "
        "Filtering is applied at query time in Athena to reduce cost and ensure relevance."
    )
else:
    st.caption(
        "Data window: not explicitly configured. Showing all available data from the source."
    )

# Controls
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    metric = st.selectbox("Metric", metrics, index=0)
with c2:
    topn = st.number_input("Top N worst columns", min_value=3, max_value=50, value=10, step=1)
with c3:
    lm = latest_month(df)
    st.write("")
    st.write("")
    st.write(f"Latest month: **{lm}**")

if lm is None:
    st.error("Could not detect latest month. Check month_start values.")
    st.stop()

# Data freshness / governance
st.caption(
    f"Data freshness: latest available month = {lm}. "
    "Metrics are produced by scheduled monthly CTAS jobs in Athena and consumed by this monitoring app."
)

# KPI
v_latest = latest_value(df, metric)
render_kpi(
    metric=metric,
    latest_month=lm,
    latest_value=v_latest,
    is_rate_fn=is_rate,
    format_value_fn=format_value,
    risk_band_fn=risk_band,
)

st.divider()

# Trend
trend_df = monthly_series(df, metric)
render_trend(metric=metric, trend_df=trend_df, is_rate_fn=is_rate)

st.divider()

# Top N worst columns (latest month)
top_df = top_n_latest(df, metric, int(topn))
render_topn(
    top_df=top_df,
    metric=metric,
    latest_month=lm,
    is_rate_fn=is_rate,
    format_value_fn=format_value,
    topn=int(topn),
)

st.divider()

# Detail table
render_detail(
    df=df,
    metric=metric,
    latest_month=lm,
    is_rate_fn=is_rate,
    format_value_fn=format_value
)

# Optional: stale-config guard (warn if latest data exceeds configured end date)
try:
    if DATA_END:
        from datetime import date
        end_dt = date.fromisoformat(DATA_END)
        if lm and lm > end_dt:
            st.warning(
                f"Configured DATA_END ({DATA_END}) is behind the latest available month ({lm}). "
                "Update DATA_END in .env if you want to include newer months."
            )
except Exception:
    # If DATA_END isn't ISO format, ignore quietly (don't break the dashboard)
    pass

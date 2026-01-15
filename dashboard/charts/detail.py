import streamlit as st
import pandas as pd

def render_detail(df: pd.DataFrame, metric: str, latest_month, is_rate_fn, format_value_fn):
    st.subheader("Detail (latest month)")

    dff = df[(df["metric_name"] == metric) & (df["month_start"] == latest_month)].copy()
    if dff.empty:
        st.info("No detail rows for latest month.")
        return

    # Sort by raw value descending
    dff = dff.sort_values("metric_value", ascending=False)
    dff["formatted"] = dff["metric_value"].apply(lambda v: format_value_fn(metric, v))

    st.dataframe(
        dff[["column_name", "metric_value", "formatted"]],
        use_container_width=True
    )

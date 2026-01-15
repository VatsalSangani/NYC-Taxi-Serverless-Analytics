import streamlit as st
import plotly.express as px
import pandas as pd

def render_topn(top_df: pd.DataFrame, metric: str, latest_month, is_rate_fn, format_value_fn, topn: int):
    st.subheader(f"Top {topn} worst columns (latest month)")
    st.caption(f"Ranking based on {latest_month} only (prevents historical dilution).")

    if top_df is None or top_df.empty:
        st.info("No latest-month rows for this metric.")
        return

    plot_df = top_df.copy()
    plot_df["label"] = plot_df["value"].apply(lambda v: format_value_fn(metric, v))

    fig = px.bar(
        plot_df.sort_values("value"),
        x="value",
        y="column_name",
        orientation="h",
        text="label",
    )
    fig.update_layout(xaxis_title="Value", yaxis_title="Column")
    if is_rate_fn(metric):
        fig.update_xaxes(tickformat=".2%")
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

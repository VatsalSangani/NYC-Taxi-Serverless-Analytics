import streamlit as st
import plotly.express as px
import pandas as pd

def render_trend(metric: str, trend_df: pd.DataFrame, is_rate_fn):
    st.subheader("Monthly trend")

    if trend_df is None or trend_df.empty:
        st.warning("No trend data for this metric.")
        return

    plot_df = trend_df.copy()
    plot_df["month_start"] = plot_df["month_start"].astype(str)

    fig = px.line(plot_df, x="month_start", y="value", markers=True)
    fig.update_layout(xaxis_title="Month", yaxis_title="Value")
    if is_rate_fn(metric):
        fig.update_yaxes(tickformat=".2%")

    st.plotly_chart(fig, use_container_width=True)

import streamlit as st

def render_kpi(
    metric: str,
    latest_month,
    latest_value,
    is_rate_fn,
    format_value_fn,
    risk_band_fn,
):
    c1, c2, c3 = st.columns([1.2, 1, 1])

    with c1:
        st.metric(
            label=f"Latest {metric} ({latest_month})",
            value=format_value_fn(metric, latest_value),
        )

    with c2:
        if is_rate_fn(metric):
            st.caption("Metric type: Rate")
            st.write("Shown as % (higher is worse).")
        else:
            st.caption("Metric type: Count")
            st.write("Shown as integer volume.")

    with c3:
        band = risk_band_fn(metric, latest_value)

        if band == "High":
            st.error("Risk level: HIGH (≥ 10%)")
        elif band == "Medium":
            st.warning("Risk level: MEDIUM (5–10%)")
        elif band == "Low":
            st.success("Risk level: LOW (< 5%)")
        elif band == "Info":
            st.info("Volume metric (no threshold)")
        else:
            st.info("Risk level: Unknown")

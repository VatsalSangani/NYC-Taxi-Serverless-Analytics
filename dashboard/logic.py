import pandas as pd

RATE_METRICS = {"null_rate", "duplicate_rate"}
COUNT_METRICS = {"row_count"}

def is_rate(metric: str) -> bool:
    return metric in RATE_METRICS

def latest_month(df: pd.DataFrame):
    if df is None or df.empty:
        return None
    return max(df["month_start"])

def format_value(metric: str, v: float) -> str:
    if v is None or pd.isna(v):
        return "—"
    if is_rate(metric):
        return f"{v:.2%}"
    return f"{v:,.0f}"

def risk_band(metric: str, value: float | None) -> str:
    """
    Ops-style risk banding.
    Not a new metric, just interpretation thresholds for rate metrics.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "Unknown"

    if metric in RATE_METRICS:
        if value >= 0.10:
            return "High"
        elif value >= 0.05:
            return "Medium"
        else:
            return "Low"

    # Counts aren't "good/bad" without business thresholds
    if metric in COUNT_METRICS:
        return "Info"

    return "Unknown"

def latest_value(df: pd.DataFrame, metric: str):
    """
    Latest-month value for the selected metric.
    Uses existing Athena metric_value; aggregation is only for display:
    - Rates: mean across rows
    - Counts: sum across rows
    """
    m = latest_month(df)
    if m is None:
        return None

    dff = df[(df["metric_name"] == metric) & (df["month_start"] == m)]
    if dff.empty:
        return None

    return float(dff["metric_value"].mean() if is_rate(metric) else dff["metric_value"].sum())

def monthly_series(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """
    Monthly trend series for the selected metric.
    - Rates: mean per month
    - Counts: sum per month
    """
    dff = df[df["metric_name"] == metric].copy()
    if dff.empty:
        return dff

    agg = "mean" if is_rate(metric) else "sum"
    out = (
        dff.groupby("month_start", as_index=False)["metric_value"]
        .agg(agg)
        .sort_values("month_start")
        .rename(columns={"metric_value": "value"})
    )
    return out

def top_n_latest(df: pd.DataFrame, metric: str, n: int) -> pd.DataFrame:
    """
    Top N worst columns for the latest month.
    - Rates: mean per column for that month
    - Counts: sum per column for that month
    """
    m = latest_month(df)
    if m is None:
        return df.head(0)

    dff = df[(df["metric_name"] == metric) & (df["month_start"] == m)].copy()
    if dff.empty:
        return dff

    agg = "mean" if is_rate(metric) else "sum"
    out = (
        dff.groupby("column_name", as_index=False)["metric_value"]
        .agg(agg)
        .sort_values("metric_value", ascending=False)
        .head(n)
        .rename(columns={"metric_value": "value"})
    )
    return out

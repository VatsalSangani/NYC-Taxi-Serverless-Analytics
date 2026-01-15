import os
import pandas as pd
import awswrangler as wr

REQUIRED_COLS = {"month_start", "metric_name", "column_name", "metric_value"}

def load_dq_data() -> pd.DataFrame:
    db = os.getenv("ATHENA_DB")
    table = os.getenv("ATHENA_TABLE")
    s3_output = os.getenv("ATHENA_S3_OUTPUT")
    workgroup = os.getenv("ATHENA_WORKGROUP") or None

    if not all([db, table, s3_output]):
        missing = [k for k in ["ATHENA_DB", "ATHENA_TABLE", "ATHENA_S3_OUTPUT"] if not os.getenv(k)]
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

    sql = f"""
    SELECT month_start, metric_name, column_name, metric_value
    FROM {db}.{table}
    """

    df = wr.athena.read_sql_query(
        sql=sql,
        database=db,
        s3_output=s3_output,
        workgroup=workgroup,
        ctas_approach=False,
    )

    # Enforce types for consistent visuals
    df["month_start"] = pd.to_datetime(df["month_start"]).dt.date
    df["metric_name"] = df["metric_name"].astype(str)
    df["column_name"] = df["column_name"].astype(str)
    df["metric_value"] = pd.to_numeric(df["metric_value"], errors="coerce")

    missing_cols = REQUIRED_COLS - set(df.columns)
    if missing_cols:
        raise RuntimeError(f"Query missing columns: {missing_cols}")

    return df

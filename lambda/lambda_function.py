import os
import json
import time
from typing import Dict, Any, List

import boto3


# ===== Config =====
DEFAULT_REGION = os.environ.get("AWS_REGION", "eu-west-2")
ATHENA_DB = os.environ.get("ATHENA_DB", "nyc_taxi_db")
ATHENA_WORKGROUP = os.environ.get("ATHENA_WORKGROUP", "primary")

# Fully qualified table name to remove any DB ambiguity
TABLE_FQN = f"{ATHENA_DB}.curated_nyc_taxi_yellow"

# Guardrails (stop expensive/abusive calls)
ALLOWED_YEAR = 2025
MAX_N = 50
MAX_WAIT_SECONDS = 30  # keep Lambda cheap


# Force region explicitly to avoid region mismatch issues
athena = boto3.client("athena", region_name=DEFAULT_REGION)


def _resp(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _wait_for_query(qid: str, timeout_s: int = MAX_WAIT_SECONDS) -> None:
    start = time.time()
    while True:
        q = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]
        state = q["Status"]["State"]

        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            if state != "SUCCEEDED":
                reason = q["Status"].get("StateChangeReason", "unknown")
                raise RuntimeError(f"{state}: {reason}")
            return

        if time.time() - start > timeout_s:
            raise TimeoutError("Athena query timed out")
        time.sleep(0.5)


def _rows_to_dicts(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    meta = result["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
    cols = [c["Name"] for c in meta]

    rows = result["ResultSet"]["Rows"]
    if not rows or len(rows) == 1:
        return []

    out = []
    for r in rows[1:]:  # skip header row
        vals = [d.get("VarCharValue") for d in r.get("Data", [])]
        out.append(dict(zip(cols, vals)))
    return out


def run_query(sql: str) -> List[Dict[str, Any]]:
    # IMPORTANT:
    # Do NOT set ResultConfiguration OutputLocation if your workgroup uses Managed Query Results.
    # Let the workgroup control results location and limits.
    resp = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": ATHENA_DB},
        WorkGroup=ATHENA_WORKGROUP,
    )
    qid = resp["QueryExecutionId"]
    _wait_for_query(qid)
    result = athena.get_query_results(QueryExecutionId=qid)
    return _rows_to_dicts(result)


def _get_path(event: Dict[str, Any]) -> str:
    # HTTP API v2 uses rawPath. REST API uses path.
    return (event.get("rawPath") or event.get("path") or "/").lower()


def _get_qs(event: Dict[str, Any]) -> Dict[str, str]:
    return event.get("queryStringParameters") or {}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    path = _get_path(event)
    qs = _get_qs(event)

    # ---- Health ----
    if path == "/health":
        return _resp(200, {"ok": True, "region": DEFAULT_REGION, "db": ATHENA_DB, "workgroup": ATHENA_WORKGROUP})

    # ---- Debug (prove what Athena sees) ----
    if path == "/debug":
        try:
            tables = run_query(f"SHOW TABLES IN {ATHENA_DB}")
            return _resp(200, {
                "ok": True,
                "region": DEFAULT_REGION,
                "db": ATHENA_DB,
                "workgroup": ATHENA_WORKGROUP,
                "tables": tables
            })
        except Exception as e:
            return _resp(500, {"ok": False, "error": str(e), "region": DEFAULT_REGION, "db": ATHENA_DB, "workgroup": ATHENA_WORKGROUP})

    # ---- Parse & validate params ----
    try:
        yr = int(qs.get("yr", str(ALLOWED_YEAR)))
        mo = int(qs.get("mo", "6"))
        n = int(qs.get("n", "10"))
    except ValueError:
        return _resp(400, {"error": "yr/mo/n must be integers"})

    if yr != ALLOWED_YEAR:
        return _resp(400, {"error": f"yr must be {ALLOWED_YEAR}"})
    if not (1 <= mo <= 12):
        return _resp(400, {"error": "mo must be between 1 and 12"})
    if not (1 <= n <= MAX_N):
        return _resp(400, {"error": f"n must be between 1 and {MAX_N}"})

    # ---- Routes ----
    if path == "/monthly-summary":
        sql = f"""
        SELECT
          yr,
          mo,
          COUNT(*) AS trips,
          ROUND(AVG(total_amount), 2) AS avg_total_amount,
          ROUND(AVG(trip_distance), 2) AS avg_trip_distance,
          ROUND(APPROX_PERCENTILE(total_amount, 0.5), 2) AS median_total_amount
        FROM {TABLE_FQN}
        WHERE yr = {yr} AND mo = {mo}
        GROUP BY yr, mo
        """
        try:
            data = run_query(sql)
            return _resp(200, {"yr": yr, "mo": mo, "data": data})
        except Exception as e:
            return _resp(500, {"error": str(e)})

    if path == "/top-pickup-zones":
        sql = f"""
        SELECT
          pulocationid,
          COUNT(*) AS trips
        FROM {TABLE_FQN}
        WHERE yr = {yr} AND mo = {mo}
        GROUP BY pulocationid
        ORDER BY trips DESC
        LIMIT {n}
        """
        try:
            data = run_query(sql)
            return _resp(200, {"yr": yr, "mo": mo, "n": n, "data": data})
        except Exception as e:
            return _resp(500, {"error": str(e)})

    # Unknown route
    return _resp(404, {"error": "not found", "path": path})

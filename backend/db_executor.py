from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DATABASE_URL, MAX_ROWS_RETURNED
import decimal
import datetime


def execute_query(sql: str) -> dict:
    """
    Executes a validated SELECT query against the database.
    Returns a dict with:
        - columns: list of column names
        - rows: list of row dicts
        - row_count: number of rows returned
    Raises an exception with a descriptive message if execution fails.
    """
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows_raw = result.fetchmany(MAX_ROWS_RETURNED)
    except SQLAlchemyError as e:
        # Re-raise with clean message (used by retry_handler)
        raise Exception(str(e)) from e

    # Serialize rows — convert non-JSON-safe types
    rows = []
    for row in rows_raw:
        serialized = {}
        for col, val in zip(columns, row):
            serialized[col] = _serialize_value(val)
        rows.append(serialized)

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
    }


def _serialize_value(val):
    """Converts DB types to JSON-safe Python primitives."""
    if val is None:
        return None
    if isinstance(val, decimal.Decimal):
        return float(val)
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.isoformat()
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return val

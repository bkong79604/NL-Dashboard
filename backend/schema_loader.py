from sqlalchemy import create_engine, text
from config import DATABASE_URL

# Schema to focus on — keeps context window manageable for smaller LLMs
TARGET_SCHEMA = "Sales"

# Only include the most useful core tables for querying
# This reduces context size and prevents the LLM from hallucinating
# columns from less-used tables
ALLOWED_TABLES = [
    "Customer",
    "SalesOrderHeader",
    "SalesOrderDetail",
    "SalesPerson",
    "SalesTerritory",
    "SpecialOffer",
    "SpecialOfferProduct",
    "Store",
]

_schema_cache: str | None = None


def _build_in_clause(items: list[str]) -> str:
    """Builds a safe SQL IN clause string from a list of whitelisted table names."""
    # Values are hardcoded in ALLOWED_TABLES, not user input, so this is safe
    quoted = ", ".join(f"'{item}'" for item in items)
    return f"({quoted})"


def load_schema() -> str:
    """
    Queries the live database INFORMATION_SCHEMA to build a compact schema
    string suitable for injection into an LLM prompt.
    Filtered to TARGET_SCHEMA and ALLOWED_TABLES only to keep context
    window manageable and reduce LLM hallucinations.
    Also includes foreign key relationships to help LLM join tables correctly.
    Results are cached in memory after the first call.
    """
    global _schema_cache
    if _schema_cache:
        return _schema_cache

    engine = create_engine(DATABASE_URL)
    tables_in = _build_in_clause(ALLOWED_TABLES)

    with engine.connect() as conn:
        # Fetch columns for allowed tables only
        col_result = conn.execute(text(f"""
            SELECT
                c.TABLE_SCHEMA,
                c.TABLE_NAME,
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.IS_NULLABLE,
                CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 'PK' ELSE '' END AS KEY_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS c
            LEFT JOIN (
                SELECT ku.TABLE_SCHEMA, ku.TABLE_NAME, ku.COLUMN_NAME
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                    ON tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                    AND tc.TABLE_SCHEMA = ku.TABLE_SCHEMA
                WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
            ) pk ON c.TABLE_SCHEMA = pk.TABLE_SCHEMA
                AND c.TABLE_NAME = pk.TABLE_NAME
                AND c.COLUMN_NAME = pk.COLUMN_NAME
            WHERE c.TABLE_SCHEMA = :schema
              AND c.TABLE_NAME IN {tables_in}
            ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
        """), {"schema": TARGET_SCHEMA})

        rows = col_result.fetchall()

        # Fetch foreign key relationships between allowed tables only
        fk_result = conn.execute(text(f"""
            SELECT
                fk.TABLE_NAME AS from_table,
                fk_col.COLUMN_NAME AS from_column,
                pk.TABLE_NAME AS to_table,
                pk_col.COLUMN_NAME AS to_column
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
            JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS fk
                ON rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME
            JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS pk
                ON rc.UNIQUE_CONSTRAINT_NAME = pk.CONSTRAINT_NAME
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE fk_col
                ON rc.CONSTRAINT_NAME = fk_col.CONSTRAINT_NAME
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE pk_col
                ON rc.UNIQUE_CONSTRAINT_NAME = pk_col.CONSTRAINT_NAME
                AND fk_col.ORDINAL_POSITION = pk_col.ORDINAL_POSITION
            WHERE fk.TABLE_SCHEMA = :schema
              AND fk.TABLE_NAME IN {tables_in}
              AND pk.TABLE_NAME IN {tables_in}
            ORDER BY fk.TABLE_NAME, fk_col.COLUMN_NAME
        """), {"schema": TARGET_SCHEMA})

        fk_rows = fk_result.fetchall()

    if not rows:
        raise RuntimeError(
            f"No tables found in schema '{TARGET_SCHEMA}'. "
            "Check that the schema name is correct and the DB user has access."
        )

    # Group columns by fully qualified table name (schema.table)
    tables: dict[str, list[str]] = {}
    for row in rows:
        schema = row[0]
        table = row[1]
        col = row[2]
        dtype = row[3]
        key = row[5]

        full_table_name = f"{schema}.{table}"
        col_def = f"  {col} ({dtype})"
        if key == "PK":
            col_def += " [PK]"

        tables.setdefault(full_table_name, []).append(col_def)

    # Format as readable schema text for the LLM prompt
    lines = [f"Database: AdventureWorks2022 | Schema: {TARGET_SCHEMA}\n"]
    lines.append(
        "IMPORTANT: Always use the full table name including schema prefix "
        "(e.g. Sales.SalesOrderHeader, not just SalesOrderHeader).\n"
        "IMPORTANT: Only use tables and columns that are explicitly listed below. "
        "Do not reference any other tables or columns.\n"
    )

    # Add table and column definitions
    for table_name, columns in tables.items():
        lines.append(f"Table: {table_name}")
        lines.extend(columns)
        lines.append("")

    # Add foreign key relationships section
    if fk_rows:
        lines.append("Foreign Key Relationships (use these to JOIN tables correctly):")
        for fk in fk_rows:
            lines.append(
                f"  {TARGET_SCHEMA}.{fk[0]}.{fk[1]} -> "
                f"{TARGET_SCHEMA}.{fk[2]}.{fk[3]}"
            )
        lines.append("")

    _schema_cache = "\n".join(lines)
    return _schema_cache


def invalidate_schema_cache():
    """Call this if you want to force a schema reload (e.g. after DB changes)."""
    global _schema_cache
    _schema_cache = None
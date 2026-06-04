import re
import sqlglot
import sqlglot.expressions as exp

# Dangerous keywords that should never appear regardless of parsing
BLOCKED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "EXEC", "EXECUTE", "SP_", "XP_", "MERGE",
    "BULK", "OPENROWSET", "OPENDATASOURCE"
]


class SQLValidationError(Exception):
    pass


def _fix_tsql_syntax(sql: str) -> str:
    """
    Fixes common non-SQL-Server syntax that LLMs tend to generate.
    Converts PostgreSQL/MySQL idioms to valid T-SQL equivalents.
    """
    # Remove NULLS FIRST / NULLS LAST (not supported in T-SQL)
    sql = re.sub(r'\bNULLS\s+(FIRST|LAST)\b', '', sql, flags=re.IGNORECASE).strip()

    # Convert LIMIT N to TOP N (move TOP into SELECT)
    limit_match = re.search(r'\bLIMIT\s+(\d+)\b', sql, flags=re.IGNORECASE)
    if limit_match:
        n = limit_match.group(1)
        # Remove the LIMIT clause
        sql = re.sub(r'\bLIMIT\s+\d+\b', '', sql, flags=re.IGNORECASE).strip()
        # Add TOP N after SELECT if not already present
        if not re.search(r'\bSELECT\s+TOP\b', sql, flags=re.IGNORECASE):
            sql = re.sub(r'\bSELECT\b', f'SELECT TOP {n}', sql, flags=re.IGNORECASE, count=1)

    # Convert OFFSET x ROWS FETCH NEXT y ROWS ONLY — already valid T-SQL, leave it
    # Convert ILIKE to LIKE (T-SQL is case-insensitive by default)
    sql = re.sub(r'\bILIKE\b', 'LIKE', sql, flags=re.IGNORECASE)

    # Remove trailing semicolons
    sql = sql.rstrip(';').strip()

    return sql


def validate_sql(sql: str) -> str:
    """
    Validates that the SQL is a safe SELECT-only statement.
    - Strips markdown code fences if the LLM accidentally included them
    - Fixes common non-T-SQL syntax automatically
    - Checks for blocked keywords
    - Parses with sqlglot to confirm it's a SELECT statement
    Returns the cleaned SQL string, or raises SQLValidationError.
    """
    # Strip markdown fences if present (LLM sometimes wraps in ```sql ... ```)
    sql = re.sub(r"```(?:sql)?", "", sql, flags=re.IGNORECASE).strip().strip("`").strip()

    # Remove any trailing semicolons
    sql = sql.rstrip(";").strip()

    if not sql:
        raise SQLValidationError("LLM returned an empty query.")

    # Fix common T-SQL syntax issues before validation
    sql = _fix_tsql_syntax(sql)

    # Block dangerous keywords via regex (case-insensitive, word boundaries)
    upper_sql = sql.upper()
    for keyword in BLOCKED_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, upper_sql):
            raise SQLValidationError(
                f"Blocked keyword detected in generated SQL: '{keyword}'. "
                "Only SELECT queries are allowed."
            )

    # Parse with sqlglot to confirm it's a valid SELECT
    try:
        statements = sqlglot.parse(sql, dialect="tsql")
    except Exception as e:
        raise SQLValidationError(f"SQL parsing failed: {e}")

    if not statements:
        raise SQLValidationError("No valid SQL statement found in LLM response.")

    if len(statements) > 1:
        raise SQLValidationError("Multiple SQL statements detected. Only a single SELECT is allowed.")

    statement = statements[0]
    if not isinstance(statement, exp.Select):
        raise SQLValidationError(
            f"Expected a SELECT statement, but got: {type(statement).__name__}. "
            "Only SELECT queries are allowed."
        )

    return sql

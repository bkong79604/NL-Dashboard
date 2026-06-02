from config import MAX_RETRY_ATTEMPTS
from prompt_builder import build_sql_prompt, build_retry_prompt
from llm_client import generate
from sql_validator import validate_sql, SQLValidationError
from db_executor import execute_query


class QueryFailedError(Exception):
    """Raised when all retry attempts are exhausted."""
    pass


def run_query_with_retry(user_query: str, schema: str) -> tuple[str, dict]:
    """
    Orchestrates the full SQL generation → validation → execution loop.
    Retries up to MAX_RETRY_ATTEMPTS times if validation or execution fails.

    Returns:
        (final_sql, query_result) on success
    Raises:
        QueryFailedError if all attempts fail
    """
    last_error = ""
    last_sql = ""

    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        # Build prompt: first attempt uses base prompt, retries include error context
        if attempt == 1:
            prompt = build_sql_prompt(user_query, schema)
        else:
            prompt = build_retry_prompt(user_query, schema, last_sql, last_error)

        # Ask LLM for SQL
        raw_response = generate(prompt)

        # Validate the SQL
        try:
            sql = validate_sql(raw_response)
        except SQLValidationError as e:
            last_sql = raw_response
            last_error = f"SQL validation error: {e}"
            print(f"[Attempt {attempt}] Validation failed: {e}")
            continue

        # Execute the SQL
        try:
            result = execute_query(sql)
            print(f"[Attempt {attempt}] Query succeeded.")
            return sql, result
        except Exception as e:
            last_sql = sql
            last_error = f"SQL execution error: {e}"
            print(f"[Attempt {attempt}] Execution failed: {e}")
            continue

    raise QueryFailedError(
        f"Query failed after {MAX_RETRY_ATTEMPTS} attempts. Last error: {last_error}"
    )

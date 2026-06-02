def build_sql_prompt(user_query: str, schema: str) -> str:
    """
    Builds the initial prompt asking the LLM to generate a SQL SELECT query.
    Uses sqlcoder's preferred prompt format for best results.
    """
    return f"""### Task
Generate a SQL SELECT query for Microsoft SQL Server (T-SQL) to answer the following question.

### Database Schema
{schema}

### Rules
- Only generate SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE or any modifying statement.
- Only use tables and columns explicitly listed in the schema above. Do not invent or assume any columns.
- Always use the full schema-prefixed table name (e.g. Sales.SalesOrderHeader, not just SalesOrderHeader).
- This is Microsoft SQL Server (T-SQL). Follow these syntax rules strictly:
  * Use TOP N instead of LIMIT N (e.g. SELECT TOP 10 ... not SELECT ... LIMIT 10)
  * Do NOT use NULLS FIRST or NULLS LAST — these are not supported
  * Do NOT use ILIKE — use LIKE instead
  * Use GETDATE() instead of NOW() or CURRENT_DATE
- Return ONLY the raw SQL query with no explanation, no markdown, no code fences.

### Question
{user_query}

### SQL Query
"""


def build_retry_prompt(user_query: str, schema: str, failed_sql: str, error_message: str) -> str:
    """
    Builds a retry prompt that includes the failed SQL and the error,
    asking the LLM to correct it.
    """
    return f"""### Task
A previously generated SQL query failed. Fix it so it runs correctly on Microsoft SQL Server (T-SQL).

### Database Schema
{schema}

### Rules
- Only generate SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE or any modifying statement.
- Only use tables and columns explicitly listed in the schema above. Do not invent or assume any columns.
- Always use the full schema-prefixed table name (e.g. Sales.SalesOrderHeader, not just SalesOrderHeader).
- This is Microsoft SQL Server (T-SQL). Follow these syntax rules strictly:
  * Use TOP N instead of LIMIT N (e.g. SELECT TOP 10 ... not SELECT ... LIMIT 10)
  * Do NOT use NULLS FIRST or NULLS LAST — these are not supported
  * Do NOT use ILIKE — use LIKE instead
  * Use GETDATE() instead of NOW() or CURRENT_DATE
- Return ONLY the corrected raw SQL query with no explanation, no markdown, no code fences.

### Original Question
{user_query}

### Failed SQL
{failed_sql}

### Error Message
{error_message}

### Corrected SQL Query
"""


def build_confirmation_prompt(user_query: str, sql: str) -> str:
    """
    Builds a prompt asking the LLM to summarize what the SQL query does
    in plain English for the user to confirm.
    """
    return f"""You are a helpful assistant. A user asked a question and a SQL query was generated to answer it.
Your task is to write ONE short, friendly sentence (max 30 words) describing what data will be retrieved.
Do NOT mention SQL. Write as if explaining to a non-technical person.
Do NOT ask the user to confirm. Just describe what will be shown.

User question: {user_query}

SQL query: {sql}

Plain English description:"""


def build_chart_advice_prompt(user_query: str, columns: list[str]) -> str:
    """
    Builds a prompt asking the LLM to suggest the best chart type
    given the query and the returned columns.
    """
    columns_str = ", ".join(columns)
    return f"""You are a data visualization expert. Given a user's question and the columns returned from a database query,
suggest the BEST way to display the results.

Respond with ONLY one of these options (no explanation):
- table
- bar
- line
- pie

Rules:
- Use "line" for time-series or trend data (dates/months/years on one axis)
- Use "bar" for comparisons across categories
- Use "pie" for proportions or percentages (max ~6 categories)
- Use "table" for everything else or when there are many columns

User question: {user_query}
Returned columns: {columns_str}

Best display type:"""
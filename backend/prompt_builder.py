# ─────────────────────────────────────────────
# Table descriptions — helps the LLM map plain
# English concepts to the correct table names
# ─────────────────────────────────────────────
TABLE_DESCRIPTIONS = """
Table Descriptions (use these to pick the correct table for each question):
- Sales.Customer         : information about customers who place orders
- Sales.SalesOrderHeader : individual sales orders/transactions (order date, total amount, status)
- Sales.SalesOrderDetail : line items within each order (products, quantity, unit price)
- Sales.SalesPerson      : salespeople and their performance metrics (quota, bonus, commission)
- Sales.SalesTerritory   : geographic sales regions/territories and their sales performance
- Sales.SpecialOffer     : discounts and promotional offers
- Sales.SpecialOfferProduct : which products are linked to which special offers
- Sales.Store            : stores that are customers (store name, sales person assigned)
"""

# ─────────────────────────────────────────────
# Few-shot examples — teaches the LLM the
# correct table/column names by example
# ─────────────────────────────────────────────
FEW_SHOT_EXAMPLES = """
Examples of correct SQL queries:

Q: Show me the top 5 customers by total order value
A: SELECT TOP 5 soh.CustomerID, SUM(soh.TotalDue) AS TotalOrderValue
   FROM Sales.SalesOrderHeader soh
   GROUP BY soh.CustomerID
   ORDER BY TotalOrderValue DESC

Q: List all sales territories and their total sales
A: SELECT st.Name, st.SalesYTD
   FROM Sales.SalesTerritory st
   ORDER BY st.SalesYTD DESC

Q: Which salesperson has the highest sales this year?
A: SELECT TOP 1 sp.BusinessEntityID, sp.SalesYTD
   FROM Sales.SalesPerson sp
   ORDER BY sp.SalesYTD DESC

Q: Show monthly order trends
A: SELECT YEAR(soh.OrderDate) AS Year, MONTH(soh.OrderDate) AS Month,
          COUNT(soh.SalesOrderID) AS OrderCount, SUM(soh.TotalDue) AS TotalSales
   FROM Sales.SalesOrderHeader soh
   GROUP BY YEAR(soh.OrderDate), MONTH(soh.OrderDate)
   ORDER BY Year, Month
"""

# ─────────────────────────────────────────────
# System prompt — sets the LLM persona and
# strict rules, sent separately from the query
# ─────────────────────────────────────────────
SQL_SYSTEM_PROMPT = """You are an expert Microsoft SQL Server (T-SQL) query generator.
Your only job is to convert natural language questions into valid T-SQL SELECT queries.

You must follow these rules strictly:
- Only generate SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or TRUNCATE.
- Only use tables and columns explicitly listed in the schema. Never invent or assume columns.
- Always use the full schema-prefixed table name (e.g. Sales.SalesOrderHeader, not SalesOrderHeader).
- This is Microsoft SQL Server (T-SQL):
  * Use TOP N instead of LIMIT N
  * Do NOT use NULLS FIRST or NULLS LAST
  * Do NOT use ILIKE — use LIKE instead
  * Use GETDATE() instead of NOW() or CURRENT_DATE
  * Use YEAR(), MONTH(), DAY() for date parts
- Return ONLY the raw SQL query. No explanation, no markdown, no code fences."""


def build_sql_prompt(user_query: str, schema: str) -> tuple[str, str]:
    """
    Builds system + user prompt for SQL generation.
    Returns (system_prompt, user_prompt) tuple.
    """
    system = SQL_SYSTEM_PROMPT

    user = f"""### Database Schema
{schema}

{TABLE_DESCRIPTIONS}

{FEW_SHOT_EXAMPLES}

### Question
{user_query}

### SQL Query
"""
    return system, user


def build_retry_prompt(user_query: str, schema: str, failed_sql: str, error_message: str) -> tuple[str, str]:
    """
    Builds system + user prompt for SQL retry after a failed attempt.
    Returns (system_prompt, user_prompt) tuple.
    """
    system = SQL_SYSTEM_PROMPT

    user = f"""### Database Schema
{schema}

{TABLE_DESCRIPTIONS}

{FEW_SHOT_EXAMPLES}

### Original Question
{user_query}

### Failed SQL
{failed_sql}

### Error Message
{error_message}

### Corrected SQL Query
"""
    return system, user


def build_confirmation_prompt(user_query: str) -> str:
    """
    Builds a prompt that rephrases the user's question into a precise
    data intent confirmation starting with "So I will...".
    """
    return f"""You are a data assistant. A user has asked a business data question.
Rephrase it into ONE clear, precise sentence starting with "So I will..." that describes 
exactly what data will be retrieved. Be specific about grouping, sorting, filters, and limits.
Keep it under 35 words. Do not mention SQL or databases.

User question: {user_query}

Confirmation sentence:"""


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

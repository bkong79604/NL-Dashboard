from llm_client import generate_general

SYSTEM_PROMPT = """You are an intent classifier for a business data query application.
Your only job is to classify the user's input into one of three categories.
Respond with ONLY one of these three words, nothing else:
- DATA_QUERY
- OFF_TOPIC
- META_QUERY

DATA_QUERY: Any question or request that involves retrieving, analyzing, summarizing,
or visualizing business data (sales, orders, customers, territories, products, revenue, etc.)

META_QUERY: Any question about the application itself, what it can do, what tables or data
are available, what columns exist, or what kinds of questions can be asked.

OFF_TOPIC: Anything else — greetings, weather, general knowledge, opinions,
personal questions, or anything unrelated to business data or the application.

Examples:
"Hi there" -> OFF_TOPIC
"How are you?" -> OFF_TOPIC
"What's the weather like?" -> OFF_TOPIC
"Who is the president?" -> OFF_TOPIC
"Show me top 10 customers" -> DATA_QUERY
"What is the total revenue by territory?" -> DATA_QUERY
"List all orders from last year" -> DATA_QUERY
"Which salesperson has the highest sales?" -> DATA_QUERY
"What tables can you access?" -> META_QUERY
"What data is available?" -> META_QUERY
"What can you help me with?" -> META_QUERY
"What fields does the orders table have?" -> META_QUERY
"What kind of questions can I ask?" -> META_QUERY"""


# Friendly description of available tables shown for META_QUERY responses
AVAILABLE_TABLES_DESCRIPTION = """Here's what I have access to:

📦 **Sales.Customer** — Information about customers who place orders

🧾 **Sales.SalesOrderHeader** — Individual sales orders and transactions (order date, total amount, status)

📋 **Sales.SalesOrderDetail** — Line items within each order (products, quantity, unit price)

👤 **Sales.SalesPerson** — Salespeople and their performance metrics (quota, bonus, commission)

🗺️ **Sales.SalesTerritory** — Geographic sales regions and their performance

🏷️ **Sales.SpecialOffer** — Discounts and promotional offers

🔗 **Sales.SpecialOfferProduct** — Which products are linked to which special offers

🏪 **Sales.Store** — Stores that are customers (store name, assigned salesperson)

You can ask questions like:
- *"Show me the top 10 customers by total order value"*
- *"Which sales territory had the highest revenue?"*
- *"What is the monthly sales trend for 2013?"*
- *"Which salesperson has the highest sales this year?"*
- *"List all orders above $10,000"*"""


def classify_intent(user_query: str) -> str:
    """
    Classifies the user's input as DATA_QUERY, OFF_TOPIC, or META_QUERY.
    Uses llama3.1:8b (general model) for better natural language understanding.
    Defaults to DATA_QUERY if classification fails.
    """
    try:
        result = generate_general(
            prompt=f"User input: {user_query}\n\nClassification:",
            system_prompt=SYSTEM_PROMPT
        ).strip().upper()

        print(f"[intent_filter] Raw result: {result}")

        if "OFF_TOPIC" in result:
            return "OFF_TOPIC"
        if "META_QUERY" in result:
            return "META_QUERY"
        return "DATA_QUERY"
    except Exception as e:
        print(f"[intent_filter] Classification failed, defaulting to DATA_QUERY: {e}")
        return "DATA_QUERY"


def get_off_topic_response(user_query: str) -> str:
    """
    Generates a friendly response for off-topic queries using llama3.1:8b.
    """
    try:
        return generate_general(
            prompt=f"User message: {user_query}\n\nResponse:",
            system_prompt=(
                "You are a friendly assistant for a business data dashboard. "
                "The user has asked something unrelated to business data. "
                "Write a brief, friendly response (max 2 sentences) acknowledging "
                "their message and politely letting them know you can only help "
                "with business data queries like sales, orders, customers, or territories."
            )
        ).strip()
    except Exception:
        return "I can only help with business data questions. Try asking about sales, customers, orders, or territories!"


def get_meta_response(user_query: str) -> str:
    """
    Returns a friendly description of available tables and example queries.
    Uses the hardcoded AVAILABLE_TABLES_DESCRIPTION for accuracy —
    we don't want the LLM guessing what tables are available.
    """
    return AVAILABLE_TABLES_DESCRIPTION

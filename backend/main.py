from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import OLLAMA_MODEL
from schema_loader import load_schema, invalidate_schema_cache
from prompt_builder import build_confirmation_prompt
from llm_client import generate, is_ollama_available
from retry_handler import run_query_with_retry, QueryFailedError
from chart_advisor import suggest_chart_type

app = FastAPI(title="NL Dashboard API", version="1.0.0")

# Allow requests from the React frontend (dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request / Response Models ----------

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    confirmation: str       # Plain English summary of what will be shown
    sql: str                # The generated SQL (for debug purposes, not shown to users)
    columns: list[str]
    rows: list[dict]
    row_count: int
    chart_type: str         # "table" | "bar" | "line" | "pie"


# ---------- Routes ----------

@app.get("/health")
def health_check():
    """Check if the API and Ollama are running."""
    ollama_ok = is_ollama_available()
    return {
        "status": "ok",
        "ollama": "connected" if ollama_ok else "unavailable",
        "model": OLLAMA_MODEL,
    }


@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    """
    Main endpoint. Accepts a plain English query, returns data + chart type.
    """
    user_query = request.query.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Check Ollama is available
    if not is_ollama_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama is not available. Please ensure it is running and the model is loaded."
        )

    # Load schema context
    try:
        schema = load_schema()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load database schema: {e}")

    # Generate SQL + execute with retry
    try:
        sql, result = run_query_with_retry(user_query, schema)
    except QueryFailedError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    # Generate plain English confirmation summary
    try:
        confirmation_prompt = build_confirmation_prompt(user_query, sql)
        confirmation = generate(confirmation_prompt)
    except Exception:
        confirmation = "Here are the results based on your question."

    # Determine best chart type
    chart_type = suggest_chart_type(user_query, result["columns"])

    return QueryResponse(
        confirmation=confirmation,
        sql=sql,
        columns=result["columns"],
        rows=result["rows"],
        row_count=result["row_count"],
        chart_type=chart_type,
    )


@app.post("/schema/reload")
def reload_schema():
    """Force a schema cache refresh (useful during development)."""
    invalidate_schema_cache()
    load_schema()
    return {"status": "Schema reloaded successfully."}

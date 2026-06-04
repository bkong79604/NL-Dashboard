from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import OLLAMA_MODEL
from schema_loader import load_schema, invalidate_schema_cache
from llm_client import is_ollama_available, get_model_status
from intent_filter import classify_intent, get_off_topic_response, get_meta_response
from retry_handler import run_query_with_retry, QueryFailedError
from chart_advisor import suggest_chart_type

app = FastAPI(title="NL Dashboard API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request / Response Models ----------

class UserQueryRequest(BaseModel):
    query: str

class ClassifyResponse(BaseModel):
    intent: str       # "DATA_QUERY" | "OFF_TOPIC" | "META_QUERY"
    message: str      # populated for OFF_TOPIC and META_QUERY, empty for DATA_QUERY

class QueryResponse(BaseModel):
    sql: str
    columns: list[str]
    rows: list[dict]
    row_count: int
    chart_type: str


# ---------- Routes ----------

@app.get("/health")
def health_check():
    """Check if the API and Ollama model are available."""
    status = get_model_status()
    return {
        "status": "ok",
        "ollama": "connected" if status["sql_model_available"] else "unavailable",
        "model": status["sql_model"],
    }


@app.post("/classify", response_model=ClassifyResponse)
def classify(request: UserQueryRequest):
    """
    Step 1 — Classify the user's intent:
    - DATA_QUERY  → frontend proceeds directly to /query
    - OFF_TOPIC   → return friendly redirect message, stop here
    - META_QUERY  → return table/capability description, stop here
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    intent = classify_intent(query)

    if intent == "OFF_TOPIC":
        return ClassifyResponse(
            intent="OFF_TOPIC",
            message=get_off_topic_response(query)
        )

    if intent == "META_QUERY":
        return ClassifyResponse(
            intent="META_QUERY",
            message=get_meta_response(query)
        )

    return ClassifyResponse(intent="DATA_QUERY", message="")


@app.post("/query", response_model=QueryResponse)
def handle_query(request: UserQueryRequest):
    """
    Step 2 — Execute the data query directly, no confirmation step.
    Uses sqlcoder:7b for SQL generation.
    """
    user_query = request.query.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if not is_ollama_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama is not available. Please ensure it is running and the model is loaded."
        )

    try:
        schema = load_schema()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load database schema: {e}")

    try:
        sql, result = run_query_with_retry(user_query, schema)
    except QueryFailedError as e:
        raise HTTPException(status_code=422, detail=str(e))

    chart_type = suggest_chart_type(user_query, result["columns"])

    return QueryResponse(
        sql=sql,
        columns=result["columns"],
        rows=result["rows"],
        row_count=result["row_count"],
        chart_type=chart_type,
    )


@app.post("/schema/reload")
def reload_schema():
    """Force a schema cache refresh."""
    invalidate_schema_cache()
    load_schema()
    return {"status": "Schema reloaded successfully."}
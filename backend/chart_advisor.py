from prompt_builder import build_chart_advice_prompt
from llm_client import generate_general

VALID_CHART_TYPES = {"table", "bar", "line", "pie"}


def suggest_chart_type(user_query: str, columns: list[str]) -> str:
    """
    Uses llama3.1:8b (general model) to suggest the best chart type.
    Falls back to heuristics if the LLM returns an unexpected value.
    Always returns one of: 'table', 'bar', 'line', 'pie'
    """
    try:
        prompt = build_chart_advice_prompt(user_query, columns)
        raw = generate_general(prompt).lower().strip()

        for chart_type in VALID_CHART_TYPES:
            if chart_type in raw:
                return chart_type
    except Exception as e:
        print(f"[chart_advisor] LLM call failed, falling back to heuristics: {e}")

    return _heuristic_chart_type(columns)


def _heuristic_chart_type(columns: list[str]) -> str:
    """Simple heuristic fallback when LLM is unavailable."""
    col_names_lower = [c.lower() for c in columns]

    time_signals = {"year", "month", "date", "day", "quarter", "week", "period"}
    if any(any(t in col for t in time_signals) for col in col_names_lower):
        return "line"

    pct_signals = {"percent", "pct", "ratio", "share", "proportion"}
    if any(any(p in col for p in pct_signals) for col in col_names_lower) and len(columns) <= 2:
        return "pie"

    if len(columns) == 2:
        return "bar"

    return "table"

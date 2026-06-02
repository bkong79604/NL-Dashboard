from prompt_builder import build_chart_advice_prompt
from llm_client import generate

VALID_CHART_TYPES = {"table", "bar", "line", "pie"}


def suggest_chart_type(user_query: str, columns: list[str]) -> str:
    """
    Uses the LLM to suggest the best chart type for the result set.
    Falls back to heuristics if the LLM returns an unexpected value.
    Always returns one of: 'table', 'bar', 'line', 'pie'
    """
    try:
        prompt = build_chart_advice_prompt(user_query, columns)
        raw = generate(prompt).lower().strip()

        # Extract just the chart type word in case LLM adds extra text
        for chart_type in VALID_CHART_TYPES:
            if chart_type in raw:
                return chart_type
    except Exception as e:
        print(f"[chart_advisor] LLM call failed, falling back to heuristics: {e}")

    # Fallback: heuristic based on column names
    return _heuristic_chart_type(columns)


def _heuristic_chart_type(columns: list[str]) -> str:
    """
    Simple heuristic when LLM is unavailable or returns unexpected output.
    """
    col_names_lower = [c.lower() for c in columns]

    # Time-series signals
    time_signals = {"year", "month", "date", "day", "quarter", "week", "period"}
    if any(any(t in col for t in time_signals) for col in col_names_lower):
        return "line"

    # Proportion signals
    pct_signals = {"percent", "pct", "ratio", "share", "proportion"}
    if any(any(p in col for p in pct_signals) for col in col_names_lower) and len(columns) <= 2:
        return "pie"

    # Two columns often means category + value → bar chart
    if len(columns) == 2:
        return "bar"

    # Default fallback
    return "table"

import re
import ollama
from config import OLLAMA_MODEL, OLLAMA_HOST

# Strip ANSI escape codes that sqlcoder:7b sometimes outputs
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m|\x1b\[[0-9;]*[A-Za-z]|<s\[[\d;]*m>|\[[\d;]*m')


def _get_client():
    return ollama.Client(host=OLLAMA_HOST)


def _clean_response(text: str) -> str:
    """
    Cleans the raw LLM response:
    - Strips ANSI/terminal escape codes (sqlcoder:7b quirk)
    - Strips leading/trailing whitespace
    """
    text = ANSI_ESCAPE.sub("", text)
    # Also strip any HTML-like escape artifacts e.g. <s[4m>
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def generate(prompt: str) -> str:
    """
    Sends a prompt to Ollama and returns the raw text response.
    Raises an exception if Ollama is unreachable or the model fails.
    """
    client = _get_client()
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0,       # Deterministic output — important for SQL
            "num_predict": 1024,    # Increased to allow complex multi-join queries
            "num_ctx": 4096,        # Context window size
        }
    )
    raw = response["message"]["content"]
    return _clean_response(raw)


def is_ollama_available() -> bool:
    """
    Quick health check to verify Ollama is running and the model is available.
    """
    try:
        client = _get_client()
        models = client.list()
        available = [m["name"] for m in models.get("models", [])]
        return any(OLLAMA_MODEL in m for m in available)
    except Exception:
        return False
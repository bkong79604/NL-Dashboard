import re
import ollama
from config import OLLAMA_MODEL, OLLAMA_GENERAL_MODEL, OLLAMA_HOST

# Strip ANSI escape codes that sqlcoder:7b sometimes outputs
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m|\x1b\[[0-9;]*[A-Za-z]|<s\[[\d;]*m>|\[[\d;]*m')


def _get_client():
    return ollama.Client(host=OLLAMA_HOST)


def _clean_response(text: str) -> str:
    """Strips ANSI/terminal escape codes and whitespace."""
    text = ANSI_ESCAPE.sub("", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def generate(prompt: str, system_prompt: str = None) -> str:
    """
    SQL generation — uses OLLAMA_MODEL (sqlcoder:7b).
    Temperature 0 for deterministic SQL output.
    """
    client = _get_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=messages,
        options={
            "temperature": 0,
            "num_predict": 1024,
            "num_ctx": 4096,
        }
    )
    return _clean_response(response["message"]["content"])


def generate_general(prompt: str, system_prompt: str = None) -> str:
    """
    General tasks — uses OLLAMA_GENERAL_MODEL (llama3.1:8b).
    Used for: intent classification, off-topic replies, meta responses.
    """
    client = _get_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat(
        model=OLLAMA_GENERAL_MODEL,
        messages=messages,
        options={
            "temperature": 0.1,
            "num_predict": 512,
            "num_ctx": 2048,
        }
    )
    return _clean_response(response["message"]["content"])


def is_ollama_available() -> bool:
    """Check if both models are available in Ollama."""
    try:
        client = _get_client()
        models = client.list()
        available = [m["name"] for m in models.get("models", [])]
        sql_ok = any(OLLAMA_MODEL in m for m in available)
        general_ok = any(OLLAMA_GENERAL_MODEL in m for m in available)
        return sql_ok and general_ok
    except Exception:
        return False


def get_model_status() -> dict:
    """Returns availability status of both models."""
    try:
        client = _get_client()
        models = client.list()
        available = [m["name"] for m in models.get("models", [])]
        return {
            "sql_model": OLLAMA_MODEL,
            "sql_model_available": any(OLLAMA_MODEL in m for m in available),
            "general_model": OLLAMA_GENERAL_MODEL,
            "general_model_available": any(OLLAMA_GENERAL_MODEL in m for m in available),
        }
    except Exception:
        return {
            "sql_model": OLLAMA_MODEL,
            "sql_model_available": False,
            "general_model": OLLAMA_GENERAL_MODEL,
            "general_model_available": False,
        }
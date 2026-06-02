# NL Dashboard

A natural language interface for querying your database and generating dashboards, powered by a local LLM via Ollama.

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running
- SQL Server with the Northwind database
- ODBC Driver 17 for SQL Server installed

---

## 1. Pull the LLM Model

```bash
ollama pull llama3.1:8b
```

Verify it's available:
```bash
ollama list
```

---

## 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure the database connection

Edit `.env` and fill in your SQL Server details:

```env
DB_SERVER=localhost
DB_NAME=Northwind
DB_USER=sa
DB_PASSWORD=your_password_here

# Or use Windows Authentication:
# DB_TRUSTED_CONNECTION=yes
```

### Run the backend

```bash
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000/health to verify the backend and Ollama are connected.

---

## 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173 to open the app.

---

## Project Structure

```
nl-dashboard/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment config
│   ├── schema_loader.py     # Live schema introspection
│   ├── prompt_builder.py    # LLM prompt construction
│   ├── llm_client.py        # Ollama API client
│   ├── sql_validator.py     # SELECT-only safety check
│   ├── db_executor.py       # SQL execution
│   ├── retry_handler.py     # Retry loop orchestration
│   ├── chart_advisor.py     # Chart type suggestion
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── ChatInput.jsx
    │   │   ├── ConfirmationBubble.jsx
    │   │   ├── ResultTable.jsx
    │   │   ├── ResultChart.jsx
    │   │   └── ErrorBubble.jsx
    │   └── services/
    │       └── api.js
    └── package.json
```

---

## Example Queries to Try

- "Show me the top 5 products by total revenue"
- "Which customers placed the most orders in 1997?"
- "What is the monthly sales trend across all years?"
- "List all employees and their managers"
- "Which country generated the most sales?"

---

## Security Notes

- The backend enforces **SELECT-only** queries via both keyword blocking and AST parsing (`sqlglot`)
- All data stays **local** — Ollama runs entirely on your machine
- The database user in `.env` should ideally be a **read-only SQL user** for extra safety

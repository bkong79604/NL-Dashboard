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
ollama pull sqlcoder:7b
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

to activate venv later, use command prompt and run this:
venv\Scripts\activate

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

- "Show me the total tax amount by territory"
- "How many total customer count we have by territory?"
- "Use a pie chart to show the top 3 territory with the most customer count"
- "Use a bar chart to show the top 5 territories with the most order count"
- "How many orders we have for ship data ='2011-06-07'?"

---

## Security Notes

- The backend enforces **SELECT-only** queries via both keyword blocking and AST parsing (`sqlglot`)
- All data stays **local** — Ollama runs entirely on your machine
- The database user in `.env` should ideally be a **read-only SQL user** for extra safety


Find out the port number for SQL Server:
SELECT local_net_address, local_tcp_port 
FROM sys.dm_exec_connections 
WHERE session_id = @@SPID

Run it in SSMS with TCP/IP connection forced (File → New → Database Engine Query → Options >> → Connection Properties → Network protocol: TCP/IP), otherwise it returns null for both columns.
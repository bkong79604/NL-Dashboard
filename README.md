# NL Dashboard

A natural language interface for querying your database and generating dashboards, powered by local LLMs via Ollama. Ask questions in plain English and get data tables or charts back instantly — no SQL knowledge required.

> **POC built against AdventureWorks2022 (Sales schema) on SQL Server Express.**

---

## How It Works

```
User types a question
        ↓
llama3.1:8b classifies intent
        ↓
OFF_TOPIC  → friendly redirect message
META_QUERY → list of available tables & capabilities
DATA_QUERY → sqlcoder:7b generates T-SQL
        ↓
SQL validated (SELECT-only, AST parsing)
        ↓
Auto-retry up to 3x if SQL fails
        ↓
Results rendered as table, bar, line, or pie chart
```

---

## Architecture

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + Tailwind CSS | Chat UI |
| Charts | Recharts | Bar, line, pie, table rendering |
| Backend | FastAPI (Python) | Orchestration layer |
| SQL Model | `sqlcoder:7b` via Ollama | T-SQL generation |
| General Model | `llama3.1:8b` via Ollama | Intent classification, off-topic replies |
| Database | SQL Server (AdventureWorks2022) | Data source |
| SQL Safety | `sqlglot` | SELECT-only validation |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running
- SQL Server with AdventureWorks2022 database
- ODBC Driver 17 for SQL Server

---

## 1. Pull the LLM Models

```bash
ollama pull sqlcoder:7b
ollama pull llama3.1:8b
```

Verify both are available:
```bash
ollama list
```

---

## 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows Command Prompt
.\venv\Scripts\Activate.ps1  # Windows PowerShell (run Set-ExecutionPolicy RemoteSigned -Scope CurrentUser first)

# Install dependencies
pip install -r requirements.txt
```

### Configure the database connection

Copy `.env.example` to `.env` and fill in your details:

```env
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=127.0.0.1,1433
DB_NAME=AdventureWorks2022
DB_USER=sa
DB_PASSWORD=your_password_here
DB_TRUSTED_CONNECTION=no

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=sqlcoder:7b
OLLAMA_GENERAL_MODEL=llama3.1:8b

MAX_RETRY_ATTEMPTS=3
MAX_ROWS_RETURNED=500
```

> **Note:** If your SQL Server Express uses a dynamic port, find it by running this query in SSMS (connected via TCP/IP):
> ```sql
> SELECT local_net_address, local_tcp_port
> FROM sys.dm_exec_connections
> WHERE session_id = @@SPID
> ```
> Then update `DB_SERVER=127.0.0.1,YOUR_PORT` in `.env`.
>
> To set a permanent static port (recommended), run in SSMS:
> ```sql
> EXEC xp_instance_regwrite N'HKEY_LOCAL_MACHINE',
>     N'Software\Microsoft\MSSQLServer\MSSQLServer\SuperSocketNetLib\Tcp\IpAll',
>     N'TcpPort', REG_SZ, N'1433'
> EXEC xp_instance_regwrite N'HKEY_LOCAL_MACHINE',
>     N'Software\Microsoft\MSSQLServer\MSSQLServer\SuperSocketNetLib\Tcp\IpAll',
>     N'TcpDynamicPorts', REG_SZ, N''
> ```
> Then restart SQL Server in `services.msc`.

### Run the backend

```bash
uvicorn main:app --reload --port 8000
```

Visit **http://localhost:8000/health** to verify the backend and both models are connected.

---

## 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173** to open the app.

---

## Project Structure

```
nl-dashboard/
├── backend/
│   ├── main.py              # FastAPI entry point — /classify and /query endpoints
│   ├── config.py            # Environment config and DB connection string
│   ├── schema_loader.py     # Live schema introspection (Sales schema, 8 core tables)
│   ├── prompt_builder.py    # LLM prompt construction with table descriptions + few-shot examples
│   ├── llm_client.py        # Ollama API client — generate() and generate_general()
│   ├── intent_filter.py     # Classifies DATA_QUERY / OFF_TOPIC / META_QUERY
│   ├── sql_validator.py     # SELECT-only safety check + T-SQL auto-fix
│   ├── db_executor.py       # SQL execution and result serialization
│   ├── retry_handler.py     # Retry loop — feeds errors back to LLM for self-correction
│   ├── chart_advisor.py     # Suggests chart type from query + result columns
│   ├── .env.example         # Environment variable template
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── App.jsx                      # Main app — classify → query flow
    │   ├── components/
    │   │   ├── ChatInput.jsx            # User query input
    │   │   ├── ResultTable.jsx          # Tabular data display
    │   │   ├── ResultChart.jsx          # Recharts bar/line/pie charts
    │   │   └── ErrorBubble.jsx          # Friendly error messages
    │   └── services/
    │       └── api.js                   # Axios calls to FastAPI
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    └── package.json
```

---

## Available Tables (Sales Schema)

| Table | Description |
|---|---|
| `Sales.Customer` | Customers who place orders |
| `Sales.SalesOrderHeader` | Individual sales orders (date, total, status) |
| `Sales.SalesOrderDetail` | Line items within each order (product, qty, price) |
| `Sales.SalesPerson` | Salespeople and performance metrics |
| `Sales.SalesTerritory` | Geographic sales regions and performance |
| `Sales.SpecialOffer` | Discounts and promotional offers |
| `Sales.SpecialOfferProduct` | Products linked to special offers |
| `Sales.Store` | Stores that are customers |

---

## Example Queries to Try

- "Show me the total tax amount by territory"
- "How many total customer count we have by territory?"
- "Use a pie chart to show the top 3 territory with the most customer count"
- "Use a bar chart to show the top 5 territories with the most order count"
- "How many orders we have for ship data ='2011-06-07'?"

---

## Known Limitations (POC)

- **Schema scope** — limited to 8 core Sales tables. Larger schemas need smarter context selection strategies
- **Model hallucination** — 7B models occasionally generate incorrect column names on complex multi-table joins. The retry mechanism handles most cases
- **Model swap delay** — switching between `llama3.1:8b` and `sqlcoder:7b` takes ~20-30s on 8GB VRAM
- **Read-only** — only SELECT queries are supported by design
- **Not production-ready** — no authentication, no multi-user support, no query history persistence

---

## Security Notes

- All data stays **100% local** — Ollama runs entirely on your machine, no cloud calls
- The backend enforces **SELECT-only** queries via keyword blocking + AST parsing (`sqlglot`)
- Never commit your `.env` file — it contains your database password
- For extra safety, use a **read-only SQL Server user** instead of `sa`

---

## Multi-User Support

The current POC is designed for **single-user or small group demo use only**. While FastAPI can technically handle multiple HTTP requests simultaneously, true concurrent multi-user support requires significant additional work.

### Current Limitations for Multi-User
- **Model swap bottleneck** — Ollama can only run one model at a time. Concurrent users will queue and block each other
- **No authentication** — anyone with the URL can access the app and query the database
- **No user isolation** — all users share the same Ollama instance and schema cache
- **No per-user history** — conversations are not saved or separated by user

---

## Production Roadmap

For a production-grade multi-user deployment (e.g. 10 concurrent users), the following areas need to be addressed:

### 1. Authentication & User Management
- Implement login system using JWT tokens (`python-jose` + `passlib`)
- Add a users table in a dedicated database
- Protect all API routes with FastAPI auth middleware
- Add a frontend login page

### 2. LLM Concurrency — Model Instance Pool
- Run multiple parallel Ollama instances (e.g. ports 11434–11443)
- Implement a backend connection pool that assigns a free instance per request
- With 128GB VRAM: 5× `sqlcoder:7b` (~25GB) + 5× `llama3.1:8b` (~30GB) = ~55GB total, comfortably serving 10 concurrent users

### 3. Request Queue & Rate Limiting
- Add a request queue (`asyncio.Queue` or Redis) to manage LLM call concurrency
- Implement per-user rate limiting using `slowapi`
- Add per-request timeouts to prevent stuck queries from blocking others

### 4. Per-User Session & History
- Store conversation history per user in Redis or PostgreSQL
- Load history on login and persist on each query
- Isolate each user's session state on the frontend

### Estimated Additional Files for Production

| File | Purpose |
|---|---|
| `auth.py` | JWT login/logout logic |
| `ollama_pool.py` | Ollama instance pool manager |
| `session_store.py` | Per-user conversation history in Redis |
| `Login.jsx` | Frontend login form |

### Hardware Recommendation for 10 Concurrent Users
| Resource | Minimum |
|---|---|
| VRAM | 64GB+ |
| RAM | 64GB+ |
| CPU | 16+ cores |
| Storage | SSD with fast I/O for DB |
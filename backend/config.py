import os
from dotenv import load_dotenv

load_dotenv()

# Database
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_SERVER = os.getenv("DB_SERVER", "127.0.0.1,52952")
DB_NAME = os.getenv("DB_NAME", "AdventureWorks2022")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "no")

if DB_TRUSTED_CONNECTION.lower() == "yes":
    DATABASE_URL = (
        f"mssql+pyodbc://{DB_SERVER}/{DB_NAME}"
        f"?driver={DB_DRIVER.replace(' ', '+')}"
        f"&trusted_connection=yes"
        f"&TrustServerCertificate=yes"
        f"&Encrypt=no"
    )
else:
    DATABASE_URL = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
        f"?driver={DB_DRIVER.replace(' ', '+')}"
        f"&TrustServerCertificate=yes"
        f"&Encrypt=no"
    )

print("DATABASE_URL:", DATABASE_URL)

# Ollama
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# App
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", 3))
MAX_ROWS_RETURNED = int(os.getenv("MAX_ROWS_RETURNED", 500))
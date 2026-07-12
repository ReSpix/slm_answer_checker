from pathlib import Path
import os

data_dir = Path("/databases")

sqlite_dir = data_dir / "sqlite"
os.makedirs(sqlite_dir, exist_ok=True)

chromadb_dir = data_dir / "chroma"
os.makedirs(chromadb_dir, exist_ok=True)

documents_dir = Path("/documents")
os.makedirs(documents_dir, exist_ok=True)

EMBEDDING_MODEL_NAME = "cointegrated/rubert-tiny2"
KEY_CONCEPTS_MODEL_CONFIG = {"name": "qwen2.5:3b", "temperature": 0.9}
GRADING_MODEL_CONFIG = {"name": "t-tech/T-lite-it-2.1:Q4_K_M", "temperature": 1}

CHROMA_COLLECTION_NAME = "slm_answer_checker_rag"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

SKIP_EMBEDDING_INIT_ON_STARTUP = os.getenv(
    "SKIP_EMBEDDING_INIT_ON_STARTUP", ""
).lower() in ("true", "1")

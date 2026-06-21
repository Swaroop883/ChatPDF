import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gemini-1.5-flash")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "models/embedding-001")
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/chatpdf")
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-insecure-key-replace-in-production")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

UPLOAD_DIR: Path = Path(__file__).resolve().parents[2] / "storage" / "uploads"
VECTORSTORE_DIR: Path = Path(__file__).resolve().parents[2] / "storage" / "vectorstore"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)


def get_llm():
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        google_api_key=LLM_API_KEY,
        temperature=0.3,
    )


def get_embedding_model():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=LLM_API_KEY,
    )

import os
import hashlib
import math
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-versatile")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", os.getenv("LLM_API_KEY", ""))
EMBEDDING_DIMENSIONS: int = int(os.getenv("EMBEDDING_DIMENSIONS", "384"))
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


class LocalHashEmbeddings:
    def __init__(self, dimensions: int = EMBEDDING_DIMENSIONS):
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"\w+", text.lower())

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0:
            return vector

        return [value / magnitude for value in vector]


def get_llm():
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=LLM_MODEL_NAME,
        groq_api_key=GROQ_API_KEY,
        temperature=0.3,
    )


def get_embedding_model():
    return LocalHashEmbeddings()

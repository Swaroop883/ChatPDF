import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gemini-1.5-flash")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "gemini")
EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "models/embedding-001")
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/chatpdf")
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-insecure-key-replace-in-production")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")


UPLOAD_DIR: Path = Path(__file__).resolve().parents[3] / "storage" / "uploads"


VECTORSTORE_DIR: Path = Path(__file__).resolve().parents[3] / "storage" / "vectorstore"


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)


def get_llm():
    
    provider = LLM_PROVIDER.lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
       
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL_NAME,
            google_api_key=LLM_API_KEY,
            temperature=0.3,
        )

    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model_name=LLM_MODEL_NAME,
            groq_api_key=LLM_API_KEY,
            temperature=0.3,
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model_name=LLM_MODEL_NAME,
            openai_api_key=LLM_API_KEY,
            temperature=0.3,
        )

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: '{provider}'. "
            "Choose from: gemini, groq, openai"
        )


def get_embedding_model():
    
    provider = EMBEDDING_PROVIDER.lower()

    if provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL_NAME,
            google_api_key=LLM_API_KEY,
        )

    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=EMBEDDING_MODEL_NAME,
            openai_api_key=LLM_API_KEY,
        )

    else:
        raise ValueError(
            f"Unsupported EMBEDDING_PROVIDER: '{provider}'. "
            "Choose from: gemini, openai"
        )

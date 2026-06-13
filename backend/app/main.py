import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.db.database import engine, Base
from app.routes import auth, documents, sessions, chat
from app.config import JWT_SECRET_KEY

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ChatPDF API",
    description=(
        "Backend API for ChatPDF — an intelligent PDF Q&A application. "
        "Supports RAG (retrieval-augmented generation) and Summary modes "
        "for answering questions about uploaded PDF documents."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=JWT_SECRET_KEY,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/document", tags=["Documents"])
app.include_router(sessions.router, prefix="/session", tags=["Sessions"])
app.include_router(chat.router, tags=["Chat"])

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "message": "ChatPDF API is running. Visit /docs for the interactive API reference.",
    }

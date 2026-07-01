import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import engine, Base
from app.routes import auth, documents, sessions, chat
from app.config import JWT_SECRET_KEY


#this line creates all the tables requied for the application in the database, based on the models defined in the application. It uses the metadata of the Base class to create the tables in the database.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ChatPDF API",
    description=(
        "Backend API for ChatPDF — an intelligent PDF Q&A application. "
        "Supports RAG (retrieval-augmented generation) and Summary modes "
        "for answering questions about uploaded PDF documents."
    ),
    version="1.0.0",
    docs_url="/docs", # these are just swagger ui for api testing 
    redoc_url="/redoc",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=JWT_SECRET_KEY, #session middleware creates the encrypted data to be stored as cookies in the browser, and whenever the user relogins it gets the encrypted data and uses its secret key to decrypt and verify the user.
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #origin = protocol+domain+port
    allow_credentials=True, #  credentials are basicallt the stuff required to validate a user,this allows stored cookies from browser to be sent in cross-origin requests, which is necessary for session management
    allow_methods=["*"], 
    allow_headers=["*"],
)


# this registers the routers in the app , so the app knows which endpoints to handle and how to route requests to the appropriate handlers.
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/document", tags=["Documents"])
app.include_router(sessions.router, prefix="/session", tags=["Sessions"])
app.include_router(chat.router, tags=["Chat"])
app.mount("/frontend", StaticFiles(directory=r"C:\development\chat-PDF\ChatPDF\frontend"), name="frontend")

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "message": "ChatPDF API is running. Visit /docs for the interactive API reference.",
    }

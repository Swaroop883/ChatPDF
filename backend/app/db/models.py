from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    google_id = Column(String(255), nullable=True, unique=True)
    created_at = Column(DateTime, server_default=func.now())

    documents = relationship("Document", back_populates="owner")
    sessions = relationship("Session", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())

    owner = relationship("User", back_populates="documents")
    sessions = relationship("Session", back_populates="document")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    session_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    owner = relationship("User", back_populates="sessions")
    document = relationship("Document", back_populates="sessions")
    messages = relationship("ChatHistory", back_populates="session")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    mode_used = Column(String(20), nullable=False)
    source_chunk = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    session = relationship("Session", back_populates="messages")

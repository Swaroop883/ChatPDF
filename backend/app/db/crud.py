from sqlalchemy.orm import Session as DBSession
from app.db.models import User, Document, Session, ChatHistory

# User Operations

def create_user(
    db: DBSession,
    username: str,
    email: str,
    password_hash: str | None = None,
    google_id: str | None = None,
) -> User:
    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        google_id=google_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_email(db: DBSession, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: DBSession, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_google_id(db: DBSession, google_id: str) -> User | None:
    return db.query(User).filter(User.google_id == google_id).first()

# Document Operations

def create_document(
    db: DBSession,
    user_id: int,
    filename: str,
    file_path: str,
) -> Document:
    new_document = Document(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return new_document


def get_document_by_id(db: DBSession, document_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()


def get_documents_by_user(db: DBSession, user_id: int) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

# Session Operations

def create_session(
    db: DBSession,
    user_id: int,
    document_id: int,
    session_name: str,
) -> Session:
    new_session = Session(
        user_id=user_id,
        document_id=document_id,
        session_name=session_name,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


def get_session_by_id(db: DBSession, session_id: int) -> Session | None:
    return db.query(Session).filter(Session.id == session_id).first()


def get_sessions_by_user(db: DBSession, user_id: int) -> list[Session]:
    return (
        db.query(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.created_at.desc())
        .all()
    )

# Chat History Operations

def save_chat_message(
    db: DBSession,
    session_id: int,
    question: str,
    answer: str,
    mode_used: str,
    source_chunk: str | None = None,
) -> ChatHistory:
    new_message = ChatHistory(
        session_id=session_id,
        question=question,
        answer=answer,
        mode_used=mode_used,
        source_chunk=source_chunk,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def get_chat_history(db: DBSession, session_id: int) -> list[ChatHistory]:
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )

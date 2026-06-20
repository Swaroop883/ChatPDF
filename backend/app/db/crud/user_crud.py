from sqlalchemy.orm import Session as DBSession
from app.db.models import User

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
from sqlalchemy.orm import Session as DBSession
from app.db.models import Session

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



#Used to validate session ownership before processing a chat query
def get_session_by_id(db: DBSession, session_id: int) -> Session | None:
    return db.query(Session).filter(Session.id == session_id).first()

#Return all sessions created by a specific user
def get_sessions_by_user(db: DBSession, user_id: int) -> list[Session]:
    return (
        db.query(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.created_at.desc())
        .all()
    )
from sqlalchemy.orm import Session as DBSession
from app.db.models import ChatHistory

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



#Return the full message history for a session in chronological order , Used when the user reopens an old session from the dashboard.
def get_chat_history(db: DBSession, session_id: int) -> list[ChatHistory]:
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )


from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DBSession

from app.db.database import get_db
from app.db.crud import session_crud, document_crud

from app.helper.auth_helper import get_current_user_id
from app.schemas.session_schemas import CreateSessionRequest

router = APIRouter()


@router.post("/create")
def create_chat_session(
    body: CreateSessionRequest,
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
   
    target_document = document_crud.get_document_by_id(db, body.document_id)

    if not target_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {body.document_id} not found.",
        )

    if target_document.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this document.",
        )

    new_session = session_crud.create_session(
        db=db,
        user_id=user_id,
        document_id=body.document_id,
        session_name=target_document.filename,
    )

    return {
        "session_id": new_session.id,
        "session_name": new_session.session_name,
        "document_id": body.document_id,
    }


@router.get("/list")
def list_user_sessions(
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    
    user_sessions = session_crud.get_sessions_by_user(db, user_id)

    return [
        {
            "session_id": session.id,
            "session_name": session.session_name,
            "document_id": session.document_id,
            "document_filename": session.document.filename if session.document else "Unknown",
            "created_at": session.created_at.isoformat() if session.created_at else None,
        }
        for session in user_sessions
    ]


@router.delete("/close/{session_id}")
def close_chat_session(
    session_id: int,
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    
    target_session = session_crud.get_session_by_id(db, session_id)

    if not target_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found.",
        )

    if target_session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to close this session.",
        )

    

    return {
        "message": f"Chat closed successfully.",
        "session_id": session_id,
    }
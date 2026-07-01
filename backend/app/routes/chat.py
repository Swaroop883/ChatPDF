

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DBSession

from app.db.database import get_db
from app.db.crud import session_crud, document_crud, chat_crud
from app.core.rag import run_rag_query
from app.core.summariser import run_summary_query
from app.helper.auth_helper import get_current_user_id
from app.schemas.chat_schemas import ChatRequest

router = APIRouter()


@router.post("/chat")
def handle_chat_query(
    body: ChatRequest,
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
   
    allowed_modes = {"rag", "summary"}
    if body.mode not in allowed_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode '{body.mode}'. Must be one of: {allowed_modes}",
        )

    target_session = session_crud.get_session_by_id(db, body.session_id)

    if not target_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {body.session_id} not found.",
        )

    if target_session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to post to this session.",
        )

    linked_document = document_crud.get_document_by_id(db, target_session.document_id)

    if not linked_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The document linked to this session could not be found.",
        )

    print("\n============= CHAT REQUEST =============")
    print("Session ID:", body.session_id)
    print("Question:", body.question)
    print("Requested Mode:", body.mode)
    print("User ID:", user_id)
    print("Linked Document ID:", linked_document.id)
    print("========================================\n")

    if body.mode == "rag":
        pipeline_result = run_rag_query(
            question=body.question,
            document_id=linked_document.id,
        )
    else:
        pipeline_result = run_summary_query(
            question=body.question,
            document_id=linked_document.id,
            pdf_file_path=linked_document.file_path,
        )

    chat_crud.save_chat_message(
        db=db,
        session_id=body.session_id,
        question=body.question,
        answer=pipeline_result["answer"],
        mode_used=pipeline_result["mode"],
        source_chunk=pipeline_result.get("source_chunk"),
    )

    response_data = {
        "answer": pipeline_result["answer"],
        "mode_used": pipeline_result["mode"],
        "source_chunk": pipeline_result.get("source_chunk"),
    }

    if body.mode == "summary":
        response_data["cache_hit"] = pipeline_result.get("cache_hit", False)

    return response_data


@router.get("/history/{session_id}")
def get_session_history(
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
            detail="You do not have permission to view this session's history.",
        )

    all_messages = chat_crud.get_chat_history(db, session_id)

    return {
        "session_id": session_id,
        "session_name": target_session.session_name,
        "messages": [
            {
                "id": msg.id,
                "question": msg.question,
                "answer": msg.answer,
                "mode_used": msg.mode_used,
                "source_chunk": msg.source_chunk,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in all_messages
        ],
    }
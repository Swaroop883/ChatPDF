import shutil
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session as DBSession

from app.config import UPLOAD_DIR
from app.db.database import get_db
from app.db.crud import document_crud
from app.core.embeddings import store_embeddings_for_document
from app.helper.auth_helper import get_current_user_id
from app.helper.document_helper import extract_text_from_pdf_file, split_text_into_chunks

router = APIRouter()


@router.post("/upload")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
 
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted. Please upload a .pdf file.",
        )

    destination_path = UPLOAD_DIR / file.filename

    with open(destination_path, "wb") as output_file:
        shutil.copyfileobj(file.file, output_file)

    full_pdf_text = extract_text_from_pdf_file(destination_path)

    pdf_text_chunks = split_text_into_chunks(full_pdf_text)

    if not pdf_text_chunks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not split the PDF text into chunks. The document may be too short.",
        )

    saved_document = document_crud.create_document(
        db=db,
        user_id=user_id,
        filename=file.filename,
        file_path=str(destination_path),
    )

    store_embeddings_for_document(
        pdf_text_chunks=pdf_text_chunks,
        document_id=saved_document.id,
    )

    return {
        "message": "PDF uploaded and processed successfully.",
        "document_id": saved_document.id,
        "filename": saved_document.filename,
        "chunk_count": len(pdf_text_chunks),
    }


@router.get("/list")
def list_user_documents(
    db: DBSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    
    user_documents = document_crud.get_documents_by_user(db, user_id)

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
        }
        for doc in user_documents
    ]
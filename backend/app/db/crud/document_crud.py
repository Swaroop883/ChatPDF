from sqlalchemy.orm import Session as DBSession
from app.db.models import Document

# Document Operations



def create_document(
    db: DBSession,
    user_id: int,
    filename: str,
    file_path: str,
    file_hash: str,
) -> Document:
    # Called after the PDF has been successfully uploaded and embedded.
    new_document = Document(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_hash=file_hash,
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return new_document



#Used to retrieve the file path for Summary mode.
def get_document_by_id(db: DBSession, document_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()



#Return all documents uploaded by a specific user
def get_documents_by_user(db: DBSession, user_id: int) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )



# return wheather the doc is already present or not using the hash created by the entire contents in the file not just the file name
def get_document_by_hash(
    db: DBSession,
    file_hash: str,
):
    return (
        db.query(Document)
        .filter(Document.file_hash == file_hash)
        .first()
    )
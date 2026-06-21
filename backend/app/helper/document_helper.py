from pathlib import Path
import pdfplumber
from fastapi import HTTPException, status
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text_into_chunks(full_pdf_text: str) -> list[str]:
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    pdf_text_chunks = text_splitter.split_text(full_pdf_text)
    return pdf_text_chunks

def extract_text_from_pdf_file(pdf_file_path: Path) -> str:
    
    all_pages_text = []

    with pdfplumber.open(str(pdf_file_path)) as pdf_document:
        for page in pdf_document.pages:
            page_text = page.extract_text()
            if page_text:
                all_pages_text.append(page_text)

    if not all_pages_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No extractable text found in this PDF. "
                "The file may be a scanned image PDF without a text layer. "
                "Please upload a PDF with selectable text."
            ),
        )

    return "\n\n".join(all_pages_text)
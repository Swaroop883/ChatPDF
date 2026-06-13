

import redis
import pdfplumber
from langchain.schema import HumanMessage
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document as LCDocument
from app.config import get_llm, REDIS_URL




def get_redis_client() -> redis.Redis:
    
    return redis.from_url(REDIS_URL, decode_responses=True)




def extract_full_pdf_text(pdf_file_path: str) -> str:
    
    all_pages_text = []

    with pdfplumber.open(pdf_file_path) as pdf_document:
        for page in pdf_document.pages:
            page_text = page.extract_text()
            if page_text:
                all_pages_text.append(page_text)

    if not all_pages_text:
        raise ValueError(
            f"No extractable text found in '{pdf_file_path}'. "
            "The PDF may be image-only (scanned) with no text layer."
        )

    return "\n\n".join(all_pages_text)




def generate_document_summary(full_pdf_text: str) -> str:
    
    llm = get_llm()

    
    langchain_document = LCDocument(page_content=full_pdf_text)

    
    summarise_chain = load_summarize_chain(llm, chain_type="map_reduce")

    summary_result = summarise_chain.invoke({"input_documents": [langchain_document]})

    
    return summary_result["output_text"]




def run_summary_query(
    question: str,
    document_id: int,
    pdf_file_path: str,
) -> dict:
    
    redis_client = get_redis_client()
    redis_cache_key = f"summary:{document_id}"

    
    cached_summary = redis_client.get(redis_cache_key)
    summary_came_from_cache = cached_summary is not None

    if summary_came_from_cache:
        
        document_summary = cached_summary
    else:
        
        full_pdf_text = extract_full_pdf_text(pdf_file_path)
        document_summary = generate_document_summary(full_pdf_text)

        
        redis_client.setex(
            name=redis_cache_key,
            time=86400,
            value=document_summary,
        )

    
    summary_answer_prompt = (
        f"Using this document summary, answer the question as accurately "
        f"and completely as possible.\n\n"
        f"Summary:\n{document_summary}\n\n"
        f"Question: {question}"
    )

    
    llm = get_llm()
    llm_response = llm.invoke([HumanMessage(content=summary_answer_prompt)])

    return {
        "answer": llm_response.content,
        "source_chunk": None,      
        "mode": "summary",
        "cache_hit": summary_came_from_cache,
    }

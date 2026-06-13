
from langchain.schema import HumanMessage
from app.config import get_llm
from app.core.embeddings import find_similar_chunks


def run_rag_query(question: str, document_id: int) -> dict:
    
    relevant_chunks = find_similar_chunks(
        question_text=question,
        document_id=document_id,
        top_k=3,
    )

    if not relevant_chunks:
        return {
            "answer": "I could not find any relevant information in this document to answer your question.",
            "source_chunk": None,
            "mode": "rag",
        }

    
    combined_context = "\n\n---\n\n".join(relevant_chunks)

    rag_prompt = (
        f"Answer the question using only the context provided. "
        f"If the answer is not in the context, say so clearly. "
        f"Do not invent information.\n\n"
        f"Context:\n{combined_context}\n\n"
        f"Question: {question}"
    )

    
    llm = get_llm()
    llm_response = llm.invoke([HumanMessage(content=rag_prompt)])

    
    answer_text = llm_response.content

    
    primary_source_chunk = relevant_chunks[0]

    return {
        "answer": answer_text,
        "source_chunk": primary_source_chunk,
        "mode": "rag",
    }

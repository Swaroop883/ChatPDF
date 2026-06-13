
import chromadb
from chromadb import PersistentClient
from app.config import get_embedding_model, VECTORSTORE_DIR




def get_chroma_client() -> PersistentClient:
    
    return chromadb.PersistentClient(path=str(VECTORSTORE_DIR))


def get_or_create_collection(chroma_client: PersistentClient):
    
    return chroma_client.get_or_create_collection(
        name="chatpdf_documents",
        metadata={"hnsw:space": "cosine"},  # Use cosine similarity for text
    )



def store_embeddings_for_document(
    pdf_text_chunks: list[str],
    document_id: int,
) -> None:
    
    if not pdf_text_chunks:
        raise ValueError("Cannot store embeddings for an empty chunk list")

    
    embedding_model = get_embedding_model()

    
    chunk_embeddings = embedding_model.embed_documents(pdf_text_chunks)

    
    chunk_ids = [
        f"doc_{document_id}_chunk_{index}"
        for index in range(len(pdf_text_chunks))
    ]

    
    chunk_metadatas = [
        {"document_id": str(document_id)}
        for _ in pdf_text_chunks
    ]

    
    chroma_client = get_chroma_client()
    collection = get_or_create_collection(chroma_client)

    collection.add(
        ids=chunk_ids,
        documents=pdf_text_chunks,
        embeddings=chunk_embeddings,
        metadatas=chunk_metadatas,
    )




def find_similar_chunks(
    question_text: str,
    document_id: int,
    top_k: int = 3,
) -> list[str]:
    
   
    embedding_model = get_embedding_model()
    question_embedding = embedding_model.embed_query(question_text)

    chroma_client = get_chroma_client()
    collection = get_or_create_collection(chroma_client)

    
    similarity_results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        where={"document_id": str(document_id)},
    )

   
    retrieved_chunks = similarity_results["documents"][0]
    return retrieved_chunks




def delete_document_vectors(document_id: int) -> None:
   
    chroma_client = get_chroma_client()
    collection = get_or_create_collection(chroma_client)

    
    existing_entries = collection.get(
        where={"document_id": str(document_id)}
    )

    if existing_entries["ids"]:
        collection.delete(ids=existing_entries["ids"])

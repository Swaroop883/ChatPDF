
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

    print("\n========== STORING EMBEDDINGS ==========")
    print("Document ID:", document_id)
    print("Chunks:", len(pdf_text_chunks))

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

    print("Vectors stored successfully.")
    print("Total vectors in Chroma:", collection.count())

    existing = collection.get(
        where={"document_id": str(document_id)}
    )

    print("Vectors for this document:", len(existing["ids"]))
    print("=======================================\n")



def find_similar_chunks(
    question_text: str,
    document_id: int,
    top_k: int = 3,
) -> list[str]:

    print("\n================ RAG SEARCH ================")
    print("Question:", question_text)
    print("Document ID:", document_id)

    embedding_model = get_embedding_model()
    question_embedding = embedding_model.embed_query(question_text)

    chroma_client = get_chroma_client()
    collection = get_or_create_collection(chroma_client)

    print("Total vectors in Chroma:", collection.count())

    existing = collection.get(
        where={"document_id": str(document_id)}
    )

    print("Vectors belonging to this document:", len(existing["ids"]))

    similarity_results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        where={"document_id": str(document_id)},
    )

    print("\nSimilarity Results:")
    print(similarity_results)

    if (
        not similarity_results["documents"]
        or len(similarity_results["documents"][0]) == 0
    ):
        print("No chunks found!")
        return []

    retrieved_chunks = similarity_results["documents"][0]

    print("\nRetrieved Chunks:")
    for i, chunk in enumerate(retrieved_chunks):
        print(f"\nChunk {i+1}:")
        print(chunk[:300])

    print("===========================================\n")

    return retrieved_chunks





from pydantic import BaseModel

class ChatRequest(BaseModel):
    
    session_id: int
    question: str
    mode: str   # rag or summary
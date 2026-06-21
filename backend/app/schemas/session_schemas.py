from pydantic import BaseModel

class CreateSessionRequest(BaseModel):
    
    document_id: int
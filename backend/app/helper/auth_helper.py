from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, status
from jose import jwt
from passlib.context import CryptContext
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRY_HOURS

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    #hashed using bcrypt and the result is a 60 char string
    return password_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    return password_context.verify(plain_password, hashed_password)

def create_jwt_token(user_id: int, email: str, username: str) -> str:
    # The frontend stores this token in localStorage and sends it
    #in every API request as 'Authorization: Bearer <token>'.
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    token_payload = {
        "sub": str(user_id),      
        "email": email,
        "username": username,
        "exp": expiry_time,
    }
    return jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
        )

def get_current_user_id(request: Request) -> int:
   
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
        )
    token_string = auth_header.split(" ")[1]
    payload = decode_jwt_token(token_string)
    return int(payload["sub"])
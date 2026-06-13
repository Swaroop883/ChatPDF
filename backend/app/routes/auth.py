
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session as DBSession
from jose import jwt
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth

from app.config import (
    JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRY_HOURS,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
)
from app.db.database import get_db
from app.db import crud

router = APIRouter()

# bcrypt context for hashing and verifying passwords
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth client configured with Google's discovery URL
oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)



class RegisterRequest(BaseModel):
    """Expected body for POST /auth/register"""
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Expected body for POST /auth/login"""
    email: EmailStr
    password: str



def hash_password(plain_password: str) -> str:
    
    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    return password_context.verify(plain_password, hashed_password)


def create_jwt_token(user_id: int, email: str, username: str) -> str:
    
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    token_payload = {
        "sub": str(user_id),      # Subject — uniquely identifies the user
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




@router.post("/register")
def register_user(body: RegisterRequest, db: DBSession = Depends(get_db)):
    
    existing_user = crud.get_user_by_email(db, body.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    
    hashed_password = hash_password(body.password)

    crud.create_user(
        db=db,
        username=body.username,
        email=body.email,
        password_hash=hashed_password,
    )

    return {"message": "Account created successfully. You can now log in."}


@router.post("/login")
def login_user(body: LoginRequest, db: DBSession = Depends(get_db)):
    
    user = crud.get_user_by_email(db, body.email)

    
    invalid_credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
    )

    if not user:
        raise invalid_credentials_error

    
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Google Sign-In. Please use the Google button.",
        )

    
    password_is_correct = verify_password(body.password, user.password_hash)
    if not password_is_correct:
        raise invalid_credentials_error

    
    jwt_token = create_jwt_token(user.id, user.email, user.username)
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id,
    }


@router.get("/google")
async def google_login(request: Request):
    
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: DBSession = Depends(get_db)):
   
    google_token = await oauth.google.authorize_access_token(request)
    google_user_info = google_token.get("userinfo")

    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve user information from Google.",
        )

    google_subject_id = google_user_info["sub"]
    user_email = google_user_info["email"]
    user_name = google_user_info.get("name", user_email.split("@")[0])

    
    existing_user = crud.get_user_by_google_id(db, google_subject_id)

    if not existing_user:
        
        existing_user = crud.get_user_by_email(db, user_email)

    if not existing_user:
        
        existing_user = crud.create_user(
            db=db,
            username=user_name,
            email=user_email,
            google_id=google_subject_id,
        )


    jwt_token = create_jwt_token(existing_user.id, existing_user.email, existing_user.username)

    
    redirect_url = f"/frontend/dashboard.html?token={jwt_token}&username={existing_user.username}"
    return RedirectResponse(url=redirect_url)

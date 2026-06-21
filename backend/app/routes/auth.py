
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DBSession
from authlib.integrations.starlette_client import OAuth

from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.db.database import get_db
from app.db.crud import user_crud

from app.schemas.auth_schemas import RegisterRequest, LoginRequest
from app.helper.auth_helper import hash_password, verify_password, create_jwt_token

router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.post("/register")
def register_user(body: RegisterRequest, db: DBSession = Depends(get_db)):
    
    existing_user = user_crud.get_user_by_email(db, body.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    hashed_password = hash_password(body.password)

    user = user_crud.create_user(
        db=db,
        username=body.username,
        email=body.email,
        password_hash=hashed_password,
    )

    jwt_token = create_jwt_token(user.id, user.email, user.username)
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id,
    }


@router.post("/login")
def login_user(body: LoginRequest, db: DBSession = Depends(get_db)):
    
    user = user_crud.get_user_by_email(db, body.email)

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
    # here the below authorize_redirect will create a state value and store it in the session cookie, and then include that state in the redirect URL to Google's OAuth endpoint. When Google redirects back to our callback URL, the state will be included in the request, and authlib will automatically verify that it matches the stored value to protect against CSRF attacks.
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: DBSession = Depends(get_db)):
    

    #google will add a code in the redirect url , then we will take teh code and give it again to google to get the user info
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

    existing_user = user_crud.get_user_by_google_id(db, google_subject_id)

    if not existing_user:
        existing_user = user_crud.get_user_by_email(db, user_email)

    if not existing_user:
        existing_user = user_crud.create_user(
            db=db,
            username=user_name,
            email=user_email,
            google_id=google_subject_id,
        )

    jwt_token = create_jwt_token(existing_user.id, existing_user.email, existing_user.username)

    redirect_url = f"/frontend/dashboard.html?token={jwt_token}&username={existing_user.username}"
    return RedirectResponse(url=redirect_url)
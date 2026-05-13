from fastapi import APIRouter
from fastapi import Request,Depends
from fastapi.responses import RedirectResponse

from authlib.integrations.starlette_client import OAuth
from jose import jwt,JWTError

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from manage_db.user_db_manager import UserDbManager

# --initial setup--
load_dotenv()
router = APIRouter()

# --oauth setup--

oauth = OAuth()
oauth.register(
    name = "google",
    client_id = os.getenv("GOOGLE_CLIENT_ID"),
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs = {
        "scope" : "openid email profile"
    }
)

# --jws helpers--
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

def create_jwt(user_id:str):
    pay_load = {
                "user_id" : user_id,
                "exp": datetime.utcnow() + timedelta(days=7)
                }
    return jwt.encode(pay_load,JWT_SECRET,ALGORITHM)

def verify_jwt(token:str):
    try:
        pay_load = jwt.decode(token,JWT_SECRET,algorithms=[ALGORITHM])
        return pay_load["user_id"]
    except JWTError:
        return None

# --api--

# -login route-

@router.get("/login")
async def login(request:Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request,redirect_uri)

@router.get("/callback")
async def auth_callback(request:Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    email = user_info["email"]
    google_sub = user_info["sub"]
    db = UserDbManager()
    user_id = db.insert_user(email,google_sub)
    db.close_conn()

    jwt_token = create_jwt(str(user_id))

    response = RedirectResponse("http://localhost:8501/") # the front page url
    response.set_cookie(
        key="session",
        value= jwt_token,
        httponly=True,
        samesite="lax"
    )
    return response


# --test--

def get_current_user(request: Request):
    token = request.cookies.get("session")
    if not token:
        return None

    user_id = verify_jwt(token)
    return user_id

@router.get("/me")
def me(user_id: str = Depends(get_current_user)):
    if not user_id:
        return {"error": "Not authenticated"}
    return {"user_id": user_id}


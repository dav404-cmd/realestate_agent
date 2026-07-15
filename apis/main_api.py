from fastapi import FastAPI
from apis.data_querying import lifespan
from apis.data_querying import router as query_router
from apis.auth import router as auth_router
from apis.agent_api import router as agent_router
from apis.user_pref_api import router as pref_router

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("JWT_SECRET")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(query_router,prefix="/query")
app.include_router(auth_router,prefix="/auth")
app.include_router(agent_router,prefix="/agent")
app.include_router(pref_router,prefix="/pref")
from fastapi import FastAPI
from ui.backend.apis.data_querying import lifespan
from ui.backend.apis.data_querying import router as query_router
from ui.backend.apis.auth import router as auth_router

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
        "http://localhost:5173",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(query_router,prefix="/query")
app.include_router(auth_router,prefix="/auth")
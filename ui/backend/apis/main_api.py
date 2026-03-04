from fastapi import FastAPI
from ui.backend.apis.data_querying import lifespan
from ui.backend.apis.data_querying import router as query_router
from ui.backend.apis.auth import router as auth_router

from starlette.middleware.sessions import SessionMiddleware
import os


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key = os.getenv("JWT_SECRET")
)

app.include_router(query_router,prefix="/query")
app.include_router(auth_router,prefix="/auth")
from fastapi import FastAPI
from ui.backend.apis.data_querying import lifespan
from ui.backend.apis.data_querying import router as query_router


app = FastAPI(lifespan=lifespan)

app.include_router(query_router,prefix="/query")
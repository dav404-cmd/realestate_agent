from fastapi import APIRouter

router = APIRouter()

@router.get("/api_active")
def check_if_active():
    return {"status" : "ok"}
from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard():
    return {"response": "Dashboard Page"}

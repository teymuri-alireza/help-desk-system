from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

# Authentication
@router.post("/signup")
def sign_up():
    return {"response": "Sign Up Page"}

@router.post("/login")
def log_in():
    return {"response": "Log In Page"}

# Session management
@router.get("/me")
def session_information():
    return {"response": "Session Information Page"}

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/auth", tags=["auth"])

# Serve the authentication page
@router.get("")
def authentication(request: Request):
    return templates.TemplateResponse(request=request, name="auth.html")

# API endpoints
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

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/auth", tags=["auth"])

# Create temporary session to manage errors
temp_session = {}

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
def log_in(request: Request, username: str = Form(...)):
    helpdesk = get_helpdesk()
    user_exist = helpdesk.authentication_api(action="login", username=username)
    if user_exist:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    else:
        global temp_session
        temp_session["error"] = "کاربر یافت نشد"
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

# Session management
@router.get("/me")
def session_information():
    return {"response": "Session Information Page"}

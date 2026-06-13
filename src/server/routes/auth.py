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
    error = temp_session.pop("error", None)
    return templates.TemplateResponse(request=request, name="auth.html", context={"request": request, "error": error})

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
        token = create_access_token({"sub": username})
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax"
        )
        return response
    else:
        global temp_session
        temp_session["error"] = "کاربر یافت نشد"
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

# Session management
@router.get("/me")
def session_information():
    return {"response": "Session Information Page"}

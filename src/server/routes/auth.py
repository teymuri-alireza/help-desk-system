from fastapi import APIRouter, Request, Response, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, create_access_token, get_current_user
from src.database.tables import User, Role, Notification

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/auth", tags=["auth"])


# Serve the authentication page
@router.get("")
def authentication(request: Request):
    try:
        logged_in_user = get_current_user(request=request)
        if logged_in_user:
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    except:
        login_error = request.session.pop("login_error", None)
        signup_error = request.session.pop("signup_error", None)
        response = templates.TemplateResponse(
            request=request, 
            name="auth.html", 
            context={"request": request, "signup_error": signup_error, "login_error": login_error})
        response.delete_cookie(key="signup_error")
        return response

# API endpoints
# Authentication
@router.post("/signup")
def sign_up(request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    ):
    try:
        helpdesk = get_helpdesk()
        user_exist = helpdesk.admin_api.find_user_by_username(username=username)
        if user_exist:
            redirect = RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
            request.session["signup_error"] = "این نام کاربری قبلا استفاده شده است."
            return redirect

        new_user = User(name=name, username=username, email=email, role=Role.STUDENT)
        helpdesk.authentication_api.signup(user=new_user)

        found_user = helpdesk.admin_api.find_user_by_username(username=username)
        notification = Notification(receiver_id=found_user.id, title="کاربر جدید", text=f"خوش آمدید {found_user.name}")
        helpdesk.notification_api.new_notification(notification=notification)

        token = create_access_token({"sub": username})
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax"
        )
        return response
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/login")
def log_in(request: Request, username: str = Form(...)):
    try:
        helpdesk = get_helpdesk()
        user_exist = helpdesk.authentication_api.login(username=username)
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
            response = RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
            request.session["login_error"] = "کاربر یافت نشد."
            return response
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/logout")
def log_out(response: Response):
    response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie("access_token")

    return response

# Session management
@router.get("/me")
def session_information():
    return {"response": "Session Information Page"}

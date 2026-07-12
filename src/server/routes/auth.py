from fastapi import APIRouter, Request, Response, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, create_access_token, get_current_user
from src.database.tables import User, Role, Notification

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/auth", tags=["auth"])


# Serve the authentication page
@router.get("", description="Serves the frontend page for authentication")
def authentication(request: Request):
    try:
        user_username = get_current_user(request=request)
        if user_username:
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
@router.post("/signup", description="Creates access token using JWT for user registration.")
def sign_up(request: Request,
    name: str = Form(..., description="User's full name."),
    username: str = Form(..., description="User's username used for authentication."),
    email: str = Form(..., description="User's unique e-mail address."),
    ):
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=username)
        if current_user:
            redirect = RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
            request.session["signup_error"] = "این نام کاربری قبلا استفاده شده است."
            return redirect

        new_user = User(name=name, username=username, email=email, role=Role.STUDENT)
        helpdesk.authentication_api.signup(user=new_user)

        notification = Notification(receiver_id=new_user.id, title="کاربر جدید", text=f"خوش آمدید {new_user.name}", url=f"/users/{new_user.id}")
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

@router.post("/login", description="Creates access token using JWT for user login.")
def log_in(request: Request, username: str = Form(..., description="User's username used for authentication")):
    try:
        helpdesk = get_helpdesk()
        user_exist = helpdesk.authentication_api.login(username=username)
        if user_exist:
            is_user_suspended = not helpdesk.authentication_api.validate_user_status(username=username)
            if is_user_suspended:
                response = RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
                request.session["login_error"] = "این نام کابری مسدود شده است. امکان ورود وجود ندارد."
                return response

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
            response = RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
            request.session["login_error"] = "کاربر یافت نشد."
            return response
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/logout", description="Removes the user access token to logout.")
def log_out(response: Response):
    response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie("access_token")

    return response

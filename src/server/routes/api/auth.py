from fastapi import APIRouter, Form, HTTPException, status, Request
from fastapi.responses import JSONResponse
from src.database.tables import Notification, Role, User
from src.server.dependencies import create_access_token, set_access_cookie, clear_access_cookie, get_current_user, get_helpdesk

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, description="Register a new user.")
def signup(
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
):
    helpdesk = get_helpdesk()

    if helpdesk.admin_api.find_user_by_username(username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.")

    try:
        user = User(name=name, username=username, email=email, role=Role.STUDENT)
        helpdesk.authentication_api.signup(user)

        notification = Notification(receiver_id=user.id, title="کاربر جدید", text=f"خوش آمدید {user.name}", url=f"/users/{user.id}")
        helpdesk.notification_api.new_notification(notification)

        response = JSONResponse(
            content={
                "success": True,
                "message": "User registered successfully.",
            },
            status_code=status.HTTP_201_CREATED,
        )

        token = create_access_token({"sub": username})
        set_access_cookie(response, token)

        return response

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")


@router.post("/login", description="Authenticate a user.")
def login(username: str = Form(...)):
    helpdesk = get_helpdesk()

    try:
        if not helpdesk.authentication_api.login(username):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

        if not helpdesk.authentication_api.validate_user_status(username):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been suspended.")

        response = JSONResponse(
            content={
                "success": True,
                "message": "Logged in successfully.",
            }
        )

        token = create_access_token({"sub": username})
        set_access_cookie(response, token)

        return response

    except HTTPException:
        raise

    except Exception:
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")


@router.post("/logout", description="Logout current user.")
def logout():
    response = JSONResponse(
        content={
            "success": True,
            "message": "Logged out successfully.",
        }
    )

    clear_access_cookie(response)

    return response


@router.get("/me", description="Retrieve user's information.")
def get_current_user_info(request: Request):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    current_user = helpdesk.admin_api.find_user_by_username(user)

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return JSONResponse(
        content={
            "user_id": current_user.id,
            "user_username": current_user.username,
            "user_role": current_user.role.value,
        },
        status_code=status.HTTP_200_OK,
    )

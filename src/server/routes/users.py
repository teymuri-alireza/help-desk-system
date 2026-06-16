from fastapi import APIRouter, Request, status, Path, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_helpdesk, get_current_user, get_static_path
from src.database.tables import Role, User, UserStatus

TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(request: Request):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        users_list = helpdesk.admin_api(action="list_users")
        context = {
            "request": request,
            "users_list": users_list,
        }
        response = templates.TemplateResponse(
            request=request,
            name="users.html",
            context=context
        )
        return response
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

@router.get("/{user_id}")
def show_user(request: Request, user_id: int = Path(...)):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)
    # Check if user is admin first
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        user_to_show = helpdesk.admin_api(action="find_user", user_id=user_id)
        if user_to_show is not None:
            context = {
                "request": request,
                "user": user_to_show,
                "Role": Role,
                "UserStatus": UserStatus,
            }
            response = templates.TemplateResponse(
                request=request,
                name="show_user.html",
                context=context
            )
            return response
        else:
            return templates.TemplateResponse(
                request=request,
                name="show_user.html",
            )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.post("")
def new_user():
    return {"response": "New User Page"}

@router.patch("/{user_id}")
def patch_user(
        request: Request, 
        user_id: int = Path(...), 
        name: str = Form(...), 
        email: str = Form(...), 
        username: str = Form(...), 
        role: str = Form(...), 
        user_status: str = Form(...)
    ):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)
    # Check if user is admin first
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        user_to_update = User(name=name, email=email, username=username, role=role, status=user_status)
        helpdesk.admin_api("update_user", user=user_to_update, user_id=user_id)
        return RedirectResponse(url=f"/users/{user_id}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(request: Request, user_id: int = Path(...)):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)
    # Check if user is admin first
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        helpdesk.admin_api(action="delete_user", user_id=user_id)
        # return RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

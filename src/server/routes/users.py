from fastapi import APIRouter, Request, status, Path, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_helpdesk, get_current_user, get_static_path
from src.database.tables import Role, User, UserStatus, Notification

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
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        users_list = helpdesk.admin_api.list_users()
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
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
    # Check if user is admin first
    if found_user is not None:
        if found_user.role == Role.SYSTEM_ADMIN or found_user.id == user_id:
            user_to_show = helpdesk.admin_api.find_user(user_id=user_id)
            if user_to_show is not None:
                update_user_flash_message = request.cookies.get("update_user_flash_message")
                context = {
                    "request": request,
                    "user": user_to_show,
                    "Role": Role,
                    "user_role": found_user.role.value,
                    "UserStatus": UserStatus,
                    "update_user_flash_message": update_user_flash_message,
                }
                response = templates.TemplateResponse(
                    request=request,
                    name="show_user.html",
                    context=context
                )
                response.delete_cookie("update_user_flash_message")
                return response
            else:
                return templates.TemplateResponse(
                    request=request,
                    name="show_user.html",
                )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.post("")
def new_user(
        request: Request,
        name: str = Form(...),
        username: str = Form(...),
        email: str = Form(...),
        role: str = Form(...)
    ):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
    # Check if user is admin first
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        new_user = User(name=name, email=email, username=username, role=role)
        helpdesk.admin_api.new_user(user=new_user)

        found_user = helpdesk.admin_api.find_user_by_username(username=username)
        notification = Notification(receiver_id=found_user.id, title="کاربر جدید", text=f"خوش آمدید {found_user.name}")
        helpdesk.notification_api.new_notification(notification=notification)

        redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        redirect.set_cookie(key="new_user_flash_message", value="successful")
        return redirect
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


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
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
    # Check if user is admin first
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        user_to_update = User(name=name, email=email, username=username, role=role, status=user_status)
        helpdesk.admin_api.update_user(new_user=user_to_update, old_user_id=user_id)

        redirect = RedirectResponse(url=f"/users/{user_id}", status_code=status.HTTP_303_SEE_OTHER)
        redirect.set_cookie(key="update_user_flash_message", value="successful")
        return redirect
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(request: Request, user_id: int = Path(...)):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
    # Check if user is admin first
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        helpdesk.admin_api.delete_user(user_id=user_id)
        return RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

import logging
from fastapi import APIRouter, Request, status, Path, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_helpdesk, get_current_user, get_static_path
from src.database.tables import Role, User, UserStatus, Notification

core_logger = logging.getLogger("core")
TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(request: Request):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if current_user is not None and current_user.role == Role.SYSTEM_ADMIN:
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
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{user_id}")
def show_user(request: Request, user_id: int = Path(...)):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        # Check if user is admin first
        if current_user is not None:
            if current_user.role == Role.SYSTEM_ADMIN or current_user.id == user_id:
                user_to_show = helpdesk.admin_api.find_user(user_id=user_id)
                if user_to_show is not None:
                    update_user_flash_message = request.cookies.get("update_user_flash_message")
                    context = {
                        "request": request,
                        "user": user_to_show,
                        "Role": Role,
                        "user_role": current_user.role.value,
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
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


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
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        # Check if user is admin first
        if current_user is not None and current_user.role == Role.SYSTEM_ADMIN:
            new_user_exist = helpdesk.admin_api.find_user_by_username(username=username)
            if new_user_exist is not None:
                redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
                redirect.set_cookie(key="user_exists_flash_message", value="successful")
                return redirect

            new_user = User(name=name, email=email, username=username, role=role)
            helpdesk.admin_api.new_user(user=new_user)

            notification = Notification(receiver_id=new_user.id, title="کاربر جدید", text=f"خوش آمدید {new_user.name}")
            helpdesk.notification_api.new_notification(notification=notification)

            redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
            redirect.set_cookie(key="new_user_flash_message", value="successful")
            return redirect
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{user_id}")
def patch_user(
        request: Request, 
        user_id: int = Path(...), 
        name: str | None = Form(None), 
        email: str | None = Form(None), 
        username: str | None = Form(None), 
        role: str | None = Form(None), 
        user_status: str | None = Form(None)
    ):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        # Check if user is admin first
        if current_user is not None:
            if current_user.role == Role.SYSTEM_ADMIN or current_user.id == user_id:
                user_to_update = User(name=name, email=email, username=username, role=role, status=user_status)
                helpdesk.admin_api.update_user(new_user=user_to_update, old_user_id=user_id)

                redirect = RedirectResponse(url=f"/users/{user_id}", status_code=status.HTTP_303_SEE_OTHER)
                redirect.set_cookie(key="update_user_flash_message", value="successful")
                return redirect

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(request: Request, user_id: int = Path(...)):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        # Check if user is admin first
        if current_user is not None and current_user.role == Role.SYSTEM_ADMIN:
            helpdesk.admin_api.delete_user(user_id=user_id)
            return RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

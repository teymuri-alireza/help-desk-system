import logging
from fastapi import APIRouter, Body, status, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user

core_logger = logging.getLogger("core")
TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_unread_notifications(request: Request):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        notifications_list = helpdesk.notification_api.list_unread(receiver_id=found_user.id)
        
        count_notifications = None
        if notifications_list is not None:
            count_notifications = len(notifications_list)

        return {"response": notifications_list, "count_notifications": count_notifications}
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/all")
def list_all_notifications(request: Request):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        notifications_list = helpdesk.notification_api.list_all(receiver_id=found_user.id)
        return templates.TemplateResponse(
            request=request,
            name="notifications.html",
            status_code=status.HTTP_200_OK, 
            context={
                "request": request,
                "notifications_list": notifications_list,
                "user_id": found_user.id,
                "role": found_user.role.value,
            }
        )
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("", status_code=status.HTTP_200_OK)
def update_notification(notification_id: int = Body(...), is_read: bool = Body(...)):
    try:
        helpdesk = get_helpdesk()
        helpdesk.notification_api.update_notification(notification_id=notification_id, is_read=is_read)
        return {"response": "ok"}
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

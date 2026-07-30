import logging
from fastapi import APIRouter, Body, status, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user

core_logger = logging.getLogger("core")
TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", description="Retrieve list of unread notifications")
def list_unread_notifications(request: Request):
    user = get_current_user(request=request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        notifications_list = helpdesk.notification_api.list_unread(receiver_id=current_user.id)

        unread_count = None
        if notifications_list is not None:
            unread_count = len(notifications_list)

        return JSONResponse(
            content={
                "notifications": [{
                    "title": n.title,
                    "text": n.text,
                    "id": n.id,
                    "url": n.url,
                } for n in notifications_list],
                "unread_count": unread_count
            },
            status_code=status.HTTP_200_OK,
        )

    except HTTPException:
        raise

    except Exception as e:
        core_logger.error(f"Unexpected error in notification API: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/all", description="Retrieve list of all notifications.")
def list_all_notifications(request: Request):
    user = get_current_user(request=request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        notifications_list = helpdesk.notification_api.list_all(receiver_id=current_user.id)
        return JSONResponse(
            content={
                "notifications": [{
                    "title": n.title,
                    "text": n.text,
                    "id": n.id,
                    "url": n.url,
                    "is_read": n.is_read,
                    "created_at": n.created_at.isoformat(),
                } for n in notifications_list],
            },
            status_code=status.HTTP_200_OK,
        )

    except HTTPException:
        raise

    except Exception as e:
        core_logger.error(f"Unexpected error in notification API: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("", status_code=status.HTTP_200_OK, description="Mark a notification as read.")
def update_notification(request: Request, notification_id: int = Body(...), is_read: bool = Body(...)):
    user = get_current_user(request=request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        found_notification = helpdesk.notification_api.find_notification(notification_id=notification_id)
        if found_notification is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        if current_user.id != found_notification.receiver_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        helpdesk.notification_api.update_notification(notification_id=notification_id, is_read=is_read)

        return {"response": "ok"}

    except HTTPException:
        raise

    except Exception as e:
        core_logger.error(f"Unexpected error in notification API: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

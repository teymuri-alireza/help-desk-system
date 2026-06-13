from fastapi import APIRouter, Body, status, Request
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_unread_notifications():
    help_desk = get_helpdesk()
    # FUTURE WORK: user_id should be fetched from session
    notifications_list = help_desk.notification_api(action="list_unread", user_id=1)
    return {"response": notifications_list}


@router.get("/all")
def list_all_notifications(request: Request):
    help_desk = get_helpdesk()
    # FUTURE WORK: user_id should be fetched from session
    notifications_list = help_desk.notification_api(action="list_all", user_id=1)
    return templates.TemplateResponse(
        request=request,
        name="notifications.html",
        status_code=status.HTTP_200_OK, 
        context={"request": request, "notifications_list": notifications_list}
    )


@router.patch("", status_code=status.HTTP_200_OK)
def update_notification(notification_id: int = Body(...), is_read: bool = Body(...)):
    help_desk = get_helpdesk()
    help_desk.notification_api(action="update", notification_id=notification_id, is_read=is_read)
    return {"response": "ok"}

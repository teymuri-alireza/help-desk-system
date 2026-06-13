from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(request: Request):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)

    if found_user is not None:

        users_list = helpdesk.admin_api(action="list_users")
        tickets_list = helpdesk.ticket_api(action="list")
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={"request": request, "users_list": users_list, "tickets_list": tickets_list, "user_username": found_user.username, "user_id": found_user.id}
            )
    else:
        return {"response": "not found"}

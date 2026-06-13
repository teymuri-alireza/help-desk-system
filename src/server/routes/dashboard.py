from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(request: Request):
    helpdesk = get_helpdesk()
    users_list = helpdesk.admin_api(action="list_users")
    tickets_list = helpdesk.ticket_api(action="list")
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request, "users_list": users_list, "tickets_list": tickets_list}
        )

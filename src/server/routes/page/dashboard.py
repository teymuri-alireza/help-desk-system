from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user_optional
from src.database.tables import Role

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", description="Serves the frontend page for dashboard")
def dashboard(request: Request):
    user = get_current_user_optional(request=request)

    if not user:
        return RedirectResponse(url="/auth")

    helpdesk = get_helpdesk()
    current_user = helpdesk.admin_api.find_user_by_username(username=user)

    if current_user.role in (Role.STUDENT, Role.EMPLOYEE):
        html_file = "user_dashboard.html"

    elif current_user.role == Role.IT_EXPERT:
        html_file = "it_expert_dashboard.html"

    else:
        html_file = "admin_dashboard.html"

    response = templates.TemplateResponse(request=request, name=html_file)
    return response


@router.get("/stats", description="Serves the frontend page for statistics")
def stats(request: Request):
    user = get_current_user_optional(request=request)

    if user:
        return templates.TemplateResponse(request=request, name="statistics.html")

    return RedirectResponse(url="/auth")

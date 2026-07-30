from fastapi import APIRouter, Request, Path
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_current_user_optional, get_static_path

TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", description="Users page")
def list_users(request: Request):
    user = get_current_user_optional(request=request)

    if user:
        return templates.TemplateResponse(request=request, name="users.html")

    return RedirectResponse(url="/auth")


@router.get("/{user_id}", description="A user's page")
def show_user(request: Request, user_id: int = Path(...)):
    user = get_current_user_optional(request=request)

    if user:
        return templates.TemplateResponse(request=request, name="show_user.html")

    return RedirectResponse(url="/auth")

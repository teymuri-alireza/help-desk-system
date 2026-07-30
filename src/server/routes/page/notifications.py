import logging
from fastapi import APIRouter, Body, status, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user_optional

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/all", description="Returns a list of all notifications.")
def list_all_notifications(request: Request):
    user = get_current_user_optional(request=request)

    if user:
        return templates.TemplateResponse(request=request, name="notifications.html")

    return RedirectResponse(url="/auth")

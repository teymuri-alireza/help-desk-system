import logging
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_current_user_optional

core_logger = logging.getLogger("core")
TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", description="Tickets page")
def list_tickets(request: Request):
    user = get_current_user_optional(request=request)

    if user:
        return templates.TemplateResponse(request=request, name="tickets.html")

    return RedirectResponse(url="/auth")


@router.get("/{ticket_id}", description="A ticket's page")
def show_ticket(request: Request):
    user = get_current_user_optional(request=request)

    if user:
        return templates.TemplateResponse(request=request, name="show_ticket.html")

    return RedirectResponse(url="/auth")

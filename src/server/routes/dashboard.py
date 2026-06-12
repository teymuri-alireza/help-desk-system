from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

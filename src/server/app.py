from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_swagger import patch_fastapi
from contextlib import asynccontextmanager
from src.server.routes.auth import router as auth_router
from src.server.routes.tickets import router as tickets_router
from src.server.routes.responses import router as responses_router
from src.server.routes.dashboard import router as dashboard_router
from src.server.routes.users import router as users_router
from src.server.routes.notifications import router as notifications_router
from src.server.dependencies import get_static_path, set_helpdesk
from src.core.engine import HelpDeskCore

TEMPLATES_DIR, STATIC_DIR = get_static_path()

@asynccontextmanager
async def lifespan(app: FastAPI):

    core = HelpDeskCore()
    set_helpdesk(core)

    yield

# Patch FastAPI to serve Swagger UI locally
app = FastAPI(docs_url=None, swagger_ui_oauth2_redirect_url=None, lifespan=lifespan)
patch_fastapi(app=app, redirect_from_root_to_docs=False)

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Home Page
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(responses_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(notifications_router)

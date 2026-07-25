import csv
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_swagger import patch_fastapi
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from src.server.routes.page.auth import router as page_auth_router
from src.server.routes.api.auth import router as api_auth_router
from src.server.routes.page.tickets import router as page_tickets_router
from src.server.routes.api.tickets import router as api_tickets_router
from src.server.routes.api.responses import router as api_responses_router
from src.server.routes.page.dashboard import router as page_dashboard_router
from src.server.routes.api.dashboard import router as api_dashboard_router
from src.server.routes.page.users import router as page_users_router
from src.server.routes.api.users import router as api_users_router
from src.server.routes.page.notifications import router as page_notifications_router
from src.server.routes.api.notifications import router as api_notifications_router
from src.server.routes.contents import router as contents_router
from src.server.dependencies import get_static_path, set_helpdesk, get_helpdesk, get_current_user
from src.core.engine import HelpDeskCore
from src.utilities.logger import get_logger

TEMPLATES_DIR, STATIC_DIR = get_static_path()
DATA_DIR = Path(__file__).parent.parent / "data"

@asynccontextmanager
async def lifespan(app: FastAPI):

    core = HelpDeskCore()
    set_helpdesk(core)

    # Initialize the core logger
    core_logger = get_logger()

    yield

# Patch FastAPI to serve Swagger UI locally
app = FastAPI(docs_url=None, swagger_ui_oauth2_redirect_url=None, lifespan=lifespan)
patch_fastapi(app=app, redirect_from_root_to_docs=False)
app.add_middleware(
    SessionMiddleware,
    secret_key="placeholder_for_secret_key"
)

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Home Page
@app.get("/", response_class=HTMLResponse, description="Serves the frontend for home page")
def root(request: Request):
    context = None
    try:
        user_username = get_current_user(request=request)

        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        context = {"user": current_user}
    except:
        # Use default value for context
        pass
    return templates.TemplateResponse(request=request, name="home.html", context=context)

# Courses Page
@app.get("/courses", response_class=HTMLResponse, description="Serves the frontend for courses page")
def courses(request: Request):
    context = {}
    try:
        user_username = get_current_user(request=request)

        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        context = {"user": current_user}
    except:
        pass
    with open(DATA_DIR / "courses.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        context["courses_data"] = [
            {
                "code": row[0],
                "name": row[1],
                "department": row[2],
                "professor": row[3],
                "credits": row[4],
                "semester": row[5],
                "capacity": row[6],
                "description": row[7],
            }
            for row in reader
        ]
    return templates.TemplateResponse(request=request, name="courses.html", context=context)

# Forbidden page
@app.get("/forbidden", description="Redirect user to the custom 403 page. This endpoint is used in JavaScript code, if necessary")
def forbidden(request: Request):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

app.include_router(page_auth_router)
app.include_router(api_auth_router)
app.include_router(page_tickets_router)
app.include_router(api_tickets_router)
app.include_router(api_responses_router)
app.include_router(page_dashboard_router)
app.include_router(api_dashboard_router)
app.include_router(page_users_router)
app.include_router(api_users_router)
app.include_router(page_notifications_router)
app.include_router(api_notifications_router)
app.include_router(contents_router)

@app.exception_handler(403)
def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request,
        name="403.html",
        context={"request": request},
        status_code=status.HTTP_403_FORBIDDEN
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request,
        name="404.html",
        context={"request": request},
        status_code=status.HTTP_404_NOT_FOUND
    )

@app.exception_handler(500)
async def server_errors(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request,
        name="500.html",
        context={"request": request},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

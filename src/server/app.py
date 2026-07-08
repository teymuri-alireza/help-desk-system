import csv
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_swagger import patch_fastapi
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from src.server.routes.auth import router as auth_router
from src.server.routes.tickets import router as tickets_router
from src.server.routes.responses import router as responses_router
from src.server.routes.dashboard import router as dashboard_router
from src.server.routes.users import router as users_router
from src.server.routes.notifications import router as notifications_router
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
@app.get("/", response_class=HTMLResponse)
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
@app.get("/courses", response_class=HTMLResponse)
def courses(request: Request):
    context = {}
    try:
        user_username = get_current_user(request=request)

        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        context = {"user": current_user}
    except:
        pass
    with open(DATA_DIR / "courses.csv", "r", newline="") as file:
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
@app.get("/forbidden")
def forbidden(request: Request):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(responses_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(notifications_router)

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

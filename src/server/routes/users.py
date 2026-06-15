from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_helpdesk, get_current_user, get_static_path
from src.database.tables import Role

TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(request: Request):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        users_list = helpdesk.admin_api(action="list_users")
        context = {
            "request": request,
            "users_list": users_list,
        }
        response = templates.TemplateResponse(
            request=request,
            name="users.html",
            context=context
        )
        return response
    else:
        return {"response": "not found"}

@router.get("/{user_id}")
def show_user():
    return {"response": "Show User Page"}

@router.post("")
def new_user():
    return {"response": "New User Page"}

@router.patch("/{user_id}")
def patch_user():
    return {"response": "Patch User Page"}

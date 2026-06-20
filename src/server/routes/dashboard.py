from fastapi import APIRouter, Request, status, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user
from src.database.tables import Role

TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(request: Request, response: Response):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)

    if found_user is not None:
        new_ticket_flash_message = request.cookies.get("new_ticket_flash_message")
        new_user_flash_message = request.cookies.get("new_user_flash_message")
        if found_user.role == Role.STUDENT or found_user.role == Role.EMPLOYEE:
            tickets_list = helpdesk.ticket_api.list_tickets(creator_id=found_user.id, limit=10)
            context = {
                    "request": request,
                    "user_username": found_user.username, 
                    "user_id": found_user.id,
                    "tickets_list": tickets_list,
                    "new_ticket_flash_message": new_ticket_flash_message,
                    }
            html_file = "user_dashboard.html"
        else:
            tickets_list = helpdesk.ticket_api.list_tickets(limit=10)
            users_list = helpdesk.admin_api.list_users(limit=10)
            context = {
                "request": request,
                "user_username": found_user.username, 
                "user_id": found_user.id,
                "users_list": users_list,
                "tickets_list": tickets_list,
                "new_ticket_flash_message": new_ticket_flash_message,
                "new_user_flash_message": new_user_flash_message,
                "Role": Role,
                }
            html_file = "admin_dashboard.html"
 
        response = templates.TemplateResponse(
            request=request,
            name=html_file,
            context=context
        )
        response.delete_cookie("new_ticket_flash_message")
        response.delete_cookie("new_user_flash_message")
        return response

    else:
        # Error handler for when db is removed but session exists
        return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)

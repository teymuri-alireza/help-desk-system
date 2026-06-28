import logging
from fastapi import APIRouter, Request, status, Response, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user
from src.database.tables import Role

core_logger = logging.getLogger("core")
TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(request: Request, response: Response):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)

        if current_user is not None:
            new_ticket_flash_message = request.cookies.get("new_ticket_flash_message")
            new_user_flash_message = request.cookies.get("new_user_flash_message")
            user_exists_flash_message = request.cookies.get("user_exists_flash_message")
            if current_user.role == Role.STUDENT or current_user.role == Role.EMPLOYEE:
                tickets_list = helpdesk.ticket_api.list_tickets(creator_id=current_user.id, limit=10)
                context = {
                        "request": request,
                        "user_username": current_user.username, 
                        "user_id": current_user.id,
                        "tickets_list": tickets_list,
                        "new_ticket_flash_message": new_ticket_flash_message,
                        }
                html_file = "user_dashboard.html"
            elif current_user.role == Role.IT_EXPERT:
                tickets_list = helpdesk.ticket_api.list_tickets(assigned_to=current_user.id, limit=10)
                assigned_tickets, open_tickets, resolved_tickets = helpdesk.statistics_api.it_expert_stats(it_expert_id=current_user.id)
                context = {
                        "request": request,
                        "user_username": current_user.username, 
                        "user_id": current_user.id,
                        "tickets_list": tickets_list,
                        "assigned_tickets": assigned_tickets,
                        "open_tickets": open_tickets,
                        "resolved_tickets": resolved_tickets,
                        "new_ticket_flash_message": new_ticket_flash_message,
                        }
                html_file = "it_expert_dashboard.html"
            elif current_user.role == Role.HELP_DESK_MANAGER:
                tickets_list = helpdesk.ticket_api.list_tickets(limit=10)
                all_tickets_count, active_tickets_count, not_assigned_tickets, last_created = helpdesk.statistics_api.ticket_stats()
                context = {
                    "request": request,
                    "user_username": current_user.username, 
                    "user_id": current_user.id,
                    "user_role": current_user.role.value,
                    "tickets_list": tickets_list,
                    "all_tickets_count": all_tickets_count,
                    "active_tickets_count": active_tickets_count,
                    "not_assigned_tickets": not_assigned_tickets,
                    "last_created": last_created,
                    "new_ticket_flash_message": new_ticket_flash_message,
                    "Role": Role,
                    }
                html_file = "admin_dashboard.html"
            else:
                tickets_list = helpdesk.ticket_api.list_tickets(limit=10)
                users_list = helpdesk.admin_api.list_users(limit=10)
                all_tickets_count, active_tickets_count, not_assigned_tickets, last_created = helpdesk.statistics_api.ticket_stats()
                all_users_count, active_users_count = helpdesk.statistics_api.users_stats()
                context = {
                    "request": request,
                    "user_username": current_user.username, 
                    "user_id": current_user.id,
                    "users_list": users_list,
                    "tickets_list": tickets_list,
                    "all_tickets_count": all_tickets_count,
                    "active_tickets_count": active_tickets_count,
                    "not_assigned_tickets": not_assigned_tickets,
                    "last_created": last_created,
                    "all_users_count": all_users_count,
                    "active_users_count": active_users_count,
                    "new_ticket_flash_message": new_ticket_flash_message,
                    "new_user_flash_message": new_user_flash_message,
                    "user_exists_flash_message": user_exists_flash_message,
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
            response.delete_cookie("user_exists_flash_message")
            return response

        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/stats")
def stats(request: Request):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if current_user.role not in (Role.SYSTEM_ADMIN, Role.IT_MANAGER, Role.HELP_DESK_MANAGER):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        all_tickets_count, active_tickets_count, not_assigned_tickets, last_created = helpdesk.statistics_api.ticket_stats()
        all_users_count, active_users_count = helpdesk.statistics_api.users_stats()
        # Only generate user role pie chart for system admins
        if current_user.role == Role.SYSTEM_ADMIN:
            helpdesk.statistics_api.users_role_pie_chart()
        helpdesk.statistics_api.tickets_status_bar_chart()
        helpdesk.statistics_api.it_experts_performance_bar_chart()
        context = {
            "request": request,
            "user_username": current_user.username, 
            "user_id": current_user.id,
            "user_role": current_user.role.value,
            "all_tickets_count": all_tickets_count,
            "active_tickets_count": active_tickets_count,
            "not_assigned_tickets": not_assigned_tickets,
            "last_created": last_created,
            "all_users_count": all_users_count,
            "active_users_count": active_users_count,
        }
        return templates.TemplateResponse(
            request=request,
            name="statistics.html",
            context=context
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

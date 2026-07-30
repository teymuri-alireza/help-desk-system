import os
import logging
from pathlib import Path as FilePath
from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from src.server.dependencies import get_helpdesk, get_current_user
from src.database.tables import Role

core_logger = logging.getLogger("core")
CHARTS_DIR = FilePath(__file__).parent.parent / "contents" / "charts"

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _serialize_ticket(ticket):
    return {
        "id": ticket.id,
        "title": ticket.title,
        "status_name": ticket.status.name,
        "status_fa": ticket.status.fa,
        "created_at": ticket.created_at.isoformat(),
        "creator_username": ticket.creator.username,
        "creator_id": ticket.creator_id,
    }


def _serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "role_fa": user.role.fa,
    }


@router.get("", description="Retrieve dashboard data")
def dashboard(request: Request):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        content = {}

        if current_user.role in (Role.STUDENT, Role.EMPLOYEE):
            tickets_list = helpdesk.ticket_api.list_tickets(creator_id=current_user.id, limit=10)
            content["tickets_list"] = [_serialize_ticket(t) for t in tickets_list]

        elif current_user.role == Role.IT_EXPERT:
            tickets_list = helpdesk.ticket_api.list_tickets(assigned_to=current_user.id, limit=10)
            assigned_tickets, open_tickets, resolved_tickets = helpdesk.statistics_api.it_expert_stats(
                it_expert_id=current_user.id
            )
            content.update({
                "tickets_list": [_serialize_ticket(t) for t in tickets_list],
                "assigned_tickets": assigned_tickets,
                "open_tickets": open_tickets,
                "resolved_tickets": resolved_tickets,
            })

        elif current_user.role == Role.IT_MANAGER:
            tickets_list = helpdesk.ticket_api.list_tickets(limit=10)
            all_tickets_count, active_tickets_count, not_assigned_tickets, last_created = helpdesk.statistics_api.ticket_stats()
            content.update({
                "tickets_list": [_serialize_ticket(t) for t in tickets_list],
                "all_tickets_count": all_tickets_count,
                "active_tickets_count": active_tickets_count,
                "not_assigned_tickets": not_assigned_tickets,
                "last_created": last_created,
            })

        else:
            tickets_list = helpdesk.ticket_api.list_tickets(limit=10)
            users_list = helpdesk.admin_api.list_users(limit=10)
            departments = helpdesk.admin_api.list_ticket_departments()
            all_tickets_count, active_tickets_count, not_assigned_tickets, last_created = helpdesk.statistics_api.ticket_stats()
            all_users_count, active_users_count = helpdesk.statistics_api.users_stats()
            content.update({
                "tickets_list": [_serialize_ticket(t) for t in tickets_list],
                "users_list": [_serialize_user(u) for u in users_list],
                "departments": [{"id": d.id, "name": d.name} for d in departments],
                "roles": [{"name": r.name, "fa": r.fa} for r in Role],
                "all_tickets_count": all_tickets_count,
                "active_tickets_count": active_tickets_count,
                "not_assigned_tickets": not_assigned_tickets,
                "last_created": last_created,
                "all_users_count": all_users_count,
                "active_users_count": active_users_count,
            })

        return JSONResponse(content=content, status_code=status.HTTP_200_OK)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/stats", description="Retrieve dashboard statistics and generate charts")
def stats(request: Request):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role not in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        os.makedirs(f"{CHARTS_DIR}/", exist_ok=True)

        all_tickets_count, active_tickets_count, not_assigned_tickets, last_created = helpdesk.statistics_api.ticket_stats()
        all_users_count, active_users_count = helpdesk.statistics_api.users_stats()

        if current_user.role == Role.SYSTEM_ADMIN:
            helpdesk.statistics_api.users_role_pie_chart()
        helpdesk.statistics_api.tickets_status_bar_chart()
        helpdesk.statistics_api.tickets_category_bar_chart()
        helpdesk.statistics_api.tickets_department_bar_chart()
        helpdesk.statistics_api.it_experts_performance_bar_chart()

        return JSONResponse(
            content={
                "all_tickets_count": all_tickets_count,
                "active_tickets_count": active_tickets_count,
                "not_assigned_tickets": not_assigned_tickets,
                "last_created": last_created,
                "all_users_count": all_users_count,
                "active_users_count": active_users_count,
            },
            status_code=status.HTTP_200_OK,
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

import logging
from fastapi import APIRouter, Request, status, Form, HTTPException
from fastapi.responses import RedirectResponse
from src.server.dependencies import get_helpdesk, get_current_user
from src.database.tables import Response, TicketStatus, Notification, Role

core_logger = logging.getLogger("core")

router = APIRouter(prefix="/tickets/{ticket_id}/responses", tags=["responses"])


@router.get("")
def list_responses(request: Request, ticket_id: int):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if current_user is not None:
            responses_list = helpdesk.response_api.list_responses(ticket_id=ticket_id)
            return {"responses": responses_list}
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("")
def new_response(
        request: Request, 
        text: str = Form(...), 
        response_ticket_id: int = Form(...), 
    ):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if current_user is not None:
            if current_user.role == Role.IT_MANAGER:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

            creator_id = current_user.id
            
            redirect = RedirectResponse(url=f"/tickets/{response_ticket_id}", status_code=status.HTTP_303_SEE_OTHER)

            ticket = helpdesk.ticket_api.find_ticket(ticket_id=response_ticket_id)
            if ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
                redirect.set_cookie(key="ticket_closed_flash_message", value="successful")
            else:
                response = Response(text=text, ticket_id=response_ticket_id, creator_id=creator_id)
                helpdesk.response_api.new_response(response=response)

                if current_user.role in (Role.STUDENT, Role.EMPLOYEE):
                    ticket.status = TicketStatus.IN_PROGRESS
                    helpdesk.ticket_api.update_ticket(new_ticket=ticket, old_ticket_id=ticket.id)

                    notification = Notification(receiver_id=ticket.assigned_to, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.")
                    helpdesk.notification_api.new_notification(notification=notification)

                elif current_user.role == Role.IT_EXPERT:
                    ticket.status = TicketStatus.WAITING_FOR_USER
                    helpdesk.ticket_api.update_ticket(new_ticket=ticket, old_ticket_id=ticket.id)

                    notification = Notification(receiver_id=ticket.creator_id, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.")
                    helpdesk.notification_api.new_notification(notification=notification)

            return redirect
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

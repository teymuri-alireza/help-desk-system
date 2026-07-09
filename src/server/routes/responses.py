import logging
from fastapi import APIRouter, Request, status, Form, HTTPException, Path
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
            serialized_responses = [{
                    "id": response.id,
                    "ticket_id": response.ticket_id,
                    "creator_id": response.creator_id,
                    "text": response.text,
                    "created_at": response.created_at.isoformat() if response.created_at is not None else None,
                    "updated_at": response.updated_at.isoformat() if response.updated_at is not None else None,
                    "creator": {
                        "id": response.creator.id if response.creator is not None else None,
                        "name": response.creator.name if response.creator is not None else None,
                        "username": response.creator.username if response.creator is not None else None,
                        "role": response.creator.role.value if response.creator is not None and hasattr(response.creator.role, "value") else str(response.creator.role) if response.creator is not None else None,
                    }
                } for response in responses_list
            ]
            return {"responses": serialized_responses}
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("")
def new_response(
        request: Request, 
        ticket_id: int = Path(...), 
        text: str = Form(...), 
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
            creator_id = current_user.id
            
            redirect = RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)

            ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
            if ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
                redirect.set_cookie(key="ticket_closed_flash_message", value="successful")
            else:
                response = Response(text=text, ticket_id=ticket_id, creator_id=creator_id)
                helpdesk.response_api.new_response(response=response)

                if current_user.role in (Role.STUDENT, Role.EMPLOYEE):
                    ticket.status = TicketStatus.IN_PROGRESS
                    helpdesk.ticket_api.update_ticket(new_ticket=ticket, old_ticket_id=ticket.id)

                    notification = Notification(receiver_id=ticket.assigned_to, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.", url=f"/tickets/{ticket_id}")
                    helpdesk.notification_api.new_notification(notification=notification)

                elif current_user.role == Role.IT_EXPERT:
                    ticket.status = TicketStatus.WAITING_FOR_USER
                    helpdesk.ticket_api.update_ticket(new_ticket=ticket, old_ticket_id=ticket.id)

                    notification = Notification(receiver_id=ticket.creator_id, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.", url=f"/tickets/{ticket_id}")
                    helpdesk.notification_api.new_notification(notification=notification)

                elif current_user.role in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
                    notification = Notification(receiver_id=ticket.assigned_to, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.", url=f"/tickets/{ticket_id}")
                    helpdesk.notification_api.new_notification(notification=notification)

                    notification = Notification(receiver_id=ticket.creator_id, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.", url=f"/tickets/{ticket_id}")
                    helpdesk.notification_api.new_notification(notification=notification)

            return redirect
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{response_id}")
def edit_response(
        request: Request,
        ticket_id: int = Path(...),
        response_id: int = Path(...),
        text: str = Form(...),
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
            found_response = helpdesk.response_api.find_response(response_id=response_id)
            if current_user.id != found_response.creator_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

            found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
            if found_ticket.status in (TicketStatus.CLOSED, TicketStatus.RESOLVED):
                request.session["edit_response_unavailable"] = "error"
                return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)

            new_response = Response(text=text)
            helpdesk.response_api.update_response(new_response=new_response, old_response_id=response_id)

            notification = Notification(receiver_id=found_response.creator_id, title="ویرایش پاسخ", text=f"پاسخ به شماره {response_id} با موفقیت ویرایش شد", url=f"/tickets/{ticket_id}")
            helpdesk.notification_api.new_notification(notification=notification)

            return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

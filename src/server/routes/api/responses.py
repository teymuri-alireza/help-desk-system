import logging
from fastapi import APIRouter, Request, status, Form, HTTPException, Path
from fastapi.responses import JSONResponse
from src.server.dependencies import get_helpdesk, get_current_user
from src.database.tables import Response, TicketStatus, Notification, Role

core_logger = logging.getLogger("core")

router = APIRouter(prefix="/api/tickets/{ticket_id}/responses", tags=["responses"])


@router.get("", description="Retrieve list of responses.")
def list_responses(request: Request, ticket_id: int = Path(...)):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        responses_list = helpdesk.response_api.list_responses(ticket_id=ticket_id)

        return JSONResponse(
            content={
                "responses":  [{
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
            } for response in responses_list]
        })

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("", description="Create a new resposne", status_code=status.HTTP_201_CREATED)
def new_response(
        request: Request, 
        ticket_id: int = Path(...), 
        text: str = Form(...), 
        parent_response_id: int | None = Form(None),
    ):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        creator_id = current_user.id

        ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
        if ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Can not perform this operation on a resolved or closed ticket.")

        response = Response(text=text, ticket_id=ticket_id, creator_id=creator_id, parent_response_id=parent_response_id)
        helpdesk.response_api.new_response(response=response)

        if current_user.role in (Role.STUDENT, Role.EMPLOYEE):
            ticket.status = TicketStatus.IN_PROGRESS
            helpdesk.ticket_api.update_ticket(new_ticket=ticket, old_ticket_id=ticket.id)

            if ticket.assigned_to is not None:
                notification = Notification(receiver_id=ticket.assigned_to, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.", url=f"/tickets/{ticket_id}")
                helpdesk.notification_api.new_notification(notification=notification)

        elif current_user.role == Role.IT_EXPERT:
            ticket.status = TicketStatus.WAITING_FOR_USER
            helpdesk.ticket_api.update_ticket(new_ticket=ticket, old_ticket_id=ticket.id)

            notification = Notification(receiver_id=ticket.creator_id, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.", url=f"/tickets/{ticket_id}")
            helpdesk.notification_api.new_notification(notification=notification)

        elif current_user.role in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
            if ticket.assigned_to is not None:
                notification = Notification(receiver_id=ticket.assigned_to, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.", url=f"/tickets/{ticket_id}")
                helpdesk.notification_api.new_notification(notification=notification)

            notification = Notification(receiver_id=ticket.creator_id, title="پاسخ جدید", text=f"برای تیکت شماره {ticket.id} پاسخ جدید ثبت شده است.", url=f"/tickets/{ticket_id}")
            helpdesk.notification_api.new_notification(notification=notification)

        return JSONResponse(
            content={
                "success": True,
                "message": "Response created successfully.",
            },
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{response_id}", description="Update a response")
def edit_response(
        request: Request,
        ticket_id: int = Path(...,),
        response_id: int = Path(...),
        text: str = Form(...),
    ):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        found_response = helpdesk.response_api.find_response(response_id=response_id)
        if found_response is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        if current_user.id != found_response.creator_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
        if found_ticket.status in (TicketStatus.CLOSED, TicketStatus.RESOLVED):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Can not perform this operation on a resolved or closed ticket.")

        new_response = Response(text=text)
        helpdesk.response_api.update_response(new_response=new_response, old_response_id=response_id)

        notification = Notification(receiver_id=found_response.creator_id, title="ویرایش پاسخ", text=f"پاسخ به شماره {response_id} با موفقیت ویرایش شد", url=f"/tickets/{ticket_id}")
        helpdesk.notification_api.new_notification(notification=notification)

        return JSONResponse(
            content={
                "success": True,
                "message": "Response updated successfully.",
            },
            status_code=status.HTTP_200_OK
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

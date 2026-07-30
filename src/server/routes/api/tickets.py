import os
import uuid
import logging
from pathlib import Path as FilePath
from fastapi import APIRouter, Request, Form, status, UploadFile, Path, HTTPException
from fastapi.responses import JSONResponse
from src.server.dependencies import get_helpdesk, get_current_user
from src.database.tables import Ticket, Attachment, Notification, Role, TicketStatus, TicketPriority

core_logger = logging.getLogger("core")

CONTENTS_DIR = FilePath(__file__).parent.parent / "contents"
UPLOAD_DIR = CONTENTS_DIR / "upload"

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("", description="Retrieve list of tickets")
def list_tickets(request: Request):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role == Role.STUDENT or current_user.role == Role.EMPLOYEE:
            tickets_list = helpdesk.ticket_api.list_tickets(creator_id=current_user.id)
        elif current_user.role == Role.IT_EXPERT:
            tickets_list = helpdesk.ticket_api.list_tickets(assigned_to=current_user.id)
        else: # For admins
            tickets_list = helpdesk.ticket_api.list_tickets()

        return JSONResponse(
            content={
                "tickets_list": [{
                    "id": t.id,
                    "title": t.title,
                    "status_name": t.status.name,
                    "status_fa": t.status.fa,
                    "description": t.description,
                    "created_at": t.created_at.isoformat(),
                    "creator_username": t.creator.username,
                    "creator_id": t.creator_id,
                } for t in tickets_list]
            },
            status_code=status.HTTP_200_OK
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{ticket_id}", description="Retrieve one ticket's information")
def show_ticket(request: Request, ticket_id: int = Path(...)):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)

        if found_ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

        # Check if user has access
        if current_user.role in (Role.STUDENT, Role.EMPLOYEE) and found_ticket.creator_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        # Raise 403 error for IT Expert without access
        if current_user.role == Role.IT_EXPERT and found_ticket.assigned_to != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        if found_ticket.department_id is None:
            it_experts = []
        else:
            it_experts = helpdesk.admin_api.list_it_experts(department_id=found_ticket.department_id)

        found_attachment = helpdesk.attachment_api.find_attachment(ticket_id=ticket_id)
        categories = helpdesk.admin_api.list_ticket_categories()
        departments = helpdesk.admin_api.list_ticket_departments()

        return JSONResponse(
            content={
                "ticket": {
                    "id": found_ticket.id,
                    "title": found_ticket.title,
                    "description": found_ticket.description,
                    "status_name": found_ticket.status.name,
                    "status_fa": found_ticket.status.fa,
                    "status_en": found_ticket.status.value,
                    "priority_name": found_ticket.priority.name,
                    "priority_fa": found_ticket.priority.fa,
                    "priority_en": found_ticket.priority.value,
                    "created_at": found_ticket.created_at.isoformat(),
                    "category_name": found_ticket.category.name if found_ticket.category is not None else None,
                    "department_name": found_ticket.department.name if found_ticket.department is not None else None,
                    "creator_id": found_ticket.creator_id,
                    "assigned_to": found_ticket.assigned_to,
                    "satisfaction_rating": found_ticket.satisfaction_rating,
                },
                "attachment": found_attachment.file_name if found_attachment is not None else None,
                "TicketStatus": [
                    {
                        "name": s.name,
                        "fa": s.fa,
                        "en": s.value
                    } for s in TicketStatus
                ],
                "TicketPriority": [
                    {
                        "name": p.name,
                        "fa": p.fa,
                        "en": p.value
                    } for p in TicketPriority
                ],
                "it_experts": [
                    {
                        "id": it.id,
                        "name": it.name,
                    } for it in it_experts
                ],
                "categories": [
                    {
                        "id": c.id,
                        "name": c.name,
                    } for c in categories
                ],
                "departments": [
                    {
                        "id": d.id,
                        "name": d.name,
                    } for d in departments
                ],
            },
            status_code=status.HTTP_200_OK
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("", description="Create a new ticket")
def new_ticket(
    request: Request,
    attachment: UploadFile,
    title: str = Form(...),
    description: str = Form(...),
    ):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        os.makedirs(f"{CONTENTS_DIR}/", exist_ok=True)
        os.makedirs(f"{UPLOAD_DIR}/", exist_ok=True)

        ticket = Ticket(title=title, description=description, creator_id=current_user.id)
        helpdesk.ticket_api.new_ticket(ticket=ticket)

        if attachment.size != 0:
            ext = FilePath(attachment.filename).suffix.lower()
            file_name = f"{uuid.uuid4()}{ext}"

            upload = Attachment(
                file_name=file_name, 
                file_type=attachment.content_type, 
                ticket_id=ticket.id, 
                creator_id=ticket.creator_id, 
                path=f"{UPLOAD_DIR}"
                )
            helpdesk.attachment_api.new_attachment(attachment=upload)
            content = attachment.file.read()
            with open(f"{upload.path}/{upload.file_name}", "wb") as file:
                file.write(content)

        notification = Notification(receiver_id=current_user.id, title="تیکت جدید ثبت شد", text=f"عنوان تیکت: {title}", url=f"/tickets/{ticket.id}")
        helpdesk.notification_api.new_notification(notification=notification)

        return JSONResponse(
            content={
                "success": True,
                "message": "Ticket created successfully."
            },
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{ticket_id}/assign/preview", description="Preview the free IT expert to assign a ticket to")
def preview_assign_ticket(request: Request, ticket_id: int = Path(...)):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role not in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
        preview_it_expert = helpdesk.ticket_api.preview_auto_assign_ticket(department_id=found_ticket.department_id)

        return JSONResponse(
            content={
                "it_username": preview_it_expert.username,
                "it_name": preview_it_expert.name
            },
            status_code=status.HTTP_200_OK
        )

    except AttributeError as e:

        if str(e) == "Can not show preview for auto assign ticket. Department field is None.":
            error_msg = "اختصاص اتوماتیک تیکت به کارشناس ممکن نیست. علت: هیچ دپارتمانی برای تیکت ثبت نشده است"

        elif str(e) == "Can not show preview for auto assign ticket. No IT expert was found for this department.":
            error_msg = "اختصاص اتوماتیک تیکت به کارشناس ممکن نیست. علت: هیچ کارشناسی در دپارتمان ثبت شده‌ی تیکت فعالیت نمیکند"

        return JSONResponse(
            content={
                "error": error_msg
            },
            status_code=status.HTTP_417_EXPECTATION_FAILED
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{ticket_id}/assign", description="Assign a ticket to an IT expert")
def assign_ticket(request: Request, ticket_id: int = Path(...)):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role not in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
        helpdesk.ticket_api.auto_assign_ticket(ticket_id=ticket_id, department_id=found_ticket.department_id)

        found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
        notification = Notification(receiver_id=found_ticket.assigned_to, title="تیکت جدید ارجاع شد", text=f"تیکت به شماره {ticket_id} به شما ارجاع داده شده است.", url=f"/tickets/{ticket_id}")
        helpdesk.notification_api.new_notification(notification=notification)


        return JSONResponse(
            content={
                "successs": True,
                "message": "Ticket assigned successfully."
            },
            status_code=status.HTTP_200_OK
        )

    except AttributeError as e:

        if str(e) == "Can not show preview for auto assign ticket. Department field is None.":
            error_msg = "اختصاص اتوماتیک تیکت به کارشناس ممکن نیست. علت: هیچ دپارتمانی برای تیکت ثبت نشده است"

        elif str(e) == "Can not show preview for auto assign ticket. No IT expert was found for this department.":
            error_msg = "اختصاص اتوماتیک تیکت به کارشناس ممکن نیست. علت: هیچ کارشناسی در دپارتمان ثبت شده‌ی تیکت فعالیت نمیکند"

        return JSONResponse(
            content={
                "error": error_msg
            },
            status_code=status.HTTP_417_EXPECTATION_FAILED
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{ticket_id}/remove_assignee", description="Remove an assigned IT expert from a ticket")
def remove_assignee(
        request: Request,
        ticket_id: int = Path(...),
        checkbox: bool = Form(...)
    ):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role not in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        if checkbox:
            helpdesk.ticket_api.remove_assignee(ticket_id=ticket_id)            

            return JSONResponse(
                content={
                    "successs": True,
                    "message": "Ticket's assignee removed successfully."
                },
                status_code=status.HTTP_200_OK
            )

        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{ticket_id}/rate", description="Rate a ticket based on IT expert's performance")
def rate_ticket(
        request: Request,
        ticket_id: int = Path(...),
        rating: int = Form(..., ge=1, le=5),
    ):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
        if current_user.id != found_ticket.creator_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        helpdesk.ticket_api.rate_ticket(ticket_id=ticket_id, satisfaction_rating=rating)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "ticket's rate submitted successfully."
            },
            status_code=status.HTTP_200_OK
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{ticket_id}", description="Update a ticket's information")
def patch_ticket(
        request: Request, 
        ticket_id: int = Path(...),
        title: str | None = Form(None),
        description: str | None = Form(None),
        ticket_status: str | None = Form(None),
        priority: str | None = Form(None),
        assigned_to: str | None = Form(None),
        category_id: int | None = Form(None),
        department_id: int | None = Form(None),
    ):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        old_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)

        if (
            current_user.role in (Role.SYSTEM_ADMIN, Role.IT_MANAGER, Role.IT_EXPERT)
            or old_ticket.creator_id == current_user.id
        ):
            ticket_to_update = Ticket(title=title, description=description, status=ticket_status, priority=priority, assigned_to=assigned_to, category_id=category_id, department_id=department_id)
            helpdesk.ticket_api.update_ticket(new_ticket=ticket_to_update, old_ticket_id=ticket_id)

            if current_user.role in (Role.SYSTEM_ADMIN, Role.IT_MANAGER) and ticket_to_update.assigned_to is not None and old_ticket.assigned_to is None:
                notification = Notification(receiver_id=assigned_to, title="تیکت جدید ارجاع شد", text=f"تیکت به شماره {ticket_id} به شما ارجاع داده شده است.", url=f"/tickets/{ticket_id}")
                helpdesk.notification_api.new_notification(notification=notification)

            if old_ticket.status not in (TicketStatus.CLOSED, TicketStatus.RESOLVED) and ticket_to_update.status in (TicketStatus.CLOSED.name, TicketStatus.RESOLVED.name):
                if current_user.id == old_ticket.creator_id:
                    if assigned_to is not None:
                        notification = Notification(receiver_id=old_ticket.assignee.id, title="تیکت بسته شد", text=f"تیکت به شماره {ticket_id} توسط کاربر بسته شد.", url=f"/tickets/{ticket_id}")
                        helpdesk.notification_api.new_notification(notification=notification)
                else:
                    notification = Notification(receiver_id=old_ticket.creator_id, title="تیکت بسته شد", text=f"تیکت به شماره {ticket_id} بسته شد. برای ثبت امتیاز به صفحه تیکت مراجعه فرمایید", url=f"/tickets/{ticket_id}")
                    helpdesk.notification_api.new_notification(notification=notification)

            return JSONResponse(
                content={
                    "success": True,
                    "message": "ticket updated successfully."
                },
                status_code=status.HTTP_200_OK
            )

        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{ticket_id}/reopen", description="Re-open a closed or resolved ticket")
def reopen_ticket(
        request: Request, 
        ticket_id: int = Path(...),
        ticket_status: str | None = Form(None),
    ):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)

        if current_user.role not in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        if found_ticket not in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Can not re-open an open ticket")

        if ticket_status is not None:
            helpdesk.ticket_api.reopen_ticket(ticket_id=ticket_id)

            notification = Notification(receiver_id=found_ticket.creator_id, title="تیکت دوباره باز شد", text=f"تیکت به شماره {ticket_id} دوباره به وضعیت درحال بررسی برگشت.", url=f"/tickets/{ticket_id}")
            helpdesk.notification_api.new_notification(notification=notification)

            if found_ticket.assigned_to:
                notification = Notification(receiver_id=found_ticket.assigned_to, title="تیکت دوباره باز شد", text=f"تیکت به شماره {ticket_id} دوباره به وضعیت درحال بررسی برگشت.", url=f"/tickets/{ticket_id}")
                helpdesk.notification_api.new_notification(notification=notification)

            return JSONResponse(
                content={
                    "success": True,
                    "message": "ticket re-opened successfully."
                },
                status_code=status.HTTP_200_OK
            )

        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

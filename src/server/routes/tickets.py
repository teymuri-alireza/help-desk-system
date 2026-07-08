import os
import uuid
import logging
from pathlib import Path as FilePath
from fastapi import APIRouter, Request, Form, status, UploadFile, Path, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user
from src.database.tables import Ticket, Attachment, Notification, Role, TicketStatus, TicketPriority

core_logger = logging.getLogger("core")
TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("")
def list_tickets(request: Request):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if current_user is not None:
            if current_user.role == Role.STUDENT or current_user.role == Role.EMPLOYEE:
                tickets_list = helpdesk.ticket_api.list_tickets(creator_id=current_user.id)
            elif current_user.role == Role.IT_EXPERT:
                tickets_list = helpdesk.ticket_api.list_tickets(assigned_to=current_user.id)
            else:
                # For admins
                tickets_list = helpdesk.ticket_api.list_tickets()

            context = {
                "request": request,
                "tickets_list": tickets_list,
                "user_id": current_user.id,
                "user_username": current_user.username,
                "user_role": current_user.role.value,
            }
            response = templates.TemplateResponse(
                request=request,
                name="tickets.html",
                context=context
            )
            return response

        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{ticket_id}")
def show_ticket(request: Request, ticket_id: int = Path(...)):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if current_user is not None:
            try:
                found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
                # Check if user has access
                if current_user.role == Role.STUDENT or current_user.role == Role.EMPLOYEE:
                    if found_ticket.creator_id != current_user.id:
                        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
                # Raise 403 error for IT Expert without access
                if current_user.role == Role.IT_EXPERT and found_ticket.assigned_to != current_user.id:
                        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

                ticket_update_flash_message = request.cookies.get("ticket_update_flash_message")
                ticket_closed_flash_message = request.cookies.get("ticket_closed_flash_message")
                assign_ticket_flash_message = request.session.pop("assign_ticket_flash_message", None)
                it_experts = helpdesk.admin_api.list_it_experts()
                found_attachment = helpdesk.attachment_api.find_attachment(ticket_id=ticket_id)
                categories = helpdesk.admin_api.list_ticket_categories()
                departments = helpdesk.admin_api.list_ticket_departments()

                response = templates.TemplateResponse(
                    request=request, 
                    name="show_ticket.html", 
                    context={
                        "request": request,
                        "ticket": found_ticket,
                        "attachment": found_attachment,
                        "user_id": current_user.id,
                        "user_role": current_user.role.value,
                        "user_username": current_user.username,
                        "TicketStatus":TicketStatus,
                        "TicketPriority":TicketPriority,
                        "it_experts": it_experts,
                        "categories": categories,
                        "departments": departments,
                        "ticket_update_flash_message": ticket_update_flash_message,
                        "ticket_closed_flash_message": ticket_closed_flash_message,
                        "assign_ticket_flash_message": assign_ticket_flash_message,
                    }
                )
                response.delete_cookie("ticket_update_flash_message")
                response.delete_cookie("ticket_closed_flash_message")
                return response
            except AttributeError as e:
                if "has no attribute 'creator_id'" in str(e):
                    # found_ticket.creator_id doesn't exist, which means ticket is not found.
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("")
def new_ticket(
    request: Request,
    attachment: UploadFile,
    title: str = Form(...),
    description: str = Form(...),
    ):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if current_user is None:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
        if current_user.role in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        os.makedirs(f"{STATIC_DIR}/upload/", exist_ok=True)

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
                path=f"{STATIC_DIR}/upload"
                )
            helpdesk.attachment_api.new_attachment(attachment=upload)
            content = attachment.file.read()
            with open(f"{upload.path}/{upload.file_name}", "wb") as file:
                file.write(content)

        notification = Notification(receiver_id=current_user.id, title="تیکت جدید ثبت شد", text=f"عنوان تیکت: {title}", url=f"/tickets/{ticket.id}")
        helpdesk.notification_api.new_notification(notification=notification)

        redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        redirect.set_cookie(key="new_ticket_flash_message", value="successful")
        return redirect
    except Exception:
        raise
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{ticket_id}/assign")
def assign_ticket(request: Request, ticket_id: int = Path(...)):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if current_user is not None:
            if current_user.role in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
                found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
                helpdesk.ticket_api.auto_assign_ticket(ticket_id=ticket_id, department_id=found_ticket.department_id)
                request.session["assign_ticket_flash_message"] = "اختصاص اتوماتیک کارشناس به تیکت با موفقیت انجام شد"

                found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
                notification = Notification(receiver_id=found_ticket.assigned_to, title="تیکت جدید ارجاع شد", text=f"تیکت به شماره {ticket_id} به شما ارجاع داده شده است.", url=f"/tickets/{ticket_id}")
                helpdesk.notification_api.new_notification(notification=notification)

                return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except AttributeError as e:
        e = str(e)
        redirect = RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)

        if e == "Can not auto assign ticket. Department field is None.":
            request.session["assign_ticket_flash_message"] = "اختصاص اتوماتیک تیکت به کارشناس ممکن نیست. علت: هیچ دپارتمانی برای تیکت ثبت نشده است"

        elif e == "Can not auto assign ticket. No IT expert was found for this department.":
            request.session["assign_ticket_flash_message"] = "اختصاص اتوماتیک تیکت به کارشناس ممکن نیست. علت: هیچ کارشناسی در دپارتمان ثبت شده‌ی تیکت فعالیت نمیکند"

        return redirect
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{ticket_id}")
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
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        current_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        # Check if user is admin first
        if current_user is not None:
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
                        notification = Notification(receiver_id=old_ticket.creator_id, title="تیکت بسته شد", text=f"تیکت به شماره {ticket_id} بسته شد.", url=f"/tickets/{ticket_id}")
                        helpdesk.notification_api.new_notification(notification=notification)

                redirect = RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)
                redirect.set_cookie(key="ticket_update_flash_message", value="successful")
                return redirect
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

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
TEMPLATES_DIR = get_static_path()[0]
templates = Jinja2Templates(directory=TEMPLATES_DIR)

CONTENTS_DIR = FilePath(__file__).parent.parent / "contents"
UPLOAD_DIR = CONTENTS_DIR / "upload"

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", description="Serves the frontend page for tickets")
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

@router.get("/{ticket_id}", description="Serves the frontend page for one ticket")
def show_ticket(request: Request, ticket_id: int = Path(..., description="Ticket ID to search for")):
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
                preview_assign_ticket_flash_message = request.session.pop("preview_assign_ticket_flash_message", None)
                rate_ticket_flash_message = request.session.pop("rate_ticket_flash_message", None)
                edit_response_unavailable = request.session.pop("edit_response_unavailable", None)
                reopen_ticket_unprocessable = request.session.pop("reopen_ticket_unprocessable", None)
                ticket_remove_assignee = request.session.pop("ticket_remove_assignee", None)

                if found_ticket.department_id is None:
                    it_experts = []
                else:
                    it_experts = helpdesk.admin_api.list_it_experts(department_id=found_ticket.department_id)

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
                        "preview_assign_ticket_flash_message": preview_assign_ticket_flash_message,
                        "rate_ticket_flash_message": rate_ticket_flash_message,
                        "edit_response_unavailable": edit_response_unavailable,
                        "reopen_ticket_unprocessable": reopen_ticket_unprocessable,
                        "ticket_remove_assignee": ticket_remove_assignee,
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

@router.post("", description="Create a new ticket")
def new_ticket(
    request: Request,
    attachment: UploadFile,
    title: str = Form(..., description="Title of the new ticket"),
    description: str = Form(..., description="Text describing the ticket"),
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

        redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        redirect.set_cookie(key="new_ticket_flash_message", value="successful")
        return redirect
    except Exception:
        raise
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{ticket_id}/assign/preview", description="Preview the free IT expert to assign a ticket to")
def preview_assign_ticket(request: Request, ticket_id: int = Path(..., description="The ticket ID to search, and to use for its department_id field")):
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
                preview_it_expert = helpdesk.ticket_api.preview_auto_assign_ticket(department_id=found_ticket.department_id)

                request.session["preview_assign_ticket_flash_message"] = f"نام کاربری: {preview_it_expert.username} - نام: {preview_it_expert.name}"
                return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except AttributeError as e:
        e = str(e)
        redirect = RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)

        if e == "Can not show preview for auto assign ticket. Department field is None.":
            request.session["assign_ticket_flash_message"] = "اختصاص اتوماتیک تیکت به کارشناس ممکن نیست. علت: هیچ دپارتمانی برای تیکت ثبت نشده است"

        elif e == "Can not show preview for auto assign ticket. No IT expert was found for this department.":
            request.session["assign_ticket_flash_message"] = "اختصاص اتوماتیک تیکت به کارشناس ممکن نیست. علت: هیچ کارشناسی در دپارتمان ثبت شده‌ی تیکت فعالیت نمیکند"

        return redirect
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{ticket_id}/assign", description="Assign a ticket to an IT expert")
def assign_ticket(request: Request, ticket_id: int = Path(..., description="Ticket ID to update")):
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


@router.post("/{ticket_id}/remove_assignee", description="Remove an assigned IT expert from a ticket")
def remove_assignee(
        request: Request,
        ticket_id: int = Path(..., description="Ticket ID to update"),
        checkbox: bool = Form(..., description="boolean indicating if assignee removal should be proceeded.")
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
            if current_user.role not in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

            if checkbox:
                helpdesk.ticket_api.remove_assignee(ticket_id=ticket_id)            
                request.session["ticket_remove_assignee"] = "کارشناس تیکت با موفقیت حذف شد"

            return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{ticket_id}/rate", description="Rate a ticket based on IT expert's performance")
def rate_ticket(
        request: Request,
        ticket_id: int = Path(..., description="Ticket ID to update"),
        rating: int = Form(..., description="Satisfaction rating value", ge=1, le=5),
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
            found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
            if current_user.id != found_ticket.creator_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

            helpdesk.ticket_api.rate_ticket(ticket_id=ticket_id, satisfaction_rating=rating)
            request.session["rate_ticket_flash_message"] = "امتیاز با موفقیت ثبت شد"
            return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{ticket_id}", description="Update a ticket's information")
def patch_ticket(
        request: Request, 
        ticket_id: int = Path(..., description="Ticket ID to update"),
        title: str | None = Form(None, description="Title of the ticket"),
        description: str | None = Form(None, description="Text describing the ticket"),
        ticket_status: str | None = Form(None, description="Status of the ticket"),
        priority: str | None = Form(None, description="Priority of the ticket"),
        assigned_to: str | None = Form(None, description="The IT expert ID to assign the ticket to"),
        category_id: int | None = Form(None, description="The category ID describing the ticket's category"),
        department_id: int | None = Form(None, description="The department ID describing the ticket's department"),
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
                        notification = Notification(receiver_id=old_ticket.creator_id, title="تیکت بسته شد", text=f"تیکت به شماره {ticket_id} بسته شد. برای ثبت امتیاز به صفحه تیکت مراجعه فرمایید", url=f"/tickets/{ticket_id}")
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


@router.patch("/{ticket_id}/reopen", description="Re-open a closed or resolved ticket")
def reopen_ticket(
        request: Request, 
        ticket_id: int = Path(..., description="Ticket ID to open"),
        ticket_status: str | None = Form(None, description="The new status of ticket after re-opening"),
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
            found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)

            if current_user.role in (Role.SYSTEM_ADMIN, Role.IT_MANAGER):
                redirect = RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)

                if found_ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
                    if ticket_status is not None:
                        helpdesk.ticket_api.reopen_ticket(ticket_id=ticket_id)
                        redirect.set_cookie(key="ticket_update_flash_message", value="successful")
                else:
                    request.session["reopen_ticket_unprocessable"] = "unprocessable"

                notification = Notification(receiver_id=found_ticket.creator_id, title="تیکت دوباره باز شد", text=f"تیکت به شماره {ticket_id} دوباره به وضعیت درحال بررسی برگشت.", url=f"/tickets/{ticket_id}")
                helpdesk.notification_api.new_notification(notification=notification)

                if found_ticket.assigned_to:
                    notification = Notification(receiver_id=found_ticket.assigned_to, title="تیکت دوباره باز شد", text=f"تیکت به شماره {ticket_id} دوباره به وضعیت درحال بررسی برگشت.", url=f"/tickets/{ticket_id}")
                    helpdesk.notification_api.new_notification(notification=notification)

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

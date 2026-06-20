import os
from fastapi import APIRouter, Request, Form, status, UploadFile, Path, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user
from src.database.tables import Ticket, Attachment, Notification, Role, TicketStatus, TicketPriority

TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("")
def list_tickets(request: Request):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
    if found_user is not None:
        if found_user.role == Role.STUDENT or found_user.role == Role.EMPLOYEE:
            tickets_list = helpdesk.ticket_api.list_tickets(creator_id=found_user.id)
        else:
            # For admins
            tickets_list = helpdesk.ticket_api.list_tickets()

        context = {
            "request": request,
            "tickets_list": tickets_list,
            "user_id": found_user.id,
            "role": found_user.role.value,
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

@router.get("/{ticket_id}")
def show_ticket(request: Request, ticket_id: int = Path(...)):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
    if found_user is not None:
        try:
            found_ticket = helpdesk.ticket_api.find_ticket(ticket_id=ticket_id)
            # Check if user has access
            if found_user.role == Role.STUDENT or found_user.role == Role.EMPLOYEE:
                if found_ticket.creator_id != found_user.id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            user_role = found_user.role.value
            it_experts = helpdesk.admin_api.list_it_experts()
            return templates.TemplateResponse(
                request=request, 
                name="show_ticket.html", 
                context={
                    "request": request,
                    "ticket": found_ticket,
                    "user_id": found_user.id,
                    "user_role": user_role,
                    "TicketStatus":TicketStatus,
                    "TicketPriority":TicketPriority,
                    "it_experts": it_experts,
                }
            )
        except AttributeError as e:
            if "has no attribute 'creator_id'" in str(e):
                # found_ticket.creator_id doesn't exist, which means ticket is not found.
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    else:
        # Error handler for when db is removed but session exists
        return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)

@router.post("")
def new_ticket(
    request: Request,
    attachment: UploadFile,
    title: str = Form(...),
    description: str = Form(...),
    creator_id: int = Form(...),
    ):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
    if found_user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)

    os.makedirs(f"{STATIC_DIR}/upload/", exist_ok=True)

    ticket = Ticket(title=title, description=description, creator_id=creator_id)
    if attachment.size != 0:
        upload = Attachment(
            file_name=attachment.filename, 
            file_type=attachment.content_type, 
            ticket_id=ticket.id, 
            creator_id=ticket.creator_id, 
            path=f"{STATIC_DIR}/upload"
            )
        helpdesk.attachment_api.new_attachment(attachment=upload)
        content = attachment.file.read()
        with open(f"{upload.path}/{upload.file_name}", "wb") as file:
            file.write(content)

    helpdesk.ticket_api.new_ticket(ticket=ticket)
    notification = Notification(receiver_id=creator_id, title="تیکت جدید ثبت شد", text=f"عنوان تیکت: {title}")
    helpdesk.notification_api.new_notification(notification=notification)

    redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    redirect.set_cookie(key="new_ticket_flash_message", value="successful")
    return redirect

@router.post("/{ticket_id}/assign")
def assign_ticket():
    return {"response": "Assign Ticket Page"}

@router.patch("/{ticket_id}")
def patch_ticket(        request: Request, 
        ticket_id: int = Path(...),
        title: str = Form(...),
        description: str = Form(...),
        ticket_status: str = Form(...),
        priority: str = Form(...),
        assigned_to: str = Form(...),
    ):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
    # Check if user is admin first
    if found_user is not None and found_user.role == Role.SYSTEM_ADMIN:
        ticket_to_update = Ticket(title=title, description=description, status=ticket_status, priority=priority, assigned_to=assigned_to)
        helpdesk.ticket_api.update_ticket(new_ticket=ticket_to_update, old_ticket_id=ticket_id)
        return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

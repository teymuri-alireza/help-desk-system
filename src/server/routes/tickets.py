import os
from fastapi import APIRouter, Request, Form, status, UploadFile, Path
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.server.dependencies import get_static_path, get_helpdesk, get_current_user
from src.database.tables import Ticket, Attachment, Notification, Role

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
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)
    if found_user is not None:
        if found_user.role == Role.STUDENT:
            tickets_list = helpdesk.ticket_api(action="list", user_id=found_user.id)
        else:
            # For admins
            tickets_list = helpdesk.ticket_api(action="list")

        context = {
            "request": request,
            "tickets_list": tickets_list,
            "role": found_user.role.value,
        }
        response = templates.TemplateResponse(
            request=request,
            name="tickets.html",
            context=context
        )
        return response

    else:
        return {"response": "not found"}

@router.get("/{ticket_id}")
def show_ticket(request: Request, ticket_id: int = Path(...)):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)
    if found_user is not None:
        found_ticket = helpdesk.ticket_api(action="find", ticket_id=ticket_id)
        user_role = found_user.role
        return templates.TemplateResponse(
            request=request, 
            name="show_ticket.html", 
            context={"request": request, "ticket": found_ticket, "user_role": user_role}
        )
    else:
        return {"response": "not found"}

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
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)
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
        helpdesk.attachment_api(upload)
        content = attachment.file.read()
        with open(f"{upload.path}/{upload.file_name}", "wb") as file:
            file.write(content)

    is_created = helpdesk.ticket_api(action="new", ticket=ticket)
    if is_created:
        notification = Notification(receiver_id=creator_id, title="تیکت جدید ثبت شد", text=f"عنوان تیکت: {title}")
        helpdesk.notification_api(action="new", notification=notification)

        redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        redirect.set_cookie(key="flash_message", value="successful")
        return redirect
    else:
        # Placeholder for error, this functionality will be implemented later
        return {"response": "error occured in new_ticket route"}

@router.post("/{ticket_id}/assign")
def assign_ticket():
    return {"response": "Assign Ticket Page"}

@router.patch("/{ticket_id}")
def patch_ticket():
    return {"response": "Patch Ticket Page"}

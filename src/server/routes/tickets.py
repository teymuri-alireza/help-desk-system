from fastapi import APIRouter, Request, Form, status, UploadFile
from fastapi.responses import RedirectResponse
from src.server.dependencies import get_static_path, get_helpdesk
from src.database.tables import Ticket, Attachment

STATIC_DIR = get_static_path()[1]

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("")
def list_tickets():
    return {"response": "List Tickets Page"}

@router.get("/{ticket_id}")
def show_ticket():
    return {"response": "Show Ticket Page"}

@router.post("")
def new_ticket(
    request: Request,
    attachment: UploadFile,
    title: str = Form(...),
    description: str = Form(...),
    creator_id: int = Form(...),
    ):
    ticket = Ticket(title=title, description=description, creator_id=creator_id)
    upload = Attachment(
        file_name=attachment.filename, 
        file_type=attachment.content_type, 
        ticket_id=ticket.id, 
        creator_id=ticket.creator_id, 
        path=f"{STATIC_DIR}/upload"
        )
    content = attachment.file.read()
    with open(f"{upload.path}/{upload.file_name}", "wb") as file:
        file.write(content)

    helpdesk = get_helpdesk()
    is_created = helpdesk.ticket_api(action="new", ticket=ticket)
    if is_created:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    else:
        # Placeholder for error, this functionality will be implemented later
        return {"response": "error occured in new_ticket route"}

@router.post("/{ticket_id}/assign")
def assign_ticket():
    return {"response": "Assign Ticket Page"}

@router.patch("/{ticket_id}")
def patch_ticket():
    return {"response": "Patch Ticket Page"}

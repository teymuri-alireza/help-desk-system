from fastapi import APIRouter

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("")
def list_tickets():
    return {"response": "List Tickets Page"}

@router.get("/{ticket_id}")
def show_ticket():
    return {"response": "Show Ticket Page"}

@router.post("")
def new_ticket():
    return {"response": "New Ticket Page"}

@router.post("/{ticket_id}/assign")
def assing_ticket():
    return {"response": "Assign Ticket Page"}

@router.patch("/{ticket_id}")
def patch_ticket():
    return {"response": "Patch Ticket Page"}

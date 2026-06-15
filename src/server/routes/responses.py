from fastapi import APIRouter, Request, status, Form
from fastapi.responses import RedirectResponse
from src.server.dependencies import get_helpdesk, get_current_user
from src.database.tables import Response

router = APIRouter(prefix="/tickets/{ticket_id}/responses", tags=["responses"])


@router.get("")
def list_responses():
    return {"response": "List Responses Page"}

@router.post("")
def new_response(
        request: Request, 
        text: str = Form(...), 
        response_ticket_id: int = Form(...), 
    ):
    try:
        user_username = get_current_user(request=request)
    except:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    helpdesk = get_helpdesk()
    found_user = helpdesk.admin_api(action="find_user_by_username", username=user_username)
    if found_user is not None:
        creator_id = found_user.id
        response = Response(text=text, ticket_id=response_ticket_id, creator_id=creator_id)
        helpdesk.response_api(action="new", response=response)
        return RedirectResponse(url=f"/tickets/{response_ticket_id}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return {"response": "not found"}

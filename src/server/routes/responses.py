import logging
from fastapi import APIRouter, Request, status, Form, HTTPException
from fastapi.responses import RedirectResponse
from src.server.dependencies import get_helpdesk, get_current_user
from src.database.tables import Response

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
        found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if found_user is not None:
            responses_list = helpdesk.response_api.list_responses(ticket_id=ticket_id)
            return {"responses": responses_list}
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("")
def new_response(
        request: Request, 
        text: str = Form(...), 
        response_ticket_id: int = Form(...), 
    ):
    try:
        user_username = get_current_user(request=request)
    except HTTPException as e:
        core_logger.error(f"{e} - The access token is missing.")
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    try:
        helpdesk = get_helpdesk()
        found_user = helpdesk.admin_api.find_user_by_username(username=user_username)
        if found_user is not None:
            creator_id = found_user.id
            response = Response(text=text, ticket_id=response_ticket_id, creator_id=creator_id)
            helpdesk.response_api.new_response(response=response)
            return RedirectResponse(url=f"/tickets/{response_ticket_id}", status_code=status.HTTP_303_SEE_OTHER)
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

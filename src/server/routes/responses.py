from fastapi import APIRouter

router = APIRouter(prefix="/tickets/{ticket_id}/responses", tags=["responses"])


@router.get("")
def list_responses():
    return {"response": "List Responses Page"}

@router.post("")
def new_response():
    return {"response": "New Response Page"}

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users():
    return {"response": "List Users Page"}

@router.get("/{user_id}")
def show_user():
    return {"response": "Show User Page"}

@router.post("")
def new_user():
    return {"response": "New User Page"}

@router.patch("/{user_id}")
def patch_user():
    return {"response": "Patch User Page"}

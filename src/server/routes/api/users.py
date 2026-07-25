import logging
from fastapi import APIRouter, Request, status, Path, Form, HTTPException
from fastapi.responses import JSONResponse
from src.server.dependencies import get_helpdesk, get_current_user
from src.database.tables import Role, User, UserStatus, Notification

core_logger = logging.getLogger("core")

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", description="Retrieve list of users")
def list_users(request: Request):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role == Role.SYSTEM_ADMIN:
            users_list = helpdesk.admin_api.list_users()

        elif current_user.role == Role.IT_MANAGER:
            users_list = helpdesk.admin_api.list_it_experts()

        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return JSONResponse(
            content={
                "users_list": [
                    {
                        "id": u.id,
                        "username": u.username,
                        "name": u.name,
                        "email": u.email,
                        "role": u.role.fa,
                        "status": u.status.fa,
                        "department_name": u.department.name if u.department is not None else None,
                    }
                    for u in users_list
                ]
            },
            status_code=status.HTTP_200_OK
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{user_id}", description="Retrieve one user's information")
def show_user(request: Request, user_id: int = Path(...)):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role != Role.SYSTEM_ADMIN and current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        found_user = helpdesk.admin_api.find_user(user_id=user_id)

        if found_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        departments = helpdesk.admin_api.list_ticket_departments()

        return JSONResponse(
            content={
                "user": {
                    "id": found_user.id,
                    "username": found_user.username,
                    "name": found_user.name,
                    "email": found_user.email,
                    "role_fa": found_user.role.fa,
                    "role_en": found_user.role.value,
                    "role_name": found_user.role.name,
                    "status": found_user.status.fa,
                    "status_name": found_user.status.name,
                    "department_id": found_user.department_id,
                    "department_name": found_user.department.name if found_user.department is not None else None,
                    "created_at": found_user.created_at.isoformat(),
                },
                "departments": [
                    {
                        "id": d.id,
                        "name": d.name,
                    } for d in departments
                ],
                "roles": [
                    {
                        "name": r.name,
                        "fa": r.fa,
                    } for r in Role
                ],
                "status": [
                    {
                        "name": s.name,
                        "fa": s.fa,
                    } for s in UserStatus
                ],
            },
            status_code=status.HTTP_200_OK
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("", description="Create a new user")
def new_user(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    department_id: int | None = Form(None),
):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role != Role.SYSTEM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        existing_user = helpdesk.admin_api.find_user_by_username(
            username=username
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        if role == Role.IT_EXPERT.name and department_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department is required for IT experts"
            )

        new_user = User(
            name=name,
            username=username,
            email=email,
            role=role,
            department_id=department_id,
        )

        helpdesk.admin_api.new_user(user=new_user)

        notification = Notification(
            receiver_id=new_user.id,
            title="کاربر جدید",
            text=f"خوش آمدید {new_user.name}",
            url=f"/users/{new_user.id}",
        )

        helpdesk.notification_api.new_notification(notification=notification)

        return JSONResponse(
            content={
                "success": True,
                "message": "User created successfully."
            },
            status_code=status.HTTP_201_CREATED,
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{user_id}", description="Update a user's information")
def patch_user(
        request: Request,
        user_id: int = Path(...),
        name: str | None = Form(None),
        email: str | None = Form(None),
        username: str | None = Form(None),
        role: str | None = Form(None),
        user_status: str | None = Form(None),
        department_id: int | None = Form(None),
    ):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role != Role.SYSTEM_ADMIN and current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        user_to_update = User(
            name=name,
            email=email,
            username=username,
            role=role,
            status=user_status,
            department_id=department_id,
        )

        helpdesk.admin_api.update_user(new_user=user_to_update, old_user_id=user_id)

        return JSONResponse(
            content={
                "success": True,
                "message": "User updated successfully."
            },
            status_code=status.HTTP_200_OK
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{user_id}", description="Delete a user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        request: Request,
        user_id: int = Path(...)
    ):
    user = get_current_user(request)

    helpdesk = get_helpdesk()

    try:
        current_user = helpdesk.admin_api.find_user_by_username(username=user)

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user.role != Role.SYSTEM_ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        helpdesk.admin_api.delete_user(user_id=user_id)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

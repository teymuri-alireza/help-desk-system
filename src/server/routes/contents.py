import logging
from pathlib import Path as FilePath
from fastapi import APIRouter, HTTPException, Request, Path, status
from fastapi.responses import FileResponse, RedirectResponse
from src.server.dependencies import get_helpdesk, get_current_user
from src.database.tables import Role

core_logger = logging.getLogger("core")

UPLOAD_DIR = FilePath(__file__).parent.parent / "upload"

router = APIRouter(prefix="/contents", tags=["contents"])


@router.get("/upload/{filename}")
async def get_upload_file(
        request: Request,
        filename: str = Path(...),
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
            found_attachment = helpdesk.attachment_api.find_attachment(filename=filename)
            if found_attachment is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

            if (current_user.role in (Role.SYSTEM_ADMIN, Role.IT_MANAGER)
                or found_attachment.creator_id == current_user.id
                or found_attachment.ticket.assigned_to == current_user.id):

                file = UPLOAD_DIR / filename

                if not file.exists():
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

                return FileResponse(file)
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        else:
            # Error handler for when db is removed but session exists
            return RedirectResponse(url="/auth/logout", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

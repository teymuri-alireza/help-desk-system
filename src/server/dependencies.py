from jose import jwt
from fastapi import Request
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from pathlib import Path
from datetime import datetime, timedelta, timezone
from src.core.engine import HelpDeskCore

_helpdesk = None
SECRET_KEY = "placeholder_for_secret_key"
ALGORITHM = "HS256"


def get_static_path() -> tuple[Path, Path]:
    """
    Return the paths to the templates and static directories.

    Returns:
        tuple[Path, Path]: A tuple containing (TEMPLATES_DIR, STATIC_DIR)
    """
    TEMPLATES_DIR = Path(__file__).parent / "templates"
    STATIC_DIR = Path(__file__).parent / "static"

    return TEMPLATES_DIR, STATIC_DIR


def set_helpdesk(core: HelpDeskCore) -> None:
    """
    Initialize the global HelpDeskCore instance.

    Args:
        core: The HelpDeskCore instance to set as the global singleton.

    Note:
        This function only sets the helpdesk if it hasn't been initialized yet.
    """
    global _helpdesk
    if _helpdesk is None:
        _helpdesk = core


def get_helpdesk() -> HelpDeskCore:
    """
    Retrieve the global HelpDeskCore instance.

    Returns:
        HelpDeskCore: The initialized HelpDeskCore instance.

    Raises:
        RuntimeError: If HelpDeskCore has not been initialized.
    """
    if _helpdesk is None:
        raise RuntimeError(
            "HelpDeskCore has not been initialized."
        )

    return _helpdesk


def create_access_token(data: dict):
    """
    Create a JWT access token with an expiration time.

    Args:
        data: A dictionary containing the token payload data.

    Returns:
        str: An encoded JWT token with a 7-day expiration.
    """
    payload = data.copy()

    payload["exp"] = (
        datetime.now(timezone.utc)
        + timedelta(days=7)
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def set_access_cookie(response: Response, token: str) -> None:
    """
    Set the access token cookie for the response.

    Args:
        response: The Response object to attach the cookie to.
        token: The JWT access token value to store in the cookie.
    """

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
    )


def clear_access_cookie(response: Response) -> None:
    """
    Remove the access token cookie from the response.

    Args:
        response: The Response object to clear the cookie from.
    """
    response.delete_cookie("access_token")


def get_current_user(request: Request):
    """
    Extract and validate the current user from the request cookies.

    Args:
        request: The FastAPI Request object containing cookies.

    Returns:
        str: The username of the authenticated user.

    Raises:
        HTTPException: If the access token is missing (401 status code).
    """
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_username = payload["sub"]

    return user_username


def get_current_user_optional(request: Request):
    """
    Extract and validate the current user from the request cookies.

    Args:
        request: The FastAPI Request object containing cookies.

    Returns:
        str|None: The username of the authenticated user, otherwise None.
    """
    token = request.cookies.get("access_token")

    if not token:
        return None

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_username = payload["sub"]

    return user_username

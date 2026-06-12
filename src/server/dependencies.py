from pathlib import Path
from src.core.engine import HelpDeskCore

_helpdesk = None


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

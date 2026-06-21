import logging


def get_logger() -> logging.Logger:
    """
    Create the core logger.

    Returns:
        Logger: The core logger.
    """
    file_format = "%(asctime)s [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    core_logger = logging.getLogger("core")

    # Prevent duplicated logging
    if not core_logger.handlers:
        file_handler = logging.FileHandler("helpdesk.log")
        file_handler.setFormatter(logging.Formatter(file_format, datefmt=date_format))
        file_handler.setLevel(logging.ERROR)

        core_logger.addHandler(file_handler)

        core_logger.setLevel(logging.ERROR)

    return core_logger

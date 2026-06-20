from src.database.engine import DatabaseEngine
from src.database.tables import User, Ticket, Response, Attachment, Notification
from src.core.storage import StorageEngine
from src.core.services.admin_service import AdminService
from src.core.services.authentication_service import AuthenticationService
from src.core.services.ticket_service import TicketService
from src.core.services.response_sesrvice import ResponseService
from src.core.services.attachment_service import AttachmentService


class HelpDeskCore:
    """
    Core engine for the Help Desk system that manages authentication, tickets, 
    responses, and notifications through a unified API interface.
    """

    def __init__(self, database_path: str = "sqlite.db") -> None:
        """
        Initialize the HelpDeskCore with database and storage engines.

        Args:
            database_path (str): Path to the SQLite database file. Defaults to `sqlite.db`.
        """
        self.database_engine = DatabaseEngine(database_path)
        self.session_factory = self.database_engine.get_session_factory()

        self.storage = StorageEngine(self.session_factory)

        self.admin_api = AdminService(storage=self.storage)
        self.authentication_api = AuthenticationService(storage=self.storage)
        self.ticket_api = TicketService(storage=self.storage)
        self.response_api = ResponseService(storage=self.storage)
        self.attachment_api = AttachmentService(storage=self.storage)

    def notification_api(
            self,
            action: str,
            notification: Notification = None,
            notification_id: int = None,
            is_read: bool = False,
            user_id: int = None
        ) -> list[Notification] | None:
        """
        Handle notification operations.

        Args:
            action (str): The notification action to perform (`new`, `update`, `list_unread`, or `list_all`).
            notification (Notification): Notification object for new notification creation.
            notification_id (int): ID of the notification for update operations.
            is_read (bool): Boolean flag to mark notification as read/unread.
            user_id (int): User ID to filter notifications.

        Returns:
            list[Notification]: List of notifications for "list_unread" and "list_all" actions, None otherwise.
        """
        if action == "new":
            self.storage.insert_notification(notification)
        elif action == "update":
            self.storage.update_notification(notification_id, is_read)
        elif action == "list_unread":
            return self.storage.list_notifications(user_id)
        elif action == "list_all":
            return self.storage.list_notifications(user_id, unread=False)

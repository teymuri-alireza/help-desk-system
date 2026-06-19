from src.database.engine import DatabaseEngine
from src.database.tables import User, Ticket, Response, Attachment, Notification
from src.core.storage import StorageEngine
from src.core.services.admin_service import AdminService
from src.core.services.authentication_service import AuthenticationService


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

    def ticket_api(
            self,
            action: str,
            ticket: Ticket = None,
            ticket_id: int = None,
            user_id: int | None = None,
            limit: int | None = None,
        ) -> list[Ticket] | Ticket | bool:
        """
        Handle ticket operations.

        Args:
            action (str): The ticket action to perform (`new`, `list`, `find`, or `update`).
            ticket (Ticket): Ticket object for new ticket creation.
            ticket_id (int): ID of the ticket for find or update operations.
            user_id (int | None): User ID to filter tickets for "list" action.
            limit (int | None): The maximum number of tickets to retrieve.

        Returns:
            list[Ticket] | Ticket | bool: List of tickets for "list" action, single ticket for "find" action,
                and boolean for "new" action, indicating it was successful or not.
        """
        if action == "new":
            return self.storage.insert_ticket(ticket)
        elif action == "list":
            return self.storage.list_tickets(user_id, limit)
        elif action == "find":
            return self.storage.find_ticket(ticket_id)
        elif action == "update":
            self.storage.update_ticket(new_ticket=ticket, old_ticket_id=ticket_id)

    def response_api(self, action: str, response: Response = None) -> list[Response] | None:
        """
        Handle response operations.

        Args:
            action (str): The response action to perform (`list` or `new`).
            response (Response): Response object for new response creation.

        Returns:
            list[Response] | None: List of responses for "list" action, None for "new" action.
        """
        if action == "list":
            return self.storage.list_responses()
        elif action == "new":
            self.storage.insert_response(response)

    def attachment_api(self, attachment: Attachment) -> None:
        """
        Handle attachment operations.

        Args:
            attachment (Attachment): Attachment object for new attachment creation.
        """
        self.storage.insert_attachment(attachment)

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

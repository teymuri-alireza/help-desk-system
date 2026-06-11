from src.database.engine import DatabaseEngine
from src.database.tables import User, Ticket, Response, Notification
from src.core.storage import StorageEngine


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

    def authentication_api(self, action: str, user: User, username: str) -> bool | None:
        """
        Handle authentication operations.

        Args:
            action (str): The authentication action to perform (`signup` or `login`).
            user (User): User object for signup operations.
            username (str): Username for login validation.

        **Note:** The sign up option is not implemented yet

        Returns:
            bool: Boolean indicating if user validation is successful, False otherwise.
        """
        if action == "signup":
            # Sign up option is not implemented yet.
            pass
        elif action == "login":
            return self.storage.validate_user(username)

    def ticket_api(self, action: str, ticket: Ticket, ticket_id: int) -> list[Ticket] | Ticket | bool:
        """
        Handle ticket operations.

        Args:
            action (str): The ticket action to perform (`new`, `list`, `find`, or `update`).
            ticket (Ticket): Ticket object for new ticket creation.
            ticket_id (int): ID of the ticket for find or update operations.

        Returns:
            list[Ticket] | Ticket | bool: List of tickets for "list" action, single ticket for "find" action,
                and boolean for "new" and "update" actions, indicating it was successful or not.
        """
        if action == "new":
            return self.storage.insert_ticket(ticket)
        elif action == "list":
            return self.storage.list_tickets()
        elif action == "find":
            return self.storage.find_ticket(ticket_id)
        elif action == "update":
            return self.storage.update_ticket(ticket)

    def response_api(self, action: str, response: Response) -> list[Response]:
        """
        Handle response operations.

        Args:
            action (str): The response action to perform (`list` or `new`).
            response (Response): Response object for new response creation.

        Returns:
            list[Response]: List of responses for "list" action, None otherwise.
        """
        if action == "list":
            return self.storage.list_responses()
        elif action == "new":
            self.storage.insert_response(response)

    def notification_api(self) -> list[Notification]:
        """
        Retrieve all notifications.

        Returns:
            list[Notification]: List of notifications from storage.
        """
        return self.storage.list_notifications()

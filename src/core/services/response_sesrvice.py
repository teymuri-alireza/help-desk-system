from src.core.storage import StorageEngine
from src.database.tables import Response


class ResponseService:
    """
    Service for managing response operations.
    """

    def __init__(self, storage: StorageEngine) -> None:
        """
        Initialize ResponseService with a storage engine.

        Args:
            storage: The StorageEngine instance for database operations.
        """
        self.storage = storage

    def list_responses(self, ticket_id: int) -> list[Response]:
        """
        List response objects.

        Args:
            ticket_id: The ticket ID to filter responses by.

        Returns:
            list[Response]: A list of Response objects.
        """
        return self.storage.list_responses(ticket_id=ticket_id)
    
    def new_response(self, response: Response) -> None:
        """
        Create a new response.

        Args:
            response: The Response object to be created.
        """
        self.storage.insert_response(response)

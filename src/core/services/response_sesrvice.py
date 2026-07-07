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

    def find_response(self, response_id: int) -> Response | None:
        """
        Find a response by their ID.

        Args:
            response_id: The ID of the response to find.

        Returns:
            Response | None: The Response object if found, otherwise None.
        """
        return self.storage.find_response(response_id=response_id)

    def new_response(self, response: Response) -> None:
        """
        Create a new response.

        Args:
            response: The Response object to be created.
        """
        self.storage.insert_response(response)

    def update_response(self, new_response: Response, old_response_id: int) -> None:
        """
        Update an existing response.

        Args:
            new_response: The updated Response object with new data.
            old_response_id: The ID of the Response to be updated.
        """
        self.storage.update_response(new_response=new_response, old_response_id=old_response_id)

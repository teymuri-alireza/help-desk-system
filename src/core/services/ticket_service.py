from src.core.storage import StorageEngine
from src.database.tables import Ticket


class TicketService:
    """
    Service for managing ticket operations.
    """

    def __init__(self, storage: StorageEngine) -> None:
        """
        Initialize TicketService with a storage engine.

        Args:
            storage: The StorageEngine instance for database operations.
        """
        self.storage = storage

    def new_ticket(self, ticket: Ticket) -> None:
        """
        Create a new ticket.

        Args:
            ticket: The Ticket object to be created.
        """
        self.storage.insert_ticket(ticket)

    def list_tickets(self, creator_id: int | None = None, limit: int | None= None) -> list[Ticket]:
        """
        List tickets filtered by creator ID, and with a specified limit.

        Args:
            creator_id: The creator ID to filter tickets by. If None, returns all tickets
            limit: The maximum number of tickets to retrieve.

        Returns:
            list[Ticket]: A list of Ticket objects up to the specified limit.
        """
        return self.storage.list_tickets(creator_id=creator_id, limit=limit)

    def find_ticket(self, ticket_id: int) -> Ticket | None:
        """
        Find a ticket by their ID.

        Args:
            ticket_id: The ID of the ticket to find.

        Returns:
            Ticket | None: The Ticket object if found, otherwise None.
        """
        return self.storage.find_ticket(ticket_id)

    def update_ticket(self, new_ticket: Ticket, old_ticket_id: int) -> None:
        """
        Update an existing ticket.

        Args:
            new_ticket: The updated Ticket object with new data.
            old_ticket_id: The ID of the ticket to be updated.
        """
        self.storage.update_ticket(new_ticket=new_ticket, old_ticket_id=old_ticket_id)

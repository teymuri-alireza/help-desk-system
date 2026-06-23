from src.core.storage import StorageEngine
from src.database.tables import Attachment


class AttachmentService:
    """
    Service for managing attachment operations.
    """

    def __init__(self, storage: StorageEngine) -> None:
        """
        Initialize AttachmentService with a storage engine.

        Args:
            storage: The StorageEngine instance for database operations.
        """
        self.storage = storage

    def new_attachment(self, attachment: Attachment) -> None:
        """
        Create a new attachment.

        Args:
            attachment: The Attachment object to be created.
        """
        self.storage.insert_attachment(attachment)

    def find_attachment(self, ticket_id: int) -> Attachment | None:
        """
        Find an attachment by its ticket ID.

        Args:
            ticket_id: The ticket ID to search for.

        Returns:
            attachment|None: attachment object if found, None otherwise.
        """
        return self.storage.find_attachment(ticket_id)

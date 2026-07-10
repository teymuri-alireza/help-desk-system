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

    def find_attachment(self, ticket_id: int | None = None, filename: str | None = None) -> Attachment | None:
        """
        Retrieve an attachment record.

        The method supports lookup by ticket ID or by attachment filename. If both
        values are provided, the ticket ID lookup takes precedence.

        Args:
            ticket_id: Optional ticket ID to search attachments by.
            filename: Optional attachment filename to search by.

        Returns:
            Attachment|None: The matched Attachment object, or None if no record
                matches the provided arguments.
        """
        return self.storage.find_attachment(ticket_id=ticket_id, filename=filename)

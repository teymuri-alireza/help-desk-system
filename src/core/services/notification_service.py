from src.core.storage import StorageEngine
from src.database.tables import Notification


class NotificationService:
    """
    Service for managing admin operations related to users.
    """

    def __init__(self, storage: StorageEngine) -> None:
        """
        Initialize AdminService with a storage engine.

        Args:
            storage: The StorageEngine instance for database operations.
        """
        self.storage = storage

    def new_notification(self, notification: Notification) -> None:
        """
        Create a new notification.

        Args:
            notification: The Notification object to create.
        """
        self.storage.insert_notification(notification=notification)

    def update_notification(self, notification_id: int, is_read: bool = False) -> None:
        """
        Update a notification's read status.

        Args:
            notification_id: The ID of the notification to update.
            is_read: Whether the notification has been read.
        """
        self.storage.update_notification(notification_id=notification_id, is_read=is_read)

    def list_unread(self, receiver_id: int) -> list[Notification]:
        """
        List all unread notifications for a receiver.

        Args:
            receiver_id: The ID of the receiver.

        Returns:
            List of unread notifications.
        """
        return self.storage.list_notifications(receiver_id=receiver_id)

    def list_all(self, receiver_id: int, unread: bool = False) -> list[Notification]:
        """
        List all notifications for a receiver.

        Args:
            receiver_id: The ID of the receiver.
            unread: Filter for unread notifications.

        Returns:
            List of notifications.
        """
        return self.storage.list_notifications(receiver_id=receiver_id, unread=unread)

    def find_notification(self, notification_id: int) -> Notification | None:
        """
        Find a notification by ID.

        Args:
            notification_id: The notification ID to search for.

        Returns:
            Notification|None: Notification object if found, otherwise None.
        """
        return self.storage.find_notification(notification_id=notification_id)

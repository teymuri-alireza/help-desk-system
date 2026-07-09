from src.core.storage import StorageEngine
from src.database.tables import User


class AuthenticationService:
    """
    Service for managing authentication operations related to users.
    """

    def __init__(self, storage: StorageEngine) -> None:
        """
        Initialize AuthenticationService with a storage engine.

        Args:
            storage: The StorageEngine instance for database operations.
        """
        self.storage = storage

    def signup(self, user: User) -> None:
        """
        Register a new user.

        Args:
            user: The User object to be registered.
        """
        self.storage.insert_user(user)

    def login(self, username: str) -> bool:
        """
        Validate user login credentials.

        Args:
            username: The username to validate.

        Returns:
            bool: True if user validation is successful, False otherwise.
        """
        return self.storage.validate_user(username)

    def validate_user_status(self, username: str) -> bool:
        """
        Validate if a user is not suspended.

        Args:
            username: The username to search for.

        Returns:
            bool: True if user is not suspended, otherwise False.
        """
        return self.storage.validate_user_status(username=username)

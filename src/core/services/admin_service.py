from src.core.storage import StorageEngine
from src.database.tables import User, Role


class AdminService:
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

    def new_user(self, user: User) -> None:
        """
        Create a new user.

        Args:
            user: The User object to be created.
        """
        self.storage.insert_user(user=user)

    def list_users(self, limit: int) -> list[User]:
        """
        List users with a specified limit.

        Args:
            limit: The maximum number of users to retrieve.

        Returns:
            list[User]: A list of User objects up to the specified limit.
        """
        return self.storage.list_users(limit=limit)

    def list_it_experts(self) -> list[User]:
        """
        List all IT expert users.

        Returns:
            list[User]: A list of User objects with IT_EXPERT role.
        """
        return self.storage.list_users(role=Role.IT_EXPERT)

    def find_user(self, user_id: int) -> User | None:
        """
        Find a user by their ID.

        Args:
            user_id: The ID of the user to find.

        Returns:
            User | None: The User object if found, otherwise None.
        """
        return self.storage.find_user(user_id)

    def find_user_by_username(self, username: str) -> User | None:
        """
        Find a user by their username.

        Args:
            username: The username of the user to find.

        Returns:
            User | None: The User object if found, otherwise None.
        """
        return self.storage.find_user_by_username(username)

    def update_user(self, new_user: User, old_user_id: int) -> None:
        """
        Update an existing user.

        Args:
            new_user: The updated User object with new data.
            old_user_id: The ID of the user to be updated.
        """
        self.storage.update_user(new_user=new_user, old_user_id=old_user_id)

    def delete_user(self, user_id: int) -> None:
        """
        Delete a user by their ID.

        Args:
            user_id: The ID of the user to delete.
        """
        self.storage.delete_user(user_id=user_id)

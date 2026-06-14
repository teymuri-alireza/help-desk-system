from sqlalchemy.orm import Session, sessionmaker
from src.database.tables import User, Ticket, Response, Attachment, Notification
from sqlalchemy.orm import joinedload
class StorageEngine:
    """
    Database storage engine for managing database tables.

    This class provides an interface for performing CRUD operations on database entities
    using SQLAlchemy ORM.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        """
        Initialize the StorageEngine with a session factory.

        Args:
            session_factory: A SQLAlchemy sessionmaker instance used to create database sessions.
        """
        self.session_factory = session_factory

    def insert_user(self, user: User) -> None:
        """
        Insert a new user into the database.

        Args:
            user: The User object to insert.
        """
        with self.session_factory() as session:
            session.add(user)
            session.commit()

    def validate_user(self, username) -> bool:
        """
        Validate if a user exists in the databse by username.

        Args:
            username: The username to search for.

        Returns:
            bool: True if user exists, otherwise False.
        """
        with self.session_factory() as session:
            found_user = session.query(User).filter(User.username==username).one_or_none()
            if found_user is not None:
                return True
            return False

    def list_tickets(self) -> list[Ticket]:
        """
        Retrieve all tickets.

        Returns:
            list[Ticket]: List of all Ticket objects.
        """
        with self.session_factory() as session:
            tickets = session.query(Ticket).options(joinedload(Ticket.creator)).all()
            return tickets

    def find_ticket(self, ticket_id: int) -> Ticket | None:
        """
        Find a ticket by ID.

        Args:
            ticket_id: The ticket ID to search for.

        Returns:
            Ticket|None: Ticket object if found, otherwise None.
        """
        with self.session_factory() as session:
            found_ticket = session.query(Ticket).filter(Ticket.id==ticket_id).one_or_none()
            return found_ticket

    def insert_ticket(self, ticket: Ticket) -> bool:
        """
        Insert a new ticket into the database.

        Args:
            ticket: The Ticket object to insert.

        Returns:
            bool: True if ticket was inserted, False if error occured.
        """
        with self.session_factory() as session:
            session.add(ticket)
            session.commit()
            return True
        return False

    def update_ticket(self, ticket: Ticket) -> bool:
        """
        Update an existing ticket in the database.

        Args:
            ticket: The Ticket object with updated values.

        Returns:
            bool: True if ticket was updated, False if ticket not found.
        """
        with self.session_factory() as session:
            old_ticket = session.query(Ticket).filter(Ticket.id==ticket.id).one_or_none()
            if old_ticket is not None:
                session.merge(ticket)
                session.commit()
                return True
            return False

    def list_responses(self, ticket_id: int) -> list[Response]:
        """
        Retrieve all responses for a ticket.

        Args:
            ticket_id: The ticket ID to retrieve responses for.

        Returns:
            list[Response]: List of Response objects for the ticket.
        """
        with self.session_factory() as session:
            found_ticket = session.query(Ticket).filter(Ticket.id==ticket_id).one_or_none()
            return found_ticket.responses

    def insert_response(self, response: Response) -> None:
        """
        Insert a new response into the database.

        Args:
            response: The Response object to insert.
        """
        with self.session_factory() as session:
            session.add(response)
            session.commit()

    def insert_attachment(self, attachment: Attachment):
        """
        Insert a new attachment into the database.

        Args:
            attachment: The Attachment object to insert.
        """
        with self.session_factory() as session:
            session.add(attachment)
            session.commit()
            session.refresh(attachment)

    def insert_notification(self, notification: Notification) -> None:
        """
        Insert a new notification into the database.

        Args:
            notification: The Notification object to insert.
        """
        with self.session_factory() as session:
            session.add(notification)
            session.commit()

    def update_notification(self, notification_id: int, is_read: bool) -> None:
        """
        Update the read status of a notification.

        Args:
            notification_id: The notification ID to update.
            is_read: The new read status value.
        """
        with self.session_factory() as session:
            old_notification = session.query(Notification).filter(Notification.id==notification_id).one_or_none()
            if old_notification is not None:
                old_notification.is_read = is_read
                session.commit()

    def list_notifications(self, user_id: int, unread: bool = True) -> list[Notification]:
        """
        Retrieve notifications for a user.

        Args:
            user_id: The user ID to retrieve notifications for.
            unread: If True, retrieve only unread notifications; if False,
                retrieve all notifications.

        Returns:
            list[Notification]: List of Notification objects for the user.
        """
        with self.session_factory() as session:
            if unread:
                fetched_notifications = session.query(Notification).filter(
                    Notification.receiver_id==user_id, Notification.is_read==False
                    ).all()
            else:
                fetched_notifications = session.query(Notification).filter(
                    Notification.receiver_id==user_id).order_by(Notification.id.desc()).all()

            return fetched_notifications

    def list_users(self) -> list[User]:
        """
        Retrieve all users.

        Returns:
            List[User]: List of all User objects.
        """
        with self.session_factory() as session:
            users_list = session.query(User).all()
            return users_list

    def find_user(self, user_id: int) -> User | None:
        """
        Find a user by ID.

        Args:
            user_id: The user ID to search for.

        Returns:
            User|None: User object if found, None otherwise.
        """
        with self.session_factory() as session:
            found_user = session.query(User).filter(User.id==user_id).one_or_none()
            return found_user

    def find_user_by_username(self, username: str) -> User | None:
        """
        Find a user by username.

        Args:
            username: The user's username to search for.

        Returns:
            User|None: User object if found, None otherwise.
        """
        with self.session_factory() as session:
            found_user = session.query(User).filter(User.username==username).one_or_none()
            return found_user

    def update_user(self, user: User) -> bool:
        """
        Update an existing user in the database.

        Args:
            user: The user object with updated values.

        Returns:
            bool: True if user was updated, False if user not found.
        """
        with self.session_factory() as session:
            found_user = session.query(User).filter(User.id==user.id).one_or_none()
            if found_user is not None:
                session.merge(user)
                session.commit()
                return True
            return False

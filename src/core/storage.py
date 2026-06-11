from sqlalchemy.orm import Session, sessionmaker
from src.database.tables import User, Ticket, Response, Notification

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
        This functions is not complete yet.
        """
        pass

    def validate_user(self, username) -> bool:
        """
        Validate if a user exists in the databse by username.

        Args:
            username: The username to search for.

        Returns:
            bool: True if user exists, otherwise False.
        """
        with self.session_factory() as session:
            found_user = session.query(User).filter_by(User.username==username).one_or_none()
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
            tickets = session.query(Ticket).all()
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
            found_ticket = session.query(Ticket).filter_by(Ticket.id==ticket_id).one_or_none()
            return found_ticket

    def insert_ticket(self, ticket: Ticket) -> None:
        """
        Insert a new ticket into the database.

        Args:
            ticket: The Ticket object to insert.
        """
        with self.session_factory() as session:
            session.add(ticket)
            session.commit()

    def update_ticket(self, ticket: Ticket) -> None:
        """
        This functions is not complete yet.
        """
        pass

    def list_responses(self, ticket_id: int) -> list[Response]:
        """
        Retrieve all responses for a ticket.

        Args:
            ticket_id: The ticket ID to retrieve responses for.

        Returns:
            list[Response]: List of Response objects for the ticket.
        """
        with self.session_factory() as session:
            found_ticket = session.query(Ticket).filter_by(Ticket.id==ticket_id).one_or_none()
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

    def list_notifications(self, user_id: int) -> list[Notification]:
        """
        Retrieve all notifications for a user.

        Args:
            user_id: The user ID to retrieve notifications for.

        Returns:
            list[Notification]: List of Notification objects for the user.
        """
        with self.session_factory() as session:
            not_read_notifications = session.query(Notification).filter_by(Notification.receiver_id==user_id).all()
            return not_read_notifications

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
            found_user = session.query(User).filter_by(User.id==user_id).one_or_none()
            return found_user

    def update_user(self, user: User) -> None:
        """
        This functions is not complete yet.
        """
        pass

import logging
from sqlalchemy.orm import Session, sessionmaker
from src.database.tables import User, Ticket, Response, Attachment, Notification
from sqlalchemy.orm import joinedload

core_logger = logging.getLogger("core")


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
        try:
            with self.session_factory() as session:
                session.add(user)
                session.commit()
                session.refresh(user)
        except Exception as e:
            core_logger.error(f"Insert user failed - {e}")
            raise

    def validate_user(self, username: str) -> bool:
        """
        Validate if a user exists in the database by username.

        Args:
            username: The username to search for.

        Returns:
            bool: True if user exists, otherwise False.
        """
        try:
            with self.session_factory() as session:
                found_user = session.query(User).filter(User.username==username).one_or_none()
                if found_user is not None:
                    return True
                return False
        except Exception as e:
            core_logger.error(f"Validate user failed - {e}")
            raise

    def list_tickets(self, creator_id: int | None, assigned_to: int | None, limit: int | None) -> list[Ticket]:
        """
        Retrieve all tickets.

        Args:
            creator_id: The creator ID to filter tickets by. If None, returns all tickets.
            assigned_to: The assignee ID to filter tickets by. If None, returns all tickets.
            limit: The maximum number of tickets to retrieve.

        Returns:
            list[Ticket]: List of all Ticket objects.
        """
        try:
            with self.session_factory() as session:
                if creator_id is not None:
                    tickets = session.query(Ticket).options(
                        joinedload(Ticket.creator), joinedload(Ticket.responses), joinedload(Ticket.assignee)).filter(
                        Ticket.creator_id==creator_id
                    ).order_by(Ticket.id.desc()).limit(limit=limit).all()
                elif assigned_to is not None:
                    tickets = session.query(Ticket).options(
                        joinedload(Ticket.creator), joinedload(Ticket.responses), joinedload(Ticket.assignee)).filter(
                        Ticket.assigned_to==assigned_to
                    ).order_by(Ticket.id.desc()).limit(limit=limit).all()
                else:
                    tickets = session.query(Ticket).options(
                        joinedload(Ticket.creator), joinedload(Ticket.responses), joinedload(Ticket.assignee)).order_by(
                        Ticket.id.desc()
                    ).limit(limit=limit).all()
                return tickets
        except Exception as e:
            core_logger.error(f"List tickets failed - {e}")
            raise

    def find_ticket(self, ticket_id: int) -> Ticket | None:
        """
        Find a ticket by ID.

        Args:
            ticket_id: The ticket ID to search for.

        Returns:
            Ticket|None: Ticket object if found, otherwise None.
        """
        try:
            with self.session_factory() as session:
                found_ticket = session.query(Ticket).options(
                    joinedload(Ticket.creator),
                    joinedload(Ticket.responses).joinedload(Response.creator),
                    joinedload(Ticket.assignee)
                    ).filter(Ticket.id==ticket_id).one_or_none()
                return found_ticket
        except Exception as e:
            core_logger.error(f"Find ticket failed - {e}")
            raise

    def insert_ticket(self, ticket: Ticket) -> None:
        """
        Insert a new ticket into the database.

        Args:
            ticket: The Ticket object to insert.
        """
        try:
            with self.session_factory() as session:
                session.add(ticket)
                session.commit()
                session.refresh(ticket)
        except Exception as e:
            core_logger.error(f"Insert ticket failed - {e}")
            raise

    def update_ticket(self, new_ticket: Ticket, old_ticket_id: int) -> None:
        """
        Update an existing ticket in the database.

        Args:
            new_ticket: The Ticket object with updated values.
            old_ticket_id: The old Ticket ID to search for.
        """
        try:
            with self.session_factory() as session:
                found_ticket = session.query(Ticket).filter(Ticket.id==old_ticket_id).one_or_none()
                if found_ticket is not None:
                    for field in ["title", "description", "status", "priority", "assigned_to"]:
                        value = getattr(new_ticket, field)
                        if value is not None:
                            setattr(found_ticket, field, value)
                    session.commit()
                    session.refresh(found_ticket)
        except Exception as e:
            core_logger.error(f"Update ticket failed - {e}")
            raise

    def list_responses(self, ticket_id: int) -> list[Response]:
        """
        Retrieve all responses for a ticket.

        Args:
            ticket_id: The ticket ID to retrieve responses for.

        Returns:
            list[Response]: List of Response objects for the ticket.
        """
        try:
            with self.session_factory() as session:
                found_responses = session.query(Response).options(joinedload(Response.creator)).filter(
                    Response.ticket_id==ticket_id).all()
                return found_responses
        except Exception as e:
            core_logger.error(f"List responses failed - {e}")
            raise

    def insert_response(self, response: Response) -> None:
        """
        Insert a new response into the database.

        Args:
            response: The Response object to insert.
        """
        try:
            with self.session_factory() as session:
                session.add(response)
                session.commit()
        except Exception as e:
            core_logger.error(f"Insert response failed - {e}")
            raise

    def insert_attachment(self, attachment: Attachment) -> None:
        """
        Insert a new attachment into the database.

        Args:
            attachment: The Attachment object to insert.
        """
        try:
            with self.session_factory() as session:
                session.add(attachment)
                session.commit()
                session.refresh(attachment)
        except Exception as e:
            core_logger.error(f"Insert attachment failed - {e}")
            raise

    def insert_notification(self, notification: Notification) -> None:
        """
        Insert a new notification into the database.

        Args:
            notification: The Notification object to insert.
        """
        try:
            with self.session_factory() as session:
                session.add(notification)
                session.commit()
        except Exception as e:
            core_logger.error(f"Insert notification failed - {e}")
            raise

    def update_notification(self, notification_id: int, is_read: bool) -> None:
        """
        Update the read status of a notification.

        Args:
            notification_id: The notification ID to update.
            is_read: The new read status value.
        """
        try:
            with self.session_factory() as session:
                old_notification = session.query(Notification).filter(Notification.id==notification_id).one_or_none()
                if old_notification is not None:
                    old_notification.is_read = is_read
                    session.commit()
        except Exception as e:
            core_logger.error(f"Update notification failed - {e}")
            raise

    def list_notifications(self, receiver_id: int, unread: bool = True) -> list[Notification]:
        """
        Retrieve notifications for a user.

        Args:
            receiver_id: The receiver ID to retrieve notifications for.
            unread: If True, retrieve only unread notifications; if False,
                retrieve all notifications.

        Returns:
            list[Notification]: List of Notification objects for the user.
        """
        try:
            with self.session_factory() as session:
                if unread:
                    fetched_notifications = session.query(Notification).filter(
                        Notification.receiver_id==receiver_id, Notification.is_read==False
                        ).all()
                else:
                    fetched_notifications = session.query(Notification).filter(
                        Notification.receiver_id==receiver_id).order_by(Notification.id.desc()).all()

                return fetched_notifications
        except Exception as e:
            core_logger.error(f"List notifications failed - {e}")
            raise

    def list_users(self, limit: int | None = None, role: str | None = None) -> list[User]:
        """
        Retrieve all users.

        Args:
            limit: The maximum number of tickets to retrieve.

        Returns:
            list[User]: List of all User objects.
        """
        try:
            with self.session_factory() as session:
                if role is not None:
                    users_list = session.query(User).order_by(
                        User.id.desc()
                    ).limit(limit=limit).filter(User.role==role).all()
                else:
                    users_list = session.query(User).order_by(
                        User.id.desc()
                    ).limit(limit=limit).all()
                return users_list
        except Exception as e:
            core_logger.error(f"List users failed - {e}")
            raise

    def find_user(self, user_id: int) -> User | None:
        """
        Find a user by ID.

        Args:
            user_id: The user ID to search for.

        Returns:
            User|None: User object if found, None otherwise.
        """
        try:
            with self.session_factory() as session:
                found_user = session.query(User).filter(User.id==user_id).one_or_none()
                return found_user
        except Exception as e:
            core_logger.error(f"Find user failed - {e}")
            raise

    def find_user_by_username(self, username: str) -> User | None:
        """
        Find a user by username.

        Args:
            username: The user's username to search for.

        Returns:
            User|None: User object if found, None otherwise.
        """
        try:
            with self.session_factory() as session:
                found_user = session.query(User).filter(User.username==username).one_or_none()
                return found_user
        except Exception as e:
            core_logger.error(f"Find user by username failed - {e}")
            raise

    def update_user(self, new_user: User, old_user_id: int) -> None:
        """
        Update an existing user in the database.

        Args:
            user: The user object with updated values.
        """
        try:
            with self.session_factory() as session:
                found_user = session.query(User).filter(User.id==old_user_id).one_or_none()
                if found_user is not None:
                    for field in ["name", "username", "email", "role", "status"]:
                        value = getattr(new_user, field)
                        if value is not None:
                            setattr(found_user, field, value)
                    session.commit()
                    session.refresh(found_user)
        except Exception as e:
            core_logger.error(f"Update user failed - {e}")
            raise

    def delete_user(self, user_id: int) -> None:
        """
        Delete an existing user in the database.

        Args:
            user_id: The user_id to search for deleting.
        """
        try:
            with self.session_factory() as session:
                user_to_delete = session.query(User).filter(User.id==user_id).one_or_none()
                if user_to_delete is not None:
                    session.delete(user_to_delete)
                    session.commit()
        except Exception as e:
            core_logger.error(f"Delete user failed - {e}")
            raise

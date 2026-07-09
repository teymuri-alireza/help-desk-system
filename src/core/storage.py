import logging
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker
from src.database.tables import User, Ticket, Response, Attachment, Notification, TicketStatus, Category, Department, Role
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
                    joinedload(Ticket.assignee),
                    joinedload(Ticket.category),
                    joinedload(Ticket.department),
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
                    for field in ["title", "description", "status", "priority", "assigned_to", "category_id", "department_id"]:
                        value = getattr(new_ticket, field)
                        if value is not None:
                            setattr(found_ticket, field, value)
                    if new_ticket.assigned_to is not None:
                        if new_ticket.status == TicketStatus.NEW.name and found_ticket.status == TicketStatus.NEW.name:
                            # Update ticket status if it's assigned if it's not chnaged before.
                            found_ticket.status = TicketStatus.IN_PROGRESS
                    session.commit()
                    session.refresh(found_ticket)
        except Exception as e:
            core_logger.error(f"Update ticket failed - {e}")
            raise

    def reopen_ticket(self, ticket_id: int) -> None:
        """
        Re-open a ticket after it has been resolved or closed.

        Args:
            ticket_id: The ID of the ticket to re-open.
        """
        try:
            with self.session_factory() as session:
                found_ticket = session.query(Ticket).filter(Ticket.id==ticket_id).one_or_none()
                if found_ticket is not None:
                    if found_ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
                        found_ticket.status = TicketStatus.IN_PROGRESS
                        session.commit()
                        session.refresh(found_ticket)
        except Exception as e:
            core_logger.error(f"Reopen ticket failed - {e}")
            raise

    def assign_ticket(self, ticket_id: int, assigned_to: int) -> None:
        """
        Assign a ticket to an IT expert.

        Args:
            ticket_id: The ID of the ticket to assign.
            assigned_to: The ID of the IT expert to assign the ticket to.
        """
        try:
            with self.session_factory() as session:
                found_ticket = session.query(Ticket).filter(Ticket.id==ticket_id).one_or_none()
                if found_ticket is not None:
                    found_ticket.assigned_to = assigned_to
                    if found_ticket.status == TicketStatus.NEW:
                            # Update ticket status if it's assigned and not chnaged before.
                            found_ticket.status = TicketStatus.IN_PROGRESS
                    session.commit()
                    session.refresh(found_ticket)
        except Exception as e:
            core_logger.error(f"Assign ticket failed - {e}")
            raise

    def rate_ticket(self, ticket_id: int, satisfaction_rating: int) -> None:
        """
        Rate a ticket after it has been resolved or closed.

        Args:
            ticket_id: The ID of the ticket to rate.
            satisfaction_rating: The satisfaction rating to assign.
        """
        try:
            with self.session_factory() as session:
                found_ticket = session.query(Ticket).filter(Ticket.id==ticket_id).one_or_none()
                if (
                    found_ticket is not None
                    and found_ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED)
                ):
                    found_ticket.satisfaction_rating = satisfaction_rating
                    session.commit()
                    session.refresh(found_ticket)
        except Exception as e:
            core_logger.error(f"Rate ticket failed - {e}")
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

    def find_response(self, response_id: int) -> Response | None:
        """
        Find a response by ID.

        Args:
            response_id: The Response ID to search for.

        Returns:
            Response|None: Response object if found, otherwise None.
        """
        try:
            with self.session_factory() as session:
                found_response = session.query(Response).options(
                    joinedload(Response.creator),
                    joinedload(Response.ticket),
                    ).filter(Response.id==response_id).one_or_none()
                return found_response
        except Exception as e:
            core_logger.error(f"Find response failed - {e}")
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

    def update_response(self, new_response: Response, old_response_id: int) -> None:
        """
        Update an existing response in the database.

        Args:
            new_response: The Response object with updated values.
            old_response_id: The old Response ID to search for.
        """
        try:
            with self.session_factory() as session:
                found_response = session.query(Response).filter(Response.id==old_response_id).one_or_none()
                if found_response is not None:
                    if new_response.text is not None:
                        found_response.text = new_response.text
                    session.commit()
                    session.refresh(found_response)
        except Exception as e:
            core_logger.error(f"Update response failed - {e}")
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

    def find_attachment(self, ticket_id: int) -> Attachment | None:
        """
        Find an attachment by its ticket ID.

        Args:
            ticket_id: The ticket ID to search for.

        Returns:
            attachment|None: attachment object if found, None otherwise.
        """
        try:
            with self.session_factory() as session:
                found_attachment = session.query(Attachment).filter(Attachment.ticket_id==ticket_id).one_or_none()
                return found_attachment
        except Exception as e:
            core_logger.error(f"Find attachment failed - {e}")
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

    def list_users(self, limit: int | None = None, role: str | None = None, department_id: int | None = None) -> list[User]:
        """
        Retrieve users, optionally filtered by role and department.

        Args:
            limit: The maximum number of users to retrieve.
            role: Filter users by role if provided.
            department_id: Filter users by department ID if provided.

        Returns:
            list[User]: List of User objects.
        """
        try:
            with self.session_factory() as session:
                if role is not None:
                    if department_id is None:
                        users_list = session.query(User).order_by(User.id.desc()).options(
                            joinedload(User.department)
                        ).limit(limit=limit).filter(User.role==role).all()
                    else:
                        users_list = session.query(User).order_by(User.id.desc()).options(
                            joinedload(User.department)
                        ).limit(limit=limit).filter(User.role==role, User.department_id==department_id).all()
                else:
                    users_list = session.query(User).order_by(User.id.desc()).options(
                        joinedload(User.department)
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
                found_user = session.query(User).filter(User.id==user_id).options(
                    joinedload(User.department)
                ).one_or_none()
                return found_user
        except Exception as e:
            core_logger.error(f"Find user failed - {e}")
            raise

    def find_free_it_expert(self, department_id: int) -> User | None:
        """
        Find an available IT expert in a department with the fewest assigned tickets.

        Args:
            department_id: The department ID to search for available IT experts.

        Returns:
            User|None: IT expert user object with fewest assignments, None if none found.
        """
        try:
            with self.session_factory() as session:
                free_it_expert = session.query(User).outerjoin(Ticket, Ticket.assigned_to == User.id).filter(
                        User.role == Role.IT_EXPERT,
                        User.department_id == department_id,
                    ).group_by(User.id).order_by(func.count(Ticket.id).asc()).first()
                return free_it_expert
        except Exception as e:
            core_logger.error(f"Find free IT expert failed - {e}")
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
                    for field in ["name", "username", "email", "role", "status", "department_id"]:
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

    def list_ticket_categories(self) -> list[Category]:
        """
        Retrieve all ticket categories from the database.

        Returns:
            list[Category]: A list of Category objects.
        """
        try:
            with self.session_factory() as session:
                return session.query(Category).all()
        except Exception as e:
            core_logger.error(f"List Ticket Categories failed - {e}")
            raise

    def list_ticket_departments(self) -> list[Department]:
        """
        Retrieve all ticket departments from the database.

        Returns:
            list[Department]: A list of Department objects.
        """
        try:
            with self.session_factory() as session:
                return session.query(Department).all()
        except Exception as e:
            core_logger.error(f"List Ticket Departments failed - {e}")
            raise

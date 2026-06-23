from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker
from src.database.tables import User, Ticket, UserStatus, TicketStatus


class StatsService:
    """
    Service for classifying statistics.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        """
        Initialize StatsService with a session factory.

        Args:
            session_factory: A SQLAlchemy sessionmaker instance used to create database sessions.
        """
        self.session_factory = session_factory

    def ticket_stats(self) -> tuple[int, int, int, int]:
        """
        Return aggregate ticket statistics.

        Returns:
            tuple[int, int, int, int]: Total tickets, active tickets, unassigned tickets,
                and tickets created in the last 24 hours.
        """
        with self.session_factory() as session:
            all_ticket = session.query(Ticket).count()
            active_stats = session.query(func.count(Ticket.id)).filter(Ticket.status.in_([
                TicketStatus.NEW,
                TicketStatus.IN_PROGRESS,
                TicketStatus.WAITING_FOR_USER
            ])).scalar()
            not_assigned_tickets = session.query(Ticket).filter(Ticket.assigned_to==None).count()

            last_24_hours = datetime.now() - timedelta(hours=24)
            last_created = session.query(Ticket).filter(Ticket.created_at >= last_24_hours).count()

            return all_ticket, active_stats, not_assigned_tickets, last_created

    def it_expert_stats(self, it_expert_id: int) -> tuple[int, int, int]:
        """
        Return statistics for a specific IT expert.

        Args:
            it_expert_id: The ID of the IT expert.

        Returns:
            tuple[int, int, int]: Number of assigned tickets, number of open assigned tickets,
                and number of resolved or closed tickets.
        """
        with self.session_factory() as session:
            assigned_tickets = session.query(Ticket).filter(Ticket.assigned_to==it_expert_id).count()
            open_tickets = session.query(Ticket).filter(Ticket.assigned_to==it_expert_id, Ticket.status.in_([
                TicketStatus.NEW,
                TicketStatus.IN_PROGRESS,
                TicketStatus.WAITING_FOR_USER
            ])).count()
            resolved_tickets = session.query(Ticket).filter(Ticket.assigned_to==it_expert_id, Ticket.status.in_([
                TicketStatus.RESOLVED,
                TicketStatus.CLOSED
            ])).count()

            return assigned_tickets, open_tickets, resolved_tickets

    def users_stats(self) -> tuple[int, int]:
        """
        Return summary user statistics.

        Returns:
            tuple[int, int]: Total number of users and number of active users.
        """
        with self.session_factory() as session:
            all_users = session.query(User).count()
            active_users = session.query(func.count(User.id)).filter(User.status.in_([
                UserStatus.ACTIVE
            ])).scalar()

            return all_users, active_users

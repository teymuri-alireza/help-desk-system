import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker
from src.database.tables import User, Ticket, UserStatus, TicketStatus

core_logger = logging.getLogger("core")
CHARTS_DIR = Path(__file__).parent.parent.parent / "server" / "static" / "charts"


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

    def users_role_pie_chart(self) -> None:
        """
        Generate and save a pie chart showing the distribution of user roles.

        This method queries the database for user roles and their counts, then
        generates a pie chart and saves it to the configured charts directory.
        If there is no role data, it falls back to creating an empty chart
        indicating that no users were found.
        """
        try:
            with self.session_factory() as session:
                user_role_grouped = session.query(User.role, func.count(User.id)).group_by(User.role).all()
            roles = []
            data = []
            for role, count in user_role_grouped:
                roles.append(role.fa)
                data.append(count)
            if not data:
                self.create_empty_chart(
                    f"{CHARTS_DIR}/user_role.png",
                    "کاربری یافت نشد"
                )
                return

            colors = plt.cm.tab10.colors
            wedge_properties = {'linewidth': 1, 'edgecolor': "black"}

            def create_autocpt(pct, allvalues):
                absolute = int(pct / 100.*np.sum(allvalues))
                return "{:.1f}%\n({:d} نفر)".format(pct, absolute)

            fig, ax = plt.subplots(figsize=(10, 7))
            wedges, texts, autotexts = ax.pie(data,
                autopct=lambda pct: create_autocpt(pct, data),
                labels=roles,
                colors=colors,
                startangle=90,
                wedgeprops=wedge_properties,
                textprops=dict(color="black")
            )

            plt.setp(autotexts, size=8, weight="bold")
            plt.savefig(f"{CHARTS_DIR}/user_role.png")
            plt.close(fig)
        except Exception as e:
            core_logger.error(f"Users Role Pie Chart failed: {e}")
            raise

def create_empty_chart(self, filename: str, message: str) -> None:
        """
        Create and save a fallback chart when no valid data is available.

        Args:
            filename: Path to save the generated chart image.
            message: Text to display in the chart explaining the absence of data.
        """
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.pie([1], colors=["lightgray"])
        ax.text(0, 0, message, ha="center", va="center", fontsize=12, fontweight="bold")

        plt.savefig(filename)
        plt.close(fig)

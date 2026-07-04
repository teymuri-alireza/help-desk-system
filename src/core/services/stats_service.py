import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker
from src.database.tables import User, Ticket, Role, UserStatus, TicketStatus, Category, Department

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
            plt.savefig(f"{CHARTS_DIR}/user_role.png", transparent=True)
            plt.close(fig)
        except Exception as e:
            core_logger.error(f"Users Role Pie Chart failed: {e}")
            raise

    def tickets_status_bar_chart(self) -> None:
        """
        Generate and save a bar chart showing the distribution of ticket statuses.

        This method queries the database for ticket statuses and their counts, then
        generates a bar chart and saves it to the configured charts directory.
        If there is no status data, it falls back to creating an empty chart
        indicating that no tickets were found.
        """
        try:
            with self.session_factory() as session:
                ticket_status_grouped = session.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
            counts = {
                status: count
                for status, count in ticket_status_grouped
            }
            statuses = []
            data = []
            for status in TicketStatus:
                statuses.append(status.fa)
                data.append(counts.get(status, 0))
            if not data:
                self.create_empty_chart(f"{CHARTS_DIR}/ticket_status.png", "تیکتی یافت نشد")
                return

            fig, ax = plt.subplots(figsize=(16, 8), dpi=150)
            ax.bar(statuses, data)
            fig.savefig(f"{CHARTS_DIR}/ticket_status.png", transparent=True)
            plt.close(fig)
        except Exception as e:
            core_logger.error(f"Tickets Status Pie Chart failed: {e}")
            raise

    def tickets_category_bar_chart(self) -> None:
        """
        Generate and save a bar chart showing the distribution of ticket categories.

        This method queries the database for ticket categories and their counts, then
        generates a bar chart and saves it to the configured charts directory.
        If there is no category data, it falls back to creating an empty chart
        indicating that no tickets were found.
        """
        try:
            with self.session_factory() as session:
                ticket_category_grouped = session.query(Category.name, func.count(Ticket.id)).outerjoin(
                    Ticket, Ticket.category_id == Category.id).group_by(Category.id, Category.name).all()

            categories = [name for name, _ in ticket_category_grouped]
            data = [count for _, count in ticket_category_grouped]
            if not data:
                self.create_empty_chart(f"{CHARTS_DIR}/ticket_category.png", "تیکتی یافت نشد")
                return

            fig, ax = plt.subplots(figsize=(16, 8), dpi=150)
            ax.bar(categories, data)
            fig.savefig(f"{CHARTS_DIR}/ticket_category.png", transparent=True)
            plt.close(fig)
        except Exception as e:
            core_logger.error(f"Tickets Category Bar Chart failed: {e}")
            raise

    def tickets_department_bar_chart(self) -> None:
        """
        Generate and save a bar chart showing the distribution of ticket departments.

        This method queries the database for ticket departments and their counts, then
        generates a bar chart and saves it to the configured charts directory.
        If there is no department data, it falls back to creating an empty chart
        indicating that no tickets were found.
        """
        try:
            with self.session_factory() as session:
                ticket_department_grouped = session.query(Department.name, func.count(Ticket.id)).outerjoin(
                    Ticket, Ticket.department_id == Department.id).group_by(Department.id, Department.name).all()

            categories = [name for name, _ in ticket_department_grouped]
            data = [count for _, count in ticket_department_grouped]
            if not data:
                self.create_empty_chart(f"{CHARTS_DIR}/ticket_department.png", "تیکتی یافت نشد")
                return

            fig, ax = plt.subplots(figsize=(16, 8), dpi=150)
            ax.bar(categories, data)
            fig.savefig(f"{CHARTS_DIR}/ticket_department.png", transparent=True)
            plt.close(fig)
        except Exception as e:
            core_logger.error(f"Tickets Department Bar Chart failed: {e}")
            raise

    def it_experts_performance_bar_chart(self) -> None:
        """
        Generate and save a bar chart showing the distribution of it experts performances
        based on resolved tickets.

        This method queries the database for it experts performances and their counts, then
        generates a bar chart and saves it to the configured charts directory.
        If there is no tickets data, it falls back to creating an empty chart
        indicating that no tickets were found.
        """
        try:
            with self.session_factory() as session:
                it_expert_tickets_grouped = (
                    session.query(User.name, func.count(Ticket.id))
                    .outerjoin(
                        Ticket,
                        (Ticket.assigned_to == User.id) &
                        (Ticket.status == TicketStatus.RESOLVED),
                    )
                    .filter(User.role == Role.IT_EXPERT)
                    .group_by(User.id, User.name).all()
                )

            experts = []
            data = []
            for name, count in it_expert_tickets_grouped:
                experts.append(name)
                data.append(count or 0)

            if not data:
                self.create_empty_chart(
                    f"{CHARTS_DIR}/it_experts_performance.png",
                    "کارشناس یا تیکت یافت نشد",
                )
                return

            fig, ax = plt.subplots(figsize=(16, 8), dpi=150)
            ax.bar(experts, data)
            fig.savefig(f"{CHARTS_DIR}/it_experts_performance.png", transparent=True)
            plt.close(fig)
        except Exception as e:
            core_logger.error(f"It experts performance chart failed: {e}")
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

        plt.savefig(filename, transparent=True)
        plt.close(fig)

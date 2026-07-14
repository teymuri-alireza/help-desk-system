from src.database.engine import DatabaseEngine
from src.core.storage import StorageEngine
from src.core.services.admin_service import AdminService
from src.core.services.authentication_service import AuthenticationService
from src.core.services.ticket_service import TicketService
from src.core.services.response_sesrvice import ResponseService
from src.core.services.attachment_service import AttachmentService
from src.core.services.notification_service import NotificationService
from src.core.services.stats_service import StatsService
from src.ai.engine import AIEngine


class HelpDeskCore:
    """
    Core engine for the Help Desk system that manages authentication, tickets, 
    responses, and notifications through a unified API interface.
    """

    def __init__(self, database_path: str = "sqlite.db") -> None:
        """
        Initialize the HelpDeskCore with database and storage engines.

        Args:
            database_path (str): Path to the SQLite database file. Defaults to `sqlite.db`.
        """
        self.database_engine = DatabaseEngine(database_path)
        self.session_factory = self.database_engine.get_session_factory()

        self.ai_engine = AIEngine()

        self.storage = StorageEngine(self.session_factory)
        self.storage.initialize_default_departments_and_categories()

        self.admin_api = AdminService(storage=self.storage)
        self.authentication_api = AuthenticationService(storage=self.storage)
        self.ticket_api = TicketService(storage=self.storage)
        self.response_api = ResponseService(storage=self.storage)
        self.attachment_api = AttachmentService(storage=self.storage)
        self.notification_api = NotificationService(storage=self.storage)

        self.statistics_api = StatsService(session_factory=self.session_factory)

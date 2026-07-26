import logging
from src.core.services.response_sesrvice import ResponseService
from src.core.storage import StorageEngine
from src.database.tables import Ticket, User
from src.ai.classifier import AIClassifier
from src.ai.priority_predictor import AIPriorityPredictor
from src.ai.suggester import AISuggester

core_logger = logging.getLogger("core")


class TicketService:
    """
    Service for managing ticket operations.
    """

    def __init__(
            self,
            storage: StorageEngine,
            response_api: ResponseService,
            ai_classifier: AIClassifier,
            ai_suggester: AISuggester,
            ai_priority_predictor: AIPriorityPredictor
        ) -> None:
        """
        Initialize TicketService with a storage engine.

        Args:
            storage: The StorageEngine instance for database operations.
            response_api: The ResponseService instance for managing ticket responses.
            ai_classifier: The AIClassifier instance for auto-classifying tickets, using AI.
            ai_suggester: The AISuggester instance for suggesting responses to tickets, using AI.
            ai_priority_predictor: The AIPriorityPredictor instance for suggesting ticket priorities.
        """
        self.storage = storage
        self.response_api = response_api
        self.ai_classifier = ai_classifier
        self.ai_suggester = ai_suggester
        self.ai_priority_predictor = ai_priority_predictor

    def new_ticket(self, ticket: Ticket) -> None:
        """
        Create a new ticket.

        Args:
            ticket: The Ticket object to be created.
        """
        try:
            ticket.priority = self.ai_priority_predictor.predict(title=ticket.title, description=ticket.description)
            department_id, category_id = self.ai_classifier.classify(ticket=ticket.description)
            ticket.department_id = department_id
            ticket.category_id = category_id
            new_ticket = self.storage.insert_ticket(ticket)

            found_ticket = self.find_ticket(new_ticket.id)
            suggested_response = self.ai_suggester.suggest(ticket=found_ticket)

            if suggested_response is not None:
                self.response_api.new_response(suggested_response)

        except ValueError:
            raise

    def list_tickets(self, creator_id: int | None = None, assigned_to: int | None = None, limit: int | None= None) -> list[Ticket]:
        """
        List tickets filtered by creator ID, assignee ID, and with a specified limit.

        Args:
            creator_id: The creator ID to filter tickets by. If None, returns all tickets
            assigned_to: The assignee ID to filter tickets by. If None, returns all tickets
            limit: The maximum number of tickets to retrieve.

        Returns:
            list[Ticket]: A list of Ticket objects up to the specified limit.
        """
        return self.storage.list_tickets(creator_id=creator_id, assigned_to=assigned_to, limit=limit)

    def find_ticket(self, ticket_id: int) -> Ticket | None:
        """
        Find a ticket by their ID.

        Args:
            ticket_id: The ID of the ticket to find.

        Returns:
            Ticket | None: The Ticket object if found, otherwise None.
        """
        return self.storage.find_ticket(ticket_id)

    def update_ticket(self, new_ticket: Ticket, old_ticket_id: int) -> None:
        """
        Update an existing ticket. If the title or description has changed,
        the priority will be re-evaluated using the AI predictor.

        Args:
            new_ticket: The updated Ticket object with new data.
            old_ticket_id: The ID of the ticket to be updated.
        """
        old_ticket = self.find_ticket(ticket_id=old_ticket_id)
        if old_ticket is not None:
            content_changed = new_ticket.title != old_ticket.title or new_ticket.description != old_ticket.description
            if content_changed:
                new_ticket.priority = self.ai_priority_predictor.predict(
                    title=new_ticket.title,
                    description=new_ticket.description,
                )

        self.storage.update_ticket(new_ticket=new_ticket, old_ticket_id=old_ticket_id)

    def reopen_ticket(self, ticket_id: int) -> None:
        """
        Re-open a ticket after it has been resolved or closed.
        Also removes the ticket's satisfaction_rating field.

        Args:
            ticket_id: The ID of the ticket to re-open.
        """
        self.storage.reopen_ticket(ticket_id=ticket_id)

    def preview_auto_assign_ticket(self, department_id: int) -> User:
        """
        Preview which IT expert would be auto-assigned for a ticket in the specified department.

        Args:
            department_id: The ID of the department to find a free IT expert from.

        Returns:
            User: The User object of the free IT expert that would be assigned.

        Raises:
            AttributeError: If department_id is None.
            AttributeError: If no free IT expert is found for the specified department.
        """
        try:
            if department_id == None:
                raise AttributeError("Can not show preview for auto assign ticket. Department field is None.")

            free_it_expert = self.storage.find_free_it_expert(department_id=department_id)
            if free_it_expert is None:
                raise AttributeError("Can not show preview for auto assign ticket. No IT expert was found for this department.")
            return free_it_expert

        except AttributeError as e:
            e = str(e)
            core_logger.error(e)

            raise AttributeError(e)

    def auto_assign_ticket(self, ticket_id: int, department_id: int) -> None:
        """
        Automatically assign a ticket to a free IT expert in the specified department.

        Args:
            ticket_id: The ID of the ticket to assign.
            department_id: The ID of the department to find a free IT expert from.

        Raises:
            AttributeError: If department_id is None.
            AttributeError: If no free IT expert is found for the specified department.
        """
        try:
            if department_id == None:
                raise AttributeError("Can not auto assign ticket. Department field is None.")

            free_it_expert = self.storage.find_free_it_expert(department_id=department_id)
            self.storage.assign_ticket(ticket_id=ticket_id, assigned_to=free_it_expert.id)

        except AttributeError as e:
            e = str(e)
            if e == "Can not auto assign ticket. Department field is None.":
                err = "Can not auto assign ticket. Department field is None."
                core_logger.error(err)
            else:
                err = "Can not auto assign ticket. No IT expert was found for this department."
                core_logger.error(err)

            raise AttributeError(err)

    def remove_assignee(self, ticket_id: int) -> None:
        """
        Remove the assigned_to field from a ticket.

        Args:
            ticket_id: The ID of the ticket to update.
        """
        self.storage.remove_assignee(ticket_id=ticket_id)

    def rate_ticket(self, ticket_id: int, satisfaction_rating: int) -> None:
        """
        Rate a ticket after it has been resolved or closed.

        Args:
            ticket_id: The ID of the ticket to rate.
            satisfaction_rating: The satisfaction rating to assign
        """
        self.storage.rate_ticket(ticket_id=ticket_id, satisfaction_rating=satisfaction_rating)

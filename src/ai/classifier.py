import os

os.environ["HF_HUB_OFFLINE"] = "1" # Force the model to load offline

from logging import getLogger
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from src.database.tables import DepartmentSchema, CategorySchema

core_logger = getLogger("core")


class AIClassifier:
    """
    Classifies support tickets into departments and categories using semantic similarity.
    
    Utilizes sentence transformers to encode tickets and compares them against
    pre-encoded department and category embeddings to determine the best match.
    """

    def __init__(self):
        """
        Initialize the classifier by loading the multilingual model and encoding
        all departments and categories into embeddings.
        """
        self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

        self.departments = [d.value for d in DepartmentSchema]
        self.department_embeddings = self.model.encode(self.departments, convert_to_tensor=True)

        self.categories = [c.value for c in CategorySchema]
        self.category_embeddings = self.model.encode(self.categories, convert_to_tensor=True)

    def classify(self, ticket: str) -> tuple[int, int]:
        """
        Classify a ticket into a department and category.

        Args:
            ticket: The ticket description to classify.

        Returns:
            tuple[int,int]: A tuple of IDs (department_id, category_id).

        Raises:
            ValueError: If ticket is None or an empty string.
        """
        if ticket is None or ticket.strip() == "":
            core_logger.error("Can not classify the ticket, using AI operations. Ticket description is not provided")
            raise ValueError("Can not classify the ticket, using AI operations. Ticket description is not provided.")

        ticket_embedding = self.model.encode(ticket, convert_to_tensor=True)

        departments_scores = cos_sim(ticket_embedding, self.department_embeddings)
        categories_scores = cos_sim(ticket_embedding, self.category_embeddings)

        # Add '1' to the final score to match the list items to the database items.
        # The list items start at index '0', but the database items start at index '1'
        return departments_scores.argmax().item() + 1, categories_scores.argmax().item() + 1

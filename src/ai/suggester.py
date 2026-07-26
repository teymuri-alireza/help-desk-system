import os

os.environ["HF_HUB_OFFLINE"] = "1" # Force the model to load offline

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from src.database.tables import Ticket, Response
from src.ai.templates import responses_templates


class AISuggester:
    """
    AI-based suggester for generating responses to tickets based on their descriptions.
    """

    def __init__(self):
        """
        Initialize the AISuggester with a pre-trained sentence transformer model.
        """
        self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    def suggest(self, ticket: Ticket) -> Response | None:
        """
        Suggest a response for a given ticket based on its description.

        Args:
            ticket: The Ticket object for which to suggest a response.

        Returns:
            Response: A Response object containing the suggested response text, or None if no suitable response is found.
        """
        examples = [r.examples for r in responses_templates if r.department.fa == ticket.department.name]
        responses = [r.response for r in responses_templates if r.department.fa == ticket.department.name]

        if not examples:
            return None

        response_embeddings = self.model.encode(examples, convert_to_tensor=True)
        ticket_embedding = self.model.encode(ticket.description, convert_to_tensor=True)

        response_score = cos_sim(ticket_embedding, response_embeddings)
        # Creator ID is hardcoded to 1 for now, but it should be replaced with the actual creator ID in the future.
        return Response(ticket_id=ticket.id, text=responses[response_score.argmax().item()], creator_id=1)

from src.ai.classifier import AIClassifier
from src.ai.priority_predictor import AIPriorityPredictor
from src.ai.suggester import AISuggester


class AIEngine:
    """
    Engine for the AI operations.
    """

    def __init__(self) -> None:
        """
        Initialize the AIEngine.
        """
        self.ai_classifier = AIClassifier()
        self.ai_suggester = AISuggester()
        self.ai_priority_predictor = AIPriorityPredictor()

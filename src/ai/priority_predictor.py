import re
from dataclasses import dataclass

from src.database.tables import TicketPriority


@dataclass
class PriorityPrediction:
    """
    Represents the outcome of a priority prediction.

    Attributes:
        priority: The predicted ticket priority.
        confidence: A value between 0 and 1 indicating how confident
            the predictor is in the predicted priority.
        reasons: A list of human-readable explanations describing which
            rules contributed to the prediction.
    """

    priority: TicketPriority
    confidence: float
    reasons: list[str]


class AIPriorityPredictor:
    """
    Predicts ticket priority using explainable business rules.

    The predictor is intentionally deterministic and lightweight.
    Every prediction includes:
        - predicted priority
        - confidence
        - explanation
    """

    def __init__(self) -> None:
        """
        Initialize the keyword sets used to score ticket text.

        Each set groups Persian keywords/phrases by the signal they
        represent (critical severity, general warning, wide-impact
        scope, or security-related incidents). These sets are later
        used by `_score_keywords` to compute a weighted priority score.
        """

        self.critical_keywords: set[str] = {
            "سرور قطع است",
            "سیستم از کار افتاده",
            "سامانه",
            "قطعی",
            "قطع",
            "بحرانی",
            "فوری",
            "مسدود شده",
            "حادثه امنیتی",
            "نشت اطلاعات",
            "باج‌افزار",
            "بدافزار",
            "هک شده",
            "دسترسی ندارم",
            "نمی‌توانم وارد شوم",
            "سرویس در دسترس نیست",
            "محیط عملیاتی از کار افتاده",
            "پایگاه داده از کار افتاده",
        }

        self.warning_keywords: set[str] = {
            "کند",
            "وی‌پی‌ان",
            "مشکل",
            "اینترنت",
            "خطا",
            "باگ",
            "اتصال",
            "نمی‌توانم متصل شوم",
            "قادر به اتصال نیستم",
            "شبکه",
            "ورود",
            "دسترسی",
            "تایم اوت",
        }

        self.high_impact_keywords: set[str] = {
            "همه",
            "همه کاربران",
            "کل شرکت",
            "تمام شرکت",
            "تمام دفتر",
            "چند کاربر",
            "کاربران زیادی",
            "هیچ کس",
            "هیچکس",
            "هیچ کاربری",
            "بخش",
        }

        self.security_keywords: set[str] = {
            "امنیت",
            "نشت",
            "ویروس",
            "بدافزار",
            "هک شده",
            "باج‌افزار",
        }

    def predict(
        self,
        title: str | None = None,
        description: str | None = None,
    ) -> PriorityPrediction:
        """
        Predict the priority of a ticket based on its title and description.

        Args:
            title: The ticket's title, if available.
            description: The ticket's description, if available.

        Returns:
            A `PriorityPrediction` containing the predicted priority,
            a confidence score, and the list of reasons that contributed
            to the prediction. If no content is provided, a default
            `NORMAL` priority is returned with a neutral confidence.
        """

        text = self._normalize(title, description)

        if not text:
            return PriorityPrediction(
                priority=TicketPriority.NORMAL,
                confidence=0.50,
                reasons=["No ticket content provided"],
            )

        score = 0
        reasons: list[str] = []

        score += self._score_keywords(
            text=text,
            keywords=self.critical_keywords,
            weight=3,
            reasons=reasons,
            label="Critical keyword"
        )

        score += self._score_keywords(
            text=text,
            keywords=self.warning_keywords,
            weight=1,
            reasons=reasons,
            label="Warning keyword"
        )

        score += self._score_keywords(
            text=text,
            keywords=self.high_impact_keywords,
            weight=2,
            reasons=reasons,
            label="High-impact phrase"
        )

        score += self._score_keywords(
            text=text,
            keywords=self.security_keywords,
            weight=3,
            reasons=reasons,
            label="Security indicator"
        )

        # Priority thresholds

        if score >= 6:
            priority = TicketPriority.CRITICAL
            confidence = min(0.98, 0.60 + score * 0.04)

        elif score >= 3:
            priority = TicketPriority.WARNING
            confidence = min(0.95, 0.55 + score * 0.05)

        else:
            priority = TicketPriority.NORMAL
            confidence = 0.75

        return PriorityPrediction(
            priority=priority,
            confidence=round(confidence, 2),
            reasons=reasons,
        )

    def _normalize(self, *parts: str | None) -> str:
        """
        Normalize and merge the given text parts into a single string.

        Joins all non-empty parts with a space, converts the result to
        lowercase, and strips any characters that are not Latin letters,
        digits, Persian letters, the Persian zero-width non-joiner, or
        whitespace. Consecutive whitespace is then collapsed into a
        single space.

        Args:
            *parts: Any number of optional text fragments (e.g. title
                and description) to normalize and combine.

        Returns:
            The normalized, whitespace-collapsed text ready for keyword
            matching.
        """

        text = " ".join(
            part.strip()
            for part in parts
            if part and part.strip()
        )

        text = text.lower()

        text = re.sub(r"[^a-z0-9\u0600-\u06FF\u200c\s]+", " ", text)

        return re.sub(r"\s+", " ", text).strip()

    def _score_keywords(
        self,
        text: str,
        keywords: set[str],
        weight: int,
        reasons: list[str],
        label: str,
    ) -> int:
        """
        Score the given text against a set of keywords.

        For every keyword found within `text`, the running score is
        increased by `weight` and a human-readable explanation is
        appended to `reasons`.

        Args:
            text: The normalized ticket text to search within.
            keywords: The set of keywords/phrases to look for.
            weight: The score contribution added per matched keyword.
            reasons: The list of explanations to append matches to
                (mutated in place).
            label: A human-readable label describing the keyword
                category, used to build the explanation string.

        Returns:
            The total score contributed by matches found in this
            keyword set.
        """

        score = 0

        for keyword in keywords:
            if keyword in text:
                score += weight
                reasons.append(f"{label}: '{keyword}'")

        return score

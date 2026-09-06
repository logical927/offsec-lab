import logging
import unicodedata
from dataclasses import dataclass

from app.repositories import ChallengeRepository

logger = logging.getLogger(__name__)


class ChallengeNotFoundError(Exception):
    pass


class ChallengeNotAnswerableError(Exception):
    pass


@dataclass(frozen=True)
class ChallengeAnswerResult:
    correct: bool


def normalize_answer(answer: str) -> str:
    """Normalize presentation differences without changing answer meaning."""
    normalized = unicodedata.normalize("NFKC", answer)
    return " ".join(normalized.strip().casefold().split())


class ChallengeService:
    def __init__(self, repository: ChallengeRepository) -> None:
        self._repository = repository

    async def check_answer(
        self,
        challenge_id: int,
        submitted_answer: str,
    ) -> ChallengeAnswerResult:
        challenge = await self._repository.get_active(challenge_id)
        if challenge is None:
            raise ChallengeNotFoundError
        if not challenge.accepted_answers:
            raise ChallengeNotAnswerableError

        normalized_answer = normalize_answer(submitted_answer)
        correct = any(
            normalized_answer == normalize_answer(accepted_answer)
            for accepted_answer in challenge.accepted_answers
        )
        logger.info(
            "event=CHALLENGE_ANSWER challenge_id=%s result=%s",
            challenge_id,
            "correct" if correct else "incorrect",
        )
        return ChallengeAnswerResult(correct=correct)

import logging
import unicodedata
from dataclasses import dataclass

from app.repositories import ChallengeRepository
from app.services.progress_service import (
    ChallengeProgressStatus,
    MissionProgressStatus,
    ProgressService,
)

logger = logging.getLogger(__name__)


class ChallengeNotFoundError(Exception):
    pass


class ChallengeNotAnswerableError(Exception):
    pass


@dataclass(frozen=True)
class ChallengeAnswerResult:
    correct: bool
    status: ChallengeProgressStatus
    next_challenge_id: int | None
    mission_status: MissionProgressStatus


def normalize_answer(answer: str) -> str:
    """Normalize presentation differences without changing answer meaning."""
    normalized = unicodedata.normalize("NFKC", answer)
    return " ".join(normalized.strip().casefold().split())


class ChallengeService:
    def __init__(
        self,
        repository: ChallengeRepository,
        progress_service: ProgressService,
    ) -> None:
        self._repository = repository
        self._progress_service = progress_service

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

        await self._progress_service.assert_unlocked(challenge.mission, challenge)
        normalized_answer = normalize_answer(submitted_answer)
        correct = any(
            normalized_answer == normalize_answer(accepted_answer)
            for accepted_answer in challenge.accepted_answers
        )
        transition = await self._progress_service.record_answer(
            challenge.mission,
            challenge,
            correct,
        )
        logger.info(
            "event=CHALLENGE_ANSWER challenge_id=%s result=%s",
            challenge_id,
            "correct" if correct else "incorrect",
        )
        return ChallengeAnswerResult(
            correct=correct,
            status=transition.challenge_status,
            next_challenge_id=transition.next_challenge_id,
            mission_status=transition.mission_status,
        )

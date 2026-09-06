import asyncio
import logging
from unittest.mock import AsyncMock, Mock

import pytest

from app.models import Challenge, Mission
from app.services import (
    ChallengeLockedError,
    ChallengeNotAnswerableError,
    ChallengeNotFoundError,
    ChallengeService,
    ChallengeProgressStatus,
    MissionProgressStatus,
    ProgressTransition,
)
from app.services.challenge_service import normalize_answer


def challenge(*, accepted_answers: list[str] | None) -> Challenge:
    mission = Mission(id=1, slug="m01", title="Recon", sort_order=1)
    return Challenge(
        id=1,
        mission_id=1,
        slug="http-port",
        title="HTTP Port",
        sort_order=1,
        is_active=True,
        accepted_answers=accepted_answers,
        mission=mission,
    )


def progress_service() -> Mock:
    service = Mock()
    service.assert_unlocked = AsyncMock()
    service.record_answer = AsyncMock(
        return_value=ProgressTransition(
            challenge_status=ChallengeProgressStatus.COMPLETED,
            next_challenge_id=2,
            mission_status=MissionProgressStatus.IN_PROGRESS,
        )
    )
    return service


@pytest.mark.parametrize(
    ("submitted", "expected"),
    [
        (" 80 ", "80"),
        ("NGINX", "nginx"),
        ("Open   SSH", "open ssh"),
        ("８０", "80"),
    ],
)
def test_normalize_answer_handles_presentation_differences(
    submitted: str,
    expected: str,
) -> None:
    assert normalize_answer(submitted) == expected


@pytest.mark.parametrize("submitted", ["80", " 80/TCP ", "８０"])
def test_check_answer_accepts_challenge_specific_values(submitted: str) -> None:
    repository = Mock()
    repository.get_active = AsyncMock(
        return_value=challenge(accepted_answers=["80", "80/tcp"])
    )
    progress = progress_service()
    service = ChallengeService(repository, progress)

    result = asyncio.run(service.check_answer(1, submitted))

    assert result.correct is True
    progress.assert_unlocked.assert_awaited_once()
    progress.record_answer.assert_awaited_once()


def test_check_answer_returns_false_for_incorrect_answer() -> None:
    repository = Mock()
    repository.get_active = AsyncMock(
        return_value=challenge(accepted_answers=["80", "80/tcp"])
    )
    progress = progress_service()
    progress.record_answer.return_value = ProgressTransition(
        challenge_status=ChallengeProgressStatus.AVAILABLE,
        next_challenge_id=None,
        mission_status=MissionProgressStatus.NOT_STARTED,
    )
    service = ChallengeService(repository, progress)

    result = asyncio.run(service.check_answer(1, "443"))

    assert result.correct is False
    assert result.status == ChallengeProgressStatus.AVAILABLE


def test_unknown_challenge_is_not_disclosed() -> None:
    repository = Mock()
    repository.get_active = AsyncMock(return_value=None)
    progress = progress_service()
    service = ChallengeService(repository, progress)

    with pytest.raises(ChallengeNotFoundError):
        asyncio.run(service.check_answer(999, "anything"))
    progress.assert_unlocked.assert_not_awaited()


def test_non_answerable_challenge_returns_domain_error() -> None:
    repository = Mock()
    repository.get_active = AsyncMock(
        return_value=challenge(accepted_answers=None)
    )
    progress = progress_service()
    service = ChallengeService(repository, progress)

    with pytest.raises(ChallengeNotAnswerableError):
        asyncio.run(service.check_answer(1, "anything"))
    progress.assert_unlocked.assert_not_awaited()


def test_answer_value_is_not_written_to_logs(caplog: pytest.LogCaptureFixture) -> None:
    repository = Mock()
    repository.get_active = AsyncMock(
        return_value=challenge(accepted_answers=["expected-answer"])
    )
    service = ChallengeService(repository, progress_service())

    with caplog.at_level(logging.INFO):
        asyncio.run(service.check_answer(1, "submitted-secret-value"))

    assert "submitted-secret-value" not in caplog.text
    assert "expected-answer" not in caplog.text
    assert "event=CHALLENGE_ANSWER" in caplog.text


def test_locked_challenge_stops_before_answer_evaluation() -> None:
    repository = Mock()
    repository.get_active = AsyncMock(
        return_value=challenge(accepted_answers=["expected-answer"])
    )
    progress = progress_service()
    progress.assert_unlocked.side_effect = ChallengeLockedError
    service = ChallengeService(repository, progress)

    with pytest.raises(ChallengeLockedError):
        asyncio.run(service.check_answer(1, "expected-answer"))

    progress.record_answer.assert_not_awaited()

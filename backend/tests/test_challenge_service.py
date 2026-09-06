import asyncio
import logging
from unittest.mock import AsyncMock, Mock

import pytest

from app.models import Challenge
from app.services import (
    ChallengeNotAnswerableError,
    ChallengeNotFoundError,
    ChallengeService,
)
from app.services.challenge_service import normalize_answer


def challenge(*, accepted_answers: list[str] | None) -> Challenge:
    return Challenge(
        id=1,
        mission_id=1,
        slug="http-port",
        title="HTTP Port",
        sort_order=1,
        is_active=True,
        accepted_answers=accepted_answers,
    )


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
    service = ChallengeService(repository)

    result = asyncio.run(service.check_answer(1, submitted))

    assert result.correct is True


def test_check_answer_returns_false_for_incorrect_answer() -> None:
    repository = Mock()
    repository.get_active = AsyncMock(
        return_value=challenge(accepted_answers=["80", "80/tcp"])
    )
    service = ChallengeService(repository)

    result = asyncio.run(service.check_answer(1, "443"))

    assert result.correct is False


def test_unknown_challenge_is_not_disclosed() -> None:
    repository = Mock()
    repository.get_active = AsyncMock(return_value=None)
    service = ChallengeService(repository)

    with pytest.raises(ChallengeNotFoundError):
        asyncio.run(service.check_answer(999, "anything"))


def test_non_answerable_challenge_returns_domain_error() -> None:
    repository = Mock()
    repository.get_active = AsyncMock(
        return_value=challenge(accepted_answers=None)
    )
    service = ChallengeService(repository)

    with pytest.raises(ChallengeNotAnswerableError):
        asyncio.run(service.check_answer(1, "anything"))


def test_answer_value_is_not_written_to_logs(caplog: pytest.LogCaptureFixture) -> None:
    repository = Mock()
    repository.get_active = AsyncMock(
        return_value=challenge(accepted_answers=["expected-answer"])
    )
    service = ChallengeService(repository)

    with caplog.at_level(logging.INFO):
        asyncio.run(service.check_answer(1, "submitted-secret-value"))

    assert "submitted-secret-value" not in caplog.text
    assert "expected-answer" not in caplog.text
    assert "event=CHALLENGE_ANSWER" in caplog.text

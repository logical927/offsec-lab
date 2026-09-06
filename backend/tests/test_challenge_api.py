import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_challenge_service
from app.main import app
from app.services import (
    ChallengeAnswerResult,
    ChallengeNotAnswerableError,
    ChallengeNotFoundError,
)

client = TestClient(app)


class FakeChallengeService:
    async def check_answer(
        self,
        challenge_id: int,
        submitted_answer: str,
    ) -> ChallengeAnswerResult:
        if challenge_id == 404:
            raise ChallengeNotFoundError
        if challenge_id == 409:
            raise ChallengeNotAnswerableError
        return ChallengeAnswerResult(correct=submitted_answer.casefold() == "correct")


def override_challenge_service() -> FakeChallengeService:
    return FakeChallengeService()


def post_answer(challenge_id: int | str, answer: str):
    app.dependency_overrides[get_challenge_service] = override_challenge_service
    try:
        return client.post(
            f"/api/v1/challenges/{challenge_id}/answers",
            json={"answer": answer},
        )
    finally:
        app.dependency_overrides.clear()


def test_correct_answer_returns_true_without_internal_values() -> None:
    response = post_answer(1, "correct")

    assert response.status_code == 200
    assert response.json() == {"correct": True}
    assert "accepted_answers" not in response.text


def test_incorrect_answer_returns_false() -> None:
    response = post_answer(1, "incorrect")

    assert response.status_code == 200
    assert response.json() == {"correct": False}


def test_unknown_challenge_returns_structured_not_found_error() -> None:
    response = post_answer(404, "anything")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "CHALLENGE_NOT_FOUND",
            "message": "Challenge not found.",
        }
    }


def test_non_answerable_challenge_returns_structured_conflict() -> None:
    response = post_answer(409, "anything")

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "CHALLENGE_NOT_ANSWERABLE",
            "message": "Challenge does not accept answers.",
        }
    }


@pytest.mark.parametrize(
    "challenge_id",
    [0, -1, "not-an-integer"],
)
def test_invalid_challenge_id_returns_validation_error(
    challenge_id: int | str,
) -> None:
    response = post_answer(challenge_id, "anything")

    assert response.status_code == 422


@pytest.mark.parametrize("answer", ["", "   ", "x" * 201])
def test_invalid_answer_returns_validation_error(answer: str) -> None:
    response = post_answer(1, answer)

    assert response.status_code == 422

from fastapi.testclient import TestClient

from app.api.dependencies import get_progress_service
from app.main import app
from app.services import (
    ChallengeProgressSnapshot,
    ChallengeProgressStatus,
    MissionProgressSnapshot,
    MissionProgressStatus,
)

client = TestClient(app)


class FakeProgressService:
    async def list_progress(self) -> list[MissionProgressSnapshot]:
        return [
            MissionProgressSnapshot(
                mission_id=1,
                status=MissionProgressStatus.IN_PROGRESS,
                challenges=[
                    ChallengeProgressSnapshot(
                        challenge_id=1,
                        status=ChallengeProgressStatus.COMPLETED,
                    ),
                    ChallengeProgressSnapshot(
                        challenge_id=2,
                        status=ChallengeProgressStatus.AVAILABLE,
                    ),
                    ChallengeProgressSnapshot(
                        challenge_id=3,
                        status=ChallengeProgressStatus.LOCKED,
                    ),
                ],
            )
        ]


def override_progress_service() -> FakeProgressService:
    return FakeProgressService()


def test_get_progress_returns_mission_and_challenge_states() -> None:
    app.dependency_overrides[get_progress_service] = override_progress_service
    try:
        response = client.get("/api/v1/progress")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "missions": [
            {
                "mission_id": 1,
                "status": "IN_PROGRESS",
                "challenges": [
                    {"challenge_id": 1, "status": "COMPLETED"},
                    {"challenge_id": 2, "status": "AVAILABLE"},
                    {"challenge_id": 3, "status": "LOCKED"},
                ],
            }
        ]
    }

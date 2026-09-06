from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.dependencies import get_mission_service
from app.main import app
from app.models import Challenge, Mission
from app.services import MissionDetail, MissionNotFoundError

client = TestClient(app)


def mission(*, mission_id: int = 1) -> Mission:
    timestamp = datetime(2026, 9, 6, tzinfo=UTC)
    return Mission(
        id=mission_id,
        slug=f"m{mission_id:02d}-recon",
        title="Reconnaissance",
        description="Map the target attack surface.",
        sort_order=mission_id,
        is_active=True,
        created_at=timestamp,
        updated_at=timestamp,
    )


def challenge(*, challenge_id: int = 1, mission_id: int = 1) -> Challenge:
    timestamp = datetime(2026, 9, 6, tzinfo=UTC)
    return Challenge(
        id=challenge_id,
        mission_id=mission_id,
        slug=f"challenge-{challenge_id}",
        title="Host Discovery",
        description="Confirm that the target is reachable.",
        accepted_answers=["internal-answer"],
        sort_order=challenge_id,
        is_active=True,
        created_at=timestamp,
        updated_at=timestamp,
    )


class FakeMissionService:
    async def list_missions(self) -> list[Mission]:
        return [mission()]

    async def get_mission(self, mission_id: int) -> MissionDetail:
        if mission_id != 1:
            raise MissionNotFoundError
        return MissionDetail(
            mission=mission(mission_id=mission_id),
            challenges=[challenge(mission_id=mission_id)],
        )


def override_mission_service() -> FakeMissionService:
    return FakeMissionService()


def test_list_missions_returns_public_fields() -> None:
    app.dependency_overrides[get_mission_service] = override_mission_service
    try:
        response = client.get("/api/v1/missions")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "slug": "m01-recon",
            "title": "Reconnaissance",
            "description": "Map the target attack surface.",
            "sort_order": 1,
        }
    ]


def test_get_mission_returns_ordered_challenge_fields() -> None:
    app.dependency_overrides[get_mission_service] = override_mission_service
    try:
        response = client.get("/api/v1/missions/1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "slug": "m01-recon",
        "title": "Reconnaissance",
        "description": "Map the target attack surface.",
        "sort_order": 1,
        "challenges": [
            {
                "id": 1,
                "slug": "challenge-1",
                "title": "Host Discovery",
                "description": "Confirm that the target is reachable.",
                "sort_order": 1,
            }
        ],
    }
    assert "answer" not in response.text


def test_get_unknown_mission_returns_structured_not_found_error() -> None:
    app.dependency_overrides[get_mission_service] = override_mission_service
    try:
        response = client.get("/api/v1/missions/999")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "MISSION_NOT_FOUND",
            "message": "Mission not found.",
        }
    }


def test_non_integer_mission_id_returns_validation_error() -> None:
    app.dependency_overrides[get_mission_service] = override_mission_service
    try:
        response = client.get("/api/v1/missions/not-an-integer")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


def test_non_positive_mission_id_returns_validation_error() -> None:
    app.dependency_overrides[get_mission_service] = override_mission_service
    try:
        response = client.get("/api/v1/missions/0")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422

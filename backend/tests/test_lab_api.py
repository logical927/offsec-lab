from fastapi.testclient import TestClient

from app.api.dependencies import get_lab_service
from app.lab import DockerCommandError, LabDefinition
from app.main import app
from app.services import LabService

client = TestClient(app)


class FakeLabRunner:
    def __init__(
        self,
        *,
        already_running: bool = False,
        fails: bool = False,
    ) -> None:
        self.already_running = already_running
        self.fails = fails

    async def start(self, _definition: LabDefinition) -> bool:
        if self.fails:
            raise DockerCommandError("sensitive internal detail")
        return self.already_running


def request_start(runner: FakeLabRunner, mission_id: int = 1):
    app.dependency_overrides[get_lab_service] = lambda: LabService(runner)
    try:
        return client.post(f"/api/v1/labs/{mission_id}/start")
    finally:
        app.dependency_overrides.clear()


def test_start_lab_returns_running() -> None:
    response = request_start(FakeLabRunner())

    assert response.status_code == 200
    assert response.json() == {
        "mission_id": 1,
        "status": "running",
        "already_running": False,
    }


def test_start_lab_returns_already_running() -> None:
    response = request_start(FakeLabRunner(already_running=True))

    assert response.status_code == 200
    assert response.json()["already_running"] is True


def test_start_unknown_lab_returns_structured_not_found() -> None:
    response = request_start(FakeLabRunner(), mission_id=999)

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "LAB_NOT_FOUND",
            "message": "Lab not found.",
        }
    }


def test_start_failure_does_not_expose_internal_details() -> None:
    response = request_start(FakeLabRunner(fails=True))

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "LAB_START_FAILED",
            "message": "Failed to start the lab.",
        }
    }
    assert "sensitive internal detail" not in response.text

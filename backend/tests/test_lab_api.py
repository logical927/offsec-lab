import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_lab_service
from app.lab import (
    DockerCommandError,
    LabDefinition,
    LabRuntimeStatus,
    LabState,
)
from app.main import app
from app.services import LabService

client = TestClient(app)


class FakeLabRunner:
    def __init__(
        self,
        *,
        already_running: bool = False,
        already_stopped: bool = False,
        fails: bool = False,
        runtime_status: LabRuntimeStatus | None = None,
    ) -> None:
        self.already_running = already_running
        self.already_stopped = already_stopped
        self.fails = fails
        self.runtime_status = runtime_status or LabRuntimeStatus(LabState.STOPPED)

    async def start(self, _definition: LabDefinition) -> bool:
        if self.fails:
            raise DockerCommandError("sensitive internal detail")
        return self.already_running

    async def stop(self, _definition: LabDefinition) -> bool:
        if self.fails:
            raise DockerCommandError("sensitive internal detail")
        return self.already_stopped

    async def reset(self, _definition: LabDefinition) -> None:
        if self.fails:
            raise DockerCommandError("sensitive internal detail")

    async def status(self, _definition: LabDefinition) -> LabRuntimeStatus:
        if self.fails:
            raise DockerCommandError("sensitive internal detail")
        return self.runtime_status


def request_start(runner: FakeLabRunner, mission_id: int = 1):
    app.dependency_overrides[get_lab_service] = lambda: LabService(runner)
    try:
        return client.post(f"/api/v1/labs/{mission_id}/start")
    finally:
        app.dependency_overrides.clear()


def request_operation(
    operation: str,
    runner: FakeLabRunner,
    mission_id: int = 1,
):
    app.dependency_overrides[get_lab_service] = lambda: LabService(runner)
    try:
        return client.post(f"/api/v1/labs/{mission_id}/{operation}")
    finally:
        app.dependency_overrides.clear()


def request_status(runner: FakeLabRunner, mission_id: int = 1):
    app.dependency_overrides[get_lab_service] = lambda: LabService(runner)
    try:
        return client.get(f"/api/v1/labs/{mission_id}/status")
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


def test_stop_lab_returns_stopped() -> None:
    response = request_operation("stop", FakeLabRunner())

    assert response.status_code == 200
    assert response.json() == {
        "mission_id": 1,
        "status": "stopped",
        "already_stopped": False,
    }


def test_repeated_stop_reports_already_stopped() -> None:
    response = request_operation("stop", FakeLabRunner(already_stopped=True))

    assert response.status_code == 200
    assert response.json()["already_stopped"] is True


def test_reset_lab_returns_running() -> None:
    response = request_operation("reset", FakeLabRunner())

    assert response.status_code == 200
    assert response.json() == {"mission_id": 1, "status": "running"}


@pytest.mark.parametrize(
    "lab_state",
    [
        LabState.STOPPED,
        LabState.STARTING,
        LabState.STOPPING,
        LabState.ERROR,
    ],
)
def test_status_returns_non_running_state_without_target(
    lab_state: LabState,
) -> None:
    response = request_status(FakeLabRunner(runtime_status=LabRuntimeStatus(lab_state)))

    assert response.status_code == 200
    assert response.json() == {
        "mission_id": 1,
        "status": lab_state.value,
        "target": None,
    }


def test_status_returns_running_target_details() -> None:
    response = request_status(
        FakeLabRunner(
            runtime_status=LabRuntimeStatus(
                LabState.RUNNING,
                target_ip="172.20.0.3",
            )
        )
    )

    assert response.status_code == 200
    assert response.json() == {
        "mission_id": 1,
        "status": "RUNNING",
        "target": {"hostname": "target-m01", "ip": "172.20.0.3"},
    }


def test_status_unknown_lab_returns_structured_not_found() -> None:
    response = request_status(FakeLabRunner(), mission_id=999)

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "LAB_NOT_FOUND", "message": "Lab not found."}
    }


def test_status_docker_failure_returns_error_without_internal_details() -> None:
    response = request_status(FakeLabRunner(fails=True))

    assert response.status_code == 200
    assert response.json() == {
        "mission_id": 1,
        "status": "ERROR",
        "target": None,
    }
    assert "sensitive internal detail" not in response.text


@pytest.mark.parametrize("operation", ["stop", "reset"])
def test_unknown_stop_or_reset_returns_structured_not_found(operation: str) -> None:
    response = request_operation(operation, FakeLabRunner(), mission_id=999)

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "LAB_NOT_FOUND",
            "message": "Lab not found.",
        }
    }


@pytest.mark.parametrize(
    ("operation", "code", "message"),
    [
        ("stop", "LAB_STOP_FAILED", "Failed to stop the lab."),
        ("reset", "LAB_RESET_FAILED", "Failed to reset the lab."),
    ],
)
def test_stop_or_reset_failure_is_sanitized(
    operation: str,
    code: str,
    message: str,
) -> None:
    response = request_operation(operation, FakeLabRunner(fails=True))

    assert response.status_code == 503
    assert response.json() == {"error": {"code": code, "message": message}}
    assert "sensitive internal detail" not in response.text

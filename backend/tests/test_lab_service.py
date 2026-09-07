import asyncio

import pytest

from app.lab import DockerCommandError, LabDefinition
from app.services import (
    LabNotFoundError,
    LabResetFailedError,
    LabService,
    LabStartFailedError,
    LabStopFailedError,
)


class FakeLabRunner:
    def __init__(
        self,
        *,
        already_running: bool = False,
        already_stopped: bool = False,
        error: Exception | None = None,
    ) -> None:
        self.already_running = already_running
        self.already_stopped = already_stopped
        self.error = error
        self.definition: LabDefinition | None = None
        self.operation: str | None = None

    async def start(self, definition: LabDefinition) -> bool:
        self.definition = definition
        self.operation = "start"
        if self.error:
            raise self.error
        return self.already_running

    async def stop(self, definition: LabDefinition) -> bool:
        self.definition = definition
        self.operation = "stop"
        if self.error:
            raise self.error
        return self.already_stopped

    async def reset(self, definition: LabDefinition) -> None:
        self.definition = definition
        self.operation = "reset"
        if self.error:
            raise self.error


def test_start_lab_uses_predefined_mission_one_definition() -> None:
    runner = FakeLabRunner()
    service = LabService(runner)

    result = asyncio.run(service.start_lab(1))

    assert result.status == "running"
    assert result.already_running is False
    assert runner.definition is not None
    assert runner.definition.compose_file.as_posix().endswith(
        "challenges/m01-recon/compose.lab.yml"
    )
    assert runner.definition.project_name == "offsec-m01"


def test_start_lab_reports_already_running() -> None:
    service = LabService(FakeLabRunner(already_running=True))

    result = asyncio.run(service.start_lab(1))

    assert result.status == "running"
    assert result.already_running is True


def test_start_lab_rejects_unknown_mission_without_calling_runner() -> None:
    runner = FakeLabRunner()
    service = LabService(runner)

    with pytest.raises(LabNotFoundError):
        asyncio.run(service.start_lab(999))

    assert runner.definition is None


def test_start_lab_translates_docker_failure() -> None:
    service = LabService(FakeLabRunner(error=DockerCommandError()))

    with pytest.raises(LabStartFailedError):
        asyncio.run(service.start_lab(1))


def test_stop_lab_resolves_mission_and_delegates() -> None:
    runner = FakeLabRunner()
    result = asyncio.run(LabService(runner).stop_lab(1))

    assert result.status == "stopped"
    assert result.already_stopped is False
    assert runner.operation == "stop"
    assert runner.definition is not None
    assert runner.definition.project_name == "offsec-m01"


def test_stop_lab_reports_already_stopped() -> None:
    result = asyncio.run(
        LabService(FakeLabRunner(already_stopped=True)).stop_lab(1)
    )

    assert result.already_stopped is True


def test_stop_lab_rejects_unknown_mission_without_calling_runner() -> None:
    runner = FakeLabRunner()

    with pytest.raises(LabNotFoundError):
        asyncio.run(LabService(runner).stop_lab(999))

    assert runner.operation is None


def test_stop_lab_translates_docker_failure() -> None:
    service = LabService(FakeLabRunner(error=DockerCommandError()))

    with pytest.raises(LabStopFailedError):
        asyncio.run(service.stop_lab(1))


def test_reset_lab_resolves_mission_and_delegates() -> None:
    runner = FakeLabRunner()
    result = asyncio.run(LabService(runner).reset_lab(1))

    assert result.status == "running"
    assert runner.operation == "reset"
    assert runner.definition is not None
    assert runner.definition.compose_file.as_posix().endswith(
        "challenges/m01-recon/compose.lab.yml"
    )


def test_reset_lab_rejects_unknown_mission_without_calling_runner() -> None:
    runner = FakeLabRunner()

    with pytest.raises(LabNotFoundError):
        asyncio.run(LabService(runner).reset_lab(999))

    assert runner.operation is None


def test_reset_lab_translates_docker_failure() -> None:
    service = LabService(FakeLabRunner(error=DockerCommandError()))

    with pytest.raises(LabResetFailedError):
        asyncio.run(service.reset_lab(1))

import asyncio

import pytest

from app.lab import DockerCommandError, LabDefinition
from app.services import (
    LabNotFoundError,
    LabService,
    LabStartFailedError,
)


class FakeLabRunner:
    def __init__(
        self,
        *,
        already_running: bool = False,
        error: Exception | None = None,
    ) -> None:
        self.already_running = already_running
        self.error = error
        self.definition: LabDefinition | None = None

    async def start(self, definition: LabDefinition) -> bool:
        self.definition = definition
        if self.error:
            raise self.error
        return self.already_running


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

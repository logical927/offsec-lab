import logging
from dataclasses import dataclass

from app.lab import DockerCommandError, LabRunner, get_lab_definition

logger = logging.getLogger(__name__)


class LabNotFoundError(Exception):
    pass


class LabStartFailedError(Exception):
    pass


@dataclass(frozen=True)
class LabStartResult:
    mission_id: int
    status: str
    already_running: bool


class LabService:
    def __init__(self, runner: LabRunner) -> None:
        self._runner = runner

    async def start_lab(self, mission_id: int) -> LabStartResult:
        definition = get_lab_definition(mission_id)
        if definition is None:
            raise LabNotFoundError

        logger.info("LAB_START mission_id=%s", mission_id)
        try:
            already_running = await self._runner.start(definition)
        except DockerCommandError as exc:
            logger.exception("LAB_ERROR mission_id=%s", mission_id)
            raise LabStartFailedError from exc

        return LabStartResult(
            mission_id=mission_id,
            status="running",
            already_running=already_running,
        )

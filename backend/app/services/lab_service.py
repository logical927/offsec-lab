import logging
from dataclasses import dataclass

from app.lab import DockerCommandError, LabRunner, LabState, get_lab_definition

logger = logging.getLogger(__name__)


class LabNotFoundError(Exception):
    pass


class LabStartFailedError(Exception):
    pass


class LabStopFailedError(Exception):
    pass


class LabResetFailedError(Exception):
    pass


@dataclass(frozen=True)
class LabStartResult:
    mission_id: int
    status: str
    already_running: bool


@dataclass(frozen=True)
class LabStopResult:
    mission_id: int
    status: str
    already_stopped: bool


@dataclass(frozen=True)
class LabResetResult:
    mission_id: int
    status: str


@dataclass(frozen=True)
class LabStatusResult:
    mission_id: int
    status: LabState
    target_hostname: str | None = None
    target_ip: str | None = None


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

    async def stop_lab(self, mission_id: int) -> LabStopResult:
        definition = get_lab_definition(mission_id)
        if definition is None:
            raise LabNotFoundError

        logger.info("LAB_STOP mission_id=%s", mission_id)
        try:
            already_stopped = await self._runner.stop(definition)
        except DockerCommandError as exc:
            logger.exception("LAB_ERROR operation=stop mission_id=%s", mission_id)
            raise LabStopFailedError from exc

        return LabStopResult(
            mission_id=mission_id,
            status="stopped",
            already_stopped=already_stopped,
        )

    async def reset_lab(self, mission_id: int) -> LabResetResult:
        definition = get_lab_definition(mission_id)
        if definition is None:
            raise LabNotFoundError

        logger.info("LAB_RESET mission_id=%s", mission_id)
        try:
            await self._runner.reset(definition)
        except DockerCommandError as exc:
            logger.exception("LAB_ERROR operation=reset mission_id=%s", mission_id)
            raise LabResetFailedError from exc

        return LabResetResult(mission_id=mission_id, status="running")

    async def get_status(self, mission_id: int) -> LabStatusResult:
        definition = get_lab_definition(mission_id)
        if definition is None:
            raise LabNotFoundError

        try:
            runtime_status = await self._runner.status(definition)
        except DockerCommandError:
            logger.exception("LAB_ERROR operation=status mission_id=%s", mission_id)
            return LabStatusResult(mission_id=mission_id, status=LabState.ERROR)

        target_hostname = None
        if runtime_status.state is LabState.RUNNING:
            target_hostname = definition.target_container

        return LabStatusResult(
            mission_id=mission_id,
            status=runtime_status.state,
            target_hostname=target_hostname,
            target_ip=runtime_status.target_ip,
        )

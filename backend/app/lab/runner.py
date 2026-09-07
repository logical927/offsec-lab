import asyncio
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol, Sequence

from app.lab.registry import LabDefinition


class DockerCommandError(Exception):
    """Raised when a predefined Docker operation cannot be completed."""


class LabState(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class LabRuntimeStatus:
    state: LabState
    target_ip: str | None = None


class CommandExecutor(Protocol):
    async def run(self, arguments: Sequence[str], timeout: float) -> CommandResult: ...


class AsyncSubprocessExecutor:
    async def run(self, arguments: Sequence[str], timeout: float) -> CommandResult:
        try:
            process = await asyncio.create_subprocess_exec(
                *arguments,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as exc:
            raise DockerCommandError("Docker CLI could not be started") from exc

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
        except TimeoutError as exc:
            process.kill()
            await process.communicate()
            raise DockerCommandError("Docker operation timed out") from exc

        result = CommandResult(
            returncode=process.returncode or 0,
            stdout=stdout_bytes.decode(errors="replace"),
            stderr=stderr_bytes.decode(errors="replace"),
        )
        if result.returncode != 0:
            raise DockerCommandError("Docker operation failed")
        return result


class LabRunner(Protocol):
    async def start(self, definition: LabDefinition) -> bool:
        """Start the lab and return whether it was already running."""

    async def stop(self, definition: LabDefinition) -> bool:
        """Stop the lab and return whether it was already stopped."""

    async def reset(self, definition: LabDefinition) -> None:
        """Destroy and recreate the lab in a running state."""

    async def status(self, definition: LabDefinition) -> LabRuntimeStatus:
        """Return the current state of the lab and its target IP when running."""


class DockerComposeLabRunner:
    def __init__(
        self,
        executor: CommandExecutor | None = None,
        *,
        timeout_seconds: float = 120,
    ) -> None:
        self._executor = executor or AsyncSubprocessExecutor()
        self._timeout_seconds = timeout_seconds
        self._lock = asyncio.Lock()
        self._states: dict[int, LabState] = {}
        self._operation_states: dict[int, LabState] = {}

    async def start(self, definition: LabDefinition) -> bool:
        async with self._lock:
            self._operation_states[definition.mission_id] = LabState.STARTING
            try:
                if await self._is_running(definition):
                    self._states[definition.mission_id] = LabState.RUNNING
                    return True

                await self._run_compose(
                    definition,
                    "up",
                    "-d",
                    "--wait",
                    "--wait-timeout",
                    str(max(1, int(self._timeout_seconds) - 10)),
                )
            except DockerCommandError:
                self._states[definition.mission_id] = LabState.ERROR
                raise
            finally:
                self._operation_states.pop(definition.mission_id, None)

            self._states[definition.mission_id] = LabState.RUNNING
            return False

    async def stop(self, definition: LabDefinition) -> bool:
        async with self._lock:
            self._operation_states[definition.mission_id] = LabState.STOPPING
            try:
                if not await self._has_running_services(definition):
                    self._states[definition.mission_id] = LabState.STOPPED
                    return True

                await self._run_compose(definition, "stop")
            except DockerCommandError:
                self._states[definition.mission_id] = LabState.ERROR
                raise
            finally:
                self._operation_states.pop(definition.mission_id, None)

            self._states[definition.mission_id] = LabState.STOPPED
            return False

    async def reset(self, definition: LabDefinition) -> None:
        async with self._lock:
            self._operation_states[definition.mission_id] = LabState.STARTING
            try:
                await self._run_compose(definition, "down", "--volumes")
                await self._run_compose(
                    definition,
                    "up",
                    "-d",
                    "--force-recreate",
                    "--wait",
                    "--wait-timeout",
                    str(max(1, int(self._timeout_seconds) - 10)),
                )
            except DockerCommandError:
                self._states[definition.mission_id] = LabState.ERROR
                raise
            finally:
                self._operation_states.pop(definition.mission_id, None)

            self._states[definition.mission_id] = LabState.RUNNING

    async def status(self, definition: LabDefinition) -> LabRuntimeStatus:
        operation_state = self._operation_states.get(definition.mission_id)
        if operation_state is not None:
            return LabRuntimeStatus(state=operation_state)

        try:
            status = await self._docker_status(definition)
        except DockerCommandError:
            self._states[definition.mission_id] = LabState.ERROR
            raise

        operation_state = self._operation_states.get(definition.mission_id)
        if operation_state is not None:
            return LabRuntimeStatus(state=operation_state)

        self._states[definition.mission_id] = status.state
        return status

    async def _docker_status(self, definition: LabDefinition) -> LabRuntimeStatus:
        running_services = await self._running_services(definition)
        if not running_services:
            return LabRuntimeStatus(state=LabState.STOPPED)
        if not definition.services.issubset(running_services):
            return LabRuntimeStatus(state=LabState.ERROR)

        target_health = await self._executor.run(
            (
                "docker",
                "inspect",
                "--format",
                "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",
                definition.target_container,
            ),
            self._timeout_seconds,
        )
        health = target_health.stdout.strip()
        if health == "starting":
            return LabRuntimeStatus(state=LabState.STARTING)
        if health != "healthy":
            return LabRuntimeStatus(state=LabState.ERROR)

        await self._executor.run(
            ("docker", "network", "inspect", definition.network_name),
            self._timeout_seconds,
        )
        target_ip = await self._executor.run(
            (
                "docker",
                "inspect",
                "--format",
                (
                    "{{with index .NetworkSettings.Networks \""
                    f"{definition.network_name}"
                    "\"}}{{.IPAddress}}{{end}}"
                ),
                definition.target_container,
            ),
            self._timeout_seconds,
        )
        ip_address = target_ip.stdout.strip()
        if not ip_address:
            return LabRuntimeStatus(state=LabState.ERROR)
        return LabRuntimeStatus(state=LabState.RUNNING, target_ip=ip_address)

    async def _is_running(self, definition: LabDefinition) -> bool:
        running_services = await self._running_services(definition)
        if not definition.services.issubset(running_services):
            return False

        target_health = await self._executor.run(
            (
                "docker",
                "inspect",
                "--format",
                "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",
                definition.target_container,
            ),
            self._timeout_seconds,
        )
        if target_health.stdout.strip() != "healthy":
            return False

        await self._executor.run(
            ("docker", "network", "inspect", definition.network_name),
            self._timeout_seconds,
        )
        return True

    async def _has_running_services(self, definition: LabDefinition) -> bool:
        return bool(await self._running_services(definition))

    async def _running_services(self, definition: LabDefinition) -> set[str]:
        result = await self._run_compose(
            definition,
            "ps",
            "--status",
            "running",
            "--services",
        )
        return {
            line.strip() for line in result.stdout.splitlines() if line.strip()
        }

    async def _run_compose(
        self,
        definition: LabDefinition,
        *arguments: str,
    ) -> CommandResult:
        compose_file = Path(definition.compose_file)
        command = (
            "docker",
            "compose",
            "--project-directory",
            compose_file.parent.as_posix(),
            "--file",
            compose_file.as_posix(),
            "--project-name",
            definition.project_name,
            *arguments,
        )
        return await self._executor.run(command, self._timeout_seconds)

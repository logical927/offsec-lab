import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from app.lab.registry import LabDefinition


class DockerCommandError(Exception):
    """Raised when a predefined Docker operation cannot be completed."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


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

    async def start(self, definition: LabDefinition) -> bool:
        async with self._lock:
            if await self._is_running(definition):
                return True

            await self._run_compose(
                definition,
                "up",
                "-d",
                "--wait",
                "--wait-timeout",
                str(max(1, int(self._timeout_seconds) - 10)),
            )
            return False

    async def stop(self, definition: LabDefinition) -> bool:
        async with self._lock:
            if not await self._has_running_services(definition):
                return True

            await self._run_compose(definition, "stop")
            return False

    async def reset(self, definition: LabDefinition) -> None:
        async with self._lock:
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
            str(compose_file.parent),
            "--file",
            str(compose_file),
            "--project-name",
            definition.project_name,
            *arguments,
        )
        return await self._executor.run(command, self._timeout_seconds)

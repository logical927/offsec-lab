import asyncio
from pathlib import Path
from typing import Sequence

import pytest

from app.lab import (
    DockerCommandError,
    DockerComposeLabRunner,
    LabDefinition,
    LabState,
)
from app.lab.runner import AsyncSubprocessExecutor, CommandResult


class RecordingExecutor:
    def __init__(self, results: list[CommandResult]) -> None:
        self.results = results
        self.calls: list[tuple[tuple[str, ...], float]] = []

    async def run(
        self,
        arguments: Sequence[str],
        timeout: float,
    ) -> CommandResult:
        self.calls.append((tuple(arguments), timeout))
        return self.results.pop(0)


def definition() -> LabDefinition:
    return LabDefinition(
        mission_id=1,
        compose_file=Path("/workspace/challenges/m01-recon/compose.lab.yml"),
        project_name="offsec-m01",
        services=frozenset({"attacker", "target"}),
        target_container="target-m01",
        network_name="offsec-m01-net",
    )


def test_runner_starts_with_fixed_compose_arguments_and_timeout() -> None:
    executor = RecordingExecutor(
        [
            CommandResult(0, "", ""),
            CommandResult(0, "", ""),
        ]
    )
    runner = DockerComposeLabRunner(executor, timeout_seconds=45)

    already_running = asyncio.run(runner.start(definition()))

    assert already_running is False
    assert executor.calls == [
        (
            (
                "docker",
                "compose",
                "--project-directory",
                "/workspace/challenges/m01-recon",
                "--file",
                "/workspace/challenges/m01-recon/compose.lab.yml",
                "--project-name",
                "offsec-m01",
                "ps",
                "--status",
                "running",
                "--services",
            ),
            45,
        ),
        (
            (
                "docker",
                "compose",
                "--project-directory",
                "/workspace/challenges/m01-recon",
                "--file",
                "/workspace/challenges/m01-recon/compose.lab.yml",
                "--project-name",
                "offsec-m01",
                "up",
                "-d",
                "--wait",
                "--wait-timeout",
                "35",
            ),
            45,
        ),
    ]


def test_runner_does_not_recreate_a_healthy_running_lab() -> None:
    executor = RecordingExecutor(
        [
            CommandResult(0, "attacker\ntarget\n", ""),
            CommandResult(0, "healthy\n", ""),
            CommandResult(0, "[]", ""),
        ]
    )
    runner = DockerComposeLabRunner(executor)

    already_running = asyncio.run(runner.start(definition()))

    assert already_running is True
    assert len(executor.calls) == 3
    assert executor.calls[1][0] == (
        "docker",
        "inspect",
        "--format",
        "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",
        "target-m01",
    )
    assert executor.calls[2][0] == (
        "docker",
        "network",
        "inspect",
        "offsec-m01-net",
    )


def test_runner_stops_running_services_with_fixed_arguments() -> None:
    executor = RecordingExecutor(
        [
            CommandResult(0, "attacker\ntarget\n", ""),
            CommandResult(0, "", ""),
        ]
    )
    runner = DockerComposeLabRunner(executor, timeout_seconds=45)

    already_stopped = asyncio.run(runner.stop(definition()))

    assert already_stopped is False
    assert executor.calls[1] == (
        (
            "docker",
            "compose",
            "--project-directory",
            "/workspace/challenges/m01-recon",
            "--file",
            "/workspace/challenges/m01-recon/compose.lab.yml",
            "--project-name",
            "offsec-m01",
            "stop",
        ),
        45,
    )


def test_runner_repeated_stop_is_idempotent() -> None:
    executor = RecordingExecutor([CommandResult(0, "", "")])
    runner = DockerComposeLabRunner(executor)

    already_stopped = asyncio.run(runner.stop(definition()))

    assert already_stopped is True
    assert len(executor.calls) == 1
    assert executor.calls[0][0][-4:] == (
        "ps",
        "--status",
        "running",
        "--services",
    )


def test_runner_reset_uses_scoped_destroy_and_recreate_commands() -> None:
    executor = RecordingExecutor(
        [CommandResult(0, "", ""), CommandResult(0, "", "")]
    )
    runner = DockerComposeLabRunner(executor, timeout_seconds=45)
    prefix = (
        "docker",
        "compose",
        "--project-directory",
        "/workspace/challenges/m01-recon",
        "--file",
        "/workspace/challenges/m01-recon/compose.lab.yml",
        "--project-name",
        "offsec-m01",
    )

    asyncio.run(runner.reset(definition()))

    assert executor.calls == [
        (prefix + ("down", "--volumes"), 45),
        (
            prefix
            + (
                "up",
                "-d",
                "--force-recreate",
                "--wait",
                "--wait-timeout",
                "35",
            ),
            45,
        ),
    ]


def test_runner_status_reports_stopped_when_no_services_are_running() -> None:
    executor = RecordingExecutor([CommandResult(0, "", "")])

    result = asyncio.run(DockerComposeLabRunner(executor).status(definition()))

    assert result.state is LabState.STOPPED
    assert result.target_ip is None


def test_runner_status_reports_running_with_internal_target_ip() -> None:
    executor = RecordingExecutor(
        [
            CommandResult(0, "attacker\ntarget\n", ""),
            CommandResult(0, "healthy\n", ""),
            CommandResult(0, "[]", ""),
            CommandResult(0, "172.20.0.3\n", ""),
        ]
    )

    result = asyncio.run(DockerComposeLabRunner(executor).status(definition()))

    assert result.state is LabState.RUNNING
    assert result.target_ip == "172.20.0.3"
    assert executor.calls[-1][0] == (
        "docker",
        "inspect",
        "--format",
        (
            '{{with index .NetworkSettings.Networks "offsec-m01-net"}}'
            "{{.IPAddress}}{{end}}"
        ),
        "target-m01",
    )


def test_runner_status_reports_starting_while_target_health_initializes() -> None:
    executor = RecordingExecutor(
        [
            CommandResult(0, "attacker\ntarget\n", ""),
            CommandResult(0, "starting\n", ""),
        ]
    )

    result = asyncio.run(DockerComposeLabRunner(executor).status(definition()))

    assert result.state is LabState.STARTING
    assert result.target_ip is None


def test_runner_status_rechecks_docker_after_observed_starting_state() -> None:
    executor = RecordingExecutor(
        [
            CommandResult(0, "attacker\ntarget\n", ""),
            CommandResult(0, "starting\n", ""),
            CommandResult(0, "attacker\ntarget\n", ""),
            CommandResult(0, "healthy\n", ""),
            CommandResult(0, "[]", ""),
            CommandResult(0, "172.20.0.3\n", ""),
        ]
    )
    runner = DockerComposeLabRunner(executor)

    first = asyncio.run(runner.status(definition()))
    second = asyncio.run(runner.status(definition()))

    assert first.state is LabState.STARTING
    assert second.state is LabState.RUNNING
    assert second.target_ip == "172.20.0.3"


def test_runner_status_reports_error_for_partial_lab() -> None:
    executor = RecordingExecutor([CommandResult(0, "attacker\n", "")])

    result = asyncio.run(DockerComposeLabRunner(executor).status(definition()))

    assert result.state is LabState.ERROR
    assert result.target_ip is None


@pytest.mark.parametrize("state", [LabState.STARTING, LabState.STOPPING])
def test_runner_status_returns_remembered_transitional_state(
    state: LabState,
) -> None:
    executor = RecordingExecutor([])
    runner = DockerComposeLabRunner(executor)
    runner._operation_states[1] = state

    result = asyncio.run(runner.status(definition()))

    assert result.state is state
    assert executor.calls == []


class TimeoutProcess:
    returncode = None

    def __init__(self) -> None:
        self.killed = False
        self.communicate_calls = 0

    async def communicate(self):
        self.communicate_calls += 1
        if self.communicate_calls == 1:
            await asyncio.Future()
        return b"", b""

    def kill(self) -> None:
        self.killed = True


def test_subprocess_executor_uses_argument_array_and_sanitizes_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = TimeoutProcess()
    captured: dict[str, object] = {}

    async def fake_create_subprocess_exec(*arguments: str, **kwargs: object):
        captured["arguments"] = arguments
        captured["kwargs"] = kwargs
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    with pytest.raises(DockerCommandError, match="timed out"):
        asyncio.run(
            AsyncSubprocessExecutor().run(("docker", "compose", "stop"), 0.01)
        )

    assert captured["arguments"] == ("docker", "compose", "stop")
    assert "shell" not in captured["kwargs"]
    assert process.killed is True


def test_subprocess_executor_sanitizes_nonzero_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailedProcess:
        returncode = 1

        async def communicate(self):
            return b"", b"sensitive docker daemon detail"

    async def fake_create_subprocess_exec(*_arguments: str, **_kwargs: object):
        return FailedProcess()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    with pytest.raises(DockerCommandError) as error:
        asyncio.run(AsyncSubprocessExecutor().run(("docker", "compose", "stop"), 1))

    assert "sensitive docker daemon detail" not in str(error.value)

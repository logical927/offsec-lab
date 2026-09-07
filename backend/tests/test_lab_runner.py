import asyncio
from pathlib import Path
from typing import Sequence

from app.lab import DockerComposeLabRunner, LabDefinition
from app.lab.runner import CommandResult


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

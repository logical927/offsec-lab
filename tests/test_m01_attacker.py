import json
import shutil
import subprocess
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MISSION_DIRECTORY = REPOSITORY_ROOT / "challenges" / "m01-recon"
COMPOSE_FILE = MISSION_DIRECTORY / "compose.lab.yml"
DOCKERFILE = MISSION_DIRECTORY / "attacker" / "Dockerfile"


@pytest.fixture(scope="module")
def attacker_service() -> dict[str, object]:
    docker = shutil.which("docker")
    if docker is None:
        pytest.fail("Docker CLI is required to validate the Mission 01 Compose file")

    result = subprocess.run(
        [
            docker,
            "compose",
            "-f",
            str(COMPOSE_FILE),
            "config",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    rendered = json.loads(result.stdout)
    return rendered["services"]["attacker"]


def test_attacker_uses_the_mission_lab_network(
    attacker_service: dict[str, object],
) -> None:
    assert attacker_service["container_name"] == "offsec-m01-attacker"
    assert attacker_service["networks"] == {"lab": None}
    assert "ports" not in attacker_service


def test_attacker_runs_with_restricted_privileges(
    attacker_service: dict[str, object],
) -> None:
    assert attacker_service["read_only"] is True
    assert attacker_service["cap_drop"] == ["ALL"]
    assert attacker_service["cap_add"] == ["NET_RAW"]
    assert attacker_service["security_opt"] == ["no-new-privileges:true"]
    assert attacker_service["pids_limit"] == 128
    assert attacker_service["mem_limit"] == "268435456"
    assert attacker_service["cpus"] == 0.5
    assert attacker_service["tmpfs"] == [
        "/tmp:rw,noexec,nosuid,nodev,size=64m"
    ]
    assert attacker_service["init"] is True
    assert attacker_service.get("privileged") is not True
    assert attacker_service.get("network_mode") != "host"
    assert "volumes" not in attacker_service


def test_attacker_image_installs_only_the_required_training_toolset() -> None:
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")

    assert dockerfile.startswith("FROM debian:bookworm-20260824-slim\n")
    for package in ("curl", "iputils-ping", "nmap"):
        assert package in dockerfile
    assert "USER trainee" in dockerfile
    assert "--no-install-recommends" in dockerfile
    assert "rm -rf /var/lib/apt/lists/*" in dockerfile

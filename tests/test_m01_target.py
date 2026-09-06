import json
import shutil
import subprocess
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MISSION_DIRECTORY = REPOSITORY_ROOT / "challenges" / "m01-recon"
COMPOSE_FILE = MISSION_DIRECTORY / "compose.lab.yml"
TARGET_DIRECTORY = MISSION_DIRECTORY / "target"


@pytest.fixture(scope="module")
def target_service() -> dict[str, object]:
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
    return rendered["services"]["target"]


def test_target_is_available_only_on_the_internal_lab_network(
    target_service: dict[str, object],
) -> None:
    assert target_service["container_name"] == "target-m01"
    assert target_service["networks"] == {
        "lab": {"aliases": ["target-m01"]}
    }
    assert target_service["expose"] == ["22", "80"]
    assert "ports" not in target_service


def test_target_runs_with_restricted_privileges(
    target_service: dict[str, object],
) -> None:
    assert target_service["read_only"] is True
    assert target_service["cap_drop"] == ["ALL"]
    assert target_service["cap_add"] == ["NET_BIND_SERVICE"]
    assert target_service["security_opt"] == ["no-new-privileges:true"]
    assert target_service["pids_limit"] == 64
    assert target_service["mem_limit"] == "134217728"
    assert target_service["cpus"] == 0.25
    assert target_service["tmpfs"] == [
        "/tmp:rw,noexec,nosuid,nodev,size=32m"
    ]
    assert target_service.get("privileged") is not True
    assert target_service.get("network_mode") != "host"
    assert "volumes" not in target_service


def test_target_image_contains_only_observable_services() -> None:
    dockerfile = (TARGET_DIRECTORY / "Dockerfile").read_text(encoding="utf-8")
    sshd_config = (TARGET_DIRECTORY / "sshd_config").read_text(encoding="utf-8")
    nginx_config = (TARGET_DIRECTORY / "nginx.conf").read_text(encoding="utf-8")
    page = (TARGET_DIRECTORY / "files" / "index.html").read_text(encoding="utf-8")

    assert dockerfile.startswith("FROM debian:bookworm-20260824-slim\n")
    assert "nginx-light" in dockerfile
    assert "openssh-server" in dockerfile
    assert "rm -f /etc/ssh/ssh_host_*" in dockerfile
    assert "USER target" in dockerfile
    assert "PasswordAuthentication no" in sshd_config
    assert "PubkeyAuthentication no" in sshd_config
    assert "PermitRootLogin no" in sshd_config
    assert "HostKey /tmp/offsec-ssh/ssh_host_ed25519_key" in sshd_config
    assert "server_tokens on" in nginx_config
    assert "Northbridge Systems Status Portal" in page

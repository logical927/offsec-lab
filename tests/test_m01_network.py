import json
import shutil
import subprocess
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = REPOSITORY_ROOT / "challenges" / "m01-recon" / "compose.lab.yml"


@pytest.fixture(scope="module")
def rendered_compose() -> dict[str, object]:
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
    return json.loads(result.stdout)


def test_mission_01_uses_a_dedicated_internal_bridge_network(
    rendered_compose: dict[str, object],
) -> None:
    networks = rendered_compose["networks"]
    assert isinstance(networks, dict)

    lab_network = networks["lab"]
    assert isinstance(lab_network, dict)
    assert lab_network["name"] == "offsec-m01-net"
    assert lab_network["driver"] == "bridge"
    assert lab_network["internal"] is True
    assert lab_network.get("attachable", False) is False


def test_mission_01_has_no_published_ports(
    rendered_compose: dict[str, object],
) -> None:
    services = rendered_compose.get("services", {})
    assert isinstance(services, dict)

    for service in services.values():
        assert isinstance(service, dict)
        assert "ports" not in service

    assert set(services) == {"attacker", "target"}


def test_mission_01_has_no_high_risk_container_settings(
    rendered_compose: dict[str, object],
) -> None:
    services = rendered_compose.get("services", {})
    assert isinstance(services, dict)

    for service in services.values():
        assert isinstance(service, dict)
        assert service.get("privileged") is not True
        assert service.get("network_mode") != "host"
        volumes = service.get("volumes", [])
        assert all("/var/run/docker.sock" not in str(volume) for volume in volumes)

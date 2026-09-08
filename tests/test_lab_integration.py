"""Real local Backend -> Docker -> Attacker -> Target. Owns the Mission 01 lab."""
import json
import os
from pathlib import Path
import subprocess
import time

import httpx
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.skipif(
    os.getenv("OFFSEC_TEST_LAB") != "1", reason="set OFFSEC_TEST_LAB=1; owns Mission 01 lab"
)]
COMPOSE = Path(__file__).resolve().parents[1] / "challenges/m01-recon/compose.lab.yml"


def docker(*args):
    return subprocess.run(["docker", *args], check=True, capture_output=True, text=True, timeout=150).stdout


def state(client, expected):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        response = client.get("/api/v1/labs/1/status")
        response.raise_for_status()
        data = response.json()
        if data["status"] == expected:
            return data
        assert data["status"] != "ERROR", data
        time.sleep(0.5)
    pytest.fail(f"Lab did not reach {expected}")


@pytest.fixture
def lab():
    # Explicit opt-in failures are failures, including unavailable Docker/API.
    docker("info", "--format", "{{.ServerVersion}}")
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=150) as client:
        try:
            client.get("/ready").raise_for_status()
            client.post("/api/v1/labs/1/stop").raise_for_status()
            state(client, "STOPPED")
            yield client
        finally:
            try:
                client.post("/api/v1/labs/1/stop").raise_for_status()
            finally:
                docker("compose", "-f", str(COMPOSE), "-p", "offsec-m01", "down", "--volumes")
                assert not docker("ps", "-aq", "--filter", "label=com.docker.compose.project=offsec-m01").strip()
                assert not docker("network", "ls", "-q", "--filter", "name=^offsec-m01-net$").strip()


def test_api_lifecycle_recon_reset_and_isolation(lab):
    initial_progress = lab.get("/api/v1/progress").json()
    start = lab.post("/api/v1/labs/1/start")
    assert start.status_code == 200
    assert start.json()["already_running"] is False
    running = state(lab, "RUNNING")
    assert running["target"]["hostname"] == "target-m01"
    assert lab.post("/api/v1/labs/1/start").json()["already_running"] is True
    for name in ("offsec-m01-attacker", "target-m01"):
        info = json.loads(docker("inspect", name))[0]
        assert info["State"]["Running"]
        assert not info["HostConfig"]["Privileged"]
        assert not info["HostConfig"]["PortBindings"]
        assert info["HostConfig"]["ReadonlyRootfs"]
        assert not info["Mounts"]
        assert set(info["NetworkSettings"]["Networks"]) == {"offsec-m01-net"}
    assert json.loads(docker("network", "inspect", "offsec-m01-net"))[0]["Internal"] is True
    resolved = docker("exec", "offsec-m01-attacker", "getent", "hosts", "target-m01")
    assert running["target"]["ip"] in resolved
    scan = docker("exec", "offsec-m01-attacker", "nmap", "-sT", "-sV", "-p", "22,80", "target-m01")
    assert "22/tcp open" in scan and "80/tcp open" in scan
    assert "OpenSSH 9.2p1" in scan and "nginx" in scan
    http = docker("exec", "offsec-m01-attacker", "curl", "--fail", "--silent", "--show-error", "--max-time", "10", "http://target-m01")
    assert "<title>Northbridge Systems Status Portal</title>" in http
    marker = "/tmp/offsec-phase9-reset-marker"
    docker("exec", "target-m01", "touch", marker)
    docker("exec", "target-m01", "test", "-f", marker)
    before = json.loads(docker("inspect", "target-m01"))[0]["Id"]
    assert lab.post("/api/v1/labs/1/reset").status_code == 200
    state(lab, "RUNNING")
    docker("exec", "target-m01", "test", "!", "-e", marker)
    assert json.loads(docker("inspect", "target-m01"))[0]["Id"] != before
    assert lab.get("/api/v1/progress").json() == initial_progress
    assert lab.post("/api/v1/labs/1/stop").json()["already_stopped"] is False
    assert state(lab, "STOPPED")["target"] is None
    assert lab.post("/api/v1/labs/1/stop").json()["already_stopped"] is True

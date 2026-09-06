from fastapi.testclient import TestClient

from app.database import check_database_connection
from app.main import app

client = TestClient(app)


async def database_connected() -> bool:
    return True


async def database_disconnected() -> bool:
    return False


def test_health_returns_200() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_does_not_check_database() -> None:
    app.dependency_overrides[check_database_connection] = database_disconnected
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_reports_connected_database() -> None:
    app.dependency_overrides[check_database_connection] = database_connected
    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "connected"}


def test_ready_returns_service_unavailable_when_database_is_disconnected() -> None:
    app.dependency_overrides[check_database_connection] = database_disconnected
    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "database": "disconnected",
    }


def test_ready_returns_service_unavailable_when_database_config_is_missing(
    monkeypatch,
) -> None:
    for name in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST"):
        monkeypatch.delenv(name, raising=False)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "database": "disconnected",
    }

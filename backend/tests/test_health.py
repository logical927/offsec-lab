from fastapi.testclient import TestClient

from app.database import check_database_connection
from app.main import app

client = TestClient(app)


async def database_connected() -> bool:
    return True


async def database_disconnected() -> bool:
    return False


def test_health_reports_connected_database() -> None:
    app.dependency_overrides[check_database_connection] = database_connected
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_health_returns_service_unavailable_when_database_is_disconnected() -> None:
    app.dependency_overrides[check_database_connection] = database_disconnected
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "status": "error",
        "database": "disconnected",
        "error": {
            "code": "DATABASE_UNAVAILABLE",
            "message": "Database connection is unavailable.",
        },
    }


def test_health_returns_service_unavailable_when_database_config_is_missing(
    monkeypatch,
) -> None:
    for name in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST"):
        monkeypatch.delenv(name, raising=False)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["database"] == "disconnected"
    assert response.json()["error"]["code"] == "DATABASE_UNAVAILABLE"

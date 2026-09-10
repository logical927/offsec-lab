import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_progress_service
from app.main import app
from app.models import Challenge
from app.repositories import ProgressRepository
from app.services import ProgressService
from app.services.mission_service import MissionNotFoundError


def service():
    missions = Mock(get_active=AsyncMock(return_value=Mock()))
    challenges = Mock(list_active_for_mission=AsyncMock(return_value=[
        Challenge(id=1, mission_id=7), Challenge(id=2, mission_id=7)
    ]))
    repo = Mock(lock_mission=AsyncMock(), delete_for_mission=AsyncMock(),
                commit=AsyncMock(), rollback=AsyncMock())
    return ProgressService(missions, challenges, repo), missions, repo


def test_reset_unlocks_first_challenge_and_commits():
    subject, _, repo = service()
    snapshot = asyncio.run(subject.reset_mission(7))
    assert snapshot.status == 'NOT_STARTED'
    assert [c.status for c in snapshot.challenges] == ['AVAILABLE', 'LOCKED']
    repo.lock_mission.assert_awaited_once_with(7)
    repo.delete_for_mission.assert_awaited_once_with(7)
    repo.commit.assert_awaited_once()


def test_unknown_mission_does_not_delete():
    subject, missions, repo = service()
    missions.get_active.return_value = None
    with pytest.raises(MissionNotFoundError):
        asyncio.run(subject.reset_mission(999))
    repo.delete_for_mission.assert_not_awaited()


def test_reset_rolls_back_failure():
    subject, _, repo = service()
    repo.commit.side_effect = RuntimeError('failed')
    with pytest.raises(RuntimeError):
        asyncio.run(subject.reset_mission(7))
    repo.rollback.assert_awaited_once()


def test_delete_is_scoped_to_one_mission():
    session = Mock(execute=AsyncMock())
    asyncio.run(ProgressRepository(session).delete_for_mission(7))
    sql = str(session.execute.await_args.args[0].compile(compile_kwargs={'literal_binds': True}))
    assert 'DELETE FROM progress WHERE progress.mission_id = 7' in sql


def test_reset_api_and_validation():
    subject, missions, _ = service()
    app.dependency_overrides[get_progress_service] = lambda: subject
    try:
        client = TestClient(app)
        result = client.post('/api/v1/progress/7/reset')
        assert result.status_code == 200
        assert result.json()['status'] == 'NOT_STARTED'
        assert result.json()['challenges'][0]['status'] == 'AVAILABLE'
        assert client.post('/api/v1/progress/0/reset').status_code == 422
        missions.get_active.return_value = None
        assert client.post('/api/v1/progress/999/reset').status_code == 404
    finally:
        app.dependency_overrides.clear()

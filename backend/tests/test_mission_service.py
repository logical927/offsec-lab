import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from app.models import Challenge, Mission
from app.services import MissionNotFoundError, MissionService


def test_list_missions_delegates_to_repository() -> None:
    missions = [Mission(id=1, slug="m01", title="Recon", sort_order=1)]
    repository = Mock()
    repository.list_active = AsyncMock(return_value=missions)
    service = MissionService(repository)

    assert asyncio.run(service.list_missions()) == missions
    repository.list_active.assert_awaited_once_with()


def test_get_mission_returns_mission_and_challenges() -> None:
    mission = Mission(id=1, slug="m01", title="Recon", sort_order=1)
    challenges = [
        Challenge(
            id=1,
            mission_id=1,
            slug="host-discovery",
            title="Host Discovery",
            sort_order=1,
        )
    ]
    repository = Mock()
    repository.get_active = AsyncMock(return_value=mission)
    repository.list_active_challenges = AsyncMock(return_value=challenges)
    service = MissionService(repository)

    detail = asyncio.run(service.get_mission(1))

    assert detail.mission is mission
    assert detail.challenges == challenges
    repository.list_active_challenges.assert_awaited_once_with(1)


def test_get_unknown_mission_stops_before_querying_challenges() -> None:
    repository = Mock()
    repository.get_active = AsyncMock(return_value=None)
    repository.list_active_challenges = AsyncMock()
    service = MissionService(repository)

    with pytest.raises(MissionNotFoundError):
        asyncio.run(service.get_mission(999))

    repository.list_active_challenges.assert_not_awaited()

from collections.abc import Sequence
from dataclasses import dataclass

from app.models import Challenge, Mission
from app.repositories import MissionRepository


class MissionNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class MissionDetail:
    mission: Mission
    challenges: Sequence[Challenge]


class MissionService:
    def __init__(self, repository: MissionRepository) -> None:
        self._repository = repository

    async def list_missions(self) -> Sequence[Mission]:
        return await self._repository.list_active()

    async def get_mission(self, mission_id: int) -> MissionDetail:
        mission = await self._repository.get_active(mission_id)
        if mission is None:
            raise MissionNotFoundError

        challenges = await self._repository.list_active_challenges(mission_id)
        return MissionDetail(mission=mission, challenges=challenges)

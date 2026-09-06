from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Challenge, Mission


class ChallengeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(self, challenge_id: int) -> Challenge | None:
        statement = (
            select(Challenge)
            .options(joinedload(Challenge.mission))
            .where(
                Challenge.id == challenge_id,
                Challenge.is_active.is_(True),
                Challenge.mission.has(Mission.is_active.is_(True)),
            )
        )
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def list_active_for_mission(
        self,
        mission_id: int,
    ) -> Sequence[Challenge]:
        statement = (
            select(Challenge)
            .where(
                Challenge.mission_id == mission_id,
                Challenge.is_active.is_(True),
            )
            .order_by(Challenge.sort_order, Challenge.id)
        )
        result = await self._session.execute(statement)
        return result.scalars().all()

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Challenge, Mission


class MissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self) -> Sequence[Mission]:
        statement = (
            select(Mission)
            .where(Mission.is_active.is_(True))
            .order_by(Mission.sort_order, Mission.id)
        )
        result = await self._session.execute(statement)
        return result.scalars().all()

    async def get_active(self, mission_id: int) -> Mission | None:
        statement = select(Mission).where(
            Mission.id == mission_id,
            Mission.is_active.is_(True),
        )
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def list_active_challenges(self, mission_id: int) -> Sequence[Challenge]:
        statement = (
            select(Challenge)
            .options(selectinload(Challenge.hints))
            .where(
                Challenge.mission_id == mission_id,
                Challenge.is_active.is_(True),
            )
            .order_by(Challenge.sort_order, Challenge.id)
        )
        result = await self._session.execute(statement)
        return result.scalars().all()

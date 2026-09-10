from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Mission, Progress


class ProgressRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_mission(self, mission_id: int) -> Sequence[Progress]:
        statement = select(Progress).where(Progress.mission_id == mission_id)
        result = await self._session.execute(statement)
        return result.scalars().all()

    def add_all(self, progress_rows: Sequence[Progress]) -> None:
        self._session.add_all(progress_rows)

    async def delete_for_mission(self, mission_id: int) -> None:
        await self._session.execute(
            delete(Progress).where(Progress.mission_id == mission_id)
        )

    async def flush(self) -> None:
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def lock_mission(self, mission_id: int) -> None:
        statement = (
            select(Mission.id)
            .where(Mission.id == mission_id)
            .with_for_update()
        )
        result = await self._session.execute(statement)
        result.scalar_one()

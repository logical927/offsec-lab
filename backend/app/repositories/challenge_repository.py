from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Challenge


class ChallengeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(self, challenge_id: int) -> Challenge | None:
        statement = select(Challenge).where(
            Challenge.id == challenge_id,
            Challenge.is_active.is_(True),
        )
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

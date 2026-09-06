from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.repositories import MissionRepository
from app.services import MissionService


def get_mission_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> MissionService:
    return MissionService(MissionRepository(session))

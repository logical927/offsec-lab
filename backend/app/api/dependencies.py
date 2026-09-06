from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.repositories import ChallengeRepository, MissionRepository
from app.services import ChallengeService, MissionService


def get_challenge_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ChallengeService:
    return ChallengeService(ChallengeRepository(session))


def get_mission_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> MissionService:
    return MissionService(MissionRepository(session))

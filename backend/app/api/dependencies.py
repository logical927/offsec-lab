from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.repositories import (
    ChallengeRepository,
    MissionRepository,
    ProgressRepository,
)
from app.services import ChallengeService, MissionService, ProgressService


def get_progress_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ProgressService:
    return ProgressService(
        MissionRepository(session),
        ChallengeRepository(session),
        ProgressRepository(session),
    )


def get_challenge_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ChallengeService:
    progress_service = ProgressService(
        MissionRepository(session),
        ChallengeRepository(session),
        ProgressRepository(session),
    )
    return ChallengeService(ChallengeRepository(session), progress_service)


def get_mission_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> MissionService:
    return MissionService(MissionRepository(session))

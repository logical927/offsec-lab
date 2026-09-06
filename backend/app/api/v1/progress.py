from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_progress_service
from app.schemas import (
    ChallengeProgressResponse,
    MissionProgressResponse,
    ProgressResponse,
)
from app.services import ProgressService

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=ProgressResponse)
async def get_progress(
    service: Annotated[ProgressService, Depends(get_progress_service)],
) -> ProgressResponse:
    snapshots = await service.list_progress()
    return ProgressResponse(
        missions=[
            MissionProgressResponse(
                mission_id=mission.mission_id,
                status=mission.status,
                challenges=[
                    ChallengeProgressResponse(
                        challenge_id=challenge.challenge_id,
                        status=challenge.status,
                    )
                    for challenge in mission.challenges
                ],
            )
            for mission in snapshots
        ]
    )

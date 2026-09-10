from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.dependencies import get_progress_service
from app.schemas import (
    ChallengeProgressResponse,
    MissionProgressResponse,
    ProgressResponse,
)
from app.services import ProgressService

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/{mission_id}/reset", response_model=MissionProgressResponse)
async def reset_progress(
    mission_id: Annotated[int, Path(gt=0)],
    service: Annotated[ProgressService, Depends(get_progress_service)],
) -> MissionProgressResponse:
    mission = await service.reset_mission(mission_id)
    return MissionProgressResponse(
        mission_id=mission.mission_id,
        status=mission.status,
        challenges=[
            ChallengeProgressResponse(challenge_id=item.challenge_id, status=item.status)
            for item in mission.challenges
        ],
    )


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

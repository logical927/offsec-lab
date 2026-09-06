from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.dependencies import get_mission_service
from app.schemas import (
    ChallengeSummaryResponse,
    MissionDetailResponse,
    MissionSummaryResponse,
)
from app.services import MissionService

router = APIRouter(prefix="/missions", tags=["missions"])


@router.get("", response_model=list[MissionSummaryResponse])
async def list_missions(
    service: Annotated[MissionService, Depends(get_mission_service)],
) -> list[MissionSummaryResponse]:
    missions = await service.list_missions()
    return [MissionSummaryResponse.model_validate(mission) for mission in missions]


@router.get("/{mission_id}", response_model=MissionDetailResponse)
async def get_mission(
    mission_id: Annotated[int, Path(gt=0)],
    service: Annotated[MissionService, Depends(get_mission_service)],
) -> MissionDetailResponse:
    detail = await service.get_mission(mission_id)
    return MissionDetailResponse(
        **MissionSummaryResponse.model_validate(detail.mission).model_dump(),
        challenges=[
            ChallengeSummaryResponse.model_validate(challenge)
            for challenge in detail.challenges
        ],
    )

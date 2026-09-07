from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.dependencies import get_lab_service
from app.schemas import LabResetResponse, LabStartResponse, LabStopResponse
from app.services import LabService

router = APIRouter(prefix="/labs", tags=["labs"])


@router.post("/{mission_id}/start", response_model=LabStartResponse)
async def start_lab(
    mission_id: Annotated[int, Path(gt=0)],
    service: Annotated[LabService, Depends(get_lab_service)],
) -> LabStartResponse:
    result = await service.start_lab(mission_id)
    return LabStartResponse(
        mission_id=result.mission_id,
        status="running",
        already_running=result.already_running,
    )


@router.post("/{mission_id}/stop", response_model=LabStopResponse)
async def stop_lab(
    mission_id: Annotated[int, Path(gt=0)],
    service: Annotated[LabService, Depends(get_lab_service)],
) -> LabStopResponse:
    result = await service.stop_lab(mission_id)
    return LabStopResponse(
        mission_id=result.mission_id,
        status="stopped",
        already_stopped=result.already_stopped,
    )


@router.post("/{mission_id}/reset", response_model=LabResetResponse)
async def reset_lab(
    mission_id: Annotated[int, Path(gt=0)],
    service: Annotated[LabService, Depends(get_lab_service)],
) -> LabResetResponse:
    result = await service.reset_lab(mission_id)
    return LabResetResponse(mission_id=result.mission_id, status="running")

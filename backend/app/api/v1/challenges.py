from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.dependencies import get_challenge_service
from app.schemas import ChallengeAnswerRequest, ChallengeAnswerResponse
from app.services import ChallengeService

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.post(
    "/{challenge_id}/answers",
    response_model=ChallengeAnswerResponse,
)
async def answer_challenge(
    challenge_id: Annotated[int, Path(gt=0)],
    request: ChallengeAnswerRequest,
    service: Annotated[ChallengeService, Depends(get_challenge_service)],
) -> ChallengeAnswerResponse:
    result = await service.check_answer(challenge_id, request.answer)
    return ChallengeAnswerResponse(correct=result.correct)

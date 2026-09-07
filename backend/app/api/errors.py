from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.services import (
    ChallengeNotAnswerableError,
    ChallengeNotFoundError,
    ChallengeLockedError,
    MissionNotFoundError,
    LabNotFoundError,
    LabStartFailedError,
)


async def lab_not_found_handler(
    _request: Request,
    _exc: LabNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "LAB_NOT_FOUND",
                "message": "Lab not found.",
            }
        },
    )


async def lab_start_failed_handler(
    _request: Request,
    _exc: LabStartFailedError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "code": "LAB_START_FAILED",
                "message": "Failed to start the lab.",
            }
        },
    )


async def challenge_locked_handler(
    _request: Request,
    _exc: ChallengeLockedError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": "CHALLENGE_LOCKED",
                "message": "Challenge is locked.",
            }
        },
    )


async def challenge_not_found_handler(
    _request: Request,
    _exc: ChallengeNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "CHALLENGE_NOT_FOUND",
                "message": "Challenge not found.",
            }
        },
    )


async def challenge_not_answerable_handler(
    _request: Request,
    _exc: ChallengeNotAnswerableError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": "CHALLENGE_NOT_ANSWERABLE",
                "message": "Challenge does not accept answers.",
            }
        },
    )


async def mission_not_found_handler(
    _request: Request,
    _exc: MissionNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "MISSION_NOT_FOUND",
                "message": "Mission not found.",
            }
        },
    )

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.services import MissionNotFoundError


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

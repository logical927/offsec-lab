from typing import Annotated

from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse

from app.api.errors import (
    challenge_not_answerable_handler,
    challenge_locked_handler,
    challenge_not_found_handler,
    lab_not_found_handler,
    lab_reset_failed_handler,
    lab_start_failed_handler,
    lab_stop_failed_handler,
    mission_not_found_handler,
)
from app.api.v1 import router as api_v1_router
from app.database import check_database_connection
from app.services import (
    ChallengeLockedError,
    ChallengeNotAnswerableError,
    ChallengeNotFoundError,
    LabNotFoundError,
    LabResetFailedError,
    LabStartFailedError,
    LabStopFailedError,
    MissionNotFoundError,
)

app = FastAPI(title="OffSec Lab API", version="0.1.0")
app.include_router(api_v1_router)
app.add_exception_handler(MissionNotFoundError, mission_not_found_handler)
app.add_exception_handler(LabNotFoundError, lab_not_found_handler)
app.add_exception_handler(LabStartFailedError, lab_start_failed_handler)
app.add_exception_handler(LabStopFailedError, lab_stop_failed_handler)
app.add_exception_handler(LabResetFailedError, lab_reset_failed_handler)
app.add_exception_handler(ChallengeNotFoundError, challenge_not_found_handler)
app.add_exception_handler(ChallengeLockedError, challenge_locked_handler)
app.add_exception_handler(
    ChallengeNotAnswerableError,
    challenge_not_answerable_handler,
)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
async def ready(
    database_connected: Annotated[bool, Depends(check_database_connection)],
):
    if not database_connected:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "disconnected",
            },
        )

    return {"status": "ready", "database": "connected"}

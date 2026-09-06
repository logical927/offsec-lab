from fastapi import APIRouter

from app.api.v1.challenges import router as challenges_router
from app.api.v1.missions import router as missions_router
from app.api.v1.progress import router as progress_router

router = APIRouter(prefix="/api/v1")
router.include_router(missions_router)
router.include_router(challenges_router)
router.include_router(progress_router)

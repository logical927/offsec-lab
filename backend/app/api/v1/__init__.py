from fastapi import APIRouter

from app.api.v1.missions import router as missions_router

router = APIRouter(prefix="/api/v1")
router.include_router(missions_router)

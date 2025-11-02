"""Router initialization for the API module."""

from fastapi import APIRouter

from src.health.routes import router as health_router
from src.k8s.routers import kubernetes_router
from src.schedules.routes import scheduler_router as schedules_router
from src.shared.auth import auth_router

# Create main API router
router = APIRouter()

# Include all sub-routers
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(kubernetes_router)
router.include_router(schedules_router)

__all__ = ["router"]

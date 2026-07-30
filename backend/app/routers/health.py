"""Health check endpoint for uptime monitoring and deployment readiness probes."""
from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Service health check")
async def health_check() -> dict:
    settings = get_settings()
    return {"status": "ok", "app_name": settings.app_name, "version": settings.app_version}

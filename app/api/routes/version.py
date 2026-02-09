from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("", summary="Build/version info")
async def version():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "git_sha": settings.GIT_SHA,
        "env": settings.APP_ENV,
    }

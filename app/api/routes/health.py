from fastapi import APIRouter

router = APIRouter()

@router.get("", summary="Health (API namespace)")
async def health():
    return {"status": "ok"}

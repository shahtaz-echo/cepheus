from fastapi import APIRouter
from app.handler.response_handler import APIResponse
from app.core.settings import get_settings

router = APIRouter()

@router.get("", response_model=APIResponse)
async def get_health() -> APIResponse:
    settings = get_settings()
    return APIResponse(
        status_code=200,
        success=True,
        message="Server is Live and Healthy!"
    )

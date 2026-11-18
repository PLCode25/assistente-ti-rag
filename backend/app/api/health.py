from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, environment=settings.environment)

from fastapi import APIRouter
from app.api import healthcheck

router = APIRouter()

router.include_router(healthcheck.router, tags=["Health Check"], prefix="/health")
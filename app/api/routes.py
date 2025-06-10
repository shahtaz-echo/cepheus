from fastapi import APIRouter
from app.api import healthcheck
from products.routes import router as product_router
from tenants.routes import router as tenant_router

router = APIRouter()

router.include_router(healthcheck.router, tags=["health check"], prefix="/health")
router.include_router(product_router, tags=["products"], prefix="/products")
router.include_router(tenant_router, tags=["tenants"], prefix="/tenants")
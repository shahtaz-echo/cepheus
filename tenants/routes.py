from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from tenants.services import TenantService
from tenants.schema import TenantCreate, Tenant
from typing import List
from uuid import UUID

router = APIRouter()


@router.post("/", response_model=Tenant)
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db)):
    service = TenantService(db)
    new_tenant = service.create_new_tenant(tenant.dict())
    return new_tenant


@router.get("/", response_model=List[Tenant])
def get_all_tenants(db: Session = Depends(get_db)):
    service = TenantService(db)
    return service.get_all_tenants()


@router.get("/{tenant_id}", response_model=Tenant)
def get_tenant(tenant_id: UUID, db: Session = Depends(get_db)):
    service = TenantService(db)
    tenant = service.get_tenant_data(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

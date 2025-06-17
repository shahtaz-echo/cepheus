from sqlalchemy.orm import Session
from tenants.models import Tenant
from uuid import UUID
from fastapi import HTTPException


def create_tenant(db:Session, tenant_data: dict):
    tenant = Tenant(**tenant_data)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

def get_tenant(db:Session, tenant_id: UUID):
    return db.query(Tenant).filter(Tenant.id==tenant_id).first()

def get_tenants(db:Session):
    return db.query(Tenant).all()

def get_tenant_platform(db: Session, tenant_id: UUID) -> str:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant.platform.value

def get_tenant_name(db: Session, tenant_id: UUID) -> str:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant.name
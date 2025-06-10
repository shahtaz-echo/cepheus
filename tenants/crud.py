from sqlalchemy.orm import Session
from tenants.models import Tenant
from uuid import UUID


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

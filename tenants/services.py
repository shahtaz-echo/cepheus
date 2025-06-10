from uuid import UUID
from tenants.crud import create_tenant, get_tenant, get_tenants

class TenantService:
    def __init__(self, db):
        self.db = db

    def create_new_tenant(self, tenant_data: dict):
        return create_tenant(self.db, tenant_data)
    
    def get_tenant_data(self, tenant_id: UUID):
        return get_tenant(self.db, tenant_id)
    
    def get_all_tenants(self):
        return get_tenants(self.db)
    
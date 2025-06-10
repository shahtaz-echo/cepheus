from pydantic import BaseModel
from uuid import UUID

class TenantCreate(BaseModel):
    name: str
    platform: str
    language: str

class Tenant(BaseModel):
    id: UUID
    name: str
    platform: str
    language: str

    class Config:
        orm_mode = True
        
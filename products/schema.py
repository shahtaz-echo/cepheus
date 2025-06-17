from uuid import UUID
from pydantic import BaseModel
from typing import List

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float

class ProductOut(BaseModel):
    id: UUID
    product_id: str
    name: str
    description: str | None
    price: float

    class Config:
        orm_mode = True

class PaginatedProductOut(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[ProductOut]
        
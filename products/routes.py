from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from products.services import ProductService
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Pydantic Schemas
class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float

class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: float

    class Config:
        orm_mode = True

# Endpoints
@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    new_product = service.create_new_product(product.dict())
    return new_product

@router.get("/", response_model=List[ProductOut])
def get_all_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_all_products()

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.get_single_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

from uuid import UUID
from fastapi import (
    APIRouter, 
    Depends, 
    File,
    Form, 
    HTTPException, 
    UploadFile, 
)
from sqlalchemy.orm import Session
from app.db.database import get_db
from products.services import ProductService
from products.schema import ProductCreate, ProductOut
from typing import List

router = APIRouter()


@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    new_product = service.add_new_product(product.dict())
    return new_product


@router.post("/bulk-create", response_model=List[ProductOut])
def create_bulk_product(products: List[ProductCreate], db: Session = Depends(get_db)):
    service = ProductService(db)
    products_data = [product.dict() for product in products]
    created_products = service.add_bulk_proudcts(products_data)
    return created_products

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


# 📦 File upload endpoint
@router.post("/upload-file/", response_model=List[ProductOut])
def upload_product_file(
    tenant_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    created_products = service.process_product_file(tenant_id, file)
    return created_products
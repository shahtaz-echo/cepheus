import time
from uuid import UUID
from app.db.database import get_db
from fastapi import (
    APIRouter, 
    Depends, 
    File,
    Form, 
    Query,
    HTTPException, 
    UploadFile, 
)
from fastapi.responses import JSONResponse
from products.services import ProductService
from products.schema import ProductCreate, ProductOut, PaginatedProductOut
from sqlalchemy.orm import Session
from typing import List


router = APIRouter()


# @router.post("/", response_model=ProductOut)
# def create_product(product: ProductCreate, db: Session = Depends(get_db)):
#     service = ProductService(db)
#     new_product = service.add_new_product(product.dict())
#     return new_product


# @router.post("/bulk-create", response_model=List[ProductOut])
# def create_bulk_product(products: List[ProductCreate], db: Session = Depends(get_db)):
#     service = ProductService(db)
#     products_data = [product.dict() for product in products]
#     created_products = service.add_bulk_proudcts(products_data)
#     return created_products


@router.get("/", response_model=PaginatedProductOut)
def get_all_products(
    limit: int = Query(10, ge=1, le=100, description="Number of products to fetch"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    total, products = service.get_all_products(limit, offset)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": products
    }


@router.get("/{tenant_id}", response_model=PaginatedProductOut)
def get_all_tenant_products(
    tenant_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Number of products to fetch"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    total, tenant_name, products = service.all_tenant_products(limit, offset, tenant_id)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "tenant": tenant_name,
        "data": products
    }



# @router.get("/{product_id}", response_model=ProductOut)
# def get_product(product_id: int, db: Session = Depends(get_db)):
#     service = ProductService(db)
#     product = service.get_single_product(product_id)
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product


@router.delete("/{tenant_id}", response_model=ProductOut)
def delete_products(tenant_id: UUID, db: Session = Depends(get_db)):
    service = ProductService(db)
    result = service.delete_tenant_products(tenant_id)
    return JSONResponse(content=result)


# File upload endpoint
@router.post("/upload-file/")
def upload_product_file(
    tenant_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    result = service.process_product_file(tenant_id, file)
    return JSONResponse(content=result)


@router.post("/fetch-products-from-url/")
def fetch_products_from_url(
    tenant_id: UUID,
    data_url: str = Query(..., description="URL to JSON or XML product feed"),
    data_format: str = Query(..., regex="^(json|xml)$", description="Format of the product feed: 'json' or 'xml'"),
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    result = service.fetch_and_process_product_data(tenant_id, data_url, data_format)
    return JSONResponse(content=result)


# Search for products
@router.post("/search/")
def search_products(tenant_id: UUID, user_query: str, db: Session = Depends(get_db)):
    start_time = time.time()

    service = ProductService(db)
    products = service.search_products(tenant_id, user_query)

    duration = round(time.time() - start_time, 4)

    return {
        "duration": f"{duration} sec",
        "total_found": len(products),
        "products": products
    }
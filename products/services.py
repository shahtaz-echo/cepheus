import uuid
from uuid import UUID
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session
from products.crud import (
    get_product, 
    get_products, 
    create_product,
    create_bulk_products,
    upsert_products
)
from tenants.crud import get_tenant_platform
from products.helpers.platform_handler import PlatformHandler

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_single_product(self, product_id: int):
        return get_product(self.db, product_id)

    def get_all_products(self):
        return get_products(self.db)

    def add_new_product(self, product_data: dict):
        return create_product(self.db, product_data)
   
    def add_bulk_proudcts(self, products_data: list[dict]):
        return create_bulk_products(self.db, products_data)
    

    def process_product_file(self, tenant_id: UUID, file) -> dict:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)

        elif file.filename.endswith(".json"):
            df = pd.read_json(file.file)

        elif file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file.file)
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        platform = get_tenant_platform(self.db, tenant_id)
        sanitized_data = PlatformHandler.sanitize(df, platform)

        products_data = [
            {
                "tenant_id": tenant_id,
                "product_id": row["product_id"],
                "name": row["name"],
                "description": row["description"],
                "price": row["price"],
            }
            for _, row in sanitized_data.iterrows()
        ]

        if not products_data:
            raise HTTPException(status_code=400, detail="No valid product entries found.")

        affected_rows = upsert_products(self.db, products_data)

        return {
            "total_uploaded": len(products_data),
            "rows_affected": affected_rows
        }
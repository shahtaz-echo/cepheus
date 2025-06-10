import uuid
from uuid import UUID
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session
from products.crud import (
    get_product, 
    get_products, 
    create_product,
    create_bulk_products
) 

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
    
    def process_product_file(self, tenant_id: UUID, file) -> list:

        # Read and parse the file
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(".json"):
            df = pd.read_json(file.file)
        elif file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        required_columns = ["name", "description", "price"]
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing column: {col}")

        df = df.dropna(subset=required_columns)
        df = df[df["price"].apply(lambda x: isinstance(x, (int, float)) and x > 0)]

        products_data = [
            {
                "tenant_id": tenant_id,
                "name": row["name"],
                "description": row["description"],
                "price": row["price"],
            }
            for _, row in df.iterrows()
        ]

        created_products = create_bulk_products(self.db, products_data)
        return created_products

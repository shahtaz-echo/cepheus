import requests
import pandas as pd

from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from products.crud import (
    get_product, 
    get_products, 
    create_product,
    create_bulk_products,
    upsert_products,
    get_products_by_ids,
    delete_bulk_products,
    get_tenant_products
)

from tenants.crud import get_tenant_platform, get_tenant_name
from products.helpers.platform_handler import PlatformHandler
from products.helpers.embed import TextEmbed
from products.helpers.indexing import index

import logging
logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_single_product(self, product_id: int):
        return get_product(self.db, product_id)

    def get_all_products(self, limit: int = 10, offset: int = 0):
        return get_products(self.db, limit, offset)
    

    def all_tenant_products(self, limit: int = 10, offset: int = 0, tenant_id: UUID=""):
        total, products = get_tenant_products(self.db, tenant_id, limit, offset)
        tenant_name = get_tenant_name(self.db, tenant_id)
        return total, tenant_name, products 


    def add_new_product(self, product_data: dict):
        return create_product(self.db, product_data)
   
    def add_bulk_proudcts(self, products_data: list[dict]):
        return create_bulk_products(self.db, products_data)
    
    
    def delete_tenant_products(self, tenant_id: UUID):
        total_deleted = delete_bulk_products(self.db, tenant_id)
        tenant_name = get_tenant_name(self.db, tenant_id)

        return {
            "message": "Deleted all products from "+ tenant_name,
            "total_deleted": total_deleted
        }
    

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
    

    def fetch_and_process_product_data(self, tenant_id: UUID, data_url: str, data_format: str) -> dict:
        MAX_PRODUCTS_TO_PROCESS = 300
        try:
            response = requests.get(data_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data from {data_url}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch data: {str(e)}")

        if data_format == "json":
            try:
                data = response.json()
                logger.info(f"Fetched JSON data with {len(data)} items")
                
                # Handle different JSON structures
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    # If it's a dict, check for common product list keys
                    if 'products' in data:
                        df = pd.DataFrame(data['products'])
                    elif 'items' in data:
                        df = pd.DataFrame(data['items'])
                    else:
                        # If it's a single product object, wrap in list
                        df = pd.DataFrame([data])
                else:
                    raise ValueError("JSON data is not in expected format (list or dict)")
                    
                logger.info(f"Created DataFrame with shape: {df.shape}")
                logger.info(f"DataFrame columns: {list(df.columns)}")
                
            except Exception as e:
                logger.error(f"Invalid JSON data: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

        elif data_format == "xml":
            try:
                df = pd.read_xml(response.content)
            except Exception as e:
                logger.error(f"Invalid XML data: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid XML data: {str(e)}")

        else:
            raise HTTPException(status_code=400, detail="Unsupported data format.")

        # Get platform and sanitize data
        try:
            platform = get_tenant_platform(self.db, tenant_id)
            logger.info(f"Processing for platform: {platform}")
            
            sanitized_data = PlatformHandler.sanitize(df, platform + "_" + data_format.lower())
            logger.info(f"Sanitized data shape: {sanitized_data.shape}")
            
        except Exception as e:
            logger.error(f"Error during data sanitization: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing data: {str(e)}")

        # Convert to products data
        try:
            products_data = []
            for _, row in sanitized_data.iterrows():
                product_data = {
                    "tenant_id": tenant_id,
                    "product_id": str(row["product_id"]),  # Ensure string
                    "name": str(row["name"]) if pd.notna(row["name"]) else "",
                    "description": str(row["description"]) if pd.notna(row["description"]) else "",
                    "price": float(row["price"]) if pd.notna(row["price"]) and row["price"] != "" else 0.0,
                }
                products_data.append(product_data)
                
            if len(products_data) > MAX_PRODUCTS_TO_PROCESS:
                logger.info(f"Truncating product list from {len(products_data)} to {MAX_PRODUCTS_TO_PROCESS}")
                products_data = products_data[:MAX_PRODUCTS_TO_PROCESS]
            logger.info(f"Processed {len(products_data)} products")
            
        except Exception as e:
            logger.error(f"Error converting to products data: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error converting product data: {str(e)}")

        if not products_data:
            raise HTTPException(status_code=400, detail="No valid product entries found.")

        try:
            affected_rows = upsert_products(self.db, products_data)
            return {
                "total_uploaded": len(products_data),
                "rows_affected": affected_rows
            }
        except Exception as e:
            logger.error(f"Error during database upsert: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    

    def search_products(self, tenant_id, user_query):
        top_k = 10
        embed = TextEmbed()
        embedded_query = embed.generate_embedding(user_query)
        results = index.query(
            vector=embedded_query,
            top_k=top_k,
            namespace=str(tenant_id),
            include_values=False
        )

        matches = [
            {
                "product_id": match['id'],
                "score": match['score']
            }
            for match in results['matches']
        ]

        product_ids = [m["product_id"] for m in matches]
        products = get_products_by_ids(self.db, product_ids)

        # Map products by product_id for faster lookup
        product_map = {p.product_id: p for p in products}

        # Attach scores while preserving Pinecone match order
        final_results = []
        for match in matches:
            product = product_map.get(match["product_id"])
            if product:
                final_results.append({
                    "product": product,
                    "score": match["score"]
                })

        return final_results
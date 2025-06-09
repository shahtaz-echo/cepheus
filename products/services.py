from sqlalchemy.orm import Session
from products.crud import (
    get_product, 
    get_products, 
    create_product
) 

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_single_product(self, product_id: int):
        return get_product(self.db, product_id)

    def get_all_products(self):
        return get_products(self.db)

    def create_new_product(self, product_data: dict):
        return create_product(self.db, product_data)

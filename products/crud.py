from sqlalchemy.orm import Session
from products.models import Product

def get_product(db:Session, product_id:int):
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(db:Session):
    return db.query(Product).all()


def create_product(db:Session, product_data: dict):
    product = Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

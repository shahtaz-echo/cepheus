from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from products.models import Product
from uuid import UUID

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


def create_bulk_products(db: Session, products_data: list[dict]) -> list[UUID]:
    products = [Product(**product_data) for product_data in products_data]
    db.add_all(products)
    db.commit()

    # Get IDs efficiently without refreshing full objects
    product_ids = [product.id for product in products]
    return product_ids


def upsert_products(db: Session, products_data: list[dict]) -> int:
    stmt = insert(Product).values(products_data)
    update_dict = {
        "name": stmt.excluded.name,
        "description": stmt.excluded.description,
        "price": stmt.excluded.price,
    }
    stmt = stmt.on_conflict_do_update(
        constraint="uix_tenant_product",
        set_=update_dict
    )
    result = db.execute(stmt)
    db.commit()

    return result.rowcount  

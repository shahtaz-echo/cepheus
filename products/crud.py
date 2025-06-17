from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from products.models import Product
from uuid import UUID
from products.helpers.embed import TextEmbed
from products.helpers.indexing import index

def get_product(db:Session, product_id:int):
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(db: Session, limit: int = 10, offset: int = 0):
    total = db.query(Product).count()
    products = (
        db.query(Product)
        .order_by(Product.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return total, products

def get_tenant_products(db: Session, tenant_id: UUID, limit: int = 10, offset: int = 0):
    query = db.query(Product).filter(Product.tenant_id == tenant_id)

    total = query.count()

    products = (
        query.order_by(Product.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return total, products

def get_products_by_ids(db: Session, product_ids: list[str]):
    return db.query(Product).filter(Product.product_id.in_(product_ids)).all()


def delete_bulk_products(db: Session, tenant_id: UUID) -> int:
    deleted_count = (
        db.query(Product)
        .filter(Product.tenant_id == tenant_id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted_count

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

    # Vectorize and upsert to Pinecone
    vectors = []
    embed = TextEmbed()
    for product in products_data:
        embedding_input = f"{product['name']} {product['description']}"
        embedding = embed.generate_embedding(embedding_input)

        vectors.append({
            "id": str(product["product_id"]),
            "values": embedding
        })

    if vectors:
        # Upsert into Pinecone in tenant namespace
        tenant_namespace = str(products_data[0]["tenant_id"])
        index.upsert(
            vectors=vectors,
            namespace=tenant_namespace
        )

    return result.rowcount  

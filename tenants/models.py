import uuid
import enum
from app.db.database import Base
from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class PlatformEnum(enum.Enum):
    shopify = "shopify"
    magento = "magento"
    bigcommerce = "bigcommerce"
    woocommerce = "woocommerce"
    custom = "custom"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    products = relationship("Product", back_populates="tenant")
    name = Column(String, nullable=False)
    platform = Column(Enum(PlatformEnum, name="platform_enum"), nullable=False)
    language = Column(String, nullable=False)

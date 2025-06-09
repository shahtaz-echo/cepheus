from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.settings import get_settings

settings = get_settings()

engine = create_engine(
    str(settings.database_url),
    pool_size = settings.max_connection_count,
    pool_pre_ping = True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

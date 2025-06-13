from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from typing import List, Dict, Any

from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "cepheus"
    app_env: str = "dev" 
    debug: bool = app_env == "dev"

    allowed_hosts: List[str] = ["*"]
    allowed_credentials: List[str] = ["*"]
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    
    api_prefix: str = "/api/v1"
    openapi_prefix: str = ""

    pinecone_api_key: str = ""
    pinecone_env: str = ""

    vector_dimension:int = 384
    embedding_model:str = 'all-MiniLM-L6-v2'

    database_url: PostgresDsn = ""
    max_connection_count: int = 10

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "title": self.app_name,
            "app_env": self.app_env,
            "api_prefix": self.api_prefix,
            "openapi_prefix": self.openapi_prefix,
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
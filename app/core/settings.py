from pydantic_settings import BaseSettings
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
    
    openapi_prefix: str = ""
    api_prefix: str = "/api/v1"

    pinecone_api_key : str = "" 

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "title": self.app_name,
            "debug": self.debug,
            "openapi_prefix": self.openapi_prefix,
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
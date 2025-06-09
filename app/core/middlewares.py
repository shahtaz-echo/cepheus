from starlette.middleware.cors import CORSMiddleware
from app.core.settings import get_settings

settings = get_settings()

middlewares = [
    {
        "middleware_class": CORSMiddleware,
        "options": {
            "allow_origins": settings.allowed_hosts,
            "allow_credentials": settings.allowed_credentials,
            "allow_methods": settings.allowed_methods,
            "allow_headers": settings.allowed_headers,
        }
    }
]
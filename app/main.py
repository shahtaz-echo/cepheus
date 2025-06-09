from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from starlette.exceptions import HTTPException

from app.handler.error_handler import (
    APIError, 
    http422_error_handler, 
    http_error_handler, 
    api_error_handler
)
from app.api.routes import router as api_router
from app.core.settings import get_settings
from app.core.middlewares import middlewares


def run_app()->FastAPI:
    settings = get_settings()
    app = FastAPI(**settings.fastapi_kwargs)

    # middleares
    for m in middlewares:
        app.add_middleware(m["middleware_class"], **m["options"])

    # api handler
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, http422_error_handler)
    app.add_exception_handler(APIError, api_error_handler)

    app.include_router(api_router, prefix=settings.api_prefix)

    return app

app = run_app()
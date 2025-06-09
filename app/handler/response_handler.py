from pydantic import BaseModel
from typing import Any, Union

class APIResponse(BaseModel):
    status_code: int
    success: bool
    message: str
    data: Any = None


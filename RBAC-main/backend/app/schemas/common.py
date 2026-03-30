from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class ResponseEnvelope(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None
    detail: Optional[str] = None

def success_response(data: Any = None, message: str = None) -> dict:
    return {"success": True, "data": data, "message": message}

def error_response(error: str, detail: str) -> dict:
    return {"success": False, "error": error, "detail": detail}
from typing import Any, Callable
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class APIException(HTTPException):
    def __init__(self, status_code: int, error: str, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.error = error

async def custom_http_exception_handler(request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": getattr(exc, "error", "error"), "detail": exc.detail},
    )
from typing import Any, Dict, Optional
from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import  HTTPException
import traceback

from app.core.logger import get_logger

logger = get_logger("error handler")


class ErrorResponse:
    """표준화된 에러 응답 포맷"""
    
    @staticmethod
    def create(
        error_code: str,
        message: str,
        detail: Optional[Any] = None,
        request_id: Optional[str] = None,
        path: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = {
            "error": {
                "code": error_code,
                "message": message,
            }
        }
        
        if detail:
            response["error"]["detail"] = detail
        
        if request_id:
            response["error"]["request_id"] = request_id
        
        if path:
            response["error"]["path"] = path
        
        return response


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTPException 핸들러"""
    request_id = getattr(request.state, "request_id", None)
    
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT",
    }
    
    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    
    log = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        detail=exc.detail,
    )
    
    if exc.status_code >= 500:
        log.exception("HTTP 5xx Exception occurred")
    else:
        log.warning("HTTP 4xx Exception occurred")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.create(
            error_code=error_code,
            message=str(exc.detail),
            request_id=request_id,
            path=str(request.url.path),
        ),
        headers=exc.headers or None
        
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """예상치 못한 에러 핸들러"""
    request_id = getattr(request.state, "request_id", None)

    logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        exception_type=type(exc).__name__,
        exception_message= str(exc),
        traceback= traceback.format_exc()
    ).critical(
        "Unhandled exception occurred"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse.create(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            request_id=request_id,
            path=str(request.url.path),
        )
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
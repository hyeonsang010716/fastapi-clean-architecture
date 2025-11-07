import uuid
import time
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logger import get_logger
from app.repository.log import LogRepository


class RequestIDMiddleware(BaseHTTPMiddleware):
    """요청 ID를 생성하고 추적하는 미들웨어"""
    
    def __init__(
        self,
        app: ASGIApp,
        header_name: str = "X-Request-ID",
        generator: Optional[Callable[[], str]] = None,
    ) -> None:
        super().__init__(app)
        self.header_name = header_name
        self.generator = generator or self._default_generator
        self.logger = get_logger("middleware.request_tracking")
    
    @staticmethod
    def _default_generator() -> str:
        """기본 요청 ID 생성기"""
        return str(uuid.uuid4())
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get(self.header_name) or self.generator()
        
        request.state.request_id = request_id
        
        self.logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path
        ).debug("요청 ID 할당됨")
        
        response = await call_next(request)
        
        response.headers[self.header_name] = request_id
        
        return response


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """에러 추적 및 모니터링 미들웨어"""
    
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.logger = get_logger("middleware.error_tracking")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")
        
        req_logger = self.logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None
        )
        
        req_logger.bind(
            query_params=dict(request.query_params),
            user_agent=request.headers.get("user-agent")
        ).info("요청 처리 시작")
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            req_logger.bind(
                status_code=response.status_code,
                process_time=process_time
            ).info("요청 처리 완료")
            
            return response
            
        except Exception:
            # 에러 핸들러에서 잡음
            raise


class MongoDBLoggingMiddleware(BaseHTTPMiddleware):
    """MongoDB에 API 호출 로그를 저장하는 미들웨어"""
    
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.logger = get_logger("middleware.mongodb_logging")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            response_time = (time.time() - start_time) * 1000
            
            client_host = request.client.host if request.client else None
            
            user_id = getattr(request.state, "user_id", None)
            
            try:
                await LogRepository.create(
                    called_api=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    user_id=user_id,
                    response_time=response_time,
                    ip_address=client_host
                )
            except Exception as e:
                self.logger.bind(
                    error=str(e),
                    api_path=request.url.path
                ).error("MongoDB 로그 저장 실패")
            
            return response
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            client_host = request.client.host if request.client else None
            
            try:
                await LogRepository.create(
                    called_api=request.url.path,
                    method=request.method,
                    status_code=500,
                    response_time=response_time,
                    ip_address=client_host
                )
            except Exception as log_error:
                self.logger.bind(
                    error=str(log_error),
                    api_path=request.url.path
                ).error("MongoDB 에러 로그 저장 실패")
            
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 추가 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        return response
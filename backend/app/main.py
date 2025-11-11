from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config.setting import settings
from app.core.logger import setup_logging, get_logger
from app.middleware.tracking import (
    RequestIDMiddleware,
    ErrorTrackingMiddleware,
    MongoDBLoggingMiddleware,
    SecurityHeadersMiddleware
)
from app.core.exception.handler import register_exception_handlers
from app.database.session import init_mongodb, close_mongodb
from app.core.redis import get_redis_client, close_redis
from app.core.llm_manager import initialize_llm_manager
from app.api.v1.router import api_router
from app.container import Container


logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    
    # MongoDB 초기화
    await init_mongodb()
    logger.info("MongoDB 연결 완료")
    
    # Redis 초기화
    redis_client = await get_redis_client()
    try:
        await redis_client.ping()
        logger.info("Redis 연결 완료")
    except Exception as e:
        logger.error(f"Redis 연결 실패: {e}")
        raise
    
    # LLM 초기화
    initialize_llm_manager()
    
    logger.bind(
        app_title=app.title,
        app_version=app.version,
        environment=settings.ENVIRONMENT
    ).info("애플리케이션 시작")
    
    yield
    
    # 종료 시 정리
    await close_mongodb()
    logger.info("MongoDB 연결 종료")
    
    await close_redis()
    logger.info("Redis 연결 종료")
    
    logger.info("애플리케이션 종료")


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 팩토리"""
    
    setup_logging()
    
    # DI Container 초기화 및 wiring
    container = Container()
    container.wire(modules=["app.api.v1.user.register"])
    
    app = FastAPI(
        title="FastAPI Server",
        description="FastAPI 서버 공통 세팅",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    logger.bind(
        is_production=settings.is_production,
        log_level=settings.LOG_LEVEL
    ).info("FastAPI 앱 생성 완료")
    
    # 미들웨어 등록 (순서 중요함 -> 먼저 등록된 것이 나중에 실행됨)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(MongoDBLoggingMiddleware)
    app.add_middleware(ErrorTrackingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    logger.debug("미들웨어 등록 완료")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Frontend URL 권한 부여
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.bind().debug("CORS 설정 완료")
    
    register_exception_handlers(app)
    logger.debug("예외 핸들러 등록 완료")
  
    app.include_router(api_router, prefix="/api/v1")
    logger.debug("API 라우터 등록 완료")
 
    @app.get("/health", tags=["health"])
    async def health_check():
        health_status = {
            "status": "healthy",
            "version": app.version,
            "environment": settings.ENVIRONMENT,
            "services": {}
        }
        
        try:
            redis_client = await get_redis_client()
            await redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        except Exception as e:
            health_status["services"]["redis"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
            
        logger.bind(**health_status).debug("헬스 체크")
        return health_status
    
    logger.bind(
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.ENVIRONMENT
    ).success("Uvicorn 서버 시작 완료")
    
    app.container = container
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.ENVIRONMENT,
        log_config=None,
    )
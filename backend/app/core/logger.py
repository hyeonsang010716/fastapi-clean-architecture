""" 
로깅 설정

- 예시:
  LOG_LEVEL=DEBUG
  LOG_FORMAT=console
  LOG_FILE_PATH=/var/log/app/app.log

필드 설명:
  LOG_LEVEL:
    - 최소 출력 로그 레벨
    - TRACE < DEBUG < INFO < SUCCESS < WARNING < ERROR < CRITICAL
    - 여기서 설정한 레벨 "이상" 만 출력됨

  LOG_FORMAT:
    - "json"   : serialize=True 로 JSON 구조화 로그 출력 (로그 수집/분석용)
    - "console": 사람이 읽기 좋은 컬러 콘솔 로그 출력 (로컬 디버깅용)

  LOG_FILE_PATH:
    - None 이면 콘솔에만 출력
    - 경로를 지정하면 해당 파일로도 로그를 남김

  LOG_ROTATION:
    - "100 MB" → 로그 파일이 100MB를 넘으면 새 파일로 롤테이션
    - 용량/시간 기준 문자열 모두 사용 가능 (Loguru 규칙 따름)

  LOG_RETENTION:
    - "30 days" → 생성된 지 30일이 지난 롤테이션된 로그 파일은 자동 삭제

  LOG_COMPRESSION:
    - "gz" → 롤테이션된 로그 파일을 gzip(.gz)으로 압축


로깅 시스템

from core.exception.logger import get_logger

logger = get_logger("service_name")

logger.bind(user_id=123).bind(user_type="he").info("서비스 완료")
logger.bind(user_id=123, user_type="he").info("서비스 완료")
"""
import sys
import logging
from pathlib import Path
from loguru import logger
from loguru._logger import Logger

from app.config.setting import settings



def setup_logging() -> None:
    """로깅 시스템 설정"""
    
    logger.remove()
    
    # 콘솔 출력 설정
    if settings.LOG_FORMAT == "json":
        # JSON 포맷
        logger.add(
            sys.stdout,
            format="{message}",
            serialize=True,
            level=settings.LOG_LEVEL,
            enqueue=True
        )
    else:
        # 읽기 쉬운 콘솔 포맷
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> | {extra}",
            level=settings.LOG_LEVEL,
            colorize=True,
            enqueue=True
        )
    
    # 파일 출력 설정
    if settings.LOG_FILE_PATH:
        log_path = Path(settings.LOG_FILE_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            settings.LOG_FILE_PATH,
            rotation=settings.LOG_ROTATION,
            retention=settings.LOG_RETENTION,
            compression=settings.LOG_COMPRESSION,
            format="{message}",
            serialize=True,
            level=settings.LOG_LEVEL,
            encoding="utf-8",
            enqueue=True
        )
    
    # 표준 logging 라이브러리와 통합
    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            # loguru 레벨로 변환
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            # 해당 로거에서 발생한 로그 찾기
            frame, depth = logging.currentframe(), 2
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
    
    # 표준 로거 설정
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # 주요 라이브러리 로거 레벨 설정
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logger.info(f"Logging system initialized with level: {settings.LOG_LEVEL}")




def get_logger(name: str) -> Logger:
    """이름이 지정된 로거 가져오기"""
    return logger.bind(logger_name=name)


# 전역 로거 인스턴스
app_logger = get_logger("app")
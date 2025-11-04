from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서버
    HOST: str = Field("0.0.0.0", description="서버 호스트")
    PORT: int = Field(8000, description="서버 포트 번호") 
    
    # 환경
    ENVIRONMENT: str = Field("DEV", description="환경 (실서버, 개발서버)")
    DEBUG: bool = Field(True, description="개발 환경")
    
    # 로깅 설정
    LOG_LEVEL: str = Field("INFO", description="로그 레벨")
    LOG_FORMAT: str = Field("console", description="로그 포맷 (json/console)")
    LOG_FILE_PATH: Optional[str] = Field(None, description="로그 파일 경로")
    LOG_ROTATION: str = Field("100 MB", description="로그 레벨")
    LOG_RETENTION: str = Field("30 days", description="로그 파일 롤테이션 기준")
    LOG_COMPRESSION: str = Field("gz", description="로그 롤테이션 파일 압축")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        json_schema_extra = {
            "example": {
                "ENVIRONMENT": "DEV",
                "DEBUG": False
            }
        }
    
    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return not self.DEBUG


settings = Settings()
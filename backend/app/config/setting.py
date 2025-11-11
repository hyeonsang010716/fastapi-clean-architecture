from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
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
    
    # LLM KEY
    OPENAI_API_KEY: str = Field("sk-", description="OpenAI API KEY")
    
    # POSTGRES 정보
    POSTGRES_HOST: str = Field("hyeonsang-postgres", description="POSTGRES HOST")
    POSTGRES_PORT: int = Field(5432, description="POSTGRES PORT")
    POSTGRES_USER: str = Field("cho", description="POSTGRES USER")
    POSTGRES_PASSWORD: str = Field("hyeonsang", description="POSTGRES PASSWORD")
    POSTGRES_NAME: str = Field("chohyeonsang", description="POSTGRES NAME")
    
    # MongoDB 정보
    MONGODB_HOST: str = Field("hyeonsang-mongodb", description="MONGODB HOST")
    MONGODB_PORT: int = Field(27017, description="MONGODB PORT")
    MONGODB_USER: str = Field("cho", description="MONGODB USER")
    MONGODB_PASSWORD: str = Field("hyeonsang", description="MONGODB PASSWORD")
    MONGODB_NAME: str = Field("chohyeonsang", description="MONGODB NAME")
    
    # Redis 정보
    REDIS_HOST: str = Field("hyeonsang-redis", description="REDIS HOST")
    REDIS_PORT: int = Field(6379, description="REDIS PORT")
    REDIS_DB: int = Field(0, description="REDIS DB")
    
    @property
    def POSTGRES_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}"
    
    @property
    def SYNC_POSTGRES_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}"
    
    @property
    def MONGODB_URL(self) -> str:
        return f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_NAME}?authSource=admin"
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return not self.DEBUG
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
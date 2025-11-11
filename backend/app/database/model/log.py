from datetime import datetime, timezone
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import Field


class Log(Document):
    """API 호출 로그 Document"""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="로그 생성 시간")
    called_api: str = Field(..., description="호출된 API 경로")
    method: Optional[str] = Field(None, description="HTTP 메소드")
    status_code: Optional[int] = Field(None, description="응답 상태 코드")
    user_id: Optional[PydanticObjectId] = Field(None, description="요청한 사용자 ID")
    response_time: Optional[float] = Field(None, description="응답 시간 (ms)")
    ip_address: Optional[str] = Field(None, description="요청자 IP 주소")
    
    class Settings:
        name = "log"
        
    class Config:
        json_schema_extra = {
            "example": {
                "created_at": "2024-01-01T12:00:00Z",
                "called_api": "/api/v1/user/register",
                "method": "POST",
                "status_code": 200,
                "response_time": 123.45,
                "ip_address": "127.0.0.1"
            }
        }
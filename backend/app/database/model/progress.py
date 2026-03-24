from datetime import datetime, timezone
from typing import Optional
from beanie import Document
from pydantic import Field


class Progress(Document):
    """진행률 추적 Document"""
    user_id: str = Field(..., description="사용자 ID")
    progress_key: str = Field(..., description="진행률 고유 키")
    end: Optional[bool] = Field(None, description="완료 여부 (None: 진행 중, True: 완료, False: 실패)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="생성 시간")

    class Settings:
        name = "progress"

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "progress_key": "PGS_1711234567_a1b2c3d4",
                "end": None,
                "created_at": "2024-01-01T12:00:00Z"
            }
        }

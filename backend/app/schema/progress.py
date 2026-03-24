from typing import Optional
from pydantic import BaseModel, Field


class ProgressChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="사용자 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123"
            }
        }


class ProgressSearchRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="사용자 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123"
            }
        }


class ProgressSearchResponse(BaseModel):
    user_id: str = Field(..., description="사용자 ID")
    progress_key: Optional[str] = Field(None, description="진행률 고유 키")
    current_step: Optional[int] = Field(None, description="현재 진행 단계")
    total_steps: Optional[int] = Field(None, description="총 단계 수")
    message: Optional[str] = Field(None, description="현재 단계 메시지")
    status: str = Field(..., description="상태 (in_progress, completed, failed, no_active_progress)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "progress_key": "PGS_1711234567_a1b2c3d4",
                "current_step": 3,
                "total_steps": 5,
                "message": "데이터 분석 중...",
                "status": "in_progress"
            }
        }

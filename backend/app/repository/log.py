from typing import List, Optional
from datetime import datetime, timedelta, timezone
from beanie import PydanticObjectId

from app.database.model.log import Log


class LogRepository:
    """로그 관련 데이터베이스 작업"""
    
    @staticmethod
    async def create(
        called_api: str,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        user_id: Optional[PydanticObjectId] = None,
        response_time: Optional[float] = None,
        ip_address: Optional[str] = None
    ) -> Log:
        """새로운 로그 생성"""
        log = Log(
            called_api=called_api,
            method=method,
            status_code=status_code,
            user_id=user_id,
            response_time=response_time,
            ip_address=ip_address
        )
        await log.insert()
        return log
    
    @staticmethod
    async def find_by_id(log_id: PydanticObjectId) -> Optional[Log]:
        """ID로 로그 조회"""
        return await Log.get(log_id)
    
    @staticmethod
    async def find_by_api(called_api: str, limit: int = 100) -> List[Log]:
        """API 경로로 로그 조회"""
        return await Log.find(Log.called_api == called_api).limit(limit).to_list()
    
    @staticmethod
    async def find_by_user(user_id: PydanticObjectId, limit: int = 100) -> List[Log]:
        """사용자 ID로 로그 조회"""
        return await Log.find(Log.user_id == user_id).limit(limit).to_list()
    
    @staticmethod
    async def find_by_date_range(
        start_date: datetime, 
        end_date: datetime,
        limit: int = 1000
    ) -> List[Log]:
        """날짜 범위로 로그 조회"""
        return await Log.find(
            Log.created_at >= start_date,
            Log.created_at <= end_date
        ).limit(limit).to_list()
    
    @staticmethod
    async def find_recent(hours: int = 24, limit: int = 1000) -> List[Log]:
        """최근 N시간 로그 조회"""
        start_date = datetime.now(timezone.utc) - timedelta(hours=hours)
        return await Log.find(
            Log.created_at >= start_date
        ).sort(-Log.created_at).limit(limit).to_list()
    
    @staticmethod
    async def count_by_api(called_api: str) -> int:
        """특정 API의 호출 횟수"""
        return await Log.find(Log.called_api == called_api).count()
    
    @staticmethod
    async def delete_old_logs(days: int = 30) -> int:
        """오래된 로그 삭제"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        result = await Log.find(Log.created_at < cutoff_date).delete()
        return result.deleted_count if result else 0
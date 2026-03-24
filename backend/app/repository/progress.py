from typing import Optional

from app.database.model.progress import Progress


class ProgressRepository:
    """진행률 관련 데이터베이스 작업"""

    @staticmethod
    async def create(user_id: str, progress_key: str) -> Progress:
        """새로운 진행률 레코드 생성 (end=None 상태)"""
        progress = Progress(
            user_id=user_id,
            progress_key=progress_key,
            end=None
        )
        await progress.insert()
        return progress

    @staticmethod
    async def find_active_by_user(user_id: str) -> Optional[Progress]:
        """사용자의 진행 중인(end=None) 레코드 조회"""
        return await Progress.find_one(
            Progress.user_id == user_id,
            Progress.end == None
        )

    @staticmethod
    async def find_by_key(progress_key: str) -> Optional[Progress]:
        """progress_key로 레코드 조회"""
        return await Progress.find_one(Progress.progress_key == progress_key)

    @staticmethod
    async def update_end_status(progress_key: str, end: bool) -> Optional[Progress]:
        """진행률 레코드의 end 상태 업데이트"""
        progress = await Progress.find_one(Progress.progress_key == progress_key)
        if progress:
            progress.end = end
            await progress.save()
        return progress
